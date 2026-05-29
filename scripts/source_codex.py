"""Codex Alimentarius (FAO/WHO 國際食品法典) 核心標準目錄

FAO 網站結構不穩定，改採手選核心標準目錄。
Codex 標準變動週期長（多年），靜態目錄合適。
"""
from __future__ import annotations
from common import make_item


CURATED_STANDARDS = [
    {
        "title": "CXS 1-1985 General Standard for the Labelling of Prepackaged Foods",
        "title_zh": "CXS 1-1985 預先包裝食品標示通則",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B1-1985%252FCXS_001e.pdf",
        "date": "2018-01-01",
        "bullets": [
            "全球預包裝食品標示通則",
            "規範產品名稱、成分、淨重、保存期限、製造商",
            "各國食品標示法規多以此為基礎",
            "輸出國際時必備合規參考",
        ],
    },
    {
        "title": "CXS 192-1995 General Standard for Food Additives",
        "title_zh": "CXS 192-1995 食品添加物通則",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B192-1995%252FCXS_192e.pdf",
        "date": "2024-01-01",
        "bullets": [
            "Codex 對食品添加物的綜合性標準",
            "規範各類食品中各種添加物的最大使用量",
            "持續更新，最新修訂為 2024",
            "與台灣食品添加物使用範圍標準對接",
        ],
    },
    {
        "title": "CXS 193-1995 General Standard for Contaminants and Toxins in Food and Feed",
        "title_zh": "CXS 193-1995 食品與飼料中污染物與毒素通則",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B193-1995%252FCXS_193e.pdf",
        "date": "2024-01-01",
        "bullets": [
            "Codex 污染物與毒素標準",
            "涵蓋鎘、鉛、汞、砷、黴菌毒素、丙烯醯胺等",
            "各國重金屬與污染物限量法規多參考此",
            "近期更新：嬰幼兒食品砷限量下修",
        ],
    },
    {
        "title": "CXC 1-1969 General Principles of Food Hygiene (含 HACCP 附錄)",
        "title_zh": "CXC 1-1969 食品衛生通則（含 HACCP 附錄）",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXC%2B1-1969%252FCXC_001e.pdf",
        "date": "2020-01-01",
        "bullets": [
            "全球 HACCP 標準的源頭",
            "規範食品衛生、HACCP 七大原則",
            "ISO 22000 與各國 HACCP 規範均參考此文件",
            "2020 年修訂，加強過敏原管理",
        ],
    },
    {
        "title": "CXS 234-1999 Recommended Methods of Analysis and Sampling",
        "title_zh": "CXS 234-1999 推薦分析與抽樣方法",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B234-1999%252FCXS_234e.pdf",
        "date": "2023-01-01",
        "bullets": [
            "各類食品的官方檢驗方法",
            "供各國檢驗實驗室參考",
            "與食品檢驗法規搭配使用",
        ],
    },
    {
        "title": "Codex Maximum Residue Limits (MRL) Database",
        "title_zh": "Codex 農藥殘留容許量資料庫",
        "url": "https://www.fao.org/fao-who-codexalimentarius/codex-texts/dbs/pestres/en/",
        "date": "2026-01-01",
        "bullets": [
            "全球農藥殘留容許量參考資料庫",
            "可查 5000+ 農藥 × 食品的 MRL",
            "持續更新，2 年一次大更新",
            "輸出業者可作為國際標準對照",
        ],
    },
    {
        "title": "CXC 53-2003 Code of Hygienic Practice for Fresh Fruits and Vegetables",
        "title_zh": "CXC 53-2003 新鮮蔬果衛生作業規範",
        "url": "https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXC%2B53-2003%252FCXC_053e.pdf",
        "date": "2022-01-01",
        "bullets": [
            "新鮮蔬果生產、處理、運輸衛生規範",
            "涵蓋初級生產到零售階段",
            "輸出蔬果業者必備合規參考",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_STANDARDS:
        tags = ["Codex", "國際標準"]
        if "Additives" in s["title"] or "添加物" in s["title_zh"]:
            tags.append("食品添加物")
        if "Contaminants" in s["title"] or "污染物" in s["title_zh"]:
            tags.append("污染物")
        if "HACCP" in s["title"] or "HACCP" in s["title_zh"]:
            tags.append("HACCP")
        if "Labelling" in s["title"] or "標示" in s["title_zh"]:
            tags.append("標示")
        if "MRL" in s["title"] or "農藥殘留" in s["title_zh"]:
            tags.append("農藥殘留")
        if "Hygiene" in s["title"] or "衛生" in s["title_zh"]:
            tags.append("衛生規範")

        item = make_item(
            source="codex",
            source_label="Codex",
            source_color="rose",
            title=s["title"],
            url=s["url"],
            date=s["date"],
            summary=s["title_zh"],
            tags=tags,
        )
        item["title_zh"] = s["title_zh"]
        item["ai_summary"] = s["bullets"]
        items.append(item)
    print(f"  [Codex] 國際食品法典核心標準 {len(items)} 條（手選目錄）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
