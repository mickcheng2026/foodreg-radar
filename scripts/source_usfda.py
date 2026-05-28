"""美國 FDA 食品安全相關新聞爬蟲

來源：FDA Food 首頁 https://www.fda.gov/food (列表式)
較不穩定，採 best-effort 策略。
"""
from __future__ import annotations
import re
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.fda.gov"
# 只接受這幾個專用列表頁，內容才是真的新聞而不是導覽
LIST_URLS = [
    "https://www.fda.gov/news-events/press-announcements",
    "https://www.fda.gov/food/cfsan-constituent-updates",
    "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts",
]

# 真新聞的 URL 特徵
NEWS_URL_PATTERNS = [
    r"/news-events/press-announcements/",
    r"/food/cfsan-constituent-updates/",
    r"/safety/recalls-market-withdrawals-safety-alerts/",
    r"/food/recalls-outbreaks-emergencies/",
]


def crawl() -> list[dict]:
    items: list[dict] = []
    seen_urls: set[str] = set()

    for list_url in LIST_URLS:
        try:
            html = fetch(list_url)
        except Exception as e:
            print(f"  [USFDA] {list_url} 失敗: {e}")
            continue

        # 任何 anchor，但 URL 必須符合「真新聞」pattern
        link_pattern = re.compile(
            r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE,
        )
        for m in link_pattern.finditer(html):
            href = m.group(1)
            if href.startswith("/"):
                url = BASE + href
            elif href.startswith("http") and "fda.gov" in href:
                url = href
            else:
                continue

            # 必須是「條目」級別的 URL（pattern 後面要有實際標題 slug，不是空白）
            is_news = False
            for pat in NEWS_URL_PATTERNS:
                if re.search(pat + r"[A-Za-z0-9_-]{8,}", url):
                    is_news = True
                    break
            if not is_news:
                continue

            if url in seen_urls:
                continue

            title = clean_text(strip_tags(m.group(2)))
            if not title or len(title) < 15 or title.lower() in ("read more", "see more"):
                continue

            seen_urls.add(url)

            # 食品相關判斷（標題或 URL）
            food_kw = ["food", "nutrition", "recall", "labeling", "allergen", "additive",
                       "contamin", "pesticide", "ingredient", "dietary", "salmonella",
                       "e. coli", "listeria", "outbreak", "tomato", "lettuce", "produce",
                       "meat", "poultry", "dairy", "infant", "formula", "beverage"]
            text_check = (title + " " + url).lower()
            food_relevant = any(k in text_check for k in food_kw)

            # 來自 /food/... 或 /safety/...recalls 預設都算食品相關
            if "/food/" in url or "/recalls" in url:
                food_relevant = True

            if not food_relevant:
                continue

            tags = ["US FDA"]
            if "recall" in text_check:
                tags.append("召回")
            if "/press-announcements/" in url:
                tags.append("新聞發布")

            items.append(make_item(
                source="usfda",
                source_label="US FDA",
                source_color="blue",
                title=title,
                url=url,
                date=None,
                summary="",
                tags=tags,
            ))

            if len(items) >= 20:
                break

    print(f"  [USFDA] 找到 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:5], ensure_ascii=False, indent=2))
