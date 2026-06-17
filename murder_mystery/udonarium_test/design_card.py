# -*- coding: utf-8 -*-
"""
カードデザイン試作（A案：PIL作り込み）。
テーマ＝機密研究ファイルの「物的証拠タグ」。本体 build_udon.py とは独立。
確定したら make_card_front を差し替える。
"""
import os, tempfile, random, math
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    "mincho_b": ("C:/Windows/Fonts/yumindb.ttf", 0),   # 游明朝 Demibold
    "mincho":   ("C:/Windows/Fonts/yumin.ttf", 0),     # 游明朝
    "biz_min":  ("C:/Windows/Fonts/BIZ-UDMinchoM.ttc", 0),
    "goth_m":   ("C:/Windows/Fonts/YuGothM.ttc", 0),   # 游ゴシック Medium
    "goth_b":   ("C:/Windows/Fonts/YuGothB.ttc", 0),
    "biz_goth": ("C:/Windows/Fonts/BIZ-UDGothicB.ttc", 0),
    "ms_goth":  ("C:/Windows/Fonts/msgothic.ttc", 0),   # 等幅
}


def F(key, sz):
    path, idx = FONTS[key]
    return ImageFont.truetype(path, sz, index=idx)


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def paper_noise(img, amount=5, seed=7):
    px = img.load()
    w, h = img.size
    rnd = random.Random(seed)
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-amount, amount)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)),
                        max(0, min(255, g + n)),
                        max(0, min(255, b + n)))
    return img


def corner(d, x, y, sx, sy, color, ln=46, w=3):
    d.line([(x, y), (x + sx * ln, y)], fill=color, width=w)
    d.line([(x, y), (x, y + sy * ln)], fill=color, width=w)


def wrap_draw(d, xy, text, fnt, fill, max_chars, line_h):
    x, y = xy
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if len(line) >= max_chars:
                d.text((x, y), line, font=fnt, fill=fill)
                y += line_h
                line = ""
            line += ch
        d.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def stamp(text, rgba, fsize, angle=-14):
    f = F("mincho_b", fsize)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    bb = tmp.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 22
    W, H = tw + pad * 2, th + pad * 2
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rectangle([5, 5, W - 5, H - 5], outline=rgba, width=6)
    sd.rectangle([13, 13, W - 13, H - 13], outline=rgba, width=2)
    sd.text((pad - bb[0], pad - bb[1]), text, font=f, fill=rgba)
    return s.rotate(angle, expand=True, resample=Image.BICUBIC)


def make_evidence_card(no, title, body, header="物的証拠", prefix="C"):
    W, H = 600, 840
    ink = (46, 41, 36)
    accent = (150, 36, 38)
    sub = (120, 110, 98)

    img = vgrad((W, H), (234, 230, 220), (206, 200, 187))
    img = paper_noise(img, 5)
    d = ImageDraw.Draw(img)

    # 外二重罫
    d.rectangle([18, 18, W - 18, H - 18], outline=ink, width=4)
    d.rectangle([28, 28, W - 28, H - 28], outline=ink, width=1)
    # コーナー飾り（赤）
    for x, y, sx, sy in [(40, 40, 1, 1), (W - 40, 40, -1, 1),
                         (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)]:
        corner(d, x, y, sx, sy, accent)

    # ヘッダ帯
    d.rectangle([28, 28, W - 28, 120], fill=ink)
    d.text((48, 52), header, font=F("mincho_b", 42), fill=(236, 232, 224))
    no_s = "No. %s-%02d" % (prefix, no)
    f_no = F("goth_m", 26)
    nw = d.textlength(no_s, font=f_no)
    d.text((W - 48 - nw, 64), no_s, font=f_no, fill=(214, 156, 156))

    # 品名
    d.text((52, 158), title, font=F("mincho_b", 46), fill=ink)
    # 区切り罫＋菱形
    yy = 236
    d.line([(52, yy), (W - 52, yy)], fill=sub, width=2)
    cx = W // 2
    d.polygon([(cx, yy - 9), (cx + 11, yy), (cx, yy + 9), (cx - 11, yy)], fill=accent)

    # 本文
    wrap_draw(d, (56, 282), body, F("goth_m", 27), (56, 51, 46), 17, 48)

    # 機密スタンプ（半透明・傾き）
    st = stamp("機密", (168, 42, 42, 150), 58)
    img = img.convert("RGBA")
    img.alpha_composite(st, (W - st.width - 54, H - st.height - 78))

    # フッタ
    d = ImageDraw.Draw(img)
    foot = "地下研究施設 ── 調査記録"
    f_ft = F("goth_m", 20)
    fw = d.textlength(foot, font=f_ft)
    d.text(((W - fw) / 2, H - 58), foot, font=f_ft, fill=(112, 102, 92))

    return img.convert("RGB")


def _back_base(top, bottom, ink, accent, noise=5):
    """裏面共通の下地＝縦グラデ＋紙ノイズ＋外二重罫＋四隅L字。(img, d) を返す。"""
    W, H = 600, 840
    img = vgrad((W, H), top, bottom)
    img = paper_noise(img, noise)
    d = ImageDraw.Draw(img)
    d.rectangle([18, 18, W - 18, H - 18], outline=ink, width=4)
    d.rectangle([28, 28, W - 28, H - 28], outline=ink, width=1)
    for x, y, sx, sy in [(40, 40, 1, 1), (W - 40, 40, -1, 1),
                         (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)]:
        corner(d, x, y, sx, sy, accent)
    return img, d


