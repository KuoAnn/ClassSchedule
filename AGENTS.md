# Agent 指示

這份檔案是本專案的**唯一規格來源**。

本專案保留 **[CLAUDE.md](CLAUDE.md)** 與 **[AGENTS.md](AGENTS.md)** 作為 AI 入口檔，
但**實際工作規格由本檔管理**。任何 AI 助理接手前，請先讀完本檔，再動任何一行程式。

## 專案形狀

```text
src/                  版面範本資源，可個別重用（打包時內嵌成單一 HTML）
  index.html          外框；{{title}} {{og_desc}} {{styles}} {{boot}} {{content}} {{scripts}}
  styles/01..13*.css  樣式，數字前綴＝串接順序
  js/01..09*.js       腳本，數字前綴＝串接順序
  icons/*.svg         內嵌圖示（`favicon.svg` 走 data URI，見下）
scripts/build.py      產生器：CSV → 卡片 HTML，再把 src/ 內嵌成單一檔
scripts/run.sh        產檔 + 四項檢查
scripts/checks/       occl.py／wcag.py／catcheck.py（＋ clock.py、de.py 為輔助）
data/                 課程 CSV
dist/                 產物
.github/workflows/    推 main 時產檔、跑檢查、發佈 Pages
```

## 核心規則

1. 只改 `src/` 與 `scripts/`，不要改 `dist/` 裡的 HTML（那是產物）
2. 改完必跑：`./scripts/run.sh`，四項檢查**全部必須是 0**（不是 0 會直接以非 0 結束）
3. 不要為了讓檢查通過而放寬標準
4. 新增規格時，把「為什麼」一起寫進本檔
5. 若要為 AI 入口檔做跨檔對齊，請維持 `AGENTS.md` 為主，`CLAUDE.md` 做轉址

## 拆檔後的四條約束

拆成資源檔是為了好維護，但打包後必須與原本的單檔行為一致，所以：

1. **檔名數字前綴就是串接順序，不要重排、不要改名而不改順序。**
   CSS 有幾組 specificity 相同、靠先後決勝負的規則，例如
   `.sheet.flat .ndock{display:none}` 與 `.ndock.show{display:flex}`、
   `.sheet.noto .tdy{display:none}` 與 `.dn.today .tdy{display:inline-block}`。
   `05-export-mode.css` 因此必須夾在 `04-narrow.css` 與 `06-narrow-card.css` 之間，
   搬到最後會改變匯出圖片的外觀。
2. **JS 是串成同一個 `<script>` 的**，彼此靠全域 `var`／`function` 互相呼叫
   （`fitCells`、`markPast`、`track`、`syncRows`、`picked`…）。
   拆檔時不要加 `"use strict"`、不要包成 IIFE、不要改成 module，會直接壞掉。
   `01-boot.js` 例外：它單獨放在 `<body>` 開頭，必須在畫面繪製前決定 `html.nv/.wv`。
3. **build 期的值不寫死在資源檔裡。**
   `01-tokens.css` 的 `--gy`／`--gut`／`--sheetw` 只是離線預覽的預設值，
   `build.py` 會在樣式尾端補一段 `:root{…}` 覆寫；
   PNG 檔名走 `window.SCHEDULE`（由 build 產生，`08-export.js` 沒有時退回 `schedule.png`）。
4. **`src/index.html` 的 `{{…}}` 佔位符要與 `build.py` 的 `FILL` 一致**，
   多打少打都會在 build 時直接丟 `KeyError`（這是刻意的，不要改成靜默略過）。

## 站台圖示（favicon）

`src/icons/favicon.svg`（K 標誌）由 `build.py` 的 `data_icon()` 轉成 data URI，
填進 `src/index.html` 的 `{{favicon}}`。**不放外部 `.ico`／`.png`**，
因為產物必須維持單一 HTML（Pages 只發佈 `dist/` 的那一份，外部檔會 404）。
圖示是純幾何 SVG、沒有 `<text>`，才不會在缺字型的環境裡變成空白。

## LINE LIFF：五條約束

