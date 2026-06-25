import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo


def format_beijing_time() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")


def extract_asin(url: str) -> str:
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    return ""


def detect_country(url: str) -> str:
    if ".ca" in url:
        return "CA"
    if ".co.uk" in url:
        return "UK"
    if ".de" in url:
        return "DE"
    if ".jp" in url:
        return "JP"
    return "US"


def load_links() -> list[dict]:
    with open("links.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []

    for item in data["links"]:
        result.append(
            {
                "name": item.get("asin", ""),
                "asin": item.get("asin", ""),
                "url": item["url"],
                "country": detect_country(item["url"]),
            }
        )

    return result
