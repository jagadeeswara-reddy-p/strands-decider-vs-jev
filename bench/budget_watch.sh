#!/usr/bin/env bash
# Every 60 s: run cost_check.py; at/over budget, kill benchmark runs and stop the instance.
# Expects AWS creds for the study account and INSTANCE_ID (the EC2 instance id) in the environment.
: "${INSTANCE_ID:?set INSTANCE_ID to the decider EC2 instance id}"
cd "$(dirname "$0")"
while true; do
  out=$(uv run -q python cost_check.py); rc=$?
  echo "$out"
  if [ $rc -eq 2 ]; then
    echo "BUDGET REACHED - stopping runs and instance"
    pkill -f 'run_full.sh' ; pkill -f 'run.py --backend' ; pkill -f 'jevbench.cli run'
    aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --output text
    exit 2
  fi
  sleep 60
done
