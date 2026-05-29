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
    # EFSA 批次補翻譯（2025-07 ~ 2026-02）
    "https://www.efsa.europa.eu/en/news/new-memorandum-understanding-mou-strengthens-cooperation-between-efsa-and-fao":
        "EFSA 與 FAO 簽署新版合作備忘錄 — 強化雙邊食安創新與標準合作",
    "https://www.efsa.europa.eu/en/news/efsa-and-ecdc-rapid-outbreak-assessment-cereulide-incident-likelihood-exposure-low":
        "EFSA 與 ECDC：cereulide（嘔吐毒素）事件快速評估 — 暴露機率低",
    "https://www.efsa.europa.eu/en/news/antimicrobial-resistance-foodborne-bacteria-remains-public-health-concern-europe":
        "EFSA：歐洲食源性細菌抗藥性仍是公衛隱憂（部分國家有改善）",
    "https://www.efsa.europa.eu/en/news/efsa-finds-sucralose-safe-when-used-currently-authorised-cannot-confirm-safety-extending-its":
        "EFSA：蔗糖素（E 955）現行用途安全，擴大使用範圍尚無法確認",
    "https://www.efsa.europa.eu/en/news/fish-and-seafood-consumption-eu-awareness-dietary-advice-mercury":
        "EFSA 研究：歐盟消費者對魚貝類汞攝取建議的認知度",
    "https://www.efsa.europa.eu/en/podcast/episode-37-no-secret-sauce-recipe-transparent-science":
        "EFSA Podcast 第 37 集：透明科學 — 文件公開的法律考量",
    "https://www.efsa.europa.eu/en/multimedia/pesticides-scroller":
        "互動式資訊：歐盟農藥核准流程與最高殘留量設定",
    "https://www.efsa.europa.eu/en/news/veterinary-drug-residues-food-whats-latest-eu":
        "歐盟食品中動物用藥殘留 — EFSA 年度報告",
    "https://www.efsa.europa.eu/en/news/provisional-safe-level-cannabidiol-novel-food":
        "EFSA 設定大麻二酚（CBD）作為新興食品的暫定安全攝取量",
    "https://www.efsa.europa.eu/en/infographics/efsas-scientific-opinion-welfare-turkeys-farm":
        "EFSA 科學意見：火雞養殖福利評估",
    "https://www.efsa.europa.eu/en/news/efsa-provides-rapid-risk-assessment-cereulide-infant-formula":
        "EFSA 快速風險評估：嬰兒配方奶中之 cereulide（蠟樣芽孢桿菌毒素）",
    "https://www.efsa.europa.eu/en/news/efsa-host-5th-european-conference-xylella-fastidiosa":
        "EFSA 將於 6 月在義大利舉辦第 5 屆 Xylella（火傷病）國際研討會",
    "https://www.efsa.europa.eu/en/news/precautionary-global-recall-infant-nutrition-products-following-detection-bacillus-cereus":
        "因驗出蠟樣芽孢桿菌毒素，多國預警性全球回收嬰兒營養品",
    "https://www.efsa.europa.eu/en/news/lectins-food-undercooked-beans-pose-health-risk-says-efsa":
        "EFSA 警告：未充分烹煮的豆類（凝集素）構成健康風險",
    "https://www.efsa.europa.eu/en/news/meat-intended-freezing-efsa-assesses-bacterial-growth-meat-it-reaches-consumers":
        "EFSA 評估：冷凍前的牛羊豬肉之細菌生長變化",
    "https://www.efsa.europa.eu/en/podcast/episode-36-nice-m-eat-you-what-are-alternative-proteins":
        "EFSA Podcast 第 36 集：替代蛋白質 — 從豆類到細胞培養肉",
    "https://www.efsa.europa.eu/en/news/efsa-introduction-bird-flu-us-dairy-cattle-europe-very-unlikely-vigilance-urged":
        "EFSA：美國乳牛禽流感傳入歐洲機率極低，但仍籲提高警覺",
    "https://www.efsa.europa.eu/en/news/avian-influenza-new-outbreaks-expected-europe-until-winter-ends":
        "EFSA：歐洲禽流感冬季疫情預期持續到春末（29 國累計案例）",
    "https://www.efsa.europa.eu/en/podcast/episode-35-bean-there-cooked-are-raw-legumes-safe":
        "EFSA Podcast 第 35 集：生豆類的食安 — 凝集素與烹飪方式",
    "https://www.efsa.europa.eu/en/infographics/foodborne-diseases-europe-whats-really-making-you-sick":
        "歐洲食源性疾病 — 2024 歐盟 One Health 年度報告重點",
    "https://www.efsa.europa.eu/en/news/serious-listeria-infections-rising-europe-eu-report-warns":
        "EFSA 報告：歐洲嚴重李斯特菌感染上升（蛋、肉、即食食品為主要來源）",
    "https://multimedia.efsa.europa.eu/drvs/index.htm":
        "EFSA DRV 工具：營養素參考攝取量查詢器（含新版氟攝取上限）",
    "https://www.efsa.europa.eu/en/news/have-your-say-dioxins-and-related-pcbs":
        "EFSA 徵詢意見：戴奧辛與多氯聯苯之健康風險評估",
    "https://www.efsa.europa.eu/en/news/avian-influenza-europe-enhanced-surveillance-and-strict-biosecurity-needed-detections-surge":
        "EFSA：歐洲禽流感檢出激增（較去年同期 4 倍），須強化監測與生物安全",
    "https://www.efsa.europa.eu/en/podcast/episode-34-cost-origin-taste-what-influences-our-food-choices":
        "EFSA Podcast 第 34 集：影響消費者食品選擇的因素",
    "https://www.efsa.europa.eu/en/news/delta-8-thc-efsa-sets-safe-intake-level":
        "EFSA 設定 Delta-8 THC（大麻精神活性成分）安全攝取量",
    "https://www.efsa.europa.eu/en/infographics/closer-look-pesticides-food":
        "EFSA 圖表：食品中農藥的監測重點",
    "https://www.efsa.europa.eu/en/news/have-your-say-complete-efsa-journal-survey":
        "EFSA 期刊讀者意見調查（5-10 分鐘）",
    "https://www.efsa.europa.eu/en/news/time-action-joint-statement-eu-cross-agency-one-health-task-force-and-european-and-central":
        "世界 One Health 日 — 9 個國際組織聯合呼籲行動",
    "https://www.efsa.europa.eu/en/podcast/episode-33-exposure-matters-why-dose-makes-poison":
        "EFSA Podcast 第 33 集：劑量決定毒性 — 危害與風險的差別",
    "https://www.efsa.europa.eu/en/interactive-pages/eurobarometer":
        "歐盟 Eurobarometer 食安認知調查（2022 與 2025）",
    "https://www.efsa.europa.eu/en/infographics/2025-eurobarometer-food-safety-eu-infographic":
        "2025 歐盟食安認知調查重點圖表",
    "https://www.efsa.europa.eu/en/podcast/episode-32-data-vs-stereotypes-what-europeans-eat":
        "EFSA Podcast 第 32 集：用資料拆解歐洲人的飲食刻板印象",
    "https://www.efsa.europa.eu/en/no-bird-flu":
        "EFSA #NoBirdFlu 活動：強化農場生物安全",
    "https://www.efsa.europa.eu/en/news/nobirdflu-clear-communications-better-biosecurity":
        "EFSA：清楚的溝通可提升禽流感防範",
    "https://www.efsa.europa.eu/en/news/nikolaus-kriz-assumes-role-efsas-new-executive-director":
        "Nikolaus Kriz 接任 EFSA 執行長",
    "https://www.efsa.europa.eu/en/podcast/episode-31-sizzling-summers-bbq-safety-served-hot":
        "EFSA Podcast 第 31 集：夏季 BBQ 食安須知",
    "https://www.efsa.europa.eu/en/infographics/welfare-animals-kept-fur-production":
        "EFSA：毛皮養殖動物福利（水貂、狐狸、貉、龍貓）評估",
    "https://www.efsa.europa.eu/en/infographics/welfare-beef-cattle-farm":
        "EFSA：肉牛農場福利評估（室內、放牧、飼料育肥）",
    "https://www.efsa.europa.eu/en/news/keeping-plant-pests-out-eu":
        "EFSA：歐盟檢疫害蟲優先名單修訂（130 位專家參與）",
    "https://www.efsa.europa.eu/en/news/fluoride-safety-updated-intake-levels-all-ages":
        "EFSA：更新各年齡層氟安全攝取量（含水、食物、加氟鹽、口腔保健）",
    "https://www.efsa.europa.eu/en/news/have-your-say-estragole-fennel-seed-preparations":
        "EFSA 徵詢意見：茴香籽製品中 estragole 的健康風險",
    "https://www.efsa.europa.eu/en/podcast/episode-30-food-supplements-add-or-not-add":
        "EFSA Podcast 第 30 集：營養補充品該不該補？",

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
  # EFSA 批次 AI 重點
  "https://www.efsa.europa.eu/en/news/new-memorandum-understanding-mou-strengthens-cooperation-between-efsa-and-fao": [
    "EFSA 與 FAO（聯合國糧農組織）簽訂新版合作備忘錄",
    "雙方目標：在快速技術變革中維持最高食安標準",
    "聚焦領域：新興食品、食源性病害評估、科學能力共享",
  ],
  "https://www.efsa.europa.eu/en/news/efsa-and-ecdc-rapid-outbreak-assessment-cereulide-incident-likelihood-exposure-low": [
    "事件：嬰兒配方奶中檢出 cereulide（蠟樣芽孢桿菌嘔吐毒素）",
    "範圍：奧地利、比利時、丹麥、法國、盧森堡、西班牙、英國 7 國",
    "風險評估：消費者整體暴露機率被評估為「低」",
    "影響：相關嬰兒奶粉已預警性回收",
  ],
  "https://www.efsa.europa.eu/en/news/antimicrobial-resistance-foodborne-bacteria-remains-public-health-concern-europe": [
    "歐洲沙門氏菌、彎曲桿菌抗藥性問題持續",
    "部分國家成功降低抗藥性比例",
    "重點抗生素：氟喹諾酮、頭孢三代",
    "業者應強化飼養端抗生素管理（One Health 策略）",
  ],
  "https://www.efsa.europa.eu/en/news/efsa-finds-sucralose-safe-when-used-currently-authorised-cannot-confirm-safety-extending-its": [
    "蔗糖素（E 955）作為甜味劑於現行核准用途仍安全",
    "若擴大使用範圍（如高溫加熱食品）— 安全性無法確認",
    "業者注意：食品熱加工含 E 955 需額外注意",
  ],
  "https://www.efsa.europa.eu/en/news/fish-and-seafood-consumption-eu-awareness-dietary-advice-mercury": [
    "EFSA 調查歐盟消費者對汞含量高的魚種（鯊魚、旗魚等）攝取頻率",
    "了解消費者對國家飲食建議的認知度",
    "用於改善風險溝通策略",
  ],
  "https://www.efsa.europa.eu/en/news/veterinary-drug-residues-food-whats-latest-eu": [
    "EFSA 年度動物用藥殘留報告",
    "監測對象：肉、奶、蛋等動物源食品",
    "整體合規率高，少數樣本超標",
    "監測指引業者飼養端用藥控管",
  ],
  "https://www.efsa.europa.eu/en/news/provisional-safe-level-cannabidiol-novel-food": [
    "EFSA 為大麻二酚（CBD）作為新興食品設定暫定安全攝取量",
    "歐盟執委會認定 CBD 屬「新興食品」，須符合相關法規",
    "影響：CBD 食品輸歐業者須注意申報程序",
  ],
  "https://www.efsa.europa.eu/en/news/efsa-provides-rapid-risk-assessment-cereulide-infant-formula": [
    "因應跨國嬰兒配方奶 cereulide 召回事件",
    "EFSA 由執委會委託作快速風險評估",
    "毒素來源：蠟樣芽孢桿菌（Bacillus cereus）",
    "對嬰兒族群風險評估為重點",
  ],
  "https://www.efsa.europa.eu/en/news/precautionary-global-recall-infant-nutrition-products-following-detection-bacillus-cereus": [
    "事件：嬰兒營養品全球預警性回收",
    "原因：檢出蠟樣芽孢桿菌毒素 cereulide",
    "涉及多批次、多產品、多品牌",
    "輸歐業者：嬰幼兒食品微生物管控應強化",
  ],
  "https://www.efsa.europa.eu/en/news/lectins-food-undercooked-beans-pose-health-risk-says-efsa": [
    "未充分烹煮的豆類含凝集素（lectins），可致嘔吐、腹瀉",
    "EFSA 應執委會請求進行此評估",
    "高危族群：消費生豆類沙拉、嫩芽食品",
    "建議：豆類煮沸 10 分鐘以上可破壞凝集素",
  ],
  "https://www.efsa.europa.eu/en/news/meat-intended-freezing-efsa-assesses-bacterial-growth-meat-it-reaches-consumers": [
    "EFSA 評估牛、羊、豬肉在冷藏、儲存、解凍時的細菌生長",
    "對冷凍肉品流通鏈業者有重要參考",
    "影響：包裝標示、儲存條件規範可能調整",
  ],
  "https://www.efsa.europa.eu/en/news/efsa-introduction-bird-flu-us-dairy-cattle-europe-very-unlikely-vigilance-urged": [
    "美國乳牛禽流感（H5N1）跨大西洋傳入歐洲機率：極低",
    "但 EFSA 仍呼籲提高警覺",
    "建議：強化乳牛、家禽生物安全",
  ],
  "https://www.efsa.europa.eu/en/news/avian-influenza-new-outbreaks-expected-europe-until-winter-ends": [
    "2025/9-11 月：歐洲家禽 442 起、野鳥 2,454 起 HPAI 案例",
    "涉及 29 個歐洲國家",
    "預期疫情持續至冬末春初",
    "對家禽輸歐業者影響：檢疫頻率可能提高",
  ],
  "https://www.efsa.europa.eu/en/news/serious-listeria-infections-rising-europe-eu-report-warns": [
    "歐洲嚴重李斯特菌感染呈上升趨勢",
    "主要污染源：蛋、肉、即食食品（RTE）",
    "業者應強化即食食品生產線消毒",
    "高風險族群：孕婦、新生兒、老人、免疫低下者",
  ],
  "https://www.efsa.europa.eu/en/news/have-your-say-dioxins-and-related-pcbs": [
    "EFSA 徵詢意見：戴奧辛與 dl-PCBs 的健康風險評估草案",
    "毒性：環境持久、在脂肪組織累積",
    "主要食物來源：肉類、乳製品、魚類",
    "業者可參與意見徵詢、表達技術觀點",
  ],
  "https://www.efsa.europa.eu/en/news/avian-influenza-europe-enhanced-surveillance-and-strict-biosecurity-needed-detections-surge": [
    "2025/9-11 月：歐洲 26 國野鳥 HPAI 檢出 1,443 起",
    "較去年同期 4 倍",
    "EFSA 呼籲：強化監測 + 嚴格生物安全",
    "對輸歐家禽業者：可能面臨更嚴格的進口檢疫",
  ],
  "https://www.efsa.europa.eu/en/news/delta-8-thc-efsa-sets-safe-intake-level": [
    "Delta-8 THC 是大麻屬植物中的次要精神活性成分",
    "EFSA 設定每日安全攝取量",
    "影響：CBD 油、大麻籽糖果等業者須注意 Δ8-THC 殘留",
  ],
  "https://www.efsa.europa.eu/en/news/time-action-joint-statement-eu-cross-agency-one-health-task-force-and-european-and-central": [
    "9 個國際組織於 World One Health Day 共同聲明",
    "4 大行動建議：監測、預防、防疫、跨領域協作",
    "推動歐洲與中亞地區 One Health 框架實施",
  ],
  "https://www.efsa.europa.eu/en/news/nikolaus-kriz-assumes-role-efsas-new-executive-director": [
    "奧地利籍獸醫 Nikolaus Kriz 接任 EFSA 執行長",
    "30 年國際食安、公衛經驗",
    "前任職務：歐盟食品創新部門主管",
  ],
  "https://www.efsa.europa.eu/en/infographics/welfare-animals-kept-fur-production": [
    "EFSA 評估毛皮養殖動物福利",
    "對象：水貂、狐狸、貉、龍貓",
    "結論：現行養殖條件難以保障動物福利",
    "對歐盟政策影響：未來可能加嚴或禁止毛皮農場",
  ],
  "https://www.efsa.europa.eu/en/infographics/welfare-beef-cattle-farm": [
    "EFSA 評估歐盟肉牛養殖福利",
    "涵蓋：室內圈養、放牧、飼料育肥三種模式",
    "重點建議：增加活動空間、減少集約飼養壓力",
  ],
  "https://www.efsa.europa.eu/en/news/keeping-plant-pests-out-eu": [
    "EFSA 修訂歐盟「優先檢疫害蟲」名單",
    "130 位專家參與評估",
    "對台灣輸歐農產品：檢疫項目可能異動",
  ],
  "https://www.efsa.europa.eu/en/news/fluoride-safety-updated-intake-levels-all-ages": [
    "EFSA 全面重新評估各年齡層氟攝取安全量",
    "涵蓋：飲水、食物、加氟食鹽、含氟牙膏",
    "影響：嬰幼兒族群安全攝取量更新",
    "對食品業者：強化食品中氟含量檢測",
  ],
  "https://www.efsa.europa.eu/en/news/have-your-say-estragole-fennel-seed-preparations": [
    "EFSA 徵詢意見：茴香籽製品 estragole（草蒿腦）健康風險",
    "包含茴香茶等草本飲品",
    "Estragole 屬潛在致癌物",
    "業者可表達技術意見",
  ],
  # EFSA Podcasts / Data viz / 短資訊（補充版）
  "https://multimedia.efsa.europa.eu/pesticides-report-2024/index.html": [
    "EFSA 2024 歐盟農藥殘留年度報告 — 互動式視覺化版本",
    "可依國家、產品、農藥種類查詢",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-37-no-secret-sauce-recipe-transparent-science": [
    "EFSA Podcast 第 37 集 — 開放科學與文件公開",
    "討論法律觀點下的科學透明度",
  ],
  "https://www.efsa.europa.eu/en/multimedia/pesticides-scroller": [
    "EFSA 互動式資訊：歐盟農藥的核准與監管流程",
  ],
  "https://www.efsa.europa.eu/en/infographics/efsas-scientific-opinion-welfare-turkeys-farm": [
    "EFSA 火雞養殖福利圖卡 — 室內、有頂遮陽棚、有戶外活動空間三種模式比較",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-36-nice-m-eat-you-what-are-alternative-proteins": [
    "EFSA Podcast 第 36 集 — 替代蛋白質（豆類、麵包蟲、培養肉）",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-35-bean-there-cooked-are-raw-legumes-safe": [
    "EFSA Podcast 第 35 集 — 生豆類與凝集素的食安",
  ],
  "https://www.efsa.europa.eu/en/infographics/foodborne-diseases-europe-whats-really-making-you-sick": [
    "EFSA One Health 2024 食源性疾病重點圖卡",
  ],
  "https://multimedia.efsa.europa.eu/drvs/index.htm": [
    "EFSA 營養素參考攝取量（DRV）互動查詢工具",
    "含新版氟攝取上限",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-34-cost-origin-taste-what-influences-our-food-choices": [
    "EFSA Podcast 第 34 集 — 食品選擇影響因素",
  ],
  "https://www.efsa.europa.eu/en/infographics/closer-look-pesticides-food": [
    "EFSA 圖卡：食品中農藥監測重點",
  ],
  "https://www.efsa.europa.eu/en/news/have-your-say-complete-efsa-journal-survey": [
    "EFSA 期刊讀者意見徵詢（5-10 分鐘）",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-33-exposure-matters-why-dose-makes-poison": [
    "EFSA Podcast 第 33 集 — 劑量決定毒性",
  ],
  "https://www.efsa.europa.eu/en/interactive-pages/eurobarometer": [
    "歐盟 Eurobarometer 食安認知互動儀表板（2022, 2025）",
  ],
  "https://www.efsa.europa.eu/en/infographics/2025-eurobarometer-food-safety-eu-infographic": [
    "2025 歐盟 Eurobarometer 食安認知圖卡",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-32-data-vs-stereotypes-what-europeans-eat": [
    "EFSA Podcast 第 32 集 — 用數據檢視歐洲人的飲食",
  ],
  "https://www.efsa.europa.eu/en/no-bird-flu": [
    "EFSA #NoBirdFlu 倡議活動：強化農場生物安全",
  ],
  "https://www.efsa.europa.eu/en/news/nobirdflu-clear-communications-better-biosecurity": [
    "EFSA：清楚的溝通可強化禽流感生物安全",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-31-sizzling-summers-bbq-safety-served-hot": [
    "EFSA Podcast 第 31 集 — 夏季 BBQ 食安",
  ],
  "https://www.efsa.europa.eu/en/podcast/episode-30-food-supplements-add-or-not-add": [
    "EFSA Podcast 第 30 集 — 營養補充品的功效與限制",
  ],
  "https://www.efsa.europa.eu/en/news/presscorner": [
    "EFSA 新聞中心入口",
  ],
  "https://www.youtube.com/watch?v=pWH3et1Y26U": [
    "EFSA 機構介紹影片：科學、安全食品、永續",
  ],

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
