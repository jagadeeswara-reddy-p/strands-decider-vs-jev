# Strands Decider vs TypeSafe Jev — internal evaluation

Internal benchmark of **Strands Decider 2B v19** (open "decision model", self-hosted on EC2) against
**TypeSafe Jev 1.13.0** (hosted API) on the decisions agents and business workflows make: routing,
tool-call gating, guardrails and judging. Run `full-2026-10-05`. **Internal use only.**

## Results at a glance

| Benchmark | Items | Strands Decider | Jev |
|---|---|---|---|
| JevBench public (18 families) | 231 | 0.727 | **0.857** |
| When2Call tool-call gating | 3,652 | 0.651 | **0.821** |
| Banking77 intent routing | 3,080 | **0.841** | 0.805 |
| CLINC150 intent + out-of-scope | 5,500 | 0.822 | **0.895** |
| Prompt-injection guardrail | 116 | 0.509 | **0.750** |
| HaluEval hallucination judge* | 1,000 | 0.637 | **0.871** |

All differences significant (exact McNemar, p < 1e-5). \*Possible contamination for the decider.

- Jev is the stronger general decision model; the decider is competitive on plain intent routing,
  well calibrated at high confidence, and cheaper per decision at full utilisation.
- The decider over-calls tools in agent gating (26% vs 9%), needs threshold tuning for yes/no
  questions, and its server crashed on > 4,096-token prompts (PyPI 0.1.0) and under concurrent
  requests.
- Modalities: the decider can read images (`--vision`); Jev 1.13 is text-only. Context: Jev 64k
  tokens, decider 4,096.

Full write-ups: [`bench/RESULTS.md`](bench/RESULTS.md) (summary) ·
[`bench/DOSSIER.md`](bench/DOSSIER.md) (complete hand-off) ·
[`bench/report/`](bench/report/) (technical report, HTML + PDF) ·
[`bench/PREREGISTRATION.md`](bench/PREREGISTRATION.md) (protocol, hypotheses, deviations) ·
[`bench/results/full-2026-10-05/report.md`](bench/results/full-2026-10-05/report.md) (all tables).

## Layout

| Path | Contents |
|---|---|
| `bench/` | benchmark code (`common/`, `run.py`, `run_full.sh`, `report.py`, `b1_jevbench/`), docs, results |
| `bench/results/full-2026-10-05/` | per-item results for both systems, JevBench harness output, report |
| `bench/results/latency-2026-10-05/` | sequential latency probe |
| `bench/results/dry/`, `comparison.md`, `decider.json`, `jev.json` | dry run and tic-tac-toe pilot |
| `infra/` | Terraform: one g6.xlarge GPU instance, SSM-only access, no inbound ports, auto-stop |

Not in this repo (fetched or referenced instead):

- Strands Decider source: https://github.com/strands-labs/strands-decider @ `75c9fd32e664954cdc18481434018aa507eee8fb`
- JevBench harness: https://github.com/fstandhartinger/jevbench @ `1bcc55eb6c8cffde2306b3db03ede39b61c6152a` (cloned into `bench/vendor/` by the run scripts)
- Tic-tac-toe app: https://github.com/jagadeeswara-reddy-p/play-jev-tictactoe
- Datasets: downloaded at pinned revisions by `bench/fetch_data.py`

## Reproduce

```bash
# 1. GPU box (us-east-1, g6.xlarge, ~$0.80/h while running; stops itself after 20 min per boot)
cd infra && terraform init && terraform apply

# 2. benchmark environment and data
cd ../bench && uv sync && uv run python fetch_data.py
git clone https://github.com/fstandhartinger/jevbench vendor/jevbench \
  && git -C vendor/jevbench checkout 1bcc55eb6c8cffde2306b3db03ede39b61c6152a \
  && uv pip install --no-deps -e vendor/jevbench

# 3. runs (Jev needs TYPESAFE_API_KEY; the decider must be reachable, e.g. via SSM port-forward)
./run_full.sh jev
CONC=1 DECIDER_URL=http://127.0.0.1:8099/v1/systemone DECIDER_ENDPOINT=http://127.0.0.1:8099 ./run_full.sh decider

# 4. tables
uv run python report.py --run-id full-2026-10-05
```

Run the decider at concurrency 1 and with `--strict-window` (see deviations in
`bench/PREREGISTRATION.md`). Credentials are never stored in this repo.

## Masked identifiers

AWS account IDs, EC2 instance / volume / security-group IDs and host names in this repo are replaced
with placeholders such as `<AWS_ACCOUNT_ID>`, `<INSTANCE_ID>`, `<VOLUME_ID>`, `<ec2-instance>` and
`<laptop>`. The real values are not needed to reproduce the study (Terraform creates fresh resources;
scripts take the instance id from `INSTANCE_ID`). If you need the real identifiers — e.g. to audit
the billing — ask the repository owner, who can provide them.

## Cost

Whole study ≈ **$3.67** (EC2 ≈ $2.32, Jev ≈ $1.27, other ≈ $0.08). The stopped instance's 100 GB
disk costs ≈ $0.27/day until `terraform destroy`.
