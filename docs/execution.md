# 3-day execution milestones

Status: **M1–M15 completed, including a public adapter, a verified Gradio ZeroGPU Space, and a final audit.** The alternate Docker image remains unbuilt; independent response quality remains unmeasured. Progress is checkpointed in Git. Each future session must read Git status, log, active branch, and docs before editing; test, scan staged diff for secrets/weights, then commit meaningful changes with the configured author. Do not reset or overwrite existing changes.

1. [x] Inspect workspace, create project scope/architecture/decision records.
2. [x] Python project, tooling, CI-ready tests, local environment.
3. [x] Document dataset and licensing; inspect base model metadata and the pinned runtime model.
4. [x] Deterministic data preparation/splitting and tests.
5. [x] Baseline inference and resource metrics (one pinned CPU run on all six held-out prompts).
6. [x] Configurable LoRA fine-tuning pipeline (real CPU integration verified).
7. [x] Execute truthful, bounded training experiment.
8. [x] Base-versus-adapted held-out generation comparison (no automatic quality claim).
9. [x] Refine inference controls and examples; inspect all six response pairs.
10. [x] Gradio app and local HTTP plus real inference smoke test.
11. [x] Gradio ZeroGPU Space metadata, deployment guide, and public build; alternate Docker image unverified.
12. [x] Publish model and Space; verify public Space status and one anonymous inference.
13. [x] Model card, experiment report, architecture finalization.
14. [x] CI, cleanup, and reproduction instructions.
15. [x] Final link, documentation, CI, local test, and public inference audit; limits recorded.

## Session 1 report

- Milestone: 1
- Workspace: isolated project in `/mnt/data/tiny-llm-hf`; no existing Git repository found in accessible task workspace.
- Created: README, architecture, decision records, milestone tracker, Git ignore rules.
- Verification: Git initialization, status/diff, author identity, committed-file listing.
- Limitations: no user machine access established, no GitHub remote, no Hugging Face authentication, no model download or GPU capability test.

## Session 2 report

- Milestone: 2 — Python packaging, optional dependency groups, development commands, offline diagnostics, tests, and lightweight CI.
- Workspace: `/mnt/data/tiny-llm-hf` in an isolated execution container; **not the user's laptop**. The Milestone 1 Git history was found intact on `main`, with a clean initial working tree.
- Added: `pyproject.toml`, `requirements.txt`, `Makefile`, `src/tinydevassist/`, `tests/`, `.github/workflows/ci.yml`, `.env.example`, `docs/development.md`, `configs/README.md`, `notebooks/README.md`.
- Verification: editable core install succeeded; `python -m pytest -q` passed (3 tests); `python -m compileall -q src tests` passed; `python -m tinydevassist doctor` produced valid JSON; `git diff --check` passed. Ruff lint/format checks could not run: Ruff was not installed and its wheel was unavailable from the configured package source. Python 3.13 is available here, whereas Python 3.11 is the recommended ML environment.
- Remaining: no model download, training, deployment, remote GitHub repository, or access to the user's computer established.

## Session 3 report

- Milestone: 3 — documented model selection, verified upstream metadata, and created a tracked, auditable 36-record seed dataset with an explicit dataset card and licensing policy.
- Workspace: restored the previously committed Milestone 2 archive to `/mnt/data/tiny-llm-hf-m3-work/tiny-llm-hf` without overwriting the unrelated existing README in `/mnt/data/tiny-llm-hf`; restored branch `main` and verified clean status and both previous commits before editing. **Not the user's laptop.**
- Changed: `LICENSE`, `README.md`, `configs/model.json`, `data/README.md`, `data/DATASET_CARD.md`, `data/samples/developer_support_v1.jsonl`, `docs/model_selection.md`, `docs/decisions.md`, `docs/execution.md`, and `tests/test_dataset_sample.py`.
- Verification: `PYTHONPATH=src python -m pytest -q` (5 passed); `python -m compileall -q src tests` passed; `git diff --check` passed. Ruff was not installed and cannot be claimed as passing. Staged diff, secret, and weight checks are required before commit.
- Limitations: no upstream model weights downloaded, no model inference or training, no GitHub remote, no Hugging Face credentials, no user-computer access. `main` remains an unpinned upstream revision until an experiment is executed.

## Session 4 report

