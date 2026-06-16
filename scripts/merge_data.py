"""合併兩份資料檔（本機 vs 線上），供 推送.sh 在 rebase 衝突時自動解決用。

用法：python3 merge_data.py <本機.json> <線上.json> <輸出.json>

- 若檔案是 items 包裝（含 "items" 陣列，例如 data/items.json）→ 依 url 聯集合併：
  兩邊的項目都保留（不會掉線上機器人新增、也不會掉本機新抓的），
  重疊的 url 以「本機」內容為主，但保留較早的 first_seen，
  並互補缺漏的 ai_summary / title_zh，最後依日期重新排序並重算統計。
- 若是扁平 dict（例如 data/incident_titles.json）→ 鍵聯集，本機優先。

這樣即使線上有 CI 機器人的每日自動更新、本機也剛跑過爬蟲，
兩邊都不會遺失資料。
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone, timedelta

TPE = timezone(timedelta(hours=8))


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merge_items(local: dict, remote: dict) -> dict:
    def index(d):
        return {it["url"]: it for it in d.get("items", []) if it.get("url")}

    li, ri = index(local), index(remote)
    out: dict[str, dict] = {}

    # 先放線上版（保留線上機器人新增、本機沒有的項目）
    for url, it in ri.items():
        out[url] = it
    # 再用本機版覆蓋（本機內容較新），但互補欄位
    for url, it in li.items():
        old = out.get(url)
        if old:
            # 保留較早的 first_seen
            of, nf = old.get("first_seen"), it.get("first_seen")
            if of and (not nf or of < nf):
                it["first_seen"] = of
            # 互補摘要與中文標題（哪邊有就留）
            if not it.get("ai_summary") and old.get("ai_summary"):
                it["ai_summary"] = old["ai_summary"]
            if not it.get("title_zh") and old.get("title_zh"):
                it["title_zh"] = old["title_zh"]
        out[url] = it

    items = list(out.values())
    items.sort(key=lambda it: (it.get("date") or "", it.get("first_seen") or ""),
               reverse=True)

    by_source: dict[str, int] = {}
    for it in items:
        s = it.get("source_label", "?")
        by_source[s] = by_source.get(s, 0) + 1

    return {
        "updated_at": datetime.now(TPE).isoformat(timespec="seconds"),
        "stats": {"total": len(items), "by_source": by_source},
        "items": items,
    }


def merge_dict(local: dict, remote: dict) -> dict:
    out = dict(remote)
    out.update(local)  # 本機優先
    return out


def main():
    if len(sys.argv) != 4:
        print("用法：python3 merge_data.py <本機.json> <線上.json> <輸出.json>")
        sys.exit(1)
    local_p, remote_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    local, remote = load(local_p), load(remote_p)

    if isinstance(local, dict) and "items" in local:
        merged = merge_items(local, remote)
        n_local = len(local.get("items", []))
        n_remote = len(remote.get("items", [])) if isinstance(remote, dict) else 0
        n_out = len(merged["items"])
    else:
        merged = merge_dict(
            local if isinstance(local, dict) else {},
            remote if isinstance(remote, dict) else {},
        )
        n_local = len(local) if isinstance(local, dict) else 0
        n_remote = len(remote) if isinstance(remote, dict) else 0
        n_out = len(merged)

    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"  [合併] {out_p}：本機 {n_local} + 線上 {n_remote} → 聯集 {n_out} 筆")


if __name__ == "__main__":
    main()
