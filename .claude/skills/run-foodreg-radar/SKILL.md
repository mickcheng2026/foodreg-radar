---
name: run-foodreg-radar
description: Run, smoke-test, screenshot, or update data for the 食規雷達 (FoodReg Radar) static site. Use when asked to run/start/serve/preview/screenshot the site, refresh/rebuild/update the JSON data, or verify the scrapers (food regulatory site for 食藥署 / EFSA / ISO / Codex / US FDA announcements).
---

# 食規雷達 (FoodReg Radar) — Run skill

Static HTML site (`index.html`) that fetches `data/items.json` and renders cards. Five Python scrapers in `scripts/` produce that JSON. No Node, no build step — just `python3`. Verified on macOS with system Python 3.9.

All paths in this doc are relative to `<unit>/` = the project root (`條文自動更新 網站/`). The driver is at `.claude/skills/run-foodreg-radar/smoke.sh`.

## Prerequisites

Already on the host — no install needed:
- `python3` (3.9+) — system Python is fine, no venv
- `curl`
- macOS host. On Linux the scrapers still work; only the screenshot path differs.

The scrapers use **only stdlib** (`urllib`, `re`, `html.parser`). Nothing to `pip install`.

For the optional headless screenshot path you need Google Chrome installed at `/Applications/Google Chrome.app/` (default macOS install).

## Run (agent path) — primary

One command verifies the whole app end-to-end (data + server + HTML structure):

```bash
.claude/skills/run-foodreg-radar/smoke.sh
```

What it does, in order:

1. Validates `data/items.json` is parseable JSON with non-empty `items[]` and required fields (`title`, `url`, `source_label`)
2. Starts `python3 -m http.server 8765 --bind 127.0.0.1` in the background
3. `curl`s `/index.html` and `/data/items.json` — both must return 200
4. Re-parses the JSON served through HTTP
5. Greps `index.html` for the structural anchors (`<title>食規雷達`, `id="search-input"`, `id="source-chips"`, `id="feed"`, `id="stats-grid"`, the `fetch("data/items.json"` call)
6. Kills the server in the `trap EXIT`

Exits 0 = OK. Exits 1 with a `FAIL:` line on any failure. Runs in ~3 seconds.

**To refresh the data first** (hits TFDA + EFSA over the network; takes 60-90 s):

```bash
.claude/skills/run-foodreg-radar/smoke.sh --fetch
```

**To serve continuously for human / browser preview** (the smoke driver tears down the server after checks — for visual review do this instead):

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"   # or cd to the project root manually
python3 -m http.server 8765 --bind 127.0.0.1
# then in another shell:
open http://127.0.0.1:8765/
```

## Run individual scrapers

Each `source_*.py` is independently runnable for debugging:

```bash
cd scripts
python3 source_tfda.py    # 食藥署 — high quality, ~30 items
python3 source_efsa.py    # EFSA — ~14 items
python3 source_usfda.py   # noisy, FDA changed URLs
python3 source_iso.py     # ~2 items (food-filtered)
python3 source_codex.py   # currently 0 — selector needs work
```

Orchestrator:

```bash
cd scripts && python3 build_data.py
```

Writes `data/items.json` with merged items, deduped by URL, sorted by date desc.

## Screenshot (optional, macOS)

The smoke driver does **not** screenshot — text checks cover server health and HTML structure. To grab a PNG of the rendered site (e.g. to attach to a PR), use Chrome headless:

```bash
pkill -f "http.server 8765" 2>/dev/null; sleep 0.3
python3 -m http.server 8765 --bind 127.0.0.1 >/tmp/foodreg.log 2>&1 &
SERVER=$!
sleep 1

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --window-size=1400,2000 --virtual-time-budget=4000 \
  --screenshot=".claude/skills/run-foodreg-radar/screenshots/site.png" \
  "http://127.0.0.1:8765/index.html"

kill $SERVER 2>/dev/null
```

The reference screenshot at `screenshots/site-loaded.png` was captured this way.

`screencapture -x` from CLI **does not work** without "Screen Recording" entitlement granted to the parent terminal — use Chrome's `--screenshot` flag instead.

## Run (human path)

```bash
python3 -m http.server 8765 --bind 127.0.0.1
open http://127.0.0.1:8765/
# Ctrl-C to stop
```

Open `prototype.html` directly with `open prototype.html` works because it has no `fetch()` — but `index.html` opened via `file://` will fail to load `data/items.json` (browser blocks `file://` → `file://` fetch in most setups). Always go through the server.

## Test (none)

No test suite. The smoke driver is the test.

## Gotchas

- **`prototype.html` is throwaway** — it's the hardcoded-data mockup shown before sign-off. `.gitignore` excludes it from upload. The live page is `index.html`.
- **Encoding subtleties in TFDA HTML**: the 食藥署 page double-encodes attribute quotes as `&#39;`. The scraper's regex matches plain `<tr>` (no class match) — don't "fix" the regex to be stricter against `class=...` or it will break (see `scripts/source_tfda.py:parse_list_page`).
- **TFDA date column is at the END of the `<tr>`, not the start**. Date regex must search the chunk *after* the `<a>`, not before — getting this wrong silently maps every item to 1937-MM-DD (民國 26 + 1911).
- **Year disambiguation**: `normalize_date()` tries 4-digit year *first*, then民國 (`<200`). Swap that order and `2026-05-27` becomes民國 2026 → 3937. (See `scripts/common.py:normalize_date`.)
- **US FDA scraper is noisy** — FDA changed several listing URLs (`/news-events/press-announcements` returns 404 from Python's `urllib`, works in WebFetch which follows redirects). It collects ~8 mostly-irrelevant entries; the orchestrator filters but expect noise. Don't trust US FDA counts.
- **Codex scraper currently returns 0** — the `news-details` selector misses the new FAO layout. Stub still committed so the orchestrator's source list stays intact.
- **GitHub Actions cron is UTC**, set to `0 1 * * *` = 09:00 台灣時間. Change in `.github/workflows/update-data.yml` if you want a different time.
- **Items dedup by URL** — re-runs don't grow the file forever, but they *do* update `fetched_at` on each item. `first_seen` is preserved from the earliest crawl. Sort key is `date` desc, then `first_seen` desc.

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `smoke.sh` says `data/items.json 不存在` | First run — use `smoke.sh --fetch` once to populate, then plain `smoke.sh` is fine. |
| `smoke.sh` says `Address already in use` then `伺服器未就緒` | Old `http.server` still running. Driver tries `pkill -f "http.server $PORT"`; if that misses, `lsof -ti :8765 \| xargs kill`. |
| Scraper TFDA prints `找到 0 筆` | `news.aspx` returned the error page (typically when CDN blocks the User-Agent). Re-run after a few seconds; the scraper sends a desktop Chrome UA in `common.DEFAULT_HEADERS`. |
| Screenshot PNG is 0 bytes or all white | Chrome's `--virtual-time-budget` too short — bump from 4000 to 8000. The page does its `fetch()` then renders cards; needs ~2 s of "virtual time" minimum. |
| `open index.html` shows the loading spinner forever | You opened it via `file://`. The JS does `fetch("data/items.json")` which the browser blocks. Use the server. |
| `screencapture -x` fails with `could not create image from display` | Terminal lacks Screen Recording permission. Use the Chrome headless flow instead — it doesn't need any system permission. |
