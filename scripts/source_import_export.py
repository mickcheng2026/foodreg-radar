"""進出口規範 — 各國食品進出口主管機關、申辦系統、特殊要求（手選目錄）

進出口資料多為法規、操作手冊與大量 PDF，無法以單一爬蟲處理。
這份目錄列出各國家「進口食品申辦入口」、「出口管制清單」、
與「特殊產品（肉品、水產、清真）」等專門要求，
作為衛生管理員與貿易商查詢起點。
"""
from __future__ import annotations
from common import make_item


# 各國家進出口主管機關與入口
CURATED_ENTRIES = [
    # === 台灣 ===
    {
        "country": "台灣",
        "title": "TW 食藥署 食品輸入查驗系統 (FRT)",
        "title_zh": "台灣 食品輸入查驗系統（FRT）",
        "url": "https://eservice.fda.gov.tw/FRTSearch/",
        "date": "2025-01-01",
        "bullets": [
            "輸台食品申辦的官方查驗系統",
            "可查詢輸入查驗應檢附文件、報驗義務人、查驗類別",
            "涵蓋食品、食品添加物、食品器具容器包裝",
            "業者申辦 / 查驗 / 簽審入口",
        ],
    },
    {
        "country": "台灣",
        "title": "TW 食品及相關產品輸入查驗辦法",
        "title_zh": "台灣 食品及相關產品輸入查驗辦法",
        "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0040107",
        "date": "2024-04-01",
        "bullets": [
            "食藥署輸入查驗的母法",
            "規範查驗類別（書面、抽驗、逐批、加強）",
            "適用範圍：食品、食品添加物、食品用洗潔劑、食品器具",
        ],
    },
    {
        "country": "台灣",
        "title": "TW 國貿署 進出口貨品分類號列",
        "title_zh": "台灣 國貿署 進出口貨品分類號列（CCC Code）",
        "url": "https://fbfh.trade.gov.tw/rich/text/indexbk.asp",
        "date": "2025-01-01",
        "bullets": [
            "食品輸入時必須對應的貨品分類號列",
            "與「輸入規定 508」配套（食品類需食藥署查驗）",
            "業者通關時所用",
        ],
    },
    {
        "country": "台灣",
        "title": "TW 食藥署 食品輸入查驗業務專區",
        "title_zh": "台灣 食藥署 食品輸入查驗業務專區",
        "url": "https://www.fda.gov.tw/TC/site.aspx?sid=1740",
        "date": "2025-01-01",
        "bullets": [
            "食藥署輸入業務主入口",
            "含查驗類別說明、廠商註冊、檢驗合格證明",
            "輸入規定 508 食品類完整對照",
        ],
    },
    {
        "country": "台灣",
        "title": "TW 食藥署 食品輸入邊境管制不合格資訊",
        "title_zh": "台灣 食藥署 食品邊境管制不合格資訊",
        "url": "https://www.fda.gov.tw/TC/siteContent.aspx?sid=11800",
        "date": "2026-01-01",
        "bullets": [
            "邊境查驗發現不合格的食品案件公告",
            "業者必查 — 避免進口同類產品被退",
            "依產品、廠商、原產國分類",
            "對應台灣業者輸出時的注意事項",
        ],
    },
    {
        "country": "台灣",
        "title": "TW 衛福部 食品出口衛生證明書申請",
        "title_zh": "台灣 食品出口衛生證明書申請",
        "url": "https://www.fda.gov.tw/TC/siteListContent.aspx?sid=10079&id=33301",
        "date": "2025-01-01",
        "bullets": [
            "輸出台灣食品所需的官方衛生證明書",
            "由衛福部食藥署核發",
            "輸日、輸美、輸馬等都可能需要",
            "線上申辦系統",
        ],
    },

    # === 美國 ===
    {
        "country": "美國",
        "title": "US FDA Import Alerts (DWPE Red List)",
        "title_zh": "美國 FDA 進口警示（DWPE 紅名單）",
        "url": "https://www.accessdata.fda.gov/cms_ia/ialist.html",
        "date": "2026-01-01",
        "bullets": [
            "FDA 公告對特定國家/廠商/產品實施『不經實體檢驗即可退運』的清單",
            "台灣業者輸美前必查 — 若在紅名單上會被自動扣留",
            "依產品類別分類（綠茶、罐頭、寵物食品、海鮮等）",
            "需定期查訪，FDA 每月更新數十條",
        ],
    },
    {
        "country": "美國",
        "title": "US FDA Prior Notice for Imported Food",
        "title_zh": "美國 FDA 進口食品事前通報 (Prior Notice)",
        "url": "https://www.fda.gov/food/importing-food-products-united-states/prior-notice-imported-food",
        "date": "2025-01-01",
        "bullets": [
            "輸美食品到貨前 4-8 小時必須申報",
            "透過 FDA Prior Notice System Interface (PNSI) 提交",
            "未事前通報 → 拒絕入境 + 退運",
            "適用所有人類與動物用食品",
        ],
    },
    {
        "country": "美國",
        "title": "US FSMA Foreign Supplier Verification Programs (FSVP)",
        "title_zh": "美國 FSMA 國外供應商驗證計畫（FSVP）",
        "url": "https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-foreign-supplier-verification-programs-fsvp-importers-food-humans-and-animals",
        "date": "2017-05-30",
        "bullets": [
            "美國進口商必須驗證其國外供應商符合 FSMA 食安標準",
            "輸美業者要配合美方進口商提交食安驗證紀錄",
            "違反者：FDA 可吊銷進口商註冊或將供應商列入 Import Alert",
        ],
    },
    {
        "country": "美國",
        "title": "US FDA Food Facility Registration",
        "title_zh": "美國 FDA 食品設施註冊",
        "url": "https://www.fda.gov/food/guidance-regulation-food-and-dietary-supplements/registration-food-facilities-and-other-submissions",
        "date": "2024-01-01",
        "bullets": [
            "輸美食品的製造、加工、包裝設施須在 FDA 註冊",
            "每兩年（偶數年 10-12 月）續展註冊",
            "未註冊 → 美方拒絕入境",
            "需指定 U.S. Agent 代理人",
        ],
    },
    {
        "country": "美國",
        "title": "US Import Refusal Reports",
        "title_zh": "美國 FDA 進口拒絕報告（OASIS）",
        "url": "https://www.accessdata.fda.gov/scripts/importrefusals/",
        "date": "2026-01-01",
        "bullets": [
            "FDA 公開的進口拒絕資料庫",
            "可查台灣輸美被拒的歷史案例",
            "可依產品、原因、廠商搜尋",
            "業者可作為自主合規參考",
        ],
    },
    {
        "country": "美國",
        "title": "USDA FSIS Imported Meat & Poultry",
        "title_zh": "美國 USDA FSIS 肉類禽類進口要求",
        "url": "https://www.fsis.usda.gov/inspection/import-export",
        "date": "2025-01-01",
        "bullets": [
            "輸美肉類、家禽、加工肉品由 USDA FSIS 管（非 FDA）",
            "出口國須先取得 USDA 對等性認證",
            "目前台灣豬肉、雞肉尚未獲認證輸美",
        ],
    },

    # === 歐盟 ===
    {
        "country": "歐盟",
        "title": "EU Rapid Alert System for Food and Feed (RASFF)",
        "title_zh": "歐盟 食品與飼料快速警報系統（RASFF）",
        "url": "https://webgate.ec.europa.eu/rasff-window/screen/list",
        "date": "2026-01-01",
        "bullets": [
            "歐盟對輸入食品的即時警報資料庫",
            "查詢台灣輸歐被通報的情況",
            "依產品、危害類型、產地分類",
            "業者可訂閱 email 通知",
        ],
    },
    {
        "country": "歐盟",
        "title": "EU TRACES NT (Trade Control and Expert System)",
        "title_zh": "歐盟 TRACES NT 動植物產品進出口管理系統",
        "url": "https://webgate.ec.europa.eu/tracesnt/login",
        "date": "2025-01-01",
        "bullets": [
            "輸歐動物產品、植物產品必須透過此系統申報",
            "需事前由出口國主管機關核發 CHED (Common Health Entry Document)",
            "適用：肉品、水產、乳製品、植物等",
        ],
    },
    {
        "country": "歐盟",
        "title": "EU Regulation 2017/625 Official Controls",
        "title_zh": "歐盟 進口食品官方檢驗規定 (Reg. 2017/625)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32017R0625",
        "date": "2019-12-14",
        "bullets": [
            "歐盟對進口食品官方檢驗的整合規定",
            "建立 Border Control Posts (BCP) 制度",
            "規範動植物產品、食品添加物、農藥殘留檢驗",
            "輸歐業者必查",
        ],
    },
    {
        "country": "歐盟",
        "title": "EU Novel Food Authorisation",
        "title_zh": "歐盟 新興食品上市核准",
        "url": "https://food.ec.europa.eu/food-safety/novel-food_en",
        "date": "2025-01-01",
        "bullets": [
            "新興食品（昆蟲、CBD、藻類蛋白等）輸歐須事前申請",
            "由 EFSA 評估安全性",
            "通過後納入 EU Novel Food List",
            "涵蓋傳統食品新材料、新製程食品",
        ],
    },
    {
        "country": "歐盟",
        "title": "EU FAVV CITES Plant Imports",
        "title_zh": "歐盟 植物源食品進口要求",
        "url": "https://food.ec.europa.eu/plants/eu-import-conditions-plants-and-plant-products_en",
        "date": "2025-01-01",
        "bullets": [
            "歐盟對植物源食品的進口要求",
            "包含蔬果、辛香料、種子、堅果",
            "需出口國 Phytosanitary Certificate",
            "對台灣茶葉、蔬果輸歐業者重要",
        ],
    },

    # === 澳洲 ===
    {
        "country": "澳洲",
        "title": "AU DAFF Imported Food Inspection Scheme (IFIS)",
        "title_zh": "澳洲 進口食品檢驗計畫（IFIS）",
        "url": "https://www.agriculture.gov.au/biosecurity-trade/import/goods/food",
        "date": "2025-01-01",
        "bullets": [
            "澳洲農漁林部 (DAFF) 主管的進口食品檢驗",
            "依風險分為 risk food 與 surveillance food",
            "Risk food 抽驗比率較高（嬰兒食品、即食、海鮮等）",
            "輸澳業者首次出口需確認類別",
        ],
    },
    {
        "country": "澳洲",
        "title": "AU MICOR (Manual of Importing Country Requirements)",
        "title_zh": "澳洲 出口要求查詢手冊（MICOR）",
        "url": "https://micor.agriculture.gov.au/",
        "date": "2026-01-01",
        "bullets": [
            "澳洲 → 各國的出口要求查詢",
            "從澳洲進口者可反查特定產品的合規要求",
            "包含台灣、日本、韓國等亞洲市場",
        ],
    },
    {
        "country": "澳洲",
        "title": "AU BICON (Biosecurity Import Conditions)",
        "title_zh": "澳洲 BICON 生物安全進口條件查詢",
        "url": "https://bicon.agriculture.gov.au/",
        "date": "2026-01-01",
        "bullets": [
            "輸澳食品/動植物必查的進口條件資料庫",
            "可依產品名稱、HS Code 查詢",
            "顯示是否需檢疫、燻蒸、檢驗、許可",
            "業者實際申辦前必看",
        ],
    },
    {
        "country": "澳洲",
        "title": "AU FSANZ Standard 1.5.1 Novel Foods",
        "title_zh": "澳洲 FSANZ Standard 1.5.1 新興食品標準",
        "url": "https://www.foodstandards.gov.au/business/novel",
        "date": "2024-01-01",
        "bullets": [
            "澳紐對新興食品的上市規範",
            "需 FSANZ 評估認可才能輸入販售",
            "涵蓋新成分、新技術製成食品",
        ],
    },
    {
        "country": "澳洲",
        "title": "AU Food Importer & Broker Licensing",
        "title_zh": "澳洲 食品進口商與報關行登記",
        "url": "https://www.agriculture.gov.au/biosecurity-trade/import/goods/food/registered-food-importers",
        "date": "2025-01-01",
        "bullets": [
            "澳洲食品進口商須先註冊登記",
            "確保進口商有食安責任",
            "與美國 FSVP 概念類似",
        ],
    },

    # === 日本 ===
    {
        "country": "日本",
        "title": "JP MHLW 輸入食品監視業務",
        "title_zh": "日本 MHLW 輸入食品監視業務",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/yunyu_kanshi/index.html",
        "date": "2025-01-01",
        "bullets": [
            "日本厚生労働省輸入食品監視窗口",
            "規範輸入食品通關、抽驗、檢疫",
            "輸日業者必查",
            "查詢年度監視計畫與抽驗重點",
        ],
    },
    {
        "country": "日本",
        "title": "JP MHLW 食品輸入相談",
        "title_zh": "日本 食品輸入諮詢窗口",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/yunyu_kanshi/dl/index.html",
        "date": "2025-01-01",
        "bullets": [
            "輸日食品事前諮詢制度",
            "日方港埠（成田、関西、神戶、橫濱）的食品衛生監視員",
            "新產品輸日建議先諮詢避免到貨被退",
        ],
    },
    {
        "country": "日本",
        "title": "JP 食品輸入届出オンラインシステム (FAINS)",
        "title_zh": "日本 食品輸入申報線上系統（FAINS）",
        "url": "https://www.fains.mhlw.go.jp/",
        "date": "2025-01-01",
        "bullets": [
            "輸日食品申報的官方系統",
            "業者線上提交輸入届出書",
            "整合 NACCS（海關系統）",
            "等同台灣 FRT、馬國 FoSIM",
        ],
    },
    {
        "country": "日本",
        "title": "JP MAFF 動物検疫所",
        "title_zh": "日本 農林水產省 動物檢疫所",
        "url": "https://www.maff.go.jp/aqs/",
        "date": "2025-01-01",
        "bullets": [
            "輸日肉品、乳製品、蛋類動物源食品的檢疫",
            "需出口國衛生證明書",
            "對台灣業者：豬肉輸日有限制（豬瘟）",
        ],
    },
    {
        "country": "日本",
        "title": "JP MAFF 植物検疫",
        "title_zh": "日本 農林水產省 植物檢疫",
        "url": "https://www.maff.go.jp/pps/",
        "date": "2025-01-01",
        "bullets": [
            "輸日蔬果、農產品的檢疫",
            "需 Phytosanitary Certificate",
            "對台灣茶葉、芒果、鳳梨輸日重要",
        ],
    },

    # === 香港 ===
    {
        "country": "香港",
        "title": "HK CFS 進口商及分銷商註冊",
        "title_zh": "香港 食物入口商及分銷商註冊",
        "url": "https://www.cfs.gov.hk/tc_chi/import/import_iddtr/import_iddtr.html",
        "date": "2025-01-01",
        "bullets": [
            "香港食物入口商與分銷商強制登記制度",
            "依《食物安全條例》（第 612 章）",
            "輸港食品必須透過註冊商才能進入香港市場",
            "註冊系統由 CFS 主管",
        ],
    },
    {
        "country": "香港",
        "title": "HK CFS 高風險食物進口許可",
        "title_zh": "香港 高風險食物進口許可制度",
        "url": "https://www.cfs.gov.hk/tc_chi/import/import_ihfp.html",
        "date": "2025-01-01",
        "bullets": [
            "輸港肉類、家禽、奶製品須事前申請進口許可",
            "源廠須在香港 CFS 核准名單上（特別是中國以外地區）",
            "台灣輸港肉品需衛福部出具衛生證明書",
        ],
    },
    {
        "country": "香港",
        "title": "HK CFS 食物入口商及分銷商規例",
        "title_zh": "香港 食物入口商及分銷商規例",
        "url": "https://www.elegislation.gov.hk/hk/cap612A",
        "date": "2024-01-01",
        "bullets": [
            "香港《食物安全條例》附屬規例",
            "規範入口商記錄保存（追溯需求）",
            "保存期限：最少 24 個月",
        ],
    },
    {
        "country": "香港",
        "title": "HK 食環署 輸港食品檢測結果",
        "title_zh": "香港 食環署 輸港食品定期檢測結果",
        "url": "https://www.cfs.gov.hk/tc_chi/programme/programme_rafs/index.html",
        "date": "2026-01-01",
        "bullets": [
            "香港 CFS 公布的食物安全例行檢測結果",
            "依產品類別公布合規率",
            "業者可作為自主合規參考",
        ],
    },
    {
        "country": "香港",
        "title": "HK 入口蔬果食物安全規例",
        "title_zh": "香港 進口蔬果食品安全規例",
        "url": "https://www.cfs.gov.hk/tc_chi/import/import_vegfruit.html",
        "date": "2025-01-01",
        "bullets": [
            "輸港蔬果的農藥殘留要求",
            "與 Codex MRL 接軌",
            "對台灣鳳梨、芒果、蔬菜輸港業者重要",
        ],
    },

    # === 馬來西亞 ===
    {
        "country": "馬來西亞",
        "title": "MY FoSIM (Food Safety Information System)",
        "title_zh": "馬來西亞 食品安全資訊系統（FoSIM）",
        "url": "https://fosim.moh.gov.my/",
        "date": "2025-01-01",
        "bullets": [
            "輸馬食品進口必經系統",
            "業者註冊 → 申報 → 抽驗 → 放行/退回",
            "整合 Customs 系統",
            "與台灣食藥署 FRT 類似",
        ],
    },
    {
        "country": "馬來西亞",
        "title": "MY Food Safety and Quality Division (BKKM)",
        "title_zh": "馬來西亞 食品安全與品質部門（BKKM）",
        "url": "https://hq.moh.gov.my/fsq/",
        "date": "2025-01-01",
        "bullets": [
            "馬來西亞食品安全主管部門",
            "管轄：進口檢驗、HACCP 認證、警報",
            "輸馬業者主要對接單位",
        ],
    },
    {
        "country": "馬來西亞",
        "title": "MY MITI Trade Customs Tariff",
        "title_zh": "馬來西亞 進出口關稅查詢",
        "url": "https://www.miti.gov.my/",
        "date": "2025-01-01",
        "bullets": [
            "馬國國際貿易與工業部",
            "輸馬食品關稅查詢",
            "與東協關稅優惠 (ATIGA) 對接",
            "台灣與馬國有 ECFA 早收清單可參考",
        ],
    },
    {
        "country": "馬來西亞",
        "title": "MY JAKIM Halal Import Recognition",
        "title_zh": "馬來西亞 JAKIM 海外清真認證對等承認名單",
        "url": "https://www.halal.gov.my/v4/index.php/en/main-menu-foreign-halal-certification-bodies",
        "date": "2026-01-01",
        "bullets": [
            "JAKIM 承認的海外清真認證機構名單",
            "台灣業者若取得 MUI（印尼）等被承認機構認證 → 可輸馬",
            "未在名單上 → 需要重新做 JAKIM 認證",
        ],
    },

    # === 國際 ===
    {
        "country": "國際",
        "title": "Codex MRL Database (農藥殘留)",
        "title_zh": "Codex 全球農藥殘留容許量資料庫",
        "url": "https://www.fao.org/fao-who-codexalimentarius/codex-texts/dbs/pestres/en/",
        "date": "2026-01-01",
        "bullets": [
            "全球農藥殘留容許量參考資料庫",
            "可查 5000+ 農藥 × 食品的 MRL",
            "業者跨國輸出時的對照基準",
            "各國 MRL 多參考此標準",
        ],
    },
    {
        "country": "國際",
        "title": "WTO TBT 通報",
        "title_zh": "WTO TBT 技術性貿易障礙通報",
        "url": "https://epingalert.org/",
        "date": "2026-01-01",
        "bullets": [
            "WTO 會員國發布新法規時的早期預警平台",
            "可訂閱 email 通知特定產品/國家的變動",
            "台灣業者可預先了解輸出國未來法規動向",
            "免費註冊",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_ENTRIES:
        tags = ["進出口", s["country"]]
        if "Halal" in s["title"] or "清真" in s["title_zh"]:
            tags.append("清真")
        if "肉" in s["title_zh"] or "Meat" in s["title"]:
            tags.append("肉品")
        if "Phyto" in s["title"] or "植物" in s["title_zh"]:
            tags.append("植物檢疫")
        if "novel" in s["title"].lower() or "新興" in s["title_zh"]:
            tags.append("新興食品")
        if "Halal" in s["title"]:
            tags.append("清真")

        item = make_item(
            source="import_export",
            source_label="進出口規範",
            source_color="slate",
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
    print(f"  [Import/Export] 各國進出口入口 {len(items)} 條（手選目錄）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
