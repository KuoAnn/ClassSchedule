# -*- coding: utf-8 -*-
import csv, html, re, colorsys, sys

import argparse, os, glob

_p = argparse.ArgumentParser(description="瑜伽課表產生器：讀 CSV，輸出單一 HTML")
_p.add_argument("--csv", help="課程 CSV 路徑（預設抓 data/ 下最新的一份）")
_p.add_argument("--month", type=int, help="月份，預設由檔名推斷")
_p.add_argument("--branch", help="館別，預設由檔名推斷")
_p.add_argument("--out", help="輸出 HTML 路徑，預設 dist/<館別>-<月>月課表.html")
_p.add_argument("--byline", default="Lulu 製作", help="署名（中文）")
_p.add_argument("--byline-en", default="Made by Lulu", help="署名（英文）")
_a = _p.parse_args()

_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = _a.csv or sorted(glob.glob(os.path.join(_ROOT, "data", "*.csv")))[-1]
_stem = os.path.splitext(os.path.basename(SRC))[0]
_m = re.search(r"(\d{1,2})\s*月", _stem)
MONTH = _a.month or (int(_m.group(1)) if _m else 1)
_b = re.match(r"([^\d]+館)", _stem)
BRANCH = _a.branch or (_b.group(1) if _b else "本館")
OUT = _a.out or os.path.join(_ROOT, "dist", "%s-%02d月課表.html" % (BRANCH, MONTH))
os.makedirs(os.path.dirname(OUT), exist_ok=True)

SHEET_W = 2040
GUT = 56
SC = 1.7
GAPH = 20.0
GAPMIN = 15

PALETTE = {
    "伸展": "#4792B8",
    "肌耐力/核心/快節奏": "#B4747C",
    "放鬆": "#47904C",
    "按摩": "#B49F74",
    "熱課程": "#A76B44",
    "姿勢正位": "#6C82C0",
    "高難度": "#9A3C87",
    "阿斯坦加": "#9BBD56",
    "瑜伽輪": "#7E6FB8",
    "陰瑜伽": "#42A99B",
    "寰宇系列": "#3C3C9A",
    "付費課": "#9A3C87",
}
ORDER = ["伸展", "肌耐力/核心/快節奏", "放鬆", "按摩", "熱課程", "姿勢正位",
         "阿斯坦加", "瑜伽輪", "陰瑜伽", "寰宇系列", "付費課"]

BANDS = [(0, 12 * 60, "早"), (12 * 60, 17 * 60, "午"), (17 * 60, 24 * 60, "晚")]
DW = ["一", "二", "三", "四", "五", "六", "日"]
DAYNAME = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]

EN_CAT = {
    "伸展": "Stretch", "肌耐力/核心/快節奏": "Strength / Core / Pace",
    "放鬆": "Relax", "按摩": "Massage", "熱課程": "Hot", "姿勢正位": "Alignment",
    "高難度": "Advanced", "阿斯坦加": "Ashtanga", "瑜伽輪": "Yoga Wheel",
    "陰瑜伽": "Yin", "寰宇系列": "Universal Series", "付費課": "Paid Class",
}
NAME_FIX = {"基礎瑜伽 Fundamental": "基礎瑜伽", "瑜伽提斯 Yoga Tone": "瑜伽提斯",
            "墊上＿皮拉提斯": "墊上皮拉提斯",
            "豪宇入門": "寰宇入門", "豪宇瑜伽": "寰宇瑜伽",
            "慢流輪": "慢流暢"}
# 「瑜伽」二字一律省略，除下列名稱（去掉後語意不成立）
CAT_FIX = {"豪宇系列": "寰宇系列", "高難度": "肌耐力/核心/快節奏"}
CAT_NOTE = {"付費課": ("（另加 <b>$350</b>）", " (<b>extra $350</b>)")}
# 課名本身即等於分類，標籤與色票都省略（顏色仍保留）
NO_CAT_TAG = {"陰瑜伽", "瑜伽輪"}   # 卡片不上分類標籤
NO_LEGEND = set()                             # 全部分類都列入色票
HIGHLIGHT = set()                             # 目前無需加強的分類
CAT_SHORT = {
    "伸展": ("伸展", "Stretch"), "肌耐力/核心/快節奏": ("力", "Core"),
    "放鬆": ("放鬆", "Relax"), "按摩": ("按摩", "Massage"), "熱課程": ("熱", "Hot"),
    "姿勢正位": ("正位", "Align"),     "阿斯坦加": ("阿斯", "Asht."), "瑜伽輪": ("輪", "Wheel"), "陰瑜伽": ("陰", "Yin"),
    "寰宇系列": ("寰宇", "Univ."), "付費課": ("付費", "Paid"),
}
KEEP_YOGA = {"陰瑜伽", "瑜伽輪", "瑜伽提斯"}


def simplify(nm):
    if nm in KEEP_YOGA:
        return nm
    out = nm.replace("瑜伽", "").strip()
    return out or nm


EN_NAME = {
    "壁繩瑜伽": "Rope Wall Yoga", "瑜伽基礎": "Yoga Basics", "流動": "Flow",
    "伸展瑜伽": "Stretch Yoga", "頌缽療癒": "Singing Bowl",
    "瑜伽伸展": "Yoga Stretch", "瑜伽療法": "Yoga Therapy", "哈達瑜伽": "Hatha Yoga",
    "瑜伽輪": "Yoga Wheel", "阿斯坦加瑜伽": "Ashtanga Yoga", "筋膜瑜伽": "Fascia Yoga",
    "瑜伽修復": "Restorative", "和緩瑜伽": "Gentle Yoga", "瑜伽舒眠": "Yoga Nidra",
    "墊上皮拉提斯": "Mat Pilates", "慢流暢": "Slow Flow", "熱和緩": "Hot Gentle",
    "熱流動": "Hot Flow", "溫基礎": "Warm Basics", "陰瑜伽": "Yin Yoga",
    "瑜伽提斯": "Yogilates", "輕流動": "Light Flow", "輔具瑜伽": "Props Yoga",
    "火箭入門": "Rocket Intro", "熱伸展": "Hot Stretch", "椅子瑜伽": "Chair Yoga",
    "水晶缽放鬆": "Crystal Bowl", "陰陽瑜伽": "Yin Yang Yoga",
    "基礎瑜伽": "Fundamental", "阿斯坦加": "Ashtanga",
    "芳療瑜伽": "Aroma Yoga", "放鬆延展": "Relax & Stretch", "哈達基礎": "Hatha Basics",
    "瑜伽提斯 Yoga Tone": "Yoga Tone", "寰宇入門": "Universal Intro",
    "肌筋膜按摩": "Myofascial", "筋膜舒壓伸展": "Fascia Release",
    "尼古瑪瑜伽": "Niguma Yoga", "熱哈達": "Hot Hatha", "火箭瑜伽": "Rocket Yoga",
    "原力核心": "Core Power", "寰宇瑜伽": "Universal Yoga", "溫和緩": "Warm Gentle",
}
ALWAYS_EN = {"JAI", "Roushan"}   # 印籍且英文授課，資料中部分列漏標（EN）
EN_TEACHER = {"丁丁": "Ding-Ding", "柳川": "Liu-Chuan", "錦潭": "Jin-Tan", "吳柏樵": "Wu Po-Chiao"}
EN_MONTH = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]
EN_BRANCH = "Guting Studio"
VIEW_ICON = {
    "w": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
          'stroke-linejoin="round"><rect x="3.2" y="4.2" width="7.2" height="7.2" rx="1.3"/>'
          '<rect x="13.6" y="4.2" width="7.2" height="7.2" rx="1.3"/>'
          '<rect x="3.2" y="12.6" width="7.2" height="7.2" rx="1.3"/>'
          '<rect x="13.6" y="12.6" width="7.2" height="7.2" rx="1.3"/></svg>'),
    "n": ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
          'stroke-linecap="round"><circle cx="4.6" cy="6.4" r="1.15" fill="currentColor" stroke="none"/>'
          '<circle cx="4.6" cy="12" r="1.15" fill="currentColor" stroke="none"/>'
          '<circle cx="4.6" cy="17.6" r="1.15" fill="currentColor" stroke="none"/>'
          '<path d="M9 6.4h11M9 12h11M9 17.6h11"/></svg>'),
}

