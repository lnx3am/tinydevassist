# Portable CPU API deployment

The root `Dockerfile` packages a separate FastAPI service for a CPU container
platform. It does not replace the [public Gradio ZeroGPU demo](deployment.md).
The service downloads the public PEFT adapter from `HF_MODEL_REPO` on its first
generation request and loads the pinned upstream base revision. It runs one
Uvicorn worker, serializes generation within the process, binds to `0.0.0.0`,
and reads the platform-provided `PORT` (default `8080`). The image runs as a
non-root user, excludes local checkpoints and secrets from the build context,
and exposes a configuration-only `/healthz` probe.

## API contract

`POST /generate` accepts JSON with `prompt` (up to 2,000 characters),
`temperature` (0–1, default 0), and `max_new_tokens` (16–256, default 96).
It returns `{"response": "..."}`. Invalid input returns HTTP 422. Model
loading or runtime failure returns HTTP 503 without exposing an internal error.
Set `TINYDEVASSIST_API_KEY` as a platform secret to require an `X-API-Key`
header for generation; if unset, the endpoint is public. `/healthz` returns
200 once an adapter location is configured, or 503 otherwise. It does **not**
download weights or prove that the model can generate; test `/generate` after
each deployment. The API also has FastAPI's `/docs` page.

## Run locally

```powershell
python -m pip install -e '.[api]'
$env:HF_MODEL_REPO='saman-shahroudi/tinydevassist'
python api.py
# In another shell:
Invoke-RestMethod http://127.0.0.1:8080/healthz
Invoke-RestMethod http://127.0.0.1:8080/generate -Method Post -ContentType application/json -Body '{"prompt":"How do I inspect my Git working tree?","max_new_tokens":64}'
python smoke_api.py --url http://127.0.0.1:8080
```

Use `TINYDEVASSIST_ADAPTER_PATH` instead of `HF_MODEL_REPO` for a local ignored
adapter directory. The public adapter needs no Hugging Face token. Keep any
optional API key in a local environment or platform secret store, never in Git.

## Build and run the same image

```powershell
docker build -t tinydevassist-api .
docker run --rm -p 8080:8080 -e HF_MODEL_REPO=saman-shahroudi/tinydevassist tinydevassist-api
# In another shell:
python smoke_api.py --url http://127.0.0.1:8080
```

The CPU baseline measured about 1.45 GB of parameter bytes and roughly
1.8 GB process RSS after generation. Start with at least 4 GB container memory
and adjust from observed peak usage, startup time, and traffic. Cold starts
include model downloads unless the platform provides a persistent cache.
Configure one concurrent request per instance where the platform supports it;
generation is serialized within one process to avoid simultaneous model use.
The local Uvicorn server served a real adapter inference request and the
`smoke_api.py` check returned HTTP 200 with a nonempty answer. Docker Desktop's
Linux daemon became available after startup; `docker build` then succeeded.
The image ran as a container with the public adapter ID, reported `healthy`,
and passed the same bounded inference smoke over its published port. A single
`docker stats` snapshot after generation showed 2.375 GiB memory usage; this
is not peak memory. The build context included only the explicitly allowed
source files, with local weights and secrets excluded by `.dockerignore`.
The verified local image was built for Linux/amd64; other architectures have
not been tested.
No external platform deployment or public API inference has been verified.

After publishing on any platform, run `python smoke_api.py --url <service-url>`
from another machine or network. The script checks `/healthz` and makes one
bounded generation request without printing the answer. If API key protection
is enabled, set `TINYDEVASSIST_API_KEY` in the caller's environment first.
Inspect container logs and resource usage after this smoke check.

## Platform configuration

| Platform | Setup using the same Dockerfile |
| --- | --- |
| [Render](https://render.com/docs/docker) | Create a Docker web service from this repository, set `HF_MODEL_REPO`, use `/healthz` as the HTTP health check, and choose memory sufficient for the measured model footprint. Render binds web services to the supplied `PORT`. |
| [Railway](https://docs.railway.com/builds/dockerfiles) | Create a service from this repository; Railway detects the root Dockerfile. Set `HF_MODEL_REPO`, configure `/healthz` as the deployment health check, and enable a public domain if desired. Railway supplies `PORT`. |
| [Google Cloud Run](https://docs.cloud.google.com/run/docs/container-contract) | Build and deploy this OCI image in a Google Cloud project, set `HF_MODEL_REPO`, allocate enough memory, set concurrency to one, and allow time for a cold model download. Cloud Run supplies `PORT` and requires binding to `0.0.0.0`. |

For private deployments, use the platform's secret storage for
`TINYDEVASSIST_API_KEY` and restrict ingress as appropriate. Platform plans,
prices, quotas, and available memory change; verify them before provisioning.
No Render, Railway, or Cloud Run deployment is claimed here.
