"""馬來西亞 食品安全與管理目錄

馬來西亞食品安全主管機關 KKM (Kementerian Kesihatan Malaysia / Ministry of Health)
其子部門：
  • BKKM (Bahagian Keselamatan dan Kualiti Makanan / Food Safety and Quality Division)
  • FSQ Portal: hq.moh.gov.my/fsq

KKM 網站是 JS-rendered 的 SPA，無法穩定爬取。
改採「手選核心目錄」模式：列出主要法規 + 管理單位網址，定期人工更新。
"""
from __future__ import annotations
from common import make_item


# 馬來西亞核心食品法規與管理單位
CURATED_ITEMS = [
    {
        "title": "Food Act 1983 (Akta Makanan 1983)",
        "title_zh": "馬來西亞食品法 1983（Akta Makanan 1983）",
        "url": "https://lom.agc.gov.my/act-view.php?type=updated&act=281",
        "date": "1983-01-01",
        "category": "基本法",
        "bullets": [
            "馬來西亞食品安全的基本母法（Akta 281）",
            "規範食品製造、進口、出口、販售、廣告",
            "下位法規包括 Food Regulations 1985 與多項通告（Pekeliling）",
            "主管機關：衛生部 (KKM)",
        ],
    },
    {
        "title": "Food Regulations 1985 (Peraturan-Peraturan Makanan 1985)",
        "title_zh": "馬來西亞食品條例 1985（Peraturan-Peraturan Makanan 1985）",
        "url": "https://hq.moh.gov.my/fsq/peraturan-makanan-1985",
        "date": "1985-10-01",
        "category": "條例",
        "bullets": [
            "依 Food Act 1983 訂定的細則",
            "規範食品添加物、污染物、農藥殘留、標示、營養標示",
            "經多次修訂，最新修訂為 Amendment 2024",
            "輸馬業者必備合規參考",
        ],
    },
    {
        "title": "Food Hygiene Regulations 2009 (Peraturan-Peraturan Kebersihan Makanan 2009)",
        "title_zh": "馬來西亞食品衛生條例 2009",
        "url": "https://lom.agc.gov.my/ilims/upload/portal/akta/outputp/PUA_20090804_FOOD%20HYGIENE%20REGULATIONS%202009.pdf",
        "date": "2009-08-04",
        "category": "衛生條例",
        "bullets": [
            "規範食品業者的場所、人員衛生、加工流程",
            "等同台灣的「食品良好衛生規範準則 (GHP)」",
            "覆蓋餐飲業、製造業、零售",
            "強制要求高風險業者申請執照",
        ],
    },
    {
        "title": "MyHACCP / MeSTI 認證計畫",
        "title_zh": "MyHACCP / MeSTI 食品安全認證",
        "url": "https://hq.moh.gov.my/fsq/mesti",
        "date": "2014-01-01",
        "category": "HACCP",
        "bullets": [
            "MyHACCP：完整 HACCP 認證（適合中大型食品業）",
            "MeSTI（Makanan Selamat Tanggungjawab Industri）：簡化版，適合中小型業者",
            "兩者皆由 KKM 食品安全與品質部門核發",
            "等同台灣 HACCP 與食安監測自主管理",
        ],
    },
    {
        "title": "JAKIM Halal Certification (Sijil Halal Malaysia)",
        "title_zh": "JAKIM 馬來西亞清真認證",
        "url": "https://www.halal.gov.my/",
        "date": "1974-01-01",
        "category": "清真",
        "bullets": [
            "JAKIM (Jabatan Kemajuan Islam Malaysia) 主管的清真認證",
            "馬來西亞 Halal 認證是全球最權威的之一",
            "輸馬食品若涉清真標示，須取得 JAKIM 認證或承認的等同認證",
            "台灣業者可透過 MUI（印尼）或 IDCP（菲律賓）做為 JAKIM 承認的替代",
        ],
    },
    {
        "title": "FoSIM — Food Safety Information System of Malaysia",
        "title_zh": "FoSIM 馬來西亞食品安全資訊系統",
        "url": "https://fosim.moh.gov.my/",
        "date": "2009-01-01",
        "category": "進出口",
        "bullets": [
            "馬來西亞食品進口必經的線上系統",
            "輸馬食品須事前透過 FoSIM Import 模組申報",
            "整合與 Customs 系統的資料",
            "業者需註冊 FoSIM 帳號才能申報",
        ],
    },
    {
        "title": "Pelan Tindakan Keselamatan Makanan Kebangsaan 2024-2030",
        "title_zh": "馬來西亞國家食品安全行動計畫 2024-2030",
        "url": "https://hq.moh.gov.my/fsq/pelan-tindakan-keselamatan-makanan-kebangsaan-20102020",
        "date": "2024-01-01",
        "category": "政策",
        "bullets": [
            "馬國最新 6 年食安政策框架",
            "目標：強化監測、進口管制、HACCP 普及、消費者教育",
            "對輸馬業者：將見更嚴格的審查週期與抽驗頻率",
        ],
    },
    {
        "title": "BKKM Sub-Standard Food Alerts (Amaran Produk Substandard)",
        "title_zh": "馬來西亞食品警報入口",
        "url": "https://hq.moh.gov.my/fsq/amaran-produk-substandard/",
        "date": "2026-01-01",
        "category": "食品警報",
        "bullets": [
            "馬來西亞食品警報與不合格產品公告入口頁",
            "包含不安全食品、不合格添加物、未標示過敏原等",
            "對應台灣食藥署「食品衛生安全相關訊息」",
            "建議定期人工查訪此頁面，KKM 網站不提供 RSS",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_ITEMS:
        tags = ["馬來西亞", s["category"]]
        if "HACCP" in s["title"]:
            tags.append("HACCP")
        if "Halal" in s["title"]:
            tags.append("清真")
        if "進出口" in s["category"]:
            tags.append("進出口")

        item = make_item(
            source="my_kkm",
            source_label="馬來西亞 KKM",
            source_color="yellow",
            title=s["title"],
            url=s["url"],
            date=s["date"],
            summary=s["title_zh"],
            tags=tags,
        )
        item["title_zh"] = s["title_zh"]
        item["ai_summary"] = s["bullets"]
        items.append(item)

    print(f"  [MY KKM] 馬來西亞食安核心目錄 {len(items)} 條（手選，定期人工更新）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
