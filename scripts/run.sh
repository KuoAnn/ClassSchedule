#!/usr/bin/env bash
# 產檔 + 四項檢查一次跑完；任何一項非 0 就停
set -e
cd "$(dirname "$0")/.."

# 找一個真的跑得起來的 Python（Windows 上 python3 可能是 Store 的空殼）
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
if [ -z "$PY" ]; then
  echo "找不到可用的 Python，請設定 PYTHON=<路徑>" >&2
  exit 1
fi

"$PY" scripts/build.py "$@"
echo "--- 遮蔽檢查 ---";   "$PY" scripts/checks/occl.py
echo "--- 對比度 寬版 ---"; "$PY" scripts/checks/wcag.py
echo "--- 對比度 窄版 ---"; "$PY" scripts/checks/wcag.py 375
echo "--- 色票對應 ---";   "$PY" scripts/checks/catcheck.py
