"""Async client for any /v1/systemone endpoint (Strands Decider or TypeSafe Jev).

Both backends get byte-identical payloads apart from `model`. Secrets come from the
environment and are never written to results.
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from dataclasses import dataclass

import httpx

JEV_URL = "https://api.typesafe.ai/v1/systemone"

BACKENDS = {
    # name: (default url, model field, env var holding the API key or None)
    "decider": ("http://127.0.0.1:8199/v1/systemone", "strands-decider-2B-hobson-v19", None),
    "jev": (JEV_URL, "jev-latest", "TYPESAFE_API_KEY"),
}


class SystemOneError(Exception):
    pass


@dataclass
class Reply:
    answers: dict
    model: str | None
    client_ms: float
    server_ms: float | None
    input_tokens: int
    attempts: int


class SystemOneClient:
    def __init__(self, backend: str, url: str | None = None, timeout: float = 120.0, retries: int = 6):
        default_url, self.model, key_env = BACKENDS[backend]
        self.backend = backend
        self.url = url or os.environ.get(f"{backend.upper()}_URL") or default_url
        self.headers = {"content-type": "application/json"}
        if key_env:
            key = os.environ.get(key_env)
            if not key:
                raise SystemOneError(f"{key_env} is not set")
            self.headers["authorization"] = f"Bearer {key}"
        self.retries = retries
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self._http.aclose()

    async def ask(self, state, questions: dict) -> Reply:
        payload = {"state": state, "model": self.model, "questions": questions}
        last = None
        for attempt in range(1, self.retries + 1):
            t0 = time.perf_counter()
            try:
                r = await self._http.post(self.url, json=payload, headers=self.headers)
            except httpx.HTTPError as ex:
                last = f"{type(ex).__name__}: {ex}"
            else:
                ms = (time.perf_counter() - t0) * 1000
                if r.status_code == 200:
                    d = r.json()
                    return Reply(
                        answers=d.get("answers", {}),
                        model=d.get("model"),
                        client_ms=round(ms, 1),
                        server_ms=d.get("latency_ms"),
                        input_tokens=(d.get("usage") or {}).get("input_tokens", 0),
                        attempts=attempt,
                    )
                last = f"HTTP {r.status_code}: {r.text[:300]}"
                if r.status_code not in (408, 409, 425, 429, 500, 502, 503, 504, 529):
                    raise SystemOneError(last)
            # exponential backoff with jitter: 0.5, 1, 2, 4, 8 s (+/- 25%)
            await asyncio.sleep(0.5 * 2 ** (attempt - 1) * random.uniform(0.75, 1.25))
        raise SystemOneError(f"failed after {self.retries} attempts: {last}")
