#!/usr/bin/env bash
# 一鍵推送：更新資料 → commit → 與線上合併 → push → GitHub Pages 自動部署
#
# 用法：
#   ./推送.sh              # 只推送現有變更（最快，幾秒）
#   ./推送.sh --refresh    # 先跑爬蟲抓最新公告再推送（60-90 秒）
#
# 重點：若線上有 CI 機器人的每日自動更新（你本機落後了），
# 本腳本會「自動合併」data/items.json 與 data/incident_titles.json
# （兩邊資料聯集，不會掉任何一邊），不再像舊版那樣把衝突誤 commit 進去。

set -e
cd "$(dirname "$0")"

REFRESH=0
for arg in "$@"; do
  case "$arg" in
    --refresh|-r) REFRESH=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
  esac
done

# 可自動合併的資料檔（其他檔案衝突一律停下來請人處理）
AUTO_MERGE_FILES="data/items.json data/incident_titles.json"

echo "=== 食規雷達 推送 ==="

# 1. 可選：跑爬蟲
if [[ "$REFRESH" -eq 1 ]]; then
  echo "[1/5] 跑爬蟲抓最新公告..."
  (cd scripts && python3 build_data.py) || { echo "爬蟲失敗"; exit 1; }
  echo
else
  echo "[1/5] （略過爬蟲，用 --refresh 可先抓最新）"
fi

# 2. 先 commit 本機變更（在碰線上之前，確保自己的工作已是正式提交）
echo "[2/5] 偵測並提交本機變更..."
if [[ -n "$(git status --porcelain)" ]]; then
  git status --short
  git add -A
  git commit -m "chore: 更新 $(date '+%Y-%m-%d %H:%M')"
else
  echo "  工作目錄乾淨（沒有未提交的檔案）"
fi

# 若本機沒有領先 origin/main 的 commit，就沒東西好推
git fetch origin 2>&1 | tail -2 || { echo "fetch 失敗（網路？）"; exit 1; }
if [[ -z "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]]; then
  echo "  沒有要推送的 commit（已與線上同步），結束。"
  exit 0
fi
echo "  本機領先 origin/main："
git log origin/main..HEAD --oneline | sed 's/^/    /'
echo

# 3. 與線上合併（若線上有新版本，rebase 並自動解決資料檔衝突）
echo "[3/5] 與線上版本合併..."
if git merge-base --is-ancestor origin/main HEAD; then
  echo "  本機已包含線上最新，無需合併。"
else
  echo "  線上有新版本（可能是每日自動更新），rebase 合併中..."
  git rebase origin/main || true

  guard=0
  while [[ -d .git/rebase-merge || -d .git/rebase-apply ]]; do
    guard=$((guard+1))
    if [[ "$guard" -gt 50 ]]; then
      echo "❌ 合併迴圈異常，已中止 rebase。"; git rebase --abort || true; exit 1
    fi

    UNRESOLVED="$(git diff --name-only --diff-filter=U)"
    if [[ -z "$UNRESOLVED" ]]; then
      GIT_EDITOR=true git rebase --continue || true
      continue
    fi

    # 確認所有衝突檔都是可自動合併的資料檔
    BAD=0
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      case " $AUTO_MERGE_FILES " in
        *" $f "*) ;;
        *) BAD=1; echo "  ⚠ 無法自動合併：$f" ;;
      esac
    done <<< "$UNRESOLVED"

    if [[ "$BAD" -eq 1 ]]; then
      echo
      echo "❌ 有非資料檔的衝突，無法自動處理。已安全還原（rebase --abort）。"
      echo "   請手動處理上面標示的檔案，或找 Claude 幫忙。"
      git rebase --abort || true
      exit 1
    fi

    # 逐一自動合併（stage 2 = 線上版，stage 3 = 本機版）
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      REMOTE_TMP="$(mktemp)"; LOCAL_TMP="$(mktemp)"
      if git show ":2:$f" > "$REMOTE_TMP" 2>/dev/null && git show ":3:$f" > "$LOCAL_TMP" 2>/dev/null; then
        python3 scripts/merge_data.py "$LOCAL_TMP" "$REMOTE_TMP" "$f"
        git add "$f"
      else
        echo "  ⚠ 無法取得 $f 的兩個版本，改用本機版。"
        git checkout --theirs -- "$f" 2>/dev/null || true
        git add "$f"
      fi
      rm -f "$REMOTE_TMP" "$LOCAL_TMP"
    done <<< "$UNRESOLVED"

    GIT_EDITOR=true git rebase --continue || true
  done
  echo "  合併完成。"
fi
echo

# 4. 再檢查一次仍領先（合併後理應有東西可推）
echo "[4/5] 確認待推送內容..."
if [[ -z "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]]; then
  echo "  合併後沒有需要推送的內容，結束。"
  exit 0
fi
echo

# 5. 推送
echo "[5/5] 推送到 GitHub..."
git push origin main || {
  echo
  echo "❌ Push 失敗。常見原因："
  echo "  1. 第一次推送：要先設定 GitHub Personal Access Token (PAT) → 看 設定git推送.md"
  echo "  2. 網路斷線"
  echo "  3. 線上又有新 commit：再跑一次 ./推送.sh 即可（會自動合併）"
  exit 1
}

echo
echo "✅ 完成！1-2 分鐘後網站會更新："
echo "   https://mickcheng2026.github.io/foodreg-radar/"
