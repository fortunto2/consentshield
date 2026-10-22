from pathlib import Path

import pytest

from consent.detectors import detect_leaks
from consent.policy import Policy


def test_credentials_locked(tmp_path: Path):
    p = Policy(tmp_path / "p.json")
    with pytest.raises(ValueError):
        p.set("credentials", "assistant", True)
    assert not p.allows("credentials", "assistant")


def test_consent_persists(tmp_path: Path):
    p = Policy(tmp_path / "p.json")
    p.set("health", "assistant", True)
    assert Policy(tmp_path / "p.json").allows("health", "assistant")


def test_detector_catches_key():
    assert detect_leaks("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")


class _Unsure:
    def classify(self, text, context=""):
        return "private_message", 0.3, 1.0


def test_user_answer_decides_the_line(tmp_path: Path):
    from consent.gate import decide
    from consent.schemas import Region

    policy = Policy(tmp_path / "p.json")
    line = Region("see you on Saturday", (0, 0, 10, 10))
    held = decide([line], "assistant", policy, _Unsure()).decisions[0]
    assert held.action == "ask"
    answered = decide([line], "assistant", policy, _Unsure(), user={line.text: "allow"}).decisions[0]
    assert (answered.action, answered.source) == ("allow", "user")


def test_user_cannot_release_a_detector_hit(tmp_path: Path):
    from consent.gate import decide
    from consent.schemas import Region

    policy = Policy(tmp_path / "p.json")
    key = Region("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE", (0, 0, 10, 10))
    d = decide([key], "assistant", policy, _Unsure(), user={key.text: "allow"}).decisions[0]
    assert (d.action, d.source) == ("redact", "detector")


def test_broken_connection_string_is_credentials(tmp_path: Path):
    from consent.gate import decide
    from consent.schemas import Region

    line = Region("REDIS_URL=redis://default: cacheP4ssword@cache.internal:6379", (0, 0, 10, 10))
    d = decide([line], "assistant", Policy(tmp_path / "p.json"), _Unsure()).decisions[0]
    assert (d.category, d.action) == ("credentials", "redact")
