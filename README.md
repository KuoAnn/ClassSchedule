# 瑜伽課表產生器

讀一份 CSV，產生**單一個 HTML 檔**的月課表。不需要伺服器，雙擊即可開。

版面是拆開維護的（`src/` 下的 HTML／CSS／JS／SVG），**打包時才內嵌成一個檔**，
所以「好維護」和「單檔可攜」兩件事同時成立。

- 寬版（週課表格線）／窄版（單日輪播）兩種版型，記憶上次選擇
- 中／英雙語即時切換
- 分類色票可點擊篩選
- 一鍵匯出 PNG（樣式跟隨當前模式；直式會收掉空堂、卡片緊密排列）
- 全站通過 WCAG AA
- 可直接掛成 **LINE LIFF**（純靜態、不讀會員資料，不需要登入）

## 快速開始

```bash
pip install -r requirements.txt
playwright install chromium        # 只有跑檢查腳本才需要

python3 scripts/build.py           # 自動抓 data/ 下最新的 CSV
open dist/古亭館-09月課表.html
```

指定參數：

```bash
python3 scripts/build.py \
  --csv data/古亭館115年10月瑜伽課表.csv \
  --month 10 --branch 古亭館 \
  --byline "Lulu 製作"
```

月份與館別預設由檔名推斷（`古亭館115年09月瑜伽課表.csv` → 古亭館 / 9 月）。

## 每月更新流程

1. 把新的一份 CSV 放進 `data/`（格式見 `data/template.csv`）
2. `python3 scripts/build.py`
3. 看終端機印出的 **WARN**，確認資料問題
4. 跑檢查：

```bash
./scripts/run.sh      # 產檔 + 四項檢查一次跑完，任一項不是 0 就中斷
```

5. 開 `dist/*.html`，右上角可切換版型與語言、下載圖片

## 範本資源

`src/` 是可個別重用的資源檔；`scripts/build.py` 在打包時把它們內嵌進單一 HTML。

```text
src/index.html      外框（{{styles}}、{{boot}}、{{content}}、{{scripts}} 由 build.py 填）
src/styles/*.css    13 份樣式，檔名的數字前綴就是串接順序（＝cascade 順序）
src/js/*.js         9 份腳本，同樣依數字前綴串接
src/icons/*.svg     內嵌圖示（版型切換、下載、翻頁、早／午／晚）
```

- 檔名前綴決定順序，**不要重排**：CSS 有幾組同 specificity 的規則靠先後決勝負
  （例如 `05-export-mode.css` 必須夾在窄版與面板樣式之間）
- `01-tokens.css` 的 `--gy` / `--gut` / `--sheetw` 是離線預覽用的預設值，
  實際尺寸由 build 依課表算出後在樣式尾端覆寫
- `08-export.js` 的 PNG 檔名讀 `window.SCHEDULE`，由 build 產生；沒有時退回 `schedule.png`
- `01-boot.js` 會在畫面繪製前決定版型與 viewport，必須留在最前面
- `13-liff.css` / `09-liff.js` 是 LINE WebView 專用的補丁，放在最後（見下節）

單獨改版面時，直接編輯 `src/` 下的檔案再重跑 build 即可，不需要碰 Python。

## 檢查腳本

| 腳本 | 檢查什麼 | 通過標準 |
|---|---|---|
| `scripts/checks/occl.py` | 文字是否被遮蔽／重疊／裁切 | 0 |
| `scripts/checks/wcag.py` | 對比度（帶寬度參數，如 `375`） | 0 |
| `scripts/checks/catcheck.py` | 卡片顏色是否符合分類色票、堂數是否與 CSV 一致 | 0 |

三支都會在不是 0 時以非 0 結束，所以 `run.sh` 與 CI 會直接失敗。

加 `FAKE_CLOCK=1` 可把時間固定在週三 14:20，驗證「今天」與「已開始」狀態：

```bash
FAKE_CLOCK=1 python3 scripts/checks/wcag.py
```

## CI

`.github/workflows/build.yml`：推到 `main`（或手動 dispatch）就重新產檔、跑四項檢查
（含 `FAKE_CLOCK` 的第二輪），並附上可直接下載的單一 HTML artifact；
發佈 Pages 是獨立的 `pages` job，Pages 出問題不會連坐產檔與檢查的結果。

已發佈在 <https://kuoann.github.io/ClassSchedule/>（首頁就是最新一份課表）。

Pages 要先在 repo 上啟用一次，否則 `configure-pages` 會死在
`Get Pages site failed ... Not Found`：**Settings → Pages → Source** 選
**GitHub Actions**，或 `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`。
workflow 裡的 `enablement: true` 只是保險 — 站已存在時它單純讀設定，真的要建站
會被 `GITHUB_TOKEN` 拒絕（`Resource not accessible by integration`）。

