# Results: run `full-2026-10-05`

Backends: decider, jev


## banking77

| metric | decider | jev |
|---|---|---|
| items (errors) | 3080 (0) | 3080 (0) |
| accuracy [95% CI] | **0.841** [0.828, 0.854] | **0.805** [0.791, 0.819] |
| macro-F1 | 0.842 | 0.797 |
| ECE / Brier | 0.032 / 0.235 | 0.091 / 0.305 |
| conf >= 0.8: coverage / accuracy | 0.626 / 0.960 | 0.790 / 0.895 |
| conf >= 0.9: coverage / accuracy | 0.483 / 0.978 | 0.711 / 0.923 |
| conf >= 0.95: coverage / accuracy | 0.374 / 0.984 | 0.640 / 0.941 |
| client ms p50 / p95 | 154 / 157 | 298 / 381 |
| server ms p50 / p95 | 152 / 155 | - / - |
| input tokens / item | 994 | 1691 |
| USD per 1k decisions | 0.0340 | 0.0710 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 3080 items: only jev right = 151, only decider right = 263, McNemar exact p = 4.07e-08.


## clinc

| metric | decider | jev |
|---|---|---|
| items (errors) | 5500 (0) | 5500 (0) |
| accuracy [95% CI] | **0.822** [0.812, 0.832] | **0.895** [0.887, 0.904] |
| macro-F1 | 0.837 | 0.899 |
| ECE / Brier | 0.019 / 0.256 | 0.024 / 0.159 |
| conf >= 0.8: coverage / accuracy | 0.612 / 0.945 | 0.841 / 0.955 |
| conf >= 0.9: coverage / accuracy | 0.480 / 0.967 | 0.771 / 0.964 |
| conf >= 0.95: coverage / accuracy | 0.389 / 0.976 | 0.703 / 0.971 |
| OOS precision | 0.944 | 0.873 |
| OOS recall | 0.612 | 0.852 |
| conf<0.3 as OOS: OOS recall / in-scope acc | 0.625 / 0.868 | 0.853 / 0.905 |
| conf<0.5 as OOS: OOS recall / in-scope acc | 0.750 / 0.845 | 0.867 / 0.898 |
| conf<0.7 as OOS: OOS recall / in-scope acc | 0.863 / 0.752 | 0.917 / 0.853 |
| in-scope accuracy | 0.869 | 0.905 |
| client ms p50 / p95 | 240 / 241 | 326 / 396 |
| server ms p50 / p95 | 237 / 239 | - / - |
| input tokens / item | 1508 | 2527 |
| USD per 1k decisions | 0.0530 | 0.1061 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 5500 items: only jev right = 611, only decider right = 209, McNemar exact p = 1.938e-46.


## halueval

_Note: built from HotpotQA, which is in Strands Decider's training mix -> possible contamination_

| metric | decider | jev |
|---|---|---|
| items (errors) | 1000 (0) | 1000 (0) |
| accuracy [95% CI] | **0.637** [0.609, 0.668] | **0.871** [0.851, 0.890] |
| macro-F1 | 0.583 | 0.871 |
| ECE / Brier | 0.116 / 0.446 | 0.031 / 0.170 |
| conf >= 0.8: coverage / accuracy | 0.493 / 0.836 | 0.814 / 0.948 |
| conf >= 0.9: coverage / accuracy | 0.000 / - | 0.705 / 0.967 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.573 / 0.986 |
| AUROC from P(true) | 0.911 | 0.960 |
| F1 (positive = true) | 0.432 | 0.864 |
| false-positive rate | 0.002 | 0.080 |
| client ms p50 / p95 | 69 / 72 | 306 / 365 |
| server ms p50 / p95 | 67 / 69 | - / - |
| input tokens / item | 236 | 465 |
| USD per 1k decisions | 0.0151 | 0.0195 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 1000 items: only jev right = 274, only decider right = 40, McNemar exact p = 4.83e-44.


## injection

_Note: deepset's 'injection' label is broad: includes role-play / persona prompts_

| metric | decider | jev |
|---|---|---|
| items (errors) | 116 (0) | 116 (0) |
| accuracy [95% CI] | **0.509** [0.422, 0.595] | **0.750** [0.664, 0.828] |
| macro-F1 | 0.379 | 0.738 |
| ECE / Brier | 0.283 / 0.617 | 0.169 / 0.387 |
| conf >= 0.8: coverage / accuracy | 0.698 / 0.691 | 0.853 / 0.768 |
| conf >= 0.9: coverage / accuracy | 0.000 / - | 0.698 / 0.864 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.612 / 0.873 |
| AUROC from P(true) | 0.870 | 0.962 |
| F1 (positive = true) | 0.095 | 0.681 |
| false-positive rate | 0.000 | 0.000 |
| client ms p50 / p95 | 68 / 70 | 303 / 356 |
| server ms p50 / p95 | 66 / 68 | - / - |
| input tokens / item | 140 | 370 |
| USD per 1k decisions | 0.0148 | 0.0156 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 116 items: only jev right = 29, only decider right = 1, McNemar exact p = 5.774e-08.


