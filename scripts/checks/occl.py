import os
from playwright.sync_api import sync_playwright
import sys, glob, os
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def target():
    for a in sys.argv[1:]:
        if a.endswith('.html'):
            return os.path.abspath(a)
    f = sorted(glob.glob(os.path.join(_ROOT, 'dist', '*.html')))
    if not f:
        sys.exit('找不到 dist/*.html，請先執行 python3 build.py')
    return f[-1]
URL = 'file://' + target()

JS = """
() => {
  const sel = '.n,.t,.m,.x,.cg,.lv';
  const bad = [];
  document.querySelectorAll('.ev').forEach(ev => {
    const cs = getComputedStyle(ev);
    const er = ev.getBoundingClientRect();
    const pad = {t:parseFloat(cs.paddingTop), b:parseFloat(cs.paddingBottom),
                 l:parseFloat(cs.paddingLeft), r:parseFloat(cs.paddingRight)};
    const bw = {t:parseFloat(cs.borderTopWidth), b:parseFloat(cs.borderBottomWidth),
                l:parseFloat(cs.borderLeftWidth), r:parseFloat(cs.borderRightWidth)};
    const box = {x1:er.left+bw.l+pad.l-0.6, y1:er.top+bw.t+pad.t-0.6,
                 x2:er.right-bw.r-pad.r+0.6, y2:er.bottom-bw.b-pad.b+0.6};
    const name = ev.querySelector('.n') ? ev.querySelector('.n').innerText.trim() : '?';
    const els = [...ev.querySelectorAll(sel)].filter(e=>{
      const c=getComputedStyle(e);
      return c.display!=='none' && c.visibility!=='hidden' && e.innerText.trim();
    });
    // 1) 超出卡片內容區
    els.forEach(e=>{
      const r=e.getBoundingClientRect();
      if(r.width===0||r.height===0) return;
      if(r.left<box.x1-1||r.right>box.x2+1||r.top<box.y1-1||r.bottom>box.y2+1)
        bad.push({card:name, el:e.className||e.tagName, why:'出界',
                  d:[Math.round(box.x1-r.left),Math.round(r.right-box.x2),
                     Math.round(box.y1-r.top),Math.round(r.bottom-box.y2)]});
    });
    // 2) 兩兩重疊（排除祖孫關係）
    for(let i=0;i<els.length;i++) for(let j=i+1;j<els.length;j++){
      const A=els[i],B=els[j];
      if(A.contains(B)||B.contains(A)) continue;
      const a=A.getBoundingClientRect(), b=B.getBoundingClientRect();
      const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left);
      const oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
      if(ox>2 && oy>2) bad.push({card:name, el:(A.className||'?')+' × '+(B.className||'?'),
                                 why:'重疊', d:[Math.round(ox),Math.round(oy)]});
    }
    // 3) 元素本身被裁切
    els.forEach(e=>{
      if(e.scrollWidth>e.clientWidth+2 && getComputedStyle(e).textOverflow!=='ellipsis')
        bad.push({card:name, el:e.className, why:'橫向裁切', d:[e.scrollWidth-e.clientWidth]});
      if(e.scrollHeight>e.clientHeight+2 && !/(^| )n( |$)/.test(e.className))
        bad.push({card:name, el:e.className, why:'縱向裁切', d:[e.scrollHeight-e.clientHeight]});
    });
    if(ev.scrollHeight>ev.clientHeight+1)
      bad.push({card:name, el:'ev', why:'卡片溢出', d:[ev.scrollHeight-ev.clientHeight]});
  });
  return bad;
}
"""
FAKEINIT = """(() => { const fixed = new Date('2026-09-02T14:20:00+08:00').getTime(); const OD = Date;
 function D(...a){ return a.length ? new OD(...a) : new OD(fixed); }
 D.now = () => fixed; D.parse = OD.parse; D.UTC = OD.UTC; D.prototype = OD.prototype;
 window.Date = D; })();""" if os.environ.get('FAKE_CLOCK') else None
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":2100,"height":1520}, timezone_id='Asia/Taipei')
    (ctx.add_init_script(FAKEINIT) if FAKEINIT else None)
    pg=ctx.new_page()
    pg.goto(URL); pg.wait_for_timeout(3500)
    total=0
    for m in ("zh","en"):
        pg.click("#lang button[data-l=%s]"%m); pg.wait_for_timeout(700)
        r=pg.evaluate(JS)
        total+=len(r)
        print(m, "問題數:", len(r))
        seen=set()
        for o in r:
            k=(o['el'],o['why'])
            if k in seen: continue
            seen.add(k); print("   ", o)
    b.close()
# 通過標準是 0；非 0 就讓 CI／run.sh 停下來
sys.exit(1 if total else 0)
