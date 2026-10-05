"""Run one task against one backend, resumably, writing one JSON line per item."""
from __future__ import annotations

import asyncio
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

from .client import SystemOneClient, SystemOneError
from .task import Item, Task


def items_sha(items: list[Item]) -> str:
    h = hashlib.sha256()
    for it in items:
        h.update(json.dumps([it.id, it.state, it.questions, it.gold], sort_keys=True).encode())
    return h.hexdigest()


def done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {json.loads(l)["id"] for l in path.open() if l.strip() and "error" not in json.loads(l)}


async def run(task: Task, items: list[Item], client: SystemOneClient, out_dir: Path,
              concurrency: int = 1, progress_every: int = 50, extra_manifest: dict | None = None):
    out_dir.mkdir(parents=True, exist_ok=True)
    res_path = out_dir / "results.jsonl"
    skip = done_ids(res_path)
    todo = [it for it in items if it.id not in skip]
    manifest = {
        "task": task.name, "backend": client.backend, "url": client.url, "model_field": client.model,
        "n_items": len(items), "items_sha256": items_sha(items), "resumed_skipping": len(skip),
        "concurrency": concurrency, "started_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(), **(extra_manifest or {}),
    }
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    counter = {"n": 0, "err": 0}
    t0 = time.time()

    async def one(it: Item):
        async with sem:
            row = {"id": it.id, "gold": it.gold, "meta": it.meta}
            try:
                rep = await client.ask(it.state, it.questions)
                p = task.parse(rep.answers)
                row.update(pred=p.pred, ok=p.pred == it.gold, probs=p.probs, confidence=p.confidence,
                           raw_confidence=p.raw_confidence, client_ms=rep.client_ms, server_ms=rep.server_ms,
                           input_tokens=rep.input_tokens, model=rep.model, attempts=rep.attempts)
            except (SystemOneError, KeyError, ValueError, TypeError) as ex:
                row["error"] = f"{type(ex).__name__}: {str(ex)[:300]}"
                counter["err"] += 1
            async with lock:
                with res_path.open("a") as f:
                    f.write(json.dumps(row) + "\n")
                counter["n"] += 1
                if counter["n"] % progress_every == 0 or counter["n"] == len(todo):
                    rate = counter["n"] / max(time.time() - t0, 1e-9)
                    print(f"  [{client.backend}/{task.name}] {counter['n']}/{len(todo)} "
                          f"errors={counter['err']} {rate:.1f} items/s", flush=True)

    await asyncio.gather(*(one(it) for it in todo))
    manifest.update(finished_utc=datetime.now(timezone.utc).isoformat(), wall_s=round(time.time() - t0, 1),
                    errors_this_session=counter["err"])
    mpath = out_dir / "manifest.json"
    history = json.loads(mpath.read_text())["sessions"] if mpath.exists() else []
    mpath.write_text(json.dumps({"sessions": history + [manifest]}, indent=1))
    return res_path
