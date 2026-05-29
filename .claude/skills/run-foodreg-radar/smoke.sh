#!/usr/bin/env bash
# 食規雷達 smoke driver
#
# 用途：在一次執行內驗證整個應用可運作
#   1. 可選：跑爬蟲 (--fetch) 重新產生 data/items.json
#   2. 驗證 items.json 是合法 JSON 且非空
#   3. 啟動本機 HTTP 伺服器
#   4. curl 抓 index.html 與 data/items.json 確認 200 + 內容
#   5. 解析 index.html 確認骨架 (Header / Feed / Footer / loader)
#   6. 關閉伺服器
#
# 用法：
#   ./smoke.sh             # 只驗證現有資料 + 伺服器 (~3 秒)
#   ./smoke.sh --fetch     # 連同重新跑爬蟲 (~60-90 秒，需網路)
#   PORT=9000 ./smoke.sh   # 自訂 port (預設 8765)

set -euo pipefail

# 路徑：腳本在 .claude/skills/run-foodreg-radar/，專案根在向上 3 層
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PORT="${PORT:-8765}"
FETCH=0
SERVER_PID=""

for arg in "$@"; do
  case "$arg" in
    --fetch) FETCH=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "未知選項：$arg" >&2; exit 2 ;;
  esac
done

cd "$ROOT"

cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    echo "[cleanup] stopped server pid=$SERVER_PID"
  fi
}
trap cleanup EXIT

echo "=== 食規雷達 smoke ==="
echo "root  : $ROOT"
echo "port  : $PORT"
echo "fetch : $FETCH"
echo

# 1. 可選：跑爬蟲
if [[ "$FETCH" -eq 1 ]]; then
  echo "[1/5] 執行爬蟲 (python3 scripts/build_data.py)..."
  (cd scripts && python3 build_data.py) || { echo "FAIL: 爬蟲失敗"; exit 1; }
  echo
fi

# 2. 驗證 items.json
echo "[2/5] 驗證 data/items.json..."
if [[ ! -f data/items.json ]]; then
  echo "FAIL: data/items.json 不存在 — 先用 --fetch 跑一次"
  exit 1
fi
python3 -c "
import json, sys
with open('data/items.json', encoding='utf-8') as f:
    d = json.load(f)
assert 'items' in d, 'missing items field'
assert 'updated_at' in d, 'missing updated_at field'
assert isinstance(d['items'], list), 'items not list'
assert len(d['items']) > 0, 'items is empty'
for it in d['items']:
    for k in ('title', 'url', 'source_label'):
        assert k in it, f'item missing {k}'
print(f\"  OK: {len(d['items'])} items, updated_at={d['updated_at']}\")
print(f\"  by_source: {d['stats']['by_source']}\")
" || exit 1
echo

# 3. 啟動本機伺服器
echo "[3/5] 啟動 python3 -m http.server $PORT..."
# pkill 殘留同 port 伺服器（避免 address already in use）
pkill -f "http.server $PORT" 2>/dev/null && sleep 0.3 || true
python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/foodreg-smoke.log 2>&1 &
SERVER_PID=$!
# 等到 port 可用 (最多 5 秒)
for i in {1..50}; do
  if curl -sf "http://127.0.0.1:$PORT/" -o /dev/null; then break; fi
  sleep 0.1
done
if ! curl -sf "http://127.0.0.1:$PORT/" -o /dev/null; then
  echo "FAIL: 伺服器未就緒"
  cat /tmp/foodreg-smoke.log
  exit 1
fi
echo "  OK: server pid=$SERVER_PID"
echo

# 4. curl 驗證關鍵 endpoint
echo "[4/5] HTTP 端點檢查..."
status_index=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/index.html")
status_json=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/data/items.json")
[[ "$status_index" == "200" ]] || { echo "FAIL: index.html $status_index"; exit 1; }
[[ "$status_json"  == "200" ]] || { echo "FAIL: items.json $status_json"; exit 1; }
echo "  OK: GET /index.html -> 200"
echo "  OK: GET /data/items.json -> 200"

# 確認 json 透過 server 仍是合法
curl -sf "http://127.0.0.1:$PORT/data/items.json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['stats']['total'] > 0
" || { echo "FAIL: 透過 server 的 JSON 無效"; exit 1; }
echo "  OK: items.json 經 server 仍為合法 JSON"
echo

# 5. HTML 骨架檢查
echo "[5/5] HTML 結構檢查..."
html=$(curl -sf "http://127.0.0.1:$PORT/index.html")
checks=(
  '<title>食規雷達'
  'id="search-input"'
  'id="source-chips"'
  'id="feed"'
  'id="stats-grid"'
  'fetch("data/items.json"'
)
for needle in "${checks[@]}"; do
  if grep -qF "$needle" <<< "$html"; then
    echo "  OK: 找到 $needle"
  else
    echo "  FAIL: 缺少 $needle"
    exit 1
  fi
done
echo

echo "=== ALL CHECKS PASSED ==="
echo
echo "下一步："
echo "  • 視覺檢查：open http://127.0.0.1:$PORT/  (smoke 結束後 server 會關閉，請手動跑下行)"
echo "      python3 -m http.server $PORT --bind 127.0.0.1"
echo "  • 重新抓資料：$0 --fetch"
