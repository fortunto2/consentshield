"""MCP adapter: any agent that can call tools gets the gated screen, never the raw one.

    claude mcp add consentshield -- uv run --directory <this repo> python -m app.mcp_server

The agent calls `screenshot(purpose)`; the gate runs on this Mac, the agent receives the redacted
frame plus the list of what was held back and why. The raw pixels never enter the agent's context.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp.server.mcpserver import Image, MCPServer

from consent.gate import decide, ledger, ocr, redact
from consent.judge import Judge
from consent.policy import LOCKED, Policy
from consent.schemas import PURPOSES

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
mcp = MCPServer("ConsentShield", instructions="Screen access goes through the user's consent gate. "
              "Call `screenshot` with the purpose you need the screen for; you receive only what the user allowed.")
_judge: Judge | None = None
policy = lambda: Policy(DATA / "policy.json")  # re-read per call: the user answers in the web UI, the agent sees it next frame


def judge() -> Judge:
    global _judge
    if _judge is None:
        print("loading the local decision model…", file=sys.stderr)
        _judge = Judge()
    return _judge


def capture() -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        subprocess.run(["screencapture", "-x", "-t", "png", f.name], check=True)
        return Path(f.name).read_bytes()


@mcp.tool()
def screenshot(purpose: str = "assistant", path: str | None = None) -> list:
    """Take a screenshot the user has consented to. `purpose` is why you need it: assistant (help the
    user right now), analytics, training or third_party. Regions the user did not allow for that purpose
    come back blurred; regions the local model was unsure about are blurred too and wait for the user.
    `path` gates an existing image instead of the live screen (demos, tests)."""
    if purpose not in PURPOSES:
        raise ValueError(f"purpose must be one of {sorted(PURPOSES)}")
    raw = Path(path).read_bytes() if path else capture()
    res = decide(ocr(raw), purpose, policy(), judge())
    entry = ledger(DATA / "ledger.jsonl", res, hashlib.sha1(raw).hexdigest()[:10])
    held = [f"- {d.action} {d.category} ({d.source}, {d.confidence:.2f}): {d.reason}"
            for d in res.decisions if d.action != "allow"]
    summary = (f"Gated on device for purpose={purpose}: {res.counts['allow']} regions sent, "
               f"{res.counts['redact']} blurred, {res.counts['ask']} waiting for the user, {res.ms:.0f} ms. "
               f"Ledger entry {entry['ts']}.\n" + ("Held back:\n" + "\n".join(held) if held else "Nothing held back."))
    return [summary, Image(data=redact(raw, res), format="png")]


@mcp.tool()
def consent_policy() -> str:
    """The user's consent matrix: which data categories may leave the device for which purpose.
    Credentials are locked and never leave."""
    return json.dumps({"rules": policy().rules, "locked": sorted(LOCKED), "purposes": PURPOSES}, indent=2)


if __name__ == "__main__":
    os.chdir(ROOT)
    mcp.run()
