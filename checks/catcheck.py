import os
# 驗證：每張卡片的顏色都必須等於其分類的色票值
import csv, re, colorsys, json
from playwright.sync_api import sync_playwright
import sys, glob, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def target():
    for a in sys.argv[1:]:
        if a.endswith('.html'):
            return os.path.abspath(a)
    f = sorted(glob.glob(os.path.join(_ROOT, 'dist', '*.html')))
    if not f:
        sys.exit('找不到 dist/*.html，請先執行 python3 build.py')
    return f[-1]
URL = 'file://' + target()


CAT_FIX = {"豪宇系列": "寰宇系列", "高難度": "肌耐力/核心/快節奏"}
PALETTE = {"伸展":"#4792B8","肌耐力/核心/快節奏":"#B4747C","放鬆":"#47904C","按摩":"#B49F74",
"熱課程":"#A76B44","姿勢正位":"#6C82C0","高難度":"#9A3C87","阿斯坦加":"#9BBD56",
"瑜伽輪":"#7E6FB8","陰瑜伽":"#42A99B","寰宇系列":"#3C3C9A","付費課":"#9A3C87"}
NO_CAT_TAG = {"陰瑜伽", "瑜伽輪"}

def hx(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def mix(a,b,k):
    ra,rb=hx(a),hx(b); return tuple(round(ra[i]+(rb[i]-ra[i])*k) for i in range(3))
def rgb(css):
    return tuple(int(v) for v in re.findall(r'\d+', css)[:3])

rows=list(csv.DictReader(open(os.path.join(_ROOT,'data',sorted(os.listdir(os.path.join(_ROOT,'data')))[-1]),encoding='utf-8-sig')))
want={}
for r in rows:
    c=CAT_FIX.get(r['分類'].strip(), r['分類'].strip())
    want[c]=want.get(c,0)+1

FAKEINIT = """(() => { const fixed = new Date('2026-09-02T14:20:00+08:00').getTime(); const OD = Date;
 function D(...a){ return a.length ? new OD(...a) : new OD(fixed); }
 D.now = () => fixed; D.parse = OD.parse; D.UTC = OD.UTC; D.prototype = OD.prototype;
 window.Date = D; })();""" if os.environ.get('FAKE_CLOCK') else None
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":2100,"height":1520}, timezone_id='Asia/Taipei')
    (ctx.add_init_script(FAKEINIT) if FAKEINIT else None)
    pg=ctx.new_page()
    pg.goto(URL); pg.wait_for_timeout(3500)
    cards=pg.evaluate("""()=>[...document.querySelectorAll('.ev,.dgrp:not(.clone) .lc')].map(e=>{
      const cs=getComputedStyle(e); const cg=e.querySelector('.cg');
      return {cat:e.dataset.cat, base:e.dataset.base, off:e.classList.contains('off'),
              kind:e.classList.contains('lc')?'lc':'ev',
              bar:cs.borderLeftColor, bg:cs.backgroundColor,
              chip:cg?getComputedStyle(cg).backgroundColor:null,
              name:e.querySelector('.n').innerText.trim()};})""")
    b.close()

bad=[]; got={}
for c in cards:
    cat=c['cat']
    if c['kind']=='ev': got[cat]=got.get(cat,0)+1
    exp=PALETTE.get(cat)
    if exp is None: bad.append((c['name'],cat,'分類無色票')); continue
    if c['base'] and c['base'].upper()!=exp.upper(): bad.append((c['name'],cat,'data-base 不符 %s'%c['base']))
    if True:
        if rgb(c['bar'])!=hx(exp): bad.append((c['name'],cat,'左色條 %s ≠ %s'%(c['bar'],exp)))
        if rgb(c['bg'])!=mix(exp,'#ffffff',0.88):
            bad.append((c['name'],cat,'底色 %s'%c['bg']))
        if cat in NO_CAT_TAG:
            if c['chip'] is not None: bad.append((c['name'],cat,'不該有分類標籤'))
        else:
            if c['chip'] is None: bad.append((c['name'],cat,'缺分類標籤'))
            elif rgb(c['chip'])!=mix(exp,'#ffffff',0.72):
                bad.append((c['name'],cat,'標籤底色 %s'%c['chip']))

print("卡片數：寬版 %d / 窄版 %d / CSV %d" % (sum(1 for c in cards if c['kind']=='ev'), sum(1 for c in cards if c['kind']=='lc'), len(rows)))
for k in sorted(set(list(want)+list(got))):
    mark = "" if want.get(k)==got.get(k) else "   ✗"
    print("  %-14s CSV %-3s 卡片 %-3s%s" % (k, want.get(k,0), got.get(k,0), mark))
print("色票不符：%d 筆" % len(bad))
for x in bad[:20]: print("   ", x)
