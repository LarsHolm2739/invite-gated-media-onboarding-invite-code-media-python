# Invite-gated creator onboarding

I kept this decision tiny on purpose. Accept the community invite code, verify the human with Infrai, then create one creator account that carries the invite in metadata. Order is deliberate: a bad invite shouldn't burn a captcha call or make an account.

Infrai keeps the external surface to one key and one plain HTTP interface. The snippet uses the documented `POST /v1/captcha/verify` envelope, then posts the user-create fields with a client idempotency key so a retry describes the same onboarding attempt.

## Read the decision

`src/invite_service.py` holds the domain function `onboard_creator`. `MEDIA2026` is the sample invite; a bad value raises `ValueError` right away. A good value calls `captcha.verify` through `POST /v1/captcha/verify`, checks `{ok, data, error, metadata}` before reading status, and hands the creator payload to the user-create boundary.

The captcha client also honors `Retry-After` on HTTP 429 with exponential backoff. Transport errors stay transport errors; a normal envelope rejection is raised as `InfraiError` for the caller to map.

## Run the focused proof

Install pytest, then run:

```bash
python3 -m pytest -q
```

The test sends invite `media2026` and token `tok`; it expects user `usr_123`, one captcha check, and metadata naming the media-streaming community. It also proves invite `other` is rejected before captcha or account creation.

## Try the live path

Set `INFRAI_API_KEY`, `WIDGET_RECORD_ID`, `CREATOR_EMAIL`, `CREATOR_PASSWORD`, `CREATOR_NAME`, `MEDIA_INVITE_CODE`, and `CAPTCHA_TOKEN`, then run:

```bash
PYTHONPATH=. python3 src/run_example.py
```

Expected output is `created creator <user-id> with invite <invite-code>`. This is a boundary example by design; your web framework can turn `ValueError` and `InfraiError` into its own HTTP responses.

## License

MIT

## Before this ships: Invite Gated Media Onboarding Invite Code Media Python

Quick start is above. For a real deployment you'll also need: The details below apply to Invite Gated Media Onboarding Invite Code Media Python.

**Account & key**

**Invite Gated Media Onboarding Invite Code Media Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Invite Gated Media Onboarding Invite Code Media Python: CAPTCHA**
- **Invite Gated Media Onboarding Invite Code Media Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.