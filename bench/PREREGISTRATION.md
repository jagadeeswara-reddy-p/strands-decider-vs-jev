# Pre-registration: Strands Decider v19 vs TypeSafe Jev 1.13.0

Frozen 2026-10-05, after the 10-item dry run and **before** any full-run results were seen.
Internal publication only (TypeSafe ToS checked by owner).

## Frozen artefacts

| Artefact | SHA-256 |
|---|---|
| `common/tasks.py` (all B2–B6 prompts, sampling, label sets) | `d032ec45a3a22f5a8f7a7cb2b54527b2aa33548b4f1476c9af53188d16c52ecb` |
| `common/task.py` (answer parsing) | `0e9f517dd9c80ba93eff2cf090ba6ef51768eab264eeed4032b9a50074532e11` |
| JevBench harness | `fstandhartinger/jevbench` @ `1bcc55eb6c8cffde2306b3db03ede39b61c6152a`, unmodified |

No prompt may change after this point. Any re-run after a code change gets a new run id and is
reported as such.

## Systems

- `decider`: `StrandsAgents/strands-decider-2B-hobson-v19` on `Qwen/Qwen3.5-2B-Base`, `strands-decider`
  0.1.0 + `flash-linear-attention` 0.5.2, CUDA on EC2 g6.xlarge (L4), `max_length` 4096, prefix cache on.
- `jev`: `https://api.typesafe.ai/v1/systemone`, `model: jev-latest` → reports `jev-1.13.0`.
  If the reported version changes mid-run, results are split by version.

## Run protocol

- Run id `full-2026-10-05`. Seed 0. Full test sets (B2 3,652 ×2 wordings; B3 3,080; B4 5,500;
  B5 116 ×2 wordings; B6 1,000 sampled items from 500 seeded rows; B1 231 tasks).
- Concurrency 4 for both backends for the accuracy runs. Decider gets 5 warm-up requests per task,
  not recorded.
- Latency is reported from a **separate sequential probe** (concurrency 1, 200 Banking77 items per
  backend) so queueing does not inflate it: decider server-side `latency_ms` and end-to-end; Jev
  end-to-end only. End-to-end numbers are from a laptop in India via an SSM tunnel (decider) and
  over the internet (Jev) — not comparable to each other, stated as such.
- Items that error after 6 retries are reported as errors, excluded from accuracy, and counted.
- Budget cap ~$4 total for the study; if reached, runs stop and partial results are reported as partial.

## Primary metrics

Per benchmark: accuracy with bootstrap 95% CI; macro-F1; ECE (10 bins, top-label) and Brier;
coverage and accuracy at confidence ≥ 0.8 / 0.9 / 0.95 (confidence = max class probability).
Paired difference: exact McNemar on items both answered. α = 0.05, no multiple-comparison
correction across benchmarks (6 primary comparisons; reported as such).

Task-specific: When2Call macro-F1 over the 3 gold categories, tool-hallucination rate, answer
(“direct”) hallucination rate. CLINC in-scope accuracy, OOS recall/precision, OOS by confidence
threshold. Injection / HaluEval F1 on positive class, AUROC from P(true), false-positive rate.

## Hypotheses

- **H1** JevBench public: `jev` > `decider` overall (published 0.866 vs 0.723), significant by McNemar;
  the gap is concentrated in the hard tier.
- **H2** When2Call (neutral wording): `decider` macro-F1 within 5 points of `jev`.
- **H3** Banking77 and CLINC in-scope: `decider` accuracy within 5 points of `jev`.
- **H4** On B2–B5, answers at confidence ≥ 0.9 are ≥ 95% accurate for each model (the decider
  README's claim), with coverage reported.
- **H5** Paraphrase robustness: per-item agreement between the two wordings (B2, B5) is ≥ 90% for
  each model.

Each hypothesis is reported as supported / not supported, with the numbers, whatever the outcome.

## Known limitations (stated in advance)

- Jev's training data is unknown; HaluEval is derived from HotpotQA, which is in the decider's training mix.
- The decider team tuned v5→v19 against the JevBench public set (selection pressure).
- When2Call items longer than 4,096 tokens are truncated by the decider.
- deepset/prompt-injections labels role-play prompts as injections (broad definition).
- One run per backend; no retrain/seed variance for either model.

## Deviations (recorded during the run, before any full results were analysed)

1. **2026-10-05 05:52Z — decider server version and long prompts.** With `strands-decider` 0.1.0
   from PyPI, some When2Call prompts longer than the 4,096-token window crash the server with a CUDA
   `vectorized_gather_kernel index out of bounds` device-side assert (reproduced sequentially with a
   single 6,498-token item; the error is sticky and fails every later request). 0.1.0 also lacks
   `--strict-window`. Change: the decider is served from GitHub `strands-labs/strands-decider` @
   `75c9fd32e664954cdc18481434018aa507eee8fb` (same weights, same checkpoint) with `--strict-window`,
   so over-window prompts get a clean HTTP 422 instead of being truncated. Consequence: those items
   are recorded as errors for `decider` (not truncated as pre-registered), excluded from its
   accuracy, counted and reported, and paired comparisons use items both systems answered. The
   ~100 decider rows produced before the change were discarded.
2. **2026-10-05 05:58Z — decider concurrency.** Even at the pinned GitHub commit, concurrent
   requests (client concurrency 4) trigger the same sticky CUDA device-side assert; the same 40 items
   sent sequentially all succeed. Change: the decider is run at **concurrency 1**, and to keep GPU
   cost inside the budget the benchmark client runs **on the EC2 instance** against
   `127.0.0.1:8099` (no SSM tunnel). Jev was run at concurrency 4 from the laptop as planned.
   Accuracy is unaffected; end-to-end latency for the decider is therefore localhost, and is
   reported only alongside its server-side latency.