站台掛 GitHub Pages，實際由 LINE LIFF 開啟，所以「手機 WebView」才是主場景。
**本站是純靜態課表、不讀任何會員資料**，因此不呼叫 `liff.login()` / `liff.getProfile()`，
也不設 `withLoginOnExternalBrowser` — 一般瀏覽器開同一個網址不會被導去登入。

1. **viewport 是動態的，而且寬版要自己算縮放比例。**
   `src/index.html` 預設 `width=device-width,initial-scale=1,viewport-fit=cover`；
   寬版是固定寬的海報版面，切過去時由 `setViewport()`（定義在 `01-boot.js`，
   `05-view.js` 也會呼叫）改成 `width=<--sheetw>`。版面寬是從 CSS 變數 `--sheetw` 讀的，
   不是 build 寫死的字串，所以「build 期的值不寫死在資源檔裡」這條仍然成立。
   兩個坑（**都踩過**，不要「簡化」回去）：
   - **縮放比例要明寫成 `initial-scale`，不能只靠瀏覽器 auto-shrink。**
     LINE 的 WebView 對「載入後才改的 viewport」常常只吃寬度、不重算縮放，
     結果寬版超出螢幕、字擠成一團還要橫向拖。比例 = 裝置寬 ÷ `--sheetw`。
   - **裝置寬要在繪製前先量下來（`DEVW`）。** 換成 `width=2040` 之後
     `clientWidth` 量到的是版面寬、不是螢幕寬，那時候就來不及了。
     轉向會讓裝置寬變掉，`remeasureViewport()` 因此先退回 `device-width` 量一次
     再把寬版套回去。量不到（`DEVW` 為 0）才退回舊行為：不給 `initial-scale`。
   - **改 viewport 是整顆 `<meta>` 換掉，不是改 `content` 屬性。**
     WebView 對屬性變更有時直接不重新套用版面。
2. **`html` 的 class 只能用 `classList` 動，不可以直接指派 `className`。**
   `01-boot.js` 在繪製前掛上的 `.liff`（UA 含 `" Line/"`）會被整串覆蓋掉，
   `inLINE()` 就會回 false，長按存圖與 canvas 降階都失效。這個坑踩過一次。
3. **在 LINE 裡不能用 `<a download>` 存圖，所以存圖要丟出去給外部瀏覽器。**
   LINE 的 WebView（iOS 尤其）直接沒反應。`08-export.js` 按下下載時先問
   `openExternalDownload()`（`09-liff.js`）：在 LIFF 裡就用
   `liff.openWindow({external:true})` 把同一份課表開到系統瀏覽器，那邊才存得到檔；
   **回 true 就直接 return，不要在 WebView 裡先畫一次 canvas**（手機畫這張很慢，
   而且畫完也用不到）。因為 PNG 是前端現畫的、沒有網址可以傳，所以是用網址參數
   把「現在這一版」重現出來：`?dl=1&v=<n|w>&l=<zh|en>&cat=<分類>`。
   - `v` 必須在繪製前就讀到，所以 `qparam()` 放在 `01-boot.js`（不是 `09-liff.js`）；
     它同時也是 `?v=n` 這種分享連結的入口。
   - 網址帶 `v` 時 `05-view.js` **不寫** `localStorage`：外部瀏覽器只是借過去存圖一次，
     不該蓋掉那台瀏覽器自己記住的版型。存完 `09-liff.js` 會把參數 `replaceState` 清掉，
     所以清掉之後手動切版型仍然照記。
   - 只有 `liff.isInClient()` 為真才算 LIFF。從聊天室點一般連結進來的是 LINE 內建瀏覽器，
     那裡 `openWindow` 只會在 LINE 自己開新分頁，等於沒解決問題。
   這條和沒設 `LIFF_ID`／`liff.init` 失敗一樣，退回舊路：`saveImage()` 把 PNG 攤成全螢幕
   讓使用者長按儲存；`.shot img` 的 `-webkit-touch-callout:default` 不能拿掉，
   拿掉就沒有長按選單。覆蓋層是點下去才建出來的 DOM，所以 `occl.py` / `wcag.py`
   掃不到也不需要掃。
4. **手機的 canvas 上限比桌機低。**
   `08-export.js` 只在 LINE 或視窗 < 900px 時把 `scale` 壓到 12M 畫素以內；
   桌機維持 `scale:2`，匯出結果與過去完全相同。
