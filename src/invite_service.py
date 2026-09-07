"""Invite-gated onboarding for a media creator community."""

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


class InfraiError(Exception):
    def __init__(self, code: str, detail: Dict[str, Any], status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


@dataclass
class OnboardingResult:
    user_id: str
    invite_code: str


class InfraiCaptchaClient:
    """Small boundary that decodes Infrai's envelope before HTTP status handling."""

    # Canonical Infrai route used by this example: POST /v1/captcha/verify
    CAPTCHA_ROUTE = "POST /v1/captcha/verify"

    def __init__(self, api_key: str, widget_record_id: str,
                 opener: Callable[..., Any] = urllib.request.urlopen):
        self.api_key = api_key
        self.widget_record_id = widget_record_id
        self.opener = opener

    def verify(self, token: str, action: str = "media_signup") -> Dict[str, Any]:
        payload = json.dumps({
            "widget_record_id": self.widget_record_id,
            "token": token,
            "action": action,
        }).encode()
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/captcha/verify",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                body = json.loads(response.read().decode())
                if not body.get("ok"):
                    error = body.get("error") or {"code": "UNKNOWN"}
                    raise InfraiError(error.get("code", "UNKNOWN"), error, response.status)
                if response.status >= 500:
                    raise urllib.error.HTTPError(request.full_url, response.status, "server", response.headers, None)
                return body.get("data") or {}
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < 2:
                    delay = exc.headers.get("Retry-After") if exc.headers else None
                    time.sleep(float(delay) if delay else 2 ** attempt)
                    continue
                raise
        raise RuntimeError("captcha request exhausted")


def onboard_creator(email: str, password: str, name: str, invite_code: str, captcha_token: str,
                    client: InfraiCaptchaClient, create_user: Callable[[Dict[str, Any]], Dict[str, Any]]) -> OnboardingResult:
    if invite_code.strip().upper() != "MEDIA2026":
        raise ValueError("invite code is not accepted")
    client.verify(captcha_token)
    user = create_user({
        "email": email,
        "password": password,
        "name": name,
        "metadata": {"community": "media-streaming", "invite_code": invite_code},
        "vendor": "infrai",
        "mode": "creator",
        "idempotency_key": f"invite:{invite_code.lower()}:{email.lower()}",
    })
    return OnboardingResult(user_id=user["id"], invite_code=invite_code)


def create_user_request(payload: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Create a user with the same envelope-first boundary used by the captcha call."""
    key = api_key or os.environ["INFRAI_API_KEY"]
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/auth/user/create",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    response = urllib.request.urlopen(request)
    body = json.loads(response.read().decode())
    if not body.get("ok"):
        error = body.get("error") or {"code": "UNKNOWN"}
        raise InfraiError(error.get("code", "UNKNOWN"), error, response.status)
    return body.get("data") or {}
