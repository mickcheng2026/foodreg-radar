#!/usr/bin/env bash
# 一鍵推送：更新資料 → commit → push → GitHub Pages 自動部署
#
# 用法：
#   ./推送.sh              # 只推送現有變更（最快，幾秒）
#   ./推送.sh --refresh    # 先跑爬蟲抓最新公告再推送（60-90 秒）

set -e
cd "$(dirname "$0")"

REFRESH=0
for arg in "$@"; do
  case "$arg" in
    --refresh|-r) REFRESH=1 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
  esac
done

echo "=== 食規雷達 推送 ==="

# 1. 可選：跑爬蟲
if [[ "$REFRESH" -eq 1 ]]; then
  echo "[1/4] 跑爬蟲抓最新公告..."
  (cd scripts && python3 build_data.py) || { echo "爬蟲失敗"; exit 1; }
  echo
fi

# 2. 拉一次線上版（避免衝突）
echo "[2/4] 同步線上版本..."
git pull --rebase origin main 2>&1 | tail -5 || {
  echo "Pull 失敗 — 可能線上有改動衝突，請手動處理或刪 .git 重來"; exit 1;
}
echo

# 3. 看有沒有要 commit 的變更（沒 commit 的檔案）
echo "[3/4] 偵測變更..."
HAS_WORKING_CHANGES=0
HAS_UNPUSHED_COMMITS=0

if [[ -n "$(git status --porcelain)" ]]; then
  HAS_WORKING_CHANGES=1
  git status --short
  git add -A
  git commit -m "chore: 更新 $(date '+%Y-%m-%d %H:%M')"
fi

# 也檢查「已 commit 但還沒 push」的部分
if [[ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]]; then
  HAS_UNPUSHED_COMMITS=1
  echo "  本機領先 origin/main："
  git log origin/main..HEAD --oneline | sed 's/^/    /'
fi

if [[ "$HAS_WORKING_CHANGES" -eq 0 && "$HAS_UNPUSHED_COMMITS" -eq 0 ]]; then
  echo "  完全沒有變更（檔案沒改、commit 沒落後），結束。"
  exit 0
fi
echo

# 4. 推送
echo "[4/4] 推送到 GitHub..."
git push -u origin main || {
  echo
  echo "❌ Push 失敗。常見原因："
  echo "  1. 第一次推送：要先設定 GitHub Personal Access Token (PAT)"
  echo "     → 看 設定git推送.md 步驟"
  echo "  2. 網路斷線"
  exit 1
}

echo
echo "✅ 完成！1-2 分鐘後網站會更新："
echo "   https://mickcheng2026.github.io/foodreg-radar/"
