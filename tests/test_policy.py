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
