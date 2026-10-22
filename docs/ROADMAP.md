# Roadmap

## Before 17:00 today (in order, stop when time is up)
- [ ] Rehearse the demo path from docs/CONTEXT.md; reset `data/` before going on stage (`rm -rf data`).
- [ ] Pitch tab or 4-slide deck inside the page (problem · live demo · how · business), big QR to the repo.
- [ ] Context window: classify each line with its neighbours (prev + next line) to cut the "ask" rate on chats.
- [ ] "Per-agent" purposes: show two agents (assistant vs analytics SDK) getting different frames side by side.
- [ ] Optional: Jev (TypeSafe API) as a second judge for comparison, clearly labelled as cloud.
- [ ] Submit: repo link + 1-paragraph description + screenshot.

## After the hackathon
- Live mode: continuous capture with change detection (port ScreenShield's luma-grid diff) instead of single frames.
- MCP proxy: sit in front of screenshot tools of computer-use agents, so any agent gets the gated frame.
- Consent receipts export (JSON, signed) for audits; per-agent identities.
- Core ML Laya build (13.7 ms/question measured) instead of torch; ship as one macOS binary.
- Learn from answers: user decisions become labelled data to calibrate the local model.
