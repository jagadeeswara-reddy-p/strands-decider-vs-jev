## Tactical accuracy (64 positions, O to move)

| Strategy | Backend | win/row | win/col | win/diag | block/row | block/col | block/diag | quiet | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| Naive | decider | 4/8 | 3/8 | 6/8 | 2/8 | 3/8 | 2/8 | 8/16 | **28/64 (44%)** |
| Naive | jev | 3/8 | 2/8 | 4/8 | 3/8 | 0/8 | 4/8 | 7/16 | **23/64 (36%)** |
| Strategic | decider | 3/8 | 2/8 | 5/8 | 2/8 | 3/8 | 2/8 | 8/16 | **25/64 (39%)** |
| Strategic | jev | 1/8 | 3/8 | 4/8 | 4/8 | 1/8 | 5/8 | 8/16 | **26/64 (41%)** |
| Noul+Score | decider | 7/8 | 5/8 | 3/8 | 1/8 | 3/8 | 2/8 | 8/16 | **29/64 (45%)** |
| Noul+Score | jev | 8/8 | 4/8 | 5/8 | 5/8 | 3/8 | 3/8 | 8/16 | **36/64 (56%)** |
| Full Rules | decider | 4/8 | 3/8 | 6/8 | 1/8 | 1/8 | 2/8 | 10/16 | **27/64 (42%)** |
| Full Rules | jev | 6/8 | 5/8 | 7/8 | 4/8 | 3/8 | 3/8 | 9/16 | **37/64 (58%)** |

## Full games (strategy plays O, X moves first)

| Strategy | Backend | vs random W/D/L | vs perfect W/D/L |
|---|---|---|---|
| Naive | decider | 2/1/2 | 0/1/4 |
| Naive | jev | 2/0/3 | 0/1/4 |
| Strategic | decider | 3/0/2 | 0/0/5 |
| Strategic | jev | 3/0/2 | 0/1/4 |
| Noul+Score | decider | 3/0/2 | 0/0/5 |
| Noul+Score | jev | 3/0/2 | 0/0/5 |
| Full Rules | decider | 2/0/3 | 0/0/5 |
| Full Rules | jev | 3/1/1 | 0/1/4 |

## Cost of a move (tactics suite)

| Strategy | Backend | calls/move | median client ms/move | median server ms/move | input tokens/move | errors |
|---|---|---|---|---|---|---|
| Naive | decider | 1.00 | 347 | 66 | 132 | 0 |
| Naive | jev | 1.00 | 295 | - | 383 | 0 |
| Strategic | decider | 1.00 | 348 | 66 | 204 | 0 |
| Strategic | jev | 1.00 | 301 | - | 455 | 0 |
| Noul+Score | decider | 1.25 | 419 | 138 | 564 | 0 |
| Noul+Score | jev | 1.36 | 334 | - | 831 | 0 |
| Full Rules | decider | 1.00 | 362 | 81 | 657 | 0 |
| Full Rules | jev | 1.00 | 299 | - | 894 | 0 |

## Calibration (single-call strategies, tactics suite)

| Strategy | Backend | conf >= 0.9: accuracy | conf 0.5-0.9 | conf < 0.5 | mean conf when right | mean conf when wrong |
|---|---|---|---|---|---|---|
| Naive | decider | - | - | 28/64 (44%) | 0.14 | 0.14 |
| Naive | jev | - | 0/2 (0%) | 23/62 (37%) | 0.18 | 0.24 |
| Strategic | decider | - | - | 25/64 (39%) | 0.21 | 0.23 |
| Strategic | jev | - | 0/9 (0%) | 26/55 (47%) | 0.26 | 0.30 |
| Full Rules | decider | - | 3/6 (50%) | 24/58 (41%) | 0.28 | 0.29 |
| Full Rules | jev | - | 8/12 (67%) | 29/52 (56%) | 0.34 | 0.30 |

## Run totals

- **decider**: 414 calls, 167,112 input tokens, 181.1 s wall
- **jev**: 446 calls, 283,772 input tokens, 154.2 s wall
