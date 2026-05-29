"""進出口規範 — 各國食品進出口主管機關入口（手選目錄）

進出口資料多為法規、操作手冊與大量 PDF，無法以單一爬蟲處理。
這份目錄列出各國家「進口食品申辦入口」與「出口管制清單」，
作為衛生管理員查詢起點。
"""
from __future__ import annotations
from common import make_item


# 各國家進出口主管機關與入口
CURATED_ENTRIES = [
    # 台灣
    {
        "country": "台灣",
        "title": "台灣 食藥署 食品輸入查驗系統 (FRT)",
        "title_zh": "台灣食品輸入查驗系統（FRT）",
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
        "title": "台灣 食品及相關產品輸入查驗辦法",
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
        "title": "台灣 國貿署 進出口貨品分類號列",
        "title_zh": "台灣 國貿署 進出口貨品分類號列（CCC Code）",
        "url": "https://fbfh.trade.gov.tw/rich/text/indexbk.asp",
        "date": "2025-01-01",
        "bullets": [
            "食品輸入時必須對應的貨品分類號列",
            "與「輸入規定 508」配套（食品類需食藥署查驗）",
            "業者通關時所用",
        ],
    },
    # 美國
    {
        "country": "美國",
        "title": "US FDA Import Alerts (Detention Without Physical Examination)",
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
        "title": "FSMA Foreign Supplier Verification Programs (FSVP)",
        "title_zh": "美國 FSMA 國外供應商驗證計畫（FSVP）",
        "url": "https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-foreign-supplier-verification-programs-fsvp-importers-food-humans-and-animals",
        "date": "2017-05-30",
        "bullets": [
            "美國進口商必須驗證其國外供應商符合 FSMA 食安標準",
            "輸美業者要配合美方進口商提交食安驗證紀錄",
            "違反者：FDA 可吊銷進口商註冊或將供應商列入 Import Alert",
        ],
    },
    # 歐盟
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
    # 澳洲
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
    # 日本
    {
        "country": "日本",
        "title": "JP 厚生労働省 輸入食品監視業務",
        "title_zh": "日本 輸入食品監視業務",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/yunyu_kanshi/index.html",
        "date": "2025-01-01",
        "bullets": [
            "日本厚生労動省輸入食品監視窗口",
            "規範輸入食品通關、抽驗、檢疫",
            "輸日業者必查",
            "查詢年度監視計畫與抽驗重點",
        ],
    },
    {
        "country": "日本",
        "title": "JP 厚生労働省 食品輸入相談",
        "title_zh": "日本 食品輸入諮詢窗口",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/yunyu_kanshi/dl/index.html",
        "date": "2025-01-01",
        "bullets": [
            "輸日食品事前諮詢制度",
            "日方港埠（成田、関西、神戶、橫濱）的食品衛生監視員",
            "新產品輸日建議先諮詢避免到貨被退",
        ],
    },
    # 香港
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
        "title": "HK 高風險食物（肉類、家禽、奶類）進口許可",
        "title_zh": "香港 高風險食物進口許可制度",
        "url": "https://www.cfs.gov.hk/tc_chi/import/import_ihfp.html",
        "date": "2025-01-01",
        "bullets": [
            "輸港肉類、家禽、奶製品須事前申請進口許可",
            "源廠須在香港 CFS 核准名單上（特別是中國以外地區）",
            "台灣輸港肉品需衛福部出具衛生證明書",
        ],
    },
    # 馬來西亞
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
]


def crawl() -> list[dict]:
    items = []
    for s in CURATED_ENTRIES:
        tags = ["進出口", s["country"]]
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
        item["country"] = s["country"]  # 直接帶在 item 上（會被 build_data 尊重）
        items.append(item)
    print(f"  [Import/Export] 各國進出口入口 {len(items)} 條（手選目錄）")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
