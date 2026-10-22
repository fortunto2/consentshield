# What a real agent received through the MCP gate

Recorded 22 Oct 2026 14:57 PT. Claude Code, started inside this repo (so `.mcp.json` is loaded),
non-interactive, with only the `mcp__consentshield__screenshot` tool allowed.

Prompt:

> Use the mcp__consentshield__screenshot tool with purpose=assistant and path=fixtures/chat-personal.png.
> Then answer in 3 short lines: (1) what text you can read in the image you received, (2) what was held
> back, (3) whether any raw personal data reached you.

Answer (translated from Russian, the agent's configured language):

> 1. I can read only one line: "Me: the new sprint planning doc is in the team drive". The other 6 regions are blurred.
> 2. Held back: 3 regions redacted (health at 0.96 without consent, a contact with a phone number and a money
>    amount by detector), 3 waiting for the user's decision (private_message ×2 and work, model unsure, < 0.8).
> 3. No: no raw personal data reached me, only blurred blocks and category labels without content.

3 turns, one tool call. The tool result the agent saw was the summary text from `app/mcp_server.py`
plus the redacted PNG; the original frame never entered its context. The same call is in the consent
ledger (`data/ledger.jsonl`) as `purpose=assistant · sent 1 · blurred 3 · asked 3`.

Reproduce:

```bash
claude -p "Use the mcp__consentshield__screenshot tool with purpose=assistant and path=$PWD/fixtures/chat-personal.png. What can you read?" \
  --mcp-config .mcp.json --strict-mcp-config --allowedTools mcp__consentshield__screenshot
```
