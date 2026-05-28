"""EFSA (歐洲食品安全局) 新聞爬蟲

頁面為 Drupal 8+ 結構，新聞列表 class 通常為 .views-row 或類似。
"""
from __future__ import annotations
import re
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.efsa.europa.eu"
LIST_URL = f"{BASE}/en/news"


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [EFSA] 抓取失敗: {e}")
        return items

    # Drupal views-row 或 article 區塊
    # 通用做法：找 <article> ... </article> 或 .views-row
    blocks = re.findall(
        r'<article[^>]*>(.*?)</article>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not blocks:
        blocks = re.findall(
            r'<div[^>]*class="[^"]*views-row[^"]*"[^>]*>(.*?)(?=<div[^>]*class="[^"]*views-row|</div>\s*</div>)',
            html,
            re.DOTALL | re.IGNORECASE,
        )

    for block in blocks[:20]:
        # 標題與連結
        link_m = re.search(r'<a\s+href="([^"]+)"[^>]*>([^<]{10,300})</a>', block, re.DOTALL)
        if not link_m:
            continue
        href = link_m.group(1)
        if href.startswith("/"):
            href = BASE + href
        elif not href.startswith("http"):
            continue

        title = clean_text(link_m.group(2))
        if not title or len(title) < 10:
            continue

        # 過濾非新聞連結
        if any(skip in href.lower() for skip in ["/podcast/", "/event/", ".pdf", "/topics/"]):
            # 這些可以保留但標籤化
            pass

        # 日期
        date_m = re.search(
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            block,
        )
        if not date_m:
            date_m = re.search(r'(\d{4}-\d{2}-\d{2})', block)
        date = normalize_date(date_m.group(1)) if date_m else None

        # 摘要：抓 block 內的純文字（去除標題後）
        text = strip_tags(block)
        text = re.sub(r"\s+", " ", text).strip()
        # 移除標題避免重複
        if title in text:
            text = text.replace(title, "", 1).strip()
        summary = text[:300]

        # 自動標籤
        tags = ["EFSA"]
        title_lower = title.lower()
        if "pesticid" in title_lower:
            tags.append("農藥殘留")
        if "additive" in title_lower or "e1" in title_lower:
            tags.append("食品添加物")
        if "contaminant" in title_lower or "toxin" in title_lower:
            tags.append("污染物")
        if "/podcast/" in href.lower():
            tags.append("Podcast")

        items.append(make_item(
            source="efsa",
            source_label="EFSA",
            source_color="purple",
            title=title,
            url=href,
            date=date,
            summary=summary,
            tags=tags,
        ))

    print(f"  [EFSA] 找到 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
