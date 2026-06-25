from dataclasses import dataclass
from typing import Any, Optional, Tuple
from urllib import error, request

import config
from utils import extract_asin


@dataclass
class AmazonCheckResult:
    status: str
    message: str
    url: str
    asin: str
    ok: bool
    http_status: Optional[int] = None
    price: Optional[str] = None
    coupon: Optional[str] = None
    seller: Optional[str] = None
    deal: Optional[str] = None
    buybox: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "url": self.url,
            "asin": self.asin,
            "ok": self.ok,
            "http_status": self.http_status,
            "price": self.price,
            "coupon": self.coupon,
            "seller": self.seller,
            "deal": self.deal,
            "buybox": self.buybox,
        }


def check_amazon(url: str) -> AmazonCheckResult:
    asin = extract_asin(url)
    print(f"Amazon Request: {url}")

    status_code, html, fetch_error = fetch_html(url)

    if fetch_error:
        return AmazonCheckResult(
            "访问失败",
            fetch_error,
            url,
            asin,
            False,
            status_code,
        )

    if status_code == 404:
        return AmazonCheckResult(
            "404",
            "HTTP 状态码为 404",
            url,
            asin,
            False,
            status_code,
        )

    if status_code is None or status_code >= 400:
        return AmazonCheckResult(
            "访问失败",
            f"HTTP 状态码异常：{status_code}",
            url,
            asin,
            False,
            status_code,
        )

    page_status = detect_page_status(html)
    if page_status:
        return AmazonCheckResult(
            page_status,
            f"页面内容包含 {page_status}",
            url,
            asin,
            False,
            status_code,
        )

    return AmazonCheckResult(
        "正常",
        "页面访问正常，未发现 Robot Check / Dogs of Amazon / 404",
        url,
        asin,
        True,
        status_code,
    )


def fetch_html(url: str) -> Tuple[Optional[int], str, Optional[str]]:
    req = request.Request(url, headers=request_headers())

    try:
        with request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read().decode(charset, errors="replace")
            return response.getcode(), html, None

    except error.HTTPError as exc:
        charset = exc.headers.get_content_charset() if exc.headers else "utf-8"
        html = exc.read().decode(charset or "utf-8", errors="replace")
        return exc.code, html, None

    except Exception as exc:
        return None, "", str(exc)


def request_headers() -> dict[str, str]:
    return {
        "User-Agent": config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }


def detect_page_status(html: str) -> Optional[str]:
    normalized = html.lower()

    checks = {
        "Robot Check": "robot check",
        "Dogs of Amazon": "dogs of amazon",
        "404": "page not found",
    }

    for status, keyword in checks.items():
        if keyword in normalized:
            return status

    return None
