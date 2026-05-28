"""Codex Alimentarius (FAO / WHO 國際食品法典) 新聞爬蟲"""
from __future__ import annotations
import re
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.fao.org"
LIST_URL = f"{BASE}/fao-who-codexalimentarius/news-and-events/en/"


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [Codex] 抓取失敗: {e}")
        return items

    # Codex 頁面結構：用 anchor + 日期附近的文字判斷
    # FAO 通用結構：<a href="...news-details..."> + 標題
    link_pattern = re.compile(
        r'<a\s+href="([^"]*news-details[^"]*)"[^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    seen = set()
    matches = list(link_pattern.finditer(html))

    for m in matches[:30]:
        href = m.group(1)
        if not href.startswith("http"):
            if href.startswith("/"):
                href = BASE + href
            else:
                continue
        if href in seen:
            continue
        seen.add(href)

        title = clean_text(strip_tags(m.group(2)))
        if not title or len(title) < 10:
            continue

        # 取 anchor 周遭 400 字找日期
        ctx_start = max(0, m.start() - 200)
        ctx_end = min(len(html), m.end() + 200)
        ctx = html[ctx_start:ctx_end]
        date_m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})|(\d{4}-\d{2}-\d{2})', ctx)
        date = normalize_date(date_m.group(0)) if date_m else None

        items.append(make_item(
            source="codex",
            source_label="Codex",
            source_color="rose",
            title=title,
            url=href,
            date=date,
            summary="",
            tags=["Codex"],
        ))

        if len(items) >= 15:
            break

    print(f"  [Codex] 找到 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:5], ensure_ascii=False, indent=2))
