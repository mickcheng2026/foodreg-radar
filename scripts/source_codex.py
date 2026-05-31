"""Codex Alimentarius (FAO/WHO 國際食品法典) 標準目錄

從 FAO 官方三份清單（標準 / 作業規範 / 準則）抓取真實標準代碼、標題、委員會、年份，
只收「橫向法規類」（全部 CXC 作業規範 + CXG 準則 + 橫向委員會的 CXS 通則），
排除單一商品標準（罐頭、乳品、魚等），避免稀釋。

連結用 FAO sh-proxy PDF 命名規則組出（與既有已驗證連結同一格式）。
抓取失敗時退回 CURATED_FALLBACK，確保流程不中斷。
"""
from __future__ import annotations
import re
import urllib.parse as _up
from common import fetch, clean_text, strip_tags, make_item

LIST_PAGES = [
    "https://www.fao.org/fao-who-codexalimentarius/codex-texts/list-standards/en/",
    "https://www.fao.org/fao-who-codexalimentarius/codex-texts/codes-of-practice/en/",
    "https://www.fao.org/fao-who-codexalimentarius/codex-texts/guidelines/en/",
]

ROW_RE = re.compile(
    r'<td nowrap>(CX[SCG]\s*\d+-\d{4})</td><td>(.*?)</td><td>(.*?)</td><td align="center">(\d{4})</td>',
    re.DOTALL,
)

# 橫向（跨商品）委員會 → 收錄；其餘（商品別）CXS 不收。CXC/CXG 一律收。
HORIZONTAL_COMMITTEES = {
    "CCFL", "CCFA", "CCCF", "CCFH", "CCMAS", "CCNFSDU",
    "CCPR", "CCRVDF", "CCGP", "CCNMW", "CCFICS",
}

COMMITTEE_ZH = {
    "CCFL": "食品標示", "CCFA": "食品添加物", "CCCF": "污染物與毒素",
    "CCFH": "食品衛生", "CCMAS": "分析與抽樣方法", "CCNFSDU": "營養與特殊膳食食品",
    "CCPR": "農藥殘留", "CCRVDF": "動物用藥殘留", "CCGP": "一般原則",
    "CCNMW": "天然礦泉水", "CCFICS": "進出口檢驗與驗證",
    "CCFFV": "新鮮蔬果", "CCMMP": "乳與乳製品", "CCFFP": "魚與水產品",
    "CCPFV": "加工蔬果", "CCCPL": "穀物與豆類", "CCSCH": "香辛料與草本",
    "CCFO": "油脂", "CCS": "糖類", "CCVP": "蔬菜蛋白", "CCSB": "自然礦泉水",
}

# 現有精緻中文摘要（依代碼前綴比對覆蓋，保留人工品質）
CURATED = {
    "CXS 1-1985": {
        "title_zh": "CXS 1-1985 預先包裝食品標示通則",
        "bullets": [
            "全球預包裝食品標示通則",
            "規範產品名稱、成分、淨重、保存期限、製造商",
            "各國食品標示法規多以此為基礎",
            "輸出國際時必備合規參考",
        ],
    },
    "CXS 192-1995": {
        "title_zh": "CXS 192-1995 食品添加物通則",
        "bullets": [
            "Codex 對食品添加物的綜合性標準",
            "規範各類食品中各種添加物的最大使用量",
            "持續更新，最新修訂為近年",
            "與台灣食品添加物使用範圍標準對接",
        ],
    },
    "CXS 193-1995": {
        "title_zh": "CXS 193-1995 食品與飼料中污染物與毒素通則",
        "bullets": [
            "Codex 污染物與毒素標準",
            "涵蓋鎘、鉛、汞、砷、黴菌毒素、丙烯醯胺等",
            "各國重金屬與污染物限量法規多參考此",
            "近期更新：嬰幼兒食品砷限量下修",
        ],
    },
    "CXC 1-1969": {
        "title_zh": "CXC 1-1969 食品衛生通則（含 HACCP 附錄）",
        "bullets": [
            "全球 HACCP 標準的源頭",
            "規範食品衛生、HACCP 七大原則",
            "ISO 22000 與各國 HACCP 規範均參考此文件",
            "2020/2022 修訂，加強過敏原管理",
        ],
    },
    "CXS 234-1999": {
        "title_zh": "CXS 234-1999 推薦分析與抽樣方法",
        "bullets": [
            "各類食品的官方檢驗方法",
            "供各國檢驗實驗室參考",
            "與食品檢驗法規搭配使用",
        ],
    },
    "CXC 53-2003": {
        "title_zh": "CXC 53-2003 新鮮蔬果衛生作業規範",
        "bullets": [
            "新鮮蔬果生產、處理、運輸衛生規範",
            "涵蓋初級生產到零售階段",
            "輸出蔬果業者必備合規參考",
        ],
    },
    "CXG 2-1985": {
        "title_zh": "CXG 2-1985 營養標示準則",
        "bullets": [
            "Codex 營養標示準則",
            "規範營養素含量標示方式、每日參考值",
            "各國營養標示（含台灣包裝營養標示）多參考此",
        ],
    },
}

# 額外保留的非清單項目（資料庫、入口）
EXTRA = [
    {
        "code": "MRL-DB",
        "title": "Codex Maximum Residue Limits (MRL) Database",
        "title_zh": "Codex 農藥殘留容許量資料庫",
        "url": "https://www.fao.org/fao-who-codexalimentarius/codex-texts/dbs/pestres/en/",
        "date": "2026-01-01",
        "committee": "CCPR",
        "bullets": [
            "全球農藥殘留容許量參考資料庫",
            "可查 5000+ 農藥 × 食品的 MRL",
            "持續更新，2 年一次大更新",
            "輸出業者可作為國際標準對照",
        ],
    },
]


