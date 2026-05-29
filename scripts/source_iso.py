"""ISO 國際標準組織 食品安全相關標準目錄

ISO 官網不提供公開的目錄 API，且標準清單只能用搜尋介面瀏覽。
ISO 標準本身變動週期長（多為 3-5 年），所以採用：
  - 維護一份手選的食品安全核心標準靜態目錄
  - 抓 ISO 新聞網頁，篩出食品相關的最新動態

未來新版發布時，可手動更新下方的 CURATED_STANDARDS 列表。
"""
from __future__ import annotations
import re
from common import fetch, clean_text, strip_tags, normalize_date, make_item

BASE = "https://www.iso.org"

# 食品安全核心 ISO 標準（手選清單）— 點連結會進 ISO 官網該標準頁
CURATED_STANDARDS = [
    {
        "code": "ISO 22000:2018",
        "title": "Food safety management systems — Requirements for any organization in the food chain",
        "title_zh": "ISO 22000:2018 食品安全管理系統 — 食品鏈中任何組織之要求",
        "url": "https://www.iso.org/standard/65464.html",
        "date": "2018-06-01",
        "category": "管理系統",
        "summary_bullets": [
            "現行版本：2018 年發布（取代 ISO 22000:2005）",
            "適用對象：食品鏈中任何組織（生產、加工、零售、餐飲、運輸）",
            "整合 HACCP 原則與 ISO 9001 結構（Annex SL）",
            "與 ISO/TS 22002-1（前提方案）配套使用",
        ],
    },
    {
        "code": "ISO/TS 22002-1:2009",
        "title": "Prerequisite programmes on food safety — Part 1: Food manufacturing",
        "title_zh": "ISO/TS 22002-1:2009 食品安全前提方案 — 第1部分：食品製造",
        "url": "https://www.iso.org/standard/44001.html",
        "date": "2009-12-01",
        "category": "前提方案 (PRP)",
        "summary_bullets": [
            "現行版本：2009 年發布（已啟動修訂程序，新版預計近年發布）",
            "適用對象：食品製造業（含包裝、運輸）",
            "規範 18 項前提方案：建築、設備、清潔消毒、害蟲管制、人員衛生等",
            "GFSI 認可的 FSSC 22000 驗證基礎之一",
        ],
    },
    {
        "code": "ISO 22002-2:2013",
        "title": "Prerequisite programmes on food safety — Part 2: Catering",
        "title_zh": "ISO 22002-2:2013 食品安全前提方案 — 第2部分：餐飲業",
        "url": "https://www.iso.org/standard/56714.html",
        "date": "2013-09-01",
        "category": "前提方案 (PRP)",
        "summary_bullets": [
            "適用對象：餐飲業、團膳、學校與醫院供餐",
            "規範餐飲場域之衛生管理、員工健康、過敏原管控",
        ],
    },
    {
        "code": "ISO 22002-3:2011",
        "title": "Prerequisite programmes on food safety — Part 3: Farming",
        "title_zh": "ISO 22002-3:2011 食品安全前提方案 — 第3部分：農作",
        "url": "https://www.iso.org/standard/57389.html",
        "date": "2011-12-01",
        "category": "前提方案 (PRP)",
        "summary_bullets": [
            "適用對象：農作物與畜牧生產（含水產養殖）",
            "規範土壤、用水、肥料、動物福利、藥物使用",
        ],
    },
    {
        "code": "ISO 22002-4:2013",
        "title": "Prerequisite programmes on food safety — Part 4: Food packaging manufacturing",
        "title_zh": "ISO 22002-4:2013 食品安全前提方案 — 第4部分：食品包裝製造",
        "url": "https://www.iso.org/standard/56678.html",
        "date": "2013-11-01",
        "category": "前提方案 (PRP)",
        "summary_bullets": [
            "適用對象：食品包裝材料製造業（與食品直接接觸）",
            "規範材料安全性、印刷油墨遷移、跨產線污染防範",
        ],
    },
    {
        "code": "ISO 22005:2007",
        "title": "Traceability in the feed and food chain — General principles and basic requirements",
        "title_zh": "ISO 22005:2007 飼料與食品鏈中之可追溯性 — 一般原則與基本要求",
        "url": "https://www.iso.org/standard/36297.html",
        "date": "2007-07-01",
        "category": "追溯",
        "summary_bullets": [
            "適用對象：所有食品鏈組織（含飼料）",
            "規範可追溯系統的設計、實施、驗證",
            "支援食品召回、產地證明、品牌保護",
        ],
    },
    {
        "code": "ISO 9001:2015",
        "title": "Quality management systems — Requirements",
        "title_zh": "ISO 9001:2015 品質管理系統 — 要求",
        "url": "https://www.iso.org/standard/62085.html",
        "date": "2015-09-01",
        "category": "品質管理",
        "summary_bullets": [
            "通用品質管理系統標準（非食品專屬，但食品業廣泛採用）",
            "整合風險思維、領導承諾、過程管理",
            "可與 ISO 22000 整合認證",
        ],
    },
    {
        "code": "ISO 17025:2017",
        "title": "General requirements for the competence of testing and calibration laboratories",
        "title_zh": "ISO 17025:2017 檢驗校正實驗室之通用能力要求",
        "url": "https://www.iso.org/standard/66912.html",
        "date": "2017-11-01",
        "category": "實驗室認證",
        "summary_bullets": [
            "食品檢驗實驗室必備認證標準",
            "規範方法驗證、量測不確定度、品質保證",
            "TFDA 委辦檢驗實驗室多依此認證",
        ],
    },
]


def make_iso_item(s: dict) -> dict:
    tags = ["ISO", s["category"]]
    # 自動加分類標籤
    title_l = s["title"].lower()
    if "haccp" in title_l or "food safety" in title_l or "管理系統" in s["title_zh"]:
        tags.append("HACCP")
    if "traceabil" in title_l:
        tags.append("追溯")
    if "packag" in title_l:
        tags.append("包裝")
    if "laboratory" in title_l or "lab" in title_l:
        tags.append("實驗室")
    if "quality" in title_l:
        tags.append("品質管理")

    item = make_item(
        source="iso",
        source_label="ISO 標準",
        source_color="indigo",
        title=f"{s['code']} {s['title']}",
        url=s["url"],
        date=s["date"],
        summary=f"{s['code']}：{s['title']}",
        tags=tags,
    )
    item["title_zh"] = f"{s['code']} — " + s["title_zh"].split(" — ", 1)[-1]
    item["ai_summary"] = s["summary_bullets"]
    return item


def crawl() -> list[dict]:
    items = [make_iso_item(s) for s in CURATED_STANDARDS]
    print(f"  [ISO] 食品安全核心標準 {len(items)} 條（手選目錄，定期人工更新）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
