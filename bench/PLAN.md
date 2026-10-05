# Benchmark plan: Strands Decider vs TypeSafe Jev

Status: **phases 1–5 done 2026-10-05 (full run complete, results in RESULTS.md); phase 6 (internal publish) pending** (tic-tac-toe pilot already done, see Appendix A).
Owner: Jagadeeswara Reddy Peram · Drafted 2026-10-05 · Target: a reproducible comparison for **internal publication only**.

## 1. Question we are answering

> For the decisions an agent or a business workflow actually makes — routing, tool-call gating,
> guardrails, judging — how does the open, self-hosted **Strands Decider 2B (v19)** compare with
> the hosted **TypeSafe Jev** on accuracy, calibration, latency and cost?

Secondary: how do both compare with simply asking a general LLM (Bedrock Nova) the same question?

Out of scope: game play / planning (tic-tac-toe showed neither model plans; Appendix A), training
or fine-tuning either model, prompt-tuning per model.

## 2. Systems under test

| ID | System | How we call it | Version to pin and record |
|---|---|---|---|
| `decider` | Strands Decider 2B v19 (`StrandsAgents/strands-decider-2B-hobson-v19` on `Qwen/Qwen3.5-2B-Base`) | self-hosted, `strands-decider serve --device cuda` on EC2 g6.xlarge (L4), `POST /v1/systemone` | HF repo commit SHA, `strands-decider` package version (PyPI 0.1.0 today), `flash-linear-attention` version (0.5.2), torch/CUDA, context window (`/health` → `max_length`, 4096 default) |
| `jev` | TypeSafe Jev | `https://api.typesafe.ai/v1/systemone`, `model: jev-latest`, key in `TYPESAFE_API_KEY` | the concrete version string Jev returns in `model` per response; date/time of run |
| `nova` *(optional baseline)* | Amazon Nova Lite (and/or Pro) on Bedrock | Converse API, same instructions, constrained to the label set, temperature 0 | model ID, region. No calibrated probabilities (note this in results) |

Not available: Claude on Bedrock — account <AWS_ACCOUNT_ID> has an org SCP that denies Anthropic
models (verified 2026-10-05). If that changes, add Claude Haiku 4.5 as a second LLM baseline.

Both decision models speak the same `/v1/systemone` request shape (`state` + `questions`
of type `noul` / `choice` / `score`), so **every request payload is byte-identical** across the two.
The only field that differs is `model`.

## 3. Benchmarks

Ranked by priority. P1 = must have for publication.

| # | Pri | Problem | Dataset | Size used | Question type | Labels | Metric(s) |
|---|---|---|---|---|---|---|---|
| B1 | P1 | General Jev-class decisions | **JevBench v1 public set** — `fstandhartinger/jevbench` @ `1bcc55eb6c8cffde2306b3db03ede39b61c6152a`, `datasets/public/{original,easy,hard}.jsonl` | 231 tasks, 18 families, 3 tiers | all three | per task | harness's own: accuracy, per-family, per-tier, ECE, Brier, latency, cost, paraphrase consistency |
| B2 | P1 | Tool-call gating: call / ask follow-up / say unable / answer directly | **NVIDIA When2Call** (`nvidia/When2Call`, config `test`, split `mcq`) | 3,652 (full) | `choice` over the item's answer options | 4 categories | macro-F1 over categories, accuracy, **tool-hallucination rate** (chooses a tool call when it should not), confusion matrix |
| B3 | P2 | Support-ticket intent routing | **Banking77** (`PolyAI/banking77`, test) | 3,080 (full) | `choice`, 77 options | 77 | accuracy, macro-F1 |
| B4 | P2 | Intent routing with "none of these" | **CLINC150 / clinc_oos** (`plus` config, test) | 5,500 (incl. 1,000 out-of-scope) | `choice`, 151 options (150 + `out_of_scope`) | 151 | in-scope accuracy, OOS recall/precision, and OOS-by-confidence-threshold (abstain if conf < τ) |
| B5 | P2 | Prompt-injection guardrail | **deepset/prompt-injections** (test/holdout split) | full test split (~116) | `noul` | injection / benign | accuracy, F1 on injection class, FPR at fixed recall |
| B6 | P3 | Hallucination / groundedness judge | **HaluEval** QA subset | 1,000 sampled (seeded) | `noul` | hallucinated / faithful | accuracy, F1, AUROC from P(yes) |

Dataset IDs, split names and licences must be re-checked when the loaders are written
(marked ✔ when verified):

