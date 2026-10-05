#!/usr/bin/env bash
# Full pre-registered run for one backend (PREREGISTRATION.md). Resumable: re-run to continue.
#   bench/run_full.sh jev
#   bench/run_full.sh decider        # needs the tunnel on DECIDER_URL / 127.0.0.1:8199
set -euo pipefail
B=${1:?usage: run_full.sh decider|jev}
cd "$(dirname "$0")"
RUN=full-2026-10-05
WARM=0; [ "$B" = decider ] && WARM=5
CONC=${CONC:-4}   # decider: 1 (server crashes under concurrent requests, see PREREGISTRATION deviation 2)
for t in when2call banking77 clinc injection halueval; do
  uv run -q python run.py --backend "$B" --task "$t" --run-id "$RUN" --concurrency "$CONC" --warmup "$WARM"
done
uv run -q python run.py --backend "$B" --task when2call --variant labeled --run-id "$RUN" --concurrency "$CONC" --warmup "$WARM"
uv run -q python run.py --backend "$B" --task injection --variant paraphrase --run-id "$RUN" --concurrency "$CONC" --warmup "$WARM"
[ -s "results/$RUN/$B/jevbench/results.jsonl" ] || bash b1_jevbench/run.sh "$B" "$RUN"
# sequential latency probe (separate run id so it never mixes with accuracy runs)
uv run -q python run.py --backend "$B" --task banking77 --limit 200 --run-id latency-2026-10-05 --concurrency 1 --warmup "$WARM"
echo "DONE $B"
