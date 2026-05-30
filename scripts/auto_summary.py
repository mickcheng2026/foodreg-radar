"""對沒有 AI 摘要的 item，從標題自動產生結構化重點

僅用模式比對，不呼叫 AI；產出的 ai_summary 形如：
  [類型：預告修正 / 公告 / 新聞]
  [主題：xxx]
  [完整內容請看原文]
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"

# 類型關鍵字偵測
TYPE_PATTERNS = [
    (r"第[一二三四五六七八九十百\d]+次預告", "二次以上預告"),
    (r"預告\s*修正", "預告修正"),
    (r"預告\s*訂定", "預告訂定"),
    (r"預告\s*廢止", "預告廢止"),
    (r"預告", "預告"),
    (r"公告\s*修正", "公告修正"),
    (r"公告\s*訂定", "公告訂定"),
    (r"公告\s*廢止", "公告廢止"),
    (r"公告", "公告"),
    (r"修正", "修正"),
    (r"廢止", "廢止"),
    (r"訂定", "訂定"),
    (r"新增", "新增"),
    (r"延長", "延長"),
    (r"駁斥", "闢謠"),
    (r"說明", "說明稿"),
    (r"提醒|注意|籲", "提醒"),
    (r"通報|警訊", "警訊"),
    (r"懶人包", "懶人包"),
]

# 主題關鍵字
TOPIC_PATTERNS = [
    (r"食品[中之]?動物用藥|動物用藥", "動物用藥"),
    (r"農藥殘留|農藥", "農藥"),
    (r"食品添加物|添加物", "食品添加物"),
    (r"食品衛生|衛生", "食品衛生"),
    (r"食品(?:廣告|標示|標籤)|廣告|標示", "食品標示/廣告"),
    (r"檢驗方法", "檢驗方法"),
    (r"輸入|輸出|進口|出口|邊境", "進出口"),
    (r"HACCP|食品安全管制系統", "HACCP"),
    (r"GMP|優良製造", "GMP"),
    (r"化粧品|化妝品", "化粧品"),
    (r"醫療器材", "醫療器材"),
    (r"藥品|西藥|管制藥", "藥品"),
    (r"健康食品", "健康食品"),
    (r"中藥", "中藥"),
    (r"營養標示|紅黃綠", "營養標示"),
    (r"塑化劑|重金屬|鎘|鉛|砷", "污染物"),
    (r"沙門|李斯特|大腸桿菌|微生物", "微生物"),
    (r"食中毒|食品中毒", "食物中毒"),
    (r"召回|回收|下架", "召回/下架"),
    (r"輻射|核輻射", "輻射"),
]


def generate_bullets(title: str, body: str = "") -> list[str]:
    """從標題與短內文自動生成 3-4 條摘要"""
    bullets = []
    title = title.strip()

    # 1. 類型
    doc_type = None
    for pat, label in TYPE_PATTERNS:
        if re.search(pat, title):
            doc_type = label
            break
    if doc_type:
        bullets.append(f"類型：{doc_type}")

    # 2. 主題
    topics = []
    for pat, topic in TOPIC_PATTERNS:
        if re.search(pat, title) and topic not in topics:
            topics.append(topic)
    if topics:
        bullets.append(f"主題：{', '.join(topics[:3])}")

    # 3. 主要對象（從標題中取「」內的內容）
    quoted = re.findall(r"「([^」]+)」", title)
    if quoted:
        main_obj = quoted[0][:60]
        bullets.append(f"標的法規：{main_obj}")

    # 4. 草案/正式
    if "草案" in title:
        bullets.append("狀態：草案階段（公開徵詢中）")
    elif "已" in title or "正式" in title:
        bullets.append("狀態：正式發布")

    # 5. body 截短
    if body and len(body) > 30:
        snippet = re.sub(r"\s+", " ", body[:200]).strip()
        bullets.append(f"原文節錄：{snippet}...")

    if not bullets:
        # 至少有一個
        bullets.append(f"原文標題：{title[:80]}")
        bullets.append("詳情請點「查看原文」")

    return bullets


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    n_added = 0
    for item in d["items"]:
        if item.get("ai_summary"):
            continue
        title = item.get("title", "")
        body = item.get("summary", "")
        if not title:
            continue
        bullets = generate_bullets(title, body)
        if bullets:
            item["ai_summary"] = bullets
            n_added += 1
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"自動產生 ai_summary：{n_added} 筆 / 全部 {len(d['items'])} 筆")


if __name__ == "__main__":
    main()
