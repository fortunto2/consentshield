---
name: consentshield
description: Give an agent screen access through the user's consent gate instead of raw screenshots. Use when setting up ConsentShield as an MCP server for Claude Code, Claude Desktop, Cursor or any MCP client, when an agent needs a `screenshot` tool that respects consent per purpose, or when a gated frame comes back wrong (black capture, everything blurred, first call slow). Do NOT use for extending the gate itself (that is the `dev` skill in this repo).
---

# ConsentShield over MCP

One idea: the agent never gets the raw screen. It calls `screenshot(purpose)`, the gate runs on the
Mac (OCR → detectors → local decision model → the user's consent matrix), and the agent receives the
redacted PNG plus a list of what was held back and why. Zero bytes leave before the decision; the
consent ledger records category and outcome, never the text.

## Install (macOS, Apple silicon, ~3 minutes)

```bash
brew tap fortunto2/tap && brew install screenshield   # ships `visionscan`, the on-device OCR helper
git clone https://github.com/fortunto2/consentshield && cd consentshield
uv sync                                               # Python 3.12, torch 2.7, laya, mcp
make demo                                             # sanity check: gates the synthetic fixtures from the CLI
```

The first run downloads the Laya model (~1 GB) into the Hugging Face cache. Python 3.13 does not work:
torch 2.7 has no wheels for it, `uv sync` pins 3.12.

## Register the server

Pick one. All of them launch the same command: `uv run --directory <repo> python -m app.mcp_server`.

| Client | How |
|---|---|
| Claude Code, from any directory | `make install-mcp` (runs `claude mcp add consentshield -s user -- …` with the repo's absolute path) |
| Claude Code, inside the repo only | nothing to do: `.mcp.json` is in the repo, Claude Code asks once to trust it |
| Claude Desktop | add the block below to `~/Library/Application Support/Claude/claude_desktop_config.json`, restart Claude |
| Cursor / other MCP clients | same block in their MCP settings; transport is stdio |

```json
{
  "mcpServers": {
    "consentshield": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/consentshield", "python", "-m", "app.mcp_server"]
    }
  }
}
```

Check: `claude mcp list` shows `consentshield`, and in a session `/mcp` lists tools `screenshot` and `consent_policy`.

## Grant Screen Recording once

`screencapture` runs inside the MCP server, which is a child of the client app. macOS asks the **client**
for permission, not the terminal you installed from: System Settings → Privacy & Security → Screen
Recording → enable Claude (Desktop) or the terminal/IDE that runs Claude Code. Without it the capture is
black or empty and the gate reports 0 text regions. Grant, then restart the client.

## Tools

`screenshot(purpose="assistant", path=None)`
- `purpose`: why the agent needs the screen. `assistant` (help the user right now, nothing stored),
  `analytics`, `training`, `third_party`. Different purpose, different frame: the defaults let work and
  public content through for assistant/analytics/third party, almost nothing for training.
- `path`: gate an existing image instead of the live screen. Use it in demos and tests
  (`fixtures/chat-personal.png` and friends are synthetic).
- Returns two content items: a text summary (`N sent, M blurred, K waiting for the user`, then one line
  per held region with category, source, confidence, reason) and the redacted PNG.

`consent_policy()` → the consent matrix as JSON: `rules[category][purpose] = true|false`, the locked
categories (`credentials`, never overridable) and the purpose descriptions.

Categories: credentials, financial, health, private_message, contact_info, work, public, plus
`injection` for lines like "ignore previous instructions", which are always removed before the agent sees them.

## How "waiting for the user" works

The local model acts alone only at confidence ≥ 0.8. Below that the region stays blurred and shows up
as `ask` in the summary. The agent cannot resolve an ask; the user does, in the web console:

```bash
make run        # http://localhost:8790
```

Pick the same screen there (or Share my screen), answer `Send it as <category>` / `Keep private`. The
answer decides that line, flips the consent matrix for that purpose, and lands in the ledger with
`source=user`. The MCP server re-reads `data/policy.json` on every call, so the agent's next
`screenshot` reflects it. Agent-side guidance: when a result says regions are waiting, tell the user
which categories and ask them to decide in the console, then call `screenshot` again. Do not retry in a loop.

## What the agent should expect

- First call in a session: ~10 s (model load) + ~1.5 s (warm-up). Later frames 0.15–0.7 s on an M-series Mac.
- Short chat lines are often `ask`; that is the design (fail closed), not a bug.
- Detectors beat the model and the user: keys, card numbers, amounts, connection strings with passwords
  and injection lines are blurred whatever the consent matrix says.
- Ledger: `data/ledger.jsonl`, one JSON per frame (timestamp, frame hash, purpose, counts, per-region
  category/action/confidence/source). Grep it to answer "what did the agent get today".

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| `visionscan: command not found` | brew tap not installed → `brew tap fortunto2/tap && brew install screenshield` |
| capture is black, 0 regions | Screen Recording not granted to the client app (see above) |
| `No module named mcp` or `mcp.server.fastmcp` | `uv sync` not run, or mcp 1.x; the server uses mcp ≥ 2 (`MCPServer`) |
| first call times out in the client | model download on first run; run `make demo` once outside the client |
| everything blurred under `training` | expected: only `public` is allowed for training by default |
| `MPS Autocast only supports…` warning on stderr | harmless torch warning on Apple silicon |
| an answer in the console does not reach the agent | console and server must share the repo's `data/`; both read `data/policy.json` |

## Files

- `app/mcp_server.py` — the server (two tools, re-reads policy per call, shared ledger).
- `.mcp.json` — project-scope registration for Claude Code.
- `consent/gate.py` — the pipeline the tool calls; `consent/policy.py` — defaults and the lock on credentials.
- `docs/mcp-transcript.md` — what Claude Code actually received on the personal-chat sample.
