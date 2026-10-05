# Results: run `dry`

Backends: decider, jev


## banking77

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.900** [0.700, 1.000] | **0.900** [0.700, 1.000] |
| macro-F1 | 0.800 | 0.800 |
| ECE / Brier | 0.135 / 0.107 | 0.144 / 0.186 |
| conf >= 0.8: coverage / accuracy | 0.800 / 1.000 | 0.900 / 0.889 |
| conf >= 0.9: coverage / accuracy | 0.700 / 1.000 | 0.800 / 1.000 |
| conf >= 0.95: coverage / accuracy | 0.500 / 1.000 | 0.800 / 1.000 |
| client ms p50 / p95 | 420 / 434 | 297 / 364 |
| server ms p50 / p95 | 132 / 133 | - / - |
| input tokens / item | 991 | 1688 |
| USD per 1k decisions | 0.0296 | 0.0709 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 0, only decider right = 0, McNemar exact p = 1.


## clinc

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.800** [0.500, 1.000] | **0.800** [0.500, 1.000] |
| macro-F1 | 0.667 | 0.727 |
| ECE / Brier | 0.111 / 0.230 | 0.167 / 0.356 |
| conf >= 0.8: coverage / accuracy | 0.700 / 1.000 | 0.900 / 0.889 |
| conf >= 0.9: coverage / accuracy | 0.700 / 1.000 | 0.800 / 0.875 |
| conf >= 0.95: coverage / accuracy | 0.600 / 1.000 | 0.800 / 0.875 |
| OOS precision | 0.000 | 0.000 |
| OOS recall | 0.000 | 0.000 |
| conf<0.3 as OOS: OOS recall / in-scope acc | 0.000 / 0.889 | 0.000 / 0.889 |
| conf<0.5 as OOS: OOS recall / in-scope acc | 1.000 / 0.889 | 0.000 / 0.889 |
| conf<0.7 as OOS: OOS recall / in-scope acc | 1.000 / 0.889 | 0.000 / 0.889 |
| in-scope accuracy | 0.889 | 0.889 |
| client ms p50 / p95 | 505 / 522 | 290 / 378 |
| server ms p50 / p95 | 216 / 217 | - / - |
| input tokens / item | 1508 | 2527 |
| USD per 1k decisions | 0.0483 | 0.1061 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 0, only decider right = 0, McNemar exact p = 1.


## halueval

_Note: built from HotpotQA, which is in Strands Decider's training mix -> possible contamination_

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.600** [0.300, 0.900] | **0.700** [0.400, 1.000] |
| macro-F1 | 0.583 | 0.697 |
| ECE / Brier | 0.237 / 0.520 | 0.193 / 0.383 |
| conf >= 0.8: coverage / accuracy | 0.400 / 0.750 | 0.700 / 0.857 |
| conf >= 0.9: coverage / accuracy | 0.000 / - | 0.500 / 0.800 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.200 / 1.000 |
| AUROC from P(true) | 0.875 | 0.917 |
| F1 (positive = true) | 0.500 | 0.727 |
| false-positive rate | 0.000 | 0.250 |
| client ms p50 / p95 | 349 / 847 | 290 / 390 |
| server ms p50 / p95 | 67 / 68 | - / - |
| input tokens / item | 233 | 465 |
| USD per 1k decisions | 0.0149 | 0.0195 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 2, only decider right = 1, McNemar exact p = 1.


## injection

_Note: deepset's 'injection' label is broad: includes role-play / persona prompts_

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.500** [0.200, 0.800] | **0.600** [0.300, 0.900] |
| macro-F1 | 0.333 | 0.524 |
| ECE / Brier | 0.310 / 0.645 | 0.321 / 0.446 |
| conf >= 0.8: coverage / accuracy | 0.700 / 0.714 | 0.700 / 0.714 |
| conf >= 0.9: coverage / accuracy | 0.000 / - | 0.500 / 1.000 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.500 / 1.000 |
| AUROC from P(true) | 0.880 | 1.000 |
| F1 (positive = true) | 0.000 | 0.333 |
| false-positive rate | 0.000 | 0.000 |
| client ms p50 / p95 | 348 / 634 | 293 / 364 |
| server ms p50 / p95 | 66 / 335 | - / - |
| input tokens / item | 141 | 371 |
| USD per 1k decisions | 0.0260 | 0.0156 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 1, only decider right = 0, McNemar exact p = 1.


