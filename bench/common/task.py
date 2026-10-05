"""What a benchmark task looks like to the runner."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Item:
    id: str
    state: Any                 # sent as-is as the systemone `state`
    questions: dict            # sent as-is as the systemone `questions`
    gold: str                  # gold label (for noul tasks: "true" / "false")
    meta: dict = field(default_factory=dict)


@dataclass
class Prediction:
    pred: str                  # predicted label
    probs: dict[str, float]    # label -> probability
    confidence: float          # max(probs) -- the number we calibrate
    raw_confidence: float | None = None  # the backend's own `confidence` field, if any


def from_choice(answer: dict) -> Prediction:
    probs = {k: float(v) for k, v in (answer.get("probabilities") or {}).items()}
    pred = answer.get("choice") or max(probs, key=probs.get)
    return Prediction(pred=pred, probs=probs, confidence=max(probs.values()) if probs else 0.0,
                      raw_confidence=answer.get("confidence"))


def from_noul(answer: dict) -> Prediction:
    p = float(answer["noul"])
    return Prediction(pred="true" if p >= 0.5 else "false", probs={"true": p, "false": 1 - p},
                      confidence=max(p, 1 - p))


@dataclass
class Task:
    name: str
    load: Callable[..., list[Item]]          # load(seed=..., limit=..., variant=...) -> items
    parse: Callable[[dict], Prediction]      # answers dict -> Prediction
    labels: Callable[[list[Item]], list[str]]  # full label set, for macro-F1
    variants: tuple[str, ...] = ("default",)
    notes: str = ""