def _pdf_url(code: str) -> str:
    """依 FAO sh-proxy 命名規則組出 PDF 連結（與既有已驗證連結同格式）"""
    prefix, rest = code.split()
    num = rest.split("-")[0]
    folder = f"{prefix}+{rest}"
    fname = f"{prefix}_{int(num):03d}e.pdf"
    inner = f"https://workspace.fao.org/sites/codex/Standards/{folder}/{fname}"
    # 第一次保留 "+"（資料夾分隔），第二次再整體編碼 → 與既有已驗證連結格式一致
    return ("https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url="
            + _up.quote(_up.quote(inner, safe="+"), safe=""))


def _tags(title: str, title_zh: str, committee: str) -> list[str]:
    tags = ["Codex", "國際標準"]
    blob = (title + " " + title_zh).lower()
    rules = [
        ("食品添加物", ("additive", "添加物")),
        ("污染物", ("contaminant", "污染物", "toxin")),
        ("HACCP", ("hygien", "haccp", "衛生")),
        ("標示", ("labell", "標示")),
        ("農藥殘留", ("pesticide", "residue", "農藥", "mrl")),
        ("動物用藥", ("veterinary", "動物用藥")),
        ("營養", ("nutrition", "營養", "dietary")),
        ("進出口", ("import", "export", "進出口", "inspection")),
        ("檢驗方法", ("method", "analysis", "sampling", "檢驗", "分析")),
    ]
    for tag, kws in rules:
        if any(k in blob for k in kws) and tag not in tags:
            tags.append(tag)
    zh = COMMITTEE_ZH.get(committee)
    if zh and zh not in tags:
        tags.append(zh)
    return tags[:5]


def _make(title, title_zh, url, year, committee, bullets):
    item = make_item(
        source="codex",
        source_label="Codex",
        source_color="rose",
        title=title,
        url=url,
        date=f"{year}-01-01",
        summary=title_zh or title,
        tags=_tags(title, title_zh, committee),
    )
    if title_zh:
        item["title_zh"] = title_zh
    item["ai_summary"] = bullets
    return item


def _scrape() -> list[dict]:
    seen: dict[str, dict] = {}
    for page in LIST_PAGES:
        html = fetch(page, timeout=25)
        rows = ROW_RE.findall(html)
        for code_raw, title_raw, comm_raw, year in rows:
            code = re.sub(r"\s+", " ", code_raw).strip()
            prefix = code.split()[0]
            committee = clean_text(strip_tags(comm_raw)).strip()
            # CXS 只收橫向委員會；CXC/CXG 全收
            if prefix == "CXS" and committee not in HORIZONTAL_COMMITTEES:
                continue
            title = clean_text(strip_tags(title_raw))
            if not title or code in seen:
                continue
            cur = CURATED.get(code, {})
            title_zh = cur.get("title_zh", "")
            bullets = cur.get("bullets") or [
                f"Codex {code}（{COMMITTEE_ZH.get(committee, committee)}）",
                f"最新版本：{year} 年",
                "FAO/WHO 國際食品法典標準，可作為各國法規與輸出對照參考",
            ]
            seen[code] = _make(f"{code} {title}", title_zh,
                               _pdf_url(code), year, committee, bullets)
    return list(seen.values())


# 抓取失敗時的最小退回清單（既有 7 筆核心）
CURATED_FALLBACK = [
    {"code": "CXS 1-1985", "committee": "CCFL", "year": "2024",
     "title": "CXS 1-1985 General Standard for the Labelling of Prepackaged Foods"},
    {"code": "CXS 192-1995", "committee": "CCFA", "year": "2024",
     "title": "CXS 192-1995 General Standard for Food Additives"},
    {"code": "CXS 193-1995", "committee": "CCCF", "year": "2024",
     "title": "CXS 193-1995 General Standard for Contaminants and Toxins in Food and Feed"},
    {"code": "CXC 1-1969", "committee": "CCFH", "year": "2022",
     "title": "CXC 1-1969 General Principles of Food Hygiene (含 HACCP 附錄)"},
    {"code": "CXS 234-1999", "committee": "CCMAS", "year": "2023",
     "title": "CXS 234-1999 Recommended Methods of Analysis and Sampling"},
    {"code": "CXC 53-2003", "committee": "CCFFV", "year": "2022",
     "title": "CXC 53-2003 Code of Hygienic Practice for Fresh Fruits and Vegetables"},
    {"code": "CXG 2-1985", "committee": "CCFL", "year": "2024",
     "title": "CXG 2-1985 Guidelines on Nutrition Labelling"},
]


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        items = _scrape()
    except Exception as e:
        print(f"  [Codex] 官方清單抓取失敗，退回核心清單：{e}")

    if len(items) < 7:
        # 退回核心清單
        for s in CURATED_FALLBACK:
            code = s["code"]
            cur = CURATED.get(code, {})
            items.append(_make(
                s["title"], cur.get("title_zh", ""),
                _pdf_url(code), s["year"], s["committee"],
                cur.get("bullets") or [f"Codex {code} 核心標準"],
            ))

    # 加上額外入口（MRL DB 等）
    for e in EXTRA:
        items.append(_make(e["title"], e["title_zh"], e["url"], e["date"][:4],
                           e["committee"], e["bullets"]))

    print(f"  [Codex] 收錄 {len(items)} 條（橫向法規 + 核心）")
    return items


if __name__ == "__main__":
    import json
    its = crawl()
    print(f"\n共 {len(its)} 條")
    print(json.dumps(its[:4], ensure_ascii=False, indent=2))
