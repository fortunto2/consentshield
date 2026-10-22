"""Web demo: the browser shares a screen frame, the gate returns what the cloud agent would see."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse

from consent.gate import DATA, gate_frame
from consent.judge import Judge
from consent.policy import Policy

ROOT = Path(__file__).resolve().parent.parent
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
    return policy.to_dict()


@app.post("/policy")
def set_policy(category: str = Form(...), purpose: str = Form(...), allowed: bool = Form(...)):
    policy.set(category, purpose, allowed)
    return policy.to_dict()


@app.post("/gate")
async def gate(frame: UploadFile = File(...), purpose: str = Form("assistant"), decisions: str = Form("{}")):  # noqa: B008
    """`decisions` is JSON {line text: "allow"|"redact"}: what the human already answered for this purpose."""
    raw = await frame.read()
    res, entry, png = gate_frame(raw, purpose, policy, judge, user=json.loads(decisions))
    return {**res.to_dict(), "ledger": entry, "agent_sees": "data:image/png;base64," + base64.b64encode(png).decode()}


@app.get("/ledger")
def get_ledger(limit: int = 30):
    p = DATA / "ledger.jsonl"
    rows = [json.loads(x) for x in p.read_text().splitlines()[-limit:]] if p.exists() else []
    return list(reversed(rows))