def _centered(d, text, fnt, cx, y, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def make_card_back():
    """全カード共通の汎用裏面（抽象シール：同心円＋菱形）。タイトル未定のため銘なし。"""
    W, H = 600, 840
    ink = (46, 41, 36)
    accent = (150, 36, 38)
    img, d = _back_base((234, 230, 220), (206, 200, 187), ink, accent)
    cx, cy = W // 2, H // 2 - 40
    for r in (152, 122):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    d.polygon([(cx, cy - 74), (cx + 74, cy), (cx, cy + 74), (cx - 74, cy)],
              outline=accent, width=4)
    # 中央：抽象的な小菱形シール（銘の代わり）
    d.polygon([(cx, cy - 30), (cx + 30, cy), (cx, cy + 30), (cx - 30, cy)], fill=ink)
    _centered(d, "C O N F I D E N T I A L", F("goth_m", 24), cx, cy + 286, accent)
    _centered(d, "地下研究施設 ── 調査記録", F("goth_m", 20), cx, cy + 330, (112, 102, 92))
    return img.convert("RGB")


def make_back_safe(variant="dial"):
    """固有マス『鍵付き金庫』の裏面。マスの種類を公開にするため銘を大きく入れる。
    variant: 'dial'＝金のダイヤル錠（神殿基調）／'chest'＝封印された古櫃（木地＋御札＋注連縄）／
    'lock'＝注連縄を巻いた和錠（墨地）。"""
    W, H = 600, 840
    cx = W // 2

    if variant == "vault":  # 研究標本保管庫＋封印（科学×民俗の融合）
        steel, gold, shu, line = (158, 168, 184), (200, 170, 104), (208, 78, 60), (224, 228, 236)
        bg = (16, 24, 36)
        img, d = _back_base((40, 50, 66), bg, line, shu, noise=2)
        # 金属キャビネット
        d.rectangle([cx - 156, 250, cx + 156, 566], outline=steel, width=4)
        d.rectangle([cx - 156, 250, cx + 156, 300], outline=steel, width=2)  # 銘板帯
        d.rectangle([cx - 120, 260, cx + 120, 292], fill=(232, 230, 224))    # 研究銘板（要素1つに集約）
        _centered(d, "標本保管庫", F("goth_b", 22), cx, 264, (40, 44, 52))
        for yy in range(372, 520, 64):                                       # 扉のパネル溝（間引き）
            d.line([(cx - 138, yy), (cx + 138, yy)], fill=_mix((40, 50, 66), steel, 0.4), width=2)
        d.ellipse([cx + 70, 470, cx + 130, 530], outline=gold, width=4)      # ダイヤル錠
        for i in range(12):
            a = math.radians(i * 30)
            d.line([(cx + 100 + 30 * math.cos(a), 500 + 30 * math.sin(a)),
                    (cx + 100 + 24 * math.cos(a), 500 + 24 * math.sin(a))], fill=gold, width=2)
        d.ellipse([cx + 92, 492, cx + 108, 508], fill=gold)
        d.rectangle([cx - 174, 320, cx + 174, 346], fill=gold)               # 注連縄帯（封印）
        for x in range(cx - 174, cx + 174, 14):
            d.line([(x, 320), (x + 8, 346)], fill=_mix(gold, bg, 0.5), width=3)
        for k in range(3):
            _shide(d, cx - 108 + k * 108, 346, 22, 13, 3, line)
        _ofuda_strip(d, cx - 70, 372, 54, 150, (242, 236, 224), shu, "封印")  # 御札（扉）
        _centered(d, "金庫", F("mincho_b", 76), cx, 590, line)
        _centered(d, "標本保管庫 ── 要開錠", F("goth_m", 23), cx, 690, gold)
        return img.convert("RGB")

    if variant == "chest":  # 封印された古櫃（唐櫃）
        gold, shu, line = (198, 168, 104), (202, 76, 58), (236, 228, 214)
        img, d = _back_base((78, 58, 42), (40, 28, 18), line, gold, noise=4)
        d.polygon([(cx - 160, 300), (cx - 128, 268), (cx + 128, 268), (cx + 160, 300)],
                  outline=gold, width=4)                         # 蓋上面
        d.rectangle([cx - 160, 300, cx + 160, 360], outline=gold, width=4)  # 蓋前面
        d.rectangle([cx - 160, 360, cx + 160, 560], outline=gold, width=4)  # 箱
        for bx in (cx - 96, cx + 96):                            # 縦金具
            d.rectangle([bx - 9, 300, bx + 9, 560], fill=_mix((78, 58, 42), gold, 0.55))
        d.rounded_rectangle([cx - 26, 392, cx + 26, 446], radius=8, fill=gold)  # 錠前
        d.ellipse([cx - 9, 404, cx + 9, 422], fill=(40, 28, 18))
        d.rectangle([cx - 178, 332, cx + 178, 356], fill=gold)   # 注連縄（横帯）
        for x in range(cx - 178, cx + 178, 14):
            d.line([(x, 332), (x + 8, 356)], fill=_mix(gold, (40, 28, 18), 0.5), width=3)
        for k in range(3):
            _shide(d, cx - 110 + k * 110, 356, 22, 13, 3, line)
        _ofuda_strip(d, cx, 380, 56, 152, (242, 236, 224), shu, "封印")  # 御札
        _centered(d, "金庫", F("mincho_b", 80), cx, 584, line)
        _centered(d, "封じられた櫃 ── 要開錠", F("goth_m", 23), cx, 686, gold)
        return img.convert("RGB")

    if variant == "lock":  # 注連縄を巻いた和錠（墨地）
        gold, shu, line = (200, 170, 104), (206, 80, 62), (232, 228, 222)
        img, d = _back_base((46, 42, 48), (20, 18, 22), line, shu, noise=3)
        cy = H // 2 - 70
        d.arc([cx - 74, cy - 150, cx + 74, cy + 26], start=180, end=360, fill=gold, width=12)  # 弦
        d.rounded_rectangle([cx - 120, cy - 36, cx + 120, cy + 92], radius=22, outline=gold, width=6)
        d.ellipse([cx - 18, cy + 8, cx + 18, cy + 44], fill=gold)  # 鍵穴
        d.polygon([(cx - 6, cy + 32), (cx + 6, cy + 32), (cx + 12, cy + 80), (cx - 12, cy + 80)], fill=gold)
        d.rectangle([cx - 150, cy - 4, cx + 150, cy + 20], fill=gold)  # 注連縄
        for x in range(cx - 150, cx + 150, 13):
            d.line([(x, cy - 4), (x + 7, cy + 20)], fill=_mix(gold, (20, 18, 22), 0.5), width=3)
        for k in range(3):
            _shide(d, cx - 100 + k * 100, cy + 20, 22, 13, 3, line)
        _centered(d, "金庫", F("mincho_b", 80), cx, cy + 168, line)
        _centered(d, "鍵付き金庫 ── 要開錠", F("goth_m", 23), cx, cy + 268, gold)
        return img.convert("RGB")

    # dial（既定・神殿基調）
    line = (224, 228, 236)
    gold = (202, 170, 104)   # 金
    shu = (208, 86, 60)      # 朱
    img, d = _back_base((34, 44, 60), (15, 22, 34), line, shu, noise=2)
    cx, cy = W // 2, H // 2 - 56

    # ダイヤル錠（ヴォルトの回転ハンドル・金）
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], outline=gold, width=5)
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=gold, width=2)
    # 目盛り（基本軸を長く）
    for i in range(36):
        a = math.radians(i * 10 - 90)
        r1 = 132 if i % 9 == 0 else (138 if i % 3 == 0 else 142)
        wd = 4 if i % 9 == 0 else 2
        d.line([(cx + 150 * math.cos(a), cy + 150 * math.sin(a)),
                (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], fill=gold, width=wd)
    # ハブ＋4本スポーク＋朱グリップ
    for a_deg in (45, 135, 225, 315):
        a = math.radians(a_deg)
        d.line([(cx, cy), (cx + 108 * math.cos(a), cy + 108 * math.sin(a))],
               fill=gold, width=10)
        gx, gy = cx + 108 * math.cos(a), cy + 108 * math.sin(a)
        d.ellipse([gx - 14, gy - 14, gx + 14, gy + 14], fill=shu)
    d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=gold)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=shu)

    _centered(d, "金庫", F("mincho_b", 84), cx, cy + 196, line)
    _centered(d, "鍵付き金庫 ── 要開錠", F("goth_m", 24), cx, cy + 300, gold)
    return img.convert("RGB")


def _seam_v(d, x, y0, y1, core, glow):
    """中央の光の隙間（扉が自動で開く演出）。"""
    d.line([(x, y0), (x, y1)], fill=glow, width=12)
    d.line([(x, y0), (x, y1)], fill=core, width=3)


def _scan_h(d, cx, y, half, col):
    """水平の走査ライン。"""
    d.line([(cx - half, y), (cx + half, y)], fill=col, width=5)
    d.line([(cx - half, y - 8), (cx + half, y - 8)], fill=col, width=1)
    d.line([(cx - half, y + 8), (cx + half, y + 8)], fill=col, width=1)


