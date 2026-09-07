import pytest

from src.invite_service import OnboardingResult, onboard_creator


class Captcha:
    def __init__(self):
        self.tokens = []

    def verify(self, token):
        self.tokens.append(token)
        return {"score": 0.99}


def test_valid_invite_verifies_captcha_and_creates_creator():
    captcha = Captcha()
    calls = []

    def create(payload):
        calls.append(payload)
        return {"id": "usr_123"}

    result = onboard_creator("a@example.com", "secret", "A", "media2026", "tok", captcha, create)

    assert result == OnboardingResult("usr_123", "media2026")
    assert captcha.tokens == ["tok"]
    assert calls[0]["metadata"]["community"] == "media-streaming"
    assert calls[0]["idempotency_key"] == "invite:media2026:a@example.com"


def test_unknown_invite_is_rejected_before_captcha():
    with pytest.raises(ValueError):
        onboard_creator("a@example.com", "secret", "A", "other", "tok", Captcha(), lambda _: {"id": "x"})
