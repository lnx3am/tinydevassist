# Architecture decision records

## ADR-001 — A narrow developer-support assistant

- **Decision:** Build TinyDevAssist for concise Git/Python/API/backend-support answers.
- **Context:** A 3-day, laptop-sized project must still demonstrate the complete ML lifecycle.
- **Alternatives considered:** General coding chatbot, customer-service assistant, documentation retrieval service.
- **Reason:** Task breadth can be controlled and measured on small labeled examples; topic aligns with backend engineering.
- **Consequences:** Limited domain, modest expected answer quality, explicit failure analysis required.

## ADR-002 — SmolLM2-360M-Instruct and LoRA as the initial candidate

- **Decision:** Start with `HuggingFaceTB/SmolLM2-360M-Instruct` and LoRA adapters, subject to licensing and hardware checks.
- **Context:** The project must run on a personal computer and serve via CPU Space.
- **Alternatives considered:** TinyLlama 1.1B, larger 1B+ models, full fine-tuning.
- **Reason:** Smaller inference footprint and efficient parameter adaptation.
- **Consequences:** Lower capacity than larger models; determine actual runtime and response quality empirically.

## ADR-003 — Docker-hosted Gradio interface

- **Decision:** Target a Docker Space on port 7860 after local verification.
- **Context:** Users need a reproducible demo with pinned runtime dependencies.
- **Alternatives considered:** Standard Gradio Space, external GPU endpoint.
- **Reason:** A Dockerfile exposes environment and runtime design without requiring paid GPU serving.
- **Consequences:** Must validate CPU latency/memory and provide a health/smoke check.

## ADR-004 — Treat experimental artifacts as unverified until measured

- **Decision:** Label training and deployment status explicitly, never fabricate measurements or URLs.
- **Context:** Training depends on hardware and deployment on external authentication.
- **Alternatives considered:** Publishing demo placeholders as results.
- **Reason:** Accurate project records and reproducibility.
- **Consequences:** Missing experiments and blockers remain visible in README and reports.

## ADR-005 — Lightweight package core with optional ML extras

- **Decision:** Package the project using a `src/` layout, setuptools, Python 3.11 as the ML target, and separate `dev`, `train`, and `app` dependency groups.
- **Context:** The baseline CI and developer tooling should run quickly without downloading PyTorch and model artifacts; GPU and CPU deployment have different requirements.
- **Alternatives considered:** A single requirements file with every ML library, Poetry-only packaging, a pinned CUDA wheel in the repository.
- **Reason:** Optional extras make the code importable and testable on ordinary machines while allowing independent runtime environments.
- **Consequences:** Training and serving dependencies are not yet resolved to a tested lockfile; dependency compatibility must be confirmed during implementation and experimentation.

## ADR-006 — Offline environment doctor and lightweight CI

- **Decision:** Add an offline `tinydevassist doctor` diagnostic, Ruff/pytest checks, and a GitHub Actions quality job on Python 3.11.
- **Context:** Each milestone needs quick verifiable quality gates before costly model downloads or training.
- **Alternatives considered:** Downloading the model as a CI smoke test, running a full training step in CI, skipping checks until inference exists.
- **Reason:** Fast deterministic checks are affordable and do not require secrets or specialized hardware.
- **Consequences:** Passing the current CI does not prove ML dependency compatibility, training, inference, or deployed Space health; these require separate later checks.

## ADR-007 — Original, transparent seed dataset instead of externally scraped Q&A

- **Decision:** Track 36 newly authored illustrative developer-support pairs in `data/samples/developer_support_v1.jsonl`, under Apache-2.0, with a dataset card and stable IDs.
- **Context:** The project needs a small legally redistributable dataset and an auditable starting point within three days. External Q&A corpora can contain third-party rights, personal information, and mixed licensing.
- **Alternatives considered:** Stack Overflow exports, GitHub issue threads, public technical-support corpora, or untracked synthetic data.
- **Reason:** Explicitly authored examples avoid unverifiable scraping provenance, are small enough to inspect, and allow the pipeline to be tested without network access.
- **Consequences:** Drafted with language-model assistance, the examples require independent technical review; 36 rows are insufficient for meaningful generalization claims. An independent held-out evaluation set is still needed. No train/validation/test split exists yet.

