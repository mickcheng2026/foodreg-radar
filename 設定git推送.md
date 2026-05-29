# Git 一鍵推送設定（只做一次）

> 第一次跑 `./推送.sh` 時會要求您輸入 GitHub 帳號密碼。但 GitHub 不再接受網頁密碼，必須改用「個人存取權杖」(Personal Access Token，簡稱 PAT)。**做完這份指南後，未來推送都不會再問**。

## 為什麼需要 PAT？

GitHub 2021 年起禁止用網頁密碼透過命令列推送。PAT 等同於命令列專用的密碼，安全性更高（可隨時撤銷、可限制權限）。

---

## 步驟 1：建立 Personal Access Token

1. 登入 GitHub 後，點右上角您的頭像 → **Settings**
2. 拉到左側選單**最底下** → **Developer settings**
3. 左側選單 → **Personal access tokens** → **Tokens (classic)**
4. 右上 **Generate new token** → **Generate new token (classic)**
5. 填寫：
   - **Note**（備註）：`foodreg-radar 推送用`
   - **Expiration**（有效期）：**No expiration**（永不過期）或 **90 days**（自動到期需重建，更安全）
   - **Select scopes**（權限）：**只勾這一個**
     - ☑ `repo` — Full control of private repositories（這會把底下所有子權限自動勾好）
6. 拉到底 → **Generate token**
7. **重要**：畫面會顯示一串 `ghp_xxxxxxxxxxxxxxxxxxxx`（30+ 字元）
   - **馬上複製**（⌘+C）
   - **離開頁面後就再也看不到了**，貼到筆記本或安全的地方暫存

---

## 步驟 2：第一次推送（讓 macOS 記住 token）

1. 打開終端機
2. `cd` 到專案資料夾：
   ```bash
   cd "/Users/mick/Desktop/claude code files/teamnotes-vault/條文自動更新 網站"
   ```
3. 跑推送腳本：
   ```bash
   ./推送.sh
   ```
4. 跳出對話框（可能是終端機文字提示，也可能是 macOS GUI 視窗）：
   - **Username**：輸入 `mickcheng2026`（您的 GitHub 帳號）
   - **Password**：**貼上剛剛複製的 PAT**（`ghp_xxxxx...`）
     - ⚠️ 不是您 GitHub 網頁的登入密碼，是 PAT
     - ⚠️ 貼上時可能不會顯示星號，這是正常的
5. 按 Enter

✅ 成功的話會看到：
```
✅ 完成！1-2 分鐘後網站會更新：
   https://mickcheng2026.github.io/foodreg-radar/
```

✅ macOS 鑰匙圈會把 PAT 記住 — **以後再跑 `./推送.sh` 都不會再問密碼**。

---

## 之後的日常使用

```bash
cd "/Users/mick/Desktop/claude code files/teamnotes-vault/條文自動更新 網站"

./推送.sh              # 只推送現有變更（最快）
./推送.sh --refresh    # 先抓最新公告 → 推送
```

或更輕鬆：直接在 Claude Code 對話框輸入「**FoodReg 推送**」或「**FoodReg 抓新資料推送**」，我就會幫您跑。

---

## 萬一忘記密碼 / 想撤銷 token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 找到 `foodreg-radar 推送用` → **Delete**
3. 同時清掉 macOS 鑰匙圈裡的舊記錄：
   ```bash
   git config --global --unset credential.helper  # 暫時關閉自動記憶
   ```
4. 重新做步驟 1+2

---

## 疑難雜症

| 錯誤訊息 | 解法 |
|---|---|
| `Authentication failed` | PAT 打錯或過期，重做步驟 1 |
| `Repository not found` | 確認 GitHub 上 repo 確實叫 `foodreg-radar`（區分大小寫） |
| `Updates were rejected` | 線上版有改動，先 `git pull origin main` 再推 |
| 卡住沒反應 | 按 Ctrl+C 中斷，重跑 |
