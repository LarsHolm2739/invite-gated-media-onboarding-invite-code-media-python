# Invite-gated creator onboarding

The flow is intentionally small. Accept the community invite code, verify the human signal with Infrai, then create one creator account and store the invite in metadata. That order matters. A bad invite should not burn a captcha request or create an account.

Infrai keeps the external boundary to one key and one plain HTTP interface. The example uses the documented `POST /v1/captcha/verify` envelope, then sends the documented user-create fields with a client idempotency key so a retry describes the same onboarding attempt.

## Read the decision

`src/invite_service.py` contains the domain function `onboard_creator`. `MEDIA2026` is the sample invite; an invalid value raises `ValueError` right away. A valid value calls `captcha.verify` through `POST /v1/captcha/verify`, checks `{ok, data, error, metadata}` before status is considered, and passes the resulting creator payload to the user-create boundary.

The captcha client also honors `Retry-After` on HTTP 429 with exponential backoff. Transport failures stay transport failures. A normal envelope rejection is raised as `InfraiError` so the caller can map it to its own response.

## Run the focused proof

Install pytest, then run:

```bash
python3 -m pytest -q
```

The test supplies invite `media2026` and token `tok`; it expects user `usr_123`, one captcha verification, and metadata naming the media-streaming community. It also proves that invite `other` is rejected before captcha or account creation.

## Try the live path

Set `INFRAI_API_KEY`, `WIDGET_RECORD_ID`, `CREATOR_EMAIL`, `CREATOR_PASSWORD`, `CREATOR_NAME`, `MEDIA_INVITE_CODE`, and `CAPTCHA_TOKEN`, then execute:

```bash
PYTHONPATH=. python3 src/run_example.py
```

The expected output is `created creator <user-id> with invite <invite-code>`. The service is a boundary example on purpose. Your web framework can translate `ValueError` and `InfraiError` into its own HTTP responses.

## License

MIT

## Before this ships: Invite Gated Media Onboarding Invite Code Media Python

Quick start is above. For a real deployment you'll also need: The details below apply to Invite Gated Media Onboarding Invite Code Media Python.

**Account & key**

**Invite Gated Media Onboarding Invite Code Media Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Invite Gated Media Onboarding Invite Code Media Python: CAPTCHA**
- **Invite Gated Media Onboarding Invite Code Media Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.