## ADR-008 — Verify upstream model metadata before downloading weights

- **Decision:** Retain `HuggingFaceTB/SmolLM2-360M-Instruct` as the candidate and record its official Apache-2.0 license, English focus, chat-template usage, and limitations in `docs/model_selection.md`.
- **Context:** Model metadata can be checked independently of local GPU and package availability.
- **Alternatives considered:** Switching immediately to TinyLlama 1.1B or SmolLM2-135M-Instruct; downloading the model before documenting license and scope.
- **Reason:** The 360M class balances capacity with a smaller anticipated serving footprint, while retaining an explicit upstream license.
- **Consequences:** No inference, training, memory, or latency claims are made. The floating `main` revision must be resolved to a commit SHA before a reproducible experiment.

## ADR-009 — Deterministic, stratified small-data splits and chat messages

- **Decision:** Normalize source rows (NFC/whitespace), reject ambiguous duplicate answers and near-duplicate questions, deduplicate identical questions/answers, and split by category with seed 42. Store generated JSONL and a SHA-256 manifest outside Git. Encode SFT examples as role/content messages, not hard-coded model tokens.
- **Context:** The 36-row project-authored seed needs reproducible preprocessing, leakage checks, and a clean contract for later Transformers/TRL training.
- **Alternatives considered:** Unseeded random splits, a single global random split, committing derived datasets, manually concatenating chat tokens, and silently removing similar but potentially distinct questions.
- **Reason:** Per-category stratification retains coverage in all three splits; hashing and stable ordering support auditability; rejecting near-duplicates avoids accidental leakage and data loss; tokenizer chat templates preserve model-specific formatting.
- **Consequences:** The current seed produces 24/6/6 rows (4/1/1 per category). Near-duplicate detection is heuristic and may need manual review for larger datasets. Generated files must be regenerated after source changes. Held-out rows from one authored source do not constitute an independent generalization benchmark.

## ADR-010 — Baseline measurements before adapter training

- **Decision:** Add a lazy-loaded Transformers baseline with the upstream chat template, deterministic greedy decoding by default, held-out test prompts, and machine-readable ignored JSON results; keep model experiments out of lightweight CI.
- **Context:** A credible LoRA comparison requires measured pre-adaptation generations and resource data, but the current workspace has no Transformers package, no model weights, and no network access to Hugging Face.
- **Alternatives considered:** Inventing sample responses, using a mocked model as a benchmark, downloading a different available model, and running inference during every CI job.
- **Reason:** The baseline implementation can be offline-tested with fakes while actual measurements remain explicitly blocked until the chosen weights are accessible. The unmodified model must be evaluated before training.
- **Consequences:** `outputs/baseline.json` is created only after successful real inference; tests using fakes do not establish quality or performance. CPU process RSS snapshots are not peak memory; CUDA peak allocation is separately recorded. Use a pinned model revision and document hardware before publishing results.

## ADR-011 — Experimental notebooks alongside production scripts

- **Decision:** Maintain numbered notebooks for dataset exploration and measured experiments; notebooks call project functions/CLIs instead of reimplementing inference and training. Commit only verifiable outputs.
- **Context:** The project needs inspectable analysis, plots, and methodology in addition to runnable scripts.
- **Alternatives considered:** Notebooks as the only implementation, empty placeholder notebooks, or no notebooks at all.
- **Reason:** A reusable CLI provides reproducibility while notebooks communicate analysis and limitations.
- **Consequences:** Notebook 01 is executed on the tracked 36-row dataset. Notebook 02 is executed only in explicit skip mode because real model inference is blocked. Later training/evaluation notebooks require measured artifacts before reporting findings.

## ADR-012 — Guarded, assistant-only LoRA SFT with strict provenance