BYLINE = (_a.byline, _a.byline_en)
EN_DAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ICON = {
    "早": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18.5h16M7.6 18.5a4.4 4.4 0 0 1 8.8 0M12 4v3.2M5.8 7.4l2.1 2.1M18.2 7.4l-2.1 2.1"/></svg>',
    "午": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.1"/><path d="M12 2.8v2.3M12 18.9v2.3M2.8 12h2.3M18.9 12h2.3M5.5 5.5l1.6 1.6M16.9 16.9l1.6 1.6M18.5 5.5l-1.6 1.6M7.1 16.9l-1.6 1.6"/></svg>',
    "晚": '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.2 14.9A8.6 8.6 0 0 1 9.1 3.8a8.6 8.6 0 1 0 11.1 11.1z"/></svg>',
}

EN_BAND = {"早": "AM", "午": "MID", "晚": "PM"}
EN_LV = {"中": "Int", "高": "Adv"}
LV_ZH = {"中": "中等", "高": "進階"}
LV_STYLE = {"中": ("#e6ecdf", "#4c6636"), "高": ("#f6e2d8", "#a04a22")}

warn = []
NAMEMAP = {}
TMAP = {}
CATCOUNT = {}


def bi(zh, en):
    return '<span class="zh">%s</span><span class="en">%s</span>' % (zh, en)


def mn(t):
    h, m = t.strip().split(":")
    return int(h) * 60 + int(m)


rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
S = [[] for _ in DW]
for r in rows:
    d = r["星期"].strip()
    di = DW.index(d) if d in DW else (int(d) - 1 if d.isdigit() else None)
    if di is None:
        warn.append("星期無法辨識：%s" % r); continue
    cat = CAT_FIX.get(r["分類"].strip(), r["分類"].strip())
    if cat not in PALETTE:
        warn.append("分類未定義：%s（%s）" % (cat, r["課程名稱"]))
    kind = r["異動類型"].strip()
    who = r["代課老師"].strip()
    dates = [x for x in re.split("[、,]", r["異動日期"].strip()) if x]
    if kind == "暫停" and who:
        warn.append("異動類型為暫停但填了代課老師：%s %s %s（已依「暫停」處理）"
                    % (d, r["開始時間"], r["課程名稱"]))
        who = ""
    if mn(r["結束時間"]) <= mn(r["開始時間"]):
        warn.append("跨日或時間顛倒：%s %s" % (r["課程名稱"], r["開始時間"]))
        continue
    tn = r["老師"].strip()
    TMAP.setdefault(re.sub(r"（[^）]*）", "", tn).strip(), set()).add(tn)
    raw = NAME_FIX.get(r["課程名稱"].strip(), r["課程名稱"].strip())
    if raw not in EN_NAME:
        warn.append("缺英文課名：%s" % raw)
    en = EN_NAME.get(raw, raw)
    zh = simplify(raw)
    NAMEMAP.setdefault(zh, set()).add(raw)
    S[di].append({
        "s": r["開始時間"].strip(), "e": r["結束時間"].strip(),
        "n": zh, "en": en,
        "t": r["老師"].strip(),
        "c": cat, "lv": r["級別"].strip(), "kind": kind, "who": who, "dates": dates,
    })


def build_axis():
    ivs = sorted([mn(c["s"]), mn(c["e"])] for day in S for c in day)
    mg = []
    for a_, b_ in ivs:
        if mg and a_ <= mg[-1][1]:
            mg[-1][1] = max(mg[-1][1], b_)
        else:
            mg.append([a_, b_])
    segs, cur = [], mg[0][0]
    for a_, b_ in mg:
        if a_ > cur:
            segs.append([cur, a_, "gap"])
        segs.append([a_, b_, "on"])
        cur = b_
    for sg in segs:
        span = sg[1] - sg[0]
        sg.append(GAPH if (sg[2] == "gap" and span >= GAPMIN) else span * SC)
    return mg[0][0], mg[-1][1], segs


T0, T1, SEGS = build_axis()
GH = sum(sg[3] for sg in SEGS)


def ypos(m):
    y = 0.0
    for a_, b_, k, hgt in SEGS:
        if m <= a_:
            return y
        if m <= b_:
            return y + (m - a_) / (b_ - a_) * hgt
        y += hgt
    return y


def cut_at(m):
    for a_, b_, k, hgt in SEGS:
        if k == "gap" and hgt < (b_ - a_) * SC and a_ == m:
            return True
    return False


def squeezed(m):
    for a_, b_, k, hgt in SEGS:
        if k == "gap" and hgt < (b_ - a_) * SC and a_ < m < b_:
            return True
    return False


def in_on(m):
    return any(k == "on" and a_ <= m <= b_ for a_, b_, k, hgt in SEGS)


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, k):
    ra, rb = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(ra[i] + (rb[i] - ra[i]) * k) for i in range(3))


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hx(c)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def fit(fg, bg, ratio=4.6):
    """darken fg until it reaches the target contrast against bg"""
    r, g, b = [v / 255.0 for v in hx(fg)]
    h, l, sa = colorsys.rgb_to_hls(r, g, b)
    for _ in range(220):
        rr, gg, bb = colorsys.hls_to_rgb(h, l, sa)
        c = "#%02x%02x%02x" % (round(rr * 255), round(gg * 255), round(bb * 255))
        if cr(c, bg) >= ratio:
            return c
        if l <= 0:
            return "#000000"
        l = max(l - 0.005, 0)
    return "#000000"


AUDIT = []


def checked(fg, bg, label):
    AUDIT.append((label, fg, bg, cr(fg, bg)))
    return fg


def deepen(c):
    r, g, b = [v / 255 for v in hx(c)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(l * 0.42, 0.16), min(s * 1.1, 0.9))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def lay(items):
    ev = sorted(items, key=lambda x: (mn(x["s"]), mn(x["e"])))
    out, cl, cend = [], [], -1

    def flush(c):
        if not c:
            return
        cols, res = [], []
        for it in c:
            placed = False
            for i, cc in enumerate(cols):
                if mn(cc[-1]["e"]) <= mn(it["s"]):
                    cc.append(it); res.append([it, i]); placed = True; break
            if not placed:
                cols.append([it]); res.append([it, len(cols) - 1])
        for r in res:
            out.append((r[0], r[1], len(cols)))

    for it in ev:
        if cl and mn(it["s"]) < cend:
            cl.append(it); cend = max(cend, mn(it["e"]))
        else:
            flush(cl); cl = [it]; cend = mn(it["e"])
    flush(cl)
    return out


def esc(s):
    return html.escape(s, quote=False)


