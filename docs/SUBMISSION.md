# Submission (super{set} national renaissance hackathon, 22 Oct 2026, track: personal agents and data privacy)

**Project:** ConsentShield
**Repo:** https://github.com/fortunto2/consentshield
**Demo (always up, recorded gate results):** https://fortunto2.github.io/consentshield/
**Screenshot:** docs/demo.png
**Team:** Rustam Salavatov (fortunto2)

## One paragraph

ConsentShield is a consent gate between a screen-watching personal agent and the cloud, running entirely
on the Mac. Every frame is OCR'd on device (Apple Vision), checked by deterministic detectors for secrets,
card numbers, money and prompt injection, then classified by a small local decision model (Laya, the open
reproduction of TypeSafe's Jev) into a data category with a calibrated confidence. The user's consent is
stored Ketch-style per purpose (assistant, analytics, training, third party) and enforced at the moment
the agent acts: at confidence ≥ 0.8 the gate sends or blurs on its own, below that it keeps the region
blurred and asks the user, whose answer becomes policy. Credentials are locked and can never be released
by a toggle; the "ignore previous instructions" line in an inbox never reaches the agent. Zero bytes leave
the device before the decision, and a consent ledger records category, purpose and outcome for every
frame, never the text. Measured on synthetic screens: 0.15–0.4 s per frame after warm-up, all keys,
cards, amounts and injections blurred, the unsure chat lines sent to the human instead of the cloud.

## Short version (if the form has a limit)

A consent gate between your screen-watching agent and the cloud, on device. OCR + detectors + a local
calibrated decision model classify every line; your Ketch-style consent per purpose (assistant / analytics /
training / 3rd party) is enforced per frame. Confident → send or blur alone; unsure → hold blurred and ask you.
Credentials never leave. A ledger records every decision without the text. 0 bytes leave before the decision.
