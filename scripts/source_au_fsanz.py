"""澳洲 FSANZ 食品召回爬蟲

來源：https://www.foodstandards.gov.au/food-recalls/recalls
- FSANZ = Food Standards Australia New Zealand
- 食品召回包括所有澳洲市場上的召回案件
- 頁面結構清晰：<div class="food-recall-wrapper"> 包住每筆
"""
from __future__ import annotations
import re
import html as html_module
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.foodstandards.gov.au"
LIST_URL = f"{BASE}/food-recalls/recalls"


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [AU FSANZ] 抓取失敗: {e}")
        return items

    # 每筆召回都包在 <div class="food-recall-wrapper">
    blocks = re.findall(
        r'<div class="food-recall-wrapper">(.*?)</div>\s*</span>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not blocks:
        # Fallback: parse via anchor pattern
        blocks = re.findall(
            r'<h2>\s*<a\s+href="(/food-recalls/recall-alert/[^"]+)"[^>]*>([^<]+)</a>\s*</h2>(.*?)(?=<h2>|</div>\s*</span>|$)',
            html,
            re.DOTALL | re.IGNORECASE,
        )

    for block in blocks[:25]:
        # 標題與連結
        title_m = re.search(
            r'<h2>\s*<a\s+href="([^"]+)"[^>]*>([^<]+)</a>\s*</h2>',
            block,
            re.DOTALL,
        )
        if not title_m:
            continue
        href = title_m.group(1)
        title = clean_text(html_module.unescape(title_m.group(2)))
        if not title:
            continue
        url = BASE + href if href.startswith("/") else href

        # 描述：<p>...</p> 在 h2 之後
        desc_m = re.search(r'<h2>.*?</h2>\s*<p>(.*?)</p>', block, re.DOTALL)
        description = clean_text(strip_tags(desc_m.group(1))) if desc_m else ""

        # 發布日期：<p class="published-date">Published DD Month YYYY</p>
        date_m = re.search(
            r'class="published-date"[^>]*>\s*(?:Published\s+)?([^<]+)',
            block,
            re.IGNORECASE,
        )
        date = normalize_date(date_m.group(1).strip()) if date_m else None

        # 標籤：原因與地區
        tags = ["召回"]
        desc_lower = description.lower()
        if "allerge" in desc_lower or "undeclared" in desc_lower:
            tags.append("過敏原")
        if "foreign matter" in desc_lower or "foreign material" in desc_lower or "glass" in desc_lower or "metal" in desc_lower or "plastic" in desc_lower:
            tags.append("異物")
        if "salmonella" in desc_lower:
            tags.append("沙門氏菌")
        if "listeria" in desc_lower:
            tags.append("李斯特菌")
        if "label" in desc_lower or "mislab" in desc_lower:
            tags.append("標示")
        # 地區
        for state in ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]:
            if state in description:
                tags.append(state)
        if "national" in desc_lower or "all states" in desc_lower:
            tags.append("全澳洲")

        # 中文標題
        title_zh = f"澳洲召回 — {title[:60]}"

        # AI 摘要（中文，從結構化資訊組成）
        ai_summary = [f"召回事件：{title}"]
        if description:
            ai_summary.append(f"原因 / 影響：{description[:200]}")
        if date:
            ai_summary.append(f"公告日期：{date}")
        ai_summary.append("來源：澳紐食品標準局 (FSANZ)")

        item = make_item(
            source="au_fsanz",
            source_label="澳洲 FSANZ",
            source_color="amber",
            title=title,
            url=url,
            date=date,
            summary=description or title,
            tags=tags,
        )
        item["title_zh"] = title_zh
        item["ai_summary"] = ai_summary
        items.append(item)

    print(f"  [AU FSANZ] 澳洲食品召回 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
