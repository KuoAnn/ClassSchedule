# Agent 指示

這份檔案是本專案的**唯一規格來源**。

本專案保留 **[CLAUDE.md](CLAUDE.md)** 與 **[AGENTS.md](AGENTS.md)** 作為 AI 入口檔，
但**實際工作規格由本檔管理**。任何 AI 助理接手前，請先讀完本檔，再動任何一行程式。

## 核心規則

1. 只改 `build.py`，不要改 `dist/` 裡的 HTML（那是產物）
2. 改完必跑：`python3 build.py` 然後 `./run.sh` 的四項檢查，**全部必須是 0**
3. 不要為了讓檢查通過而放寬標準
4. 新增規格時，把「為什麼」一起寫進本檔，不要再用 AI_INSTRUCTIONS 累積重複內容
5. 若要為 AI 入口檔做跨檔對齊，請維持 `AGENTS.md` 為主，`CLAUDE.md` 做轉址

## 參考資訊

- **規格入口**：本檔 `AGENTS.md`
- **Claude 轉址**：`CLAUDE.md`
- **AI_INSTRUCTIONS**：已退役，僅保留兼容提醒，不再作為主要資料來源

> 若你需要查完整專案定義，請直接從本檔開始，不要再依賴 AI_INSTRUCTIONS。