def make_back_biodoor(variant="gate"):
    """固有マス『生体認証扉』の裏面。指紋ではなく『近づくと存在を照合し自動開放する扉』。
    指紋との誤認を避けるため複数モチーフを用意（gate/figure/sensor/panel）。反応条件は明かさない。
    銘は大きく入れ、マスの種類を公開情報にする。"""
    W, H = 600, 840
    cx = W // 2

    if variant == "gate":  # 神殿門＋自動開放（民俗学テーマと融合）
        ink, accent, gold = (224, 228, 236), (208, 86, 60), (202, 170, 104)
        img, d = _back_base((34, 44, 60), (15, 22, 34), ink, accent, noise=2)
        d.polygon([(cx - 192, 200), (cx - 178, 166), (cx + 178, 166),
                   (cx + 192, 200), (cx + 178, 188), (cx - 178, 188)], fill=accent)  # 笠木
        d.rectangle([cx - 12, 188, cx + 12, 250], fill=accent)   # 額束
        d.rectangle([cx - 154, 248, cx + 154, 268], fill=accent)  # 貫
        d.rectangle([cx - 134, 188, cx - 108, 486], fill=accent)  # 左柱
        d.rectangle([cx + 108, 188, cx + 134, 486], fill=accent)  # 右柱
        d.rectangle([cx - 150, 484, cx + 150, 500], fill=gold)    # 土台
        for x0, x1 in ((cx - 104, cx - 6), (cx + 6, cx + 104)):   # 引き戸
            d.rectangle([x0, 270, x1, 480], outline=ink, width=3)
            for yy in range(304, 470, 34):
                d.line([(x0 + 8, yy), (x1 - 8, yy)], fill=_mix((15, 22, 34), ink, 0.32), width=2)
        _seam_v(d, cx, 270, 480, (252, 238, 204), gold)           # 中央の光（開放）
        _scan_h(d, cx, 392, 150, gold)
        status = "▶ AUTHENTICATION  COMPLETE"

    elif variant == "figure":  # 全身シルエット照合
        ink, accent = (214, 234, 236), (98, 208, 214)
        img, d = _back_base((26, 58, 64), (13, 36, 42), ink, accent, noise=2)
        for x, y, sx, sy in [(cx - 162, 178, 1, 1), (cx + 162, 178, -1, 1),
                             (cx - 162, 510, 1, -1), (cx + 162, 510, -1, -1)]:
            d.line([(x, y), (x + sx * 42, y)], fill=accent, width=3)
            d.line([(x, y), (x, y + sy * 42)], fill=accent, width=3)
        d.ellipse([cx - 30, 198, cx + 30, 258], outline=accent, width=3)  # 頭
        d.line([(cx, 258), (cx, 300)], fill=accent, width=3)              # 首
        body = [(cx - 48, 300), (cx + 48, 300), (cx + 36, 432), (cx + 50, 522),
                (cx + 14, 522), (cx, 436), (cx - 14, 522), (cx - 50, 522), (cx - 36, 432)]
        d.line(body + [body[0]], fill=accent, width=3, joint="curve")     # 胴〜脚
        d.line([(cx - 48, 306), (cx - 74, 426)], fill=accent, width=3)    # 腕
        d.line([(cx + 48, 306), (cx + 74, 426)], fill=accent, width=3)
        tick = _mix((26, 58, 64), accent, 0.6)
        for yy in range(212, 508, 24):
            d.line([(cx - 178, yy), (cx - 168, yy)], fill=tick, width=2)
            d.line([(cx + 168, yy), (cx + 178, yy)], fill=tick, width=2)
        _scan_h(d, cx, 372, 150, accent)
        status = "▶ FULL-BODY  MATCH  COMPLETE"

    elif variant == "sensor":  # 走査センサー（抽象・身体部位を出さない）
        ink, accent = (214, 234, 236), (98, 208, 214)
        img, d = _back_base((22, 52, 60), (12, 32, 40), ink, accent, noise=2)
        mcy = 330
        for R in (58, 106, 154):
            pts = [(cx + R * math.cos(math.radians(60 * k - 90)),
                    mcy + R * math.sin(math.radians(60 * k - 90))) for k in range(6)]
            d.line(pts + [pts[0]], fill=accent if R == 154 else _mix((22, 52, 60), accent, 0.7),
                   width=3 if R == 154 else 2, joint="curve")
        cross = _mix((22, 52, 60), accent, 0.45)
        d.line([(cx - 182, mcy), (cx + 182, mcy)], fill=cross, width=1)
        d.line([(cx, mcy - 182), (cx, mcy + 182)], fill=cross, width=1)
        for a in range(0, 360, 15):
            ar = math.radians(a)
            r1 = 178 if a % 45 == 0 else 168
            d.line([(cx + 158 * math.cos(ar), mcy + 158 * math.sin(ar)),
                    (cx + r1 * math.cos(ar), mcy + r1 * math.sin(ar))], fill=accent, width=2)
        d.polygon([(cx, mcy - 16), (cx + 16, mcy), (cx, mcy + 16), (cx - 16, mcy)], fill=accent)
        d.arc([cx - 106, mcy - 106, cx + 106, mcy + 106], start=-90, end=12,
              fill=(224, 252, 252), width=5)
        status = "▶ PRESENCE  DETECTED"

    elif variant == "shrine":  # 注連縄を渡した鳥居（彼岸の冷光・配色変更）
        ink, accent = (214, 224, 236), (150, 196, 214)
        rope, stone = (200, 178, 120), (150, 162, 180)
        img, d = _back_base((20, 26, 40), (8, 11, 20), ink, accent, noise=2)
        d.polygon([(cx - 192, 200), (cx - 178, 166), (cx + 178, 166),
                   (cx + 192, 200), (cx + 178, 188), (cx - 178, 188)], fill=stone)  # 笠木
        d.rectangle([cx - 12, 188, cx + 12, 250], fill=stone)    # 額束
        d.rectangle([cx - 134, 188, cx - 108, 486], fill=stone)  # 柱
        d.rectangle([cx + 108, 188, cx + 134, 486], fill=stone)
        _seam_v(d, cx, 272, 480, (228, 248, 255), accent)        # 彼岸の冷光
        d.rectangle([cx - 152, 240, cx + 152, 272], fill=rope)   # 注連縄
        for x in range(cx - 152, cx + 152, 13):
            d.line([(x, 240), (x + 7, 272)], fill=_mix(rope, (8, 11, 20), 0.5), width=3)
        for k in range(3):
            _shide(d, cx - 100 + k * 100, 272, 24, 15, 3, (236, 236, 230))
        status = "▶ AUTHENTICATION  COMPLETE"

    elif variant == "shrine_tech":  # 注連縄鳥居＋走査装置・電極（科学×民俗の融合）
        ink, accent = (214, 224, 236), (120, 202, 216)
        rope, stone = (200, 178, 120), (150, 162, 180)
        img, d = _back_base((20, 28, 42), (8, 12, 22), ink, accent, noise=2)
        for x, y, sx, sy in [(cx - 176, 182, 1, 1), (cx + 176, 182, -1, 1),
                             (cx - 176, 500, 1, -1), (cx + 176, 500, -1, -1)]:  # 走査枠（研究）
            d.line([(x, y), (x + sx * 40, y)], fill=accent, width=3)
            d.line([(x, y), (x, y + sy * 40)], fill=accent, width=3)
        d.polygon([(cx - 188, 200), (cx - 174, 168), (cx + 174, 168),
                   (cx + 188, 200), (cx + 174, 188), (cx - 174, 188)], fill=stone)  # 笠木
        d.rectangle([cx - 12, 188, cx + 12, 250], fill=stone)     # 額束
        d.rectangle([cx - 130, 188, cx - 106, 470], fill=stone)   # 柱
        d.rectangle([cx + 106, 188, cx + 130, 470], fill=stone)
        _seam_v(d, cx, 268, 470, (224, 248, 255), accent)         # 彼岸の冷光
        for sgn in (-1, 1):                                       # 電極ノード（封印装置＝電極・1対のみ）
            px = cx + sgn * 118
            d.ellipse([px - 7, 366 - 7, px + 7, 366 + 7], outline=accent, width=2)
            d.ellipse([px - 2, 366 - 2, px + 2, 366 + 2], fill=accent)
            d.line([(px - sgn * 7, 366), (px - sgn * 26, 366)], fill=accent, width=2)
        d.rectangle([cx - 150, 236, cx + 150, 266], fill=rope)    # 注連縄
        for x in range(cx - 150, cx + 150, 13):
            d.line([(x, 236), (x + 7, 266)], fill=_mix(rope, (8, 12, 22), 0.5), width=3)
        for k in range(3):
            _shide(d, cx - 100 + k * 100, 266, 24, 15, 3, (236, 236, 230))
        status = "▶ AUTHENTICATION  COMPLETE"

    elif variant == "mirror":  # 八咫鏡＋注連縄（覗き＝鏡。近づく者を映して認証）
        ink, accent = (224, 228, 236), (202, 176, 110)
        mcy = 322
        img, d = _back_base((26, 30, 46), (12, 14, 26), ink, accent, noise=2)
        for i, R in enumerate(range(150, 0, -22)):               # 鏡面（磨いた銅の放射）
            c = _mix((26, 30, 46), (206, 216, 226), min(0.86, 0.16 + i * 0.12))
            d.ellipse([cx - R, mcy - R, cx + R, mcy + R], fill=c)
        for R in (150, 128):                                     # 銅縁
            d.ellipse([cx - R, mcy - R, cx + R, mcy + R], outline=accent, width=5 if R == 150 else 2)
        d.arc([cx - 64, mcy - 34, cx + 64, mcy + 30], start=200, end=340,
              fill=_mix((26, 30, 46), (70, 84, 110), 1.0), width=3)  # 映り込み（覗き）
        _shimenawa(d, cx, mcy, 178, accent, _mix(accent, (12, 14, 26), 0.45), (236, 232, 222))
        status = "▶ AUTHENTICATION  COMPLETE"

    else:  # panel: 自動スライド扉＋認証ステータス
        variant = "panel"
        ink, accent = (214, 232, 238), (110, 214, 200)
        img, d = _back_base((30, 46, 58), (14, 26, 38), ink, accent, noise=2)
        d.rectangle([cx - 160, 188, cx + 160, 470], outline=ink, width=4)
        for x0, x1 in ((cx - 154, cx - 8), (cx + 8, cx + 154)):
            d.rectangle([x0, 194, x1, 464], outline=_mix((30, 46, 58), ink, 0.55), width=2)
            for yy in range(218, 456, 28):
                d.line([(x0 + 10, yy), (x1 - 10, yy)], fill=_mix((30, 46, 58), ink, 0.26), width=2)
        _seam_v(d, cx, 194, 464, (224, 255, 246), accent)
        d.polygon([(cx - 42, 326), (cx - 70, 308), (cx - 70, 344)], fill=accent)  # ◄
        d.polygon([(cx + 42, 326), (cx + 70, 308), (cx + 70, 344)], fill=accent)  # ►
        d.rounded_rectangle([cx - 124, 492, cx + 124, 536], radius=10, outline=accent, width=2)
        d.ellipse([cx - 108, 506, cx - 88, 526], fill=(122, 242, 172))
        d.text((cx - 72, 500), "AUTH  ✓  OPEN", font=F("goth_b", 24), fill=accent)
        status = "▶ AUTO-GATE  RELEASED"

    _centered(d, status, F("goth_m", 19), cx, 136, accent)
    _centered(d, "生体認証扉", F("mincho_b", 76), cx, 552, ink)
    _centered(d, "生体認証 ── 自動開放", F("goth_m", 23), cx, 650, accent)
    return img.convert("RGB")


