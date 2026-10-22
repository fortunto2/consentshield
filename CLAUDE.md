# ConsentShield — CLAUDE.md

Consent gate between a screen-watching personal agent and the cloud. Hackathon build (super{set}, 22.10.2026).

- `consent/schemas.py` — domain: categories, purposes, Decision, GATE=0.8
- `consent/detectors.py` — deterministic secrets/PII/injection (copied from ScreenShield, keep in sync by hand)
- `consent/judge.py` — Laya local decision model (choice over CATEGORIES)
- `consent/policy.py` — consent matrix, credentials locked; `data/policy.json`
- `consent/gate.py` — ocr → detectors → model → policy → redact → ledger
- `app/server.py` + `app/index.html` — web demo :8790; `cli/main.py` — CLI mirror

Commands: `make run`, `make demo`, `make test`. Python 3.12 (torch 2.7 has no 3.13 wheels for laya).

Don't: store frame text in the ledger; let a toggle release credentials; send anything before the decision.
Fixtures are synthetic; never add real personal screenshots.

## Next session
Start with `docs/CONTEXT.md` and `docs/ROADMAP.md`. Deadline today 17:00 PT. The web demo may already be running on :8790
(`lsof -i :8790`). Skills: `.claude/skills/dev/SKILL.md` (extend the gate), `.claude/skills/consentshield/SKILL.md` (install and use over MCP).
