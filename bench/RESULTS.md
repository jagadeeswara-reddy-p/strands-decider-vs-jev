# Strands Decider v19 vs TypeSafe Jev 1.13.0: results

Run `full-2026-10-05` · internal only · protocol in [PREREGISTRATION.md](PREREGISTRATION.md) (2 deviations,
listed below) · raw per-item results in `results/full-2026-10-05/` · full tables in
`results/full-2026-10-05/report.md` · study cost **≈ $3.67**.

## Headline

**Jev is the stronger general decision model; Strands Decider holds its own on plain intent routing
and is cheaper per decision, but it needs threshold tuning for yes/no checks and is not ready for
production serving (it crashed under concurrent load).**

| Benchmark | Items | Strands Decider | Jev | Winner (McNemar) |
|---|---|---|---|---|
| **JevBench public** (18 families) | 231 | 0.727 | **0.857** | Jev, p = 9e-6 |
| **When2Call** tool-call gating | 3,652 | 0.651 | **0.821** | Jev, p = 8e-90 |
| **Banking77** intent routing (77 classes) | 3,080 | **0.841** | 0.805 | **Decider**, p = 4e-8 |
| **CLINC150** intent + out-of-scope (151) | 5,500 | 0.822 | **0.895** | Jev, p = 2e-46 |
| **Prompt-injection** guardrail | 116 | 0.509 | **0.750** | Jev, p = 6e-8 |
| **HaluEval** hallucination judge ⚠ | 1,000 | 0.637 | **0.871** | Jev, p = 5e-44 |

⚠ HaluEval is built from HotpotQA, which is in the decider's training mix.

Both scores on JevBench reproduce the published figures (decider 168/231 = repo's own 168 at 4096;
Jev 198/231 vs 200/231 on the board).

## Pre-registered hypotheses

| | Hypothesis | Result | Verdict |
|---|---|---|---|
| H1 | JevBench: Jev > decider, significant | 0.857 vs 0.727, 38 vs 8 discordant, p = 9e-6 | ✅ supported |
| H2 | When2Call: decider macro-F1 within 5 pts of Jev | 3-class macro-F1 0.658 vs 0.830 (−17 pts) | ❌ not supported |
| H3 | Banking77 & CLINC in-scope: decider within 5 pts | Banking77 **+3.6** (decider better); CLINC in-scope 0.869 vs 0.905 (−3.6) | ✅ supported |
| H4 | Confidence ≥ 0.9 → ≥ 95% accurate (each model) | Decider: 96.6–97.8% on When2Call/Banking77/CLINC, but at tiny coverage on When2Call (4%) and none on injection/HaluEval. Jev: 91.8–96.7%, below 95% on 3 of 4 | ✅ decider / ❌ Jev |
| H5 | Paraphrase agreement ≥ 90% | Decider: When2Call **0.836**, injection 0.957. Jev: 0.944, 0.983 | ❌ decider / ✅ Jev |

## What the numbers say

**1. Plain classification (intent routing) — the decider is competitive.** It beat Jev on Banking77
(0.841 vs 0.805) with better calibration (ECE 0.032 vs 0.091; 97.8% right on the 48% of messages it
was ≥ 0.9 sure about). On CLINC it trails by 3.6 points in-scope and is weaker at spotting
out-of-scope requests (recall 0.61 vs 0.85), though it is more precise when it does say "out of scope"
(0.94 vs 0.87).

**2. Agent tool-call gating — Jev is far ahead.** When2Call is the use case Strands pitches the
decider for. The decider recognises "call the tool" (0.83) and "ask for missing info" (0.78) but
mostly fails to say "I can't do that with these tools" (0.37 vs 0.74) and **picks a tool call when it
shouldn't 26% of the time** (Jev 9%). With no tools offered at all it is right only 46% of the time
(Jev 83%). Its answer also changes with the wording of the question on 16% of items.