- Milestone: 4 — implemented deterministic source validation, normalization, duplicate/near-duplicate controls, category-stratified splits, chat-message formatting, leakage checks, and SHA-256 manifest.
- Workspace: restored Milestone 3 archive into `/mnt/data/tinydevassist-m4-work/tiny-llm-hf` to avoid overwriting an unrelated `/mnt/data/tiny-llm-hf/README.md`; no access to the user's personal computer. Verified `main`, clean initial status, and all three previous commits before edits.
- Files: `prepare_data.py`, `src/tinydevassist/data.py`, `tests/test_data_preparation.py`, `Makefile`, `README.md`, `data/README.md`, `data/DATASET_CARD.md`, `docs/architecture.md`, `docs/decisions.md`, and this tracker.
- Data result: source SHA-256 `92ffc379ffe09d71052d9a7cfc9c9b4fe740c540cb7955e4347e2f646bef151f`; 36 retained rows, 24/6/6 stratified split, no duplicate questions or IDs. Generated outputs are Git-ignored.
- Verification: offline tests, Python compilation, manifest/hash checks, staged diff/secret/weights checks, and Git commit are recorded in the run report. Ruff remains unavailable in this environment and must not be reported as passing.
- Limitations: no real model inference/training/deployment, no user-laptop access, no GitHub remote, no Hugging Face credentials. Independent evaluation questions still needed.

## Session 5 report

- Milestone: 5 **implementation checkpoint** — added baseline CLI, lazy-loaded Transformers generator, deterministic decoding and measurable JSON output, offline tests, and the first two notebooks. Real baseline measurements remain **uncompleted**, so Milestone 5 stays unchecked.
- Workspace: restored Milestone 4 archive to `/mnt/data/tinydevassist-work-m5/tiny-llm-hf`, separate from an unrelated `/mnt/data/tiny-llm-hf/README.md`. Verified `main`, clean initial status, and commits `4bedf18`, `4c0b4a0`, `3fbd101`, `d39f6ca`. Not the user's laptop.
- Files: `inference.py`, `src/tinydevassist/inference.py`, `tests/test_inference.py`, `notebooks/01_dataset_exploration.ipynb`, `notebooks/02_baseline_model.ipynb`, `notebooks/README.md`, `README.md`, `docs/development.md`, `docs/decisions.md`, `docs/execution.md`, `pyproject.toml`, `Makefile`, `.gitignore`.
- Verification: 24 offline tests passed; compilation passed; notebook 01 executed against the tracked source and notebook 02 executed in **skip mode**; baseline CLI correctly fails when Transformers is unavailable. No real model weights downloaded or executed. Ruff unavailable and offline installation unsuccessful; do not claim lint or format checks passed.
- Blockers: no network resolution for huggingface.co; Transformers/weights unavailable; no local-computer access or GitHub remote. Actual model performance, baseline generations, training, and deployment remain unverified.

## Session 6 report

- Milestone: 6 **implementation checkpoint** — added strict LoRA config and bounded dry-run/opt-in CLI, hash-verified train/validation/test inputs, a measured-baseline/pinned-revision gate, assistant-only loss tokenization, right-padding collator, offline tests, and notebook 03. Real training remains **uncompleted**, so Milestone 6 stays unchecked.
- Workspace: restored the verified Milestone 5 archive into `/mnt/data/tinydevassist-m6-work/tiny-llm-hf`, separately from prior workspaces. Verified `main`, clean initial status, latest commit `5b8151f`, and no Git remote. Not the user's personal computer.
- Files: `train_lora.py`, `src/tinydevassist/training.py`, `configs/train_lora.json`, `tests/test_training.py`, `tests/test_notebooks.py`, `notebooks/03_lora_finetuning.ipynb`, `notebooks/README.md`, `Makefile`, `README.md`, `docs/development.md`, `docs/architecture.md`, `docs/decisions.md`, and this tracker.
- Verification: offline dry run confirmed the unchanged 36-record source SHA-256, 24/6/6 splits, and a 6-step plan. Unit tests, compilation, notebook execution in **skip mode**, diff checks, and staged secret/weight checks are recorded in the run report. No model download, adapter training, or benchmark occurred.
- Blockers: no measured baseline, pinned upstream model revision, Transformers/PEFT packages or cached weights, user-laptop access, or GitHub remote. Training/integration and quality claims remain unverified.

