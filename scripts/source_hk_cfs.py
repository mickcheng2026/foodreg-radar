"""香港食物環境衛生署 食物安全中心 (CFS) 食物警報爬蟲

來源：https://www.cfs.gov.hk/tc_chi/whatsnew/whatsnew_fa/whatsnew_fa.html
- 食物警報（Class 1）：可能含異物 / 微生物 / 受污染等
- 致敏物警報（Class 2）：未標示過敏原

頁面結構是乾淨的 HTML table，每一 row 一筆警報。
"""
from __future__ import annotations
import re
import html as html_module
from datetime import datetime
from common import fetch, clean_text, make_item

BASE = "https://www.cfs.gov.hk"
LIST_URL = f"{BASE}/tc_chi/whatsnew/whatsnew_fa/whatsnew_fa.html"


def parse_date_hk(s: str) -> str | None:
    """HK 格式：20.4.2026 → 2026-04-20"""
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", s.strip())
    if not m:
        return None
    try:
        return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))).date().isoformat()
    except ValueError:
        return None


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [HK CFS] 抓取失敗: {e}")
        return items

    # 找 tbody
    tbody_m = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL | re.IGNORECASE)
    if not tbody_m:
        print("  [HK CFS] 找不到 tbody")
        return items
    tbody = tbody_m.group(1)

    rows = re.findall(r'<tr\s+class="datarow"[^>]*>(.*?)</tr>', tbody, re.DOTALL | re.IGNORECASE)
    for row in rows:
        # 日期
        date_m = re.search(r"<td[^>]*class=\"subHeader\"[^>]*>(\d{1,2}\.\d{1,2}\.\d{4})", row)
        date = parse_date_hk(date_m.group(1)) if date_m else None

        # 警報類別
        cat_m = re.search(r'<td[^>]*class="categoryfield"[^>]*>([^<]+)</td>', row)
        category = clean_text(cat_m.group(1)) if cat_m else ""

        # 標題與連結
        a_m = re.search(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', row)
        if not a_m:
            continue
        href = a_m.group(1)
        title = clean_text(html_module.unescape(a_m.group(2)))
        if not title:
            continue
        if href.startswith("/"):
            url = BASE + href
        elif href.startswith("http"):
            url = href
        else:
            url = BASE + "/" + href.lstrip("/")

        # 標籤
        tags = ["警報"]
        if category:
            tags.append(category)
        if "致敏物" in category or "過敏" in title:
            tags.append("過敏原")
        if "玻璃" in title or "金屬" in title or "異物" in title:
            tags.append("異物")
        if "微生物" in title or "細菌" in title or "病毒" in title:
            tags.append("微生物")

        # 結構化中文 AI 摘要
        ai_summary = []
        if category:
            ai_summary.append(f"警報類別：{category}")
        ai_summary.append(f"事件：{title}")
        if date:
            ai_summary.append(f"公告日期：{date}")
        ai_summary.append("來源：香港食物安全中心 (CFS)")

        item = make_item(
            source="hk_cfs",
            source_label="香港 CFS",
            source_color="cyan",
            title=title,
            url=url,
            date=date,
            summary=f"[{category}] {title}",
            tags=tags,
        )
        item["ai_summary"] = ai_summary
        items.append(item)

    print(f"  [HK CFS] 香港食物警報 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
