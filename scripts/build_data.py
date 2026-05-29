"""主排程：依序執行所有來源爬蟲，整合進 data/items.json

執行：python3 build_data.py
"""
from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import source_tfda
import source_efsa
import source_iso
import source_usfda
import source_codex

TPE = timezone(timedelta(hours=8))

# 路徑：data/items.json 在專案根目錄下
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "items.json"


def main():
    DATA_DIR.mkdir(exist_ok=True)

    print(f"=== 食規雷達 資料更新 開始 {datetime.now(TPE).isoformat(timespec='seconds')} ===\n")

    all_items: list[dict] = []

    sources = [
        ("食藥署 TFDA", source_tfda.crawl),
        ("EFSA", source_efsa.crawl),
        ("US FDA", source_usfda.crawl),
        ("ISO", source_iso.crawl),
        ("Codex", source_codex.crawl),
    ]

    for name, fn in sources:
        print(f"\n--- 抓取 {name} ---")
        try:
            items = fn()
            all_items.extend(items)
        except Exception as e:
            print(f"  ! {name} 整個失敗，跳過：{e}")

    # 載入既有資料（若存在），合併、去重（依 url），保留歷史
    existing: list[dict] = []
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8")).get("items", [])
        except Exception as e:
            print(f"  ! 既有資料載入失敗（重新建立）：{e}")

    # 用 url 為主鍵合併（新資料優先）
    merged: dict[str, dict] = {}
    for item in existing:
        if item.get("url"):
            merged[item["url"]] = item
    for item in all_items:
        if item.get("url"):
            # 新版本：更新 fetched_at 與內容；保留 first_seen 與 ai_summary
            old = merged.get(item["url"])
            if old:
                if old.get("first_seen"):
                    item["first_seen"] = old["first_seen"]
                if old.get("ai_summary"):
                    item["ai_summary"] = old["ai_summary"]
            if not item.get("first_seen"):
                item["first_seen"] = datetime.now(TPE).isoformat(timespec="seconds")
            merged[item["url"]] = item

    # 排序：有日期者依日期新→舊；無日期者照 first_seen
    def sort_key(item: dict):
        d = item.get("date") or ""
        return (d, item.get("first_seen", ""))

    sorted_items = sorted(merged.values(), key=sort_key, reverse=True)

    # 統計
    by_source: dict[str, int] = {}
    for it in sorted_items:
        by_source[it["source_label"]] = by_source.get(it["source_label"], 0) + 1

    output = {
        "updated_at": datetime.now(TPE).isoformat(timespec="seconds"),
        "stats": {
            "total": len(sorted_items),
            "by_source": by_source,
        },
        "items": sorted_items,
    }

    DATA_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== 完成 ===")
    print(f"  總筆數：{len(sorted_items)}")
    for src, cnt in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {src}: {cnt} 筆")
    print(f"  寫入：{DATA_FILE}")


if __name__ == "__main__":
    main()
