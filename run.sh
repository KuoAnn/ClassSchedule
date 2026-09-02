#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 build.py "$@"
echo "--- 遮蔽檢查 ---";   python3 checks/occl.py
echo "--- 對比度 寬版 ---"; python3 checks/wcag.py
echo "--- 對比度 窄版 ---"; python3 checks/wcag.py 375
echo "--- 色票對應 ---";   python3 checks/catcheck.py