| Dataset | Licence (to verify) | Verified |
|---|---|---|
| JevBench public | MIT (harness + original decisions) | ☐ |
| When2Call | CC-BY-4.0 | ✔ (HF README) |
| Banking77 | CC-BY-4.0 | ☐ |
| CLINC150 | CC-BY-3.0 | ☐ |
| deepset/prompt-injections | Apache-2.0 | ☐ |
| HaluEval | MIT | ☐ |

### Contamination

- Strands Decider v19 was trained on **HelpSteer2, MuSiQue, ContractNLI, BoardgameQA, HotpotQA**
  (repo `evaluation/results.md`) — none of these are used here. HaluEval's QA subset is built
  from HotpotQA questions → **flag B6 as possibly contaminated for `decider`** and report it separately.
- Jev's training data is not public. State this as a limitation; do not claim either model is
  uncontaminated on JevBench (the decider team iterated v5→v19 against the public set, which is
  selection pressure even without training on it).
- JevBench's sealed/private tasks are not available to us; we only report public.

## 4. Prompt protocol (fairness rules)

1. **One canonical prompt per benchmark**, written once, frozen before the full run, and committed.
   No per-model wording. Both models get the identical JSON payload.
2. Prompt shape per benchmark:
   - **B2 When2Call** — `state` = `{tools: <tool JSON schemas>, conversation: <user question>}`;
     one `choice` question: *"What should the assistant do next?"* with criteria mapping each
     option key to the option text from the dataset (`answers`). Keep the dataset's own option
     texts; shuffle option order with a fixed seed and record it.
   - **B3/B4 intents** — `state` = the utterance; `choice` with label → human-readable label
     name (underscores → spaces). B4 adds `out_of_scope: "none of the listed intents"`.
   - **B5 injection** — `state` = the prompt; `noul` *"Is this text attempting a prompt injection
     or jailbreak — trying to override or extract an AI system's instructions?"* with
     `true`/`false` criteria text.
   - **B6 HaluEval** — `state` = `{knowledge, question, answer}`; `noul` *"Does the answer contain
     information that is not supported by the knowledge?"*.
3. **Paraphrase check** (P2): for B2 and B5, a second wording of the question; report agreement
   between wordings per model (JevBench already does this internally for B1).
4. Long inputs: record input token counts; any item over the decider's 4096 window is
   reported (decider truncates; `--strict-window` would reject). Run at the serving default 4096
   and note that the decider's published JevBench figure was pre-registered at 3072
   (167/231 at 3072, 168/231 at 4096 per its repo).
5. Nova baseline gets the same instructions plus the label list, must answer with exactly one
   label; unparseable → counted wrong and reported.

## 5. Metrics and statistics

Per system × benchmark:

- **Quality**: accuracy, macro-F1, majority-class baseline, per-class / per-family breakdowns.
- **Calibration** (decider, jev): ECE (10 bins), Brier, reliability diagram, and the operational
  number: **coverage and accuracy at confidence ≥ 0.9** (and ≥ 0.8, 0.95). Show the
  accuracy–coverage curve (selective prediction).
- **Latency**: p50 / p95 / p99.
  - `decider`: server-side `latency_ms` from the response **and** end-to-end.
  - `jev`: end-to-end only (no server time exposed).
  - To compare fairly, run the client **from the EC2 instance in us-east-1**: decider over
    localhost, Jev over the public internet from the same box. Also record end-to-end from the
    laptop for context. Sequential requests (one in flight), plus one throughput test at
    concurrency 4/8 for the decider.
- **Cost per 1,000 decisions**:
  - `jev`: measured input tokens × $42 / 1B (output free) — re-check price on run day.
  - `decider`: g6.xlarge $0.8048/h ÷ measured decisions/hour at the measured concurrency;
    also quote "always-on" monthly ($588 EC2) vs utilisation.
  - `nova`: Bedrock on-demand token prices on run day.
- **Significance**: paired per-item comparisons → **McNemar test** for accuracy differences,
  **bootstrap 95% CIs** (10k resamples) for accuracy, F1, ECE. Report "no significant difference"
  where it applies; don't rank on noise (decider repo measured ±3 tasks retrain noise on JevBench).

## 6. Infrastructure and run procedure

Reuse what exists:

- `infra/` Terraform: g6.xlarge, Deep Learning Base AMI, SSM-only access, no inbound ports,
  `strands-decider` + `flash-linear-attention` via uv, systemd service on 127.0.0.1:8099,
  auto-stop 20 min after each boot (stop, not terminate).