def _contact(paths, labels, cols=2, scale=0.46):
    """選定用コンタクトシート（縮小サムネ＋ラベルを格子に並べる）。"""
    tw, th = int(600 * scale), int(840 * scale)
    pad, lh = 26, 34
    rows = (len(paths) + cols - 1) // cols
    W = cols * tw + (cols + 1) * pad
    H = rows * (th + lh) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), (236, 236, 238))
    d = ImageDraw.Draw(sheet)
    for i, (p, lb) in enumerate(zip(paths, labels)):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + lh + pad)
        sheet.paste(Image.open(p).resize((tw, th)), (x, y))
        d.text((x + 4, y + th + 6), lb, font=F("goth_b", 20), fill=(40, 40, 44))
    return sheet


# ============================================================
# 「科学 × 日本神話/民俗学」デザイン言語の探索用パーツ＆サンプル
# ============================================================
def _enso(d, cx, cy, r, col, width):
    """円相（筆で描いた閉じきらない円）。和の象徴。"""
    d.arc([cx - r, cy - r, cx + r, cy + r], start=38, end=332, fill=col, width=width)
    d.arc([cx - r + 3, cy - r - 2, cx + r + 3, cy + r - 2], start=60, end=300,
          fill=col, width=max(2, width - 8))


def _seal(d, cx, cy, r, text, col, paper):
    """朱印（白抜きの角印）。研究文書に神社的な印を重ねる。"""
    d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=12, fill=col)
    d.rounded_rectangle([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                        radius=8, outline=paper, width=2)
    f = F("mincho_b", int(r * 1.25))
    bb = d.textbbox((0, 0), text, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
           text, font=f, fill=paper)


def _vtext(d, x, y, text, fnt, fill, lh):
    """縦書き（1文字ずつ下へ）。"""
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        y += lh


def _tomoe(d, cx, cy, r, col, hole_col=None, ring=True):
    """三つ巴（神紋風）。hole_col を与えると各頭に穴＝勾玉（魂）として読ませる。"""
    if ring:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
    for k in range(3):
        a = math.radians(120 * k - 90)
        hx, hy = cx + 0.42 * r * math.cos(a), cy + 0.42 * r * math.sin(a)
        hr = 0.34 * r
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=col)
        # 中心へ向かう尾
        pa = math.radians(120 * k - 90 + 36)
        d.polygon([(hx + hr * math.cos(a), hy + hr * math.sin(a)),
                   (cx, cy),
                   (hx + hr * math.cos(pa - math.pi / 2),
                    hy + hr * math.sin(pa - math.pi / 2))], fill=col)
        if hole_col is not None:  # 勾玉の穴
            d.ellipse([hx - hr * 0.36, hy - hr * 0.36, hx + hr * 0.36, hy + hr * 0.36],
                      fill=hole_col)


