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
import source_tfda_law
import source_efsa
import source_iso
import source_usfda
import source_codex
import source_hk_cfs
import source_au_fsanz
import source_jp_fsc
import source_my_kkm
import source_import_export
import source_haccp
import source_jp_curated
import source_export_guide
import source_food_incidents

# 來源 → 國家對應（顯示於前端國家篩選器）
SOURCE_COUNTRY = {
    "tfda":          "台灣",
    "tfda_law":      "台灣",
    "usfda":         "美國",
    "efsa":          "歐盟",
    "iso":           "國際",
    "codex":         "國際",
    "hk_cfs":        "香港",
    "au_fsanz":      "澳洲",
    "jp_fsc":        "日本",
    "my_kkm":        "馬來西亞",
    # 進出口 / HACCP item 在 item 自己的 country 欄位上會自帶
}

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
        ("食藥署 食品類法規", source_tfda_law.crawl),
        ("EFSA", source_efsa.crawl),
        ("US FDA", source_usfda.crawl),
        ("ISO", source_iso.crawl),
        ("Codex", source_codex.crawl),
        ("香港 CFS", source_hk_cfs.crawl),
        ("澳洲 FSANZ", source_au_fsanz.crawl),
        ("日本 FSC", source_jp_fsc.crawl),
        ("馬來西亞 KKM", source_my_kkm.crawl),
        ("進出口規範", source_import_export.crawl),
        ("HACCP 認證", source_haccp.crawl),
        ("日本法規目錄", source_jp_curated.crawl),
        ("出口指南", source_export_guide.crawl),
        ("食安事件", source_food_incidents.crawl),
    ]
    # --clean-only：不抓網路，只對既有資料重跑下方的清理／歸併（改了清理規則時用）
    if "--clean-only" in sys.argv:
        sources = []

    for name, fn in sources:
        print(f"\n--- 抓取 {name} ---")
        try:
            items = fn()
            # 自動標記國家
            for it in items:
                src_code = it.get("source", "")
                if src_code in SOURCE_COUNTRY:
                    it["country"] = SOURCE_COUNTRY[src_code]
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
                if old.get("title_zh") and not item.get("title_zh"):
                    item["title_zh"] = old["title_zh"]
            if not item.get("first_seen"):
                item["first_seen"] = datetime.now(TPE).isoformat(timespec="seconds")
            merged[item["url"]] = item

    # 食安事件清理（自癒，含既有資料）：
    #  1) 濾掉意見專欄／解釋文／調查報告／政策修法等「非具體事件」雜訊，
    #     以及同一場疫情的「人數又增加」後續追蹤（一個事件只留一則）
    #  2) 依正規化標題去重 — Google News 同一則新聞每天會給不同網址，
    #     只靠 URL 去重會讓同標題累積成多筆，這裡保留 first_seen 最早的一筆
    #  3) 剝掉標題尾端的導讀子句／新聞分類標籤（「: What to Know」「| 生活」）——
    #     既讓標題乾淨，也讓同一事件的不同版本標題對得起來
    #  4) 濾掉看不出是具體事件的產業新聞（舊版 Food Safety News 全收留下的）
    #  5) 標籤重算成只有中文危害分類（拿掉媒體名、公司名、英文重複分類）
    #  6) 同一事件的多則報導標上同一個 event_id，前端摺成一張卡（不刪任何報導）
    try:
        from source_food_incidents import (
            is_noise as _inc_is_noise,
            is_count_update as _inc_is_count,
            is_incident as _inc_is_incident,
            incident_tags as _inc_tags,
            assign_events as _inc_assign_events,
            country_from_title as _inc_country,
            _norm_title as _inc_norm,
            _same_event as _inc_same,
            strip_tail as _inc_strip,
        )
        removed_noise = 0
        removed_offtopic = 0
        removed_dup = 0
        trimmed = 0
        recountried = 0

        inc_urls = [u for u, it in merged.items() if it.get("source") == "food_incidents"]

        # (1) 雜訊 + (4) 非事件 + (3) 標題剝尾 + (5) 標籤
        for url in inc_urls:
            it = merged[url]
            title = it.get("title", "")
            if _inc_is_noise(title) or _inc_is_count(title):
                del merged[url]
                removed_noise += 1
                continue
            if not _inc_is_incident(title):
                del merged[url]
                removed_offtopic += 1
                continue
            clean = _inc_strip(it.get("title", ""))
            if clean and clean != it.get("title"):
                it["title"] = clean
                # 中文標題是照舊標題翻的，清掉讓 translate_titles.py 重譯
                it.pop("title_zh", None)
                trimmed += 1
            it["tags"] = _inc_tags(it["title"], it.get("summary", ""))
            # AI 重點的「病原／危害」那行跟著標籤走（舊資料是用舊危害清單產生的）
            hz = it["tags"][1:]
            if isinstance(it.get("ai_summary"), list):
                lines = [b for b in it["ai_summary"] if not b.startswith("病原／危害：")]
                if hz:
                    lines.insert(1, "病原／危害：" + "、".join(hz[:4]))
                it["ai_summary"] = lines
            # 標題明講的國家優先（事件歸併要求同國家，國家錯了會把別國事件併進來）
            tc = _inc_country(it["title"])
            if tc and tc != it.get("country"):
                it["country"] = tc
                recountried += 1

        # (2) 依正規化標題去重：排序後相鄰比對，同一組保留 first_seen 最早的一筆
        keyed = [(_inc_norm(merged[u].get("title", "")), u)
                 for u in merged if merged[u].get("source") == "food_incidents"]
        keyed = sorted((k, u) for k, u in keyed if k)
        rep_key: str | None = None
        group: list[str] = []

        def _flush(urls: list[str]) -> int:
            if len(urls) < 2:
                return 0
            keep = min(urls, key=lambda u: merged[u].get("first_seen") or "￿")
            for u in urls:
                if u != keep:
                    del merged[u]
            return len(urls) - 1

        for key, url in keyed:
            if rep_key is not None and _inc_same(rep_key, key):
                group.append(url)
                continue
            removed_dup += _flush(group)
            rep_key, group = key, [url]
        removed_dup += _flush(group)

        # (6) 同一事件歸併（只摺疊）
        folded = _inc_assign_events(
            [it for it in merged.values() if it.get("source") == "food_incidents"])

        print(f"  [食安事件清理] 移除雜訊 {removed_noise} 筆、非事件新聞 {removed_offtopic} 筆、"
              f"重複標題 {removed_dup} 筆、標題剝尾 {trimmed} 筆、依標題更正國家 {recountried} 筆；"
              f"同一事件摺疊 {folded} 則報導")
    except Exception as e:
        print(f"  ! 食安事件清理略過：{e}")

    # 所有來源：同一張卡片的標籤不重複（例如食藥署「公告」分類 + 標題含「公告」）
    for it in merged.values():
        if it.get("tags"):
            it["tags"] = list(dict.fromkeys(it["tags"]))

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