## Session 7 report

- Milestone: 5 baseline preflight — **not completed**. The repository was available in an isolated workspace, but this does not establish access to the user's computer.
- Verified: `main` was clean at `e509bdf`; `prepare_data.py --seed 42` reproduced the 24/6/6 split, including test SHA-256 `706756348bd549ee3db4f453189955b84950760a723751fd287b37134566dde7`. A Python 3.11 CPU environment installed the project, PyTorch `2.14.1+cpu`, Transformers `4.57.6`, and the declared experiment dependencies. CUDA is unavailable.
- Upstream: the Hugging Face API resolved `HuggingFaceTB/SmolLM2-360M-Instruct` to immutable revision `a10cc1512eabd3dde888204e902eca88bddb4951`.
- Result: baseline loading was attempted with that exact revision and all six held-out examples, but the tokenizer artifact request was reset by the remote connection; subsequent model retrieval did not finish. No `outputs/baseline.json` was created, so no generation, latency, memory, quality, training, or deployment claim is warranted.
- Next exact action: on a machine that can complete the model-artifact download, rerun `python inference.py --revision a10cc1512eabd3dde888204e902eca88bddb4951 --device cpu --max-samples 6 --max-new-tokens 96 --temperature 0`, validate the resulting report, then mark M5 complete before attempting LoRA execution.

## Session 8 report

- Milestone: 5 — **completed** with one real, bounded baseline measurement in this isolated workspace; this does not establish access to the user's computer.
- Inputs: `prepare_data.py --seed 42` generated the same 24/6/6 split. The six held-out test rows have SHA-256 `706756348bd549ee3db4f453189955b84950760a723751fd287b37134566dde7`.
- Environment: Python 3.11.16, PyTorch 2.14.1+cpu, no CUDA device, Transformers 4.57.6, and `HuggingFaceTB/SmolLM2-360M-Instruct` resolved and loaded at immutable revision `a10cc1512eabd3dde888204e902eca88bddb4951`.
- Result: greedy decoding (`max_new_tokens=96`, `temperature=0`) completed for all six prompts. The ignored `outputs/baseline.json` recorded a 14.302741-second median and 12.300894-second mean latency, 361,821,120 unique parameters, and 1,447,284,480 parameter bytes. All six responses were nonempty.
- Limitations: this small held-out set is not independent evidence of quality or generalization, CPU RSS snapshots are not peak CPU memory, and a single local CPU run is not a deployment benchmark. No adapter training, comparative evaluation, or public deployment occurred.
- Next milestone: execute the guarded LoRA experiment only after revalidating this matching baseline report and the pinned revision; do not mark M6 complete until an actual adapter run succeeds.

## Session 9 report

- Milestones: 6–7 — **completed** with one truthful, bounded CPU LoRA integration run in `C:\\Users\\Saman\\Documents\\Projects\\tiny-llm-hf`. The checkout was synchronized to `d6ee408` first; no access to any other user computer is claimed.
- Inputs: regenerated deterministic 24/6/6 splits, then reran all six baseline prompts at revision `a10cc1512eabd3dde888204e902eca88bddb4951`. The baseline and training reports agree on the test split SHA-256 `706756348bd549ee3db4f453189955b84950760a723751fd287b37134566dde7` and source SHA-256 `92ffc379ffe09d71052d9a7cfc9c9b4fe740c540cb7955e4347e2f646bef151f`.
- Environment: Python 3.11.16, PyTorch 2.14.1+cpu, Transformers 4.57.6, CPU only. The configured LoRA rank 8/alpha 16/dropout 0.05 targets `q_proj` and `v_proj`; execution used one epoch, batch size 1, gradient accumulation 4, and the hard six-step limit.
- Result: 819,200 of 362,640,320 parameters were trainable. Training completed in 43.5369 seconds (0.138 steps/second), with train loss 3.27303 and validation loss 3.39398. The ignored adapter directory and `outputs/train_lora.json` were created successfully.
- Limitations: the losses are not a quality comparison, no adapted test evaluation has run, the 36 authored rows are too small for generalization claims, and no public model or Space deployment occurred.
- Next milestone: compare the base model and adapter on the held-out prompts with an explicit evaluation protocol before making any quality claim.

## Session 10 report

