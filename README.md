# 瑜伽課表產生器

讀一份 CSV，產生**單一個 HTML 檔**的月課表。不需要伺服器，雙擊即可開。

- 寬版（週課表格線）／窄版（單日輪播）兩種版型，記憶上次選擇
- 中／英雙語即時切換
- 分類色票可點擊篩選
- 一鍵匯出 PNG（樣式跟隨當前模式）
- 全站通過 WCAG AA

## 快速開始

```bash
pip install -r requirements.txt
playwright install chromium        # 只有跑檢查腳本才需要

python3 build.py                   # 自動抓 data/ 下最新的 CSV
open dist/古亭館-09月課表.html
```

指定參數：

```bash
python3 build.py \
  --csv data/古亭館115年10月瑜伽課表.csv \
  --month 10 --branch 古亭館 \
  --byline "Lulu 製作"
```

月份與館別預設由檔名推斷（`古亭館115年09月瑜伽課表.csv` → 古亭館 / 9 月）。

## 每月更新流程

1. 把新的一份 CSV 放進 `data/`（格式見 `data/template.csv`）
2. `python3 build.py`
3. 看終端機印出的 **WARN**，確認資料問題
4. 跑檢查：

```bash
./run.sh          # 產檔 + 四項檢查一次跑完
```

5. 開 `dist/*.html`，右上角可切換版型與語言、下載圖片

## 檢查腳本

| 腳本 | 檢查什麼 | 通過標準 |
|---|---|---|
| `checks/occl.py` | 文字是否被遮蔽／重疊／裁切 | 0 |
| `checks/wcag.py` | 對比度（帶寬度參數，如 `375`） | 0 |
| `checks/catcheck.py` | 卡片顏色是否符合分類色票、堂數是否與 CSV 一致 | 0 |

加 `FAKE_CLOCK=1` 可把時間固定在週三 14:20，驗證「今天」與「已開始」狀態：

```bash
FAKE_CLOCK=1 python3 checks/wcag.py
```

## 無障礙

通過 WCAG 2.2 AA：對比度、鍵盤操作、焦點可見、觸控目標 ≥ 24px、
語言標記、ARIA 狀態、篩選結果朗讀、`prefers-reduced-motion`。
細節與理由見 `AI_INSTRUCTIONS.md` 第 14 節。

## 專案結構

```
build.py              產生器（唯一要改的地方）
AI_INSTRUCTIONS.md    完整規格 — AI 接手前必讀
CLAUDE.md             指向 AI_INSTRUCTIONS.md
data/                 課程 CSV 與空白範本
checks/               三支驗證腳本
dist/                 產出的 HTML（git 不追蹤內容）
```

## 給 AI 助理

**改任何東西之前請先讀 [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md)。**
裡面每一條規格都有原因，包含踩過的坑（語言切換的選擇器陷阱、
sticky 在 html2canvas 下的定位問題、難度標籤壓到時間的成因等）。

不要改 `dist/` 裡的 HTML — 那是產物，下次產檔會被覆蓋。