**3. Yes/no guardrails and judges — the decider is mis-thresholded, not blind.** At the default 0.5
cut-off it almost never says "yes" (injection F1 0.10, HaluEval F1 0.43) because its P(yes) rarely
exceeds 0.5 (max 0.60–0.72). But it *ranks* items well: AUROC 0.87–0.93 vs Jev 0.96. Exploratory,
**post-hoc** (threshold fitted on the test set, so optimistic): a tuned threshold would give 0.80–0.87
vs Jev 0.89–0.91. In practice: the decider needs per-question calibration on your own labelled data
before a yes/no gate can be trusted; Jev works out of the box.

**4. Calibration.** Both are well calibrated on multi-class routing (ECE ≤ 0.05). The decider is
*conservative*: when it does claim ≥ 0.9 it is right ~97% of the time, but it claims it far less often
(e.g. 4% of When2Call items vs 63% for Jev). Jev claims high confidence more often and is right
92–96% of the time at that level.

## Speed and cost

| | Strands Decider (self-hosted, g6.xlarge L4) | Jev (hosted API) |
|---|---|---|
| Model time per decision (server, p50) | 66 ms (short yes/no) – 237 ms (151-option routing) | not exposed |
| End-to-end, sequential probe (Banking77) | 154 ms p50 (client on the GPU box) | 305 ms p50 / 478 ms p99 (from India) |
| Throughput | **1 request at a time** (concurrent requests crash it) → 4–6 decisions/s | ~12–13 decisions/s at concurrency 4, 0 errors in 17k |
| Cost per 1,000 decisions | $0.015–0.053 at 100% utilisation | $0.015–0.106 (output tokens free) |
| Fixed cost | $0.80/h → **~$588/month always-on** | none |

Break-even: $588/month buys ~6–10M Jev decisions at these prompt sizes. One decider box can serve at
most ~13M/month sequentially, so self-hosting only pays off near full, steady utilisation — and only
if the concurrency crash is fixed.

## Engineering findings (Strands Decider)

- **PyPI 0.1.0 crashes on prompts over the 4,096-token window** (CUDA `index out of bounds`,
  sticky: every later request fails until restart) and has no `--strict-window`. Fixed by serving
  GitHub commit `75c9fd3` with `--strict-window` (clean HTTP 422 instead). 10 of 3,652 When2Call items
  (4,097–7,723 tokens) were rejected and excluded for the decider.
- **Concurrent requests crash the server** with the same sticky CUDA assert, even on `75c9fd3`; the
  same items sequentially all succeed. Production use needs a fix or a request queue in front.
- **PyPI 0.1.0 has no `[cuda]` extra**, so `flash-linear-attention` must be installed explicitly;
  `causal-conv1d` still runs on its slow fallback (no wheel for torch 2.14 / CUDA 13).
- Cold start: first request ~65 s (kernel compile); ~1–12 min to serve after an instance start.

## Deviations from the pre-registration

1. Decider served from GitHub `75c9fd3` with `--strict-window` (over-window prompts rejected, not truncated).
2. Decider run at concurrency 1 with the client on the EC2 instance (Jev at concurrency 4 from the laptop).

## Limitations

- One run per system; Jev's training data unknown; the decider was tuned against JevBench public
  (selection pressure) and trained on HotpotQA (HaluEval source).
- deepset's "injection" label is broad (role-play prompts count), and the set is small (116).
- End-to-end latencies are not comparable across systems (different network paths); the decider's
  server-side time is the fair model-only number.
- Post-hoc threshold numbers in finding 3 are fitted on the test set and are optimistic.

## Reproduce

```bash
cd bench && uv sync
./run_full.sh jev                                   # TYPESAFE_API_KEY set
CONC=1 DECIDER_URL=http://127.0.0.1:8099/v1/systemone DECIDER_ENDPOINT=http://127.0.0.1:8099 ./run_full.sh decider
uv run python report.py --run-id full-2026-10-05
```
Infra: `infra/` (Terraform, g6.xlarge, SSM-only). Study spend tracked by `cost_check.py`.
