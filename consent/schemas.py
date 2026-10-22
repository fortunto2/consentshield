"""Domain language: what is on the screen, why the agent wants it, what the user allowed."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Category = Literal["credentials", "financial", "health", "private_message", "contact_info", "work", "public"]
Purpose = Literal["assistant", "analytics", "training", "third_party"]
Action = Literal["allow", "redact", "ask"]

CATEGORIES: dict[str, str] = {
    "credentials": "Passwords, API keys, tokens, secrets, login codes, connection strings",
    "financial": "Bank balances, card numbers, transactions, salaries, invoices, account numbers",
    "health": "Medical conditions, diagnoses, prescriptions, test results, therapy, doctor visits",
    "private_message": "Personal chat or DM between people, private conversation, dating, family talk",
    "contact_info": "A person's phone number, home address, personal email, date of birth",
    "work": "Ordinary work content: code, documents, tickets, roadmaps, standup notes, meeting notes without secrets",
    "public": "Weather, news, restaurant menus, ads, app titles and generic UI labels, nothing about a specific person",
}

PURPOSES: dict[str, str] = {
    "assistant": "The agent uses the screen to help me right now, nothing is stored",
    "analytics": "Usage analytics about what I do",
    "training": "Improving the vendor's models",
    "third_party": "Sharing with a third-party tool or API the agent calls",
}

GATE = 0.8  # calibrated confidence needed to act without asking the human (Haldar's rule)


@dataclass
class Region:
    text: str
    box: tuple[float, float, float, float]  # x, y, w, h, top-left origin, pixels


@dataclass
class Decision:
    text: str
    box: tuple[float, float, float, float]
    category: str
    confidence: float
    action: Action
    reason: str
    source: Literal["detector", "model", "user"] = "model"
    ms: float = 0.0


@dataclass
class GateResult:
    purpose: str
    decisions: list[Decision] = field(default_factory=list)
    ms: float = 0.0

    @property
    def counts(self) -> dict[str, int]:
        out = {"allow": 0, "redact": 0, "ask": 0}
        for d in self.decisions:
            out[d.action] += 1
        return out

    def to_dict(self) -> dict:
        return {"purpose": self.purpose, "ms": round(self.ms, 1), "counts": self.counts,
                "decisions": [asdict(d) for d in self.decisions]}