## injection__paraphrase

_Note: deepset's 'injection' label is broad: includes role-play / persona prompts_

| metric | decider | jev |
|---|---|---|
| items (errors) | 116 (0) | 116 (0) |
| accuracy [95% CI] | **0.500** [0.414, 0.586] | **0.750** [0.664, 0.828] |
| macro-F1 | 0.362 | 0.738 |
| ECE / Brier | 0.367 / 0.672 | 0.158 / 0.376 |
| conf >= 0.8: coverage / accuracy | 0.853 / 0.566 | 0.836 / 0.804 |
| conf >= 0.9: coverage / accuracy | 0.319 / 0.946 | 0.647 / 0.867 |
| conf >= 0.95: coverage / accuracy | 0.000 / - | 0.586 / 0.882 |
| AUROC from P(true) | 0.933 | 0.961 |
| F1 (positive = true) | 0.065 | 0.681 |
| false-positive rate | 0.000 | 0.000 |
| client ms p50 / p95 | 69 / 71 | 305 / 404 |
| server ms p50 / p95 | 67 / 69 | - / - |
| input tokens / item | 120 | 350 |
| USD per 1k decisions | 0.0154 | 0.0147 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 116 items: only jev right = 29, only decider right = 0, McNemar exact p = 3.725e-09.


## when2call

_Note: gold is an option key; meta.keymap maps keys back to the dataset category_

| metric | decider | jev |
|---|---|---|
| items (errors) | 3652 (10) | 3652 (0) |
| accuracy [95% CI] | **0.651** [0.636, 0.667] | **0.821** [0.808, 0.834] |
| macro-F1 | 0.493 | 0.622 |
| ECE / Brier | 0.052 / 0.470 | 0.055 / 0.276 |
| conf >= 0.8: coverage / accuracy | 0.172 / 0.941 | 0.757 / 0.895 |
| conf >= 0.9: coverage / accuracy | 0.042 / 0.974 | 0.634 / 0.918 |
| conf >= 0.95: coverage / accuracy | 0.004 / 0.933 | 0.528 / 0.934 |
| acc | gold=cannot_answer | 0.369 | 0.742 |
| acc | gold=request_for_info | 0.784 | 0.827 |
| acc | gold=tool_call | 0.826 | 0.896 |
| acc | no tools offered | 0.461 | 0.829 |
| answer-hallucination rate (picks 'direct') | 0.062 | 0.026 |
| macro-F1 (3 gold classes) | 0.658 | 0.830 |
| tool-hallucination rate | 0.262 | 0.089 |
| client ms p50 / p95 | 158 / 404 | 318 / 397 |
| server ms p50 / p95 | 156 / 402 | - / - |
| input tokens / item | 1186 | 1378 |
| USD per 1k decisions | 0.0418 | 0.0579 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 3642 items: only jev right = 819, only decider right = 199, McNemar exact p = 8.08e-90.


## when2call__labeled

_Note: gold is an option key; meta.keymap maps keys back to the dataset category_

| metric | decider | jev |
|---|---|---|
| items (errors) | 3652 (10) | 3652 (0) |
| accuracy [95% CI] | **0.641** [0.626, 0.657] | **0.830** [0.818, 0.843] |
| macro-F1 | 0.477 | 0.628 |
| ECE / Brier | 0.024 / 0.472 | 0.063 / 0.259 |
| conf >= 0.8: coverage / accuracy | 0.216 / 0.927 | 0.790 / 0.902 |
| conf >= 0.9: coverage / accuracy | 0.074 / 0.966 | 0.669 / 0.925 |
| conf >= 0.95: coverage / accuracy | 0.013 / 0.957 | 0.576 / 0.939 |
| acc | gold=cannot_answer | 0.377 | 0.768 |
| acc | gold=request_for_info | 0.647 | 0.828 |
| acc | gold=tool_call | 0.899 | 0.895 |
| acc | no tools offered | 0.415 | 0.829 |
| answer-hallucination rate (picks 'direct') | 0.035 | 0.021 |
| macro-F1 (3 gold classes) | 0.636 | 0.837 |
| tool-hallucination rate | 0.342 | 0.091 |
| client ms p50 / p95 | 163 / 410 | 314 / 375 |
| server ms p50 / p95 | 161 / 408 | - / - |
| input tokens / item | 1204 | 1396 |
| USD per 1k decisions | 0.0429 | 0.0587 |
| model id(s) returned | strands-decider-2B-hobson-v19 | jev-1.13.0 |

Paired on 3642 items: only jev right = 889, only decider right = 198, McNemar exact p = 5.684e-105.

