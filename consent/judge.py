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

    def classify(self, text: str, context: str = "") -> tuple[str, float, float]:
        t = time.perf_counter()
        state = f"Screen title and nearby lines: {context}\nLine to classify: {text}" if context else text
        a = self.agent.system_one(state, {"c": QUESTION})["answers"]["c"]
        return a["choice"], float(a["confidence"]), (time.perf_counter() - t) * 1000