def _shide(d, cx, top, w, seg, n, col):
    """紙垂（しで）＝注連縄から垂れる稲妻形の白紙。"""
    y = top
    for i in range(n):
        off = (i % 2) * (w // 2) - w // 4
        d.rectangle([cx + off - w // 2, y, cx + off + w // 2, y + seg - 2], fill=col)
        y += seg


def _shimenawa(d, cx, cy, R, rope, rope_d, shide_col, n_shide=3):
    """注連縄の輪＝封印/結界。縄のねじれ＋下辺に紙垂を吊る。"""
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=rope, width=22)
    for a in range(0, 360, 11):
        ar = math.radians(a)
        x0, y0 = cx + (R - 10) * math.cos(ar), cy + (R - 10) * math.sin(ar)
        x1, y1 = cx + (R + 10) * math.cos(ar + 0.14), cy + (R + 10) * math.sin(ar + 0.14)
        d.line([(x0, y0), (x1, y1)], fill=rope_d, width=3)
    for k in range(n_shide):
        sx = cx - R + (2 * R) * (k + 1) / (n_shide + 1)
        _shide(d, int(sx), int(cy + R - 8), 26, 16, 4, shide_col)


def _ofuda_strip(d, cx, y0, w, h, paper, ink, text):
    """御札（封符）＝白い縦長紙に縦書きの朱字。"""
    d.rectangle([cx - w // 2, y0, cx + w // 2, y0 + h], fill=paper, outline=ink, width=3)
    f = F("mincho_b", w - 18)
    _vtext(d, cx - (w - 18) // 2, y0 + 16, text, f, ink, w - 4)


def _taiji_magatama(d, cx, cy, R, red, white, ring=None):
    """紅白の二つ巴（＝赤白の勾玉を合わせた魂のしるし。太極状にかみ合う）。"""
    bbox = [cx - R, cy - R, cx + R, cy + R]
    d.ellipse(bbox, fill=white)
    d.pieslice(bbox, 270, 90, fill=red)                                  # 右半＝朱
    d.ellipse([cx - R / 2, cy - R, cx + R / 2, cy], fill=red)            # 上の渦＝朱
    d.ellipse([cx - R / 2, cy, cx + R / 2, cy + R], fill=white)          # 下の渦＝白
    er = R * 0.14                                                         # 勾玉の穴（眼）
    d.ellipse([cx - er, cy - R / 2 - er, cx + er, cy - R / 2 + er], fill=white)
    d.ellipse([cx - er, cy + R / 2 - er, cx + er, cy + R / 2 + er], fill=red)
    if ring:
        d.ellipse([cx - R - 10, cy - R - 10, cx + R + 10, cy + R + 10], outline=ring, width=3)


def _lab_plate(d, cx, y, w, code, ink, paper=None):
    """研究ラベル（標本票風）＝型番＋簡易バーコード。科学側の存在感を残す小片。"""
    h = 32
    if paper:
        d.rectangle([cx - w // 2, y, cx + w // 2, y + h], fill=paper, outline=ink, width=2)
    else:
        d.rectangle([cx - w // 2, y, cx + w // 2, y + h], outline=ink, width=1)
    d.text((cx - w // 2 + 10, y + 7), code, font=F("ms_goth", 16), fill=ink)
    rr = random.Random(sum(ord(c) for c in code))
    bx = cx + w // 2 - 82
    for i in range(38):
        if rr.random() < 0.5:
            continue
        d.line([(bx + i * 2, y + 8), (bx + i * 2, y + h - 8)], fill=ink, width=1)


def _spec_sticker(code, label="標本  SPECIMEN", angle=-6):
    """研究標本の整理票（白いラベルを傾けて貼る＝科学側のモチーフ）。RGBAを返す。"""
    w, h = 198, 86
    s = Image.new("RGBA", (w + 22, h + 22), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rectangle([11, 11, 11 + w, 11 + h], fill=(247, 246, 242), outline=(74, 70, 64), width=2)
    sd.text((24, 18), label, font=F("goth_b", 16), fill=(150, 60, 52))
    sd.line([(24, 42), (11 + w - 13, 42)], fill=(150, 60, 52), width=1)
    sd.text((24, 50), code, font=F("ms_goth", 17), fill=(38, 36, 32))
    rr = random.Random(sum(ord(c) for c in code))
    bx = 122
    for i in range(38):
        if rr.random() < 0.45:
            continue
        sd.line([(bx + i * 2, 52), (bx + i * 2, h + 7)], fill=(28, 26, 24), width=1)
    return s.rotate(angle, expand=True, resample=Image.BICUBIC)


def make_evidence_card_wa(no, title, body, variant="ofuda", header="物的証拠", prefix="C"):
    """『科学×民俗学』版のカード表。和紙＋朱＋墨＋朱印。
    variant: 'ofuda'＝証拠カード（御札の朱太枠＋標本票）／'research'＝研究資料（藍枠＋綴じ穴の内部文書）／
    'shrine'＝社務所文書（朱帯＋方眼）。"""
    W, H = 600, 840
    sumi = (40, 33, 29)        # 墨
    shu = (188, 54, 44)        # 朱
    kin = (172, 138, 74)       # 金（くすませ）
    washi0, washi1 = (239, 234, 223), (223, 216, 200)
    img = vgrad((W, H), washi0, washi1)
    img = paper_noise(img, 5)
    d = ImageDraw.Draw(img)

    if variant == "ofuda":
        # 御札の朱太枠＋墨の内罫
        d.rectangle([16, 16, W - 16, H - 16], outline=shu, width=12)
        d.rectangle([34, 34, W - 34, H - 34], outline=sumi, width=2)
        # 左の縦書き封号
        _vtext(d, 50, 152, "封", F("mincho_b", 40), shu, 52)
        # ヘッダ朱帯
        d.rectangle([110, 48, W - 50, 126], fill=shu)
        d.text((128, 64), header, font=F("mincho_b", 38), fill=(239, 231, 219))
        no_s = "No. %s-%02d" % (prefix, no)
        fno = F("goth_m", 23)
        d.text((W - 66 - d.textlength(no_s, font=fno), 76), no_s, font=fno, fill=(244, 210, 204))
        # 題
        d.text((112, 158), title, font=F("mincho_b", 44), fill=sumi)
        d.line([(112, 232), (W - 50, 232)], fill=kin, width=2)
        # 研究フィールド（科学側のモチーフを混ぜる）
        d.text((112, 244), "分類 ⌖   採取 観察室   記録者 ─",
               font=F("ms_goth", 18), fill=(98, 86, 74))
        # 円相の透かし
        _enso(d, W // 2 + 20, 474, 148, _mix(washi1, shu, 0.16), 18)
        wrap_draw(d, (112, 286), body, F("goth_m", 26), (54, 47, 43), 15, 46)
        _seal(d, W - 122, H - 152, 52, "秘", shu, washi0)
        # 研究標本の整理票を貼り付け（御札×研究の融合）
        img = img.convert("RGBA")
        img.alpha_composite(_spec_sticker("%s-%02d  観察室" % (prefix, no)), (38, H - 190))
        d = ImageDraw.Draw(img)
    elif variant == "research":
        # 研究資料＝綴じた内部文書（藍枠＋綴じ穴）。証拠カード（御札・朱）と差別化。
        indigo = (44, 62, 96)
        d.rectangle([16, 16, W - 16, H - 16], outline=indigo, width=10)
        d.rectangle([34, 34, W - 34, H - 34], outline=sumi, width=2)
        for hy in (210, 410, 610):                       # 綴じ穴
            d.ellipse([44, hy - 13, 70, hy + 13], outline=indigo, width=3)
        d.rectangle([96, 48, W - 50, 128], fill=indigo)  # 藍帯ヘッダ
        d.text((116, 62), header, font=F("mincho_b", 42), fill=(232, 234, 240))
        no_s = "No. %s-%02d" % (prefix, no)
        fno = F("goth_m", 23)
        d.text((W - 66 - d.textlength(no_s, font=fno), 78), no_s, font=fno, fill=(206, 214, 230))
        d.text((112, 160), title, font=F("mincho_b", 44), fill=sumi)
        d.line([(112, 234), (W - 50, 234)], fill=kin, width=2)
        d.text((112, 246), "分類 ⌖   整理 ──   観測者効果",
               font=F("ms_goth", 18), fill=(86, 92, 110))
        _enso(d, W // 2 + 16, 474, 148, _mix(washi1, indigo, 0.14), 18)
        wrap_draw(d, (112, 288), body, F("goth_m", 26), (52, 50, 58), 15, 46)
        _seal(d, W - 122, H - 152, 52, "資", indigo, washi0)
    else:  # shrine
        d.rectangle([18, 18, W - 18, H - 18], outline=sumi, width=4)
        d.rectangle([28, 28, W - 28, H - 28], outline=kin, width=1)
        # 方眼（科学側）
        grid = _mix(washi1, sumi, 0.10)
        for gx in range(60, W - 40, 40):
            d.line([(gx, 140), (gx, H - 100)], fill=grid, width=1)
        for gy in range(140, H - 100, 40):
            d.line([(50, gy), (W - 40, gy)], fill=grid, width=1)
        # 円相透かし
        _enso(d, W // 2, 460, 156, _mix(washi1, shu, 0.14), 18)
        # 朱帯ヘッダ＋紙垂風の刻み
        d.rectangle([28, 28, W - 28, 122], fill=shu)
        for sx in range(40, W - 40, 26):
            d.line([(sx, 122), (sx + 8, 138)], fill=shu, width=3)
        d.text((50, 50), header, font=F("mincho_b", 40), fill=(239, 231, 219))
        no_s = "No. %s-%02d" % (prefix, no)
        fno = F("goth_m", 24)
        d.text((W - 50 - d.textlength(no_s, font=fno), 66), no_s, font=fno, fill=(244, 210, 204))
        d.text((52, 162), title, font=F("mincho_b", 46), fill=sumi)
        d.line([(52, 238), (W - 52, 238)], fill=kin, width=2)
        wrap_draw(d, (56, 286), body, F("goth_m", 27), (54, 47, 43), 16, 48)
        _seal(d, W - 116, H - 150, 52, "封", shu, washi0)

    foot = "地下研究施設 ── 調査記録"
    fft = F("goth_m", 20)
    d.text(((W - d.textlength(foot, font=fft)) / 2, H - 56), foot, font=fft, fill=(120, 100, 86))
    return img.convert("RGB")


def make_card_back_wa(variant="enso"):
    """『神殿』基調の裏面（gateと統一の濃紺＋朱/金）。variant: 'enso'＝円相＋朱印／'tomoe'＝三つ巴。"""
    W, H = 600, 840
    line = (224, 228, 236)
    shu = (208, 86, 60)
    gold = (202, 170, 104)
    bg = (15, 22, 34)
    img, d = _back_base((34, 44, 60), bg, line, shu, noise=2)
    cx, cy = W // 2, H // 2 - 40
    if variant == "tomoe":
        _tomoe(d, cx, cy, 150, shu)
        _seal(d, cx, cy + 250, 46, "秘", gold, (20, 26, 38))
    elif variant == "magatama":   # 勾玉三つ巴（＝三つの魂）
        _tomoe(d, cx, cy, 152, shu, hole_col=bg)
        _centered(d, "魂  ──  みたま", F("goth_m", 22), cx, cy + 196, gold)
    elif variant == "magatama_rw":  # 紅白の勾玉（二つ巴／魂）＋「証拠カード」表記
        _taiji_magatama(d, cx, cy, 150, shu, (236, 232, 222), ring=gold)
        _centered(d, "証拠カード", F("mincho_b", 76), cx, cy + 200, line)
    elif variant == "shimenawa":  # 注連縄の輪＋中央に勾玉（＝封印の結界）
        _shimenawa(d, cx, cy, 150, gold, _mix(gold, bg, 0.45), (236, 232, 222))
        _tomoe(d, cx, cy, 64, shu, hole_col=bg)
    else:  # enso
        _enso(d, cx, cy, 150, gold, 16)
        _seal(d, cx, cy, 52, "秘", shu, (236, 230, 220))
    _centered(d, "地下研究施設 ── 調査記録", F("goth_m", 22), cx, cy + 318, _mix(bg, line, 0.7))
    return img.convert("RGB")


def make_shock_card(no, title, body, header="物的証拠", prefix="C"):
    """衝撃証拠カード。通常のクラフト紙タグと違い、めくった瞬間に色調が暗転する。
    『空の防護服＋こぼれ落ちる灰』のイラストで開示時のギョッとを狙う一点物デザイン。"""
    W, H = 600, 840
    ash = (208, 201, 188)   # 灰白＝主テキスト
    ember = (158, 46, 42)   # 残り火の赤
    suit = (150, 159, 170)  # 防護服の線
    sub = (132, 124, 114)

    # 焦げた暗い下地
    img = vgrad((W, H), (42, 37, 35), (16, 14, 13))
    img = paper_noise(img, 4)
    img = img.convert("RGBA")
    # 四隅の焦げ（半透明の黒い滲み）
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    rnd = random.Random(29)
    for _ in range(70):
        ex = rnd.choice([rnd.randint(0, 150), rnd.randint(W - 150, W)]) if rnd.random() < .5 else rnd.randint(0, W)
        ey = rnd.choice([rnd.randint(0, 150), rnd.randint(H - 150, H)]) if rnd.random() < .5 else rnd.randint(0, H)
        r = rnd.randint(30, 90)
        a = rnd.randint(18, 46)
        od.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(0, 0, 0, a))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)

    # 枠＋焦げ色コーナー
    d.rectangle([18, 18, W - 18, H - 18], outline=ash, width=3)
    d.rectangle([28, 28, W - 28, H - 28], outline=(78, 44, 40), width=1)
    for x, y, sx, sy in [(40, 40, 1, 1), (W - 40, 40, -1, 1),
                         (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)]:
        corner(d, x, y, sx, sy, ember)

    # ヘッダ帯（血のような暗赤）
    d.rectangle([28, 28, W - 28, 118], fill=(92, 28, 26))
    d.text((48, 48), header, font=F("mincho_b", 42), fill=ash)
    no_s = "No. %s-%02d" % (prefix, no)
    f_no = F("goth_m", 26)
    d.text((W - 48 - d.textlength(no_s, font=f_no), 62), no_s, font=f_no, fill=(206, 150, 148))

    # 品名
    d.text((52, 150), title, font=F("mincho_b", 48), fill=ash)
    yy = 224
    d.line([(52, yy), (W - 52, yy)], fill=(96, 72, 66), width=2)
    cx = W // 2
    d.polygon([(cx, yy - 9), (cx + 11, yy), (cx, yy + 9), (cx - 11, yy)], fill=ember)

    # ── イラスト：空の防護服が立ったまま崩れ、中身が灰になってこぼれる ──
    icx = cx
    # フード（頭部）＋バイザー
    d.ellipse([icx - 58, 244, icx + 58, 360], outline=suit, width=4)
    d.rounded_rectangle([icx - 38, 282, icx + 38, 334], radius=14,
                        fill=(24, 26, 30), outline=suit, width=3)
    # 肩〜胴（下側は崩れて線が途切れる）
    d.line([(icx - 80, 380), (icx + 80, 380)], fill=suit, width=4)
    d.line([(icx - 80, 380), (icx - 66, 476)], fill=suit, width=4)
    d.line([(icx + 80, 380), (icx + 66, 476)], fill=suit, width=4)
    # 袖
    d.line([(icx - 78, 386), (icx - 110, 484)], fill=suit, width=4)
    d.line([(icx + 78, 386), (icx + 110, 484)], fill=suit, width=4)
    # 胴の崩れ際＝破線
    for sx in range(icx - 66, icx + 67, 15):
        d.line([(sx, 476), (sx + 7, 476)], fill=suit, width=3)

    # こぼれ落ちる灰（下に広がる山＋飛散）
    pile = random.Random(5)
    for _ in range(120):
        py = pile.randint(476, 540)
        spread = 34 + (py - 476) * 1.9
        px = icx + pile.uniform(-spread, spread)
        r = pile.uniform(6, 19)
        g = pile.randint(120, 196)
        d.ellipse([px - r, py - r * 0.7, px + r, py + r * 0.7],
                  fill=(g, g - 6, g - 16))
    for _ in range(140):  # 舞い上がる細かな灰
        px = icx + pile.uniform(-140, 140)
        py = pile.randint(400, 536)
        g = pile.randint(150, 215)
        d.ellipse([px, py, px + 2, py + 2], fill=(g, g - 4, g - 12))

    # 本文
    wrap_draw(d, (56, 566), body, F("goth_m", 24), ash, 20, 41)

    # スタンプ（赤・傾き）
    st = stamp("要検証", (190, 52, 48, 175), 50)
    img.alpha_composite(st, (W - st.width - 44, 312))

    # フッタ
    d = ImageDraw.Draw(img)
    foot = "地下研究施設 ── 調査記録"
    f_ft = F("goth_m", 20)
    d.text(((W - d.textlength(foot, font=f_ft)) / 2, H - 58), foot, font=f_ft, fill=(150, 120, 112))
    return img.convert("RGB")


PAPER_STYLES = {
    "warm":      dict(bg="paper",     c=((247, 245, 241), (236, 233, 227)), ink=(38, 34, 30),    acc=(150, 36, 38),   sub=(110, 104, 96),  f=("mincho_b", "mincho_b", "mincho", "mincho"), st=("原本", -10, (168, 42, 42, 140)),     nz=3),
    "mono":      dict(bg="plain",     c=((250, 250, 252), (243, 244, 246)), ink=(28, 30, 34),    acc=(74, 80, 90),    sub=(120, 124, 130), f=("goth_b", "goth_b", "goth_m", "goth_m"),   st=("管理", 0, (84, 90, 100, 150)),         nz=1),
    "blueprint": dict(bg="blueprint", c=((20, 40, 72), (14, 30, 56)),       ink=(214, 226, 242), acc=(124, 184, 234), sub=(120, 152, 194), f=("goth_b", "goth_b", "goth_m", "goth_m"),   st=("CONTROLLED", 0, (150, 192, 232, 150)), nz=0),
    "terminal":  dict(bg="plain",     c=((13, 16, 18), (9, 11, 13)),        ink=(120, 232, 140), acc=(96, 205, 128),  sub=(70, 150, 96),   f=("goth_m", "goth_b", "goth_m", "goth_m"),   st=("// LOG", 0, (120, 232, 140, 120)),     nz=0),
    "sepia":     dict(bg="paper",     c=((233, 217, 187), (213, 193, 157)), ink=(72, 50, 30),    acc=(142, 72, 40),   sub=(140, 116, 84),  f=("mincho_b", "mincho", "mincho", "mincho"), st=("archive", -8, (150, 90, 50, 140)),     nz=6),
    "labnote":   dict(bg="grid",      c=((250, 250, 244), (244, 245, 236)), ink=(40, 44, 52),    acc=(184, 60, 60),   sub=(120, 128, 120), f=("goth_b", "goth_b", "goth_m", "goth_m"),   st=("LAB", -6, (64, 94, 164, 140)),         nz=1),
    "topsecret": dict(bg="plain",     c=((252, 252, 250), (246, 246, 243)), ink=(18, 18, 20),    acc=(196, 42, 42),   sub=(108, 108, 110), f=("goth_b", "goth_b", "goth_m", "goth_m"),   st=("TOP SECRET", -12, (200, 42, 42, 165)), nz=1),
}


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _paper_bg(size, s):
    W, H = size
    c0, c1 = s["c"]
    img = vgrad(size, c0, c1)
    if s["nz"]:
        img = paper_noise(img, s["nz"])
    if s["bg"] in ("grid", "blueprint"):
        d = ImageDraw.Draw(img)
        if s["bg"] == "blueprint":
            line, step = _mix(c0, (255, 255, 255), 0.22), 50
        else:
            line, step = _mix(c0, s["ink"], 0.14), 40
        for x in range(0, W, step):
            d.line([(x, 0), (x, H)], fill=line, width=1)
        for y in range(0, H, step):
            d.line([(0, y), (W, y)], fill=line, width=1)
    return img


def make_paper(redacted=False, style="warm"):
    """学術論文風の研究資料。style で多テイスト（PAPER_STYLES参照）。
    redacted=Trueで核心を墨消し（教授の査読ギミック用）。"""
    W, H = 1000, 1414
    s = PAPER_STYLES[style]
    ink, accent, sub = s["ink"], s["acc"], s["sub"]
    f_ttl, f_hd, f_bd, f_ab = s["f"]
    img = _paper_bg((W, H), s)
    d = ImageDraw.Draw(img)
    M = 84
    colw = (W - M * 2 - 44) // 2
    lx, rx = M, M + colw + 44
    redactions = []

    # ヘッダ
    d.text((M, 34), "CLASSIFIED ── 内部資料 / 持出厳禁", font=F(f_bd, 20), fill=accent)
    rh, f_rh = "内部紀要  Vol.7 No.3", F(f_bd, 20)
    d.text((W - M - d.textlength(rh, font=f_rh), 34), rh, font=f_rh, fill=sub)
    d.line([(M, 64), (W - M, 64)], fill=sub, width=1)

    # タイトル
    ty = 100
    for i, line in enumerate(["観測者効果による認知崩壊の二経路モデル",
                              "── 共鳴経路と破壊経路の分岐条件について ──"]):
        f = F(f_ttl, 40 if i == 0 else 27)
        d.text(((W - d.textlength(line, font=f)) / 2, ty), line, font=f, fill=ink)
        ty += 56 if i == 0 else 46
    au, f_au = "霧島 透 ・ 朏 玲奈", F("goth_m", 23)
    d.text(((W - d.textlength(au, font=f_au)) / 2, ty + 8), au, font=f_au, fill=ink)
    af, f_af = "□□大学大学院 認知科学研究室", F(f_ab, 20)
    d.text(((W - d.textlength(af, font=f_af)) / 2, ty + 44), af, font=f_af, fill=sub)

    # Abstract
    ay, abh = ty + 92, 184
    d.rectangle([M, ay, W - M, ay + abh], outline=sub, width=1)
    d.text((M + 18, ay + 14), "Abstract", font=F(f_hd, 22), fill=ink)
    abst = ("本研究は、深層認知への直接干渉（観測）が対象の人格構造に及ぼす影響を、共鳴経路と"
            "破壊経路の二系統に分類し、両者を分岐させる臨界条件を定式化する。さらに観測主体の"
            "封じ込めに関する理論的基盤を提示し、依代への転写手順とその失敗時の挙動を論じる。")
    wrap_draw(d, (M + 18, ay + 52), abst, F(f_bd, 21), ink,
              (W - 2 * M - 36) // 21, 32)

    # 本文（2段組）
    body_top = ay + abh + 34
    f_h, f_b = F(f_hd, 25), F(f_bd, 22)
    mc, lh = colw // 22, 36

    def section(x, y, head, paras, redact_idx=()):
        d.text((x, y), head, font=f_h, fill=ink)
        y += 44
        for i, p in enumerate(paras):
            y0 = y
            y = wrap_draw(d, (x, y), p, f_b, ink, mc, lh)
            if i in redact_idx:
                redactions.append((x - 2, y0 - 2, x + colw + 2, y - 8))
            y += 14
        return y

    y = section(lx, body_top, "1. 序論", [
        "深層認知への直接的干渉、すなわち対象の内的表象を外部から観測する行為は、長らく"
        "理論上の可能性に留まってきた。第四世代観測機構の確立により、本現象は再現可能な"
        "実験対象となった。",
    ])
    section(lx, y, "2. 二経路モデル", [
        "観測対象に生じる反応は、共鳴経路と破壊経路の二系統に大別される。共鳴経路では"
        "観測者と被観測者の表象が部分的に同期し、人格の同一性は保持される。破壊経路では"
        "自己モデルが不可逆的に崩壊し、いわゆる廃人化に至る。",
        "両経路を分岐させる臨界条件は、観測深度が第三層を超え、かつ被観測者の防衛機制が"
        "一定閾値を下回った場合に破壊経路へ遷移する。臨界値は個体差が大きい。",
    ], redact_idx=(1,))

    y = section(rx, body_top, "3. 封じ込め手順", [
        "封じ込めは、観測主体を物理的依代へ転写し、外部刺激を遮断することで成立する。",
        "手順の核心は、依代に特定の符牒を刻み、認証鍵を生体情報と二重に束ねることにある。"
        "手順を誤れば主体は依代を離脱し、最も近い新たな器へ移動する。",
    ], redact_idx=(1,))
    y = section(rx, y, "4. 結論", [
        "本モデルは観測現象の制御可能性を理論的に保証する。ただし臨界条件の個体差に"
        "ついては追試を要する。",
    ])
    # 図プレースホルダ
    fy = y + 12
    d.rectangle([rx, fy, rx + colw, fy + 150], outline=sub, width=1)
    d.line([(rx, fy), (rx + colw, fy + 150)], fill=sub, width=1)
    d.line([(rx, fy + 150), (rx + colw, fy)], fill=sub, width=1)
    d.text((rx, fy + 158), "Fig.1 認知共鳴の模式図", font=F(f_bd, 18), fill=sub)

    # 墨消し（redactedのみ。明インク系は明バー、暗インク系は黒バー）
    if redacted:
        bar = _mix(s["c"][0], (255, 255, 255), 0.35) if sum(ink) > 380 else (16, 14, 12)
        for x0, y0, x1, y1 in redactions:
            d.rectangle([x0, y0, x1, y1], fill=bar)

    # フッタ＋スタンプ
    d.line([(M, H - 72), (W - M, H - 72)], fill=sub, width=1)
    d.text(((W - d.textlength("- 1 -", font=F(f_bd, 20))) / 2, H - 60),
           "- 1 -", font=F(f_bd, 20), fill=sub)
    stx, sang, scol = s["st"]
    st = stamp(stx, scol, 44, angle=sang)
    img = img.convert("RGBA")
    img.alpha_composite(st, (W - M - st.width, 74))
    return img.convert("RGB")


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    OUT = os.path.join(HERE, "outputs", "design")
    os.makedirs(OUT, exist_ok=True)

    # ============================================================
    # 採用デザイン（最終成果物）だけを出力する。
    # ファイル名 final_* が現在の確定版。中身（文面/題名）は仮サンプル。
    # 比較用コンタクト・不採用バリアント・探索物は出力しない
    #   （必要になったら上の make_*(variant=...) を呼び戻して再生成できる）。
    # ============================================================

    # ── 表（和紙＋朱／御札＋研究の融合） ──
    make_evidence_card_wa(   # 証拠カード（通常＝在地の含みは入れない）
        3, "観測機構 制御端末",
        "観察室の据置型コンソール。\n第四世代観測機構を制御する装置。\n起動ログの最終記録は施設封鎖の三日後。\n──封鎖された施設で、誰が触れた。",
        variant="ofuda", header="物的証拠").save(os.path.join(OUT, "final_front_evidence.png"))
    make_evidence_card_wa(   # 研究資料（固有デザイン＝藍枠の綴じ文書）＋末尾に「より詳しく…」の含み
        1, "二経路モデル",
        "認知崩壊の機序をめぐる内部研究資料。\n共鳴と破壊――二つの経路の記録。\n――詳しく調べれば、より多くの情報が得られる気がする。",
        variant="research", header="研究資料", prefix="R").save(os.path.join(OUT, "final_front_research.png"))
    make_shock_card(         # 衝撃証拠「灰と防護服」（一点物・暗転デザイン）＋末尾に「より詳しく…」の含み
        7, "灰と防護服",
        "隔離区画の隅に、防護服が一着。\n中身は、指でつまめるほどの灰だけ。\n他の先遣隊員とは、少し違う気がする。\n――詳しく調べれば、より多くの情報が得られる気がする。",
    ).save(os.path.join(OUT, "final_front_ash.png"))

    # ── 裏／固有マス（濃紺・民俗×研究の融合） ──
    make_card_back_wa("magatama_rw").save(os.path.join(OUT, "final_back_common.png"))  # 汎用裏＝紅白の勾玉
    make_back_safe("vault").save(os.path.join(OUT, "final_back_safe.png"))             # 金庫＝研究標本保管庫＋封印
    make_back_biodoor("shrine_tech").save(os.path.join(OUT, "final_back_biodoor.png")) # 生体扉＝注連縄鳥居＋走査装置

    # ── 研究論文（原本／墨消し・warm確定） ──
    make_paper(redacted=False, style="warm").save(os.path.join(OUT, "final_paper_full.png"))
    make_paper(redacted=True, style="warm").save(os.path.join(OUT, "final_paper_redacted.png"))

    # ── 採用一覧（カード6種を1枚で確認） ──
    overview = [("final_front_evidence.png", "表 証拠カード（御札+研究）"),
                ("final_front_research.png", "表 研究資料札（題名）"),
                ("final_front_ash.png", "表 灰と防護服（衝撃）"),
                ("final_back_common.png", "裏 汎用（紅白の勾玉）"),
                ("final_back_safe.png", "裏 金庫（標本保管庫＋封印）"),
                ("final_back_biodoor.png", "裏 生体認証扉（鳥居＋走査装置）")]
    _contact([os.path.join(OUT, f) for f, _l in overview], [l for _f, l in overview],
             cols=3, scale=0.40).save(os.path.join(OUT, "final_overview.png"))

    print("saved -> outputs/design/ : final_* (採用デザインのみ) + final_overview.png")
