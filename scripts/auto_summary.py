"""對沒有摘要、或仍是舊「占位型」摘要的 item，從標題自動產生「自然語句」重點。

僅用模式比對，不呼叫 AI。產出風格比照人工/AI 摘要（短句、可掃讀），例如：
  預告修正「健康食品之調節血糖功能評估方法」（草案）
  領域：健康食品
  狀態：草案、公開徵詢意見中，尚未正式施行

設計重點：
- 只會「升級」舊占位摘要（含「類型：/主題：/標的法規：/原文標題：/原文節錄：」等機器味標記）
  或完全沒有摘要的 item；對已寫好的人工/AI 摘要一律不動。
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"

# 舊占位格式的專屬標記（人工/AI 摘要不會用這些開頭）→ 用來判斷「可被升級」
OLD_MARKERS = ("類型：", "主題：", "標的法規：", "原文標題：", "原文節錄：")

# 文件類型（順序：specific → general）
TYPE_PATTERNS = [
    (r"第[一二三四五六七八九十百\d]+次預告", "二次以上預告修正"),
    (r"預告\s*修正", "預告修正"),
    (r"預告\s*訂定", "預告訂定"),
    (r"預告\s*廢止", "預告廢止"),
    (r"預告\s*增訂", "預告增訂"),
    (r"預告", "預告"),
    (r"公告\s*修正", "公告修正"),
    (r"公告\s*訂定", "公告訂定"),
    (r"公告\s*廢止", "公告廢止"),
    (r"公告\s*增訂", "公告增訂"),
    (r"公告", "公告"),
    (r"修正", "修正"),
    (r"廢止", "廢止"),
    (r"訂定", "訂定"),
    (r"增訂", "增訂"),
    (r"新增", "新增"),
    (r"延長", "延長"),
]

# 「這是新聞/說明」類，標題本身即重點，不套用「訂定法規」句型
NEWS_PATTERNS = [
    (r"駁斥|不實|闢謠|謠言|假訊息", "澄清闢謠"),
    (r"提醒|籲|呼籲|注意", "提醒"),
    (r"通報|警訊|示警", "警示"),
    (r"懶人包|圖卡|一次看", "懶人包"),
    (r"說明|回應", "說明稿"),
]

# 主題領域
TOPIC_PATTERNS = [
    (r"食品[中之]?動物用藥|動物用藥|動物用[藥]", "動物用藥"),
    (r"農藥殘留|農藥", "農藥殘留"),
    (r"食品添加物|添加物", "食品添加物"),
    (r"基因改造|基改", "基因改造"),
    (r"食品(?:廣告|標示|標籤)|廣告不實|標示", "標示/廣告"),
    (r"檢驗方法|檢驗", "檢驗方法"),
    (r"輸入|輸出|進口|出口|邊境|報驗", "進出口"),
    (r"HACCP|食品安全管制系統", "HACCP"),
    (r"GMP|優良製造", "GMP"),
    (r"化粧品|化妝品", "化粧品"),
    (r"醫療器材", "醫療器材"),
    (r"健康食品|特殊營養|膠囊錠狀", "健康食品"),
    (r"中藥", "中藥"),
    (r"藥品|西藥|管制藥|藥事", "藥品/藥事"),
    (r"營養標示|紅黃綠燈", "營養標示"),
    (r"塑化劑|重金屬|鎘|鉛|砷|戴奧辛", "污染物"),
    (r"沙門|李斯特|大腸桿菌|微生物|病原", "微生物"),
    (r"食品中毒|食物中毒", "食品中毒"),
    (r"召回|回收|下架", "召回/下架"),
    (r"輻射|核能|核災", "輻射"),
    (r"基層衛生|偏遠地區", "醫療資源"),
]


def _detect(patterns, text):
    for pat, label in patterns:
        if re.search(pat, text):
            return label
    return None


def generate_bullets(title: str, body: str = "") -> list[str]:
    """從標題（與少數有內文者的 body）產生 2-4 條自然語句重點"""
    title = (title or "").strip()
    if not title:
        return []

    bullets: list[str] = []
    quoted = re.findall(r"「([^」]+)」", title)
    target = quoted[0].strip() if quoted else ""
    is_draft = "草案" in title
    org = "衛生福利部" if ("衛生福利部" in title or "衛福部" in title) else ""

    news_kind = _detect(NEWS_PATTERNS, title)
    doc_type = _detect(TYPE_PATTERNS, title)

    # ── 主重點 ──
    if news_kind == "澄清闢謠":
        bullets.append("性質：澄清稿 — 官方駁斥網路流傳的不實訊息")
        if target:
            bullets.append(f"涉及說法：「{target[:50]}」")
    elif news_kind and not doc_type:
        # 提醒/警示/懶人包/說明：標題即重點
        bullets.append(f"性質：{news_kind}")
        bullets.append(title[:80])
    elif doc_type:
        if target:
            lead = f"{org}{doc_type}「{target[:60]}」"
            if is_draft and "草案" not in lead:
                lead += "（草案）"
        else:
            # 沒有「」標的：直接用標題當主句，避免切壞長複合標題
            lead = title[:90]
        bullets.append(lead)
        # 附表資訊
        atts = re.findall(r"附表[一二三四五六七八九十\d]+", title)
        if atts:
            bullets.append("涉及條文：" + "、".join(dict.fromkeys(atts)))
    else:
        bullets.append(f"「{target[:60]}」" if target else title[:90])

    # ── 領域 ──
    topics = []
    for pat, topic in TOPIC_PATTERNS:
        if re.search(pat, title) and topic not in topics:
            topics.append(topic)
    if topics:
        bullets.append("領域：" + "、".join(topics[:3]))

    # ── 生效 / 施行（標題或內文中明講者）──
    eff = re.search(r"(自[^，。；、\s「」]{1,14}?(?:起)?(?:施行|生效|實施|適用))",
                    title + " " + (body or ""))

    # ── 狀態 ──
    if is_draft:
        bullets.append("狀態：草案、公開徵詢意見中，尚未正式施行")
    elif eff:
        bullets.append("生效：" + eff.group(1)[:30])
    elif doc_type and doc_type.startswith("公告"):
        bullets.append("狀態：已正式公告")

    # 去重 + 上限
    out: list[str] = []
    for b in bullets:
        b = b.strip()
        if b and b not in out:
            out.append(b)
    return out[:4] or [title[:80]]


def is_placeholder(bullets) -> bool:
    """判斷某筆 ai_summary 是否為『舊占位格式』（可被升級）"""
    if not isinstance(bullets, list) or not bullets:
        return False
    joined = " ".join(str(b) for b in bullets)
    if "完整內容請看原文" in joined or "詳情請點" in joined:
        return True
    return any(str(b).startswith(OLD_MARKERS) for b in bullets)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    n_new = n_upgraded = 0
    for item in d["items"]:
        existing = item.get("ai_summary")
        if existing and not is_placeholder(existing):
            continue  # 人工/AI 摘要：保留不動
        title = item.get("title", "")
        if not title:
            continue
        bullets = generate_bullets(title, item.get("summary", ""))
        if not bullets:
            continue
        if existing:
            n_upgraded += 1
        else:
            n_new += 1
        item["ai_summary"] = bullets
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"auto_summary：新增 {n_new} 筆、升級舊占位 {n_upgraded} 筆 / 全部 {len(d['items'])} 筆")


if __name__ == "__main__":
    main()
