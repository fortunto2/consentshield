# 🛡️ ConsentShield

**Your agent watches your screen. Your consent decides what leaves it.**

**Demo:** [fortunto2.github.io/consentshield](https://fortunto2.github.io/consentshield/) (recorded results from the
real gate, consent matrix live in the page) · the live gate runs on your Mac, see Run below.

![ConsentShield: your screen on the left, what the cloud agent receives on the right](docs/demo.png)

Personal agents now see the screen: computer-use agents, "remember everything" assistants, Claude
through MCP. Every screenshot they send to the cloud carries whatever was open: a chat about a
biopsy, a bank balance, an `.env` file. Consent today is a cookie banner on a website. Nothing asks
at the moment an agent actually takes your data.

ConsentShield sits between the screen and the agent, on the device:

```
screen frame ─► OCR on device (Apple Vision)
             ─► detectors first: secrets, card numbers, money, prompt injection   (deterministic)
             ─► local decision model (Laya, open Jev): data category + calibrated confidence
             ─► your consent per (category × purpose): assistant · analytics · training · third party
             ─► confident (≥ 0.8) → act alone: send or blur · unsure → hold it blurred and ask you
             ─► the cloud agent gets the redacted frame · a consent ledger records every decision
```

Nothing leaves the Mac before the decision. The ledger stores categories and outcomes, never the text.

Built at the **super{set} national renaissance hackathon**, San Francisco, 22 Oct 2026,
track *Personal agents and data privacy*.

## Why this shape

- **Consent at the moment of action.** Purposes (assistant / analytics / training / third party) are
  the model privacy platforms like Ketch use for websites; here they are enforced per frame, per agent.
- **Detectors before models.** A key or a card number is blurred by a regex no model can talk out of it.
  Credentials are locked: no consent toggle can release them.
- **Calibrated, local decisions.** [Laya](https://huggingface.co/convaiinnovations/laya) (Apache 2.0
  reproduction of TypeSafe's Jev) answers a typed question with a probability in ~30 ms on Apple
  silicon. Act alone at ≥ 0.8, otherwise ask, the rule from Vivek Haldar's
  [decision models in agent harnesses](https://vivekhaldar.com/articles/llms-do-too-much-offload-to-decision-models/).
- **Fail closed.** An "ask" stays blurred until you answer. Your answer decides that line and becomes
  policy for the purpose; the ledger records it as a human decision.

## Models, all local
- **OCR: Apple Vision** through `visionscan`, a small Swift helper. It runs on the Mac's own hardware and returns text lines with boxes.
- **Decisions: Laya multilingual** (convaiinnovations, Apache 2.0). It is an open reproduction of TypeSafe's Jev: mmBERT-base, 322M parameters, about 650 MB. It does not generate text. Each typed question gets one forward pass that returns a probability distribution and a confidence, about 30 ms per line on MPS here.
- **Measured before this hackathon** on an M5: 10 of 12 on our EN+RU smoke set (both misses in Russian). ONNX int8 brings it to 325 MB, Core ML fp16 runs at 13.7 ms per question on the GPU, and the Neural Engine refuses it. Hosted Jev takes 70–500 ms per call, so local is 5–35x faster, and no frame has to leave the machine to be judged.
- **No LLM anywhere in the gate.** An LLM can be the agent behind the gate. It never decides what the agent is allowed to see.

## Built before vs. today
**Before:**
- [ScreenShield](https://github.com/fortunto2/screenshield) (9 Oct): DLP for video, a Rust binary that blurs secrets in a live stream with a 1 s delay. We reuse its OCR helper and secret, PII and injection detectors.
- The Laya port to ONNX and Core ML, with measurements.
- BroCheck (yesterday): Jev on images in one call.

**Today:**
- The consent layer: categories × purposes, a policy with locked credentials, the gate (detectors → model → policy, fail closed), and the money detector.
- The ledger, plus a web demo with screen sharing, purpose switching and one-click answers that become policy.
- Synthetic personal screens, the CLI and tests, and the measurement that showed context makes the model worse.

## Run (macOS, Apple silicon)

```bash
brew tap fortunto2/tap && brew install screenshield   # ships the visionscan OCR helper
uv sync
make run        # http://localhost:8790 , Share screen or click a sample
make demo       # same gate from the CLI over fixtures/
```

Samples in `fixtures/` are synthetic: every name, number and diagnosis is invented.

## Plug it into a real agent (MCP)

The same gate is an MCP server. The agent calls `screenshot(purpose)` and receives the redacted frame
plus a list of what was held back and why; the raw pixels never enter its context. Answers you give in
the web UI apply to the agent's next frame, and both write the same consent ledger.

```bash
claude mcp add consentshield -- uv run --directory "$PWD" python -m app.mcp_server   # Claude Code
make mcp                                                                             # or any MCP client over stdio
```

`make install-mcp` registers it for every directory (user scope). This repo also ships `.mcp.json`, so Claude Code started inside it already has the tool.
Full setup, Screen Recording permission, tool contract and troubleshooting: [.claude/skills/consentshield/SKILL.md](.claude/skills/consentshield/SKILL.md). Claude Desktop takes
the same command in `claude_desktop_config.json`. Tools: `screenshot(purpose, path=None)` and `consent_policy()`.

Tried for real: Claude Code called the tool on the personal-chat sample and reported *"I can read only one
line: the sprint planning doc. The other 6 regions are blurred. No raw personal data reached me."*
Full transcript in [docs/mcp-transcript.md](docs/mcp-transcript.md).

## Measured on the samples (M-series Mac, purpose = assistant)

| Screen | regions | sent | blurred | asked | time |
|---|---|---|---|---|---|
| personal chat | 7 | 2 | 2 | 3 | 1.4 s (first frame, warm-up) |
| bank dashboard | 7 | 1 | 5 | 1 | 0.16 s |
| work inbox with injection | 6 | 2 | 2 | 2 | 0.32 s |

Honest limits: Laya is small and often unsure on short chat lines, which is exactly why those go to
the human instead of silently through. OCR boxes are per line, not per word.

## Team

Rustam Salavatov ([fortunto2](https://github.com/fortunto2)). Reuses the OCR and detectors of
[ScreenShield](https://github.com/fortunto2/screenshield) (3rd place, Cyberdefense Hackathon, SF, 9 Oct 2026).

MIT.
