"""食藥署 食品類法令規章 爬蟲

來源：https://www.fda.gov.tw/TC/law.aspx?cid=62

特性：
- 跟「食藥署公告」(source_tfda) 不同 — 這是現行法規目錄，含各條法規的「最近修正日期」
- 「自動確保為最新」：build_data.py 合併時會更新 date 欄位，
  若某條法規的修正日期變新，就會自動排到上面、被標記為新更新
- 每次抓全部 10 條（這是食品類法規的完整清單）
"""
from __future__ import annotations
import re
import html as html_module
from common import fetch, clean_text, normalize_date, make_item

BASE = "https://www.fda.gov.tw"
LIST_URL = f"{BASE}/TC/law.aspx?cid=62"

# 法規類別關鍵字 → 標籤（協助衛生管理員快速分流）
TAG_KEYWORDS = [
    ("農藥殘留", "農藥殘留"),
    ("動物用藥", "動物用藥"),
    ("食品標示", "標示"),
    ("產品標示", "標示"),
    ("食品安全管制系統", "HACCP"),
    ("HACCP", "HACCP"),
    ("回收", "回收"),
    ("登錄", "業者登錄"),
    ("熱殺菌", "熱加工"),
    ("低酸性食品", "低酸性"),
    ("酸化食品", "酸化食品"),
    ("水產", "水產"),
    ("乳品", "乳品"),
    ("肉類", "肉類"),
    ("輸入", "輸入"),
    ("食品添加物", "食品添加物"),
    ("污染物", "污染物"),
    ("微生物", "微生物"),
    ("殘留", "殘留"),
    ("檢驗", "檢驗方法"),
]

# 純目錄入口（沒有實質法規內容）— 給較低權重
PORTAL_KEYWORDS = ["諮詢服務平台", "查詢系統", "彙編查詢"]


def parse_list(html: str) -> list[dict]:
    items: list[dict] = []
    tbody_m = re.search(r"<tbody[^>]*>(.*?)</tbody>", html, re.DOTALL | re.IGNORECASE)
    if not tbody_m:
        return items
    tbody = tbody_m.group(1)
    rows = re.split(r"<tr[\s>]", tbody)[1:]

    for row in rows:
        a = re.search(
            r"<a\s+[^>]*href=['\"]([^'\"]+)['\"]\s*(?:[^>]*title=['\"]([^'\"]*)['\"])?[^>]*>(.*?)</a>",
            row, re.DOTALL | re.IGNORECASE,
        )
        if not a:
            continue
        href = a.group(1).strip()
        title_attr = html_module.unescape(a.group(2) or "")
        title_text = clean_text(re.sub(r"<[^>]+>", "", a.group(3) or ""))
        title = clean_text(title_attr) or title_text
        if not title:
            continue

        # 日期：最後出現的 YYYY-MM-DD
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", row)
        date = normalize_date(dates[-1]) if dates else None

        # URL：補上 BASE 若是相對路徑
        if href.startswith("/"):
            url = BASE + href
        elif href.startswith("http"):
            url = href
        else:
            url = BASE + "/TC/" + href

        # 清理標題尾巴的「(另開新視窗)」雜訊
        title = re.sub(r"\s*[(（]另開(新)?視窗[)）]\s*$", "", title)

        items.append({"title": title, "url": url, "date": date})
    return items


def make_law_item(raw: dict) -> dict:
    title = raw["title"]
    is_portal = any(k in title for k in PORTAL_KEYWORDS)

    # 標籤：法規 + 類別 + 是否為目錄入口
    tags = ["法規"]
    if is_portal:
        tags.append("查詢系統")
    for kw, tag in TAG_KEYWORDS:
        if kw in title and tag not in tags:
            tags.append(tag)

    # AI 摘要：以結構化方式呈現（不需要 NLP）
    ai_summary = []
    if raw["date"]:
        ai_summary.append(f"最近修正日期：{raw['date']}")
    if is_portal:
        ai_summary.append("此為查詢/解釋彙編入口，非單一法規條文")
    else:
        ai_summary.append("食品類現行有效法規")
    if len(tags) > 1:
        ai_summary.append(f"分類：{'、'.join(t for t in tags if t != '法規')}")
    ai_summary.append("點「查看原文」前往條文全文（多為衛福部法規檢索系統外部連結）")

    return make_item(
        source="tfda_law",
        source_label="食藥署法規",
        source_color="amber",
        title=title,
        url=raw["url"],
        date=raw["date"],
        summary=f"食品類現行法規。最近修正：{raw['date'] or '未標註'}。",
        tags=tags,
    ) | {"ai_summary": ai_summary}


def crawl() -> list[dict]:
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [TFDA Law] 抓取失敗: {e}")
        return []
    raw = parse_list(html)
    items = [make_law_item(r) for r in raw]
    print(f"  [TFDA Law] 食品類法規 {len(items)} 條")
    return items


if __name__ == "__main__":
    import json
    items = crawl()
    print(json.dumps(items[:3], ensure_ascii=False, indent=2))
