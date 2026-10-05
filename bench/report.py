"""Compare backends for one run id: results/<run-id>/<backend>/<task>/results.jsonl -> report.md

    uv run python report.py --run-id dry
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import metrics as M
from common.tasks import TASKS

HERE = Path(__file__).resolve().parent
JEV_USD_PER_TOKEN = 42 / 1e9          # input tokens; output free (re-check on run day)
DECIDER_USD_PER_HOUR = 0.8048         # g6.xlarge on-demand us-east-1
THRESHOLDS = (0.8, 0.9, 0.95)


def load_rows(path: Path):
    last = {}
    for line in path.open():
        if line.strip():
            r = json.loads(line)
            last[r["id"]] = r  # later lines (retries) win
    return list(last.values())


def fmt(x, d=3):
    return "-" if x is None or x != x else f"{x:.{d}f}"


def category_view(task, rows):
    """When2Call: map option keys back to dataset categories."""
    if task != "when2call":
        return rows
    out = []
    for r in rows:
        km = r["meta"]["keymap"]
        out.append({**r, "gold": km[r["gold"]], "pred": km.get(r.get("pred"), r.get("pred"))})
    return out


def task_extras(task, rows):
    ex = {}
    if task == "when2call":
        c = category_view(task, rows)
        ex["macro-F1 (3 gold classes)"] = M.macro_f1(c, ["tool_call", "request_for_info", "cannot_answer"])
        not_tool = [r for r in c if r["gold"] != "tool_call"]
        ex["tool-hallucination rate"] = sum(r["pred"] == "tool_call" for r in not_tool) / max(len(not_tool), 1)
        ex["answer-hallucination rate (picks 'direct')"] = sum(r["pred"] == "direct" for r in c) / len(c)
        for cat in ("tool_call", "request_for_info", "cannot_answer"):
            sub = [r for r in c if r["gold"] == cat]
            ex[f"acc | gold={cat}"] = M.accuracy(sub)
        zero = [r for r in c if r["meta"]["n_tools"] == 0]
        ex["acc | no tools offered"] = M.accuracy(zero)
    if task == "clinc":
        ins = [r for r in rows if not r["meta"]["oos"]]
        oos = [r for r in rows if r["meta"]["oos"]]
        ex["in-scope accuracy"] = M.accuracy(ins)
        ex["OOS recall"] = sum(r["pred"] == "oos" for r in oos) / max(len(oos), 1)
        pred_oos = [r for r in rows if r["pred"] == "oos"]
        ex["OOS precision"] = sum(r["gold"] == "oos" for r in pred_oos) / max(len(pred_oos), 1)
        for t in (0.3, 0.5, 0.7):  # abstain-as-OOS when confidence < t
            rec = sum(r["pred"] == "oos" or r["confidence"] < t for r in oos) / max(len(oos), 1)
            keep = sum(r["ok"] and r["confidence"] >= t for r in ins) / max(len(ins), 1)
            ex[f"conf<{t} as OOS: OOS recall / in-scope acc"] = f"{rec:.3f} / {keep:.3f}"
    if task in ("injection", "halueval"):
        ex["F1 (positive = true)"] = M.f1_for(rows, "true")
        ex["AUROC from P(true)"] = M.auroc([r["probs"]["true"] for r in rows], [r["gold"] == "true" for r in rows])
        neg = [r for r in rows if r["gold"] == "false"]
        ex["false-positive rate"] = sum(r["pred"] == "true" for r in neg) / max(len(neg), 1)
    return ex


def summarize(task, backend, rows, labels):
    ok_rows = [r for r in rows if "error" not in r]
    s = {"n": len(rows), "errors": len(rows) - len(ok_rows)}
    if not ok_rows:
        return s
    r = ok_rows
    s["accuracy"] = M.accuracy(r)
    s["accuracy 95% CI"] = M.bootstrap_ci(r, M.accuracy, n=2000)
    s["macro-F1"] = M.macro_f1(category_view(task, r), labels if task != "when2call" else
                               ["cannot_answer", "direct", "request_for_info", "tool_call"])
    s["ECE"] = M.ece(r)
    s["Brier"] = M.brier(r, labels if task != "when2call" else sorted({k for x in r for k in x["probs"]}))
    s["selective"] = [M.selective(r, t) for t in THRESHOLDS]
    s["client_ms"] = M.percentiles([x["client_ms"] for x in r])
    s["server_ms"] = M.percentiles([x.get("server_ms") for x in r])
    toks = sum(x["input_tokens"] for x in r)
    s["input_tokens/item"] = toks / len(r)
    if backend == "jev":
        s["USD per 1k decisions"] = toks / len(r) * 1000 * JEV_USD_PER_TOKEN
    else:
        srv = [x["server_ms"] for x in r if x.get("server_ms") is not None]
        if srv:
            s["USD per 1k decisions"] = sum(srv) / len(srv) / 1000 * 1000 / 3600 * DECIDER_USD_PER_HOUR
    s["models seen"] = sorted({x.get("model") or "?" for x in r})
    s["extras"] = task_extras(task, r)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    root = HERE / "results" / args.run_id
    backends = sorted(p.name for p in root.iterdir() if p.is_dir())
    subs = sorted({t.name for b in backends for t in (root / b).iterdir() if t.is_dir()})
    md = [f"# Results: run `{args.run_id}`\n", f"Backends: {', '.join(backends)}\n"]
    allsum = {}
    for sub in subs:
        task = sub.split("__")[0]
        if task not in TASKS:  # e.g. jevbench: the pinned harness writes its own summary.json
            continue
        data = {b: load_rows(root / b / sub / "results.jsonl") for b in backends if (root / b / sub / "results.jsonl").exists()}
        if not data:
            continue
        any_items = TASKS[task].load(limit=1, variant=sub.split("__")[1] if "__" in sub else TASKS[task].variants[0])
        labels = TASKS[task].labels(any_items)
        sums = {b: summarize(task, b, rows, labels) for b, rows in data.items()}
        allsum[sub] = sums
        md.append(f"\n## {sub}\n")
        if TASKS[task].notes:
            md.append(f"_Note: {TASKS[task].notes}_\n")
        md.append("| metric | " + " | ".join(sums) + " |")
        md.append("|---|" + "---|" * len(sums))
        def row(name, f):
            md.append(f"| {name} | " + " | ".join(f(s) for s in sums.values()) + " |")
        row("items (errors)", lambda s: f"{s['n']} ({s['errors']})")
        row("accuracy [95% CI]", lambda s: f"**{fmt(s.get('accuracy'))}** [{fmt(s['accuracy 95% CI'][0])}, {fmt(s['accuracy 95% CI'][1])}]" if "accuracy" in s else "-")
        row("macro-F1", lambda s: fmt(s.get("macro-F1")))
        row("ECE / Brier", lambda s: f"{fmt(s.get('ECE'))} / {fmt(s.get('Brier'))}")
        for i, t in enumerate(THRESHOLDS):
            row(f"conf >= {t}: coverage / accuracy", lambda s, i=i: f"{fmt(s['selective'][i]['coverage'])} / {fmt(s['selective'][i]['accuracy'])}" if "selective" in s else "-")
        for k in sorted({k for s in sums.values() for k in s.get("extras", {})}):
            row(k, lambda s, k=k: (v if isinstance(v := s.get("extras", {}).get(k), str) else fmt(v)))
        row("client ms p50 / p95", lambda s: f"{fmt(s['client_ms']['p50'], 0)} / {fmt(s['client_ms']['p95'], 0)}" if "client_ms" in s else "-")
        row("server ms p50 / p95", lambda s: f"{fmt(s['server_ms']['p50'], 0)} / {fmt(s['server_ms']['p95'], 0)}" if "server_ms" in s else "-")
        row("input tokens / item", lambda s: fmt(s.get("input_tokens/item"), 0))
        row("USD per 1k decisions", lambda s: fmt(s.get("USD per 1k decisions"), 4))
        row("model id(s) returned", lambda s: ", ".join(s.get("models seen", [])))
        if len(data) == 2:
            (a, ra), (b, rb) = data.items()
            ia = {r["id"]: r for r in ra if "error" not in r}
            ib = {r["id"]: r for r in rb if "error" not in r}
            common = sorted(set(ia) & set(ib))
            b01, b10, p = M.mcnemar([ia[i]["ok"] for i in common], [ib[i]["ok"] for i in common])
            md.append(f"\nPaired on {len(common)} items: only {b} right = {b01}, only {a} right = {b10}, "
                      f"McNemar exact p = {p:.4g}.\n")
    (root / "report.md").write_text("\n".join(md) + "\n")
    (root / "summary.json").write_text(json.dumps(allsum, indent=1, default=str))
    print("\n".join(md))


if __name__ == "__main__":
    main()
