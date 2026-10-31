"""Held-out base-versus-adapter generation comparison utilities."""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from typing import Any

from tinydevassist.data import prompt_messages

MAX_SEQUENCE_LENGTH = 512


@dataclass(frozen=True)
class EvaluationGeneration:
    response: str
    latency_seconds: float
    input_tokens: int
    generated_tokens: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_generations(rows: list[dict[str, Any]], key: str) -> dict[str, float | int]:
    """Summarize measured generations without inventing a quality score."""
    values = [row[key] for row in rows]
    latencies = [item["latency_seconds"] for item in values]
    return {
        "samples": len(values),
        "nonempty_responses": sum(bool(item["response"].strip()) for item in values),
        "mean_latency_seconds": sum(latencies) / len(latencies),
        "mean_generated_tokens": sum(item["generated_tokens"] for item in values) / len(values),
    }


def comparison_report(
    rows: list[dict[str, Any]], *, model_id: str, revision: str, test_sha256: str
) -> dict[str, Any]:
    if not rows:
        raise ValueError("evaluation needs at least one held-out example")
    seen_ids: set[str] = set()
    required_fields = {"id", "base", "adapter"}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("evaluation row must be a mapping")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id.strip() or set(row) != required_fields:
            raise ValueError("evaluation rows must contain id, base, and adapter")
        if row_id in seen_ids:
            raise ValueError(f"duplicate evaluation id: {row_id}")
        seen_ids.add(row_id)
        for key in ("base", "adapter"):
            item = row[key]
            if not isinstance(item, dict) or not isinstance(item.get("response"), str):
                raise ValueError("evaluation generation is malformed")
            latency = item.get("latency_seconds")
            if (
                isinstance(latency, bool)
                or not isinstance(latency, (int, float))
                or not math.isfinite(latency)
                or latency < 0
            ):
                raise ValueError("evaluation latency must be finite and nonnegative")
            for metric in ("input_tokens", "generated_tokens"):
                count = item.get(metric)
                if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                    raise ValueError(f"evaluation {metric} must be a nonnegative integer")
    return {
        "schema_version": 1,
        "status": "measured_comparison",
        "model_id": model_id,
        "revision": revision,
        "input_sha256": test_sha256,
        "methodology": {
            "prompts": "all held-out test instructions",
            "decoding": "greedy, max_new_tokens=96, temperature=0",
            "quality_metric": None,
            "quality_note": "Responses require human review; no automatic quality claim is made.",
        },
        "summary": {
            "base": summarize_generations(rows, "base"),
            "adapter": summarize_generations(rows, "adapter"),
        },
        "results": rows,
    }


class AdapterGenerator:
    """Load a PEFT adapter and generate one response at a time."""

    def __init__(
        self, model_id: str, revision: str, adapter_path: str, device: str = "cpu"
    ) -> None:
        if device not in {"cpu", "cuda"}:
            raise ValueError("device must be cpu or cuda")
        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("install the train dependencies for adapter evaluation") from exc
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but unavailable")
        self.torch = torch
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, revision=revision, trust_remote_code=False
        )
        base = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, trust_remote_code=False
        )
        # ZeroGPU emulates CUDA during startup; safetensors must first load on CPU.
        self.model = (
            PeftModel.from_pretrained(base, adapter_path, torch_device="cpu").to(device).eval()
        )

    def generate(
        self, prompt: str, *, max_new_tokens: int = 96, temperature: float = 0.0
    ) -> EvaluationGeneration:
        if not 1 <= max_new_tokens <= 512:
            raise ValueError("max_new_tokens must be between 1 and 512")
        if not 0 <= temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        encoded = self.tokenizer.apply_chat_template(
            prompt_messages(prompt),
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        encoded = {name: value.to(self.device) for name, value in encoded.items()}
        input_tokens = int(encoded["input_ids"].shape[-1])
        if input_tokens + max_new_tokens > MAX_SEQUENCE_LENGTH:
            raise ValueError(
                f"question is too long for the {MAX_SEQUENCE_LENGTH}-token demo budget; "
                "shorten it or lower maximum new tokens"
            )
        started = time.perf_counter()
        kwargs = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id,
        }
        if temperature > 0:
            kwargs["temperature"] = temperature
        with self.torch.inference_mode():
            output = self.model.generate(**encoded, **kwargs)
        completion = output[0][input_tokens:]
        return EvaluationGeneration(
            response=self.tokenizer.decode(completion, skip_special_tokens=True).strip(),
            latency_seconds=round(time.perf_counter() - started, 6),
            input_tokens=input_tokens,
            generated_tokens=int(len(completion)),
        )