- **Decision:** Use Transformers Trainer and PEFT LoRA, keeping the ML imports lazy and the CLI dry-run-only by default. Mask system/user tokens and padding from the causal-LM loss; use only train/validation splits during adaptation. Require a 40-character upstream model SHA and a matching measured baseline on all held-out test prompts before `--execute`.
- **Context:** The previous milestone's inference implementation exists, but actual baseline inference is blocked in this runtime; model weights and Transformers/PEFT are unavailable. The 36-row dataset is small and may overfit.
- **Alternatives considered:** TRL SFTTrainer (version-dependent formatting/label behavior), training on prompt tokens, executing from a floating `main` revision, or training without baseline comparison.
- **Reason:** An explicit, tested label mask and strict hashes make accidental prompt-loss training or data leakage less likely. A minimal Trainer/PEFT stack avoids TRL version-dependent APIs while preserving adapter-only saves.
- **Consequences:** The config, CLI, and notebook are **implementation only**, not proof of training. Real tokenizer/chat-template compatibility, adapter loading, GPU memory, loss, and evaluation remain to be verified. The hard step cap and opt-in execution limit accidental long runs.

## ADR-013 — Record the first baseline as a bounded CPU measurement

- **Decision:** Mark the baseline measurement objective complete only for the six held-out prompts at upstream revision `a10cc1512eabd3dde888204e902eca88bddb4951`; keep the raw report ignored and document its environment and aggregate results.
- **Context:** A real run completed on Python 3.11.16 with PyTorch 2.14.1+cpu after the repository's earlier isolated environments could not obtain the model artifacts. It used greedy decoding, a maximum of 96 new tokens, and no CUDA device.
- **Alternatives considered:** Reporting mocked results, treating the tiny held-out split as a quality benchmark, committing the full generation report, or claiming a CPU serving SLA.
- **Reason:** The matching base-model evidence is now sufficient for the guarded LoRA entry gate, while the small authored split and a single machine are not sufficient for broader quality or operational claims.
- **Consequences:** The report's 14.303-second median and 12.301-second mean per-prompt latency, 361,821,120 unique parameters, and 1,447,284,480 parameter bytes are reproducibility evidence only. Adapter training, comparative evaluation, and deployment remain unverified.

## ADR-014 — Execute one bounded adapter-training integration run

- **Decision:** Execute the guarded LoRA configuration once on CPU at the same immutable base-model revision as the measured baseline, then retain adapter weights and raw reports outside Git.
- **Context:** The verified baseline, deterministic 24/6/6 split, matching hashes, installed ML dependencies, and explicit six-step cap satisfied the training CLI's fail-closed entry gates.
- **Alternatives considered:** Extending training until loss improved, changing hyperparameters after seeing the first loss, training on test rows, committing adapter weights, or claiming quality improvement without base-versus-adapter evaluation.
- **Reason:** A single short run validates model loading, chat-template tokenization, LoRA attachment, assistant-only loss masking, optimizer steps, validation, and adapter serialization while limiting cost and overfitting risk for a 24-row training set.
- **Consequences:** The completed run trained 819,200 adapter parameters for six steps, with 3.27303 training loss and 3.39398 validation loss. Those losses are diagnostic outputs, not evidence of usefulness or improvement; a controlled base-versus-adapter evaluation is still required.

## ADR-015 — Compare complete held-out generations without an invented quality score

- **Decision:** Evaluate the base report and adapter on every held-out prompt at the same pinned revision, reporting coverage, latency, token counts, and paired raw responses while leaving response-quality scoring null.
- **Context:** The project has six held-out prompts from the same tiny authored seed set. Automatic lexical similarity or a self-judged score would not be meaningful evidence of developer-support quality.
- **Alternatives considered:** Declaring the lower-loss adapter superior, scoring with an unrelated language model, using a single anecdotal prompt, or skipping comparison until a large benchmark exists.
- **Reason:** A strict paired generation report validates that both artifacts execute under identical decoding controls, exposes the actual text for review, and preserves an honest boundary around what this data can show.
- **Consequences:** The first CPU comparison completed all six prompts for both models, but does not select a winner. Independent questions and human technical review remain required before any quality or safety claim.

## ADR-016 — Package the adapter and CPU Space with explicit upload manifests

