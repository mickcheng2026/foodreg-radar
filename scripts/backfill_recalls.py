"""把 US FDA / 澳洲 FSANZ 的「固定格式召回」自動轉成乾淨的中文重點，寫進 ai_backfill.json。

只處理這兩個來源、且 body 為制式格式者：
  US FDA : Product: ... | Reason: ... | Distribution: ... | Recall #: ...
  FSANZ  : <原因敘述> | <範圍>

無法解析（格式不符）的就跳過，留給人工或規則式處理。零 API 費用。
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"
BACKFILL = ROOT / "data" / "ai_backfill.json"

sys.path.insert(0, str(ROOT / "scripts"))
from apply_ai_summaries import SUMMARIES as CURATED  # noqa: E402

# 原因關鍵字 → 中文（順序：specific → general）
REASON_MAP = [
    (r"clostridium botulinum|botulin|under-?process", "加工不足，恐滋生肉毒桿菌"),
    (r"salmonella", "可能遭沙門氏菌污染"),
    (r"listeria", "可能遭李斯特菌污染"),
    (r"escherichia coli|e\.?\s*coli", "可能遭大腸桿菌污染"),
    (r"hepatitis a", "可能遭A型肝炎病毒污染"),
    (r"norovirus", "可能遭諾羅病毒污染"),
    (r"cronobacter", "可能遭阪崎腸桿菌污染"),
    (r"foreign (?:matter|material|object)|metal|plastic|glass|rubber", "含異物"),
    (r"good manufacturing practice|cgmp|gmp", "違反GMP，恐有微生物污染風險"),
    (r"lead|heavy metal|cadmium|arsenic|mercury", "重金屬超標"),
    (r"mold|mould|yeast", "黴菌／酵母菌問題"),
    (r"mislabel|mis-?label|incorrect label|wrong label", "標示錯誤"),
    (r"unapproved|unauthori[sz]ed|new animal drug|new drug", "含未經核准之成分／用途"),
    (r"elevated|excess|exceed", "成分含量超標"),
]

# 過敏原關鍵字 → 中文
ALLERGEN_MAP = [
    (r"milk|dairy|casein|whey", "乳"),
    (r"egg", "蛋"),
    (r"peanut", "花生"),
    (r"tree ?nut|almond|walnut|cashew|pecan|hazelnut|pistachio", "堅果"),
    (r"soy|soya", "大豆"),
    (r"wheat|gluten", "小麥／麩質"),
    (r"sesame", "芝麻"),
    (r"\bfish\b", "魚"),
    (r"shellfish|crustacean|shrimp|crab|lobster", "甲殼類"),
    (r"sulfite|sulphite", "亞硫酸鹽"),
]

DIST_MAP = {
    "nationwide": "全美",
    "national": "全國",
}


def _translate_reason(reason: str) -> str:
    r = reason.lower()
    # 過敏原未標示
    if re.search(r"undeclared|not declared|not listed|fail(?:ure)? to declare|allergen|missing allergen", r):
        found = [zh for pat, zh in ALLERGEN_MAP if re.search(pat, r)]
        if found:
            return "未標示過敏原（" + "、".join(dict.fromkeys(found)) + "）"
        return "未標示過敏原"
    for pat, zh in REASON_MAP:
        if re.search(pat, r):
            return zh
    # 取不到就用原文（截短）
    return "召回原因：" + reason.strip()[:60]


def _translate_dist(dist: str) -> str:
    d = dist.strip()
    low = d.lower()
    for k, v in DIST_MAP.items():
        if low == k:
            return v
    if low.startswith("nationwide"):
        return "全美" + d[len("nationwide"):]
    return d[:80]


def _parse_usfda(body: str) -> list[str] | None:
    fields = {}
    for key in ("Product", "Reason", "Distribution", "Recall #"):
        m = re.search(rf"{re.escape(key)}:\s*(.*?)(?=\s*\|\s*(?:Product|Reason|Distribution|Recall #):|$)",
                      body, re.DOTALL)
        if m:
            fields[key] = m.group(1).strip()
    if "Reason" not in fields and "Product" not in fields:
        return None
    bullets = ["性質：美國 FDA 召回／市場下架通知"]
    if fields.get("Product"):
        bullets.append("產品：" + fields["Product"][:90])
    if fields.get("Reason"):
        bullets.append("原因：" + _translate_reason(fields["Reason"]))
    if fields.get("Distribution"):
        bullets.append("範圍：" + _translate_dist(fields["Distribution"]))
    return bullets if len(bullets) >= 2 else None


def _parse_fsanz(body: str, title: str) -> list[str] | None:
    parts = [p.strip() for p in body.split("|")]
    reason_txt = parts[0] if parts else body
    scope = parts[1] if len(parts) > 1 else ""
    # 去掉 "The recall is due to" 之類前綴後再判斷
    bullets = ["性質：澳洲 FSANZ 食品召回"]
    if title:
        bullets.append("產品：" + title[:90])
    bullets.append("原因：" + _translate_reason(reason_txt))
    if scope:
        bullets.append("範圍：" + _translate_dist(scope))
    return bullets


def main():
    items = json.loads(DATA.read_text(encoding="utf-8"))["items"]
    bf = json.loads(BACKFILL.read_text(encoding="utf-8")) if BACKFILL.exists() else {}
    n_us = n_au = n_skip = 0
    for it in items:
        url = it.get("url")
        src = it.get("source_label", "")
        body = (it.get("summary") or "").strip()
        if not url or len(body) < 30 or url in CURATED or url in bf:
            continue
        if src == "US FDA":
            b = _parse_usfda(body)
            if b:
                bf[url] = b
                n_us += 1
            else:
                n_skip += 1
        elif src == "澳洲 FSANZ":
            b = _parse_fsanz(body, it.get("title", ""))
            if b:
                bf[url] = b
                n_au += 1
            else:
                n_skip += 1
    BACKFILL.write_text(json.dumps(bf, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"US FDA 解析 {n_us} 筆、FSANZ 解析 {n_au} 筆、無法解析跳過 {n_skip} 筆")
    print(f"回填檔現有 {len(bf)} 筆")


if __name__ == "__main__":
    main()
