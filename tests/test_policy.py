from pathlib import Path

import pytest

from consent.detectors import detect_leaks
from consent.gate import decide
from consent.policy import Policy
from consent.schemas import Region


def region(text: str) -> Region:
    return Region(text, (0, 0, 10, 10))


class _Unsure:
    def classify(self, text, context=""):
        return "private_message", 0.3, 1.0


def test_credentials_locked(tmp_path: Path):
    p = Policy(tmp_path / "p.json")
    with pytest.raises(ValueError):
        p.set("credentials", "assistant", True)
    assert not p.allows("credentials", "assistant")


def test_consent_persists(tmp_path: Path):
    p = Policy(tmp_path / "p.json")
    p.set("health", "assistant", True)
    assert Policy(tmp_path / "p.json").allows("health", "assistant")


def test_policy_follows_the_file(tmp_path: Path):
    """Two processes share one file: a change or a `rm -rf data` is seen without a restart."""
    writer, reader = Policy(tmp_path / "p.json"), Policy(tmp_path / "p.json")
    assert not reader.allows("health", "assistant")
    writer.set("health", "assistant", True)
    assert reader.allows("health", "assistant")
    (tmp_path / "p.json").unlink()
    assert not reader.allows("health", "assistant")


def test_detector_catches_key():
    assert detect_leaks("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")


def test_user_answer_decides_the_line(tmp_path: Path):
    policy, line = Policy(tmp_path / "p.json"), region("see you on Saturday")
    assert decide([line], "assistant", policy, _Unsure()).decisions[0].action == "ask"
    answered = decide([line], "assistant", policy, _Unsure(), user={line.text: "allow"}).decisions[0]
    assert (answered.action, answered.source) == ("allow", "user")


def test_user_cannot_release_a_detector_hit(tmp_path: Path):
    key = region("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
    d = decide([key], "assistant", Policy(tmp_path / "p.json"), _Unsure(), user={key.text: "allow"}).decisions[0]
    assert (d.action, d.source) == ("redact", "detector")


def test_broken_connection_string_is_credentials(tmp_path: Path):
    line = region("REDIS_URL=redis://default: cacheP4ssword@cache.internal:6379")
    d = decide([line], "assistant", Policy(tmp_path / "p.json"), _Unsure()).decisions[0]
    assert (d.category, d.action, d.source) == ("credentials", "redact", "detector")
