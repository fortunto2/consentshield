"""Local decision model: Laya (Apache 2.0 reproduction of TypeSafe's Jev), on this Mac, no network.

One pass answers a typed question with a calibrated distribution. We ask it which data category a
piece of screen text belongs to; the confidence decides whether the gate may act alone.
"""

from __future__ import annotations

import os
import time

from .schemas import CATEGORIES

QUESTION = {
    "type": "choice",
    "instructions": "What kind of information is shown in this text captured from a computer screen",
    "criteria": CATEGORIES,
}


class Judge:
    def __init__(self, device: str | None = None):
        import laya  # heavy import: torch

        self.agent = laya.load("convaiinnovations/laya", subfolder="multilingual",
                               device=device or os.environ.get("LAYA_DEVICE", "mps"))
        self.agent.system_one("warm up", {"c": QUESTION})
        self._seen: dict[tuple[str, str], tuple[str, float]] = {}

    def classify(self, text: str, context: str = "") -> tuple[str, float, float]:
        """(category, confidence, ms). Deterministic for a given text, so re-gating the same frame under
        another purpose or after a user answer costs nothing."""
        t = time.perf_counter()
        choice, conf = self._ask(text, context)
        return choice, conf, (time.perf_counter() - t) * 1000

    def _ask(self, text: str, context: str) -> tuple[str, float]:
        if (key := (text, context)) not in self._seen:
            state = f"Screen title and nearby lines: {context}\nLine to classify: {text}" if context else text
            a = self.agent.system_one(state, {"c": QUESTION})["answers"]["c"]
            self._seen[key] = (a["choice"], float(a["confidence"]))
            if len(self._seen) > 4096:
                self._seen.pop(next(iter(self._seen)))
        return self._seen[key]
