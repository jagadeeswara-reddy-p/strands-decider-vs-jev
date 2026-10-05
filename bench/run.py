"""Run benchmark tasks against a /v1/systemone backend.

    uv run python run.py --backend decider --task banking77 --limit 10 --run-id dry
    uv run python run.py --backend jev --task all --run-id full-2026-10-06
    DECIDER_URL=http://127.0.0.1:8099/v1/systemone uv run python run.py --backend decider ...

Results land in results/<run-id>/<backend>/<task>[__<variant>]/results.jsonl (resumable:
re-running the same command skips items already answered without error).
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from common.client import BACKENDS, SystemOneClient
from common.runner import run
from common.tasks import TASKS

HERE = Path(__file__).resolve().parent


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=list(BACKENDS))
    ap.add_argument("--task", required=True, help=f"one of {list(TASKS)} or 'all'")
    ap.add_argument("--variant", default=None, help="prompt variant; default = the task's first")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--limit", type=int, default=None, help="seeded sample size; omit for the full set")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--url", default=None)
    ap.add_argument("--warmup", type=int, default=0, help="unrecorded warm-up requests per task")
    args = ap.parse_args()

    names = list(TASKS) if args.task == "all" else [args.task]
    client = SystemOneClient(args.backend, url=args.url)
    try:
        for name in names:
            task = TASKS[name]
            variant = args.variant or task.variants[0]
            if variant not in task.variants:
                raise SystemExit(f"{name} has variants {task.variants}")
            items = task.load(seed=args.seed, limit=args.limit, variant=variant)
            sub = name if variant == task.variants[0] else f"{name}__{variant}"
            out = HERE / "results" / args.run_id / args.backend / sub
            print(f"[{args.backend}] {sub}: {len(items)} items -> {out}", flush=True)
            for it in items[: args.warmup]:
                await client.ask(it.state, it.questions)  # not recorded: kernel warm-up / prefix cache
            await run(task, items, client, out, concurrency=args.concurrency,
                      extra_manifest={"variant": variant, "seed": args.seed, "limit": args.limit})
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
