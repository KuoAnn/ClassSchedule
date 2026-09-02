# -*- coding: utf-8 -*-
import csv, html, re, colorsys, sys, json, hashlib

import argparse, os, glob
from urllib.parse import quote

_p = argparse.ArgumentParser(description="瑜伽課表產生器：讀 CSV，輸出單一 HTML")
_p.add_argument("--csv", help="課程 CSV 路徑（預設抓 data/ 下最新的一份）")
_p.add_argument("--month", type=int, help="月份，預設由檔名推斷")
_p.add_argument("--branch", help="館別，預設由檔名推斷")
_p.add_argument("--out", help="輸出 HTML 路徑，預設 dist/<館別>-<月>月課表.html")
_p.add_argument("--byline", default="Lulu 製作", help="署名（中文）")
_p.add_argument("--byline-en", default="Made by Lulu", help="署名（英文）")
# 課表版本：預設由 data/versions.json 自己跑（見下方 resolve_version），這裡只留手動覆寫
_p.add_argument("--version", help="課表版本，例如 1.2；預設依 CSV 內容自動編號")
# LIFF ID：本站是純靜態課表、不讀會員資料，沒填也照樣能看，只是不初始化 LINE SDK
_p.add_argument("--liff-id", default=os.environ.get("LIFF_ID", ""),
                help="LINE LIFF ID（預設讀環境變數 LIFF_ID）")
_a = _p.parse_args()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
SRC = _a.csv or sorted(glob.glob(os.path.join(_ROOT, "data", "*.csv")))[-1]
_stem = os.path.splitext(os.path.basename(SRC))[0]
_m = re.search(r"(\d{1,2})\s*月", _stem)
MONTH = _a.month or (int(_m.group(1)) if _m else 1)
_b = re.match(r"([^\d]+館)", _stem)
BRANCH = _a.branch or (_b.group(1) if _b else "本館")
_y = re.search(r"(\d{2,4})\s*年", _stem)
YEAR = _y.group(1) if _y else ""
OUT = _a.out or os.path.join(_ROOT, "dist", "%s-%02d月課表.html" % (BRANCH, MONTH))
os.makedirs(os.path.dirname(OUT), exist_ok=True)


def asset(*parts):
    """讀一份 src/ 下的範本資源檔"""
    with open(os.path.join(_SRC, *parts), encoding="utf-8") as f:
        return f.read()


def bundle(sub, skip=()):
    """把 src/<sub>/ 依檔名順序（01-、02-…）串成一份，打包時內嵌進單一 HTML"""
    names = [n for n in sorted(os.listdir(os.path.join(_SRC, sub))) if n not in skip]
    return "\n".join(asset(sub, n).rstrip("\n") for n in names)


def icon(name):
    """src/icons/<name>.svg → 內嵌 SVG"""
    return asset("icons", name + ".svg").strip()


def data_icon(name):
    """src/icons/<name>.svg → data URI；favicon 沒有外部檔可指，只能內嵌進單一 HTML"""
    raw = re.sub(r"<!--.*?-->", "", asset("icons", name + ".svg"), flags=re.S)
    return "data:image/svg+xml," + quote(re.sub(r"\s+", " ", raw).strip(), safe="/:;=,()'")


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
VIEW_ICON = {"w": icon("view-grid"), "n": icon("view-list")}

BYLINE = (_a.byline, _a.byline_en)

# ---------- 課表版本：同一個月改一次 CSV 就往上跑一號 ----------
# 版本代表「這份課表改到第幾版」，不是站台版本，所以只看 CSV 內容 —— 改版面、
# 改樣式重新產檔都不該讓版本跳號。編號記在 data/versions.json：一個月一筆，
# 值是這個月依序出現過的 CSV 指紋，指紋的序號就是小版號（第一版 = 1.0）。
# 這樣即使 CI 端沒有寫入權限，只要 json 有跟著 commit，算出來的版本就一致。
_VERFILE = os.path.join(_ROOT, "data", "versions.json")


