"""AI 摘要：用 Claude Haiku 把官方公告的長文濃縮為 3-5 條繁中重點

- 完全使用 stdlib (urllib)，不需 pip install
- 沒設定 ANTHROPIC_API_KEY 時自動跳過 (return None)，整個流程不會中斷
- 每筆 item 只摘要一次，已摘要過的 (有 ai_summary 欄位) 直接略過
- 使用最便宜的 Haiku 4.5 模型；估算每筆約 NT$0.06，30 筆/天 ≈ NT$54/月
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error
import ssl

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"

_ctx = ssl.create_default_context()

PROMPT_TEMPLATE = """你是食品法規專員，請把以下公告濃縮成 3-5 條繁體中文重點，給衛生管理員快速掌握。

要求：
1. 每條一行，開頭不加數字或符號（前端會自動加項目符號）
2. 突出「修改了什麼 / 限值多少 / 何時生效 / 影響誰」
3. 不要重複標題的字
4. 純文字，不要 markdown、不要連結
5. 如果是國際公告（英文），翻譯成中文重點

標題：{title}

原文：
{body}

只輸出重點，每條一行，不要有任何前後綴或說明。"""


def summarize(title: str, body: str, api_key: str | None = None) -> list[str] | None:
    """產生 AI 重點清單 (list of strings)；失敗或沒 key 時回傳 None"""
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    title = (title or "").strip()
    body = (body or "").strip()
    if not body or len(body) < 30:
        return None

    prompt = PROMPT_TEMPLATE.format(title=title, body=body[:3000])

    payload = {
        "model": MODEL,
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}],
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=_ctx) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"    AI 摘要 HTTP {e.code}: {err_body[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    AI 摘要錯誤: {e}", file=sys.stderr)
        return None

    text = ""
    for block in resp.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    bullets = [
        line.strip().lstrip("·•-*0123456789. 、").strip()
        for line in text.splitlines()
        if line.strip()
    ]
    bullets = [b for b in bullets if len(b) >= 5][:6]
    return bullets or None


def enrich_items(items: list[dict], skip_existing: bool = True, max_new: int | None = None) -> int:
    """對 items 清單中尚未有 ai_summary 的項目逐一產生摘要；回傳實際呼叫次數"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  [AI] 未設定 ANTHROPIC_API_KEY，跳過 AI 摘要")
        return 0

    called = 0
    for item in items:
        if max_new is not None and called >= max_new:
            break
        if skip_existing and item.get("ai_summary"):
            continue
        title = item.get("title", "")
        body = item.get("summary", "")
        if not body:
            continue
        bullets = summarize(title, body, api_key)
        if bullets:
            item["ai_summary"] = bullets
            called += 1
            print(f"    AI [{called}] {title[:40]}... ({len(bullets)} 點)")
    return called


if __name__ == "__main__":
    # 測試模式：把 items.json 重新跑一次 AI 摘要
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    f = ROOT / "data" / "items.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    n = enrich_items(d["items"], skip_existing=True)
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成，新增 {n} 筆 AI 摘要")
