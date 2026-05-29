"""食藥署 (TFDA) 公告、新聞、預告法規爬蟲"""
from __future__ import annotations
import re
from common import fetch, clean_text, normalize_date, make_item, strip_tags

BASE = "https://www.fda.gov.tw"

# 食藥署各分類 cid 對照
# cid=3 本署公告；cid=4 本署新聞；cid=5072 預告法規沿革
CATEGORIES = [
    {"cid": 3, "label": "公告", "color": "emerald"},
    {"cid": 4, "label": "新聞", "color": "emerald"},
    {"cid": 5072, "label": "預告法規", "color": "red"},
]

# 每分類抓的頁數（每頁 10 筆）— 50 頁 = 500 筆 ~ 1 年
PAGES_PER_CATEGORY = 50


def parse_list_page(html: str, cid: int) -> list[dict]:
    """從食藥署列表頁面解出每筆公告

    HTML 結構（注意：屬性的單引號是 HTML entity &#39;，所以不能用一般 regex 抓 class）：
      <tbody>
        <tr><td>序號</td><td>...<a href="newsContent.aspx?...">標題</a></td><td>YYYY-MM-DD</td></tr>
        ...
      </tbody>
    """
    items: list[dict] = []
    seen: set[str] = set()

    # 1. 取出 tbody
    tbody_m = re.search(r"<tbody[^>]*>(.*?)</tbody>", html, re.DOTALL | re.IGNORECASE)
    if not tbody_m:
        return items
    tbody = tbody_m.group(1)

    # 2. 用 <tr 切片
    chunks = re.split(r"<tr[\s>]", tbody)[1:]  # 第一個是 <tr 前的空白

    for chunk in chunks:
        # 找出 anchor
        a_m = re.search(
            r'<a\s+href="(newsContent\.aspx\?cid=\d+&id=[^"]+)"\s*(?:title="([^"]*)")?[^>]*>(.*?)</a>',
            chunk,
            re.DOTALL | re.IGNORECASE,
        )
        if not a_m:
            continue
        href = a_m.group(1)
        if href in seen:
            continue
        seen.add(href)

        title_attr = clean_text(a_m.group(2) or "")
        title_text = clean_text(strip_tags(a_m.group(3) or ""))
        title = title_attr or title_text

        # 日期在最後一個 <td>，搜尋 YYYY-MM-DD
        date_match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", chunk)
        date_str = date_match.group(0) if date_match else None

        items.append({
            "date": normalize_date(date_str) if date_str else None,
            "url": f"{BASE}/TC/{href}",
            "title": title,
        })
    return items


def fetch_detail_summary(url: str) -> str:
    """抓取公告內文，截取前幾句作為摘要

    食藥署公告詳細頁通常有 <div class="news-content"> 或 <div id="ContentPlaceHolder1_..."> 包住內文
    """
    try:
        html = fetch(url, timeout=20)
    except Exception:
        return ""

    # 食藥署內文主區塊 id = ContentPlaceHolder1_PageContentUC_PnlCms
    body = None
    m = re.search(
        r'<div[^>]*id="ContentPlaceHolder1_PageContentUC_PnlCms"[^>]*>(.*?)</div>\s*(?:<div[^>]*id="ContentPlaceHolder1_PageContentUC_(?:lblFile|ScoreStrPanel|UpdatedDateLabel)|<table)',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        body = m.group(1)
    else:
        # 後備：抓 <div id="pastingspan1"> 區段
        spans = re.findall(r'<div[^>]*id="pastingspan\d+"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
        if spans:
            body = " ".join(spans)

    if not body:
        return ""

    text = strip_tags(body)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400].strip()


def crawl() -> list[dict]:
    all_items: list[dict] = []
    for cat in CATEGORIES:
        cat_rows: list[dict] = []
        seen_urls: set[str] = set()
        # 分頁抓取
        for pn in range(1, PAGES_PER_CATEGORY + 1):
            url = f"{BASE}/TC/news.aspx?cid={cat['cid']}&pn={pn}"
            try:
                html = fetch(url)
            except Exception as e:
                print(f"  [TFDA cid={cat['cid']} pn={pn}] 抓取失敗: {e}")
                break
            rows = parse_list_page(html, cat["cid"])
            if not rows:
                break
            new_count = 0
            for row in rows:
                if row.get("url") and row["url"] not in seen_urls:
                    seen_urls.add(row["url"])
                    cat_rows.append(row)
                    new_count += 1
            if new_count == 0:
                # 沒新項目，跳出（達到歷史頁面）
                break

        print(f"  [TFDA {cat['label']}] 共 {len(cat_rows)} 筆（{PAGES_PER_CATEGORY} 頁內）")

        # 只對前 30 筆抓內文摘要（避免太多請求）；其他用標題當摘要
        for i, row in enumerate(cat_rows):
            if i < 30:
                summary = fetch_detail_summary(row["url"]) if row.get("url") else ""
            else:
                summary = ""
            tags = [cat["label"]]
            # 自動標籤化
            t = row["title"] or ""
            if "HACCP" in t or "食品安全管制系統" in t:
                tags.append("HACCP")
            if "預告" in t or cat["cid"] == 5072:
                tags.append("預告")
            if "修正" in t:
                tags.append("修正")
            if "公告" in t:
                tags.append("公告")

            all_items.append(make_item(
                source="tfda",
                source_label="食藥署",
                source_color="emerald",
                title=row["title"],
                url=row["url"],
                date=row["date"],
                summary=summary,
                tags=tags,
            ))
    return all_items


if __name__ == "__main__":
    import json
    items = crawl()
    print(f"\n共 {len(items)} 筆")
    print(json.dumps(items[:3], ensure_ascii=False, indent=2))
