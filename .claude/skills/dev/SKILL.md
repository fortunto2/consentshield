---
name: consentshield-dev
description: Dev workflow for ConsentShield (consent gate for screen-watching agents) — run the demo, test, extend the gate. Use when working in this repo. Do NOT use for other projects.
---

# ConsentShield dev

Read first: `docs/CONTEXT.md` (event, judges, pitch, status), `docs/ROADMAP.md` (what next), `CLAUDE.md` (map).

- Run: `make run` → http://localhost:8790 (server loads Laya once, ~10 s). Restart after Python edits.
- CLI: `make demo` prints every decision for every fixture. Use it to check a change before the UI.
- Tests: `make test` (no model). Add a test for any new detector or policy rule.
- New category or purpose: edit `consent/schemas.py`, then the defaults in `consent/policy.py`; delete `data/policy.json`.
- New deterministic rule: `consent/gate.py` (before the model). Detectors win over the model, always.
- Fixtures are synthetic (`bin/make_fixtures.py`); never commit real personal screenshots.
- The ledger never stores text. Keep it that way.
