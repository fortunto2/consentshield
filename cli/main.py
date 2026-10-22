"""CLI mirror of the gate: `uv run python -m cli.main fixtures/env-demo.png --purpose assistant`."""

from __future__ import annotations

import argparse
from pathlib import Path

from consent.gate import decide, ledger, ocr, redact
from consent.judge import Judge
from consent.policy import Policy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--purpose", default="assistant")
    ap.add_argument("--out", type=Path, default=Path("data/out"))
    a = ap.parse_args()
    judge, policy = Judge(), Policy(Path("data/policy.json"))
    a.out.mkdir(parents=True, exist_ok=True)
    for p in a.images:
        raw = p.read_bytes()
        res = decide(ocr(raw), a.purpose, policy, judge)
        (a.out / p.name).write_bytes(redact(raw, res))
        ledger(Path("data/ledger.jsonl"), res, p.name)
        print(f"\n{p.name}  purpose={a.purpose}  {res.counts}  {res.ms:.0f} ms")
        for d in res.decisions:
            print(f"  {d.action:6} {d.category:15} {d.confidence:.2f} {d.source:8} {d.text[:60]}")


if __name__ == "__main__":
    main()
