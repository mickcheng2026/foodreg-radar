"""從 data/items.json 產生 data/items-recent.json（首屏快速載入用）。

為什麼要這個檔？
  items.json 有 5000+ 筆、壓縮後約 900 KB，網路較慢時使用者要等 3-4 秒
  才看得到第一則公告。items-recent.json 只放最近 90 天（約 1400 筆、
  壓縮後約 330 KB），網頁先載它立刻顯示，再於背景把完整資料載回來。

重要：這是「衍生檔」，內容完全由 items.json 決定。
  任何會改動 items.json 的流程（爬蟲、AI 摘要、合併衝突）跑完後，
  重跑本腳本即可，不需要也不應該手動編輯 items-recent.json。

用法：python3 scripts/make_recent.py [items.json 路徑] [輸出路徑]
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

RECENT_DAYS = 90

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "data" / "items.json"
DEFAULT_OUT = ROOT / "data" / "items-recent.json"


def item_date(item: dict) -> str:
    """取用來判斷新舊的日期：優先發布日，沒有就用收錄日。"""
    d = item.get("date")
    if d:
        return d[:10]
    fs = item.get("first_seen") or item.get("fetched_at") or ""
    return fs[:10]


def build_recent(data: dict, recent_days: int = RECENT_DAYS) -> dict:
    items = data.get("items", [])

    # 用「資料裡最新的日期」當基準，而不是今天。
    # 這樣同一份 items.json 永遠產生同一份輸出（不會因為隔天再跑就產生差異，
    # 免得每天冒出內容相同卻一直變動的 commit）。
    dates = [d for d in (item_date(i) for i in items) if d]
    if not dates:
        recent = items
        cutoff = ""
    else:
        newest = max(dates)
        try:
            y, m, d = (int(x) for x in newest.split("-")[:3])
            cutoff = (date(y, m, d) - timedelta(days=recent_days)).isoformat()
        except (ValueError, TypeError):
            cutoff = ""
        recent = [i for i in items if item_date(i) >= cutoff] if cutoff else items

    return {
        "updated_at": data.get("updated_at", ""),
        # stats 沿用完整資料的統計，讓首屏的「總收錄」等數字一開始就是對的
        "stats": data.get("stats", {}),
        "partial": True,          # 給前端判斷：這是節選，要再去載完整版
        "recent_days": recent_days,
        "cutoff": cutoff,
        "items": recent,
    }


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT

    if not src.exists():
        print(f"! 找不到 {src}，略過產生 items-recent.json")
        return 0

    data = json.loads(src.read_text(encoding="utf-8"))
    recent = build_recent(data)

    out.write_text(
        json.dumps(recent, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    total = len(data.get("items", []))
    kept = len(recent["items"])
    print(f"  items-recent.json：{kept} / {total} 筆"
          f"（{recent['cutoff']} 之後）→ {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