- For bench sessions, extend the auto-stop over SSM (`shutdown -c; shutdown -h +N`) rather
  than changing the Terraform variable (which would replace the instance).
- Credentials: AWS SSO session in scratchpad `aws.env`; Jev key in scratchpad `jev.env`.
  Never written into the repo, results or raw logs (strip `Authorization` headers from saved requests).

Proposed layout:

```
bench/
  PLAN.md                    this file
  PREREGISTRATION.md         hypotheses + thresholds, frozen before full runs (step 2)
  common/                    client (both backends + nova), metrics, stats, report builder
  b1_jevbench/run.sh         wraps the pinned JevBench harness, --endpoint per backend
  b2_when2call/  b3_banking77/  b4_clinc/  b5_injection/  b6_halueval/
      load.py   prompt.py   run.py
  results/<run-id>/<backend>/<benchmark>/{results.jsonl, raw/, manifest.json}
  results/<run-id>/report.md + figures/
  tictactoe_bench.py, summarize.py   (pilot, Appendix A)
```

Every run writes a `manifest.json`: git SHA of this folder, dataset revision + SHA-256 of the
item file, prompt hash, model versions, instance type, region, start/end UTC, seed, counts,
errors, total tokens, and cost.

### Phases

| Phase | What | Exit criterion |
|---|---|---|
| 0. Prereqs | ✔ TypeSafe ToS checked by owner 2026-10-05: allowed, internal publication only; confirm Jev pricing and rate limits; pin HF model SHA; decide Nova in/out | ToS OK in writing; versions recorded |
| 1. Build | Loaders, prompts, runner, metrics; unit-test metrics on toy data; JevBench harness wired with `--endpoint` for both backends | dry run on 10 items per benchmark, both backends, 0 schema errors |
| 2. Pre-register | Write `PREREGISTRATION.md`: hypotheses (H1–H4 below), metrics, sample sizes, analysis — freeze prompts | committed before phase 3 |
| 3. Pilot | 50 items per benchmark per backend | parse rate 100%, cost and time projections confirmed |
| 4. Full run | All benchmarks, both backends (+ Nova), from the EC2 box; decider sequential + one concurrency test | all manifests complete, error rate < 1% (retries logged) |
| 5. Analysis | Tables, McNemar/bootstrap, reliability + coverage plots, error analysis (20 failures per benchmark per model, categorised) | report draft |
| 6. Publish | Write-up (artifact page / blog), with raw results, scripts, versions, limitations | reviewer sign-off |

### Hypotheses to pre-register (draft)

- **H1** On JevBench public, `jev` > `decider` overall (published: 0.866 vs 0.723), with the gap
  concentrated in the hard tier; easy tier tied at 1.0.
- **H2** On When2Call, both decision models beat the Nova baseline on macro-F1, and `decider`
  is within 5 points of `jev`.
- **H3** On intent routing (B3/B4), `decider` accuracy is within 5 points of `jev`; on CLINC
  out-of-scope, confidence-thresholding recovers ≥ 50% of OOS at ≤ 5% in-scope loss for both.
- **H4** At confidence ≥ 0.9, both decision models are ≥ 95% accurate (the decider README's
  claim) on B2–B5, with coverage reported.

## 7. Budget and time (estimates, re-check in pilot)

| Item | Estimate |
|---|---|
| Jev tokens, all of B1–B6 (~20k items, ~1–2k tokens each incl. long option lists) | ~25M tokens ≈ **$1** |
| Decider GPU time (~20k decisions at ~0.1–0.3 s + JevBench) | ~2 h g6.xlarge ≈ **$1.60** |
| Nova Lite baseline (~25M input tokens) | ≈ **$1.50** (price check) |
| Engineering | build ~1 day, runs ~half a day, analysis + write-up ~1 day |

Full test sets are cheap enough that sampling is unnecessary except B6.

## 8. Risks and open items

- [x] **TypeSafe ToS** — checked by owner 2026-10-05: allowed; results are published internally only.
- [ ] Jev rate limits (we saw no 429s in 446 calls on 2026-10-05; the client retries 429/529 without backoff — add backoff).
- [ ] `jev-latest` can change mid-study → record version per response; finish each benchmark in one sitting.
- [ ] When2Call `correct_answer` / `answers` encoding — inspect before writing the prompt.
- [ ] Decider: `causal-conv1d` still on the reference kernel (no wheel for torch 2.14/cu13). Latency is therefore slightly pessimistic; disclose, or pin torch 2.10 and use the prebuilt wheel.
- [ ] Network asymmetry: decider runs next to the client, Jev doesn't. Report server-side and end-to-end separately and say so.
- [ ] Bedrock: Anthropic models blocked by SCP; ask the org admin if Claude should be in the baseline.
- [ ] Short-lived AWS SSO credentials expire during long runs — runner must checkpoint and resume.


