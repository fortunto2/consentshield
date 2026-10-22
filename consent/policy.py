"""User consent per (category, purpose). Ketch-style purposes, enforced at the moment the agent acts."""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import CATEGORIES, PURPOSES

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
    def __init__(self, path: Path):
        self.path = path
        self.rules = json.loads(path.read_text()) if path.exists() else json.loads(json.dumps(DEFAULT))

    def allows(self, category: str, purpose: str) -> bool:
        return bool(self.rules.get(category, {}).get(purpose, False))

    def set(self, category: str, purpose: str, allowed: bool) -> None:
        if category in LOCKED or category not in CATEGORIES or purpose not in PURPOSES:
            raise ValueError(f"cannot change {category}/{purpose}")
        self.rules.setdefault(category, {})[purpose] = allowed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.rules, indent=2))
