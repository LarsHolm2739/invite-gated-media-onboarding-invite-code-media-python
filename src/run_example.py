import os

from invite_service import InfraiCaptchaClient, create_user_request, onboard_creator


def main() -> None:
    result = onboard_creator(
        email=os.environ["CREATOR_EMAIL"],
        password=os.environ["CREATOR_PASSWORD"],
        name=os.environ.get("CREATOR_NAME", "New Creator"),
        invite_code=os.environ["MEDIA_INVITE_CODE"],
        captcha_token=os.environ["CAPTCHA_TOKEN"],
        client=InfraiCaptchaClient(
            os.environ["INFRAI_API_KEY"],
            os.environ["WIDGET_RECORD_ID"],
        ),
        create_user=create_user_request,
    )
    print(f"created creator {result.user_id} with invite {result.invite_code}")


if __name__ == "__main__":
    main()