def teacher_html(name):
    tags = []
    if "印籍" in name:
        tags.append(("印", "IN"))
    if re.search(r"（EN）|\(EN\)", name):
        tags.append(("EN", "EN"))
    base = re.sub(r"（[^）]*）|\([^)]*\)", "", name).strip()
    if base in ALWAYS_EN and not any(t[0] == "EN" for t in tags):
        tags.append(("EN", "EN"))
    out = bi(esc(base), esc(EN_TEACHER.get(base, base)))
    for z, e in tags:
        out += ' <i class="tg">%s</i>' % bi(z, e)
    return out


def note_html(it):
    k, who, ds = it["kind"], it["who"], it["dates"]
    if not k:
        return ""
    whoe = esc(EN_TEACHER.get(who, who))
    who = esc(who)
    dd = "・".join(ds)
    chips = []
    if k == "代課":
        chips.append('<span class="sub">%s</span>'
                     % bi("%s %s 代" % (dd, who), "%s %s Sub" % (dd, whoe)))
    elif k == "暫停":
        chips.append('<span class="stop">%s</span>' % bi("%s 暫停" % dd, "%s Off" % dd))
    else:
        d0 = ds[0] if ds else ""
        rest = "・".join(ds[1:])
        chips.append('<span class="sub">%s</span>'
                     % bi("%s %s 代" % (d0, who), "%s %s Sub" % (d0, whoe)))
        chips.append('<span class="stop">%s</span>' % bi("%s 暫停" % rest, "%s Off" % rest))
    return '<div class="x">%s</div>' % "".join(chips)


def emit_keys():
    present = [c for c in ORDER
               if c not in NO_LEGEND and any(x["c"] == c for day in S for x in day)]
    a('<div class="keys">')
    for c in present:
        sz, se = CAT_SHORT.get(c, (c, c))
        fz, fe = esc(c), esc(EN_CAT.get(c, c))
        nz, ne = CAT_NOTE.get(c, ("", ""))
        if c in NO_CAT_TAG:
            short, tz, te = bi(fz, fe), nz, ne
        else:
            short = bi(esc(sz), esc(se))
            tz = (fz if sz != c else '') + nz
            te = (fe if se != fe else '') + ne
        tail = ('<u>%s</u>' % bi(tz, te)) if (tz or te) else ''
        a('<button class="key" data-cat="%s"><i style="background:%s"></i>%s%s</button>' % (
            esc(c), PALETTE.get(c, "#9a938b"), short, tail))
    a('<button class="clear" id="clear" data-noexport="1">%s</button>' % bi("顯示全部", "Show all"))
    a('</div>')


