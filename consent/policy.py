"""User consent per (category, purpose). Ketch-style purposes, enforced at the moment the agent acts."""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import CATEGORIES, GATE, PURPOSES

# Defaults: the assistant may see ordinary work and public content; nothing personal leaves for
# analytics, training or third parties. Credentials never leave, whatever the user clicked.
DEFAULT: dict[str, dict[str, bool]] = {
    "credentials": {p: False for p in PURPOSES},
    "financial": {"assistant": False, "analytics": False, "training": False, "third_party": False},
    "health": {"assistant": False, "analytics": False, "training": False, "third_party": False},
    "private_message": {"assistant": False, "analytics": False, "training": False, "third_party": False},
    "contact_info": {"assistant": False, "analytics": False, "training": False, "third_party": False},
    "work": {"assistant": True, "analytics": True, "training": False, "third_party": True},
    "public": {p: True for p in PURPOSES},
}
LOCKED = {"credentials"}  # never overridable


class Policy:
    """Consent matrix backed by one JSON file. Re-reads it when the file changes or disappears, so the web
    server, the MCP server and `rm -rf data` agree without restarts."""

    def __init__(self, path: Path):
        self.path = path
        self._mtime: float | None = -1.0
        self._rules: dict[str, dict[str, bool]] = {}

    @property
    def rules(self) -> dict[str, dict[str, bool]]:
        mtime = self.path.stat().st_mtime if self.path.exists() else None
        if mtime != self._mtime:
            self._rules = json.loads(self.path.read_text()) if mtime is not None else json.loads(json.dumps(DEFAULT))
            self._mtime = mtime
        return self._rules

    def allows(self, category: str, purpose: str) -> bool:
        return bool(self.rules.get(category, {}).get(purpose, False))

    def to_dict(self) -> dict:
        return {"rules": self.rules, "categories": CATEGORIES, "purposes": PURPOSES, "locked": sorted(LOCKED), "gate": GATE}

    def set(self, category: str, purpose: str, allowed: bool) -> None:
        if category in LOCKED or category not in CATEGORIES or purpose not in PURPOSES:
            raise ValueError(f"cannot change {category}/{purpose}")
        rules = self.rules
        rules.setdefault(category, {})[purpose] = allowed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(rules, indent=2))
        self._mtime = self.path.stat().st_mtime