- Milestone: 8 — **completed**. Added `evaluate.py`, `src/tinydevassist/evaluation.py`, focused offline tests, and [`docs/evaluation.md`](evaluation.md).
- Protocol: the evaluation verifies the held-out split hash and pinned revision, reuses the measured base report, generates every adapter response with greedy decoding, and saves a machine-readable ignored paired report without inventing an automatic quality score.
- Result: all six base and six adapter responses were nonempty at revision `a10cc1512eabd3dde888204e902eca88bddb4951`; base mean latency was 9.519711 seconds and adapter mean latency was 10.301151 seconds. The shared test SHA-256 was `706756348bd549ee3db4f453189955b84950760a723751fd287b37134566dde7`.
- Limitations: the six held-out prompts originate from the same 36-row authored seed and are not independent generalization evidence. No quality winner, model publication, or deployment is claimed.
- Next milestone: refine inference controls and curate examples, including transparent good/bad-generation review.

## CI repair

- Reproduced the GitHub failure with the workflow's exact Ruff command on Python 3.11. Fixed UTC alias, import order, notebook import placement, and existing formatting drift across source, tests, and notebooks.
- The notebook data exploration cell now imports the installed package directly, matching the documented editable install.
- Verified `python -m ruff check .`, `python -m ruff format --check .`, and the offline test suite locally before commit. This repair does not change model weights or experiment reports.
- The pushed repair `e9a02c229727af8a2550f40416b9220da3152c48` passed [GitHub Actions run 40577541798](https://github.com/samanshahroudi/tinydevassist/actions/runs/40577541798).

## Deployment preparation

- Added a bounded Gradio interface, public inference smoke script, CPU Docker Space files, model card, and an explicit allowlist publisher. See [`deployment.md`](deployment.md).
- The local Hugging Face CLI reported no authenticated account and no `HF_MODEL_REPO` or `HF_SPACE_REPO` environment variables were set. Exact repository IDs and a local `hf auth login` are required to publish; no public model or Space exists from this work yet.
- Gradio 5.50.0 with Hugging Face Hub 0.36.2 resolved against Transformers 4.57.6. The local UI instantiated successfully, `pip check` found no broken requirements, and a local HTTP plus real adapter inference smoke test returned a nonempty response.
- Docker Desktop's Linux daemon was unavailable during the build check, so the container itself remains unverified. The public upload and Space build remain pending Hugging Face login and exact repository IDs.

## Inference review

- Milestone 9 — **completed**. Documented a text inspection of all six held-out response pairs in [`qualitative_review.md`](qualitative_review.md). The adapter invented `psutil.memory_profiler`, gave a misleading Git history command, and suggested a premature pod restart. A `KeyError` definition was understandable but incomplete. No quality improvement is claimed.
- Added a tokenized prompt plus completion preflight limit of 512 tokens, matching the training sequence budget. Longer requests receive a clear error instead of silent truncation. The existing Gradio interface retains its bounded generation controls and four curated example questions.
- Next: finish deployment verification when Hugging Face authentication and exact repository IDs are available. Docker container verification also remains pending a working Linux daemon.

## Documentation reconciliation

- Milestone 13 — **completed**. The README and architecture now match the measured CPU baseline, six-step LoRA run, paired comparison, and local Gradio smoke. The qualitative review includes verbatim useful and incorrect adapter excerpts; the model card includes usage instructions, experiment hashes, and the actual quality boundary.
- The Hugging Face CLI again reported no login and no model or Space repository IDs were configured. Docker Desktop's Linux daemon remained unavailable. No public deployment or container build is claimed.
- Next: M14 CI and reproducibility audit; M11 container verification and M12 publication remain pending their prerequisites.

## Partial Hugging Face publication

- Confirmed the `lnxsam` Hugging Face login and the user-specified IDs `lnxsam/tinydevassist` and `lnxsam/tinydevassist-demo`. The curated nine-file model upload succeeded. An anonymous Hub query verified the public model at commit `7e21c7d08913bc0725ea3cf2c6b72b184f694572`, including 3,293,480-byte adapter weights. No model weights were added to Git.
- Creating the Docker Space failed with HTTP 402: Hugging Face requires a PRO subscription for Gradio/Docker Spaces on free `cpu-basic` for this account. An anonymous query confirmed that the Space does not exist. No public inference was run.
- Added a guarded Space-only resume mode and documented the exact command in [`deployment.md`](deployment.md). M12 remains incomplete until a Space builds and public inference passes; M11 container verification remains blocked by the unavailable local Docker daemon.

## Hugging Face account rename

- The authenticated CLI now reports `saman-shahroudi`. An anonymous Hub query resolved `saman-shahroudi/tinydevassist` to the same public model commit `7e21c7d08913bc0725ea3cf2c6b72b184f694572`; the model was not republished. The future Space ID under the new namespace remains uncreated.
- Updated current links and the Space-only recovery command to the canonical namespace. Application code already accepts repo IDs through `HF_MODEL_REPO` and `HF_SPACE_REPO`; neither is set in this shell. The Space is still blocked by the documented hosting requirement.

## Reproducibility and CI audit

- Milestone 14 — **completed**. Pinned the observed source and split SHA-256 values in the deterministic preparation test so CI catches unintended input changes. Baseline inference now refuses to overwrite an existing report before model loading. Reconciled first-baseline and comparison-baseline latency measurements in the README and development guide, and added exact reproduction commands with measured limits.
- The published adapter remains public; the Space has not been created because the account lacks the required hosting entitlement. CI does not download weights or claim end-to-end model verification.
- Next: M15 final link, documentation, and local behavior audit; M11/M12 hosting verification remains pending the external prerequisite.

## Verified ZeroGPU publication

- Milestones 11–12 — **completed through Gradio ZeroGPU**. The authenticated `saman-shahroudi` account created the public Space `saman-shahroudi/tinydevassist-demo` on `zero-a10g`; the existing model repository was reused after all nine curated files matched the local artifact by SHA-256.
- The first build exposed a PEFT adapter-loading issue under ZeroGPU CUDA emulation. Loading adapter safetensors on CPU before model placement fixed startup. The final published Space revision `d09419f3efb10526fd4bbe93a93ddeb83acfb83c` reached `RUNNING`; build/runtime logs showed base and adapter downloads and Gradio startup on port 7860.
- An anonymous `smoke.py` request to `https://saman-shahroudi-tinydevassist-demo.hf.space` returned HTTP 200 and a nonempty generated answer. One public request does not establish quality, quota headroom, or sustained reliability. The separate Docker CPU image has not been built or verified.
- Files: `deploy_zerogpu.py`, `space/zerogpu/`, `app.py`, `src/tinydevassist/evaluation.py`, `tests/test_app.py`, README, deployment/architecture/decision records, and model card. Next: M15 final audit and broader response evaluation.

## Final audit

- Milestone 15 — **completed**. Corrected stale dataset, model-selection, development, and README status text. The [audit report](final_audit.md) lists verified checks and remaining limits.
- The public model and ZeroGPU Space were anonymously confirmed, and a fresh hosted inference smoke returned HTTP 200 plus a nonempty response. The earlier deployment commit passed GitHub Actions; this audit commit requires its own CI check after push.
- Local quality gates, dry-run training plan, dependency diagnostic, and 49 relative Markdown links were checked. No full retraining or independent quality study was run during this audit.

## Evaluation integrity update

- Refined the README and supporting records to emphasize evaluation safeguards, measured results, and next research steps.
- Strengthened comparison report validation to reject duplicate prompt IDs and invalid latency/token measurements before aggregation; added offline regression cases. Historical measured results and published model artifacts were not changed.

## Portable CPU serving preparation

- Added a separate FastAPI JSON service, root OCI Dockerfile, pinned API dependency list, and build-context exclusions for deployments outside Hugging Face. The existing Gradio ZeroGPU Space remains the only verified public endpoint.
- Added bounded `/generate`, configuration-only `/healthz`, platform `PORT` support, optional `X-API-Key`, a portable API smoke script, and offline API tests. A real local adapter generated a nonempty HTTP response through the API. The [deployment guide](portable_deployment.md) records local commands, container requirements, and provider settings.
- A local Uvicorn server passed `smoke_api.py` with the real adapter, returning HTTP 200 and a nonempty answer. Docker Desktop's Linux daemon became available after startup. The root image built with a restricted source-only context; its container reported `healthy` and passed a real adapter HTTP inference smoke. A post-generation `docker stats` snapshot read 2.375 GiB (not peak). No Render, Railway, or Cloud Run deployment is claimed; each requires its own runtime logs and remote inference smoke.
