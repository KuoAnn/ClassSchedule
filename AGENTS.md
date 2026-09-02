# Agent 指示

這份檔案是本專案的**唯一規格來源**。

本專案保留 **[CLAUDE.md](CLAUDE.md)** 與 **[AGENTS.md](AGENTS.md)** 作為 AI 入口檔，
但**實際工作規格由本檔管理**。任何 AI 助理接手前，請先讀完本檔，再動任何一行程式。

## 專案形狀

```text
src/                  版面範本資源，可個別重用（打包時內嵌成單一 HTML）
  index.html          外框；{{title}} {{sheet_width}} {{styles}} {{boot}} {{content}} {{scripts}}
  styles/01..12*.css  樣式，數字前綴＝串接順序
  js/01..08*.js       腳本，數字前綴＝串接順序
  icons/*.svg         內嵌圖示
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

## 參考資訊

- **規格入口**：本檔 `AGENTS.md`
- **Claude 轉址**：`CLAUDE.md`
- **使用說明與 CI**：`README.md`

> 若你需要查完整專案定義，請直接從本檔開始。
