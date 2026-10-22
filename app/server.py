"""Web demo: the browser shares a screen frame, the gate returns what the cloud agent would see."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse

from consent.gate import decide, ledger, ocr, redact
from consent.judge import Judge
from consent.policy import LOCKED, Policy
from consent.schemas import CATEGORIES, GATE, PURPOSES

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
app = FastAPI(title="ConsentShield")
judge = Judge()
policy = Policy(DATA / "policy.json")


@app.get("/")
def index():
    return FileResponse(ROOT / "app" / "index.html")


@app.get("/qr.png")
def qr():
    return FileResponse(ROOT / "app" / "qr.png")


@app.get("/fixtures/{name}")
def fixture(name: str):
    return FileResponse(ROOT / "fixtures" / Path(name).name)


@app.get("/policy")
def get_policy():
    return {"rules": policy.rules, "categories": CATEGORIES, "purposes": PURPOSES, "locked": sorted(LOCKED),
            "gate": GATE}


@app.post("/policy")
def set_policy(category: str = Form(...), purpose: str = Form(...), allowed: bool = Form(...)):
    policy.set(category, purpose, allowed)
    return get_policy()


@app.post("/gate")
async def gate(frame: UploadFile = File(...), purpose: str = Form("assistant"), decisions: str = Form("{}")):
    """`decisions` is JSON {line text: "allow"|"redact"}: what the human already answered for this purpose."""
    raw = await frame.read()
    res = decide(ocr(raw), purpose, policy, judge, user=json.loads(decisions))
    entry = ledger(DATA / "ledger.jsonl", res, hashlib.sha1(raw).hexdigest()[:10])
    return {**res.to_dict(), "ledger": entry,
            "agent_sees": "data:image/png;base64," + base64.b64encode(redact(raw, res)).decode()}


@app.get("/ledger")
def get_ledger(limit: int = 30):
    p = DATA / "ledger.jsonl"
    rows = [json.loads(x) for x in p.read_text().splitlines()[-limit:]] if p.exists() else []
    return list(reversed(rows))
