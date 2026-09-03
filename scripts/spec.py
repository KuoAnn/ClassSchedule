# -*- coding: utf-8 -*-
"""匯入格式的規格表：欄位、分類、師資標註、級別。

`build.py`（產檔）與 `checks/catcheck.py`（驗色）都讀這一份，
免得分類色票在兩邊各寫一份、加一個新分類時漏改一邊。

**加新東西只要改這個檔**，而且沒改到也不會壞：
沒定義過的分類會自動配一個色（`auto_color`），沒定義過的分類／國籍／語系／級別
標籤一律取前兩個字（`short_tag`），全名仍留在 aria-label 與色票列上。
兩種情形都會由 `build.py` 印出 WARN，提醒把正式的譯名與色票補進來 ——
讓課表先出得去，不是讓它悄悄出錯。
"""
import colorsys
import hashlib

# CSV 欄位；缺欄位 build.py 會直接停（跟 index.html 的 {{…}} 一樣不靜默略過），
# 多出來的欄位只會被忽略並提醒一聲
COLUMNS = ["星期", "開始時間", "結束時間", "課程名稱",
           "師資名稱", "師資國籍", "教學語系", "分類", "級別",
           "異動類型", "異動老師", "異動日期"]

# 異動：一列可以有多筆，欄位內以半形分號分隔，三個欄位「同一個位置」配成一組
CHANGE_SEP = ";；"
DATE_SEP = "、,，"
KIND_SUB = "代課"      # 要有異動老師
KIND_OFF = "暫停"      # 不取用異動老師
KINDS = (KIND_SUB, KIND_OFF)

# ---------- 分類 ----------
# 一個分類一行：color 色票、en 英文全名、short 卡片與色票列上的簡稱、
# tag=False 代表課名本身就等於分類（卡片不再上標籤，顏色仍保留）、
# note 是色票列上補充的小字（zh, en）。dict 的順序就是色票列的順序。
CAT_FIX = {"高難度": "肌耐力/核心/快節奏"}
CATS = {
    "伸展": dict(color="#4792B8", en="Stretch", short=("伸展", "Stretch")),
    "肌耐力/核心/快節奏": dict(color="#B4747C", en="Strength / Core / Pace",
                              short=("力", "Core")),
    "放鬆": dict(color="#47904C", en="Relax", short=("放鬆", "Relax")),
    "按摩": dict(color="#B49F74", en="Massage", short=("按摩", "Massage")),
    "熱課程": dict(color="#A76B44", en="Hot", short=("熱", "Hot")),
    "姿勢正位": dict(color="#6C82C0", en="Alignment", short=("正位", "Align")),
    "阿斯坦加": dict(color="#9BBD56", en="Ashtanga", short=("阿斯", "Asht.")),
    "瑜伽輪": dict(color="#7E6FB8", en="Yoga Wheel", short=("輪", "Wheel"), tag=False),
    "陰瑜伽": dict(color="#42A99B", en="Yin", short=("陰", "Yin"), tag=False),
    "寰宇系列": dict(color="#3C3C9A", en="Universal Series", short=("寰宇", "Univ.")),
    "付費課": dict(color="#9A3C87", en="Paid Class", short=("付費", "Paid"),
                   note=("（另加 <b>$350</b>）", " (<b>extra $350</b>)")),
}


def short_tag(v):
    """判斷不出來時的標籤文字：只取前兩個字。

    標籤的空間很小（窄版卡片只有 142px、寬版並排時更窄），未定義的值整串印
    會把卡片撐爆或被裁掉。前兩個字足以辨識是哪一個，完整的名稱仍然留在
    aria-label 與色票列的說明裡，資訊不會消失。
    """
    return (v[:2], v[:2])


def auto_color(name):
    """沒定義過的分類：由名字算出一個固定的色相。

    色相是雜湊出來的（同一個分類名永遠同一色），明度與彩度釘在既有色票的
    水位（L .50 / S .44），所以卡片底色（混白 88%）與文字對比都落在跟現有
    分類一樣的範圍 —— `fit()` 仍會把文字壓到 4.6:1 以上才輸出。
    """
    h = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16) % 360
    r, g, b = colorsys.hls_to_rgb(h / 360.0, 0.50, 0.44)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def cat_name(raw):
    """正規化分類名（修錯字、把已併入的分類導到現用的那一個）"""
    raw = raw.strip()
    return CAT_FIX.get(raw, raw)


