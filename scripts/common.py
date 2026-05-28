"""共用工具：HTTP 請求、HTML 解析、去除標籤、日期正規化等"""
from __future__ import annotations
import urllib.request
import urllib.error
import ssl
import re
import html as html_module
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

TPE = timezone(timedelta(hours=8))

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def fetch(url: str, timeout: int = 25) -> str:
    """抓取網頁 HTML / XML 內容"""
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx) as r:
        raw = r.read()
        # 嘗試多種編碼
        for enc in ("utf-8", "big5", "cp950"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="ignore")


class _StripTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
    def handle_data(self, data):
        self.parts.append(data)


def strip_tags(text: str) -> str:
    p = _StripTags()
    p.feed(text or "")
    return html_module.unescape("".join(p.parts)).strip()


def clean_text(text: str) -> str:
    """去除多餘空白、HTML 實體"""
    if not text:
        return ""
    text = html_module.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_date(s: str) -> str | None:
    """把各種日期字串轉成 ISO 8601 (YYYY-MM-DD)"""
    if not s:
        return None
    s = s.strip()

    # 先試西元年（4 位數）：2026-05-27 / 2026/05/27
    m = re.search(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date().isoformat()
        except ValueError:
            pass

    # 民國年（含「年」「月」「日」字樣）
    m = re.search(r"(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 1911:
            y += 1911
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            pass

    # 民國年：114-05-27（保守：年份小於 200 才當民國，避免吃到西元）
    m = re.search(r"\b(\d{2,3})[-/](\d{1,2})[-/](\d{1,2})\b", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 200:
            y += 1911
        try:
            return datetime(y, mo, d).date().isoformat()
        except ValueError:
            pass

    # 英文格式：21 May 2026 / May 21, 2026
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10,
        "november": 11, "december": 12,
    }
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
    if m:
        mo = months.get(m.group(2).lower())
        if mo:
            try:
                return datetime(int(m.group(3)), mo, int(m.group(1))).date().isoformat()
            except ValueError:
                pass
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        mo = months.get(m.group(1).lower())
        if mo:
            try:
                return datetime(int(m.group(3)), mo, int(m.group(2))).date().isoformat()
            except ValueError:
                pass

    return None


def make_item(source: str, source_label: str, title: str, url: str,
              date: str | None, summary: str = "", tags: list[str] | None = None,
              source_color: str = "slate") -> dict:
    """產出統一格式的 item"""
    return {
        "source": source,                  # 內部代號 ex: "tfda"
        "source_label": source_label,      # 顯示名稱 ex: "食藥署"
        "source_color": source_color,      # tailwind 配色 key
        "title": clean_text(title)[:300],
        "url": url,
        "date": date,
        "summary": clean_text(summary)[:500],
        "tags": tags or [],
        "fetched_at": datetime.now(TPE).isoformat(timespec="seconds"),
    }
