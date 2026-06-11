"""食安事件（各國）爬蟲 — 來源：Food Safety News（全球食安新聞）

Food Safety News (foodsafetynews.com) 是涵蓋全球的食安新聞站，每日報導
各國的食品中毒、病原菌爆發、跨國回收、污染事件等。本爬蟲讀取其 RSS（主 feed
+ 數個 tag feed），彙整成「食安事件」分類。

設計：
- 純 stdlib（urllib + xml.etree），無需 API 金鑰
- 每筆 item 從 RSS category 與標題推斷「國家/地區」與「病原/危害類型」標籤
- 因為 build_data 以 URL 去重並保留歷史，每天累積 → 涵蓋會隨時間變廣
- 產出結構化中文 ai_summary（事件 / 地區 / 病原 / 來源 / 日期）
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from common import fetch, clean_text, make_item, normalize_date

# 主 feed + 幾個 tag feed（年份 tag 每年要更新；抓不到的會自動略過）
FEEDS = [
    "https://www.foodsafetynews.com/feed/",
    "https://www.foodsafetynews.com/tag/2026-outbreaks/feed/",
    "https://www.foodsafetynews.com/tag/2025-outbreaks/feed/",
    "https://www.foodsafetynews.com/tag/recalls/feed/",
    "https://www.foodsafetynews.com/tag/recall/feed/",
    "https://www.foodsafetynews.com/tag/salmonella/feed/",
    "https://www.foodsafetynews.com/tag/listeria/feed/",
    "https://www.foodsafetynews.com/tag/e-coli/feed/",
]

# 國家/地區推斷（標題或 category 命中 → 對應到前端國家分類）
COUNTRY_PATTERNS = [
    # 歐盟先判（ECDC/EFSA 等含 CDC/FDA 子字串，需先攔下避免誤判美國）
    (r"\bEU\b|Europe|European|\bECDC\b|\bEFSA\b|Germany|France|Italy|Spain|Netherlands|Belgium|Sweden|Denmark|Ireland|Poland", "歐盟"),
    (r"\bU\.?S\.?\b|United States|America|\bFDA\b|\bUSDA\b|\bCDC\b|\b(?:California|Texas|Florida|New York|Ohio|Michigan|Illinois|Wisconsin)\b", "美國"),
    (r"\bUK\b|United Kingdom|Britain|British|England|Scotland|Wales|\bFSA\b", "英國"),
    (r"Canada|Canadian|CFIA", "加拿大"),
    (r"Australia|Australian|FSANZ|New Zealand", "澳洲"),
    (r"Japan|Japanese", "日本"),
    (r"Hong Kong", "香港"),
    (r"Taiwan|Taiwanese", "台灣"),
    (r"China|Chinese|Korea|Korean|Vietnam|Thailand|India|Indonesia|Malaysia|Singapore|Philippines", "亞洲其他"),
]

# 病原 / 危害類型標籤
HAZARD_PATTERNS = [
    (r"salmonell", "沙門氏菌"),
    (r"listeri", "李斯特菌"),
    (r"e\.?\s*coli|escherichia|STEC|O157", "大腸桿菌"),
    (r"botulism|clostridium", "肉毒桿菌"),
    (r"norovirus", "諾羅病毒"),
    (r"hepatitis a", "A型肝炎"),
    (r"campylobacter", "彎曲桿菌"),
    (r"cronobacter", "阪崎腸桿菌"),
    (r"aflatoxin|mycotoxin|ochratoxin", "黴菌毒素"),
    (r"undeclared|allergen", "未標示過敏原"),
    (r"foreign (?:matter|material|object)|metal|plastic|glass", "異物"),
    (r"recall", "回收"),
    (r"outbreak", "疫情爆發"),
    (r"poisoning|illness", "食品中毒"),
]


def _detect(patterns, text, default=None):
    for pat, label in patterns:
        if re.search(pat, text, re.I):
            return label
    return default


def _all_hazards(text):
    out = []
    for pat, label in HAZARD_PATTERNS:
        if re.search(pat, text, re.I) and label not in out:
            out.append(label)
    return out


def crawl() -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    for feed in FEEDS:
        try:
            raw = fetch(feed, timeout=20)
            root = ET.fromstring(raw)
        except Exception as e:
            print(f"  [食安事件] {feed.split('/tag/')[-1].rstrip('/feed/') or 'main'} 略過: {str(e)[:50]}")
            continue

        for node in root.findall(".//item"):
            link = (node.findtext("link") or "").strip()
            title = clean_text(node.findtext("title") or "")
            if not link or not title or link in seen:
                continue
            seen.add(link)

            date = normalize_date(node.findtext("pubDate") or "")
            cats = [c.text or "" for c in node.findall("category")]
            desc = clean_text(re.sub(r"<[^>]+>", " ", node.findtext("description") or ""))[:300]

            blob = title + " " + " ".join(cats) + " " + desc
            country = _detect(COUNTRY_PATTERNS, blob, default="國際")
            hazards = _all_hazards(blob)

            tags = ["食安事件"] + hazards
            # 把可讀的 category（病原/主題）也加入，去重、限量
            for c in cats:
                c = clean_text(c)
                if c and len(c) <= 16 and c not in tags and not re.match(r"\d{4}", c):
                    tags.append(c)
            tags = tags[:8]

            ai = [f"性質：食安事件 — {country}"]
            if hazards:
                ai.append("病原／危害：" + "、".join(hazards[:4]))
            ai.append(f"事件：{title[:90]}")
            if desc and len(desc) >= 10:
                ai.append("摘要：" + desc[:90])
            if date:
                ai.append(f"日期：{date}")
            ai.append("來源：Food Safety News（全球食安新聞）")

            item = make_item(
                source="food_incidents",
                source_label="食安事件",
                source_color="red",
                title=title,
                url=link,
                date=date,
                summary=desc or title,
                tags=tags,
            )
            item["country"] = country
            item["ai_summary"] = ai
            items.append(item)

    print(f"  [食安事件] Food Safety News 全球食安事件 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    out = crawl()
    print(json.dumps(out[:4], ensure_ascii=False, indent=2))
