"""美國 FDA 食品召回爬蟲 — 改用 openFDA 官方 JSON API

來源：https://api.fda.gov/food/enforcement.json
- 免 API key、免費、官方維護
- 結構化資料（公司名、產品、原因、分級、流通範圍）
- 不會像爬 HTML 那樣因網站改版而壞

每筆會自動產生：
- title:        英文官方產品描述
- title_zh:     根據召回原因關鍵字產生的中文短標
- summary:     英文結構化摘要
- ai_summary:  中文條列重點（從欄位機械翻譯）
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from common import clean_text, make_item, DEFAULT_HEADERS

API_URL = "https://api.fda.gov/food/enforcement.json"
LIMIT = 1000  # openFDA 單次最多 1000；近 1 年食品召回約 800-1200 筆
RECALL_DEEP_LINK = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


# 召回原因常見關鍵字 → 中文
TRANSLATE_REASON = [
    ("undeclared allergen", "未標示過敏原"),
    ("foreign object", "異物（金屬、玻璃、塑膠等）"),
    ("foreign material", "異物"),
    ("metal", "金屬碎片"),
    ("glass", "玻璃"),
    ("plastic", "塑膠"),
    ("salmonella", "沙門氏菌污染"),
    ("listeria", "李斯特菌污染"),
    ("e. coli", "大腸桿菌污染"),
    ("e.coli", "大腸桿菌污染"),
    ("staphyl", "葡萄球菌"),
    ("clostridium", "肉毒桿菌相關"),
    ("botul", "肉毒桿菌"),
    ("hepatitis", "A 型肝炎病毒"),
    ("norovirus", "諾羅病毒"),
    ("mislabel", "標示錯誤"),
    ("mislabeled", "標示錯誤"),
    ("incorrect label", "標示錯誤"),
    ("nutritional label", "營養標示問題"),
    ("nutrition facts", "營養標示問題"),
    ("expired", "效期問題"),
    ("temperature abuse", "溫度控制不當"),
    ("yeast", "酵母 / 黴菌"),
    ("mold", "黴菌"),
    ("aflatoxin", "黃麴毒素"),
    ("histamine", "組織胺"),
    ("pesticide", "農藥殘留"),
    ("heavy metal", "重金屬"),
    ("lead", "鉛"),
    ("arsenic", "砷"),
    ("hidden drug", "摻偽藥物"),
    ("unapproved drug", "未核准藥物成分"),
    ("benzene", "苯類化合物"),
    # 過敏原細節
    ("milk", "牛奶過敏原"),
    ("soy", "大豆過敏原"),
    ("wheat", "小麥過敏原"),
    ("gluten", "麩質"),
    ("egg", "蛋過敏原"),
    ("peanut", "花生過敏原"),
    ("tree nut", "堅果過敏原"),
    ("cashew", "腰果過敏原"),
    ("almond", "杏仁過敏原"),
    ("pecan", "胡桃過敏原"),
    ("walnut", "核桃過敏原"),
    ("hazelnut", "榛果過敏原"),
    ("pistachio", "開心果過敏原"),
    ("fish", "魚類過敏原"),
    ("shellfish", "甲殼類過敏原"),
    ("sesame", "芝麻過敏原"),
]

CLASS_DESC_ZH = {
    "Class I":  "Class I 重大風險（恐致死或嚴重健康危害）",
    "Class II": "Class II 中度風險（可能造成可逆健康影響）",
    "Class III":"Class III 輕度風險（不太可能造成健康危害）",
    "Not Yet Classified": "尚未分級",
}


def translate_reason(reason: str) -> str:
    """從原因字串擷取關鍵字翻譯，盡量精準對應"""
    if not reason:
        return ""
    rl = reason.lower()
    matched = []
    for kw, zh in TRANSLATE_REASON:
        if kw in rl and zh not in matched:
            matched.append(zh)
    return "、".join(matched) if matched else ""


def yyyymmdd_to_iso(s: str) -> str | None:
    if not s or len(s) != 8 or not s.isdigit():
        return None
    try:
        return datetime.strptime(s, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def fetch_api(limit: int) -> list[dict]:
    from datetime import datetime, timedelta
    # 過濾近 1 年的召回（report_date >= 1 年前）
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    today = datetime.now().strftime("%Y%m%d")
    url = f"{API_URL}?search=report_date:[{one_year_ago}+TO+{today}]&limit={limit}&sort=report_date:desc"
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=_ctx) as r:
        return json.loads(r.read().decode("utf-8")).get("results", [])


def build_item(rec: dict) -> dict:
    firm = clean_text(rec.get("recalling_firm") or "")
    product = clean_text(rec.get("product_description") or "")
    reason_en = clean_text(rec.get("reason_for_recall") or "")
    reason_zh = translate_reason(reason_en)
    classification = rec.get("classification") or "Not Yet Classified"
    distribution = clean_text(rec.get("distribution_pattern") or "")
    recall_number = rec.get("recall_number") or ""
    status = rec.get("status") or ""
    date = yyyymmdd_to_iso(rec.get("report_date"))

    # 英文標題：公司 — 產品（前 80 字）— 召回原因（前 50 字）
    title_en_parts = []
    if firm:
        title_en_parts.append(firm)
        title_en_parts.append("recalls")
    short_product = product[:80] + ("..." if len(product) > 80 else "")
    if short_product:
        title_en_parts.append(short_product)
    if reason_en:
        title_en_parts.append("—")
        title_en_parts.append(reason_en[:60])
    title_en = " ".join(title_en_parts)

    # 中文標題：公司 + 產品類型猜測 + 原因
    title_zh_parts = []
    if firm:
        title_zh_parts.append(firm)
    title_zh_parts.append("召回")
    if reason_zh:
        title_zh_parts.append("—")
        title_zh_parts.append(reason_zh)
    elif reason_en:
        title_zh_parts.append("—")
        title_zh_parts.append(reason_en[:50])
    title_zh = " ".join(title_zh_parts)

    # 英文結構化 summary（原文）
    summary_en_parts = []
    if product:
        summary_en_parts.append(f"Product: {product[:200]}")
    if reason_en:
        summary_en_parts.append(f"Reason: {reason_en[:200]}")
    if distribution:
        summary_en_parts.append(f"Distribution: {distribution[:150]}")
    if recall_number:
        summary_en_parts.append(f"Recall #: {recall_number}")
    summary_en = " | ".join(summary_en_parts)

    # 中文 AI 摘要（從結構化欄位機械翻譯）
    ai_bullets = []
    if firm:
        loc = []
        if rec.get("city"): loc.append(rec["city"])
        if rec.get("state"): loc.append(rec["state"])
        loc_str = f"（{', '.join(loc)}）" if loc else ""
        ai_bullets.append(f"召回廠商：{firm}{loc_str}")
    if product:
        ai_bullets.append(f"產品：{product[:120]}")
    if reason_zh:
        ai_bullets.append(f"召回原因：{reason_zh}")
        if reason_en and reason_en[:80].lower() not in reason_zh.lower():
            ai_bullets.append(f"原因原文：{reason_en[:120]}")
    elif reason_en:
        ai_bullets.append(f"召回原因：{reason_en[:120]}")
    ai_bullets.append(f"分級：{CLASS_DESC_ZH.get(classification, classification)}")
    if distribution:
        ai_bullets.append(f"流通範圍：{distribution[:150]}")
    if recall_number:
        ai_bullets.append(f"召回編號：{recall_number}")

    # tags
    tags = ["召回"]
    if classification in CLASS_DESC_ZH:
        tags.append(classification)
    if "nationwide" in distribution.lower():
        tags.append("全美")
    if status == "Ongoing":
        tags.append("進行中")
    if reason_zh and ("過敏原" in reason_zh):
        tags.append("過敏原")
    if reason_zh and any(b in reason_zh for b in ("沙門", "李斯特", "大腸桿菌", "肉毒")):
        tags.append("微生物")
    if reason_zh and ("異物" in reason_zh):
        tags.append("異物")

    # URL：FDA 官方無逐筆深層連結，連到分類頁並用 hash 做書籤
    url = f"{RECALL_DEEP_LINK}#{recall_number}" if recall_number else RECALL_DEEP_LINK

    item = make_item(
        source="usfda",
        source_label="US FDA",
        source_color="blue",
        title=clean_text(title_en),
        url=url,
        date=date,
        summary=summary_en,
        tags=tags,
    )
    item["title_zh"] = clean_text(title_zh)
    item["ai_summary"] = ai_bullets
    return item


def crawl() -> list[dict]:
    try:
        results = fetch_api(LIMIT)
    except Exception as e:
        print(f"  [USFDA] openFDA API 失敗: {e}")
        return []

    items = [build_item(r) for r in results]
    print(f"  [USFDA] 從 openFDA API 抓到 {len(items)} 筆食品召回")
    return items


if __name__ == "__main__":
    items = crawl()
    print(json.dumps(items[:2], ensure_ascii=False, indent=2))
