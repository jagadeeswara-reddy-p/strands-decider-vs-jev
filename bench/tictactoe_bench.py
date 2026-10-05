"""Benchmark the play-jev-tictactoe strategies against two /v1/systemone backends.

Reuses the game's own engine.py, strategies.py and jev_client.py unchanged, so each backend
sees byte-identical prompts. Two suites, both seeded so every backend gets the same work:

  tactics  sampled positions with O to move, graded against the game's minimax solver:
           win   -- O has a winning cell; correct = takes a win
           block -- O has no win and X has exactly one threat; correct = blocks it
           quiet -- nothing forced; correct = a minimax-optimal (non-losing) move
           win/block are stratified by line type (row/col/diag)
  games    O (the strategy) vs X = random player or X = perfect minimax player

    python tictactoe_bench.py --backend decider --url http://127.0.0.1:8199/v1/systemone
    python tictactoe_bench.py --backend jev        # needs TYPESAFE_API_KEY
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import statistics
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parent.parent / "play-jev-tictactoe"
sys.path.insert(0, str(GAME))

import engine as e  # noqa: E402
import strategies as strat  # noqa: E402
from jev_client import JevClient, JevError  # noqa: E402

O, X = "O", "X"
LINE_TYPE = {line: ("row" if i < 3 else "col" if i < 6 else "diag") for i, line in enumerate(e.WIN_LINES)}


# ------------------------------------------------------------------ position suite

def completing_cells(board, sym):
    """Empty cells that complete a line for `sym`, with the line type each completes."""
    out = {}
    for line in e.WIN_LINES:
        vals = [board[i] for i in line]
        if vals.count(sym) == 2 and vals.count(".") == 1:
            out.setdefault(line[vals.index(".")], set()).add(LINE_TYPE[line])
    return out


def reachable_o_to_move():
    seen, stack, out = set(), [(tuple(e.new_board()), X)], []
    while stack:
        b, turn = stack.pop()
        if (b, turn) in seen:
            continue
        seen.add((b, turn))
        board = list(b)
        if e.check_winner(board) or e.is_full(board):
            continue
        if turn == O:
            out.append(board)
        for m in e.legal_moves(board):
            stack.append((tuple(e.apply_move(board, m, turn)), O if turn == X else X))
    return out


def build_suite(seed, per_bucket=8, quiet_n=16):
    rng = random.Random(seed)
    buckets: dict[str, list] = {}
    for board in reachable_o_to_move():
        wins, threats = completing_cells(board, O), completing_cells(board, X)
        if wins:
            types = set().union(*wins.values())
            if len(types) == 1:
                buckets.setdefault(f"win/{types.pop()}", []).append((board, sorted(wins)))
        elif len(threats) == 1:
            (cell, types), = threats.items()
            if len(types) == 1:
                buckets.setdefault(f"block/{next(iter(types))}", []).append((board, [cell]))
        elif not threats:
            _, best = e._minimax(board, O, O)
            buckets.setdefault("quiet", []).append((board, sorted(best)))
    suite = []
    for key in sorted(buckets):
        items = buckets[key]
        rng.shuffle(items)
        for board, correct in items[: quiet_n if key == "quiet" else per_bucket]:
            suite.append({"bucket": key, "board": board, "correct": correct})
    return suite


# ------------------------------------------------------------------ running a strategy

def trace_stats(trace):
    server = [s["response"].get("latency_ms") for s in trace if isinstance(s["response"].get("latency_ms"), (int, float))]
    conf = trace[-1].get("parsed", {}).get("confidence")
    return {
        "calls": len(trace),
        "client_ms": round(sum(s["latency_ms"] for s in trace), 1),
        "server_ms": round(sum(server), 1) if server else None,
        "input_tokens": sum(s["usage"].get("input_tokens", 0) for s in trace),
        "confidence": conf,
    }


async def play_move(client, sid, board):
    fn, _ = strat.STRATEGIES[sid]
    cell, trace = await fn(client, board, O)
    return cell, trace_stats(trace)


async def run_tactics(client, sid, suite, log):
    rows = []
    for i, p in enumerate(suite):
        try:
            cell, st = await play_move(client, sid, p["board"])
            ok = cell in p["correct"]
            rows.append({**st, "bucket": p["bucket"], "cell": cell, "ok": ok})
        except (JevError, KeyError, ValueError) as ex:
            rows.append({"bucket": p["bucket"], "error": str(ex)[:200], "ok": False})
        log(f"  tactics {i + 1}/{len(suite)}", end="\r")
    log("")
    return rows


async def run_games(client, sid, opponent, n, seed):
    results = []
    for g in range(n):
        rng = random.Random(seed * 1000 + g)
        e.random.seed(seed * 1000 + g)  # minimax tie-breaks use the module-level RNG
        board, turn, moves = e.new_board(), X, []
        while not e.check_winner(board) and not e.is_full(board):
            if turn == X:
                m = rng.choice(e.legal_moves(board)) if opponent == "random" else e.minimax_move(board, X)
            else:
                try:
                    m, _ = await play_move(client, sid, board)
                except JevError as ex:
                    results.append({"result": "error", "error": str(ex)[:200]})
                    break
            board = e.apply_move(board, m, turn)
            moves.append(m)
            turn = O if turn == X else X
        else:
            w = e.check_winner(board)
            results.append({"result": "win" if w == O else "loss" if w == X else "draw", "moves": moves})
    return results


# ------------------------------------------------------------------ main

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, help="label, e.g. decider or jev")
    ap.add_argument("--url", default=None, help="systemone URL; default TypeSafe's")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--games", type=int, default=5, help="games per opponent per strategy")
    ap.add_argument("--out", default=str(Path(__file__).parent / "results"))
    args = ap.parse_args()

    client = JevClient(base_url=args.url, timeout=60.0)
    suite = build_suite(args.seed)
    out = {"backend": args.backend, "url": client.base_url, "seed": args.seed, "strategies": {}}
    t0 = time.time()
    for sid in strat.STRATEGIES:
        print(f"[{args.backend}] {sid}", flush=True)
        tactics = await run_tactics(client, sid, suite, lambda *a, **k: print(*a, **k, flush=True))
        games = {opp: await run_games(client, sid, opp, args.games, args.seed) for opp in ("random", "minimax")}
        out["strategies"][sid] = {"tactics": tactics, "games": games}
        ok = sum(r["ok"] for r in tactics)
        print(f"  tactics {ok}/{len(tactics)}  games " + "  ".join(
            f"vs {o}: " + "/".join(str(sum(r['result'] == k for r in gs)) for k in ('win', 'draw', 'loss'))
            for o, gs in games.items()), flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    out["total_input_tokens"] = client.total_input_tokens
    out["total_calls"] = client.total_calls
    await client.close()
    Path(args.out).mkdir(parents=True, exist_ok=True)
    path = Path(args.out) / f"{args.backend}.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path} in {out['wall_s']} s, {out['total_calls']} calls")


if __name__ == "__main__":
    asyncio.run(main())
