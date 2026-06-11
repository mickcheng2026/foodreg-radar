"""把所有外文（非中文）標題自動翻成繁體中文，寫入 item['title_zh']。

- 使用 Google 翻譯免費端點（translate.googleapis.com/translate_a/single），純 stdlib、免金鑰
- 多筆合併成一次請求（以換行分隔）以降低請求數；行數不符時退回逐筆翻譯
- 已有 title_zh 者略過；中文標題略過（中文字比例 >= 0.2）
- build_data 合併時會保留 title_zh，故只有新進外文項目需要翻譯 → 每日成本/請求極少
- 翻譯品質為機器翻譯（夠看懂內容即可）；人工精選標題（incident_titles.json 等）仍優先保留
"""
from __future__ import annotations
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from common import fetch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"

ENDPOINT = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=zh-TW&dt=t&q="
BATCH = 16              # 每次請求最多幾筆
MAX_CHARS = 1600        # 每次請求合併文字長度上限
DELAY = 0.4            # 每次請求間隔（秒），客氣一點避免被擋


def _is_chinese(text: str, ratio: float = 0.2) -> bool:
    if not text:
        return True
    cj = sum(1 for c in text if "一" <= c <= "鿿")
    return cj / max(len(text), 1) >= ratio


def _translate_join(texts: list[str]) -> list[str] | None:
    """一次翻譯多行；回傳對應的中文行，數量不符則回 None"""
    joined = "\n".join(texts)
    try:
        raw = fetch(ENDPOINT + urllib.parse.quote(joined), timeout=20)
        d = json.loads(raw)
    except Exception as e:
        print(f"    翻譯請求失敗: {str(e)[:60]}", file=sys.stderr)
        return None
    out = "".join(seg[0] for seg in d[0] if seg and seg[0])
    lines = out.split("\n")
    return lines if len(lines) == len(texts) else None


def _translate_one(text: str) -> str | None:
    try:
        raw = fetch(ENDPOINT + urllib.parse.quote(text), timeout=15)
        d = json.loads(raw)
        return "".join(seg[0] for seg in d[0] if seg and seg[0]).strip() or None
    except Exception:
        return None


def enrich(items: list[dict], max_new: int | None = None) -> int:
    todo = [it for it in items
            if it.get("title") and not it.get("title_zh") and not _is_chinese(it["title"])]
    if max_new is not None:
        todo = todo[:max_new]
    if not todo:
        print("  [翻譯] 無待翻譯外文標題")
        return 0

    print(f"  [翻譯] 待翻譯外文標題 {len(todo)} 筆")
    done = 0
    i = 0
    while i < len(todo):
        batch, chars = [], 0
        while i < len(todo) and len(batch) < BATCH and chars < MAX_CHARS:
            batch.append(todo[i])
            chars += len(todo[i]["title"]) + 1
            i += 1
        texts = [it["title"] for it in batch]
        zh = _translate_join(texts) or [_translate_one(t) for t in texts]
        for item, z in zip(batch, zh):
            if z and z.strip() and z.strip() != item["title"]:
                item["title_zh"] = z.strip()
                done += 1
        if done and done % 160 < BATCH:
            print(f"    已翻譯約 {done} 筆…")
        time.sleep(DELAY)
    print(f"  [翻譯] 完成，新增中文標題 {done} 筆")
    return done


def main():
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else None
    n = enrich(doc["items"], max_new=cap)
    if n:
        DATA.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  寫入 {DATA}")


if __name__ == "__main__":
    main()
