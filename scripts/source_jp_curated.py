"""日本 食品安全核心法規與管理單位（手選目錄）

補強 source_jp_fsc 的即時公告，加上日本食品安全的基礎法規與管理單位入口。
日本 MHLW 網站結構複雜、頻繁改版，靜態目錄較穩定。
"""
from __future__ import annotations
from common import make_item


CURATED_ITEMS = [
    {
        "title": "Food Sanitation Act (食品衛生法)",
        "title_zh": "日本 食品衛生法",
        "url": "https://www.japaneselawtranslation.go.jp/en/laws/view/3884",
        "date": "2024-06-01",
        "bullets": [
            "日本食品安全的母法（昭和 22 年法律第 233 號）",
            "規範食品製造、販賣、進口、輸出",
            "2018 年大修改後納入 HACCP 強制義務化",
            "下位法規包括食品衛生法施行令、施行規則",
        ],
    },
    {
        "title": "JP Food Safety Basic Act (食品安全基本法)",
        "title_zh": "日本 食品安全基本法",
        "url": "https://www.japaneselawtranslation.go.jp/en/laws/view/4046",
        "date": "2003-05-23",
        "bullets": [
            "日本食品安全的總體框架法",
            "成立食品安全委員会 (FSC) 進行風險評估",
            "FSC 與 MHLW、農林水産省（MAFF）分工：FSC 評估、MHLW/MAFF 管理",
        ],
    },
    {
        "title": "JP MHLW 食品安全情報",
        "title_zh": "日本 厚生労働省 食品安全情報入口",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/index.html",
        "date": "2026-01-01",
        "bullets": [
            "日本厚生労働省 食品安全主入口",
            "涵蓋食品衛生、食中毒、輸入食品、HACCP",
            "輸日食品業者主要查詢入口",
        ],
    },
    {
        "title": "JP 食品中の農薬等のポジティブリスト制度",
        "title_zh": "日本 食品中農藥等正面表列制度",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/zanryu/index.html",
        "date": "2026-01-01",
        "bullets": [
            "日本對食品中農藥、動物用藥、飼料添加物的正面表列制度",
            "未列名或超量者不得輸入販售（一律 0.01 ppm 限量）",
            "輸日業者必須事前確認對應殘留標準",
            "由 MHLW 主管，FSC 評估",
        ],
    },
    {
        "title": "JP Food Labelling Act (食品表示法)",
        "title_zh": "日本 食品標示法",
        "url": "https://www.caa.go.jp/policies/policy/food_labeling/",
        "date": "2024-04-01",
        "bullets": [
            "由消費者廳 (CAA) 主管",
            "整合過去食品衛生法、JAS 法、健康増進法中的標示規定",
            "強制要求營養標示（自 2020 年起）",
            "輸日預包裝食品必備合規參考",
        ],
    },
    {
        "title": "JP MAFF 輸入植物検疫",
        "title_zh": "日本 農林水産省 植物檢疫",
        "url": "https://www.maff.go.jp/pps/j/import/",
        "date": "2026-01-01",
        "bullets": [
            "日本農林水產省（MAFF）植物防疫所",
            "輸日植物、果蔬、種子的檢疫入口",
            "查詢檢疫條件、禁止/限制品項清單",
            "輸日蔬果、農產品業者必查",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_ITEMS:
        tags = ["法規", "日本"]
        if "HACCP" in s["title"] or "HACCP" in str(s.get("bullets", "")):
            tags.append("HACCP")
        if "輸入" in s["title"] or "農林" in s["title"]:
            tags.append("輸入")
        if "標示" in s["title_zh"]:
            tags.append("標示")
        if "農藥" in s["title_zh"]:
            tags.append("農藥殘留")

        item = make_item(
            source="jp_curated",
            source_label="日本 法規目錄",
            source_color="rose",
            title=s["title"],
            url=s["url"],
            date=s["date"],
            summary=s["title_zh"],
            tags=tags,
        )
        item["title_zh"] = s["title_zh"]
        item["ai_summary"] = s["bullets"]
        item["country"] = "日本"
        items.append(item)
    print(f"  [JP Curated] 日本食安核心法規 {len(items)} 條（手選目錄）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
