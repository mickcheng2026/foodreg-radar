"""ISO 國際標準組織新聞爬蟲

僅抓取與「食品安全」相關的新聞清單與標準資訊。
不抓取標準全文（受版權保護）。
"""
from __future__ import annotations
import re
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.iso.org"
LIST_URL = f"{BASE}/news/"


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [ISO] 抓取失敗: {e}")
        return items

    # ISO 新聞列表通常用 article 區塊或 .news-item
    blocks = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL | re.IGNORECASE)
    if not blocks:
        blocks = re.findall(
            r'<div[^>]*class="[^"]*news[-_]item[^"]*"[^>]*>(.*?)</div>\s*</div>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
    if not blocks:
        # 簡單 fallback：用 a href="/news/..." 全部撈出來
        link_blocks = re.findall(
            r'<a\s+href="(/news/[^"]+)"[^>]*>([^<]{10,300})</a>',
            html,
            re.DOTALL,
        )
        for href, title in link_blocks[:15]:
            title = clean_text(title)
            if not title:
                continue
            items.append(make_item(
                source="iso",
                source_label="ISO 標準",
                source_color="indigo",
                title=title,
                url=BASE + href,
                date=None,
                summary="",
                tags=["ISO"],
            ))
        print(f"  [ISO] 找到 {len(items)} 筆（fallback）")
        return _filter_food_relevant(items)

    for block in blocks[:20]:
        link_m = re.search(r'<a\s+href="([^"]+)"[^>]*>([^<]{10,300})</a>', block, re.DOTALL)
        if not link_m:
            continue
        href = link_m.group(1)
        if href.startswith("/"):
            href = BASE + href
        title = clean_text(link_m.group(2))
        if not title:
            continue

        date_m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', block)
        date = normalize_date(date_m.group(1)) if date_m else None

        text = strip_tags(block)
        text = re.sub(r"\s+", " ", text).strip()
        if title in text:
            text = text.replace(title, "", 1).strip()
        summary = text[:300]

        items.append(make_item(
            source="iso",
            source_label="ISO 標準",
            source_color="indigo",
            title=title,
            url=href,
            date=date,
            summary=summary,
            tags=["ISO"],
        ))

    items = _filter_food_relevant(items)
    print(f"  [ISO] 找到 {len(items)} 筆（食品相關）")
    return items


def _filter_food_relevant(items: list[dict]) -> list[dict]:
    """只保留食品安全 / 食品科學 / 包裝 / 衛生相關的新聞"""
    keywords = [
        "food", "safety", "haccp", "iso 22000", "iso 22002", "iso 9001",
        "packaging", "hygien", "labelling", "label", "agricultur", "fish",
        "meat", "dairy", "beverage", "nutrit", "allergen", "pesticide",
        "contam", "additive", "halal", "kosher", "organic",
    ]
    out = []
    for it in items:
        text = (it["title"] + " " + it.get("summary", "")).lower()
        if any(k in text for k in keywords):
            out.append(it)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:5], ensure_ascii=False, indent=2))
