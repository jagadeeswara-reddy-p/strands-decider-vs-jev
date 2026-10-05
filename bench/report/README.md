# Strands Decider vs Jev: technical benchmark report

This folder contains the review-ready technical report for the Strands Decider versus TypeSafe Jev comparison.

## Audience and scope

The report is written for DOTs, architects, and technical leads. It focuses on workload fit, measured behavior, operational readiness, and deployment economics. It does not treat either system as a general-purpose planner.

## Build

```bash
./build.sh
```

`build.sh` posts `index.html` to the Gotenberg Chromium endpoint at `http://localhost:3555/forms/chromium/convert/html` and writes `out/strands-decider-vs-jev.pdf`. Override the endpoint with `GOTENBERG_URL`.

If Gotenberg is not running:

```bash
docker run --rm -p 3555:3000 gotenberg/gotenberg:8
```

## Evidence

- `../DOSSIER.md`: complete study hand-off and source index.
- `../PREREGISTRATION.md`: frozen protocol, hypotheses, and deviations.
- `../RESULTS.md`: short results summary.
- `../results/full-2026-10-05/report.md`: generated benchmark tables.
- `../results/full-2026-10-05/summary.json`: machine-readable metrics.
- `../results/full-2026-10-05/<backend>/<benchmark>/results.jsonl`: per-item raw results.

Run: `full-2026-10-05`, internal publication only, study cost approximately `$3.67`.
