"""食安事件（各國）爬蟲 — 全球食安新聞 + 各國新聞事件

兩類來源（皆 RSS、純 stdlib、無需金鑰）：
1. Food Safety News — 全球食安專業新聞站
2. Google News RSS — 用關鍵字搜各國新聞，補抓「沒有官方公告、只有新聞」的食安事件
   - 英文：全球 outbreak / recall
   - 中文：台灣／華語圈 食品中毒、回收、污染（標題本身即中文，免翻譯）

設計：
- 每筆推斷國家/地區與病原標籤，產出結構化中文 ai_summary
- 以 URL + 標題正規化去重（跨來源同篇只留一筆）
- Google News 結果以食安關鍵字過濾，濾掉政策/活動等雜訊
- build_data 以 URL 去重保留歷史 → 涵蓋隨每日 cron 累積
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from common import fetch, clean_text, make_item, normalize_date

# 來源清單：kind=fsn 全收；kind=gnews 需通過食安關鍵字過濾
FEEDS = [
    # Food Safety News（美國媒體；未偵測到他國時預設美國）
    {"url": "https://www.foodsafetynews.com/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/2026-outbreaks/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/2025-outbreaks/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/recalls/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/salmonella/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/listeria/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/e-coli/feed/", "kind": "fsn", "default": "美國"},
    # Google News — 英文（gl=US，未偵測到他國時預設美國）
    {"url": "https://news.google.com/rss/search?q=food%20safety%20outbreak%20OR%20recall%20OR%20contamination%20when:365d&hl=en-US&gl=US&ceid=US:en",
     "kind": "gnews", "default": "美國"},
    {"url": "https://news.google.com/rss/search?q=salmonella%20OR%20listeria%20OR%20%22e.%20coli%22%20outbreak%20when:365d&hl=en-US&gl=US&ceid=US:en",
     "kind": "gnews", "default": "美國"},
    # Google News — 中文（台灣／華語圈）食安事件
    {"url": "https://news.google.com/rss/search?q=%E9%A3%9F%E5%93%81%E4%B8%AD%E6%AF%92%20OR%20%E9%A3%9F%E5%AE%89%20OR%20%E9%A3%9F%E5%93%81%E5%9B%9E%E6%94%B6%20OR%20%E9%A3%9F%E5%93%81%E4%B8%8B%E6%9E%B6%20when:365d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
     "kind": "gnews", "default": "台灣"},
]

# 國家/地區推斷（含中英關鍵字；歐盟先於美國，避免 ECDC/EFSA 子字串誤判）
COUNTRY_PATTERNS = [
    (r"\bEU\b|Europe|European|\bECDC\b|\bEFSA\b|Germany|France|Italy|Spain|Netherlands|Belgium|Sweden|Denmark|Ireland|Poland|歐盟|歐洲|德國|法國|義大利|西班牙|荷蘭", "歐盟"),
    (r"\bU\.?S\.?\b|United States|America|\bFDA\b|\bUSDA\b|\bCDC\b|美國|加州|紐約", "美國"),
    (r"\bUK\b|United Kingdom|Britain|British|England|Scotland|Wales|\bFSA\b|英國", "英國"),
    (r"Canada|Canadian|CFIA|加拿大", "加拿大"),
    (r"Australia|Australian|FSANZ|New Zealand|澳洲|紐西蘭", "澳洲"),
    (r"Japan|Japanese|日本", "日本"),
    (r"Hong Kong|香港", "香港"),
    (r"Taiwan|Taiwanese|台灣|臺灣|台北|臺北|新北|桃園|台中|臺中|台南|臺南|高雄|新竹|彰化|宜蘭|花蓮|衛福部|食藥署|食藥署", "台灣"),
    (r"China|Chinese|中國|大陸|北京|上海|Korea|韓國|Vietnam|越南|Thailand|泰國|India|印度|Indonesia|Malaysia|馬來西亞|Singapore|新加坡|Philippines|菲律賓", "亞洲其他"),
    # 全球性／其他地區 → 國際（須在預設美國之前攔下，避免誤判）
    (r"\bWHO\b|World Health|\bFAO\b|United Nations|worldwide|globe|global(?:ly)?|multi-?country|multiple countries|several countries|cross-border|國際|全球|多國", "國際"),
    (r"Paraguay|Brazil|Brazilian|Mexico|Mexican|Argentina|Chile|Peru|Colombia|Africa|Nigeria|Kenya|Egypt|Cape Verde|Russia|Ukraine|Saudi|\bUAE\b|Dubai|Israel|Turkey|巴西|墨西哥|阿根廷|非洲|中東", "國際"),
]

HAZARD_PATTERNS = [
    (r"salmonell|沙門", "沙門氏菌"),
    (r"listeri|李斯特", "李斯特菌"),
    (r"e\.?\s*coli|escherichia|STEC|O157|大腸桿菌", "大腸桿菌"),
    (r"botulism|clostridium|肉毒", "肉毒桿菌"),
    (r"norovirus|諾羅", "諾羅病毒"),
    (r"hepatitis a|A型肝炎", "A型肝炎"),
    (r"campylobacter|彎曲桿菌", "彎曲桿菌"),
    (r"cronobacter|阪崎", "阪崎腸桿菌"),
    (r"aflatoxin|mycotoxin|ochratoxin|黃[麴曲]|黴菌毒素", "黴菌毒素"),
    (r"undeclared|allergen|過敏原|致敏", "未標示過敏原"),
    (r"foreign (?:matter|material|object)|metal|plastic|glass|異物|玻璃|金屬碎片", "異物"),
    (r"塑化劑|重金屬|鉛|鎘|砷|超標", "化學污染物"),
    (r"recall|回收|下架|召回", "回收"),
    (r"outbreak|疫情|爆發|群聚", "疫情爆發"),
    (r"poisoning|illness|中毒|食物中毒|食品中毒", "食品中毒"),
]

# Google News 相關性過濾：標題須命中食安事件關鍵字（濾掉政策/活動/標章等雜訊）
INCIDENT_KW = re.compile(
    r"outbreak|recall|salmonell|listeri|e\.?\s*coli|botulism|contamin|poison|illness|"
    r"hepatitis|norovirus|tainted|unsafe|adulterat|withdrawn|alert|"
    r"中毒|回收|下架|召回|污染|沙門|李斯特|大腸桿菌|肉毒|諾羅|黴菌|黃[麴曲]|"
    r"塑化劑|超標|不合格|黑心|過期|致癌|毒|異物|疫情|群聚", re.I)


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


def _norm_title(t: str) -> str:
    return re.sub(r"[\s\-–—|]+", "", (t or "").lower())[:60]


def crawl() -> list[dict]:
    items: list[dict] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for feed in FEEDS:
        try:
            root = ET.fromstring(fetch(feed["url"], timeout=20))
        except Exception as e:
            print(f"  [食安事件] 略過一個來源: {str(e)[:50]}")
            continue

        for node in root.findall(".//item"):
            link = (node.findtext("link") or "").strip()
            raw_title = clean_text(node.findtext("title") or "")
            if not link or not raw_title:
                continue

            # Google News 標題尾端常帶「 - 媒體名」，且來源在 <source>
            outlet = clean_text(node.findtext("source") or "")
            title = raw_title
            if feed["kind"] == "gnews" and outlet and title.endswith(outlet):
                title = title[: -len(outlet)].rstrip(" -–—|").strip()
            elif feed["kind"] == "gnews":
                title = re.sub(r"\s[-–—]\s[^-–—]{2,30}$", "", title).strip()

            # Google News：相關性過濾
            if feed["kind"] == "gnews" and not INCIDENT_KW.search(raw_title):
                continue

            nt = _norm_title(title)
            if link in seen_urls or (nt and nt in seen_titles):
                continue
            seen_urls.add(link)
            if nt:
                seen_titles.add(nt)

            date = normalize_date(node.findtext("pubDate") or "")
            cats = [c.text or "" for c in node.findall("category")]
            desc = clean_text(re.sub(r"<[^>]+>", " ", node.findtext("description") or ""))[:300]

            blob = title + " " + " ".join(cats) + " " + desc
            country = _detect(COUNTRY_PATTERNS, blob, default=feed["default"])
            hazards = _all_hazards(blob)

            tags = ["食安事件"] + hazards
            if outlet:
                tags.append(outlet)
            for c in cats:
                c = clean_text(c)
                if c and len(c) <= 16 and c not in tags and not re.match(r"\d{4}", c):
                    tags.append(c)
            tags = tags[:8]

            src_name = outlet or ("Food Safety News" if feed["kind"] == "fsn" else "新聞")
            ai = [f"性質：食安事件 — {country}"]
            if hazards:
                ai.append("病原／危害：" + "、".join(hazards[:4]))
            ai.append(f"事件：{title[:100]}")
            if date:
                ai.append(f"日期：{date}")
            ai.append(f"來源：{src_name}（新聞報導）")

            item = make_item(
                source="food_incidents",
                source_label="食安事件",
                source_color="red",
                title=title,
                url=link,
                date=date,
                summary=(desc or title)[:500],
                tags=tags,
            )
            item["country"] = country
            item["ai_summary"] = ai
            items.append(item)

    print(f"  [食安事件] 全球食安新聞 + 各國新聞事件 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    from collections import Counter
    out = crawl()
    print("國家:", dict(Counter(i["country"] for i in out)))
    print(json.dumps(out[:3], ensure_ascii=False, indent=2))
