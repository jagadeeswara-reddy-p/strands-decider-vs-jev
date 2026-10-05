"""Turn bench/results/*.json into side-by-side comparison tables (markdown on stdout)."""
import json
import statistics
import sys
from pathlib import Path

RES = Path(__file__).parent / "results"
BUCKETS = ["win/row", "win/col", "win/diag", "block/row", "block/col", "block/diag", "quiet"]
TITLES = {"naive_choice": "Naive", "strategic_choice": "Strategic", "noul_score": "Noul+Score", "full_rules": "Full Rules"}


def pct(ok, n):
    return f"{ok}/{n} ({100 * ok / n:.0f}%)" if n else "-"


def med(xs):
    xs = [x for x in xs if x is not None]
    return f"{statistics.median(xs):.0f}" if xs else "-"


def load():
    return {p.stem: json.loads(p.read_text()) for p in sorted(RES.glob("*.json"))}


def main():
    runs = load()
    backends = list(runs)
    print("## Tactical accuracy (64 positions, O to move)\n")
    print("| Strategy | Backend | " + " | ".join(BUCKETS) + " | **Total** |")
    print("|---|---|" + "---|" * (len(BUCKETS) + 1))
    for sid, title in TITLES.items():
        for b in backends:
            rows = runs[b]["strategies"][sid]["tactics"]
            cells = []
            for k in BUCKETS:
                rs = [r for r in rows if r["bucket"] == k]
                cells.append(f"{sum(r['ok'] for r in rs)}/{len(rs)}")
            print(f"| {title} | {b} | " + " | ".join(cells) + f" | **{pct(sum(r['ok'] for r in rows), len(rows))}** |")

    print("\n## Full games (strategy plays O, X moves first)\n")
    print("| Strategy | Backend | vs random W/D/L | vs perfect W/D/L |")
    print("|---|---|---|---|")
    for sid, title in TITLES.items():
        for b in backends:
            g = runs[b]["strategies"][sid]["games"]
            f = lambda gs: "/".join(str(sum(r["result"] == k for r in gs)) for k in ("win", "draw", "loss")) + \
                (f" ({sum(r['result'] == 'error' for r in gs)} err)" if any(r["result"] == "error" for r in gs) else "")
            print(f"| {title} | {b} | {f(g['random'])} | {f(g['minimax'])} |")

    print("\n## Cost of a move (tactics suite)\n")
    print("| Strategy | Backend | calls/move | median client ms/move | median server ms/move | input tokens/move | errors |")
    print("|---|---|---|---|---|---|---|")
    for sid, title in TITLES.items():
        for b in backends:
            rows = [r for r in runs[b]["strategies"][sid]["tactics"] if "error" not in r]
            errs = len(runs[b]["strategies"][sid]["tactics"]) - len(rows)
            print(f"| {title} | {b} | {statistics.mean(r['calls'] for r in rows):.2f} | {med(r['client_ms'] for r in rows)} | "
                  f"{med(r['server_ms'] for r in rows)} | {statistics.mean(r['input_tokens'] for r in rows):.0f} | {errs} |")

    print("\n## Calibration (single-call strategies, tactics suite)\n")
    print("| Strategy | Backend | conf >= 0.9: accuracy | conf 0.5-0.9 | conf < 0.5 | mean conf when right | mean conf when wrong |")
    print("|---|---|---|---|---|---|---|")
    for sid in ("naive_choice", "strategic_choice", "full_rules"):
        for b in backends:
            rows = [r for r in runs[b]["strategies"][sid]["tactics"] if r.get("confidence") is not None]
            band = lambda lo, hi: [r for r in rows if lo <= r["confidence"] < hi]
            cell = lambda rs: pct(sum(r["ok"] for r in rs), len(rs))
            mc = lambda rs: f"{statistics.mean(r['confidence'] for r in rs):.2f}" if rs else "-"
            print(f"| {TITLES[sid]} | {b} | {cell(band(0.9, 1.01))} | {cell(band(0.5, 0.9))} | {cell(band(0, 0.5))} | "
                  f"{mc([r for r in rows if r['ok']])} | {mc([r for r in rows if not r['ok']])} |")

    print("\n## Run totals\n")
    for b in backends:
        r = runs[b]
        print(f"- **{b}**: {r['total_calls']} calls, {r['total_input_tokens']:,} input tokens, {r['wall_s']} s wall")


if __name__ == "__main__":
    sys.exit(main())
