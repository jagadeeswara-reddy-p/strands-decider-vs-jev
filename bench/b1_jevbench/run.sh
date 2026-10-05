#!/usr/bin/env bash
# B1: JevBench v1 public set (231 tasks) against one backend, with the unmodified harness at
# the commit Strands Decider's published score used.
#
#   bench/b1_jevbench/run.sh decider <run-id> [limit]   # needs the tunnel: DECIDER_ENDPOINT (default http://127.0.0.1:8199)
#   bench/b1_jevbench/run.sh jev     <run-id> [limit]   # needs TYPESAFE_API_KEY
#
# Writes bench/results/<run-id>/<backend>/jevbench/{results.jsonl,raw/,ledger.jsonl,manifest.json,summary.json}
set -euo pipefail

BACKEND=${1:?usage: run.sh decider|jev <run-id> [limit]}
RUN_ID=${2:?usage: run.sh decider|jev <run-id> [limit]}
LIMIT=${3:-}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BENCH=$(cd "$HERE/.." && pwd)
JB="$BENCH/vendor/jevbench"
COMMIT=1bcc55eb6c8cffde2306b3db03ede39b61c6152a

[ "$(git -C "$JB" rev-parse HEAD)" = "$COMMIT" ] || { echo "vendor/jevbench is not at $COMMIT"; exit 1; }
[ -z "$(git -C "$JB" status --porcelain --untracked-files=no)" ] || { echo "vendor/jevbench has local modifications"; exit 1; }

OUT="$BENCH/results/$RUN_ID/$BACKEND/jevbench"
if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null)" ]; then echo "$OUT is not empty (the harness never overwrites)"; exit 1; fi
mkdir -p "$OUT"
TASKS="$OUT/all.jsonl"
cat "$JB"/datasets/public/{original,easy,hard}.jsonl > "$TASKS"

COMMON=(--tasks "$TASKS" --adapter typesafe --results "$OUT/results.jsonl" --raw-dir "$OUT/raw"
        --ledger "$OUT/ledger.jsonl" --manifest "$OUT/manifest.json")
[ -n "$LIMIT" ] && COMMON+=(--limit "$LIMIT")

case "$BACKEND" in
  decider)
    ENDPOINT=${DECIDER_ENDPOINT:-http://127.0.0.1:8199}
    curl -sf "$ENDPOINT/health" > "$OUT/health.json" || { echo "decider /health unreachable at $ENDPOINT"; exit 1; }
    cat "$OUT/health.json"; echo
    uv run --project "$BENCH" python -m jevbench.cli run "${COMMON[@]}" --endpoint "$ENDPOINT" --key-env '' \
      --model strands-decider-2B-hobson-v19 --run-label strands-decider-v19 \
      --cost-basis self_hosted_ec2_g6xlarge --reserve-usd 0
    ;;
  jev)
    : "${TYPESAFE_API_KEY:?set TYPESAFE_API_KEY}"
    uv run --project "$BENCH" python -m jevbench.cli run "${COMMON[@]}" --endpoint https://api.typesafe.ai \
      --key-env TYPESAFE_API_KEY --model jev-latest --run-label jev-latest \
      --price-in-per-m 0.042 --price-out-per-m 0 --cap-usd 2
    ;;
  *) echo "backend must be decider or jev"; exit 1 ;;
esac

uv run --project "$BENCH" python -m jevbench.cli summarize --tasks "$TASKS" --results "$OUT/results.jsonl" \
  --ledger "$OUT/ledger.jsonl" --public-export "$OUT/summary.json" > "$OUT/summarize.log"
tail -n 30 "$OUT/summarize.log"
