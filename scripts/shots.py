# -*- coding: utf-8 -*-
"""把課表預先畫成四張 PNG：寬／窄 × 中／英，輸出到 dist/。

為什麼改成 build 時預製，而不是前端用 html2canvas 現畫：

* 手機畫這張要好幾秒，而且 canvas 有畫素上限，窄版整週那張在舊機器上會直接失敗。
* LINE 的 WebView 存不了 blob／`<a download>`，以前得把整份課表用網址參數
  （`?dl=1&v=…&l=…`）重現到外部瀏覽器再畫一次 —— 一條為了「畫圖」而存在的長路。
* 預製之後圖有固定網址，按下載就是導過去，LINE 裡長按即可存到相簿。

畫面狀態要跟舊的 `08-export.js` 完全一致（同一組 CSS class），所以那段流程照抄成
`EXPORT_JS`：解掉篩選、拿掉「現在幾點／今天星期幾」、窄版加 `npack`／`weekexp`、
把工具列之類的 `[data-noexport]` 藏起來（用 visibility 保留位置，版面才不會位移）。
"""
import glob
import os
import sys

from playwright.sync_api import sync_playwright

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 下載的是「完整課表」：分類篩選要解掉，時間狀態（今天／已結束／進行中）也要拿掉，
# 圖才跟「什麼時候按下下載」無關。這段與 08-export.js 的匯出流程是同一套 class。
EXPORT_JS = """
(v) => {
  const sheet = document.getElementById('sheet');
  if (typeof picked !== 'undefined' && picked !== null) { picked = null; applyFilter(); }
  fitCells();
  sheet.classList.add('nopast', 'flat', 'noto');
  document.querySelectorAll('.stt').forEach(c => c.remove());
  document.querySelectorAll('.st-done,.st-live').forEach(c => {
    c.classList.remove('st-done', 'st-live');
  });
  if (v === 'n') {
    sheet.classList.add('npack');
    if (!track.classList.contains('full')) sheet.classList.add('weekexp');
    syncRows();
  }
  sheet.querySelectorAll('[data-noexport]').forEach(el => {
    el.style.visibility = 'hidden';
  });
  return {w: sheet.offsetWidth, h: sheet.offsetHeight};
}
"""


def target():
    """要畫哪一份 HTML：參數指定，否則抓 dist/ 下最新的一份"""
    for a in sys.argv[1:]:
        if a.endswith(".html"):
            return os.path.abspath(a)
    f = sorted(glob.glob(os.path.join(_ROOT, "dist", "*.html")))
    if not f:
        sys.exit("找不到 dist/*.html，請先執行 python3 scripts/build.py")
    return f[-1]


def names(page):
    """檔名由 build.py 寫進 window.SCHEDULE.png，跟 08-export.js 讀的是同一份"""
    m = page.evaluate("() => (window.SCHEDULE && window.SCHEDULE.png) || null")
    if not m:
        sys.exit("HTML 裡沒有 window.SCHEDULE.png，build.py 與 shots.py 對不上")
    return m


def shoot(page, v, lang, out):
    page.evaluate("(v) => setView(v)", v)
    page.evaluate("(l) => applyLang(l)", lang)
    page.wait_for_timeout(120)
    box = page.evaluate(EXPORT_JS, v)
    # 視窗寬度要跟版面一樣寬，否則 @media 會照「手機視窗」出小一號的標題列。
    # 改視窗會觸發 resize（重算 --dayw、重排小時列），所以要再跑一次同一段收尾 ——
    # 那段是冪等的，重複套用不會有副作用
    page.set_viewport_size({"width": box["w"] + 40, "height": 900})
    page.wait_for_timeout(150)
    box = page.evaluate(EXPORT_JS, v)
    page.locator("#sheet").screenshot(path=out)
    return box


def main():
    src = target()
    out_dir = os.path.dirname(src)
    url = "file://" + src
    made = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for v in ("w", "n"):
            for lang in ("zh", "en"):
                # 每一張都開一個乾淨的 page：匯出狀態是「加上去就不拿掉」的單向流程
                # （08-export.js 有 restore()，這裡不需要，重開比還原可靠）
                ctx = browser.new_context(
                    viewport={"width": 2100 if v == "w" else 390, "height": 900},
                    device_scale_factor=2)
                page = ctx.new_page()
                page.goto(url)
                page.wait_for_timeout(400)
                if page.evaluate("() => !!(document.fonts && document.fonts.ready)"):
                    page.evaluate("() => document.fonts.ready")
                name = names(page)[v][lang]
                path = os.path.join(out_dir, name)
                box = shoot(page, v, lang, path)
                made.append((name, box["w"], box["h"], os.path.getsize(path)))
                ctx.close()
        browser.close()
    for name, w, h, size in made:
        print("wrote %s  %d×%d  %.1f MB" % (name, w * 2, h * 2, size / 1e6))


main()