- **Decision:** Publish the PEFT adapter as a model repository and serve it from a Docker Gradio Space using a pinned base revision and a curated file manifest.
- **Context:** The local adapter is only a few megabytes, while the base model remains upstream; the project needs a reproducible, CPU oriented demo without committing weights to GitHub. The current Gradio 6 major release requires a Hugging Face Hub dependency incompatible with the measured Transformers 4.57.6 stack.
- **Alternatives considered:** Commit weights to GitHub, merge and upload a full base model, use a floating base revision, or let an upload command scan the entire local repository.
- **Reason:** An explicit file list keeps reports, credentials, training arguments, and local caches out of the public repositories. Gradio 5.50.0 and Hugging Face Hub 0.36.2 resolve with the measured Transformers stack; a CPU PyTorch wheel keeps the Docker image focused on CPU serving.
- **Consequences:** Publication requires authenticated Hugging Face access and exact model and Space repository IDs. Upload success is separate from a healthy Space build and public inference; each must be checked before claiming deployment.

## ADR-017 — Bound demo context and publish observed response failures

- **Decision:** Reject generation requests whose tokenized chat prompt plus requested completion exceeds the 512-token training sequence budget, and publish a text inspection of all six held-out response pairs.
- **Context:** The Gradio demo exposes a configurable 16–256 completion-token range. The measured adapter supplied fabricated API usage and misleading Git and operations guidance on the small held-out set.
- **Alternatives considered:** Silent prompt truncation, allowing requests beyond the training budget, claiming a quality score from six authored prompts, or showing only favorable generations.
- **Reason:** A preflight rejection gives users a clear way to shorten the request while preserving their original question. Showing specific failures gives the demo and model card a checkable limitation.
- **Consequences:** Some longer questions require fewer requested new tokens or cannot be served through the demo. The text inspection is descriptive and cannot estimate generalization or an error rate.

## ADR-018 — Reconcile project documentation with measured evidence

- **Decision:** Replace early planning claims in the README and architecture with the actual bounded CPU experiment status, and add short verbatim response examples and reproducibility hashes to the review and model card.
- **Context:** Early pages still said that no model had been downloaded, trained, or evaluated, while later pages recorded a six-step training run and paired held-out comparison.
- **Alternatives considered:** Leave the historical planning text intact, remove the early sections entirely, or claim independent quality from the small authored split.
- **Reason:** A reader should find one consistent account of what executed, what was measured, and what still requires public verification.
- **Consequences:** The documentation now distinguishes local experiment evidence from deployment and independent quality validation; it must be updated again when a public Space is actually verified.

## ADR-019 — Resume a partial Hub publication only after verifying the model

- **Decision:** Keep the published adapter repository intact and add a `--space-only` recovery mode that hashes each public model file against the local curated manifest before attempting Space creation.
- **Context:** The authenticated model upload succeeded, but Space creation returned HTTP 402 because this account lacks the required PRO hosting entitlement. Repeating the original publisher would fail on the already existing model repository.
- **Alternatives considered:** Delete and recreate the model, overwrite it without comparison, silently ignore the partial state, or publish an unverified static page in place of inference.
- **Reason:** Hash verification makes the resume step safe and reproducible, and an explicit Space-only path avoids replacing the verified model artifact.
- **Consequences:** A subscription or other confirmed hosting entitlement is still required. The resume command refuses to proceed if any published file differs from the local artifact; Space build and inference must be checked separately after creation.

## ADR-020 — Use the canonical Hub namespace after the account rename

- **Decision:** Update current model links and future deployment commands from `lnxsam` to `saman-shahroudi`, while retaining the earlier namespace only in historical execution notes.
- **Context:** The authenticated CLI reports the new username, and an anonymous Hub query resolves `saman-shahroudi/tinydevassist` to the same public model commit. The app and publisher already read repository IDs from environment variables or command-line arguments.
- **Alternatives considered:** Continue using the former namespace through redirects, hard-code the new name in application code, or republish the adapter as a second model.
- **Reason:** Canonical IDs are clearer for users and future deployment without duplicating model weights or changing the tested application behavior.
- **Consequences:** Any previously configured `HF_MODEL_REPO` or `HF_SPACE_REPO` value outside this workspace must be updated separately. The planned Space remains unpublished and subject to the hosting entitlement blocker.

