"""Metrics and paired statistics. Pure numpy, no sklearn."""
from __future__ import annotations

import math

import numpy as np


def accuracy(rows):
    return float(np.mean([r["ok"] for r in rows])) if rows else float("nan")


def macro_f1(rows, labels):
    f1s = []
    for lab in labels:
        tp = sum(r["pred"] == lab and r["gold"] == lab for r in rows)
        fp = sum(r["pred"] == lab and r["gold"] != lab for r in rows)
        fn = sum(r["pred"] != lab and r["gold"] == lab for r in rows)
        if tp + fp + fn == 0:
            continue  # label absent from gold and predictions
        f1s.append(2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f1s)) if f1s else float("nan")


def f1_for(rows, label):
    tp = sum(r["pred"] == label and r["gold"] == label for r in rows)
    fp = sum(r["pred"] == label and r["gold"] != label for r in rows)
    fn = sum(r["pred"] != label and r["gold"] == label for r in rows)
    return 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else float("nan")


def ece(rows, bins=10):
    """Top-label ECE over the predicted label's probability."""
    conf = np.array([r["confidence"] for r in rows])
    ok = np.array([r["ok"] for r in rows], dtype=float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi) if lo > 0 else (conf >= lo) & (conf <= hi)
        if m.any():
            total += m.mean() * abs(ok[m].mean() - conf[m].mean())
    return float(total)


def brier(rows, labels):
    """Multi-class Brier score over the full label set (missing probs count as 0)."""
    s = []
    for r in rows:
        s.append(sum((r["probs"].get(l, 0.0) - (1.0 if l == r["gold"] else 0.0)) ** 2 for l in labels))
    return float(np.mean(s))


def selective(rows, threshold):
    """Coverage and accuracy among answers with confidence >= threshold."""
    kept = [r for r in rows if r["confidence"] >= threshold]
    return {"threshold": threshold, "coverage": len(kept) / len(rows) if rows else float("nan"),
            "accuracy": accuracy(kept) if kept else float("nan"), "n": len(kept)}


def auroc(scores, positives):
    """AUROC of `scores` for binary `positives` (Mann-Whitney U)."""
    s = np.asarray(scores, float)
    y = np.asarray(positives, bool)
    if y.all() or (~y).all():
        return float("nan")
    ranks = s.argsort().argsort() + 1.0
    # average ranks for ties
    for v in np.unique(s):
        idx = s == v
        if idx.sum() > 1:
            ranks[idx] = ranks[idx].mean()
    n1, n0 = y.sum(), (~y).sum()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def percentiles(xs, ps=(50, 95, 99)):
    xs = [x for x in xs if x is not None]
    return {f"p{p}": float(np.percentile(xs, p)) for p in ps} if xs else {f"p{p}": None for p in ps}


def bootstrap_ci(rows, fn, n=10_000, seed=0, alpha=0.05):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(rows))
    vals = [fn([rows[i] for i in rng.choice(idx, len(idx))]) for _ in range(n)]
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def mcnemar(a_ok, b_ok):
    """Exact two-sided McNemar on paired correctness lists. Returns (b01, b10, p)."""
    b01 = sum((not a) and b for a, b in zip(a_ok, b_ok))
    b10 = sum(a and (not b) for a, b in zip(a_ok, b_ok))
    n = b01 + b10
    if n == 0:
        return b01, b10, 1.0
    k = min(b01, b10)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return b01, b10, min(1.0, 2 * p)
