import os
from playwright.sync_api import sync_playwright
JS = """
() => {
  const L = c => { const [r,g,b]=c; const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b) };
  const parse = s => { const m=s.match(/[\\d.]+/g).map(Number); return m.length>3&&m[3]===0?null:[m[0],m[1],m[2]] };
  const over = (fg,bg,a)=>fg.map((v,i)=>v*a+bg[i]*(1-a));
  function bgOf(el){ let cur=el, stack=[];
    while(cur && cur!==document.documentElement){ const cs=getComputedStyle(cur);
      const m=cs.backgroundColor.match(/[\\d.]+/g).map(Number); const a=m.length>3?m[3]:1;
      if(a>0) stack.push([[m[0],m[1],m[2]],a]); if(a>=1) break; cur=cur.parentElement; }
    let res=[255,255,255]; for(let i=stack.length-1;i>=0;i--) res=over(stack[i][0],res,stack[i][1]); return res; }
  const out=[];
  let skipped = 0;
  document.querySelectorAll('*').forEach(el=>{ if(el.closest('[data-noexport]')) return;
    // 已結束的課刻意淡化，依需求不套 WCAG 對比要求
    if(el.closest('.st-done')){ skipped++; return; }
    if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) return;
    const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden') return;
    const fg=parse(cs.color); if(!fg) return; let bg=bgOf(el);
    // 累乘祖先的 opacity 與 filter:opacity()，把文字實際混向底色
    let a=1, cur=el;
    while(cur && cur!==document.documentElement){
      const c2=getComputedStyle(cur);
      a *= parseFloat(c2.opacity);
      const m=(c2.filter||'').match(/opacity[(]([0-9.]+)[)]/);
      if(m) a *= parseFloat(m[1]);
      cur=cur.parentElement;
    }
    if(a<0.999){ const page=[244,240,233];
      for(let i=0;i<3;i++){ fg[i]=fg[i]*a+page[i]*(1-a); bg[i]=bg[i]*a+page[i]*(1-a); } }
    const l1=L(fg),l2=L(bg); const r=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
    const fs=parseFloat(cs.fontSize), fw=parseInt(cs.fontWeight)||400;
    const need=(fs>=24||(fs>=18.66&&fw>=700))?3:4.5;
    if(r<need) out.push({cls:el.className.toString().slice(0,24),fs,r:+r.toFixed(2),need}); });
  const seen=new Set(), u=[];
  out.forEach(o=>{const k=o.cls+o.fs+o.r; if(!seen.has(k)){seen.add(k);u.push(o)}});
  return {n:out.length, u, skipped};
}
"""
import sys
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

W=int([a for a in sys.argv[1:] if a.isdigit()][0]) if [a for a in sys.argv[1:] if a.isdigit()] else 2100
FAKEINIT = """(() => { const fixed = new Date('2026-09-02T14:20:00+08:00').getTime(); const OD = Date;
 function D(...a){ return a.length ? new OD(...a) : new OD(fixed); }
 D.now = () => fixed; D.parse = OD.parse; D.UTC = OD.UTC; D.prototype = OD.prototype;
 window.Date = D; })();""" if os.environ.get('FAKE_CLOCK') else None
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":W,"height":1520}, timezone_id='Asia/Taipei')
    (ctx.add_init_script(FAKEINIT) if FAKEINIT else None)
    pg=ctx.new_page()
    pg.goto(URL); pg.wait_for_timeout(3500)
    for m in ("zh","en"):
        pg.click("#lang button[data-l=%s]"%m); pg.wait_for_timeout(700)
        r=pg.evaluate(JS); print(m, "WCAG 不合格:", r["n"], "（已結束卡片豁免 %d 個節點）" % r["skipped"])
        for o in r["u"][:10]: print("   ", o)
    b.close()
