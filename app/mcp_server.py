"""MCP adapter: any agent that can call tools gets the gated screen, never the raw one.

    claude mcp add consentshield -- uv run --directory <this repo> python -m app.mcp_server

The agent calls `screenshot(purpose)`; the gate runs on this Mac, the agent receives the redacted
frame plus the list of what was held back and why. The raw pixels never enter the agent's context.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from mcp.server.mcpserver import Image, MCPServer

from consent.gate import DATA, gate_frame
from consent.judge import Judge
from consent.policy import Policy
from consent.schemas import PURPOSES

mcp = MCPServer("ConsentShield", instructions="Screen access goes through the user's consent gate. "
                "Call `screenshot` with the purpose you need the screen for; you receive only what the user allowed.")
policy = Policy(DATA / "policy.json")  # re-reads the file when the web console changes it
_judge: Judge | None = None
_lock = threading.Lock()


def judge() -> Judge:
    """Loaded once (~15 s). Started in the background at launch so the agent's first call does not pay for it."""
    global _judge
    with _lock:
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
    res, entry, png = gate_frame(raw, purpose, policy, judge())
    held = [f"- {d.action} {d.category} ({d.source}, {d.confidence:.2f}): {d.reason}"
            for d in res.decisions if d.action != "allow"]
    summary = (f"Gated on device for purpose={purpose}: {res.counts['allow']} regions sent, "
               f"{res.counts['redact']} blurred, {res.counts['ask']} waiting for the user, {res.ms:.0f} ms. "
               f"Ledger entry {entry['ts']}.\n" + ("Held back:\n" + "\n".join(held) if held else "Nothing held back."))
    return [summary, Image(data=png, format="png")]


@mcp.tool()
def consent_policy() -> str:
    """The user's consent matrix: which data categories may leave the device for which purpose.
    Credentials are locked and never leave."""
    return json.dumps(policy.to_dict(), indent=2)


if __name__ == "__main__":
    threading.Thread(target=judge, daemon=True).start()
    mcp.run()
