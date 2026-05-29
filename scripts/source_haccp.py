"""HACCP 認證 — 各國 HACCP 認證單位與標準（手選目錄）

HACCP 是方法學不是組織，各國各有認證主管機關與計畫名稱。
這份目錄列出各國家的 HACCP 認證單位入口。
"""
from __future__ import annotations
from common import make_item


CURATED_ENTRIES = [
    # 台灣
    {
        "country": "台灣",
        "title": "台灣 食品安全管制系統準則 (HACCP)",
        "title_zh": "台灣 食品安全管制系統準則（HACCP）",
        "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0040036",
        "date": "2024-08-01",
        "bullets": [
            "依食安法第 8 條訂定，強制特定業別實施",
            "適用業別：水產加工、肉類加工、餐盒、即食調理、乳品等",
            "由衛福部食藥署主管",
            "驗證機構：認證實驗室審查，發給「食品安全管制系統認證書」",
        ],
    },
    {
        "country": "台灣",
        "title": "台灣 CAS 優良農產品認證",
        "title_zh": "台灣 CAS 優良農產品認證",
        "url": "https://www.cas.org.tw/",
        "date": "2025-01-01",
        "bullets": [
            "農業部主管的台灣本土認證標章",
            "涵蓋 肉品、水產、冷凍食品、米、蔬果、有機、林產品 等 14 大類",
            "強制要求業者實施 HACCP 或同等品質管理",
            "驗證機構：財團法人台灣優良農產品發展協會",
        ],
    },
    {
        "country": "台灣",
        "title": "台灣 TQF 食品 GMP 認證",
        "title_zh": "台灣 TQF 食品 GMP 認證",
        "url": "https://www.tqf.org.tw/",
        "date": "2025-01-01",
        "bullets": [
            "由台灣食品產業協會（TQF）主管的自主管理認證",
            "原 GMP 認證 → 改為 TQF（Taiwan Quality Food）",
            "涵蓋食品製造業 GMP、HACCP、產品檢驗",
            "整合 ISO 22000、FSSC 22000",
        ],
    },
    # 美國
    {
        "country": "美國",
        "title": "US FDA Seafood HACCP Regulation",
        "title_zh": "美國 海鮮 HACCP 法規（21 CFR Part 123）",
        "url": "https://www.fda.gov/food/hazard-analysis-critical-control-point-haccp/seafood-haccp",
        "date": "2022-01-01",
        "bullets": [
            "美國強制要求海鮮加工業者實施 HACCP",
            "依 21 CFR Part 123 規範",
            "適用：美國海鮮加工 + 海鮮進口商",
            "對台灣輸美海鮮業者尤其重要",
        ],
    },
    {
        "country": "美國",
        "title": "US FDA Juice HACCP Regulation",
        "title_zh": "美國 果汁 HACCP 法規（21 CFR Part 120）",
        "url": "https://www.fda.gov/food/hazard-analysis-critical-control-point-haccp/juice-haccp",
        "date": "2022-01-01",
        "bullets": [
            "美國強制要求果汁業者實施 HACCP",
            "依 21 CFR Part 120 規範",
            "包含加工殺菌、酸化、無菌包裝程序",
        ],
    },
    {
        "country": "美國",
        "title": "USDA FSIS Meat & Poultry HACCP",
        "title_zh": "美國 USDA FSIS 肉類禽類 HACCP",
        "url": "https://www.fsis.usda.gov/policy/fsis-directives/5000.1",
        "date": "2025-01-01",
        "bullets": [
            "美國農業部 FSIS（食品安全檢驗局）對肉類禽類的 HACCP 要求",
            "9 CFR Part 417 規範",
            "適用屠宰場、肉品加工廠",
            "與 FDA HACCP 並行（FDA 管魚與其他食品、FSIS 管肉禽蛋）",
        ],
    },
    # 歐盟
    {
        "country": "歐盟",
        "title": "EU Regulation 852/2004 Hygiene of Foodstuffs",
        "title_zh": "歐盟 食品衛生規範（852/2004）含 HACCP",
        "url": "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32004R0852",
        "date": "2004-04-29",
        "bullets": [
            "歐盟所有食品業者強制實施 HACCP 原則",
            "屬「衛生包」（Hygiene Package）之一",
            "與 853/2004（動物源食品）、854/2004（官方控制）配套",
            "輸歐業者須符合此規範",
        ],
    },
    # 澳洲
    {
        "country": "澳洲",
        "title": "AU SQF (Safe Quality Food) Program",
        "title_zh": "澳洲 SQF 食品安全品質認證",
        "url": "https://www.sqfi.com/",
        "date": "2025-01-01",
        "bullets": [
            "起源於澳洲，現由美國 FMI 維護",
            "GFSI 認可的食品安全認證之一",
            "涵蓋初級生產、加工、儲存運輸、餐飲",
            "整合 HACCP + ISO 9001 + 食品防護",
        ],
    },
    {
        "country": "澳洲",
        "title": "AU FSANZ Code of Practice for HACCP",
        "title_zh": "澳洲 FSANZ HACCP 實務規範",
        "url": "https://www.foodstandards.gov.au/sites/default/files/publications/Documents/Safe%20Food%20Australia%20-%20updated%20August%202016.pdf",
        "date": "2016-08-01",
        "bullets": [
            "FSANZ 對食品安全標準 3.2.1 的詮釋指引",
            "食品業者依此實施食品安全計畫（FSP）",
            "FSP 與 HACCP 內容類似但澳洲法規用語",
        ],
    },
    # 日本
    {
        "country": "日本",
        "title": "JP 食品衛生法 HACCP 義務化",
        "title_zh": "日本 食品衛生法 HACCP 義務化",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000179028.html",
        "date": "2021-06-01",
        "bullets": [
            "2021 年 6 月起日本全面強制食品業者實施 HACCP",
            "分大型業者：完整 HACCP（依 Codex 標準）",
            "小型業者：HACCP 思維下的衛生管理（簡化版）",
            "由 厚生労働省 主管",
        ],
    },
    # 香港
    {
        "country": "香港",
        "title": "HK CFS 食物業者良好衛生規範 (GHP)",
        "title_zh": "香港 食物業者良好衛生規範",
        "url": "https://www.cfs.gov.hk/tc_chi/food_leg/food_leg_Hygiene.html",
        "date": "2025-01-01",
        "bullets": [
            "香港對食物業者的基本衛生規範",
            "雖未強制 HACCP，但 CFS 鼓勵業者導入",
            "酒店、大型餐廳多自主實施 HACCP",
            "由食物安全中心（CFS）主管",
        ],
    },
    # 馬來西亞
    {
        "country": "馬來西亞",
        "title": "MY MyHACCP / MeSTI 認證",
        "title_zh": "馬來西亞 MyHACCP / MeSTI 認證",
        "url": "https://hq.moh.gov.my/fsq/mesti",
        "date": "2014-01-01",
        "bullets": [
            "MyHACCP：完整 HACCP（中大型業者）",
            "MeSTI：簡化版 HACCP（中小型業者）",
            "由 KKM 食品安全與品質部門核發",
            "等同台灣 HACCP 認證 + 食安監測",
        ],
    },
    # 國際
    {
        "country": "國際",
        "title": "GFSI (Global Food Safety Initiative) Recognized Schemes",
        "title_zh": "GFSI 全球食品安全倡議認可方案",
        "url": "https://mygfsi.com/how-to-implement/recognition/recognised-cpos/",
        "date": "2026-01-01",
        "bullets": [
            "GFSI 是國際食品安全認證的整合平台（不發認證）",
            "認可方案：FSSC 22000、SQF、BRCGS、IFS、Global GAP 等",
            "輸出至國際大型超市鏈通常被要求 GFSI 認可方案之一",
            "業者可挑選一個 GFSI 方案做為國際通行的食安認證",
        ],
    },
    {
        "country": "國際",
        "title": "FSSC 22000",
        "title_zh": "FSSC 22000 國際食品安全認證系統",
        "url": "https://www.fssc.com/",
        "date": "2026-01-01",
        "bullets": [
            "整合 ISO 22000 + ISO/TS 22002-1（前提方案）+ 額外 FSSC 要求",
            "GFSI 認可的食品安全認證",
            "全球超過 35,000 家業者已認證",
            "適合食品製造業、包裝業",
        ],
    },
    {
        "country": "國際",
        "title": "Codex HACCP General Principles",
        "title_zh": "Codex HACCP 一般原則",
        "url": "https://www.fao.org/fao-who-codexalimentarius/codex-texts/codes-of-practice/en/",
        "date": "2020-01-01",
        "bullets": [
            "Codex Alimentarius 的 HACCP 一般原則文件",
            "全球 HACCP 標準的源頭",
            "各國 HACCP 規範皆參考此文件",
            "免費下載 PDF",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_ENTRIES:
        tags = ["HACCP", s["country"]]
        if "Halal" in s["title"] or "清真" in s["title"]:
            tags.append("清真")
        if "SQF" in s["title"]:
            tags.append("SQF")
        if "FSSC" in s["title"]:
            tags.append("FSSC")
        if "GFSI" in s["title"]:
            tags.append("GFSI")

        item = make_item(
            source="haccp",
            source_label="HACCP 認證",
            source_color="lime",
            title=s["title"],
            url=s["url"],
            date=s["date"],
            summary=s["title_zh"],
            tags=tags,
        )
        item["title_zh"] = s["title_zh"]
        item["ai_summary"] = s["bullets"]
        item["country"] = s["country"]
        items.append(item)
    print(f"  [HACCP] 各國 HACCP 認證入口 {len(items)} 條（手選目錄）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
