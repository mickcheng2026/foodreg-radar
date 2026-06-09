"""一次性 AI 摘要回填工具（由 Claude 在對話中手寫摘要，零 API 費用）。

流程：
  1. dump  START COUNT  → 印出待處理項目的 url/title/source/body（給 Claude 讀）
  2. Claude 把摘要寫進 data/ai_backfill.json（url -> [bullets]）
  3. merge → 把 ai_backfill.json 套回 items.json

待處理 = 有內文(>=30字) 且 url 不在「精選摘要(apply_ai_summaries.SUMMARIES)」
        且 url 還沒在 ai_backfill.json 裡。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"
BACKFILL = ROOT / "data" / "ai_backfill.json"

sys.path.insert(0, str(ROOT / "scripts"))
from apply_ai_summaries import SUMMARIES as CURATED  # noqa: E402


def _load_backfill() -> dict:
    if BACKFILL.exists():
        return json.loads(BACKFILL.read_text(encoding="utf-8"))
    return {}


def _todo_items(items: list[dict]) -> list[dict]:
    done = set(_load_backfill().keys())
    out = []
    for it in items:
        url = it.get("url")
        body = (it.get("summary") or "").strip()
        if not url or len(body) < 30:
            continue
        if url in CURATED or url in done:
            continue
        out.append(it)
    return out


def cmd_status():
    items = json.loads(DATA.read_text(encoding="utf-8"))["items"]
    todo = _todo_items(items)
    done = _load_backfill()
    print(f"已回填: {len(done)} 筆")
    print(f"待回填: {len(todo)} 筆")
    from collections import Counter
    c = Counter(it.get("source_label", "?") for it in todo)
    for k, v in c.most_common():
        print(f"  {k}: {v}")


def cmd_dump(start: int, count: int):
    items = json.loads(DATA.read_text(encoding="utf-8"))["items"]
    todo = _todo_items(items)
    chunk = todo[start:start + count]
    out = [
        {
            "url": it["url"],
            "source": it.get("source_label", ""),
            "title": it.get("title", ""),
            "body": (it.get("summary") or "").strip()[:500],
        }
        for it in chunk
    ]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n# 本批 {len(out)} 筆（全待回填 {len(todo)} 筆，本批為 {start}~{start+len(out)}）",
          file=sys.stderr)


def cmd_merge():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    bf = _load_backfill()
    n = 0
    for it in d["items"]:
        url = it.get("url")
        if url in bf and bf[url]:
            it["ai_summary"] = bf[url]
            n += 1
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已套用 {n} 筆 AI 回填摘要 / 全部 {len(d['items'])} 筆")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        cmd_status()
    elif cmd == "dump":
        cmd_dump(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "merge":
        cmd_merge()
    else:
        print("用法: ai_backfill.py [status | dump START COUNT | merge]")
