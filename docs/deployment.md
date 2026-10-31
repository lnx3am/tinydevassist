# Hugging Face deployment

For a separate CPU HTTP service that can run on multiple container platforms,
see the [portable API guide](portable_deployment.md). The public deployment
verified below remains the Gradio ZeroGPU Space.

## Verified public release

- [PEFT adapter and model card](https://huggingface.co/saman-shahroudi/tinydevassist)
- [Gradio ZeroGPU Space](https://huggingface.co/spaces/saman-shahroudi/tinydevassist-demo)
- Space revision verified: `d09419f3efb10526fd4bbe93a93ddeb83acfb83c` on `zero-a10g`, status `RUNNING`.
- An anonymous `python smoke.py --url https://saman-shahroudi-tinydevassist-demo.hf.space` returned HTTP 200 and a nonempty generated answer. This verifies one public inference request, not sustained availability or response quality.

The Space loads the public adapter over the pinned `SmolLM2-360M-Instruct` base model. Its curated upload contains only the Gradio entry point, shared app and inference modules, metadata, and dependencies. The adapter weights remain in the model repository; no weights or experiment reports are committed to GitHub. `HF_MODEL_REPO` is a public Space variable set to `saman-shahroudi/tinydevassist`. The ZeroGPU image uses Python 3.12.12, Gradio 5.50.0, and PyTorch 2.13.0. The model is placed on CUDA at Space startup and generation runs under `@spaces.GPU(duration=60)`; PEFT adapter tensors must first load on CPU before ZeroGPU placement.

## Reproduce locally

```powershell
python -m pip install -e '.[app,dev]'
$env:TINYDEVASSIST_ADAPTER_PATH='checkpoints/tinydevassist-lora'
python app.py
# In another shell:
python smoke.py --url http://127.0.0.1:7860
```

The ZeroGPU publisher has a dry run and requires exact repository IDs. For an existing model and an existing Gradio ZeroGPU Space, it compares every curated published model file to the local artifact by SHA-256 before upload. It refuses a missing or mismatched model. Authenticate with `hf auth login` locally; never place tokens in arguments, logs, Git, or chat.

```powershell
python deploy_zerogpu.py --model-repo saman-shahroudi/tinydevassist --space-repo saman-shahroudi/tinydevassist-demo
python deploy_zerogpu.py --model-repo saman-shahroudi/tinydevassist --space-repo saman-shahroudi/tinydevassist-demo --execute
python smoke.py --url https://saman-shahroudi-tinydevassist-demo.hf.space
```

The Space repository must already exist with SDK `gradio` and requested hardware `zero-a10g`; a fresh Space can be created through the Hub UI or API after confirming account entitlement. The publisher does not create or replace the model. A successful upload alone does not confirm a healthy build: inspect Space build/runtime logs and run the public smoke test. Free ZeroGPU has per-user GPU quotas and may queue or reject requests after quota exhaustion; do not treat one pass as an uptime guarantee. The 36-example authored seed and six held-out prompts cannot establish answer quality or generalization.

## Earlier Docker route

The original Docker Space attempt on `cpu-basic` returned HTTP 402, requiring PRO for that account at the time. The repository retains `space/Dockerfile`, `space/README.md`, and `deploy_hf.py` as an alternate Gradio path; that specific image has not been built or deployed. The separate root `Dockerfile` packages the locally verified portable CPU API. The verified public demo still uses Gradio ZeroGPU.
