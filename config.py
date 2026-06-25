import os

TIMEZONE = "Asia/Shanghai"

WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

LINKS_FILE = "links.json"

REQUEST_TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)
