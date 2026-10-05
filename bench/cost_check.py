"""Running spend estimate for the decider-vs-jev study, against the $2 budget.

    uv run python cost_check.py            # prints spend; exit code 2 if >= budget
Needs AWS creds in env and INSTANCE_ID (the EC2 instance id; reads instance state only).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BUDGET = 4.00  # raised from $2 by owner 2026-10-05 for the full run
EC2_PER_H = 0.8048
EBS_PER_GB_H = 0.08 / 730
JEV_PER_TOKEN = 42 / 1e9
INSTANCE = os.environ.get("INSTANCE_ID", "<INSTANCE_ID>")  # real ID masked in the repo; set INSTANCE_ID

# Completed EC2 sessions (UTC), from instance launch/stop times observed on 2026-10-05.
CLOSED_EC2_MIN = [
    16.7,  # <PREVIOUS_INSTANCE_ID> 03:50:36 -> ~04:07:20 (terminated on replacement)
    53.0,  # <INSTANCE_ID> 04:07:34 -> ~05:00:30 (auto-stop)
]
# Already-spent extras: Cost Explorer 2 x $0.01, Bedrock test calls, Jev tic-tac-toe (~285k tokens).
FIXED_USD = 0.02 + 0.01 + 285_000 * JEV_PER_TOKEN
DISK_GB, DISK_SINCE = 100, datetime(2026, 10, 5, 3, 50, 36, tzinfo=timezone.utc)
BENCH_RESULTS = Path(__file__).parent / "results"
SESSION_LOG = Path(__file__).parent / "results" / "ec2_sessions.json"  # appended when we stop a session


def aws(*args):
    return json.loads(subprocess.check_output(["aws", *args, "--output", "json"], text=True))


def main():
    now = datetime.now(timezone.utc)
    closed = CLOSED_EC2_MIN + (json.loads(SESSION_LOG.read_text()) if SESSION_LOG.exists() else [])
    inst = aws("ec2", "describe-instances", "--instance-ids", INSTANCE)["Reservations"][0]["Instances"][0]
    state = inst["State"]["Name"]
    live_min = 0.0
    if state in ("pending", "running", "stopping"):
        launched = datetime.fromisoformat(inst["LaunchTime"].replace("Z", "+00:00"))
        live_min = (now - launched).total_seconds() / 60
    ec2 = (sum(closed) + live_min) / 60 * EC2_PER_H
    disk = DISK_GB * EBS_PER_GB_H * (now - DISK_SINCE).total_seconds() / 3600
    jev_tokens = 0
    for f in BENCH_RESULTS.glob("*/jev/**/results.jsonl"):
        jev_tokens += sum(json.loads(l).get("input_tokens", 0) for l in f.open() if l.strip())
    for f in BENCH_RESULTS.glob("*/jev/jevbench/ledger.jsonl"):
        for l in f.open():
            if l.strip():
                jev_tokens += json.loads(l).get("input_tokens", 0) or 0
    jev = jev_tokens * JEV_PER_TOKEN
    total = ec2 + disk + jev + FIXED_USD
    print(f"{now:%H:%M:%S}Z instance={state} live={live_min:.1f}min | EC2 ${ec2:.3f} disk ${disk:.3f} "
          f"jev ${jev:.4f} ({jev_tokens:,} tok) fixed ${FIXED_USD:.3f} | TOTAL ${total:.3f} / ${BUDGET:.2f} "
          f"| headroom {(BUDGET - total) / EC2_PER_H * 60:.0f} EC2-min")
    return 2 if total >= BUDGET else 0


if __name__ == "__main__":
    sys.exit(main())