def _csv_digest(path):
    """CSV 內容指紋：換行形式與尾端空白不算改版，避免編輯器存檔就跳號"""
    with open(path, encoding="utf-8-sig") as f:
        rows = [ln.rstrip() for ln in f.read().replace("\r\n", "\n").split("\n")]
    while rows and not rows[-1]:
        rows.pop()
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def resolve_version():
    """回傳 (版本字串, 要不要顯示)；當月第一版是 1.0，不顯示，1.1 起才印出來"""
    if _a.version:
        v = _a.version.strip().lstrip("vV")
        return v, v != "1.0"
    key = "%s-%s%02d" % (BRANCH, YEAR + "-" if YEAR else "", MONTH)
    try:
        with open(_VERFILE, encoding="utf-8") as f:
            book = json.load(f)
    except (OSError, ValueError):
        book = {}
    seen = book.get(key) or []
    dg = _csv_digest(SRC)
    if dg not in seen:
        seen.append(dg)
        book[key] = seen
        try:
            with open(_VERFILE, "w", encoding="utf-8", newline="\n") as f:
                json.dump(book, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write("\n")
        except OSError:
            pass  # 唯讀環境（CI）寫不進去也沒關係，版本仍算得出來
    n = seen.index(dg)
    return "1.%d" % n, n > 0


VERSION, SHOW_VERSION = resolve_version()
EN_DAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ICON = {"早": icon("band-am"), "午": icon("band-mid"), "晚": icon("band-pm")}

EN_BAND = {"早": "AM", "午": "MID", "晚": "PM"}
EN_LV = {"中": "Int", "高": "Adv"}
LV_ZH = {"中": "中等", "高": "進階"}
LV_STYLE = {"中": ("#e6ecdf", "#4c6636"), "高": ("#f6e2d8", "#a04a22")}

warn = []
NAMEMAP = {}
TMAP = {}
CATCOUNT = {}


def bi(zh, en):
    return ('<span class="zh" lang="zh-Hant">%s</span>'
            '<span class="en" lang="en">%s</span>' % (zh, en))


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
        "n": zh, "en": en, "di": di,
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
    a('<div class="keys" role="group" aria-label="%s">'
      % ("課程分類篩選 / Filter by category"))
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

a('<div class="top"><div class="trow">')
a('<div class="hd"><h1>%s<em>%s</em></h1><div class="by">%s%s</div></div>' % (
    bi("%d月課表" % MONTH, "%s Schedule" % EN_MONTH[MONTH - 1]),
    bi(BRANCH, EN_BRANCH), bi(esc(BYLINE[0]), esc(BYLINE[1])),
    ('<span class="ver">v%s</span>' % esc(VERSION)) if SHOW_VERSION else ''))
a('<div class="tools" data-noexport="1">'
  '<div class="seg" id="view" role="group" aria-label="版型 / Layout">'
  '<button data-v="w" aria-pressed="true" aria-label="寬版格線 / Grid view" title="寬版">' + VIEW_ICON["w"] + '</button>'
  '<button data-v="n" aria-pressed="false" aria-label="窄版清單 / List view" title="窄版">' + VIEW_ICON["n"] + '</button></div>'
  '<div class="seg" id="lang" role="group" aria-label="語言 / Language">'
  '<button data-l="zh" class="on" aria-pressed="true" lang="zh-Hant" '
  'aria-label="中文">中</button>'
  '<button data-l="en" aria-pressed="false" lang="en" aria-label="English">EN</button></div>'
  '<button id="dl" aria-label="Download image">' + icon("download") + icon("spinner")
  + '</button>'
  '</div>')
a('</div>')
emit_keys()
a('</div>')
a('<div class="topspacer" aria-hidden="true"></div>')

a('<div class="wideonly">')
a('<div class="headrow"><div class="hcorner" aria-hidden="true"></div>')
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
    LVFULL = {"初": ("初級", "Beginner"), "中": ("中等", "Intermediate"),
              "高": ("進階", "Advanced")}
    lvz, lve = LVFULL.get(it["lv"], (it["lv"], it["lv"]))
    tbase = re.sub(r"（[^）]*）|\([^)]*\)", "", it["t"]).strip()
    tz = tbase
    te = EN_TEACHER.get(tbase, tbase)
    if "印籍" in it["t"]:
        tz += "（印籍）"
        te += " (Indian)"
    if re.search(r"（EN）|\(EN\)", it["t"]) or tbase in ALWAYS_EN:
        tz += "，英文授課"
        te += ", taught in English"
    nz = ne = ""
    if it["kind"] == "代課":
        nz = "，%s 由 %s 代課" % ("・".join(it["dates"]), it["who"])
        ne = ", substitute %s on %s" % (it["who"], "・".join(it["dates"]))
    elif it["kind"] == "暫停":
        nz = "，%s 暫停" % "・".join(it["dates"])
        ne = ", cancelled on %s" % "・".join(it["dates"])
    elif it["kind"]:
        d0 = it["dates"][0] if it["dates"] else ""
        rest = "・".join(it["dates"][1:])
        nz = "，%s 由 %s 代課，%s 暫停" % (d0, it["who"], rest)
        ne = ", substitute %s on %s, cancelled on %s" % (it["who"], d0, rest)
    dz = DAYNAME[it["di"]]
    de_ = EN_DAY[it["di"]]
    labz = "%s %s，%s 至 %s，%s，%s，%s%s" % (
        dz, it["n"], it["s"], it["e"], tz, it["c"], lvz, nz)
    labe = "%s %s, %s to %s, %s, %s, %s%s" % (
        de_, it["en"], it["s"], it["e"], te, EN_CAT.get(it["c"], it["c"]), lve, ne)
    return dict(base=base, hi=hi, cardbg=cardbg, edge=edge, name=name, time=time,
                lv=lv, who=who, note=note, cg=cg,
                labz=esc(labz.replace('"', '')), labe=esc(labe.replace('"', '')))


for day in S:
    a('<div class="col" data-day="%d">' % S.index(day))
    for it, ci, n in lay(day):
        p = card_parts(it)
        CATCOUNT[it["c"]] = CATCOUNT.get(it["c"], 0) + 1
        top = ypos(mn(it["s"])) + 2
        hh = ypos(mn(it["e"])) - ypos(mn(it["s"])) - 4
        cls = ("ev" + (" nar" if n > 1 else "")
               + (" hi" if p["hi"] else "") + (" lvd" if it["lv"] in EN_LV else ""))
        a('<div class="%s" role="group" aria-label="%s" data-lab-en="%s" data-cat="%s" data-base="%s" data-start="%d" data-end="%d" style="top:%.1fpx;height:%.1fpx;left:calc(%.4f%% + 3px);width:calc(%.4f%% - 6px);background:%s;border-color:%s;border-left-color:%s">'
          % (cls, p["labz"], p["labe"], esc(it["c"]), p["base"], mn(it["s"]), mn(it["e"]),
             top, hh, ci * 100.0 / n, 100.0 / n,
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

a('<div class="ndock narrowonly" id="ndock" data-noexport="1" aria-hidden="true">'
  '<div class="ndockin" id="ndockin"></div></div>')
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
    a('<section class="dgrp" data-day="%d"><h3 class="dhd">'
      '<span class="dday">%s<i class="tdy">%s</i></span></h3>'
      % (di, bi(DAYNAME[di], EN_DAY[di]), bi("今天", "Today")))
    for h in HOURS:
        g = sorted([x for x in day if mn(x["s"]) // 60 == h], key=lambda x: mn(x["s"]))
        a('<div class="hrow%s" data-h="%d">' % ("" if g else " empty", h))
        for it in g:
            p = card_parts(it)
            a('<article class="lc%s" aria-label="%s" data-lab-en="%s" data-cat="%s" data-start="%d" data-end="%d" style="background:%s;border-color:%s;border-left-color:%s">'
              % (" hi" if p["hi"] else "", p["labz"], p["labe"], esc(it["c"]), mn(it["s"]), mn(it["e"]),
                 p["cardbg"], p["edge"], p["base"]))
            a('<div class="nr">%s%s</div>%s%s' % (p["name"], p["lv"], p["time"], p["who"]))
            a('<div class="bt">%s%s</div>' % (p["note"], p["cg"]))
            a('</article>')
        a('</div>')
    a('</section>')
a('</div>')
a('<button class="nav p" id="navp" data-noexport="1" aria-label="Previous day">%s</button>'
  % icon("nav-prev"))
a('<button class="nav n" id="navn" data-noexport="1" aria-label="Next day">%s</button>'
  % icon("nav-next"))
a('</div></div>')
a('</div></div>')

# ---------- 打包：把 src/ 的資源檔內嵌成單一 HTML ----------
STYLES = "\n".join([
    bundle("styles"),
    "",
    "/* 由 build.py 依這份課表算出的尺寸，覆寫 01-tokens.css 的預設值 */",
    ":root{--gy:%.0fpx;--gut:%dpx;--sheetw:%dpx}" % (GH, GUT, SHEET_W),
])
SCRIPTS = "\n".join([
    "// 由 build.py 依這份課表產生（08-export.js 讀 window.SCHEDULE，09-liff.js 讀 window.LIFF_ID）",
    'window.SCHEDULE = {png: {zh: "%s", en: "%s"}};' % (
        "%s-%d月課表.png" % (BRANCH, MONTH),
        "%s-%s-schedule.png" % (EN_BRANCH.replace(" ", "-"), EN_MONTH[MONTH - 1])),
    'window.LIFF_ID = "%s";' % _a.liff_id.replace('"', ""),
    bundle("js", skip=("01-boot.js",)),
])
FILL = {
    "favicon": data_icon("favicon"),
    "title": "%d月課表 %s" % (MONTH, BRANCH),
    "og_desc": html.escape("%s %d月課表，共 %d 堂課；可切換寬版格線與單日清單。"
                           % (BRANCH, MONTH, sum(len(d) for d in S))),
    "styles": STYLES,
    "boot": asset("js", "01-boot.js").rstrip("\n"),
    "content": "\n".join(o),
    "scripts": SCRIPTS,
}
PAGE = re.sub(r"\{\{(\w+)\}\}", lambda m: FILL[m.group(1)], asset("index.html"))

open(OUT, "w", encoding="utf-8").write(PAGE)
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