## injection__paraphrase

_Note: deepset's 'injection' label is broad: includes role-play / persona prompts_

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.500** [0.200, 0.800] | **0.700** [0.400, 0.900] |
| macro-F1 | 0.333 | 0.670 |
| ECE / Brier | 0.425 / 0.661 | 0.217 / 0.399 |
| conf >= 0.8: coverage / accuracy | 0.900 / 0.556 | 0.600 / 0.833 |
| conf >= 0.9: coverage / accuracy | 0.400 / 1.000 | 0.500 / 1.000 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.500 / 1.000 |
| AUROC from P(true) | 1.000 | 1.000 |
| F1 (positive = true) | 0.000 | 0.571 |
| false-positive rate | 0.000 | 0.000 |
| client ms p50 / p95 | 348 / 364 | 298 / 351 |
| server ms p50 / p95 | 66 / 68 | - / - |
| input tokens / item | 121 | 351 |
| USD per 1k decisions | 0.0148 | 0.0147 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 2, only decider right = 0, McNemar exact p = 0.5.


## when2call

_Note: gold is an option key; meta.keymap maps keys back to the dataset category_

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.600** [0.300, 0.900] | **0.800** [0.500, 1.000] |
| macro-F1 | 0.354 | 0.775 |
| ECE / Brier | 0.341 / 0.458 | 0.094 / 0.234 |
| conf >= 0.8: coverage / accuracy | 0.200 / 1.000 | 0.700 / 1.000 |
| conf >= 0.9: coverage / accuracy | 0.100 / 1.000 | 0.700 / 1.000 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.700 / 1.000 |
| acc | gold=cannot_answer | 0.000 | 0.500 |
| acc | gold=request_for_info | 0.750 | 1.000 |
| acc | gold=tool_call | 0.750 | 0.750 |
| acc | no tools offered | 0.000 | 1.000 |
| answer-hallucination rate (picks 'direct') | 0.100 | 0.000 |
| macro-F1 (3 gold classes) | 0.472 | 0.775 |
| tool-hallucination rate | 0.333 | 0.000 |
| client ms p50 / p95 | 441 / 36410 | 303 / 412 |
| server ms p50 / p95 | 156 / 35947 | - / - |
| input tokens / item | 1203 | 1393 |
| USD per 1k decisions | 1.4937 | 0.0585 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 3, only decider right = 1, McNemar exact p = 0.625.


## when2call__labeled

_Note: gold is an option key; meta.keymap maps keys back to the dataset category_

| metric | decider | jev |
|---|---|---|
| items (errors) | 10 (0) | 10 (0) |
| accuracy [95% CI] | **0.600** [0.300, 0.900] | **0.800** [0.500, 1.000] |
| macro-F1 | 0.613 | 0.769 |
| ECE / Brier | 0.214 / 0.480 | 0.179 / 0.262 |
| conf >= 0.8: coverage / accuracy | 0.200 / 1.000 | 0.800 / 0.875 |
| conf >= 0.9: coverage / accuracy | 0.100 / 1.000 | 0.700 / 1.000 |
| conf >= 0.95: coverage / accuracy | 0.100 / 1.000 | 0.700 / 1.000 |
| acc | gold=cannot_answer | 0.500 | 0.500 |
| acc | gold=request_for_info | 0.500 | 1.000 |
| acc | gold=tool_call | 0.750 | 0.750 |
| acc | no tools offered | 0.000 | 1.000 |
| answer-hallucination rate (picks 'direct') | 0.000 | 0.000 |
| macro-F1 (3 gold classes) | 0.613 | 0.769 |
| tool-hallucination rate | 0.500 | 0.167 |
| client ms p50 / p95 | 385 / 884 | 308 / 363 |
| server ms p50 / p95 | 97 / 449 | - / - |
| input tokens / item | 1221 | 1411 |
| USD per 1k decisions | 0.0403 | 0.0592 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 10 items: only jev right = 4, only decider right = 2, McNemar exact p = 0.6875.

