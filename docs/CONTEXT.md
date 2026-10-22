# Context for the next session

## The event
- **super{set} national renaissance hackathon**, San Francisco, Thu 22 Oct 2026 (luma.com/superset-hy5n).
- Schedule: hack 10:30–17:00 · **17:00 projects due** · 17:00–18:00 demos · 18:30 winners · networking to 19:00.
- Prizes per track: 1st $1.5K, 2nd $1K, plus a desk at super{set} for a month and an interview at s{s} or a portfolio company.
- Tracks: (1) public data APIs/datasets; (2) **personal agents and data privacy, user consent** ← we are here.

## Who judges and what they want
- super{set} is a startup studio (Tom Chavez, Vivek Vaidya; Krux → Salesforce, Rapt → Microsoft). Portfolio:
  **Ketch** (privacy and consent management), Habu (data clean rooms, sold to LiveRamp), Checksum, Kapstan, Boombox.
- Track 2 is Ketch's home turf. Speak their language: *purposes*, consent records, enforcement, auditability.
- "Renaissance engineer" = tech + user need + business + system impact. The demo must show all four, not just code.

## The pitch in one line
Ketch for the agent era: consent is checked at the moment an agent acts, not in a cookie banner,
and nothing leaves the device before the decision.

## Pitch beats (2–3 min)
1. Problem: agents now see the screen (computer use, recall-style assistants, MCP). Every screenshot = whatever was open.
2. Live: click "chat-personal" → biopsy line, money, address blurred on the right; the work line goes through.
3. Switch purpose to "training" → almost everything blurs. Same screen, different purpose, different answer.
4. Click "allow private message" on an ask → policy changes, ledger records it. The human stays in the loop only where the model is unsure.
5. Agent inbox: the "ignore previous instructions" line never reaches the agent (inbound protection too).
6. Business: SDK/sidecar for agent vendors + consent ledger for compliance (GDPR/CCPA/EU AI Act); a natural Ketch extension.

## What exists (verified 22.10 ~14:15)
- Gate works end to end: OCR (Apple Vision via `visionscan`) → detectors → Laya → policy → blur → ledger.
- Web demo `make run` → http://localhost:8790, 4 synthetic fixtures, screen share via getDisplayMedia.
- CLI `make demo`, tests `make test` (3 pass, no model needed).
- Numbers on fixtures in README.

- Pitch: button 🎤 Pitch in the page header, 5 slides, arrows/click, QR to the repo on the last slide.
- MCP server (`app/mcp_server.py`, `.mcp.json`): Claude Code inside the repo gets `screenshot(purpose)` and receives
  only the gated frame; transcript of a real run in docs/mcp-transcript.md. Answers in the web UI apply to the agent's next frame.
- Console redesigned 14:35: asks queue on top, purpose tabs on the agent pane, hover a row → box on both screens.
- Before stage: `make reset` (kills :8790, deletes data/, starts clean). Submission paragraph: docs/SUBMISSION.md.

## Known weak spots
- Laya is unsure on short chat lines (0.2–0.4) → many "ask". Frame it as the feature (fail closed + human in loop).
- First frame is slow (~1.4 s, warm-up); later frames 0.15–0.4 s.
- Per-line OCR boxes; a chat bubble split across lines is judged line by line, without context.
