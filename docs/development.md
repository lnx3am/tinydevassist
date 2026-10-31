# Development setup and verification

## Supported environments

- Target for the measured local training and CPU serving workflow: **Python 3.11**. The public ZeroGPU Space runs Python 3.12.12 with pinned serving dependencies; local Python 3.12 training has not been tested.
- Python 3.13 can run the dependency-free core and its tests, but ML-library compatibility is **not yet verified**.
- Linux/macOS/WSL2 recommended. GPU is optional for the initial project setup, but training time depends heavily on CUDA availability.
- Do not install unverified CUDA-specific PyTorch wheels blindly. Follow the [official PyTorch selector](https://pytorch.org/get-started/locally/) for the local CUDA driver/runtime.

## Bootstrap (Ubuntu / WSL2)

```bash
cd tiny-llm-hf
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m tinydevassist doctor
make check
```

The `requirements.txt` file provides a minimal editable installation. Optional dependency groups are maintained in `pyproject.toml`:

```bash
python -m pip install -e '.[train]'
python -m pip install -e '.[app]'
python -m pip install -e '.[api]'
python -m pip install -e '.[notebooks]'
```

Do **not** install all extras on a CPU-only deployment until actual serving requirements have been measured. No Hugging Face token is required for environment diagnostics or unit tests.

## Quality gates

```bash
make lint
make format-check
make test
make check
```

`make format` intentionally changes formatting; inspect its diff before committing. The `doctor` command checks module presence only, not dependency compatibility or successful model loading.

## Reproducibility boundary

Version ranges are specified in `pyproject.toml`, but there is no cross-platform lockfile. One Python 3.11.16 CPU environment completed baseline generation, six-step LoRA training, and paired evaluation with PyTorch 2.14.1+cpu, Transformers 4.57.6, PEFT 0.21.2, seed 42, and upstream revision `a10cc1512eabd3dde888204e902eca88bddb4951`. The source and split hashes are pinned by the data-preparation regression test. Separately, the pinned Python 3.12.12 ZeroGPU serving image built and answered one public request. Neither observation validates all platforms or sustained hosted reliability.

## Baseline experiment

```bash
python prepare_data.py --seed 42
python -m pip install -e '.[train,notebooks]'
python inference.py --revision a10cc1512eabd3dde888204e902eca88bddb4951 --device cpu --max-samples 6 --temperature 0 --max-new-tokens 96
# Writes ignored outputs/baseline.json on success only.
```

The model and tokenizer are loaded with `trust_remote_code=False`. The script
uses the upstream tokenizer chat template, generates from **held-out test rows**,
and records per-question output, token counts, wall-clock generation latency,
model parameter count/bytes, optional process RSS snapshots (`psutil`), and CUDA
peak allocation if applicable. CPU RSS before/after are not CPU peak memory.
`--revision` should be an immutable upstream commit hash; the report records
both requested and resolved revisions. `main` is convenient but not pinned.
Two CPU baseline runs completed on 2026-10-27 using Python 3.11.16, PyTorch
2.14.1+cpu, and upstream revision `a10cc1512eabd3dde888204e902eca88bddb4951`.
All six held-out prompts were generated with greedy decoding and the ignored
first report recorded 14.303 seconds median and 12.301 seconds mean latency.
A later matching baseline rerun used for paired evaluation recorded 10.793
seconds median and 9.520 seconds mean latency. These are single-machine
measurements, not quality or deployment claims. The CLI
still fails rather than producing placeholder numbers when dependencies are
missing.

## LoRA fine-tuning plan and guarded execution (Milestone 6)

```bash
python prepare_data.py --seed 42
python train_lora.py  # offline dry run; verifies source/split hashes, no model download
# First run the baseline on ALL SIX held-out test examples at the same pinned SHA:
python inference.py --revision <40-character-upstream-model-commit-sha> --max-samples 6
# Only after baseline success and with training dependencies installed:
python train_lora.py --revision <same-40-character-sha> --execute
```

The config is [`configs/train_lora.json`](../configs/train_lora.json):
LoRA rank 8, alpha 16, dropout 0.05, target modules `q_proj`/`v_proj`;
maximum 512 tokens, 1 epoch, batch size 1, gradient accumulation 4, and
a hard cap of 6 optimizer steps. One CPU run used those exact bounded settings;
they are not validated hyperparameters. Review them for your hardware before
training.

The CLI fails closed if source/split SHA-256 hashes or seed change, if the
upstream revision is not a 40-character commit SHA, if the baseline is absent
or mismatched, or if an existing training report would be overwritten.
It refuses to reuse a nonempty adapter directory. Actual execution requires
`pip install -e '.[train]'` and access to the pinned model weights.
A completed run writes ignored `checkpoints/tinydevassist-lora/` and
`outputs/train_lora.json`. A real CPU run completed on 2026-10-27 with the
matching pinned baseline: 24 training rows, 6 validation rows, six optimizer
steps, 819,200 trainable LoRA parameters, 43.537 seconds training runtime,
and 3.39398 validation loss. It is a bounded pipeline verification only—not a
quality comparison, generalization result, or deployment benchmark.

Notebook [`03_lora_finetuning.ipynb`](../notebooks/03_lora_finetuning.ipynb)
executes the verified dry run by default, visualizes only real split counts,
and reads completed training metrics only if a genuine report exists.
Do not treat its default execution as a training run.
