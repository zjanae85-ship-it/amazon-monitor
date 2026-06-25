import json
from urllib import request

import config


def send_feishu(text: str, webhook: str = config.WEBHOOK) -> bool:
    print("Send Feishu")

    if not webhook:
        print("Feishu Send Failed")
        print("FEISHU_WEBHOOK is empty")
        return False

    payload = json.dumps(
        {
            "msg_type": "text",
            "content": {
                "text": text
            },
        }
    ).encode("utf-8")

    req = request.Request(
        webhook,
        data=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"Feishu Response Code: {response.getcode()}")
            print(f"Feishu Response Body: {body}")

        print("Feishu Send Success")
        return True

    except Exception as exc:
        print("Feishu Send Failed")
        print(f"Feishu Error: {exc}")
        return False