不想用 Pages 就把 `pages` job 移掉，`build` 的 artifact 照樣拿得到。

只改 `*.md` 的 commit 不會觸發。

## LINE LIFF

站台掛在 GitHub Pages，透過 LINE LIFF 開啟。**本站是純靜態課表，不讀任何會員資料**，
所以不呼叫 `liff.login()` / `liff.getProfile()`，也不設 `withLoginOnExternalBrowser` —
用一般瀏覽器開同一個網址不會被導去登入。

### 設定

1. LINE Developers → Provider → **LINE Login** channel → **LIFF** → Add
2. **Endpoint URL** 填 Pages 網址（<https://kuoann.github.io/ClassSchedule/>）
3. **Size** 選 **Full**（課表很長，compact/tall 會太擠）
4. Scopes 只留 `profile` 以外的預設即可 — 本站不會去要授權
5. 把拿到的 LIFF ID 設成 repo 的 Actions Variable `LIFF_ID`
   （Settings → Secrets and variables → Actions → **Variables**）
6. 分享 `https://liff.line.me/<LIFF ID>` 給學員

`LIFF_ID` 沒設也不會壞：`09-liff.js` 只是不初始化 SDK，課表照樣顯示。
本機要帶的話：

```bash
python3 scripts/build.py --liff-id 1234567890-abcdefgh
# 或 LIFF_ID=1234567890-abcdefgh python3 scripts/build.py
```

### 為了 LINE 做了哪些事

| 問題 | 做法 |
|---|---|
| 原本 `viewport` 寫死 `width=2040`，手機上整張海報縮到看不清 | 預設 `width=device-width`；切到寬版時 `01-boot.js` / `05-view.js` 才換成版面寬 |
| LINE WebView 擋掉 `<a download>`，按了沒反應 | 在 LIFF 裡改用 `liff.openWindow({external:true})` 把同一份課表（`?dl=1&v=…&l=…&cat=…`）開到系統瀏覽器下載（`09-liff.js` 的 `openExternalDownload`）；沒有 SDK 時退回把 PNG 攤成全螢幕、長按存到相簿（`saveImage`） |
| 手機 canvas 上限比桌機低，寬版匯出會整個失敗 | `08-export.js` 依版面面積把 scale 壓到 12M 畫素以內（桌機仍是 scale 2） |
| iOS 把「11:00–12:00」判成電話號碼 | `<meta name="format-detection" content="telephone=no,date=no,address=no">` |
| 瀏海／home indicator 蓋住工具列與底部 | `viewport-fit=cover` ＋ `env(safe-area-inset-*)`（`13-liff.css`） |
| 輪播滑到底把手勢傳給外層，變成關掉 LIFF | `.ntrack{overscroll-behavior-x:contain}` |
| 橫向時 WebView 自動放大字、點擊留灰影 | `-webkit-text-size-adjust:100%`、`-webkit-tap-highlight-color:transparent` |
| 連結貼進聊天室沒有預覽 | `og:title` / `og:description`（由 build 依課表產生） |

LINE 的判定靠 UA 裡的 `" Line/"`，`01-boot.js` 會在繪製前掛上 `html.liff`，
JS 端用 `inLINE()` 讀同一個旗標。

## 無障礙

通過 WCAG 2.2 AA：對比度、鍵盤操作、焦點可見、觸控目標 ≥ 24px、
語言標記、ARIA 狀態、篩選結果朗讀、`prefers-reduced-motion`。
詳細規格與理由見 [AGENTS.md](AGENTS.md)。

## 專案結構

```text
src/                  版面範本資源（HTML／CSS／JS／SVG）
scripts/build.py      產生器：讀 CSV ＋ 內嵌 src/ → 單一 HTML
scripts/run.sh        產檔 + 四項檢查
scripts/checks/       三支驗證腳本
data/                 課程 CSV 與空白範本
dist/                 產出的 HTML（git 不追蹤內容）
AGENTS.md             主要規格來源（AI 接手前必讀）
CLAUDE.md             Claude 轉址入口
```

## 給 AI 助理

**改任何東西之前請先讀 [`AGENTS.md`](AGENTS.md)。**
`CLAUDE.md` 只是轉址入口，不再有單獨的規格來源。
裡面每一條規格都有原因，包含踩過的坑（語言切換的選擇器陷阱、
sticky 在 html2canvas 下的定位問題、難度標籤壓到時間的成因等）。

不要改 `dist/` 裡的 HTML — 那是產物，下次產檔會被覆蓋。
