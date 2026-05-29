"""把預先準備好的 AI 摘要與中文標題翻譯寫進 items.json
以 URL 為主鍵；未列在這裡的 item 不變動。

- SUMMARIES: URL → list[str]，每筆 3-5 條繁中重點
- ZH_TITLES: URL → str，英文來源的中文翻譯標題（中文來源不需要）
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"

# 英文來源的中文翻譯標題
ZH_TITLES = {
    "https://www.efsa.europa.eu/en/news/african-swine-fever-outbreaks-increase-pigs-and-wild-boar-across-eu":
        "歐盟非洲豬瘟疫情擴大 — 豬隻與野豬感染雙升",
    "https://www.efsa.europa.eu/en/podcast/episode-40-science-communication-taking-misinformation-menu":
        "EFSA Podcast 第 40 集：科學溝通 — 把假訊息趕出菜單",
    "https://www.efsa.europa.eu/en/news/plant-health-4-life-reinforcing-simple-actions-protect-plants":
        "EFSA 推動「Plant Health 4 Life」植物健康倡議第 4 年",
    "https://multimedia.efsa.europa.eu/pesticides-report-2024/index.html":
        "2024 歐盟農藥殘留報告（互動式視覺化）",
    "https://www.efsa.europa.eu/en/news/pesticide-residues-food-latest-data-released":
        "EFSA 公布最新歐盟農藥殘留檢測資料",
    "https://www.efsa.europa.eu/en/news/eu-agencies-highlight-role-research-effective-policy-making":
        "歐盟機構強調研究在有效政策制定中的角色",
    "https://www.efsa.europa.eu/en/news/safe2eat-2026-science-backed-guidance-all-europeans":
        "Safe2Eat 2026 — 為全歐洲提供以科學為基礎的食安指引",
    "https://www.efsa.europa.eu/en/news/efsa-guidance-documents-new-catalogue-improve-access-and-use":
        "EFSA 指引文件分類更新 — 提升可近性與易用性",
    "https://www.efsa.europa.eu/en/podcast/episode-39-eu-career-boost-efsa-looking-you":
        "EFSA Podcast 第 39 集：EU 實習計畫 — EFSA 正在找您",
    "https://www.efsa.europa.eu/en/news/avian-influenza-detections-birds-decline-across-eu":
        "歐盟禽流感 — 鳥類檢出案件減少",
    "https://www.efsa.europa.eu/en/podcast/episode-38-speed-how-food-risk-assessment-changing":
        "EFSA Podcast 第 38 集：食品風險評估正如何加速演進",
    "https://www.efsa.europa.eu/en/news/latest-xylella-control-options-reviewed-have-your-say":
        "Xylella（火傷病）最新防治選項評估 — 公開徵詢意見",
    "https://www.efsa.europa.eu/en/news/presscorner":
        "EFSA 新聞中心 — 互動式工具一覽",
    "https://www.youtube.com/watch?v=pWH3et1Y26U":
        "EFSA 介紹影片：科學、安全食品、永續",
    # 日本 FSC
    "https://www.fsc.go.jp/iken-bosyu/pc1_idensi_soy_260527.html":
        "耐除草劑（嘉磷塞、固殺草）基改大豆 DBN9004 食品健康影響評估 — 公開徵詢",
    "https://www.fsc.go.jp/iken-bosyu/pc_1_no_florylpicoxamid_260520.html":
        "殺菌劑 Florylpicoxamid 食品健康影響評估審議草案 — 公開徵詢",
    "https://www.fsc.go.jp/iken-bosyu/pc_1_no_cycloxydim_260520.html":
        "除草劑 Cycloxydim（環苯草酮）食品健康影響評估審議草案 — 公開徵詢",
    "https://www.fsc.go.jp/iken-bosyu/pc_1_no_ethiprole_260520.html":
        "殺蟲劑 Ethiprole（乙蟲腈）食品健康影響評估審議草案 — 公開徵詢",
}


SUMMARIES = {
  # 日本 FSC 公開徵詢
  "https://www.fsc.go.jp/iken-bosyu/pc1_idensi_soy_260527.html": [
    "標的：耐除草劑（嘉磷塞 + 固殺草）基改大豆品系 DBN9004",
    "用途：除草劑耐性大豆，可同時抗 Glyphosate 與 Glufosinate",
    "階段：日本食品安全委員會公開徵詢意見（等同台灣預告法規）",
    "影響：未來日本進口豆製品可能涉及此基改品系",
    "意見徵詢期至公告後 30 日內",
  ],
  "https://www.fsc.go.jp/iken-bosyu/pc_1_no_florylpicoxamid_260520.html": [
    "標的：殺菌劑 Florylpicoxamid",
    "用途：新型農用殺菌劑，可能用於穀物、水果、蔬菜",
    "階段：食品健康影響評估審議草案",
    "影響：日本將訂定該殺菌劑於各類食品中的殘留容許量",
  ],
  "https://www.fsc.go.jp/iken-bosyu/pc_1_no_cycloxydim_260520.html": [
    "標的：除草劑 Cycloxydim（環苯草酮）",
    "用途：選擇性禾本科除草劑，常用於大豆、棉花、油菜",
    "階段：食品健康影響評估審議草案",
    "影響：相關農產品輸日時的殘留容許量規範可能變動",
  ],
  "https://www.fsc.go.jp/iken-bosyu/pc_1_no_ethiprole_260520.html": [
    "標的：殺蟲劑 Ethiprole（乙蟲腈）",
    "用途：苯吡唑類殺蟲劑，用於水稻、棉花防治稻飛蝨等害蟲",
    "階段：食品健康影響評估審議草案",
    "影響：水稻、棉籽油等輸日時殘留容許量規範可能變動",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31554": [
    "預告修正「藥事法偏遠地區列表」附表一、二、五、十、十四、十五（健保西醫巡迴地點）",
    "依藥事法第 102 條第 2 項辦理，由衛生福利部主管",
    "影響：偏遠地區藥師執業認定、處方權範圍",
    "意見徵詢期 60 日，由食藥署承辦",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31553": [
    "預告修正「藥事法偏遠地區列表」附表六（非屬偏遠地區清單）",
    "與 31554 號公告為配套修正，調整偏遠地區範圍",
    "影響：藥師執業地點劃分、調劑作業認定",
    "意見徵詢期 60 日",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31552": [
    "第二次預告修正「食品中動物用藥殘留量檢驗方法－Avermectin類抗生素」",
    "Avermectin 類為畜禽常用驅蟲抗生素，方法更新後影響殘留量檢測結果",
    "依據食品安全衛生管理法第 38 條，由食藥署負責",
    "意見徵詢期 60 日，業者與檢驗實驗室應提早因應",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=3&id=31551": [
    "預告修正「生物相似性藥品查驗登記基準」",
    "影響國內生物相似性藥品（biosimilars）的審查標準與申請流程",
    "由食藥署藥品組主辦，公告次日起 60 日內可陳述意見",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=3&id=31550": [
    "115 年度食品添加物查驗登記業務委託「台灣優良農產品發展協會」審查",
    "委託期限：115 年 1 月 12 日至 12 月 31 日（全年度）",
    "受託業務範圍：新案申請與許可文件展延審查",
    "業者送件時應留意受託機構變更，依「食品與相關產品查驗登記業務委託辦法」第 11 條辦理",
  ],
  "https://www.efsa.europa.eu/en/news/african-swine-fever-outbreaks-increase-pigs-and-wild-boar-across-eu": [
    "歐盟非洲豬瘟（ASF）2025 年疫情明顯上升",
    "家豬感染案件較 2024 年增加 76%、野豬則增加 44%",
    "EFSA 年度流行病學報告示警，加強生物安全管制",
    "影響：輸歐豬肉與相關製品業者需注意檢疫升級可能",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31549": [
    "預告修正「輸入醫療器材邊境抽查檢驗辦法」第六條附表二",
    "依醫療器材管理法第 52 條第 2 項辦理，調整邊境抽查項目",
    "影響進口醫療器材業者，須留意抽驗品項異動",
    "意見徵詢期 60 日，由食藥署承辦",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=3&id=31548": [
    "新訂「食品廣告合規輔導指引」協助業者釐清廣告合規界線",
    "依行政程序法第 165 條訂定，屬指引性質非強制",
    "目的：強化食品廣告管理、促進業者自律",
    "全文可於食藥署「公告資訊」網頁下載",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-40-science-communication-taking-misinformation-menu": [
    "EFSA Podcast 第 40 集，主題：科學溝通與打擊不實訊息",
    "討論食安疑慮、假新聞、昆蟲食物、微塑膠等議題的溝通方式",
    "適合食品業者了解國際食安傳播趨勢",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31543": [
    "預告訂定「西藥非處方藥仿單與外盒刊載應遵行事項」草案",
    "規範非處方藥（OTC）包裝標示應記載項目與格式",
    "與下方廢止案配套，建立新版仿單與外盒規定",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31542": [
    "預告廢止 105 年「西藥非處方藥仿單外盒格式及規範」",
    "原公告（部授食字第 1051402838 號）將由新版規範取代",
    "業者需注意新舊規範銜接時程",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=3&id=31540": [
    "修正「輸入規定『508』貨品分類號列表」，溯及 115 年 4 月 1 日生效",
    "新增 CCC2924.29.90.32-9「含全氟己烷磺酸酯之環醯胺化合物」等 5 項貨品號列",
    "屬食品或食品添加物用途者，須向食藥署申請輸入查驗",
    "影響進口食品、食品添加物（含香料）業者",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=3&id=31545": [
    "推出「藥品查驗登記國產加速審查試辦方案」",
    "涵蓋 4 個子方案：新藥、信賴審查、原料藥/學名藥加速、原料藥/製劑垂直整合",
    "目標：縮短查驗登記審查時程，提升藥品可近性",
    "試辦期至 116 年 12 月 31 日，屆時視成效決定續辦",
  ],
  "https://www.efsa.europa.eu/en/news/plant-health-4-life-reinforcing-simple-actions-protect-plants": [
    "EFSA 推動「Plant Health 4 Life」植物健康倡議第 4 年（最終年）",
    "與歐盟執委會及 33 個國家合作推廣保護植物的簡易行動",
    "對國內輸歐農產品業者具有檢疫趨勢參考價值",
  ],
  "https://www.efsa.europa.eu/en/news/pesticide-residues-food-latest-data-released": [
    "EFSA 公布最新歐盟農藥殘留檢測結果",
    "基於跨歐盟逾 125,000 份食品樣本，整體符合 EU 限值比例維持高水準",
    "影響輸歐農產品業者，可作為自主檢驗的對標基準",
  ],
  "https://www.efsa.europa.eu/en/news/eu-agencies-highlight-role-research-effective-policy-making": [
    "EU‑ANSA（歐盟科學諮詢機構網絡）重申科學研究在政策制定中的核心角色",
    "強調將科學知識轉化為實證導向政策的重要性",
    "屬政策性聲明，對台灣業者直接影響有限",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31530": [
    "預告修正「管制藥品分級及品項」",
    "增列 3 項為第二級管制藥品：碳依托咪酯（Carboetomidate）、甲氧羰基碳依托咪酯、烯丙基依托咪酯",
    "依管制藥品管理條例第 3 條第 2 項辦理",
    "醫療院所、藥商需注意新增品項的管理規範",
  ],
  "https://www.efsa.europa.eu/en/news/safe2eat-2026-science-backed-guidance-all-europeans": [
    "EFSA 旗艦倡議「Safe2Eat」邁入第 6 年",
    "以科學為基礎，將食安知識轉譯為一般民眾易懂的日常指引",
    "可參考其衛教傳播設計，作為國內食安溝通借鏡",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=4&id=31511": [
    "食藥署與國健署合作推動「食品紅黃綠」正面營養標示制度",
    "依據國民營養調查：63% 成人鈉攝取超標、17.3% 游離糖逾總熱量 10%",
    "以紅黃綠分級協助消費者快速辨識較健康選項",
    "目前處於草案研議階段，未來將擴及包裝食品",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-39-eu-career-boost-efsa-looking-you": [
    "EFSA Podcast 第 39 集：歐盟食安實習生計畫介紹",
    "屬機構招募宣傳，對業者直接影響低",
  ],
  "https://www.efsa.europa.eu/en/news/efsa-guidance-documents-new-catalogue-improve-access-and-use": [
    "EFSA 更新指引文件分類，分為 5 類：目的、內容、適用性、強制程度、對象",
    "強化跨領域與專案領域之區分，提升使用者便利度",
    "風險評估從業者可參考新的文件分類體系",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31461": [
    "預告修正「食品添加物規格檢驗方法－二氧化鈦」",
    "二氧化鈦（E171）為常見食品白色著色劑，歐盟已禁用",
    "更新檢驗方法後將影響市售食品的添加物檢測結果",
    "依食安法第 38 條辦理，意見徵詢期 60 日",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31460": [
    "同時預告修正「鹽酸吡哆辛（維生素 B6）」與「二氧化碳」兩項添加物的規格檢驗方法",
    "B6 常見於營養強化食品，CO₂ 常用於碳酸飲料與食品保鮮包裝",
    "影響範圍：保健食品、飲料、加工食品業者",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31457": [
    "預告修正「食品添加物規格檢驗方法－食用紅色七號鋁麗基」",
    "紅色七號鋁麗基為常用人工色素之鋁色澱形式",
    "影響使用該色素的食品業者與檢驗機構",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31456": [
    "預告廢止「歐來金得」舊版動物用藥檢驗方法",
    "廢止原因：原 HPLC-UV 方法僅可檢測歐來金得，前處理已不合時宜",
    "改採新版 LC-MS/MS 方法（一併檢測代謝物 MQCA）",
    "影響：動物用藥檢驗實驗室需更新方法",
  ],
  "https://www.efsa.europa.eu/en/news/avian-influenza-detections-birds-decline-across-eu": [
    "歐盟高病原性禽流感（HPAI）疫情在秋冬高峰後開始下降",
    "禽肉與蛋類輸歐業者可預期檢疫趨於穩定",
    "提醒：仍應持續監控國內生物安全防護",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-38-speed-how-food-risk-assessment-changing": [
    "EFSA Podcast 第 38 集：食品風險評估的演進與創新",
    "EFSA 食品創新部門主管 Nik Kriz 分享如何加快風險評估時程",
    "對風險評估與法規從業人員具參考價值",
  ],
  "https://www.efsa.europa.eu/en/news/latest-xylella-control-options-reviewed-have-your-say": [
    "EFSA 公開徵詢「Xylella fastidiosa（火傷病）」防治方法評估",
    "目前 EU 核准的合成活性物質效果最一致，多種生物性物質亦在評估中",
    "影響：橄欖、葡萄、柑橘等植物進出口檢疫",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31430": [
    "預告修訂「藥品優良臨床試驗作業指引」",
    "因應 ICH E6(R3) Annex 1 於 114 年 1 月發布的國際標準更新",
    "依行政程序法第 165 條辦理",
    "藥品研發、臨床試驗執行機構應留意指引變更",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31415": [
    "預告廢止「食品中殘留農藥檢驗方法－殺蟎劑三亞蟎」",
    "廢止原因：檢測流程繁雜、適用基質少、不符現行需求",
    "改採新版「三亞蟎及其代謝物之檢驗」方法",
    "影響：農藥殘留檢驗實驗室方法清單更新",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31414": [
    "預告修正「食品中植物性成分檢驗方法－芒果之定性檢驗」",
    "方法名稱由「芒果成分之定性檢驗」更名",
    "影響：食品摻偽鑑別、過敏原標示稽核",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31405": [
    "預告修正「醫療器材回收處理辦法」第四條",
    "依醫療器材管理法第 58 條第 3 項辦理",
    "影響醫療器材製造業者、進口業者的回收作業流程",
  ],
  "https://www.fda.gov.tw/TC/newsContent.aspx?cid=5072&id=31404": [
    "預告國際 ICH E9(R1) 統計指引：估計目標與敏感度分析",
    "為國際醫藥法規協和會（ICH）之臨床試驗統計原則指引附錄",
    "影響：跨國臨床試驗設計、分析計畫書撰寫",
  ],
}


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    n_summary = 0
    n_zh_title = 0
    for item in d["items"]:
        url = item.get("url")
        if url in SUMMARIES:
            item["ai_summary"] = SUMMARIES[url]
            n_summary += 1
        if url in ZH_TITLES:
            item["title_zh"] = ZH_TITLES[url]
            n_zh_title += 1
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"AI 摘要：{n_summary} / {len(d['items'])} 筆")
    print(f"中文標題：{n_zh_title} 筆（國際來源）")


if __name__ == "__main__":
    main()
