"""日本 食品安全委員会 (FSC) 公開意見徵詢爬蟲

來源：https://www.fsc.go.jp/iken-bosyu/index.html
- パブリックコメント募集 = 公開徵詢意見（食品安全相關法規預告）
- 等同台灣食藥署的預告法規階段
- 內容主要是農藥、添加物、化合物的食品健康影響評估
"""
from __future__ import annotations
import re
import html as html_module
from common import fetch, clean_text, strip_tags, make_item
from datetime import datetime

BASE = "https://www.fsc.go.jp"
LIST_URL = f"{BASE}/iken-bosyu/index.html"


# 日文→中文簡易對應，協助標題翻譯
JP_TRANSLATE = [
    ("食品健康影響評価", "食品健康影響評估"),
    ("意見・情報の募集", "公開徵詢意見"),
    ("について", ""),
    ("に係る", "相關"),
    ("審議結果", "審議結果"),
    ("（案）", "(草案)"),
    ("除草剤", "除草劑"),
    ("殺虫剤", "殺蟲劑"),
    ("殺菌剤", "殺菌劑"),
    ("耐性", "耐性"),
    ("ダイズ", "大豆"),
    ("系統", "系統"),
    ("コメ", "稻米"),
    ("食品添加物", "食品添加物"),
    ("動物用医薬品", "動物用藥"),
    ("器具・容器包装", "器具與容器包裝"),
    ("について", ""),
]


def parse_date_jp(s: str) -> str | None:
    """日期：2026/05/27 / 令和8年5月27日"""
    s = s.strip()
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date().isoformat()
        except ValueError:
            return None
    # 令和：令和元年 = 2019
    m = re.match(r"令和(\d+)年(\d{1,2})月(\d{1,2})", s)
    if m:
        y = 2018 + int(m.group(1))
        try:
            return datetime(y, int(m.group(2)), int(m.group(3))).date().isoformat()
        except ValueError:
            return None
    return None


def translate_title_basic(jp: str) -> str:
    """簡易日譯中：用對照表做機械替換"""
    out = jp
    for jp_w, zh_w in JP_TRANSLATE:
        out = out.replace(jp_w, zh_w)
    # 去掉多餘標點
    out = re.sub(r"[\s　]+", " ", out).strip()
    return out


def crawl() -> list[dict]:
    items: list[dict] = []
    try:
        html = fetch(LIST_URL)
    except Exception as e:
        print(f"  [JP FSC] 抓取失敗: {e}")
        return items

    # 表格 row 結構：<tr>...<td>日期</td>...<td>標題與連結</td></tr>
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    for row in rows:
        # 第一個 td 是日期
        date_m = re.search(r'<td[^>]*>\s*(\d{4}/\d{1,2}/\d{1,2})', row)
        if not date_m:
            continue
        date = parse_date_jp(date_m.group(1))

        # anchor + 標題
        a_m = re.search(r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>', row, re.DOTALL)
        if not a_m:
            # 純文字標題（無連結）也接受，URL fallback 到列表頁
            text_m = re.search(r'<td[^>]*>([^<]{20,300})</td>\s*</tr>', row)
            if not text_m:
                continue
            title = clean_text(html_module.unescape(text_m.group(1)))
            url = LIST_URL
        else:
            url_part = a_m.group(1)
            if url_part.startswith("/"):
                url = BASE + url_part
            elif url_part.startswith("http"):
                url = url_part
            else:
                url = BASE + "/iken-bosyu/" + url_part.lstrip("./")
            title = clean_text(html_module.unescape(a_m.group(2)))

        if not title or len(title) < 5:
            continue

        # 中文翻譯標題
        title_zh = translate_title_basic(title)

        # 標籤
        tags = ["公開徵詢", "食品健康影響評估"]
        if "除草" in title or "農薬" in title or "農藥" in title:
            tags.append("農藥殘留")
        if "添加物" in title:
            tags.append("食品添加物")
        if "動物用" in title or "用医薬品" in title:
            tags.append("動物用藥")
        if "ダイズ" in title or "大豆" in title:
            tags.append("基改作物")
        if "耐性" in title and ("ダイズ" in title or "系統" in title):
            tags.append("基因改造")

        ai_summary = [
            f"日本食品安全委員會公開徵詢意見",
            f"事項：{title_zh}",
        ]
        if date:
            ai_summary.append(f"公告日期：{date}")
        ai_summary.append("等同食藥署的「預告法規」階段 — 開放意見徵詢")
        ai_summary.append("來源：日本食品安全委員會 (FSC)")

        item = make_item(
            source="jp_fsc",
            source_label="日本 FSC",
            source_color="rose",
            title=title,
            url=url,
            date=date,
            summary=title,
            tags=tags,
        )
        item["title_zh"] = title_zh
        item["ai_summary"] = ai_summary
        items.append(item)

    print(f"  [JP FSC] 日本食品安全公開徵詢 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    print(json.dumps(crawl()[:3], ensure_ascii=False, indent=2))
