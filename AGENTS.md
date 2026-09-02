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

1. **viewport 是動態的，不要再寫死。**
   `src/index.html` 預設 `width=device-width,initial-scale=1,viewport-fit=cover`；
   寬版是固定寬的海報版面，切過去時由 `setViewport()`（定義在 `01-boot.js`，
   `05-view.js` 也會呼叫）改成 `width=<--sheetw>`，且**不給 initial-scale**，
   讓瀏覽器整頁縮放。版面寬是從 CSS 變數 `--sheetw` 讀的，不是 build 寫死的字串，
   所以「build 期的值不寫死在資源檔裡」這條仍然成立。
2. **`html` 的 class 只能用 `classList` 動，不可以直接指派 `className`。**
   `01-boot.js` 在繪製前掛上的 `.liff`（UA 含 `" Line/"`）會被整串覆蓋掉，
   `inLINE()` 就會回 false，長按存圖與 canvas 降階都失效。這個坑踩過一次。
3. **在 LINE 裡不能用 `<a download>` 存圖。**
   LINE 的 WebView（iOS 尤其）直接沒反應。`08-export.js` 改成呼叫
   `saveImage()`（`09-liff.js`），在 LINE 裡把 PNG 攤成全螢幕讓使用者長按儲存；
   `.shot img` 的 `-webkit-touch-callout:default` 不能拿掉，拿掉就沒有長按選單。
   覆蓋層是點下去才建出來的 DOM，所以 `occl.py` / `wcag.py` 掃不到也不需要掃。
4. **手機的 canvas 上限比桌機低。**
   `08-export.js` 只在 LINE 或視窗 < 900px 時把 `scale` 壓到 12M 畫素以內；
   桌機維持 `scale:2`，匯出結果與過去完全相同。
5. **`13-liff.css` 放在最後是刻意的。**
   裡面都是要蓋過前面版型的補丁，而且 `html.nv .hd h1` 這種選擇器的 specificity
   比 `@media` 裡的 `.hd h1` 高 — 想在窄版覆寫尺寸，選擇器就得一樣帶 `html.nv`。

`LIFF_ID` 由 `build.py --liff-id`（或環境變數 `LIFF_ID`，CI 走 repo Variable）帶入，
產生 `window.LIFF_ID`；沒設也不會壞，只是不初始化 SDK。設定步驟見 README。

## 參考資訊

- **規格入口**：本檔 `AGENTS.md`
- **Claude 轉址**：`CLAUDE.md`
- **使用說明與 CI**：`README.md`

> 若你需要查完整專案定義，請直接從本檔開始。
