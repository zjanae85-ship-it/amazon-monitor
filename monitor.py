import argparse
import traceback
from typing import Any

import config
from amazon import check_amazon
from notify import send_feishu
from utils import format_beijing_time, load_links


Result = dict[str, Any]


def main() -> int:
    args = parse_args()

    print("Start Monitor")
    print("Load Config")
    print(f"Timezone: {config.TIMEZONE}")
    print(f"Mode: {'alarm' if args.alarm else 'normal-report'}")

    results: list[Result] = []
    exit_code = 0

    try:
        links = load_links()

        if not links:
            raise ValueError("links.json 中没有可用的监控链接")

        for link in links:
            print(f"Checking {link['country']}")
            check_result = check_amazon(link["url"]).to_dict()
            results.append({**link, **check_result})

    except Exception as exc:
        exit_code = 1
        print(f"Monitor Error: {exc}")
        print(traceback.format_exc())
        results.append(build_task_error_result(exc))

    normal_count, abnormal_count = count_results(results)

    print(f"Normal Count: {normal_count}")
    print(f"Abnormal Count: {abnormal_count}")

    if should_send_report(args.alarm, abnormal_count):
        message = build_report(results, normal_count, abnormal_count)

        print("Feishu Message Preview:")
        print(message)

        if not send_feishu(message):
            exit_code = 1
    else:
        print("Send Feishu: skipped, alarm mode has no abnormal result")

    print("Finish")
    return exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Amazon Monitor")
    parser.add_argument(
        "--alarm",
        action="store_true",
        help="只在发现异常时发送飞书告警",
    )
    return parser.parse_args()


def build_task_error_result(exc: Exception) -> Result:
    return {
        "name": "监控任务",
        "country": "US",
        "url": config.LINKS_FILE,
        "status": "访问失败",
        "message": f"监控任务执行失败：{exc}",
        "asin": "",
        "ok": False,
        "http_status": None,
        "price": None,
        "coupon": None,
        "seller": None,
        "deal": None,
        "buybox": None,
    }


def count_results(results: list[Result]) -> tuple[int, int]:
    abnormal_count = sum(1 for item in results if not item["ok"])
    normal_count = len(results) - abnormal_count
    return normal_count, abnormal_count


def should_send_report(alarm_mode: bool, abnormal_count: int) -> bool:
    if alarm_mode:
        return abnormal_count > 0

    return True


def build_report(results: list[Result], normal_count: int, abnormal_count: int) -> str:
    title = "Amazon 监控异常" if abnormal_count else "Amazon 监控正常"

    lines = [
        title,
        f"检测时间：{format_beijing_time()}",
        f"正常数量：{normal_count}",
        f"异常数量：{abnormal_count}",
        "",
        "检测详情：",
    ]

    for index, item in enumerate(results, start=1):
        mark = "正常" if item["ok"] else "异常"
        http_status = item.get("http_status")
        asin = item.get("asin") or "未识别"
        http_text = f"HTTP {http_status}" if http_status else "无 HTTP 状态码"

        lines.extend(
            [
                f"{index}. [{mark}] {item['name']}",
                f"   站点：{item['country']}",
                f"   ASIN：{asin}",
                f"   状态：{item['status']}",
                f"   说明：{item['message']}",
                f"   HTTP：{http_text}",
                f"   链接：{item['url']}",
            ]
        )

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
