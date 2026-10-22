"""The consent gate: screen frame in, what the agent may see out, plus a consent ledger entry.

Order matters and is deliberate:
1. Deterministic detectors first (secrets, card numbers, injection). No model can talk them out of it.
2. The local decision model classifies everything else, with a calibrated confidence.
3. Policy decides per (category, purpose). Confident -> act alone. Unsure -> ask the human,
   and the region stays blurred until they answer (fail closed).
"""

from __future__ import annotations

import io
import os
import re
import json
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .detectors import detect_injection, detect_leaks
from .policy import Policy
from .schemas import GATE, Decision, GateResult, Region

MONEY = re.compile(r"[$€£]\s?\d[\d,]*(\.\d{2})?")  # an amount on screen is about someone's money, whatever the model says
CONTEXT = os.environ.get("GATE_CONTEXT", "0") == "1"  # measured worse on fixtures 22.10 (biopsy line -> ask, address -> allow); judge a line together with the screen title and its neighbours
RULE_CATEGORY = {"email": "contact_info", "phone": "contact_info", "us-ssn": "contact_info",
                 "credit-card": "financial"}


def ocr(image: bytes) -> list[Region]:
    """Apple Vision on device via the `visionscan` helper that ships with ScreenShield."""
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        f.write(image)
        f.flush()
        out = subprocess.run(["visionscan", f.name], capture_output=True, text=True, check=True).stdout
    d = json.loads(out.splitlines()[0])
    return [Region(t["text"], (t["box"]["x"], t["box"]["y"], t["box"]["w"], t["box"]["h"]))
            for t in d.get("texts", []) if t["text"].strip()]


def decide(regions: list[Region], purpose: str, policy: Policy, judge) -> GateResult:
    t0 = time.perf_counter()
    res = GateResult(purpose)
    for i, r in enumerate(regions):
        hits = detect_leaks(r.text) + detect_injection(r.text)
        if hits:
            h = max(hits, key=lambda f: f.severity == "critical")
            cat = "injection" if h.kind == "injection" else RULE_CATEGORY.get(h.rule, "credentials")
            if cat == "injection" or not policy.allows(cat, purpose):
                res.decisions.append(Decision(r.text, r.box, cat, 1.0, "redact", f"{h.rule}: {h.reason}", "detector"))
                continue
        if MONEY.search(r.text):
            act = "allow" if policy.allows("financial", purpose) else "redact"
            res.decisions.append(Decision(r.text, r.box, "financial", 1.0, act, "amount of money on screen", "detector"))
            continue
        if len(r.text.strip()) < 3:
            res.decisions.append(Decision(r.text, r.box, "public", 1.0, "allow", "too short to mean anything", "detector"))
            continue
        near = [regions[0].text] + [x.text for x in regions[max(1, i - 1):i + 2] if x is not r]
        cat, conf, ms = judge.classify(r.text, " | ".join(dict.fromkeys(near)) if CONTEXT else "")
        allowed = policy.allows(cat, purpose)
        if conf < GATE:
            action, why = "ask", f"model unsure ({conf:.2f} < {GATE}), held until you decide"
        elif allowed:
            action, why = "allow", f"you allowed {cat} for {purpose}"
        else:
            action, why = "redact", f"no consent for {cat} → {purpose}"
        res.decisions.append(Decision(r.text, r.box, cat, round(conf, 3), action, why, "model", round(ms, 1)))
    res.ms = (time.perf_counter() - t0) * 1000
    return res


def redact(image: bytes, res: GateResult) -> bytes:
    """Blur everything that is not explicitly allowed. 'ask' is blurred too: fail closed."""
    img = Image.open(io.BytesIO(image)).convert("RGB")
    draw = ImageDraw.Draw(img)
    for d in res.decisions:
        if d.action == "allow":
            continue
        x, y, w, h = (int(v) for v in d.box)
        box = (max(0, x - 4), max(0, y - 4), min(img.width, x + w + 4), min(img.height, y + h + 4))
        img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
        draw.rectangle(box, outline=(255, 80, 80) if d.action == "redact" else (255, 190, 0), width=2)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def ledger(path: Path, res: GateResult, frame: str) -> dict:
    """Consent record: what was decided, by whom, under which purpose. Text itself is not stored."""
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "frame": frame,
             "purpose": res.purpose, "counts": res.counts, "ms": round(res.ms),
             "decisions": [{"category": d.category, "action": d.action, "confidence": d.confidence,
                            "source": d.source} for d in res.decisions if d.category != "public"]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry
