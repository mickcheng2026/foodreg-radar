"""出口指南 — 台灣業者把產品送進各國的完整步驟清單

不是法規條文，而是「實際要做什麼」的有序步驟清單。
每國一張卡片，含：
  - 主要主管機關
  - 申辦系統
  - 順序步驟（Step 1 → Step N）
  - 常見退運原因
  - 預估時程
"""
from __future__ import annotations
from common import make_item


EXPORT_GUIDES = [
    # === 出口美國 ===
    {
        "country": "美國",
        "title": "🚢 出口美國 完整步驟（台灣 → US）",
        "title_zh": "出口美國 完整步驟（台灣 → US）",
        "url": "https://www.fda.gov/food/importing-food-products-united-states",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：確認產品類別 — 食品/添加物/包材，是否為 FDA 或 USDA 管轄（肉禽蛋走 USDA、其他走 FDA）",
            "Step 2：到 FDA Food Facility Registration 系統註冊您的製造廠（兩年一次），指定 U.S. Agent",
            "Step 3：檢查您是否在 Import Alert (DWPE) 紅名單上 — 若在，先解除才能輸美",
            "Step 4：對方美國進口商必須符合 FSVP（國外供應商驗證計畫）— 配合提供文件",
            "Step 5：到貨前 4-8 小時透過 PNSI 系統做 Prior Notice 事前通報",
            "Step 6：到港時 FDA 抽驗（依產品類別風險）— 重點檢查標示、農藥、微生物、過敏原",
            "預估時程：首次出口準備 2-3 個月（含設施註冊、文件準備）",
            "常見退運原因：標示英文不全、未事前通報、農藥超標、過敏原未標、設施未註冊",
            "輸美業者主要對接：美方進口商（FSVP 由進口商負責）",
        ],
    },
    # === 出口日本 ===
    {
        "country": "日本",
        "title": "🚢 出口日本 完整步驟（台灣 → JP）",
        "title_zh": "出口日本 完整步驟（台灣 → JP）",
        "url": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/yunyu_kanshi/index.html",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：確認您的產品輸日有沒有特殊限制 — 例如豬肉因豬瘟限制、植物源需檢疫",
            "Step 2：日本進口商註冊 FAINS（食品輸入届出線上系統）",
            "Step 3：對應日本「正面表列制度」— 確認您的產品所含農藥、添加物全部都在日本核准清單上（未列名一律 0.01 ppm）",
            "Step 4：準備衛生證明書 — 由台灣食藥署核發",
            "Step 5：產品包裝符合日本食品表示法 — 全日文標示，含原材料、過敏原、營養成分",
            "Step 6：到貨前向日本港埠食品衛生監視員提交「食品等輸入届出書」",
            "Step 7：抽驗（如有需要）— 重點檢查農藥、動物用藥、輻射、添加物",
            "Step 8：清關 + 配送",
            "預估時程：首次出口 1-2 個月（含產品配方對照、標示翻譯）",
            "常見退運原因：未列名農藥/添加物、輻射超標（東日本震災後特別敏感）、標示不符",
            "建議：新產品輸日先寫信給「事前相談窗口」確認可行性",
        ],
    },
    # === 出口歐盟 ===
    {
        "country": "歐盟",
        "title": "🚢 出口歐盟 完整步驟（台灣 → EU）",
        "title_zh": "出口歐盟 完整步驟（台灣 → EU）",
        "url": "https://food.ec.europa.eu/food-safety_en",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：確認產品是否需 EFSA 評估 — 一般食品免，新興食品 (Novel Food)、基改、添加物需要",
            "Step 2：歐盟進口商需在 TRACES NT 註冊（動植物源食品強制）",
            "Step 3：取得 CHED 文件 — 動植物源需 Common Health Entry Document",
            "Step 4：產品包裝符合歐盟標示規範 — 24 種官方語言至少一種，含營養標示、過敏原、原產地",
            "Step 5：透過 Border Control Post (BCP) 通關 — 動物源、植物源、加工食品有不同 BCP",
            "Step 6：邊境官方檢驗（依風險）— RASFF 系統追蹤所有不合格案件",
            "Step 7：清關 + 配送",
            "預估時程：首次出口 2-4 個月（含 CHED 申請、標示翻譯）",
            "常見退運原因：黃麴毒素、農藥超標、未經核准 GMO、Novel Food 未申請",
            "強烈建議：先到 RASFF 系統查您產品類別過去被通報案例，避免重蹈覆轍",
            "輸歐茶葉重點：注意 Anthraquinone、農藥殘留標準（比台灣嚴）",
        ],
    },
    # === 出口澳洲 ===
    {
        "country": "澳洲",
        "title": "🚢 出口澳洲 完整步驟（台灣 → AU）",
        "title_zh": "出口澳洲 完整步驟（台灣 → AU）",
        "url": "https://www.agriculture.gov.au/biosecurity-trade/import/goods/food",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：到 BICON（澳洲生物安全進口條件查詢）查您的產品 HS Code — 看是否需檢疫、燻蒸、許可",
            "Step 2：確認您的產品屬於 risk food（嬰兒、即食、海鮮 — 高抽驗率）或 surveillance food（一般 — 低抽驗率）",
            "Step 3：澳洲進口商註冊登記",
            "Step 4：產品符合澳紐食品標準（FSANZ Code）— 含營養標示、過敏原、原產地",
            "Step 5：到貨後 DAFF 進行 IFIS 進口食品檢驗",
            "Step 6：抽驗結果合格 → 清關；不合格 → Failed Food Report 公告",
            "預估時程：首次出口 1-2 個月（產品分類確認 + 標示）",
            "常見退運原因：標示不符（過敏原、營養）、微生物超標、農藥",
            "特殊：新興食品 (Novel Food) 需 FSANZ 事前評估認可",
            "輸澳水產重點：先看您的產地有沒有澳洲核可、貝類有額外管制",
        ],
    },
    # === 出口香港 ===
    {
        "country": "香港",
        "title": "🚢 出口香港 完整步驟（台灣 → HK）",
        "title_zh": "出口香港 完整步驟（台灣 → HK）",
        "url": "https://www.cfs.gov.hk/tc_chi/import/",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：找香港註冊食物入口商（強制 — 您不能直接賣）",
            "Step 2：確認是否為高風險食物 — 肉類、家禽、奶類、奶粉、配方奶需 CFS 進口許可",
            "Step 3：肉品/禽類：源廠必須在 CFS 核准廠商名單上",
            "Step 4：取得衛生證明書 — 台灣衛福部食藥署核發",
            "Step 5：產品標示符合香港《食物及藥物（成分組合及標籤）規例》— 中英文標示",
            "Step 6：透過註冊入口商辦理通關，CFS 抽驗",
            "預估時程：首次出口 2-4 週（最快的市場）",
            "常見退運原因：標示繁中/英文錯誤、未透過註冊入口商、肉品來源未核可",
            "好消息：香港是台灣食品最易進入的市場 — 法規鬆、文化相通、距離近",
            "輸港蔬果重點：農藥殘留須符合香港標準（與 Codex 接軌）",
        ],
    },
    # === 出口馬來西亞 ===
    {
        "country": "馬來西亞",
        "title": "🚢 出口馬來西亞 完整步驟（台灣 → MY）",
        "title_zh": "出口馬來西亞 完整步驟（台灣 → MY）",
        "url": "https://fosim.moh.gov.my/",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：馬國進口商註冊 FoSIM（食品安全資訊系統）— 強制",
            "Step 2：確認您產品是否涉及清真 — 若是肉類、含明膠、含酒精成分必須走 Halal 認證",
            "Step 3：清真認證 — 若有 MUI（印尼）等 JAKIM 承認的認證可直接用；否則需要新做 JAKIM 認證",
            "Step 4：產品符合馬來西亞食品條例 1985（Food Regulations 1985）— 添加物、污染物、標示",
            "Step 5：標示符合馬國規定 — 馬來文 / 英文，含產品名、成分、淨重、製造商、效期",
            "Step 6：透過 FoSIM 線上申報，配合 BKKM 抽驗",
            "預估時程：首次出口 2-4 個月（含清真認證評估）",
            "常見退運原因：清真認證不被承認、含未核准添加物、標示不符、效期過短",
            "特別注意：馬國穆斯林市場大，幾乎所有食品都會被詢問是否清真",
        ],
    },
    # === 一般出口共通流程 ===
    {
        "country": "國際",
        "title": "🚢 食品出口 國際通用 7 大步驟",
        "title_zh": "食品出口 國際通用 7 大步驟",
        "url": "https://www.fao.org/fao-who-codexalimentarius/codex-texts/codes-of-practice/en/",
        "date": "2026-05-30",
        "bullets": [
            "Step 1：確認目標市場的食品法規 — 看您產品所含成分有沒有禁/限用",
            "Step 2：取得必要的國際認證 — HACCP、ISO 22000、FSSC 22000、Halal、Kosher、有機",
            "Step 3：完成產品檢驗 — 重金屬、農藥、微生物、添加物、過敏原",
            "Step 4：準備出口文件 — 衛生證明書（CFS）、原產地證明、INVOICE、PACKING LIST",
            "Step 5：產品標示在地化 — 對應目標國語言、法規、營養標示格式",
            "Step 6：找當地進口商 — 多數國家強制透過註冊進口商",
            "Step 7：到貨 + 通關 + 配送 — 對應目標國的事前通報、抽驗、海關清關",
            "💡 建議優先順序：先做 HACCP（國內合法基礎）→ 申請輸出衛生證明 → 再對應目標國細項",
            "💡 國際認證對照：日本 / 美國 / 歐盟 = ISO 22000 普遍接受；馬國 = 加 Halal；歐盟 = 加 BRCGS",
            "💡 退運處理：保留所有抽驗、運輸紀錄 — 不只能申訴，還能找出根因避免重複",
        ],
    },
]


def crawl() -> list[dict]:
    items = []
    for s in EXPORT_GUIDES:
        tags = ["出口指南", s["country"]]
        item = make_item(
            source="export_guide",
            source_label="出口指南",
            source_color="indigo",
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
    print(f"  [Export Guide] 各國出口完整步驟 {len(items)} 條")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:1], ensure_ascii=False, indent=2))
