# Held-out base-versus-adapter evaluation

## Protocol

The evaluation CLI compares the unmodified base-model report with a locally
loaded LoRA adapter on every row in the deterministic held-out test split. It
requires the same immutable model revision and test-input SHA-256 as the
baseline report, uses greedy decoding (`temperature=0`, `max_new_tokens=96`),
and refuses to overwrite an existing report.

```bash
python prepare_data.py --seed 42
python inference.py --revision a10cc1512eabd3dde888204e902eca88bddb4951 --device cpu
python train_lora.py --revision a10cc1512eabd3dde888204e902eca88bddb4951 --execute
python evaluate.py --revision a10cc1512eabd3dde888204e902eca88bddb4951 --device cpu
```

The raw report is written to ignored `outputs/evaluation.json`; it contains
both response sets, per-generation latency/token counts, methodology, and the
exact held-out-input hash. It does not create an automatic response-quality
score: the six project-authored prompts are too small and not independent.
Report construction rejects duplicate prompt IDs, negative or nonfinite latency,
and invalid token counts before computing aggregate metrics.

## Measured comparison (2026-10-27)

The base and adapter were compared on all six held-out prompts with test SHA-256
`706756348bd549ee3db4f453189955b84950760a723751fd287b37134566dde7`, base model
`HuggingFaceTB/SmolLM2-360M-Instruct`, revision
`a10cc1512eabd3dde888204e902eca88bddb4951`, Python 3.11.16, and PyTorch
2.14.1+cpu.

| Measure | Base | LoRA adapter |
| --- | ---: | ---: |
| Prompts completed | 6/6 | 6/6 |
| Nonempty responses | 6/6 | 6/6 |
| Mean latency | 9.520 s | 10.301 s |
| Mean generated tokens | 81.833 | 80.500 |

These figures prove that both paths generated responses in this CPU
environment; they do **not** prove that the adapter is more accurate, safer, or
generally useful. A larger independently sourced evaluation set and human
review are required before making that claim.

See [text inspection of all six held-out responses](qualitative_review.md)
for representative useful and incorrect answers. The adapter fabricated a
`psutil` API in one answer and gave misleading Git and operations guidance in
others. This review is an inspection of the same small authored split, not an
independent quality assessment.
