# 食規雷達 FoodReg Radar

> 自動匯整食藥署、HACCP、ISO、US FDA、EFSA、Codex 食品法規與安全公告的網站。

**部署上線請看 → [部署步驟.md](./部署步驟.md)**

## 專案結構

```
.
├── index.html              ← 前端網頁（純 HTML + Tailwind CDN）
├── data/items.json         ← 抓取後的資料（由爬蟲自動更新）
├── scripts/                ← Python 爬蟲程式
│   ├── common.py             共用工具
│   ├── source_tfda.py        食藥署（主要來源）
│   ├── source_efsa.py        歐洲食品安全局
│   ├── source_usfda.py       美國 FDA
│   ├── source_iso.py         ISO 國際標準組織
│   ├── source_codex.py       Codex 國際食品法典
│   └── build_data.py         主排程（整合所有來源）
├── .github/workflows/
│   └── update-data.yml     ← 每天自動執行爬蟲的設定
└── 部署步驟.md             ← 給非技術使用者的上線教學
```

## 本機測試

```bash
# 抓資料
cd scripts && python3 build_data.py

# 啟動本機網站
cd ..
python3 -m http.server 8765
# 開啟 http://127.0.0.1:8765
```

## Tailwind 樣式（正式版，免 Node）

網頁樣式改用「預先編好的」`assets/app.css`（取代過去的 `cdn.tailwindcss.com`，
正式環境較快、無 console 警告）。

**重新編譯已全自動**：只要把 `index.html`、`tailwind.config.js` 或
`assets/tailwind-input.css` 推上 `main`，GitHub Actions（`.github/workflows/build-css.yml`）
就會自動重編 `app.css` 並 commit 回來——不必手動跑指令，也不會發生「改了 class 卻忘了重編」。

需要在本機手動重編時（可選）：

```bash
# 1. 下載 Tailwind 獨立版工具（只需第一次；macOS Apple Silicon）
mkdir -p .build
curl -sL -o .build/tailwindcss \
  https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/tailwindcss-macos-arm64
chmod +x .build/tailwindcss

# 2. 重新編譯 CSS
.build/tailwindcss -c tailwind.config.js -i assets/tailwind-input.css -o assets/app.css --minify
```

- `tailwind.config.js`：掃描設定（含 safelist，保住 JS 動態組出的顏色 class）
- `assets/tailwind-input.css`：自訂樣式（漸層、卡片 hover 等）
- `assets/app.css`：編譯產物（**要 commit**，網站實際載入這支）
- `.build/`：工具二進位，已被 `.gitignore` 忽略

## 加新資料來源

1. 在 `scripts/` 新增 `source_xxx.py`，提供 `crawl()` 函式回傳 `list[dict]`
2. 用 `common.make_item(...)` 產出統一格式
3. 在 `build_data.py` 的 `sources` 列表加入新模組

## 自動化

GitHub Actions 設定：每天台灣時間 09:00 跑爬蟲，更新後自動 commit 回 main branch，GitHub Pages 同步更新。
