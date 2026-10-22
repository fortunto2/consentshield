# Roadmap

## Before 17:00 today (in order, stop when time is up)
- [x] Rehearsed the demo path in the browser (22.10 14:35): samples, answer an ask, switch purpose, pitch deck.
- [ ] Before going on stage: `make reset` (= `rm -rf data`; servers re-read the policy file, reload the browser tab).
- [x] Pitch deck inside the page (🎤 Pitch), 5 slides, QR to the repo.
- [x] Context window tried (GATE_CONTEXT=1): worse on fixtures, biopsy line went to ask and an address to allow. Off by default.
- [x] A human's answer decides the line (was: policy flipped but the line stayed "ask"). source=user in the ledger.
- [x] MCP server (`app/mcp_server.py`, `.mcp.json`): `screenshot(purpose)` returns the gated frame to any MCP client.
- [x] Submission text: `docs/SUBMISSION.md`.
- [x] Redesigned console: queue of asks on top, purpose tabs on the agent pane, hover a row → box on both screens, confidence bars. Design preview also in a Claude artifact.
- [ ] "Per-agent" purposes: two agents getting different frames side by side (dropped for MCP).
- [ ] Optional: Jev (TypeSafe API) as a second judge for comparison, clearly labelled as cloud.
- [ ] Submit the form: repo link + paragraph from docs/SUBMISSION.md + docs/demo.png.

## After the hackathon
- Live mode: continuous capture with change detection (port ScreenShield's luma-grid diff) instead of single frames.
- Line-level answers live in the browser tab (`U[purpose][text]`); move them into Policy (hashed text, next to policy.json)
  so MCP and CLI see them too and they survive a reload. Then offer "this line" vs "all <category> for <purpose>" as two buttons.
- MCP: add `ask` resolution over MCP elicitation, so the agent itself can route the question to the user.
- Consent receipts export (JSON, signed) for audits; per-agent identities.
- Core ML Laya build (13.7 ms/question measured) instead of torch; ship as one macOS binary.
- Learn from answers: user decisions become labelled data to calibrate the local model.
