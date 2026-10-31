from __future__ import annotations

import pytest

from tinydevassist.evaluation import AdapterGenerator, comparison_report, summarize_generations


def test_comparison_report_has_no_automatic_quality_metric():
    rows = [
        {
            "id": "git-005",
            "base": {
                "response": "base",
                "latency_seconds": 1.0,
                "input_tokens": 2,
                "generated_tokens": 3,
            },
            "adapter": {
                "response": "adapter",
                "latency_seconds": 2.0,
                "input_tokens": 2,
                "generated_tokens": 4,
            },
        }
    ]
    report = comparison_report(rows, model_id="model", revision="a" * 40, test_sha256="b" * 64)
    assert report["status"] == "measured_comparison"
    assert report["methodology"]["quality_metric"] is None
    assert report["summary"]["adapter"]["nonempty_responses"] == 1


def test_comparison_rejects_missing_generation_metrics():
    with pytest.raises(ValueError):
        comparison_report(
            [{"id": "a", "base": {"response": "x"}, "adapter": {"response": "y"}}],
            model_id="model",
            revision="a" * 40,
            test_sha256="b" * 64,
        )


def test_comparison_rejects_duplicate_ids():
    row = {
        "id": "git-005",
        "base": {
            "response": "base",
            "latency_seconds": 1.0,
            "input_tokens": 2,
            "generated_tokens": 3,
        },
        "adapter": {
            "response": "adapter",
            "latency_seconds": 2.0,
            "input_tokens": 2,
            "generated_tokens": 4,
        },
    }
    with pytest.raises(ValueError, match="duplicate evaluation id"):
        comparison_report([row, row], model_id="model", revision="a" * 40, test_sha256="b" * 64)


def test_comparison_rejects_blank_id():
    generation = {
        "response": "ok",
        "latency_seconds": 1.0,
        "input_tokens": 2,
        "generated_tokens": 3,
    }
    with pytest.raises(ValueError, match="evaluation rows must contain id"):
        comparison_report(
            [{"id": " ", "base": generation, "adapter": generation}],
            model_id="model",
            revision="a" * 40,
            test_sha256="b" * 64,
        )


@pytest.mark.parametrize(
    ("metric", "value"),
    [
        ("latency_seconds", -0.1),
        ("latency_seconds", float("nan")),
        ("input_tokens", -1),
        ("input_tokens", True),
        ("generated_tokens", 1.5),
    ],
)
def test_comparison_rejects_invalid_measurements(metric, value):
    generation = {
        "response": "answer",
        "latency_seconds": 1.0,
        "input_tokens": 2,
        "generated_tokens": 3,
    }
    generation[metric] = value
    with pytest.raises(ValueError, match="evaluation"):
        comparison_report(
            [{"id": "git-005", "base": generation, "adapter": generation}],
            model_id="model",
            revision="a" * 40,
            test_sha256="b" * 64,
        )


def test_generation_summary_counts_blank_responses():
    rows = [
        {"adapter": {"response": "", "latency_seconds": 1.0, "generated_tokens": 0}},
        {"adapter": {"response": "ok", "latency_seconds": 3.0, "generated_tokens": 4}},
    ]
    assert summarize_generations(rows, "adapter") == {
        "samples": 2,
        "nonempty_responses": 1,
        "mean_latency_seconds": 2.0,
        "mean_generated_tokens": 2.0,
    }


def test_adapter_rejects_requests_beyond_training_sequence_budget():
    class FakeTensor:
        shape = (1, 500)

        def to(self, device):
            return self

    class FakeTokenizer:
        def apply_chat_template(self, *args, **kwargs):
            return {"input_ids": FakeTensor()}

    generator = AdapterGenerator.__new__(AdapterGenerator)
    generator.tokenizer = FakeTokenizer()
    generator.device = "cpu"
    with pytest.raises(ValueError, match="512-token demo budget"):
        generator.generate("What happened?", max_new_tokens=96)