o = []
a = o.append
a('<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">')
a('<title>%d月課表 %s</title>' % (MONTH, BRANCH))
a('<meta name="viewport" content="width=%d">' % SHEET_W)
a('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
a('<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap" rel="stylesheet">')
a("""<style>
:root{--page:#F4F0E9;--ink:#33302b;--ink2:#635d55;--ink3:#6e675d;
--rule:#e3dcd1;--rule2:#cdc3b4;--lane:#c3b6a1;--band1:#fdfcfa;--band2:#f8f3eb;--band3:#f0e9de;
--gy:__GH__px;--gut:__GUT__px}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--page);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
.wrap{width:__SW__px;margin:0 auto}
html.nv .wrap{width:auto;max-width:none}
html.nv .sheet{padding:16px 14px 20px}
html.nv .wideonly{display:none}
html.wv .narrowonly{display:none}
html.nv .hd h1{font-size:26px}
html.nv .hd h1 em{font-size:14px;margin-left:11px}
html.nv .tools{gap:7px}
html.nv .seg{padding:2px}
html.nv .seg button{padding:6px 11px;font-size:13px}
html.nv #view button{padding:6px 9px}
html.nv #view svg{width:16px;height:16px}
html.nv #dl{width:34px;height:34px}
html.nv #dl svg{width:16px;height:16px}
html.nv .keys{gap:0 16px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;
margin:9px -14px 0 0;padding:1px 14px 3px 0}
html.nv .keys::-webkit-scrollbar{display:none}

.nlist{margin:2px -14px 0 0;display:flex;align-items:flex-start}
.ndock{display:none;position:sticky;top:var(--dockH,92px);z-index:24;
background:var(--page);padding:6px 0 8px;border-bottom:2px solid var(--lane);
align-items:baseline;gap:11px;font-size:27px;font-weight:700;letter-spacing:.14em}
.ndock.show{display:flex}
.ndock span{font-size:13px;font-weight:400;letter-spacing:.04em;color:var(--ink3)}
.ndock .tdy{display:none}
.ndock.istoday .tdy{display:inline-block}
.ngut{flex:0 0 48px;position:relative;z-index:3;background:var(--page)}
.ngc{border-top:1px solid var(--rule);padding-top:5px;font-size:12.5px;color:var(--ink3);
font-variant-numeric:tabular-nums;box-sizing:border-box;overflow:hidden}
.ngc.head{border-top:0}
.ngc b{font-weight:400;display:block}
.ngc .gb{display:flex;align-items:center;gap:3px;color:#786a56;font-size:11.5px;
letter-spacing:.08em;margin-bottom:1px}
.ngc .gb .ic{width:11px;height:11px;flex:0 0 11px;display:block}
.ncar{position:relative;flex:1;min-width:0}
.ncar::before,.ncar::after{content:"";position:absolute;top:0;bottom:0;
pointer-events:none;z-index:2}
.ncar::before{left:0;width:var(--fadeL,0px);background:linear-gradient(to right,var(--page) 14%,rgba(244,240,233,0))}
.ncar::after{right:0;width:var(--fadeR,0px);background:linear-gradient(to left,var(--page) 14%,rgba(244,240,233,0))}
.hrow{border-top:1px solid var(--rule);padding-top:5px;box-sizing:border-box;overflow:hidden}
.ntrack{--dayw:320px;--gap:12px;--peek:26px;
display:flex;align-items:flex-start;gap:var(--gap);
overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;
-webkit-overflow-scrolling:touch;cursor:grab}
.ntrack::-webkit-scrollbar{display:none}
.ntrack.drag{cursor:grabbing;scroll-snap-type:none}
.ntrack.full{padding-left:0;overflow-x:hidden;scroll-snap-type:none;cursor:default;
justify-content:center}
.ntrack.full .dgrp.clone{display:none}
.nlist.full .ncar::before,.nlist.full .ncar::after{display:none}
.sheet.flat .top,.sheet.flat .headrow{position:static}
.sheet.flat .gut{position:relative}
.sheet.flat .ndock{display:none}
.sheet.weekexp{width:max-content}
.sheet.weekexp .nlist,.sheet.weekexp .ncar{width:max-content}
.sheet.weekexp .ntrack{overflow:visible;padding:0!important;justify-content:flex-start;width:max-content}
.sheet.weekexp .dgrp.clone{display:none}
.sheet.weekexp .ncar::before,.sheet.weekexp .ncar::after{display:none}
.sheet.weekexp .keys{overflow:visible;flex-wrap:wrap;margin-right:0}
.sheet.noto .dn.today:not(.we){background:transparent}
.sheet.noto .dn.today.we{background:#ece5d9}
.sheet.noto .col.today{background:transparent}
.sheet.noto .tdy{display:none}
.sheet.noto .dgrp.today .dhd{border-bottom-color:var(--lane)}
.nav{position:fixed;top:50%;transform:translate(-50%,-50%);z-index:28;
width:38px;height:38px;border-radius:50%;border:1px solid var(--rule2);
background:rgba(255,255,255,.92);color:var(--ink2);cursor:pointer;
display:flex;align-items:center;justify-content:center;padding:0}
.nav svg{width:19px;height:19px;display:block}
.nav:hover{background:#fff;color:var(--ink)}
html.wv .nav{display:none}
.dgrp{flex:0 0 var(--dayw);scroll-snap-align:center;margin-bottom:2px}
.dhd{display:flex;align-items:baseline;gap:11px;font-size:27px;font-weight:700;
letter-spacing:.14em;padding:2px 2px 8px;border-bottom:2px solid var(--lane);
background:var(--page)}
.dhd span{font-size:13px;font-weight:400;letter-spacing:.04em;color:var(--ink3)}
.lc{border:1px solid;border-left-width:3px;border-radius:8px;padding:9px 11px;margin-bottom:5px}
.lc .nr{display:flex;align-items:flex-start;gap:8px}
.lc .n{flex:1;min-width:0;font-size:16px;font-weight:500;line-height:1.25}
.lc .lv{flex:0 0 auto;font-style:normal;font-weight:500;font-size:11px;line-height:1.3;
border-radius:4px;padding:1px 6px;letter-spacing:.04em;white-space:nowrap}
.lc .t{font-size:13.5px;color:var(--ink2);line-height:1.4;font-variant-numeric:tabular-nums;margin-top:1px}
.lc .t .du{font-style:normal;margin-left:2px;font-size:.86em;color:var(--ink3)}
.lc .m{font-size:13.5px;color:var(--ink3);line-height:1.4}
.lc .m .tg{font-style:normal;font-size:10.5px;background:#efeae2;color:#635d55;
border-radius:3px;padding:0 4px;margin-left:2px;vertical-align:1px}
.lc .bt{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin-top:6px}
.lc .x{display:flex;flex-wrap:wrap;gap:4px}
.lc .x>span{display:inline-block;font-weight:500;font-size:11.5px;line-height:1.4;
border-radius:4px;padding:1px 6px;letter-spacing:.02em}
.lc .x>.sub{color:#33506b;background:#dde6ee}
.lc .x>.stop{color:#8f3b24;background:#f4ddd9}
.lc .cg{margin-left:auto;font-weight:500;font-size:11px;line-height:1.4;
border-radius:4px;padding:1px 6px;letter-spacing:.04em;white-space:nowrap}
.sheet{background:var(--page);padding:0 20px 16px;position:relative}
.sheet .en{display:none}
.sheet.en .zh{display:none}
.sheet.en .en{display:inline}
.hd{padding-bottom:12px}
.hd h1{font-size:34px;font-weight:500;letter-spacing:.06em;line-height:1.1}
.hd .by{font-size:13px;color:var(--ink3);letter-spacing:.14em;margin-top:7px}
.hd h1 em{font-style:normal;font-size:17px;font-weight:400;color:var(--ink3);letter-spacing:.12em;margin-left:18px}

.top{position:sticky;top:0;z-index:30;background:var(--page);padding:20px 0 11px}
.trow{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}
.tools{display:flex;gap:10px;align-items:center;flex:0 0 auto}
html.wv .tools{position:fixed;top:14px;right:16px;z-index:32}

.tools button{font:400 14px/1 inherit;color:var(--ink2);background:#fff;border:1px solid var(--rule2);
padding:11px 20px;cursor:pointer;letter-spacing:.06em;border-radius:22px}
#dl{padding:0;width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center}
#dl svg{width:19px;height:19px;display:block}
#dl .i-sp{display:none}
#dl.busy .i-dl{display:none}
#dl.busy .i-sp{display:block;animation:sp .8s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.tools button:hover{background:#faf7f1;color:var(--ink)}
.tools button:disabled{opacity:.5;cursor:default}
.seg{display:flex;background:#fff;border:1px solid var(--rule2);border-radius:22px;padding:3px}
.seg button{border:0;background:transparent;padding:8px 16px;border-radius:18px;font-size:14px;color:var(--ink2);letter-spacing:.04em}
.seg button.on{background:#ece5d9;color:var(--ink);font-weight:500}
#view button{padding:7px 13px;display:flex;align-items:center;justify-content:center}
#view svg{width:18px;height:18px;display:block}

.headrow{display:flex;margin-left:var(--gut);border-radius:10px 10px 0 0;overflow:hidden;
position:sticky;top:var(--dockH,92px);z-index:25;background:var(--page)}
.dn{flex:1;text-align:center;font-size:18px;font-weight:500;letter-spacing:.16em;padding:12px 0;border-right:2px solid var(--lane);border-bottom:1px solid var(--rule2)}
.dn:last-child{border-right:0}
.dn.we{background:#ece5d9}
.tdy{display:none;font-size:11px;font-weight:400;letter-spacing:.08em;color:#7f643a;
background:#efeae2;border-radius:4px;padding:1px 6px;margin-left:9px;vertical-align:2px}
.today .tdy{display:inline-block}
.dn.today{background:#e8e0cf}
.col.today{background:rgba(196,156,64,.075)}
.dgrp.today .dhd{border-bottom-color:#a89670}

.body{display:flex}
.gut{width:var(--gut);position:sticky;left:0;height:var(--gy);z-index:20;
background:var(--page);flex:0 0 var(--gut)}
.gut .hr{position:absolute;right:12px;font-size:14px;color:var(--ink3);transform:translateY(-50%);font-variant-numeric:tabular-nums;white-space:nowrap}
.gut .bl{position:absolute;right:12px;transform:translateY(-50%);display:flex;align-items:center;
gap:3px;white-space:nowrap;color:#786a56}
.gut .bl b{font-weight:500;font-size:14px;letter-spacing:.08em}
.gut .bl .ic{width:12px;height:12px;flex:0 0 12px;display:block}
.gut .hr.end{color:#786a56}

.cal{flex:1;position:relative;height:var(--gy);border-radius:0 0 10px 10px;overflow:hidden}
.lay{position:absolute;inset:0;overflow:hidden;border-radius:0 0 12px 12px}
.bg{position:absolute;left:0;right:0}
.hl{position:absolute;left:0;right:0;border-top:1px solid var(--rule)}
.hl.s{border-top-color:var(--rule2)}
.hl.h{border-top:1px dashed var(--rule);opacity:.7}
.cut{position:absolute;left:0;right:0;background:repeating-linear-gradient(135deg,#e7e0d4 0 2px,#f1ebe1 2px 7px);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);opacity:.85}
.we-wash{position:absolute;top:0;bottom:0;background:#dfd2bc;opacity:.2}
.cols{position:absolute;inset:0;display:flex}
.col{flex:1;position:relative;border-right:2px solid var(--lane)}
.col:last-child{border-right:0}

.ev{position:absolute;padding:6px 10px;border:1px solid;border-left-width:3px;overflow:hidden;
border-radius:7px;display:flex;flex-direction:column;gap:4px}
.ev>*{flex:0 0 auto;min-width:0}
.ev .tp{min-width:0}
.ev .nr{display:flex;align-items:flex-start;gap:6px;min-width:0}
.ev .n{flex:1;min-width:0;font-size:16px;font-weight:500;line-height:1.2;letter-spacing:.01em;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.ev .t{font-size:13.5px;color:var(--ink2);line-height:1.26;font-variant-numeric:tabular-nums}
.ev .t .hh{white-space:nowrap}
.ev .t .du{font-style:normal;margin-left:1px;font-size:.86em;color:var(--ink3);white-space:nowrap}
.ev .m{font-size:13.5px;color:var(--ink3);line-height:1.26;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ev .m .tg{font-style:normal;font-size:10.5px;background:#efeae2;border-radius:3px;
padding:1px 4px;margin-left:4px;vertical-align:1px;letter-spacing:.02em;color:#635d55}
.ev .lv{flex:0 0 auto;font-style:normal;font-size:10.5px;font-weight:500;color:#7f643a;
background:#efeae2;border-radius:4px;padding:0 5px;letter-spacing:.04em;
line-height:1.25;white-space:nowrap}
.ev .bt{margin-top:auto;display:flex;flex-wrap:wrap;align-items:baseline;gap:1px 8px}
.ev .x{display:flex;flex-wrap:wrap;gap:2px 4px;max-width:100%}
.ev .x>span{display:inline-block;font-weight:500;font-size:11px;line-height:1.4;
border-radius:4px;padding:1px 5px;letter-spacing:.02em;white-space:nowrap}
.ev .x>.sub{color:#33506b;background:#dde6ee}
.ev .x>.stop{color:#8f3b24;background:#f4ddd9}
.ev .cg{margin-left:auto;font-size:10.5px;font-weight:500;line-height:1.4;letter-spacing:.04em;
white-space:nowrap;border-radius:4px;padding:1px 5px}
.ev.nar{padding:5px 7px;gap:3px}
.ev.nar .n{font-size:14px;line-height:1.16;overflow-wrap:break-word}
.ev.nar .lv{font-size:10px;padding:0 4px;line-height:1.2}
.ev.nar .t{font-size:11.5px}
.ev.nar .m{font-size:11.5px;white-space:normal;line-height:1.24;text-overflow:clip;overflow-wrap:break-word}
.ev.nar .x>span{font-size:10px;padding:1px 4px;white-space:normal}
.ev.nar .cg{font-size:10px;padding:1px 5px}
.ev.nar .m .tg{font-size:10px;padding:0 4px;margin-left:1px}
.ev.f1{gap:2px;padding-top:4px;padding-bottom:4px}
.ev.f1 .n{font-size:11.6px;line-height:1.1}
.ev.f1 .t,.ev.f1 .m{font-size:10px;line-height:1.14}
.ev.f1 .lv,.ev.f2 .lv{font-size:9.5px;line-height:1.15}
.ev.f1 .x>span{font-size:9.5px}
.ev.f2{gap:1px;padding:3px 7px}
.ev.f2 .n{font-size:10.8px;line-height:1.08}
.ev.f2 .t,.ev.f2 .m{font-size:9.5px;line-height:1.1}
.ev.f2 .x>span,.ev.f2 .cg{font-size:9px;padding:0 4px}
.ev.f3{gap:0;padding:2px 6px}
.ev.f3 .n{font-size:10px;line-height:1.05}
.ev.f3 .t,.ev.f3 .m{font-size:9px;line-height:1.08}
.ev.f3 .x>span,.ev.f3 .cg{font-size:8.5px;padding:0 3px}
.ev.f3 .lv,.ev.f3 .m .tg{display:none}
.ev.f4{gap:0;padding:2px 5px}
.ev.f4 .n{font-size:9.5px;line-height:1.04}
.ev.f4 .t,.ev.f4 .m{font-size:8.5px;line-height:1.06}
.ev.f4 .x>span{font-size:8px;padding:0 3px}
.ev.f4 .lv,.ev.f4 .cg,.ev.f4 .m .tg,.ev.f4 .du{display:none}
.ev.f1{gap:1px;padding-top:4px;padding-bottom:4px}
.ev.f1 .n{font-size:11.6px;line-height:1.1}
.ev.f1 .t,.ev.f1 .m{font-size:10px;line-height:1.14}
.ev.f1 .x>span{font-size:9.5px}
.ev.f2{gap:0;padding:3px 7px}
.ev.f2 .n{font-size:10.8px;line-height:1.08}
.ev.f2 .t,.ev.f2 .m{font-size:9.5px;line-height:1.1}
.ev.f2 .x{font-size:9px;line-height:1.1}
.ev.f3{gap:0;padding:2px 6px}
.ev.f3 .n{font-size:10px;line-height:1.05}
.ev.f3 .t,.ev.f3 .m{font-size:9px;line-height:1.08}
.ev.f3 .x{font-size:8.5px;line-height:1.08}
.ev.f3 .lv,.ev.f3 .m .tg{display:none}
.ev.f4{gap:0;padding:2px 5px}
.ev.f4 .n{font-size:9.5px;line-height:1.04}
.ev.f4 .t,.ev.f4 .m{font-size:8.5px;line-height:1.06}
.ev.f4 .x>span{font-size:8px;padding:0 3px}
.ev.f4 .lv,.ev.f4 .cg,.ev.f4 .m .tg,.ev.f4 .du{display:none}

.keys{margin-top:11px}
.keys{display:flex;flex-wrap:wrap;gap:9px 22px;align-items:center}
.keys.on .key:not(.sel){opacity:.4}
.key{border:0;background:transparent;font-family:inherit;cursor:pointer;
padding:3px 6px;margin:-3px -2px;border-radius:7px;
display:flex;align-items:center;gap:7px;font-size:14px;color:var(--ink2);white-space:nowrap}
.key:hover{background:rgba(0,0,0,.05)}
.key.sel{background:rgba(0,0,0,.08)}
.key i{width:14px;height:14px;flex:0 0 14px;display:block;border-radius:4px}
.clear{display:none;border:1px solid var(--rule2);background:#fff;font-family:inherit;
font-size:13px;color:var(--ink2);padding:5px 14px;border-radius:16px;cursor:pointer;
letter-spacing:.06em;margin-left:4px}
.clear:hover{background:#faf7f1}
.keys.on .clear{display:inline-block}
.ev.past,.lc.past{filter:opacity(.42)}
.sheet.nopast .past{filter:none}
.sheet.on .ev,.sheet.on .lc{opacity:.14}
.sheet.on .ev.match,.sheet.on .lc.match{opacity:1}
.key u{text-decoration:none;color:var(--ink3);font-size:13px;margin-left:5px}
.key u b{font-weight:500;color:var(--ink)}

@media print{@page{size:A2 landscape;margin:8mm}body{background:#fff}.wrap{width:100%;margin:0}.sheet{padding:0;border-radius:0}.tools{display:none}}
</style></head><body>
<script>(function(){var v;try{v=localStorage.getItem('yoga-view')}catch(e){}
if(v!=='n'&&v!=='w')v=(window.innerWidth||1200)<900?'n':'w';
document.documentElement.className=(v==='n'?'nv':'wv')})();</script>
<div class="wrap"><div class="sheet" id="sheet">"""
  .replace("__GH__", "%.0f" % GH).replace("__GUT__", str(GUT)).replace("__SW__", str(SHEET_W)))

a('<div class="top"><div class="trow">')
a('<div class="hd"><h1>%s<em>%s</em></h1><div class="by">%s</div></div>' % (
    bi("%d月課表" % MONTH, "%s Schedule" % EN_MONTH[MONTH - 1]),
    bi(BRANCH, EN_BRANCH), bi(esc(BYLINE[0]), esc(BYLINE[1]))))
a('<div class="tools" data-noexport="1">'
  '<div class="seg" id="view">'
  '<button data-v="w" aria-label="Grid view" title="寬版">' + VIEW_ICON["w"] + '</button>'
  '<button data-v="n" aria-label="List view" title="窄版">' + VIEW_ICON["n"] + '</button></div>'
  '<div class="seg" id="lang"><button data-l="zh" class="on">中</button>'
  '<button data-l="en">EN</button></div>'
  '<button id="dl" aria-label="Download image">'
  '<svg class="i-dl" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
  'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5v11M7.4 10l4.6 4.6 4.6-4.6M4.5 20h15"/></svg>'
  '<svg class="i-sp" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  'stroke-linecap="round"><path d="M12 3.2a8.8 8.8 0 1 0 8.8 8.8"/></svg>'
  '</button>'
  '</div>')
a('</div>')
emit_keys()
a('</div>')

a('<div class="wideonly">')
a('<div class="headrow">')
for i, d in enumerate(DAYNAME):
    a('<div class="dn%s" data-day="%d">%s<span class="tdy">%s</span></div>'
      % (" we" if i >= 5 else "", i, bi(d, EN_DAY[i]), bi("今天", "Today")))
a('</div>')

a('<div class="body"><div class="gut">')
BSTART = {}
for bs, be, lb in BANDS:
    k = max(bs, T0) if bs <= T0 < be else bs
    if T0 <= k <= T1:
        BSTART[k if k % 60 == 0 else (k // 60) * 60] = lb
t = (T0 // 60) * 60
while t <= T1:
    if T0 <= t and not squeezed(t) and not cut_at(t):
        lb = BSTART.get(t)
        if lb:
            a('<div class="bl" style="top:%.1fpx">%s<b>%s</b></div>'
              % (ypos(t) - 19, ICON[lb], bi(lb, EN_BAND[lb])))
        a('<div class="hr" style="top:%.1fpx">%02d:00</div>' % (ypos(t), t // 60))
    t += 60
if T1 % 60:
    a('<div class="hr end" style="top:%.1fpx">%02d:%02d</div>' % (GH, T1 // 60, T1 % 60))
a('</div>')

a('<div class="cal"><div class="lay">')
for idx, (bs, be, lb) in enumerate(BANDS):
    y1, y2 = ypos(max(bs, T0)), ypos(min(be, T1))
    if y2 > y1:
        a('<div class="bg" style="top:%.1fpx;height:%.1fpx;background:var(--band%d)"></div>' % (y1, y2 - y1, idx + 1))
for a_, b_, k, hgt in SEGS:
    if k == "gap" and hgt < (b_ - a_) * SC:
        a('<div class="cut" style="top:%.1fpx;height:%.1fpx"></div>' % (ypos(a_), hgt))
for i in (5, 6):
    a('<div class="we-wash" style="left:%.4f%%;width:%.4f%%"></div>' % (i * 100 / 7.0, 100 / 7.0))
t = (T0 // 60) * 60
while t <= T1:
    if T0 <= t and not squeezed(t) and not cut_at(t):
        cls = "hl s" if t in (12 * 60, 17 * 60) else "hl"
        a('<div class="%s" style="top:%.1fpx"></div>' % (cls, ypos(t)))
    if t + 30 <= T1 and in_on(t + 30):
        a('<div class="hl h" style="top:%.1fpx"></div>' % ypos(t + 30))
    t += 60
a('</div><div class="cols">')

def card_parts(it):
    """回傳卡片內容（寬版與窄版共用）"""
    if it["c"] not in PALETTE:
        raise SystemExit("分類沒有對應色票：%s（%s）" % (it["c"], it["n"]))
    base = PALETTE[it["c"]]
    hi = it["c"] in HIGHLIGHT
    cardbg = mix(base, "#ffffff", 0.74 if hi else 0.88)
    edge = mix(base, "#ffffff", 0.6)
    name = '<div class="n" style="color:%s">%s</div>' % (
        checked(fit(deepen(base), cardbg), cardbg, "課名 " + it["c"]),
        bi(esc(it["n"]), esc(it["en"])))
    dur = mn(it["e"]) - mn(it["s"])
    # 起訖皆為整點時兩端都省略分鐘：11:00–12:00 → 11–12
    if mn(it["s"]) % 60 == 0 and mn(it["e"]) % 60 == 0:
        span = "%s–%s" % (it["s"][:2], it["e"][:2])
    else:
        span = "%s–%s" % (it["s"], it["e"])
    time = ('<div class="t"><span class="hh">%s</span>%s</div>'
            % (span, '' if dur == 60 else ' <i class="du">(%d)</i>' % dur))
    if it["lv"] in EN_LV:
        lvbg, lvfg = LV_STYLE[it["lv"]]
        lv = ('<i class="lv" style="background:%s;color:%s">%s</i>'
              % (lvbg, checked(fit(lvfg, lvbg), lvbg, "難度標籤 " + LV_ZH[it["lv"]]),
                 bi(LV_ZH[it["lv"]], EN_LV[it["lv"]])))
    else:
        lv = ""
    who = '<div class="m">%s</div>' % teacher_html(it["t"])
    note = note_html(it)
    cz, ce = CAT_SHORT.get(it["c"], (it["c"], it["c"]))
    chipbg = mix(base, "#ffffff", 0.52 if hi else 0.72)
    if it["c"] in NO_CAT_TAG:
        cg = ''
    else:
        cg = ('<span class="cg" style="color:%s;background:%s">%s</span>'
              % (checked(fit(mix(base, "#241F1A", 0.34), chipbg), chipbg, "分類標籤 " + cz),
                 chipbg, bi(esc(cz), esc(ce))))
    return dict(base=base, hi=hi, cardbg=cardbg, edge=edge, name=name, time=time,
                lv=lv, who=who, note=note, cg=cg)


for day in S:
    a('<div class="col" data-day="%d">' % S.index(day))
    for it, ci, n in lay(day):
        p = card_parts(it)
        CATCOUNT[it["c"]] = CATCOUNT.get(it["c"], 0) + 1
        top = ypos(mn(it["s"])) + 2
        hh = ypos(mn(it["e"])) - ypos(mn(it["s"])) - 4
        cls = ("ev" + (" nar" if n > 1 else "")
               + (" hi" if p["hi"] else "") + (" lvd" if it["lv"] in EN_LV else ""))
        a('<div class="%s" data-cat="%s" data-base="%s" data-start="%d" style="top:%.1fpx;height:%.1fpx;left:calc(%.4f%% + 3px);width:calc(%.4f%% - 6px);background:%s;border-color:%s;border-left-color:%s">'
          % (cls, esc(it["c"]), p["base"], mn(it["s"]), top, hh, ci * 100.0 / n, 100.0 / n,
             p["cardbg"], p["edge"], p["base"]))
        a('<div class="tp"><div class="nr">%s%s</div>%s%s</div>'
          % (p["name"], p["lv"], p["time"], p["who"]))
        a('<div class="bt">%s%s</div>' % (p["note"], p["cg"]))
        a('</div>')
    a('</div>')
a('</div></div></div>')
a('</div>')

# ---------- 窄版：以小時列跨日對齊，空班留白 ----------
HOURS = sorted({mn(x["s"]) // 60 for day in S for x in day})
BAND_AT = {}
for bs, be, blb in BANDS:
    for h in HOURS:
        if bs <= h * 60 < be:
            BAND_AT.setdefault(blb, h)
BAND_OF = {h: lb for lb, h in BAND_AT.items()}

a('<div class="ndock narrowonly" id="ndock" data-noexport="1"></div>')
a('<div class="nlist narrowonly">')
a('<div class="ngut" id="ngut"><div class="ngc head"></div>')
for h in HOURS:
    lb = BAND_OF.get(h)
    a('<div class="ngc" data-h="%d">%s<b>%02d:00</b></div>'
      % (h,
         ('<span class="gb">%s%s</span>' % (ICON[lb], bi(lb, EN_BAND[lb]))) if lb else '',
         h))
a('</div>')
a('<div class="ncar"><div class="ntrack" id="ntrack">')
for di, day in enumerate(S):
    a('<section class="dgrp" data-day="%d"><h3 class="dhd">%s'
      '<span class="tdy">%s</span></h3>'
      % (di, bi(DAYNAME[di], EN_DAY[di]), bi("今天", "Today")))
    for h in HOURS:
        g = sorted([x for x in day if mn(x["s"]) // 60 == h], key=lambda x: mn(x["s"]))
        a('<div class="hrow%s" data-h="%d">' % ("" if g else " empty", h))
        for it in g:
            p = card_parts(it)
            a('<article class="lc%s" data-cat="%s" data-start="%d" style="background:%s;border-color:%s;border-left-color:%s">'
              % (" hi" if p["hi"] else "", esc(it["c"]), mn(it["s"]),
                 p["cardbg"], p["edge"], p["base"]))
            a('<div class="nr">%s%s</div>%s%s' % (p["name"], p["lv"], p["time"], p["who"]))
            a('<div class="bt">%s%s</div>' % (p["note"], p["cg"]))
            a('</article>')
        a('</div>')
    a('</section>')
a('</div>')
a('<button class="nav p" id="navp" data-noexport="1" aria-label="Previous day">'
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  'stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 5.5 8 12l6.5 6.5"/></svg></button>')
a('<button class="nav n" id="navn" data-noexport="1" aria-label="Next day">'
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  'stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg></button>')
a('</div></div>')
a('</div></div>')

a('</div></div>')
a('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>')
a("""<script>
function fitCells(){
  var els = document.querySelectorAll('.ev'), steps = ['f1','f2','f3','f4'];
  for (var i = 0; i < els.length; i++){
    var el = els[i];
    el.classList.remove('f1','f2','f3','f4');
    for (var j = 0; j < steps.length; j++){
      if (el.scrollHeight <= el.clientHeight) break;
      if (j) el.classList.remove(steps[j-1]);
      el.classList.add(steps[j]);
    }
  }
}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fitCells);
(function(){
  var td = (new Date().getDay() + 6) % 7;
  document.querySelectorAll('[data-day="' + td + '"]').forEach(function(el){
    el.classList.add('today');
  });
})();
function markPast(){
  var d = new Date(), td = (d.getDay() + 6) % 7, now = d.getHours() * 60 + d.getMinutes();
  document.querySelectorAll('.ev,.lc').forEach(function(el){
    var host = el.closest('[data-day]');
    el.classList.toggle('past',
      !!host && +host.dataset.day === td && +el.dataset.start < now);
  });
}
markPast();
setInterval(markPast, 60000);
var track = document.getElementById('ntrack'), cur = 0;
var navp = document.getElementById('navp'), navn = document.getElementById('navn');
var NDAYS = track.children.length, vpos = NDAYS;
// 前後各複製一整組，捲進複製區後靜默歸位 → 循環沒有跳點
(function(){
  var real = Array.prototype.slice.call(track.children);
  for (var i = real.length - 1; i >= 0; i--) {
    var c = real[i].cloneNode(true);
    c.classList.add('clone');
    track.insertBefore(c, track.firstChild);
  }
  real.forEach(function(el){
    var c = el.cloneNode(true);
    c.classList.add('clone');
    track.appendChild(c);
  });
  markPast();
})();
function px(name, fb){
  var v = parseFloat(getComputedStyle(track).getPropertyValue(name));
  return isNaN(v) ? fb : v;
}
function panelStep(){
  var a = track.children[0], b = track.children[1];
  return b ? b.offsetLeft - a.offsetLeft : px('--dayw', 320) + px('--gap', 12);
}
function layout(){
  if (!document.documentElement.classList.contains('nv')) return;
  var nl = document.querySelector('.nlist'), car = document.querySelector('.ncar');
  var dayw = px('--dayw', 320), gap = px('--gap', 12);
  var W = track.clientWidth, step = dayw + gap, n = NDAYS;
  // 七天全部放得下 → 關閉輪播互動
  var full = (n * dayw + (n - 1) * gap) <= W;
  track.classList.toggle('full', full);
  nl.classList.toggle('full', full);
  navp.style.display = navn.style.display = full ? 'none' : '';
  if (full) {
    track.style.paddingLeft = track.style.paddingRight = '0px';
    track.scrollLeft = 0;
    car.style.setProperty('--fadeL', '0px');
    car.style.setProperty('--fadeR', '0px');
    return;
  }
  // 當天置中：左右各留 (可視寬 − 單日寬)/2，兩端的日子也能捲到正中
  var side = (W - dayw) / 2;
  track.style.paddingLeft = track.style.paddingRight = side + 'px';
  // 單側能完整顯示的鄰日數，以及最外側被切一半那天的可見寬度
  var m = Math.floor(side / step);
  var sliver = Math.max(0, side - m * step - gap);
  var f = sliver > 3 ? Math.min(Math.max(sliver, 18), 130) : 0;
  car.style.setProperty('--fadeL', f + 'px');
  car.style.setProperty('--fadeR', f + 'px');
  var r = car.getBoundingClientRect();
  navp.style.left = '23px';
  navn.style.left = (window.innerWidth - 23) + 'px';
}
window.addEventListener('resize', function(){ measureDock(); syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
// 各日的同一小時列取最大高度，讓七天橫向對齊；空班自然留白
var ndock = document.getElementById('ndock');
function measureDock(){
  var t = document.querySelector('.top');
  document.documentElement.style.setProperty('--dockH',
    Math.round(t.getBoundingClientRect().height) + 'px');
}
function updateDock(){
  if (!document.documentElement.classList.contains('nv')) return;
  var panel = track.children[vpos];
  if (!panel) return;
  var hd = panel.querySelector('.dhd');
  if (hd && ndock.dataset.k !== String(vpos)) {
    ndock.innerHTML = hd.innerHTML;
    ndock.dataset.k = String(vpos);
  }
  ndock.classList.toggle('istoday', panel.classList.contains('today'));
  var dockH = parseFloat(getComputedStyle(document.documentElement)
    .getPropertyValue('--dockH')) || 92;
  var top = document.querySelector('.nlist').getBoundingClientRect().top;
  ndock.classList.toggle('show', top < dockH - 2 && !track.classList.contains('full'));
}
var dockRaf = 0;
window.addEventListener('scroll', function(){
  if (dockRaf) return;
  dockRaf = requestAnimationFrame(function(){ dockRaf = 0; updateDock(); });
}, {passive: true});
function syncRows(){
  if (!document.documentElement.classList.contains('nv')) return;
  var gut = document.getElementById('ngut');
  var head = gut.querySelector('.ngc.head');
  var hs = [], hd = 0;
  var heads = track.querySelectorAll('.dgrp > .dhd');
  Array.prototype.forEach.call(heads, function(el){
    el.style.height = 'auto';
    hd = Math.max(hd, el.getBoundingClientRect().height);
  });
  Array.prototype.forEach.call(heads, function(el){ el.style.height = hd + 'px'; });
  Array.prototype.forEach.call(gut.querySelectorAll('.ngc[data-h]'), function(g){
    hs.push(g.dataset.h);
  });
  head.style.height = hd + 'px';
  hs.forEach(function(h){
    var rows = track.querySelectorAll('.hrow[data-h="' + h + '"]');
    var g = gut.querySelector('.ngc[data-h="' + h + '"]');
    var mx = 0;
    Array.prototype.forEach.call(rows, function(r){ r.style.height = 'auto'; });
    g.style.height = 'auto';
    Array.prototype.forEach.call(rows, function(r){
      mx = Math.max(mx, r.scrollHeight);
    });
    mx = Math.max(mx, g.scrollHeight);
    Array.prototype.forEach.call(rows, function(r){ r.style.height = mx + 'px'; });
    g.style.height = mx + 'px';
  });
}
function markCur(){
  Array.prototype.forEach.call(track.children, function(c, k){
    c.classList.toggle('cur', k === vpos);
  });
}
function goDay(v, smooth){
  if (track.classList.contains('full')) { vpos = NDAYS; cur = 0; return; }
  vpos = v;
  cur = ((v - NDAYS) % NDAYS + NDAYS) % NDAYS;
  markCur();
  updateDock();
  track.scrollTo({left: v * panelStep(), behavior: smooth ? 'smooth' : 'auto'});
}
// 停在複製區時，把捲動位置搬回中央那一組（畫面完全相同，看不出來）
function normalize(){
  if (vpos < NDAYS || vpos >= NDAYS * 2) {
    vpos = cur + NDAYS;
    track.scrollLeft = vpos * panelStep();
    markCur();
  }
}
navp.addEventListener('click', function(){ goDay(vpos - 1, true); });
navn.addEventListener('click', function(){ goDay(vpos + 1, true); });
var st;
track.addEventListener('scroll', function(){
  clearTimeout(st);
  st = setTimeout(function(){
    if (track.classList.contains('full')) return;
    vpos = Math.round(track.scrollLeft / panelStep());
    cur = ((vpos - NDAYS) % NDAYS + NDAYS) % NDAYS;
    markCur();
    normalize();
    updateDock();
  }, 140);
});
(function(){
  var down = false, x0 = 0, s0 = 0, moved = 0;
  track.addEventListener('pointerdown', function(e){
    if (e.pointerType === 'touch' || track.classList.contains('full')) return;
    down = true; moved = 0; x0 = e.clientX; s0 = track.scrollLeft;
    track.classList.add('drag');
  });
  track.addEventListener('pointermove', function(e){
    if (!down) return;
    var d = e.clientX - x0;
    if (Math.abs(d) > 3) moved = 1;
    track.scrollLeft = s0 - d;
  });
  function end(){
    if (!down) return;
    down = false; track.classList.remove('drag');
    goDay(Math.round(track.scrollLeft / panelStep()), true);
  }
  track.addEventListener('pointerup', end);
  track.addEventListener('pointercancel', end);
  track.addEventListener('pointerleave', end);
  track.addEventListener('click', function(e){ if (moved) e.preventDefault(); }, true);
})();
// 首次進入定位到今天（週一=0 … 週日=6）
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
  .then(function(){ measureDock(); syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
measureDock();
syncRows();
layout();
goDay(((new Date().getDay() + 6) % 7) + NDAYS, false);
updateDock();

var vseg = document.getElementById('view');
function setView(v){
  document.documentElement.className = (v === 'n' ? 'nv' : 'wv');
  Array.prototype.forEach.call(vseg.children, function(x){
    x.classList.toggle('on', x.dataset.v === v);
  });
  try { localStorage.setItem('yoga-view', v); } catch(e) {}
  fitCells();
  measureDock();
  if (v === 'n') requestAnimationFrame(function(){ syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
  else ndock.classList.remove('show');
}
vseg.addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  setView(b.dataset.v);
});
setView(document.documentElement.classList.contains('nv') ? 'n' : 'w');

// 分類篩選：單選，再點同一個即取消
var picked = null;
function applyFilter(){
  var sheet = document.getElementById('sheet'), keys = document.querySelector('.keys');
  var on = picked !== null;
  sheet.classList.toggle('on', on);
  keys.classList.toggle('on', on);
  document.querySelectorAll('.key').forEach(function(k){
    k.classList.toggle('sel', k.dataset.cat === picked);
    k.setAttribute('aria-pressed', k.dataset.cat === picked ? 'true' : 'false');
  });
  document.querySelectorAll('.ev,.lc').forEach(function(ev){
    ev.classList.toggle('match', ev.dataset.cat === picked);
  });
}
document.querySelector('.keys').addEventListener('click', function(e){
  var k = e.target.closest('.key'); if(!k) return;
  picked = (picked === k.dataset.cat) ? null : k.dataset.cat;
  applyFilter();
});
document.getElementById('clear').addEventListener('click', function(){
  picked = null; applyFilter();
});
document.getElementById('lang').addEventListener('click', function(e){
  var b = e.target.closest('button'); if(!b) return;
  var sheet = document.getElementById('sheet');
  sheet.classList.toggle('en', b.dataset.l === 'en');
  Array.prototype.forEach.call(this.children, function(x){
    x.classList.toggle('on', x.dataset.l === b.dataset.l);
  });
  fitCells();
  syncRows();
});
</script>""")
a("""<script>
document.getElementById('dl').addEventListener('click', function(){
  var btn=this, sheet=document.getElementById('sheet');
  btn.disabled=true; btn.classList.add('busy');
  var hide=sheet.querySelectorAll('[data-noexport]');
  (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){
    fitCells();
    var nar = document.documentElement.classList.contains('nv');
    sheet.classList.add('nopast','flat','noto');
    if (nar && !track.classList.contains('full')) sheet.classList.add('weekexp');
    hide.forEach(function(el){el.style.visibility='hidden'});
    return html2canvas(sheet,{scale:2,backgroundColor:'#F4F0E9',useCORS:true,
      width:sheet.offsetWidth,height:sheet.offsetHeight,windowWidth:sheet.offsetWidth});
  }).then(function(canvas){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    var a=document.createElement('a');
    var en = sheet.classList.contains('en');
    var nv = document.documentElement.classList.contains('nv');
    a.download = (en ? '__FNE__' : '__FN__')
      .replace('.png', (nv ? (en ? '-vertical' : '-直式') : '') + '.png');
    a.href=canvas.toDataURL('image/png'); a.click();
    btn.disabled=false; btn.classList.remove('busy');
  }).catch(function(e){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    btn.disabled=false; btn.classList.remove('busy'); alert('Export failed: '+e);
  });
});
</script>""".replace("__FN__", "%s-%d月課表.png" % (BRANCH, MONTH)).replace("__FNE__", "%s-%s-schedule.png" % (EN_BRANCH.replace(" ", "-"), EN_MONTH[MONTH - 1])))
a('</body></html>')

open(OUT, "w", encoding="utf-8").write("\n".join(o))
print("wrote", OUT, "grid", int(GH), "classes", sum(len(d) for d in S))
for k, v in sorted(TMAP.items()):
    if len(v) > 1:
        warn.append("老師標註不一致：%s ← %s" % (k, "／".join(sorted(v))))
for k, v in sorted(NAMEMAP.items()):
    if len(v) > 1:
        warn.append("簡化後同名：%s ← %s" % (k, "／".join(sorted(v))))
seen = {}
for label, fg, bg, ratio in AUDIT:
    seen[label] = min(seen.get(label, 99), ratio)
bad = sorted((r, l) for l, r in seen.items() if r < 4.5)
print("分類色票：" + "、".join("%s %d 堂" % (k, CATCOUNT[k]) for k in ORDER if k in CATCOUNT))
print("對比度稽核：%d 組色彩，最低 %.2f:1" % (len(seen), min(seen.values())))
for r, l in bad:
    warn.append("對比度不足 %.2f:1 — %s" % (r, l))
for w in warn:
    print("WARN:", w)