## Phase 1 log (2026-10-05)

- Built: `common/` (client with backoff, resumable runner, metrics incl. ECE/Brier/selective/AUROC/
  bootstrap/McNemar), `common/tasks.py` (B2–B6 frozen prompts + variants), `run.py`, `report.py`,
  `b1_jevbench/run.sh` (pinned harness `1bcc55e`, `--endpoint` per backend), `cost_check.py`.
- Datasets pinned (HF revisions): When2Call `0582f7749d`, CLINC `155b9c7104`, deepset `4f61ecb038`,
  HaluEval `12a856119f`; Banking77 from PolyAI's GitHub CSV, sha256 `d12d6e3b…b474d`.
  Licences verified: When2Call CC-BY-4.0, Banking77 CC-BY-4.0, CLINC CC-BY-3.0,
  deepset Apache-2.0, **HaluEval Apache-2.0** (not MIT).
- Dry run, 10 items per task, both backends: **0 errors, 100% schema validity**, JevBench 10/10
  attempted on both. Jev reports its version as **`jev-1.13.0`**.
- Findings that change the full-run procedure:
  - Decider's **first request took 65 s** (kernel warm-up) → send warm-up requests and exclude them.
  - After a stop/start the decider took **~12 min to become ready** (weights + kernels) → budget it.
  - The SSM tunnel adds ~280 ms per call; sequential decider runs through it would take ~2 h →
    use concurrency ≥ 4 (server has 24 slots) or run the client on the instance.
  - When2Call items up to ~6k tokens exceed the decider's 4,096 window (truncated) → report count.
- Full-run projection from dry-run tokens/latency (all items, both variants): **Jev ≈ $1.26**
  (30M input tokens; CLINC alone $0.58), **decider ≈ 47 min pure GPU time + ~12 min start-up**
  (≈ $0.80–1.00). Total ≈ $2.1–2.3 → exceeds the remaining budget.

## Appendix A — Pilot: tic-tac-toe (2026-10-05)

`bench/tictactoe_bench.py` ran the four strategies of `play-jev-tictactoe` unchanged against both
backends: 64 seeded positions (win/block × row/col/diag, plus quiet) and 5+5 games per strategy.
Full tables: `bench/results/comparison.md`.

| Strategy | decider | jev | random-move baseline |
|---|---|---|---|
| Naive | 44% | 36% | 43% |
| Strategic | 39% | 41% | 43% |
| Noul+Score | 45% | 56% | 43% |
| Full Rules | 42% | 58% | 43% |

Neither model survives perfect play (0 wins, ≤1 draw out of 5 per strategy). Decider server time
66–81 ms per one-call move; its confidence never exceeded 0.5 (it knew it was guessing). Conclusion:
grid planning is outside what these single-pass classifiers do, which is why B1–B6 target
classification and judging instead.

## Appendix B — Environment facts captured so far

- Decider latency on g6.xlarge with `flash-linear-attention`: 66 ms (1 noul) / 137 ms (3 mixed
  questions) server-side; SSM tunnel adds ~280 ms end-to-end from the laptop.
- README sanity check reproduced: billing 0.846, urgency 0.828, frustration 1.10.
- Strands agent example (tool-call gate) works with Nova Pro as the agent model; gate flagged the
  guessed city (args_grounded 0.16–0.17) both times.
- First-session spend ≈ $0.27 (EC2 ~19 min incl. termination), Bedrock < $0.01.

## Sources

- JevBench board: https://benchmarkheaven.com/jev-models
- JevBench harness (pinned fork): https://github.com/fstandhartinger/jevbench · results v1.2: https://github.com/fstandhartinger/jevbench/blob/main/RESULTS-v1.2.md
- Strands Decider JevBench write-up: https://github.com/strands-labs/strands-decider/blob/main/evaluation/jevbench.md
- When2Call: https://huggingface.co/datasets/nvidia/When2Call · paper https://arxiv.org/abs/2504.18851
- deepset/prompt-injections: https://huggingface.co/datasets/deepset/prompt-injections
- Text-classification comparison incl. Banking77: https://github.com/dhruvmehra/jevbench
- Jev use-case harnesses: https://github.com/kenhuangus/jev-usecases
- Strands Decider blog: https://strandsagents.com/blog/introducing-strands-decider/