## ADR-021 — Pin the measured data hashes in CI and state experiment limits

- **Decision:** Assert the measured source and train/validation/test hashes in the deterministic data-preparation test, refuse to overwrite an existing baseline report, and put exact reproduction commands and measured limits in the README.
- **Context:** The existing test checked repeatability but would pass after an unintended source or split change. Baseline inference could silently replace an earlier report, and early documentation described the first run without explaining the later matching rerun used for evaluation.
- **Alternatives considered:** Trusting counts alone, committing generated split files, adding a heavyweight model run to CI, or describing the project as a public deployed assistant.
- **Reason:** Hash assertions catch accidental changes to the experiment input without model downloads; refusing report replacement protects provenance. The README should describe only verified results and known limits.
- **Consequences:** Intentional dataset edits require a reviewed hash update and a new experiment. CI remains lightweight; it cannot verify model loading or public inference.

## ADR-022 — Serve the published adapter through Gradio ZeroGPU

- **Decision:** Publish the existing adapter in a Gradio ZeroGPU Space, with a curated upload manifest and an eager CUDA model placement followed by GPU-decorated generation. Load PEFT adapter tensors on CPU before placement.
- **Context:** A Docker Space on `cpu-basic` returned HTTP 402 for this account. The authenticated account could create a Gradio Space requesting `zero-a10g`. The first ZeroGPU build exposed a PEFT safetensors load failure under startup CUDA emulation; explicit CPU loading fixed it.
- **Alternatives considered:** Upgrade to PRO for the Docker route, wait without a demo, publish a static page without inference, or change the local CPU app into a ZeroGPU-only entry point.
- **Reason:** The Gradio SDK uses the account's available free ZeroGPU entitlement and reuses the verified public adapter. A separate Space entry point preserves the tested local CPU behavior. Pinning the hosted Python, Gradio, and PyTorch versions makes the runtime more reproducible.
- **Consequences:** The public Space built and one anonymous inference returned a nonempty response. ZeroGPU queues and quota limits may affect future requests; one pass does not establish uptime or quality. The Docker variant remains unverified.

## ADR-023 — Validate evaluation measurements before aggregation

- **Decision:** Reject duplicate or blank evaluation IDs and require nonnegative, finite latency and integer token counts before building the comparison report.
- **Context:** The earlier report builder accepted duplicate rows, negative measurements, fractional token counts, and booleans as numbers. These values could produce misleading aggregate metrics even when generation itself succeeded.
- **Alternatives considered:** Trust the caller, silently drop invalid rows, or coerce values to numbers.
- **Reason:** Explicit rejection keeps reported sample counts and averages tied to valid, distinct observations.
- **Consequences:** Malformed input now fails with a clear error; the previously recorded six-row comparison remains unchanged and was not rerun for this validation change.

## ADR-024 — Package a separate portable CPU inference API

- **Decision:** Add a root OCI Dockerfile and FastAPI JSON service that reuse the existing pinned CPU adapter generator, bind to the platform's `PORT`, expose `/healthz` and `/generate`, serialize generation per process, and optionally require an API key.
- **Context:** The verified Gradio ZeroGPU Space is tied to Hugging Face's GPU runtime. A container interface gives the project a deployment path for other platforms without changing the public demo or the measured model.
- **Alternatives considered:** Repurpose the Gradio Space image, duplicate inference logic for each provider, or include model weights and credentials in the image.
- **Reason:** One shared inference implementation avoids diverging prompt and decoding behavior. A small HTTP contract and root Dockerfile map to common container services, while an explicit `.dockerignore` keeps checkpoints and secrets out of remote build contexts.
- **Consequences:** CPU serving still needs sufficient memory and cold-download time. `/healthz` checks configuration only; generation must be verified separately after deployment. The image built locally and generated a nonempty answer from the public adapter; Render, Railway, and Cloud Run remain unverified.