5. **`13-liff.css` 放在最後是刻意的。**
   裡面都是要蓋過前面版型的補丁，而且 `html.nv .hd h1` 這種選擇器的 specificity
   比 `@media` 裡的 `.hd h1` 高 — 想在窄版覆寫尺寸，選擇器就得一樣帶 `html.nv`。

`LIFF_ID` 由 `build.py --liff-id`（或環境變數 `LIFF_ID`，CI 走 repo Variable）帶入，
產生 `window.LIFF_ID`；沒設也不會壞，只是不初始化 SDK。設定步驟見 README。

## 課表版本：只跟 CSV 一起跑

課表會在月中改（代課、暫停），改過就要重新貼進 LINE，所以圖上要有版本號讓人分辨新舊。
規則：**一個月從 1.0 開始跑，1.0 不印出來**（當月第一版不需要標「第一版」），
1.1 起才在署名旁邊以小字顯示 `v1.1`。

版本代表「這份課表改到第幾版」，不是站台版本，所以 `resolve_version()`（`scripts/build.py`）
**只看 CSV 內容**：改版面、改樣式、重新產檔都不該讓版本跳號。編號記在 `data/versions.json`，
一個月一筆（key 是 `<館別>-<年>-<月>`），值是這個月依序出現過的 CSV 指紋，
指紋在陣列裡的序號就是小版號。

- 指紋算之前會把 CRLF 與尾端空白正規化 —— 編輯器換個存檔格式不該算改版。
- 沒見過的指紋會 append 並寫回 json。**這個 json 要跟著 commit**：
  CI 端只要 json 是最新的，算出來就跟本機一致；寫不進去（唯讀環境）也不會壞，
  版本仍然算得出來，只是下一次沒有紀錄可對。
- 要手動指定用 `--version 1.3`（`--version 1.0` 一樣不顯示）。
- 署名 `.by` 在 `@media (max-width:560px)` 是隱藏的，但匯出的圖不該少版本號，
  所以 `05-export-mode.css` 用 `.sheet.flat .hd .by{display:block}` 蓋回來
  （media query 不加權重，選擇器帶 `.sheet.flat` 就贏）。

## 匯出圖片：直式要留住時間軸

畫面上的窄版讓七天逐時對齊（`syncRows()`＋左側 `.ngut` 時間欄），
匯出的直式圖片**同樣維持這個對齊**：時間欄是七天共用的一欄，
只要有任何一天自己把卡片往上收，`10:00`、`11:00` 就會指到別的時段的卡片，
那是錯的資訊。所以「收掉空堂」不能用「整列 `display:none`／`height:auto`」來做
（那一版把時間欄也一起藏了，等於少一個看整週的座標）。

空堂的留白改從卡片本身省：`08-export.js` 在窄版匯出時加 `npack`（`05-export-mode.css`），
壓掉 `.lc` 的內距、行距、`.bt` 的上緣間距，並把空的 `.bt` 收掉。
螢幕上那些留白是為了好點擊，印成圖只是白費高度。實測 2900px → 2447px。

**卡片變矮之後一定要重算對齊高度**：`syncRows()` 把跨日對齊的高度寫成 inline style，
不重算就會每一列都留著舊卡片的空白。所以 `08-export.js` 掛上 `npack` 之後呼叫一次
`syncRows()`，`restore()` 裡再呼叫一次還原。`restore()` 的順序是
**先 `markPast()` 再 `syncRows()`** —— 狀態標籤 `.stt` 是塞進 `.nr` 的、會撐高卡片，
順序反了就會拿缺標籤的高度去對齊，卡片被 `.hrow` 的 `overflow:hidden` 切掉。

PNG 的 URL 走 `canvas.toBlob()`，`toDataURL()` 只當退路：幾 MB 的 data URL
在手機瀏覽器上常常直接不下載，而外部瀏覽器下載正是主要路徑。


## 參考資訊

- **規格入口**：本檔 `AGENTS.md`
- **Claude 轉址**：`CLAUDE.md`
- **使用說明與 CI**：`README.md`

> 若你需要查完整專案定義，請直接從本檔開始。