def cat(raw):
    """回傳分類的顯示規格；沒定義過的自動補齊，known 為 False 讓上層提醒"""
    name = cat_name(raw)
    d = CATS.get(name)
    if d:
        out = dict(d)
        out.setdefault("tag", True)
        out.setdefault("note", ("", ""))
        out["name"] = name
        out["known"] = True
        return out
    return dict(name=name, color=auto_color(name), en=name, short=short_tag(name),
                tag=True, note=("", ""), known=False)


def color(raw):
    """分類色票（catcheck 驗卡片顏色用的同一個來源）"""
    return cat(raw)["color"]


# ---------- 師資：名稱／國籍／語系拆成三欄 ----------
# 國籍只會有一個字（印＝印度、美＝美國）；tag 是卡片上的小標，
# full 是 aria-label 念出來的全稱。沒定義過的字照抄，不會擋掉產檔。
NATIONS = {
    "印": dict(tag=("印", "IN"), full=("印籍", "Indian")),
    "美": dict(tag=("美", "US"), full=("美籍", "American")),
    "英": dict(tag=("英", "UK"), full=("英籍", "British")),
    "日": dict(tag=("日", "JP"), full=("日籍", "Japanese")),
    "韓": dict(tag=("韓", "KR"), full=("韓籍", "Korean")),
    "泰": dict(tag=("泰", "TH"), full=("泰籍", "Thai")),
    "法": dict(tag=("法", "FR"), full=("法籍", "French")),
    "德": dict(tag=("德", "DE"), full=("德籍", "German")),
    "澳": dict(tag=("澳", "AU"), full=("澳籍", "Australian")),
    "加": dict(tag=("加", "CA"), full=("加籍", "Canadian")),
}
# 教學語系：未設定＝以中文授課，不顯示
LANGS = {
    "EN": dict(tag=("EN", "EN"), full=("英文授課", "taught in English")),
    "JP": dict(tag=("JP", "JP"), full=("日文授課", "taught in Japanese")),
}


def nation(v):
    v = v.strip()
    if not v:
        return None
    d = NATIONS.get(v)
    if d:
        return dict(d, value=v, known=True)
    return dict(value=v, tag=short_tag(v), full=(v + "籍", v), known=False)


def language(v):
    v = v.strip()
    if not v:
        return None
    d = LANGS.get(v)
    if d:
        return dict(d, value=v, known=True)
    return dict(value=v, tag=short_tag(v), full=(v + "授課", "taught in " + v),
                known=False)


# ---------- 級別 ----------
# tag=None 代表「這是預設級別」：aria-label 仍念得出來，但卡片不上標籤 ——
# 跟「一小時的課只印起始時間」同一條理由，預設值印出來只是雜訊。
# 未設定（空字串）則連 aria-label 都不提。
LEVEL_STYLE = ("#ece7e0", "#5f574d")   # 沒定義過的級別用的中性底色
LEVELS = {
    "初": dict(full=("初級", "Beginner"), tag=None),
    "中": dict(full=("中等", "Intermediate"), tag=("中等", "Int"),
               style=("#e6ecdf", "#4c6636")),
    "高": dict(full=("進階", "Advanced"), tag=("進階", "Adv"),
               style=("#f6e2d8", "#a04a22")),
}


def level(v):
    v = v.strip()
    if not v:
        return None
    d = LEVELS.get(v)
    if d:
        out = dict(d, value=v, known=True)
        out.setdefault("style", LEVEL_STYLE)
        return out
    return dict(value=v, full=(v, v), tag=short_tag(v), style=LEVEL_STYLE, known=False)


# ---------- 課名 ----------
NAME_FIX = {"基礎瑜伽 Fundamental": "基礎瑜伽", "瑜伽提斯 Yoga Tone": "瑜伽提斯",
            "墊上＿皮拉提斯": "墊上皮拉提斯",
            "慢流輪": "慢流暢"}
# 「瑜伽」二字一律省略，除下列名稱（去掉後語意不成立）
KEEP_YOGA = {"陰瑜伽", "瑜伽輪", "瑜伽提斯"}
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
    "阿斯串聯": "Ashtanga Vinyasa",
}
EN_TEACHER = {"丁丁": "Ding-Ding", "柳川": "Liu-Chuan", "紳漳": "Shen-Chang",
              "吳柏樵": "Wu Po-Chiao"}


def simplify(nm):
    if nm in KEEP_YOGA:
        return nm
    out = nm.replace("瑜伽", "").strip()
    return out or nm
