"""CLI mirror of the gate: `uv run python -m cli.main fixtures/env-demo.png --purpose assistant`."""

from __future__ import annotations

import argparse
from pathlib import Path

from consent.gate import DATA, gate_frame
from consent.judge import Judge
from consent.policy import Policy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--purpose", default="assistant")
    ap.add_argument("--out", type=Path, default=DATA / "out")
    a = ap.parse_args()
    judge, policy = Judge(), Policy(DATA / "policy.json")
    a.out.mkdir(parents=True, exist_ok=True)
    for p in a.images:
        res, _, png = gate_frame(p.read_bytes(), a.purpose, policy, judge, frame=p.name)
        (a.out / p.name).write_bytes(png)
        print(f"\n{p.name}  purpose={a.purpose}  {res.counts}  {res.ms:.0f} ms")
        for d in res.decisions:
            print(f"  {d.action:6} {d.category:15} {d.confidence:.2f} {d.source:8} {d.text[:60]}")


if __name__ == "__main__":
    main()
