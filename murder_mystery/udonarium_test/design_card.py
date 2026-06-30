# -*- coding: utf-8 -*-
"""
カードデザイン試作（A案：PIL作り込み）。
テーマ＝機密研究ファイルの「物的証拠タグ」。本体 build_udon.py とは独立。
確定したら make_card_front を差し替える。
"""
import os, tempfile, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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


def wrap_draw(d, xy, text, fnt, fill, max_w, line_h):
    x, y = xy
    for para in text.split("\n"):
        if not para:
            y += line_h
            continue
        line = ""
        for ch in para:
            test = line + ch
            if d.textlength(test, font=fnt) > max_w and line:
                d.text((x, y), line, font=fnt, fill=fill)
                y += line_h
                line = ch
            else:
                line = test
        if line:
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
    wrap_draw(d, (56, 282), body, F("goth_m", 27), (56, 51, 46), 488, 48)

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

    if variant == "vault":  # 鍵付き金庫＋封印（科学×民俗の融合）
        steel, gold, shu, line = (158, 168, 184), (200, 170, 104), (208, 78, 60), (224, 228, 236)
        bg = (16, 24, 36)
        img, d = _back_base((40, 50, 66), bg, line, shu, noise=2)
        # 金属キャビネット
        d.rectangle([cx - 156, 250, cx + 156, 566], outline=steel, width=4)
        d.rectangle([cx - 156, 250, cx + 156, 300], outline=steel, width=2)  # 銘板帯
        d.rectangle([cx - 120, 260, cx + 120, 292], fill=(232, 230, 224))    # 研究銘板（要素1つに集約）
        _centered(d, "機密保管庫", F("goth_b", 22), cx, 264, (40, 44, 52))
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
        _centered(d, "機密保管庫 ── 要開錠", F("goth_m", 23), cx, 690, gold)
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
    """固有マス『自動認証扉』の裏面。指紋ではなく『近づくと存在を照合し自動開放する扉』。
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

        # ── 老朽化レイヤー（経年劣化・ガッツリ） ──
        rng = random.Random(42)
        bg = (20, 28, 42)
        crack_c = _mix(stone, bg, 0.55)
        moss_c = _mix(stone, (45, 65, 35), 0.5)
        stain_c = _mix(stone, bg, 0.4)
        debris_c = _mix(stone, bg, 0.3)

        # 柱の大きなひび割れ
        for base_x in (cx - 118, cx + 118):
            for _ in range(8):
                y0 = rng.randint(200, 460)
                pts = [(base_x + rng.randint(-10, 10), y0)]
                for _ in range(rng.randint(3, 8)):
                    pts.append((pts[-1][0] + rng.randint(-12, 12),
                                pts[-1][1] + rng.randint(6, 24)))
                d.line(pts, fill=crack_c, width=rng.choice([1, 1, 2, 2, 3]))

        # 笠木・額束のひび
        for _ in range(6):
            x0 = rng.randint(cx - 170, cx + 170)
            y0 = rng.randint(168, 200)
            pts = [(x0, y0)]
            for _ in range(rng.randint(2, 6)):
                pts.append((pts[-1][0] + rng.randint(-16, 16),
                            pts[-1][1] + rng.randint(-5, 5)))
            d.line(pts, fill=crack_c, width=rng.choice([1, 2]))

        # 柱の欠け（下部が崩壊）
        for base_x, w in [(cx - 130, 24), (cx + 106, 24)]:
            for y0 in range(450, 472, 4):
                xoff = rng.randint(-4, 4)
                d.rectangle([base_x, y0, base_x + w, y0 + 3], fill=bg)
                rx0 = base_x + rng.randint(2, 8)
                rx1 = base_x + w - rng.randint(2, 8) + xoff
                if rx1 > rx0:
                    d.rectangle([rx0, y0, rx1, y0 + 2], fill=debris_c)

        # 水染み（縦方向の暗い筋）
        for _ in range(5):
            sx = rng.randint(cx - 170, cx + 170)
            sy = rng.randint(170, 260)
            for dy in range(0, rng.randint(60, 180), 3):
                sw = rng.randint(1, 4)
                d.line([(sx + rng.randint(-2, 2), sy + dy),
                        (sx + rng.randint(-2, 2), sy + dy + 3)],
                       fill=stain_c, width=sw)

        # 走査枠の破損（4角中2角を完全消去、1角を明滅）
        for x, y, sx, sy in [(cx + 176, 182, -1, 1), (cx - 176, 500, 1, -1)]:
            d.line([(x - 2, y - 2), (x + sx * 42, y - 2)], fill=bg, width=6)
            d.line([(x - 2, y - 2), (x - 2, y + sy * 42)], fill=bg, width=6)
        dim_a = _mix(bg, accent, 0.25)
        x, y, sx, sy = cx + 176, 500, -1, -1
        d.line([(x, y), (x + sx * 40, y)], fill=dim_a, width=2)
        d.line([(x, y), (x, y + sy * 40)], fill=dim_a, width=2)

        # 右電極ノードを消灯
        px_r = cx + 118
        d.ellipse([px_r - 9, 357, px_r + 9, 375], fill=bg)
        d.ellipse([px_r - 6, 360, px_r + 6, 372], outline=_mix(bg, stone, 0.2), width=1)
        d.line([(px_r - 7, 366), (px_r - 26, 366)], fill=bg, width=3)

        # 注連縄の劣化（垂れ下がった切れ端）
        rope_dark = _mix(rope, bg, 0.5)
        for _ in range(4):
            hx = rng.randint(cx - 140, cx + 140)
            hy = 266
            pts = [(hx, hy)]
            for _ in range(rng.randint(3, 6)):
                pts.append((pts[-1][0] + rng.randint(-4, 4),
                            pts[-1][1] + rng.randint(6, 14)))
            d.line(pts, fill=rope_dark, width=rng.choice([1, 2]))

        # 紙垂の破損（1枚を半分にする）
        d.rectangle([cx + 92, 282, cx + 120, 304], fill=bg)

        # 落下した石片・瓦礫
        for _ in range(18):
            dx = rng.randint(cx - 180, cx + 180)
            dy = rng.randint(480, 530)
            ds = rng.randint(2, 10)
            pts_d = [(dx, dy),
                     (dx + ds, dy + rng.randint(-3, 3)),
                     (dx + rng.randint(-2, ds), dy + rng.randint(2, ds // 2 + 3))]
            d.polygon(pts_d, fill=debris_c)

        # 土台のひび割れ
        for _ in range(4):
            x0 = rng.randint(cx - 145, cx + 145)
            d.line([(x0, 484), (x0 + rng.randint(-24, 24), 500)],
                   fill=crack_c, width=rng.choice([1, 2]))

        status = "▶ AUTH████  ██PLETE"

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
    _centered(d, "自動認証扉", F("mincho_b", 76), cx, 552, ink)
    _centered(d, "自動認証 ── 区画間制御", F("goth_m", 23), cx, 650, accent)
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

    # ── 統一テンプレート（ofuda / log / research 共通骨格）──
    _vtable = {
        "ofuda": dict(
            accent=(148, 68, 52), paper=((244, 238, 228), (232, 224, 212)),
            hdr_font="goth_b", body_font="goth_m", title_font="goth_b",
            meta="採取地点: 施設内   記録者: 調査員", stamp_text="秘",
            rule_tint=0.08),
        "log": dict(
            accent=(90, 96, 110), paper=((244, 242, 236), (234, 230, 222)),
            hdr_font="goth_b", body_font="ms_goth", title_font="goth_b",
            meta="文書種別: 施設記録   保管区分: 内部", stamp_text="機密",
            rule_tint=0.12),
        "research": dict(
            accent=(44, 62, 96), paper=((240, 242, 246), (228, 232, 238)),
            hdr_font="mincho_b", body_font="mincho", title_font="mincho_b",
            meta="分類: 内部紀要   査読: 要専門知識", stamp_text="資",
            rule_tint=0.10),
    }
    if variant in _vtable:
        v = _vtable[variant]
        ac = v["accent"]
        p0, p1 = v["paper"]
        rule_col = _mix(p1, ac, v["rule_tint"])
        img = vgrad((W, H), p0, p1)
        img = paper_noise(img, 3)
        d = ImageDraw.Draw(img)
        # 外枠（二重線）
        d.rectangle([14, 14, W - 14, H - 14], outline=ac, width=3)
        d.rectangle([20, 20, W - 20, H - 20], outline=_mix(p1, ac, 0.25), width=1)
        # 綴じ穴（左辺）
        for hy in (180, 380, 580):
            d.ellipse([26, hy - 12, 50, hy + 12], outline=ac, width=2)
            d.ellipse([30, hy - 8, 46, hy + 8], fill=_mix(p1, (180, 176, 168), 0.5))
        # 罫線（本文領域）
        for ry in range(290, H - 80, 40):
            d.line([(80, ry), (W - 40, ry)], fill=rule_col, width=1)
        # ヘッダ帯
        d.rectangle([60, 44, W - 40, 120], fill=ac)
        d.text((78, 56), header, font=F(v["hdr_font"], 38), fill=(236, 234, 228))
        no_s = "No. %s-%02d" % (prefix, no)
        fno = F("ms_goth", 22)
        nw = d.textlength(no_s, font=fno)
        d.text((W - 54 - nw, 74), no_s, font=fno,
               fill=tuple(min(255, c + 80) for c in ac))
        # 題
        d.text((80, 140), title, font=F(v["title_font"], 40), fill=sumi)
        d.line([(80, 206), (W - 40, 206)], fill=ac, width=2)
        # メタ行
        d.text((80, 216), v["meta"], font=F("ms_goth", 16),
               fill=_mix(p1, sumi, 0.4))
        # 本文
        wrap_draw(d, (80, 262), body, F(v["body_font"], 25),
                  (48, 42, 38), 480, 40)
        # スタンプ（右下・傾き）
        img = img.convert("RGBA")
        st = stamp(v["stamp_text"], (shu[0], shu[1], shu[2], 120), 38, angle=-8)
        img.alpha_composite(st, (W - 170, H - 180))
        d = ImageDraw.Draw(img)
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
        wrap_draw(d, (56, 286), body, F("goth_m", 27), (54, 47, 43), 488, 48)
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
    """衝撃証拠カード。統一テンプレートと同じ骨格だが色調が暗転＋構造が焦げている。
    「同じ書式のはずなのに何かがおかしい」で不気味さを出す。"""
    W, H = 600, 840
    sumi = (40, 33, 29)
    shu = (188, 54, 44)
    ash = (208, 201, 188)
    ember = (128, 36, 32)
    suit = (150, 159, 170)

    # ── 背景：焦げた紙（統一テンプレートの紙が焼けた形） ──
    p0, p1 = (62, 56, 50), (32, 28, 24)
    img = vgrad((W, H), p0, p1)
    img = paper_noise(img, 4)
    img = img.convert("RGBA")
    # 四隅の焦げ滲み
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

    # ── 統一テンプレートと同じ構造要素（暗転色） ──
    # 外枠（二重線）— 通常と同じ位置だが色が焦げている
    d.rectangle([14, 14, W - 14, H - 14], outline=ember, width=3)
    d.rectangle([20, 20, W - 20, H - 20], outline=_mix(p1, ember, 0.25), width=1)
    # 綴じ穴（左辺）— 穴の周囲が焦げている
    for hy in (180, 380, 580):
        d.ellipse([26, hy - 12, 50, hy + 12], outline=ember, width=2)
        d.ellipse([30, hy - 8, 46, hy + 8], fill=_mix(p1, (20, 16, 12), 0.6))
    # 罫線 — 途中で途切れる（焼失）
    rule_col = _mix(p1, ember, 0.15)
    rnd_rule = random.Random(77)
    for ry in range(290, H - 80, 40):
        cut = rnd_rule.randint(W // 3, W - 80)
        d.line([(80, ry), (cut, ry)], fill=rule_col, width=1)
    # ヘッダ帯 — 暗赤（通常テンプレートと同じ位置 [60,44]-[W-40,120]）
    d.rectangle([60, 44, W - 40, 120], fill=ember)
    d.text((78, 56), header, font=F("goth_b", 38), fill=ash)
    no_s = "No. %s-%02d" % (prefix, no)
    fno = F("ms_goth", 22)
    nw = d.textlength(no_s, font=fno)
    d.text((W - 54 - nw, 74), no_s, font=fno, fill=(206, 150, 148))
    # 題 — 同じ位置
    d.text((80, 140), title, font=F("goth_b", 40), fill=ash)
    d.line([(80, 206), (W - 40, 206)], fill=ember, width=2)
    # メタ行
    d.text((80, 216), "状態: 異常   保管区分: ──",
           font=F("ms_goth", 16), fill=_mix(p1, ash, 0.4))

    # ── イラスト（灰の塊 — 人型なし） ──
    cx = W // 2
    pile = random.Random(5)
    # 灰の山 — 底部から積み上げる不定形の楕円群
    for i in range(10):
        y_c = 490 - i * 20
        w_h = 110 - i * 6
        h_h = 22 - i
        g = 95 + i * 8
        d.ellipse([cx - w_h, y_c - h_h, cx + w_h, y_c + h_h],
                  fill=(g, g - 6, g - 16))
    # 表面の粒子 — 不規則に散る灰
    for _ in range(200):
        py = pile.randint(310, 510)
        max_spread = 30 + (py - 300) * 0.58
        px = cx + pile.uniform(-max_spread, max_spread)
        r = pile.uniform(5, 16)
        g = pile.randint(105, 190)
        d.ellipse([px - r, py - r * 0.6, px + r, py + r * 0.6],
                  fill=(g, g - 6, g - 16))
    # 浮遊する塵 — 上方に漂う微粒子
    for _ in range(70):
        px = cx + pile.uniform(-100, 100)
        py = pile.randint(250, 350)
        r = pile.uniform(1, 4)
        g = pile.randint(150, 215)
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=(g, g - 4, g - 12))
    # 内部の残り火 — 灰の中に微かに赤い粒
    for _ in range(12):
        px = cx + pile.uniform(-60, 60)
        py = pile.randint(410, 480)
        r = pile.uniform(2, 6)
        eg = pile.randint(30, 50)
        d.ellipse([px - r, py - r * 0.5, px + r, py + r * 0.5],
                  fill=(ember[0] - eg, ember[1] - eg, ember[2] - eg))

    # ── 本文（統一テンプレートと同じフォントサイズ） ──
    wrap_draw(d, (80, 560), body, F("goth_m", 25), ash, 480, 40)

    # スタンプ（右下・傾き — 統一テンプレートと同じ位置）
    st = stamp("要検証", (shu[0], shu[1], shu[2], 150), 38, angle=-8)
    img.alpha_composite(st, (W - 170, H - 180))

    # フッタ
    d = ImageDraw.Draw(img)
    foot = "地下研究施設 ── 調査記録"
    f_ft = F("goth_m", 20)
    d.text(((W - d.textlength(foot, font=f_ft)) / 2, H - 56), foot,
           font=f_ft, fill=(150, 120, 112))
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


def draw_table(d, x, y, headers, rows, colw, ink, accent, sub, f_hd_key, f_bd_key):
    n = len(headers)
    cw = colw // n
    cell_h = 32
    f_h = F(f_hd_key, 18)
    f_b = F(f_bd_key, 16)
    # ヘッダ行
    for i, h in enumerate(headers):
        cx = x + i * cw
        d.rectangle([cx, y, cx + cw, y + cell_h], fill=accent, outline=sub, width=1)
        light = (240, 235, 228)
        d.text((cx + 8, y + 6), h, font=f_h, fill=light)
    y += cell_h
    # データ行
    for ri, row in enumerate(rows):
        row_bg = (232, 228, 218) if ri % 2 == 0 else None
        for i, cell in enumerate(row):
            cx = x + i * cw
            if row_bg:
                d.rectangle([cx, y, cx + cw, y + cell_h], fill=row_bg, outline=sub, width=1)
            else:
                d.rectangle([cx, y, cx + cw, y + cell_h], outline=sub, width=1)
            d.text((cx + 8, y + 6), cell, font=f_b, fill=ink)
        y += cell_h
    return y


def draw_branch_diagram(d, x, y, colw, ink, accent, sub):
    f_b = F("mincho", 18)
    cx = x + colw // 2
    top_y = y + 10
    # 「覗き込み」ラベル
    label = "覗き込み"
    lw = int(d.textlength(label, font=f_b))
    d.text((cx - lw // 2, top_y), label, font=f_b, fill=ink)
    # 垂直線
    stem_y1 = top_y + 24
    stem_y2 = stem_y1 + 20
    d.line([(cx, stem_y1), (cx, stem_y2)], fill=sub, width=2)
    # 水平分岐線
    lbx = x + colw // 4
    rbx = x + 3 * colw // 4
    branch_y = stem_y2
    d.line([(lbx, branch_y), (rbx, branch_y)], fill=sub, width=2)
    # 左右の垂直線
    box_top = branch_y + 18
    d.line([(lbx, branch_y), (lbx, box_top)], fill=sub, width=2)
    d.line([(rbx, branch_y), (rbx, box_top)], fill=sub, width=2)
    # 矢印（▼）
    for bx in (lbx, rbx):
        d.polygon([(bx - 6, box_top - 8), (bx + 6, box_top - 8), (bx, box_top)], fill=sub)
    # 左ボックス（共鳴経路）
    green_muted = (80, 110, 80)
    bw = colw // 2 - 14
    bh = 32
    lbx0 = lbx - bw // 2
    d.rounded_rectangle([lbx0, box_top, lbx0 + bw, box_top + bh], radius=6, outline=green_muted, width=2)
    lbl_l = "【共鳴経路】"
    lw2 = int(d.textlength(lbl_l, font=f_b))
    d.text((lbx - lw2 // 2, box_top + 8), lbl_l, font=f_b, fill=green_muted)
    # 右ボックス（破壊経路）
    rbx0 = rbx - bw // 2
    d.rounded_rectangle([rbx0, box_top, rbx0 + bw, box_top + bh], radius=6, outline=accent, width=2)
    lbl_r = "【破壊経路】"
    rw2 = int(d.textlength(lbl_r, font=f_b))
    d.text((rbx - rw2 // 2, box_top + 8), lbl_r, font=f_b, fill=accent)
    # サブラベル行1
    sub_y1 = box_top + bh + 8
    sub_l1 = "器を保つ(同期)"
    sub_r1 = "器を壊す(崩壊)"
    sw = int(d.textlength(sub_l1, font=f_b))
    d.text((lbx - sw // 2, sub_y1), sub_l1, font=f_b, fill=green_muted)
    sw2 = int(d.textlength(sub_r1, font=f_b))
    d.text((rbx - sw2 // 2, sub_y1), sub_r1, font=f_b, fill=accent)
    # 末端ラベル
    sub_y2 = sub_y1 + 24
    sub_l2 = "〈成熟した個体〉"
    sub_r2 = "〈未成熟な個体〉"
    sw3 = int(d.textlength(sub_l2, font=f_b))
    d.text((lbx - sw3 // 2, sub_y2), sub_l2, font=f_b, fill=green_muted)
    sw4 = int(d.textlength(sub_r2, font=f_b))
    d.text((rbx - sw4 // 2, sub_y2), sub_r2, font=f_b, fill=accent)
    return sub_y2 + 24


def draw_numbered_list(d, x, y, items, colw, ink, f_bd_key, lh=36,
                       accent=None, f_hd_key=None):
    f_n = F(f_hd_key or f_bd_key, 22)
    f_b = F(f_bd_key, 20)
    indent = 38
    mc = colw - indent
    num_col = accent or ink
    for i, item in enumerate(items, 1):
        y0 = y
        d.text((x + 6, y), f"{i}.", font=f_n, fill=num_col)
        y = wrap_draw(d, (x + indent, y), item, f_b, ink, mc, lh)
        if accent:
            d.line([(x, y0 + 4), (x, y0 + lh - 6)], fill=accent, width=3)
        y += 8
    return y


def draw_warning_box(d, x, y, title, lines, colw, accent, ink, f_hd_key, f_bd_key):
    pad = 16
    f_h = F(f_hd_key, 22)
    f_b = F(f_bd_key, 20)
    lh = 30
    # 高さを計算
    content_h = 36 + len(lines) * lh + pad
    box_h = content_h + pad * 2
    # 外枠
    d.rectangle([x, y, x + colw, y + box_h], outline=accent, width=3)
    # 内枠（4px オフセット）
    d.rectangle([x + 4, y + 4, x + colw - 4, y + box_h - 4], outline=accent, width=1)
    # タイトル
    d.text((x + pad, y + pad), title, font=f_h, fill=accent)
    # 本文
    ty = y + pad + 36
    mc = colw - pad * 2
    for line in lines:
        wrap_draw(d, (x + pad, ty), line, f_b, ink, mc, lh)
        ty += lh
    return y + box_h + 10


def draw_footnotes(d, x, y, notes, W, M, sub, f_bd_key, highlight_indices=None, highlight_color=None):
    f_b = F(f_bd_key, 16)
    f_b_bold = F("mincho_b", 17)
    d.line([(M, y), (W - M, y)], fill=sub, width=1)
    y += 8
    for i, note in enumerate(notes):
        if highlight_indices and i in highlight_indices and highlight_color:
            tw = d.textlength(note, font=f_b_bold)
            d.rectangle([(M - 2, y - 1), (M + tw + 4, y + 19)], fill=(255, 248, 240))
            d.text((M, y), note, font=f_b_bold, fill=highlight_color)
            d.line([(M, y + 20), (M + tw, y + 20)], fill=highlight_color, width=1)
        else:
            d.text((M, y), note, font=f_b, fill=sub)
        y += 24
    return y + 6


def draw_margin_note(img, x, y, text, ink, f_bd_key, angle=-5):
    f = F("goth_m", 19)
    note_color = _mix(ink, (150, 36, 38), 0.5)
    # テキストサイズ計算
    tmp_d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    lines = text.split("\n")
    max_w = max(int(tmp_d.textlength(l, font=f)) for l in lines) + 20
    note_h = len(lines) * 26 + 10
    # 透明レイヤー
    layer = Image.new("RGBA", (max_w, note_h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i, line in enumerate(lines):
        ld.text((10, i * 26 + 5), line, font=f, fill=(*note_color, 230))
    rotated = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(rotated, (x, y))
    return img_rgba.convert("RGB")


def make_paper(paper_id=1, redacted=False, style="warm"):
    """学術論文風の研究資料。paper_id で4本の論文を切り替え。
    redacted=True で核心を墨消し。"""
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
    f_h, f_b = F(f_hd, 25), F(f_bd, 22)
    mc, lh = colw, 36

    # ── ヘッダ ──
    d.text((M, 34), "CLASSIFIED ── 内部資料 / 持出厳禁", font=F(f_bd, 20), fill=accent)
    if paper_id == 4:
        rh_text = "管理文書 CLO-003-R3"
    elif paper_id == 1:
        rh_text = "内部紀要  Vol.7 No.3"
    elif paper_id == 2:
        rh_text = "内部紀要  Vol.7 No.4"
    else:
        rh_text = "内部紀要  Vol.8 No.1"
    f_rh = F(f_bd, 20)
    d.text((W - M - d.textlength(rh_text, font=f_rh), 34), rh_text, font=f_rh, fill=sub)
    d.line([(M, 64), (W - M, 64)], fill=sub, width=1)

    # ── タイトルブロック ──
    paper_meta = {
        1: {
            "title": "覗き込み現象の段階的記録",
            "subtitle": "── 周辺集落における同型症例との対照分析 ──",
            "author": "○○ ○ ・ ○○ ○○",
            "affiliation": "深層認知研究部門",
        },
        2: {
            "title": "観測者効果による認知崩壊の二経路モデル",
            "subtitle": "── 共鳴経路と破壊経路の分岐条件について ──",
            "author": "○○ ○ ・ ○○ ○○",
            "affiliation": "深層認知研究部門",
        },
        3: {
            "title": "収容個体の形質比較",
            "subtitle": "── 発達段階仮説に基づく脱走事案の事後分析 ──",
            "author": "○○ ○○",
            "affiliation": "管理記録部門",
        },
        4: {
            "title": "施設閉鎖手順書（改訂第三版）",
            "subtitle": "── 封じ込め機構と自動認証扉の運用指針 ──",
            "author": "管理部門",
            "affiliation": "文書番号 CLO-003-R3",
        },
    }
    meta = paper_meta[paper_id]
    ty = 100
    for i, line in enumerate([meta["title"], meta["subtitle"]]):
        f = F(f_ttl, 40 if i == 0 else 27)
        d.text(((W - d.textlength(line, font=f)) / 2, ty), line, font=f, fill=ink)
        ty += 56 if i == 0 else 46
    au, f_au = meta["author"], F("goth_m", 23)
    d.text(((W - d.textlength(au, font=f_au)) / 2, ty + 8), au, font=f_au, fill=ink)
    af, f_af = meta["affiliation"], F(f_ab, 20)
    d.text(((W - d.textlength(af, font=f_af)) / 2, ty + 44), af, font=f_af, fill=sub)

    # ── Abstract ──
    abstracts = {
        1: ("本稿は○○県御影村に伝わる「魂抜き」伝承と収容環境下で再現された覗き込み現象を対照し、"
            "段階的崩壊機序を記録する。求心力の漸減に基づく四段階分類を提案し、当該伝承との整合性を検証する。"),
        2: ("深層認知への直接干渉が対象に及ぼす影響は一様ではなく、共鳴経路と破壊経路の二系統に分類"
            "される。本稿ではこの分岐条件を論じ、観測主体の発達段階が決定因子であることを示す。"),
        3: ("当施設が収容した二体の上位観測体（個体α・個体β）の形質を比較し、発達段階仮説との"
            "整合性を検証する。個体αの脱走事案を事後分析し、今後の管理方針を提言する。"),
        4: ("本手順書は施設閉鎖時の封じ込め手順および自動認証扉の運用指針を規定する。"
            "担当者は全手順を熟知し、対象の誤認防止に細心の注意を払うこと。"),
    }
    ay, abh = ty + 92, 148
    d.rectangle([M, ay, W - M, ay + abh], outline=sub, width=1)
    d.text((M + 18, ay + 14), "Abstract", font=F(f_hd, 22), fill=ink)
    wrap_draw(d, (M + 18, ay + 50), abstracts[paper_id], F(f_bd, 20), ink,
              W - 2 * M - 36, 30)

    body_top = ay + abh + 34

    # ── 本文（2段組）──
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

    # ── 論文ごとのレイアウト ──
    if paper_id == 1:
        # 左列
        y_l = section(lx, body_top, "1. 序論", [
            "○○県御影村には「魂を抜かれた」と語り継がれる症例が散発してきた。"
            "外傷を伴わない精神変調に始まり、重篤例では廃人に至る。本報は収容"
            "環境下の同現象を記録し、当該伝承との整合性を検証する。",
        ])
        d.text((lx, y_l), "2. 段階記録", font=f_h, fill=ink)
        y_l += 44
        y_l = draw_table(d, lx, y_l,
                         ["段階", "求心力", "状態", "集落対応"],
                         [["Ⅰ", "高", "精神不安定", "軽症例"],
                          ["Ⅱ", "低", "自意識喪失", "重症例"],
                          ["Ⅲ", "零", "器の崩壊", "神隠し伝承"],
                          ["？", "──", "灰のみ残存", "該当なし"]],
                         colw, ink, accent, sub, f_hd, f_bd)
        y_l += 14
        pub_para = "段階Ⅰ〜Ⅲは求心力の漸減に沿った連続的経過で、集落症例と対応する。両者は同一機序と結論する。"
        y_l = wrap_draw(d, (lx, y_l), pub_para, f_b, ink, mc, lh)
        y_l += 14
        redact_para_real = ("段階「？」の個体は質的に異なる所見を示す。他の崩壊体は人のフォルムを残すが、当該個体は"
                            "ほぼ灰のみが残存し、装備だけが原形を保っていた。これは観測体が身体を「依代」として"
                            "使用し尽くした──器の求心力を完全に搾取した痕跡である。")
        redact_para_dummy = ("第四分類の残骸は先行三段階と有意に異なるΔG値を示した（p<0.01, n=3）。"
                             "高次構造の脱凝集率は99.2%に達し、外装具のみが原形を維持する。"
                             "ψ場の終末相におけるエネルギー収支との整合性が示唆される。")
        p1_r = redact_para_dummy if redacted else redact_para_real
        y0r = y_l
        y_l = wrap_draw(d, (lx, y_l), p1_r, f_b, ink, mc, lh)
        redactions.append((lx - 2, y0r - 2, lx + colw + 2, y_l - 8))
        # 右列
        y_r = section(rx, body_top, "3. 所見", [
            "覗き込みは対象の求心力を段階的かつ不可逆的に奪う現象であり、集落に伝わる「魂抜き」と"
            "同一の機序であることが裏付けられた。ただし、灰のみ残存する段階は単なる覗き込みとは"
            "質的に異なり、観測体の利用形態に起因すると考えられる。依代転用と二経路の関係は、"
            "本紀要 Vol.7 No.4 を参照されたし。",
        ])

    elif paper_id == 2:
        # 左列
        y_l = section(lx, body_top, "1. 序論", [
            "深層認知への直接干渉（覗き込み）が対象に及ぼす影響は一様ではない。前報*2 で段階的崩壊を"
            "記録したが、一部の事例では対象の認知構造が保持されたまま同期現象が観測された。本稿では、"
            "この二種の反応を経路として分類し、分岐条件を論じる。",
        ])
        y_l = section(lx, y_l, "2. 求心力の定義", [
            "自意識を器（肉体）に繋ぎ止める力が存在する。外部研究*1 の「自己モデルの統合強度」に"
            "相当する概念であり、本稿ではこれを「求心力」と定義する。人間はこの力を有するが、"
            "上位観測体はこれを持たない──すなわち「空洞」である。空洞同士は互いを感知するが、"
            "人間にはこの差異を知覚できない。",
        ])
        # 右列
        d.text((rx, body_top), "3. 二経路の分岐", font=f_h, fill=ink)
        y_r = body_top + 44
        redact_3_real = ("覗き込みによる相互作用は二経路に分岐する。共鳴経路では観測者と被験体の認知表象が"
                         "部分的に同期し、求心力は保持される。破壊経路では被験体の自己モデルが不可逆的に崩壊し、"
                         "求心力が喪失する。分岐条件は観測主体の発達段階に依存する──成熟した個体は共鳴を、"
                         "未成熟な個体は破壊を引き起こす。")
        redact_3_dummy = ("深層認知干渉の応答関数f(ψ,τ)は特異点τ*で不連続な分岐を示す。"
                          "第一系列ではコヒーレンス長が閾値Lcを超え位相同期が成立、"
                          "第二系列ではデコヒーレンス速度が発散し非可逆遷移を起こす。"
                          "分岐はη指標に依存し、η≧η_cで第一系列が選択される。")
        p2_r = redact_3_dummy if redacted else redact_3_real
        y0r = y_r
        y_r = wrap_draw(d, (rx, y_r), p2_r, f_b, ink, mc, lh)
        redactions.append((rx - 2, y0r - 2, rx + colw + 2, y_r - 8))
        y_r += 14
        y_r = section(rx, y_r, "4. 考察", [
            "二経路の存在は、観測体が均質な脅威ではないことを意味する。共鳴型は無害で、"
            "破壊型のみが封じ込め対象となる。この区別を欠けば無害な個体への過誤が生じうる。"
            "今後は分岐条件の定量化と個体差の解明が求められる。",
        ])
        y_r = draw_branch_diagram(d, rx, y_r + 10, colw, ink, accent, sub)
        # 脚注
        fn_y = max(y_r + 16, H - 140)
        draw_footnotes(d, lx, fn_y,
                       ["*1 ○○（○○大学 認知科学専攻教授）「自己モデルの統合と離散」",
                        "*2 ○○・○○「覗き込み現象の段階的記録」本紀要 Vol.7 No.3"],
                       W, M, sub, f_bd,
                       highlight_indices={0}, highlight_color=accent)

    elif paper_id == 3:
        # 左列
        y_l = section(lx, body_top, "1. 収容経緯", [
            "当施設は設立以来、計2体の上位観測体を収容した。個体αは自発的に接触し研究協力の"
            "意思を示した。個体βは激しい抵抗を示したが、制圧のうえ収容に至った。両者の覗き込みの"
            "様態には顕著な差異が認められた。",
        ])
        d.text((lx, y_l), "2. 個体比較", font=f_h, fill=ink)
        y_l += 44
        y_l = draw_table(d, lx, y_l,
                         ["項目", "個体α", "個体β"],
                         [["擬態", "安定・長期維持", "不安定・摩耗"],
                          ["覗き込み", "認知を保持", "認知を崩壊"],
                          ["精神変調", "軽微", "周囲に発生"],
                          ["器の由来", "自己形成体", "他者から転用"],
                          ["現状", "脱走", "封印中"]],
                         colw, ink, accent, sub, f_hd, f_bd)
        y_l += 14
        after_table = "両者は求心力走査において同じく「空洞」を示すが、覗き込みの帰結が正反対である。"
        y_l = wrap_draw(d, (lx, y_l), after_table, f_b, ink, mc, lh)
        # 右列
        d.text((rx, body_top), "3. 発達段階仮説", font=f_h, fill=ink)
        y_r = body_top + 44
        redact_p1_real = ("二経路モデルの分岐条件を個体差に適用する。個体αは成熟を全うし自発的に器を"
                          "形成した個体であり──諸神話における「受肉」に相当する過程である。覗き込みは共鳴"
                          "経路を取り、器を壊さず人間との共存が成立する。個体βは成熟を経ず自前の器を持たない"
                          "個体であり、他者の器を奪って擬態する。覗き込みは破壊経路を取る。")
        redact_p2_real = ("脱走した個体αは共鳴型──器を保つ側であり、脱走後に覗き込み被害は確認されていない。"
                          "封印下にある個体βが破壊型──器を壊す側であり、崩壊症例の原因個体と結論する。")
        redact_p1_dummy = ("前報の分岐条件をη指標に基づき個体水準に適用する。個体αはη値が"
                           "臨界値η_cを超過し（η_α=4.72）、自発的相転移により安定構造を形成"
                           "したと推定される。第一系列選択性が確認された。個体βはη_β<η_cであり、"
                           "外部基質からの構造借用による準安定状態を維持する。")
        redact_p2_dummy = ("個体αは第一系列選択体であり、逸脱後のモニタリングでΔG異常は未検出。"
                           "個体βは第二系列選択体であり、直近の計測でδ(ψ)の発散傾向が認められた。")
        p3_r1 = redact_p1_dummy if redacted else redact_p1_real
        p3_r2 = redact_p2_dummy if redacted else redact_p2_real
        y0r1 = y_r
        y_r = wrap_draw(d, (rx, y_r), p3_r1, f_b, ink, mc, lh)
        redactions.append((rx - 2, y0r1 - 2, rx + colw + 2, y_r - 8))
        y_r += 14
        y0r2 = y_r
        y_r = wrap_draw(d, (rx, y_r), p3_r2, f_b, ink, mc, lh)
        redactions.append((rx - 2, y0r2 - 2, rx + colw + 2, y_r - 8))
        y_r += 14
        y_r = section(rx, y_r, "4. 脱走事案", [
            "個体αは保安手順の不備により収容区画から逸脱し、擬態状態のまま施設外へ逃走した。追跡は"
            "当日中に打ち切られた。再侵入への警戒を継続すること。",
        ])

    elif paper_id == 4:
        # 左列
        y_l = section(lx, body_top, "1. 閉鎖の目的", [
            "施設閉鎖は、収容個体の逸脱または未登録の上位観測体の侵入検知時に発動する。本施設の"
            "安全機構は二層で構成される──外周封鎖（全出入口の遮断）と、施設内部の自動認証扉"
            "（区画間の通行制御）である。閉鎖発動時、外周は自動封鎖され、解除には封印の完了が"
            "必要となる。",
        ])
        d.text((lx, y_l), "2. 封印実行手順", font=f_h, fill=ink)
        y_l += 44
        y_l = draw_numbered_list(d, lx, y_l,
                                 ["施設全域の出入口を封鎖",
                                  "封印装置の起動確認（所在: 最奥区画）",
                                  "対象個体を特定・確保",
                                  "対象を封印装置まで誘導",
                                  "電極デバイスを装着、意識転写を実行",
                                  "転写完了を確認 → ロック解除"],
                                 colw, ink, f_bd, lh=34,
                                 accent=accent, f_hd_key=f_hd)
        # 右列
        d.text((rx, body_top), "3. 自動認証扉（区画間制御）", font=f_h, fill=ink)
        y_r = body_top + 44
        redact_3_real = ("施設内部の各区画間に設置された自動認証扉は、通行制御と上位観測体の感測を"
                         "兼ねる。接近者の求心力を走査し、正常値（人間）検出時はロック維持、零値（空洞）"
                         "検出時にのみ開放する。開放方向は外周から最奥区画への一方向に限定され、"
                         "対象を封印装置へ段階的に誘導する設計である。擬態状態でも空洞検知は有効に"
                         "作動し、接近した上位観測体を特定する手がかりとなる。")
        redact_3_dummy = ("区画間遷移制御機構（ISTC）は生体インピーダンス分光法に基づく"
                          "ψ場走査モジュールを内蔵する。走査閾値はZψ=0.00±0.02に設定され、"
                          "Zψ>0.15検出時はFail-Secureモードを維持する。トランジット・ベクトルは"
                          "外周→中核の単方向制約であり、Rev.3で走査精度が改善された。")
        p4_r = redact_3_dummy if redacted else redact_3_real
        y0r = y_r
        y_r = wrap_draw(d, (rx, y_r), p4_r, f_b, ink, mc, lh)
        redactions.append((rx - 2, y0r - 2, rx + colw + 2, y_r - 8))
        y_r += 20
        y_r = draw_warning_box(d, rx, y_r, "注 意",
                               ["封印装置は上位観測体専用ではない。",
                                "人間に使用した場合にも意識が抽出され、",
                                "対象は不可逆的に廃人化する。",
                                "対象の誤認は取り返しのつかない結果を招く。"],
                               colw, accent, ink, f_hd, f_bd)

    # ── モザイク＋薄靄（未査読領域） ──
    if redacted and redactions:
        for x0, y0, x1, y1 in redactions:
            rw, rh = x1 - x0, y1 - y0
            if rw < 4 or rh < 4:
                continue
            region = img.crop((x0, y0, x1, y1))
            # モザイク: 1/16に縮小→NEAREST拡大（粗いブロック）
            sw, sh = max(1, rw // 16), max(1, rh // 16)
            mosaic = region.resize((sw, sh), Image.BILINEAR).resize((rw, rh), Image.NEAREST)
            # 薄い靄を上乗せ（背景色寄りのベール）
            mist_base = s["c"][0]
            veil = Image.new("RGBA", (rw, rh), (*mist_base, 40))
            mosaic = mosaic.convert("RGBA")
            mosaic.alpha_composite(veil)
            img = img.convert("RGBA")
            img.paste(mosaic.convert("RGB"), (x0, y0))
        d = ImageDraw.Draw(img)

    # ── フッタ ──
    d.line([(M, H - 72), (W - M, H - 72)], fill=sub, width=1)
    d.text(((W - d.textlength("- 1 -", font=F(f_bd, 20))) / 2, H - 60),
           "- 1 -", font=F(f_bd, 20), fill=sub)

    # ── スタンプ ──
    stamp_text = "未査読" if redacted else ("管理" if paper_id == 4 else s["st"][0])
    stamp_angle = s["st"][1]
    stamp_col = s["st"][2]
    st = stamp(stamp_text, stamp_col, 44, angle=stamp_angle)
    img = img.convert("RGBA")
    img.alpha_composite(st, (W - M - st.width, 74))

    # ── 余白メモ（論文③のみ）──
    if paper_id == 3:
        img = img.convert("RGB")
        img = draw_margin_note(img, rx + colw - 200, y_r + 6,
                               "αの所在は不明──\n危険度はβに比して低いが\n放置してよいのか？",
                               ink, f_bd, angle=-5)
        return img

    return img.convert("RGB")


def make_board(zones=True):
    """テーブル背景ボード。1920×1200。地下研究施設内部＋民俗学モチーフ。"""
    W, H = 1920, 1200
    bg0, bg1 = (18, 22, 34), (6, 8, 16)
    shu = (208, 86, 60)
    gold = (202, 170, 104)
    line = (190, 196, 210)
    steel = (80, 88, 106)
    dim = _mix(bg0, line, 0.08)
    rope = (200, 178, 120)

    img = vgrad((W, H), bg0, bg1)
    img = paper_noise(img, 3, seed=42)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # ── 研究所の壁面テクスチャ ──
    rnd = random.Random(77)
    pipe_col = _mix(bg0, steel, 0.35)
    pipe_hi = _mix(bg0, steel, 0.55)
    pipe_dk = _mix(bg0, steel, 0.20)
    rivet = _mix(bg0, steel, 0.45)

    # 主グリッド（床タイル）
    for x in range(0, W, 64):
        d.line([(x, 0), (x, H)], fill=dim, width=1)
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=dim, width=1)
    # タイル目地の交差点にアンカーボルト
    for x in range(0, W, 256):
        for y in range(0, H, 192):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=rivet)

    # 天井配管ラック（上部 3本束）
    for py in (76, 90, 104):
        d.line([(0, py), (W, py)], fill=pipe_col, width=5)
        d.line([(0, py - 2), (W, py - 2)], fill=pipe_hi, width=1)
        d.line([(0, py + 2), (W, py + 2)], fill=pipe_dk, width=1)
    # 配管ラックのブラケット（一定間隔の吊り金具）
    for bx in range(120, W, 240):
        d.rectangle([bx - 3, 70, bx + 3, 110], fill=pipe_col, outline=pipe_hi, width=1)
        d.ellipse([bx - 4, 68, bx + 4, 74], fill=rivet)
    # ダクト（天井帯）
    d.rectangle([0, 112, W, 124], fill=_mix(bg0, steel, 0.16))
    for x in range(0, W, 24):
        d.rectangle([x, 113, x + 12, 123], fill=_mix(bg0, steel, 0.26))
    # ケーブルトレイ（天井下）
    ct_y = 128
    d.line([(0, ct_y), (W, ct_y)], fill=pipe_dk, width=2)
    d.line([(0, ct_y + 6), (W, ct_y + 6)], fill=pipe_dk, width=2)
    for x in range(0, W, 40):
        d.line([(x, ct_y), (x, ct_y + 6)], fill=pipe_dk, width=1)

    # 縦配管（左右壁面 各3本）
    for px in (22, 38, 54, W - 22, W - 38, W - 54):
        d.line([(px, 0), (px, H)], fill=pipe_col, width=4)
        d.line([(px - 2, 0), (px - 2, H)], fill=pipe_hi, width=1)
        d.line([(px + 2, 0), (px + 2, H)], fill=pipe_dk, width=1)
    # 配管ジョイント（縦×横の交差）
    for px in (22, 38, 54, W - 22, W - 38, W - 54):
        for py in (76, 90, 104):
            d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=pipe_col, outline=pipe_hi, width=1)
    # 縦配管のバルブ（ランダム位置）
    for px in (38, W - 38):
        for vy in range(200, H - 60, 280):
            vy2 = vy + rnd.randint(-30, 30)
            d.rectangle([px - 10, vy2, px + 10, vy2 + 16], fill=pipe_col, outline=pipe_hi, width=1)
            d.line([(px - 14, vy2 + 8), (px - 10, vy2 + 8)], fill=shu, width=2)

    # 壁面計器パネル（アナログゲージ・バーグラフ・目盛り）
    gauge_bg = _mix(bg0, steel, 0.12)
    gauge_line = _mix(bg0, steel, 0.40)
    gauge_fill = _mix(bg0, (60, 180, 120), 0.25)
    gauge_warn = _mix(bg0, shu, 0.30)
    for side_x in (72, W - 72):
        for py in range(160, H - 60, 130):
            pw, ph = 34, 60
            px0 = side_x - pw // 2
            d.rectangle([px0, py, px0 + pw, py + ph], fill=gauge_bg, outline=gauge_line, width=1)
            # ゲージタイプをランダム選択
            gtype = rnd.choice(["arc", "bar", "bar"])
            if gtype == "arc":
                gcx, gcy = px0 + pw // 2, py + 28
                gr = 12
                d.arc([gcx - gr, gcy - gr, gcx + gr, gcy + gr], 200, 340,
                      fill=gauge_line, width=1)
                angle = rnd.randint(210, 330)
                nx = gcx + int(gr * 0.8 * math.cos(math.radians(angle)))
                ny = gcy + int(gr * 0.8 * math.sin(math.radians(angle)))
                d.line([(gcx, gcy), (nx, ny)], fill=gauge_warn if angle > 300 else gauge_fill, width=1)
                d.ellipse([gcx - 2, gcy - 2, gcx + 2, gcy + 2], fill=gauge_line)
            else:
                bx = px0 + 6
                bh_max = ph - 16
                bar_fill_h = rnd.randint(int(bh_max * 0.2), bh_max)
                bc = gauge_warn if bar_fill_h > bh_max * 0.8 else gauge_fill
                d.rectangle([bx, py + 8, bx + 8, py + 8 + bh_max], outline=gauge_line, width=1)
                d.rectangle([bx + 1, py + 8 + bh_max - bar_fill_h,
                             bx + 7, py + 8 + bh_max - 1], fill=bc)
                # 目盛り
                for ti in range(0, bh_max, bh_max // 4 or 1):
                    d.line([(bx + 9, py + 8 + ti), (bx + 12, py + 8 + ti)],
                           fill=gauge_line, width=1)
                # 2本目のバー
                bx2 = px0 + 18
                bar2_h = rnd.randint(int(bh_max * 0.1), int(bh_max * 0.7))
                d.rectangle([bx2, py + 8, bx2 + 8, py + 8 + bh_max], outline=gauge_line, width=1)
                d.rectangle([bx2 + 1, py + 8 + bh_max - bar2_h,
                             bx2 + 7, py + 8 + bh_max - 1], fill=gauge_fill)
            # パネルIDラベル
            f_pid = F("ms_goth", 8)
            pid = f"{chr(65 + rnd.randint(0, 5))}-{rnd.randint(1,9)}"
            d.text((px0 + 2, py + ph - 10), pid, font=f_pid, fill=gauge_line)

    # 床の誘導マーキング（中央矢印ライン）
    arrow_col = _mix(bg0, gold, 0.12)
    for ay in range(H - 30, 140, -80):
        d.polygon([(cx - 8, ay), (cx, ay - 16), (cx + 8, ay)], fill=arrow_col)
        d.line([(cx, ay), (cx, ay + 40)], fill=arrow_col, width=2)

    # 左右壁面のハザードストライプ（上部）
    hz_y = 136
    for hx in range(0, 68, 8):
        d.polygon([(hx, hz_y), (hx + 4, hz_y), (hx + 8, hz_y + 12), (hx + 4, hz_y + 12)],
                  fill=_mix(bg0, gold, 0.18))
    for hx in range(W - 68, W, 8):
        d.polygon([(hx, hz_y), (hx + 4, hz_y), (hx + 8, hz_y + 12), (hx + 4, hz_y + 12)],
                  fill=_mix(bg0, gold, 0.18))

    # 換気グリル（左右壁面、パネル間）
    for side_x in (70, W - 70):
        for gy in range(180, H - 80, 200):
            gx0 = side_x - 16
            d.rectangle([gx0, gy, gx0 + 32, gy + 20], outline=_mix(bg0, steel, 0.3), width=1)
            for gs in range(gx0 + 2, gx0 + 30, 4):
                d.line([(gs, gy + 2), (gs, gy + 18)], fill=_mix(bg0, steel, 0.2), width=1)

    # 床面のグリッド参照（A1, A2... 薄い座標表記）
    f_grid = F("ms_goth", 11)
    grid_lbl_col = _mix(bg0, line, 0.10)
    for gi, gx in enumerate(range(120, W - 120, 200)):
        for gj, gy in enumerate(range(150, H, 200)):
            lbl = f"{chr(65 + gi)}{gj + 1}"
            d.text((gx, gy), lbl, font=f_grid, fill=grid_lbl_col)

    # 壁面の計測目盛り（左端、10px刻み）
    for ty in range(140, H, 40):
        tw = 6 if ty % 200 == 0 else 3
        d.line([(10, ty), (10 + tw, ty)], fill=_mix(bg0, steel, 0.3), width=1)
    for ty in range(140, H, 40):
        tw = 6 if ty % 200 == 0 else 3
        d.line([(W - 10, ty), (W - 10 - tw, ty)], fill=_mix(bg0, steel, 0.3), width=1)

    # 底辺の排水溝グレーチング
    for gx in range(0, W, 16):
        d.rectangle([gx, H - 12, gx + 8, H], fill=_mix(bg0, steel, 0.15))
        d.rectangle([gx + 8, H - 12, gx + 16, H], fill=_mix(bg0, (0, 0, 0), 0.6))

    # ── ひび割れテクスチャ（経年劣化・廃墟感） ──
    crack_col1 = _mix(bg0, line, 0.14)
    crack_col2 = _mix(bg0, line, 0.09)
    crack_shadow = _mix(bg0, (0, 0, 0), 0.7)
    crack_rnd = random.Random(333)
    crack_seeds = [
        # (始点x, 始点y, x方向バイアス, y方向バイアス, 長さ)
        (80, 160, 1.5, 1.0, 350), (200, 120, 0.6, 1.2, 280),
        (W - 100, 200, -1.2, 1.0, 400), (W - 250, 140, -0.8, 0.9, 300),
        (cx - 400, 300, 0.3, 1.4, 320), (cx + 350, 250, -0.4, 1.3, 280),
        (150, 600, 1.0, 0.8, 250), (W - 200, 550, -1.0, 1.0, 300),
        (300, 900, 0.8, 0.6, 200), (W - 350, 850, -0.5, 0.8, 220),
        (cx, 500, 0.2, 1.5, 350), (cx - 200, 700, -0.3, 1.2, 280),
        (cx + 250, 400, 0.7, 1.1, 260), (100, 1000, 1.2, 0.4, 200),
        (W - 120, 980, -0.9, 0.5, 180), (cx + 100, 800, -0.6, 1.3, 240),
    ]
    for sx, sy, bx_bias, by_bias, length in crack_seeds:
        x, y = float(sx), float(sy)
        main_w = 2 if length > 280 else 1
        for step in range(length):
            fade = 1.0 - step / length * 0.4
            dx = crack_rnd.gauss(bx_bias, 1.4)
            dy = crack_rnd.gauss(by_bias, 1.1)
            nx, ny = x + dx, y + dy
            d.line([(int(x), int(y) + 1), (int(nx), int(ny) + 1)],
                   fill=crack_shadow, width=main_w)
            col = crack_col1 if fade > 0.7 else crack_col2
            d.line([(int(x), int(y)), (int(nx), int(ny))],
                   fill=col, width=main_w)
            x, y = nx, ny
            if crack_rnd.random() < 0.12:
                bx2, by2 = x, y
                branch_len = crack_rnd.randint(20, 80)
                for _ in range(branch_len):
                    bdx = crack_rnd.gauss(-bx_bias * 0.6, 1.6)
                    bdy = crack_rnd.gauss(by_bias * 0.5, 1.2)
                    bnx, bny = bx2 + bdx, by2 + bdy
                    d.line([(int(bx2), int(by2)), (int(bnx), int(bny))],
                           fill=crack_col2, width=1)
                    bx2, by2 = bnx, bny
                    if crack_rnd.random() < 0.06:
                        break

    # ── 区画表示・壁面ステンシル ──
    f_sec = F("ms_goth", 16)
    f_warn = F("ms_goth", 13)
    sec_col = _mix(bg0, line, 0.18)
    d.text((100, 140), "SECTION B-1F  SUBSURFACE RESEARCH WING", font=f_sec, fill=sec_col)
    d.text((W - 280, 140), "RESTRICTED AREA", font=f_sec, fill=_mix(bg0, shu, 0.35))
    d.text((100, 158), "AUTHORIZED PERSONNEL ONLY", font=f_warn, fill=_mix(bg0, shu, 0.22))
    d.text((W - 280, 158), "BIOSAFETY LEVEL 4", font=f_warn, fill=_mix(bg0, shu, 0.22))
    # 底辺にも区画注記
    d.text((100, H - 28), "EXIT →  ELEVATOR SHAFT  B-1F", font=f_warn, fill=_mix(bg0, line, 0.12))
    d.text((W - 320, H - 28), "EMERGENCY PROTOCOL: SEAL ALL SECTIONS",
           font=f_warn, fill=_mix(bg0, shu, 0.15))

    # ── タイトル帯 ──
    title_y = 10
    f_title = F("mincho_b", 72)
    title_text = "覗きの代"
    tw = d.textlength(title_text, font=f_title)
    d.text((cx - tw / 2, title_y), title_text, font=f_title, fill=line)
    sub_text = "～ 御影村研究所 封鎖事案 調査記録 ～"
    f_sub = F("goth_m", 22)
    sw = d.textlength(sub_text, font=f_sub)
    d.text((cx - sw / 2, title_y + 78), sub_text, font=f_sub, fill=gold)

    # ── カード配置ゾーン（下=入口→上=最奥） ──
    if zones:
        cw, ch = 164, 230
        gap = 10
        frame_pad = 14
        safe_rgba = (202, 170, 104, 70)
        door_rgba = (100, 200, 210, 70)
        norm_rgba = (160, 168, 190, 50)

        rows_def = [
            ("P1  第1調査",   "SECTION B-3F  ENTRANCE",      8, False, False),
            ("P4  第2調査",   "SECTION B-4F  ISOLATION WARD", 6, True,  True),
            ("P7  最終調査",  "SECTION B-5F  INNER SANCTUM",  2, True,  True),
        ]
        row_gap = 34
        row_h = frame_pad * 2 + ch + 28
        total_h = len(rows_def) * row_h + (len(rows_def) - 1) * row_gap
        zy_base = H - total_h - 16

        img = img.convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        f_lbl = F("goth_b", 24)
        f_sec2 = F("ms_goth", 14)
        f_slot = F("goth_m", 18)

        for ri_raw, (row_label, sec_code, n_norm, has_safe, has_door) in enumerate(rows_def):
            ri = len(rows_def) - 1 - ri_raw
            zy = zy_base + ri * (row_h + row_gap)

            n_total = n_norm + (1 if has_safe else 0) + (1 if has_door else 0)
            inner_w = n_total * cw + (n_total - 1) * gap
            frame_w = inner_w + frame_pad * 2
            frame_x = (W - frame_w) // 2
            frame_y = zy
            frame_h = row_h

            # フレーム外枠（二重線）
            od.rectangle([frame_x, frame_y, frame_x + frame_w, frame_y + frame_h],
                         fill=(14, 18, 28, 140),
                         outline=(steel[0], steel[1], steel[2], 160), width=3)
            od.rectangle([frame_x + 4, frame_y + 4,
                          frame_x + frame_w - 4, frame_y + frame_h - 4],
                         outline=(steel[0], steel[1], steel[2], 60), width=1)
            # コーナーマーク（L字）
            cm = 14
            for (cxp, cyp, dx, dy) in [
                (frame_x + 2, frame_y + 2, 1, 1),
                (frame_x + frame_w - 2, frame_y + 2, -1, 1),
                (frame_x + 2, frame_y + frame_h - 2, 1, -1),
                (frame_x + frame_w - 2, frame_y + frame_h - 2, -1, -1),
            ]:
                od.line([(cxp, cyp), (cxp + cm * dx, cyp)],
                        fill=(gold[0], gold[1], gold[2], 140), width=2)
                od.line([(cxp, cyp), (cxp, cyp + cm * dy)],
                        fill=(gold[0], gold[1], gold[2], 140), width=2)
            # リベット（上辺に等間隔）
            for rvx in range(frame_x + 20, frame_x + frame_w - 20, 36):
                od.ellipse([rvx - 2, frame_y + 1, rvx + 2, frame_y + 5],
                           fill=(steel[0], steel[1], steel[2], 120))
            # 上辺の警告帯（ハザードストライプ）
            stripe_h = 6
            for sx in range(frame_x + 6, frame_x + frame_w - 6, 10):
                if (sx // 10) % 2 == 0:
                    od.polygon([(sx, frame_y + 6), (sx + 5, frame_y + 6),
                                (sx + 8, frame_y + 6 + stripe_h),
                                (sx + 3, frame_y + 6 + stripe_h)],
                               fill=(gold[0], gold[1], gold[2], 80))
            # 下辺にも薄い帯
            for sx in range(frame_x + 6, frame_x + frame_w - 6, 10):
                if (sx // 10) % 2 == 0:
                    od.rectangle([sx, frame_y + frame_h - 3,
                                  sx + 5, frame_y + frame_h - 1],
                                 fill=(steel[0], steel[1], steel[2], 50))
            # ラベル（フレーム上辺）
            od.text((frame_x + 14, frame_y + stripe_h + 8), row_label, font=f_lbl,
                    fill=(gold[0], gold[1], gold[2], 230))
            # 区画コード（右端）
            scw = od.textlength(sec_code, font=f_sec2)
            od.text((frame_x + frame_w - scw - 14, frame_y + stripe_h + 10),
                    sec_code, font=f_sec2, fill=(steel[0], steel[1], steel[2], 160))
            # フレーム間の接続パイプ（上の行への導管表現）
            if ri > 0:
                pipe_cx = frame_x + frame_w // 2
                od.line([(pipe_cx - 20, frame_y + frame_h),
                         (pipe_cx - 20, frame_y + frame_h + row_gap)],
                        fill=(steel[0], steel[1], steel[2], 80), width=3)
                od.line([(pipe_cx + 20, frame_y + frame_h),
                         (pipe_cx + 20, frame_y + frame_h + row_gap)],
                        fill=(steel[0], steel[1], steel[2], 80), width=3)

            # カードスロット配置（金庫=最左、通常カード、認証扉=最右）
            slot_y = frame_y + stripe_h + 30
            slot_x0 = frame_x + frame_pad

            def _draw_slot(sx, sy, rgba, label=None):
                od.rectangle([sx, sy, sx + cw, sy + ch],
                             fill=rgba,
                             outline=(rgba[0], rgba[1], rgba[2], max(rgba[3], 130)), width=2)
                if label:
                    lw_s = od.textlength(label, font=f_slot)
                    od.text((sx + (cw - lw_s) / 2, sy + ch + 4), label, font=f_slot,
                            fill=(rgba[0], rgba[1], rgba[2], 230))

            idx = 0
            if has_safe:
                _draw_slot(slot_x0, slot_y, safe_rgba, "金庫")
                idx = 1

            for ci in range(n_norm):
                sx = slot_x0 + (idx + ci) * (cw + gap)
                _draw_slot(sx, slot_y, norm_rgba)

            if has_door:
                sx = slot_x0 + (idx + n_norm) * (cw + gap)
                _draw_slot(sx, slot_y, door_rgba, "認証扉")

        img.alpha_composite(ov)
        d = ImageDraw.Draw(img)

    # zones=False でもここ以降 RGBA が必要
    if img.mode != "RGBA":
        img = img.convert("RGBA")
        d = ImageDraw.Draw(img)

    # ── 鳥居シルエット（最奥フレームの上に控えめに） ──
    tori_col = _mix(bg0, (130, 140, 170), 0.18)
    tcy = (zy_base - 20) if zones else 460
    d.polygon([(cx - 200, tcy), (cx - 180, tcy - 30),
               (cx + 180, tcy - 30), (cx + 200, tcy),
               (cx + 180, tcy - 10), (cx - 180, tcy - 10)], fill=tori_col)
    d.rectangle([cx - 14, tcy - 10, cx + 14, tcy + 44], fill=tori_col)
    d.rectangle([cx - 150, tcy + 10, cx + 150, tcy + 24], fill=tori_col)
    d.rectangle([cx - 132, tcy - 10, cx - 112, tcy + 90], fill=tori_col)
    d.rectangle([cx + 112, tcy - 10, cx + 132, tcy + 90], fill=tori_col)

    # 冷光
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glow2)
    for r, a in [(120, 5), (70, 12), (35, 24), (10, 40)]:
        gd2.ellipse([cx - r, tcy - r, cx + r, tcy + r], fill=(180, 220, 255, a))
    gd2.line([(cx, tcy + 24), (cx, tcy + 90)], fill=(200, 220, 255, 18), width=8)
    gd2.line([(cx, tcy + 24), (cx, tcy + 90)], fill=(240, 248, 255, 30), width=2)
    img.alpha_composite(glow2)

    return img.convert("RGB")


def make_prologue():
    """プロローグ/導入文画像。1600×1000。"""
    W, H = 1600, 1000
    shu = (188, 54, 44)
    gold = (172, 138, 74)
    sumi = (40, 33, 29)
    line_col = (224, 228, 236)
    washi0, washi1 = (236, 231, 220), (218, 212, 198)

    img = vgrad((W, H), (22, 28, 44), (8, 10, 18))
    img = paper_noise(img, 4, seed=13)
    d = ImageDraw.Draw(img)

    # 外枠（朱太枠＋金内罫）
    d.rectangle([16, 16, W - 16, H - 16], outline=shu, width=10)
    d.rectangle([34, 34, W - 34, H - 34], outline=gold, width=2)

    # 左上タイトル
    f_small = F("goth_m", 22)
    d.text((56, 56), "マーダーミステリー", font=f_small, fill=gold)
    f_big = F("mincho_b", 72)
    d.text((56, 88), "覗きの代", font=f_big, fill=line_col)
    d.text((56, 172), "～御影村研究所封鎖事案調査記録～", font=F("goth_m", 20), fill=_mix((8, 10, 18), gold, 0.6))
    d.line([(56, 218), (W // 2 - 40, 218)], fill=shu, width=2)

    # プロローグ本文（左半分）
    prologue = (
        "○○県御影村──。\n\n"
        "地元村民によって偶然発見されたのは、\n"
        "いかなる公的記録にも存在しない\n"
        "極秘の地下研究施設だった。\n\n"
        "先行調査に入った先遣隊3名との通信は途絶。\n"
        "調査本部は、正体不明の施設内で\n"
        "起きた異常事態に対し、\n"
        "通常の救助班では対処が困難だと\n"
        "判断した。\n\n"
        "この判断を受け、各分野の専門家を含む\n"
        "第二次調査チーム4名が編成され、\n"
        "今、当該施設への調査計画が\n"
        "開始されようとしていた──。"
    )
    wrap_draw(d, (56, 242), prologue, F("goth_m", 26), line_col, 572, 44)

    # 縦区切り線
    div_x = W // 2 + 20
    d.line([(div_x, 56), (div_x, H - 56)], fill=_mix((8, 10, 18), gold, 0.4), width=2)

    # 右半分：キャスト紹介
    casts = [
        ("民俗学者",   "独自に農村の伝承を調査していた\n研究者。"),
        ("調査隊員",   "先遣隊と同じ組織の正規隊員。"),
        ("大学教授",   "認知科学を専門とする研究者。"),
        ("大学院生",   "教授の研究室に所属する院生。"),
    ]
    cx_r = div_x + 40
    f_cast_name = F("mincho_b", 36)
    f_cast_body = F("goth_m", 22)
    cy = 80
    d.text((cx_r, cy), "── キャスト ──", font=F("goth_m", 26), fill=gold)
    cy += 60
    for name, desc in casts:
        d.text((cx_r, cy), name, font=f_cast_name, fill=line_col)
        cy += 48
        wrap_draw(d, (cx_r + 12, cy), desc, f_cast_body, _mix((8, 10, 18), line_col, 0.7), 616, 36)
        cy += 36 * (desc.count("\n") + 1) + 20
        d.line([(cx_r, cy), (W - 56, cy)], fill=_mix((8, 10, 18), gold, 0.3), width=1)
        cy += 20

    return img.convert("RGB")


def make_rules():
    """プレイ上の注意画像。1600×1000。"""
    W, H = 1600, 1000
    shu = (188, 54, 44)
    gold = (172, 138, 74)
    line_col = (224, 228, 236)

    img = vgrad((W, H), (22, 28, 44), (8, 10, 18))
    img = paper_noise(img, 4, seed=17)
    d = ImageDraw.Draw(img)

    d.rectangle([16, 16, W - 16, H - 16], outline=shu, width=10)
    d.rectangle([34, 34, W - 34, H - 34], outline=gold, width=2)

    cx = W // 2
    d.text((56, 56), "マーダーミステリー", font=F("goth_m", 22), fill=gold)
    d.text((56, 88), "覗きの代", font=F("mincho_b", 72), fill=line_col)
    d.line([(56, 178), (W - 56, 178)], fill=shu, width=2)

    d.text((56, 204), "── プレイ上の注意 ──", font=F("goth_m", 28), fill=gold)

    rules = [
        "キャラクターシートは他の人に見せないこと",
        "キャラクターシートの文章をそのまま読み上げないこと",
        "キャラ設定の一部はプレイヤーが決めてよい（名前・性別・外見など）",
        "全員が嘘をついてOK",
        "一番の目標は「みんなで楽しむこと」",
    ]
    f_rule = F("goth_m", 30)
    ry = 290
    for rule in rules:
        check_col = _mix((8, 10, 18), (100, 220, 140), 0.85)
        d.text((68, ry), "✓", font=f_rule, fill=check_col)
        wrap_draw(d, (120, ry), rule, f_rule, line_col, 1080, 48)
        ry += 100

    return img.convert("RGB")


def make_phase_bar():
    """フェイズ進行表。1400×200横長帯。Day区切り付き。"""
    W, H = 1400, 200
    DAY_H = 36
    bg = (14, 17, 26)
    line_col = (224, 228, 236)
    gold = (202, 170, 104)
    shu = (208, 86, 60)
    day_bg = _mix(bg, gold, 0.15)

    img = Image.new("RGB", (W, H), bg)
    img = paper_noise(img, 2, seed=9)
    d = ImageDraw.Draw(img)

    phases = [
        ("P0", "導入",     "〜0:20"),
        ("P1", "第1調査",  "〜0:50"),
        ("P2", "第1会議",  "〜1:10"),
        ("P3", "固有1",    "〜1:25"),
        ("P4", "第2調査",  "〜1:55"),
        ("P5", "第2会議",  "〜2:10"),
        ("P6", "固有2",    "〜2:25"),
        ("P7", "最終調査", "〜2:45"),
        ("P8", "会議+投票","〜3:05"),
        ("P9", "ED",       "〜3:15"),
    ]
    n = len(phases)
    cell_w = W // n

    days = [
        (0, 1, "到着"),
        (1, 4, "Day 1「化け物がいた施設」"),
        (4, 7, "Day 2「この中に化け物がいる」"),
        (7, 10, "Day 3「どちらが悪か」"),
    ]
    for start, end, label in days:
        x0 = start * cell_w
        x1 = end * cell_w - 2
        d.rectangle([x0, 0, x1, DAY_H - 1], fill=day_bg)
        cx = (x0 + x1) // 2
        f_day = F("goth_m", 16)
        tw = d.textlength(label, font=f_day)
        d.text((cx - tw / 2, (DAY_H - 16) // 2), label, font=f_day, fill=gold)
        if start > 0:
            d.line([x0, 0, x0, DAY_H - 1], fill=gold, width=1)

    d.line([0, DAY_H, W, DAY_H], fill=gold, width=1)

    cell_top = DAY_H
    cell_h = H - DAY_H
    for i, (pno, pname, ptime) in enumerate(phases):
        x0 = i * cell_w
        is_fixed = i in (3, 6)
        col = shu if is_fixed else _mix(bg, line_col, 0.12)
        d.rectangle([x0, cell_top, x0 + cell_w - 2, H], fill=col)
        cx = x0 + cell_w // 2
        pno_col = (255, 240, 220) if is_fixed else gold
        name_col = (255, 255, 250) if is_fixed else line_col
        d.text((cx - d.textlength(pno, font=F("goth_b", 36)) / 2, cell_top + 8),
               pno, font=F("goth_b", 36), fill=pno_col)
        d.text((cx - d.textlength(pname, font=F("mincho", 22)) / 2, cell_top + 54),
               pname, font=F("mincho", 22), fill=name_col)
        time_col = (240, 230, 220) if i in (3, 6) else _mix(bg, gold, 0.7)
        d.text((cx - d.textlength(ptime, font=F("goth_m", 18)) / 2, cell_top + 96),
               ptime, font=F("goth_m", 18), fill=time_col)

    d.rectangle([0, 0, W - 1, H - 1], outline=gold, width=2)
    return img


def make_action_matrix():
    """アクション可否表。900×500。"""
    W, H = 900, 500
    bg = (32, 36, 46)
    line_col = (200, 204, 214)
    gold = (202, 170, 104)
    shu = (208, 86, 60)
    ok_col = (80, 200, 120)
    ng_col = (200, 72, 60)

    img = Image.new("RGB", (W, H), bg)
    img = paper_noise(img, 2, seed=5)
    d = ImageDraw.Draw(img)

    title = "アクション可否表"
    f_title = F("mincho_b", 30)
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 16), title, font=f_title, fill=gold)

    row_labels = ["単独調査", "バディ調査（密談）", "全体会議"]
    col_labels = ["カードの譲渡", "カードの公開", "相手にだけ見せる"]

    matrix = [
        ["×", "○", "×"],
        ["○", "○", "○"],
        ["○", "○", "×"],
    ]

    lw = 240
    cell_w = (W - lw - 20) // 3
    cell_h = 76
    hdr_h = 50
    top = 68

    f_hdr = F("goth_m", 20)
    f_row = F("mincho", 22)
    f_cell = F("goth_b", 30)

    # 列ヘッダ
    for j, cl in enumerate(col_labels):
        cx = lw + 10 + j * cell_w + cell_w // 2
        d.rectangle([lw + 10 + j * cell_w, top, lw + 20 + (j + 1) * cell_w - 2, top + hdr_h],
                    fill=_mix(bg, gold, 0.18))
        cw_txt = d.textlength(cl, font=f_hdr)
        d.text((cx - cw_txt / 2, top + 14), cl, font=f_hdr, fill=gold)

    # 行
    for i, (rl, row) in enumerate(zip(row_labels, matrix)):
        ry = top + hdr_h + i * cell_h
        row_bg = _mix(bg, line_col, 0.06) if i % 2 == 0 else bg
        d.rectangle([4, ry, W - 5, ry + cell_h - 2], fill=row_bg)
        rw = d.textlength(rl, font=f_row)
        d.text((lw - rw - 10, ry + (cell_h - 26) // 2), rl, font=f_row, fill=line_col)
        for j, cell in enumerate(row):
            cx = lw + 10 + j * cell_w + cell_w // 2
            col = ok_col if cell == "○" else ng_col
            cw_cell = d.textlength(cell, font=f_cell)
            d.text((cx - cw_cell / 2, ry + (cell_h - 36) // 2), cell, font=f_cell, fill=col)

    # グリッド線
    for i in range(len(row_labels) + 1):
        ry = top + hdr_h + i * cell_h
        d.line([(0, ry), (W, ry)], fill=_mix(bg, line_col, 0.25), width=1)
    for j in range(len(col_labels) + 1):
        cx = lw + 10 + j * cell_w
        d.line([(cx, top), (cx, top + hdr_h + len(row_labels) * cell_h)],
               fill=_mix(bg, line_col, 0.25), width=1)

    d.rectangle([0, 0, W - 1, H - 1], outline=gold, width=3)
    return img


def make_marker(char_name, color):
    """キャラマーカー。120×120円形トークン。"""
    W, H = 120, 120
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    r = 56
    cx, cy = W // 2, H // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(220, 224, 232), width=4)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
              outline=(255, 255, 255, 60), width=2)

    f = F("mincho_b", 48)
    bb = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textbbox((0, 0), char_name, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1]), char_name, font=f, fill=(255, 255, 255))

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
    make_evidence_card_wa(   # 書類・ログ系（施設記録＝罫線紙＋等幅＋綴じ穴）
        5, "先遣隊 活動記録",
        "[20██年5月12日]\n第3日。B区画の調査を継続。\n設備の劣化が激しいが\n通行に支障なし。\n明日は奥の区画に入る予定。\n\n──以降の記録はない。",
        variant="log", header="記録", prefix="L").save(os.path.join(OUT, "final_front_log.png"))
    make_evidence_card_wa(   # 研究資料（固有デザイン＝藍枠の綴じ文書）＋末尾に「より詳しく…」の含み
        1, "二経路モデル",
        "認知崩壊の機序をめぐる内部研究資料。\n共鳴と破壊――二つの経路の記録。\n――詳しく調べれば、より多くの情報が得られる気がする。",
        variant="research", header="研究資料", prefix="R").save(os.path.join(OUT, "final_front_research.png"))
    make_shock_card(         # 衝撃証拠「灰の残骸」（一点物・暗転デザイン）
        7, "灰の残骸",
        "先遣隊の状態と近しいような灰の塊。\nしかし先遣隊と違い、人の原型すらとどめていない。\n",
    ).save(os.path.join(OUT, "final_front_ash.png"))

    # ── 裏／固有マス（濃紺・民俗×研究の融合） ──
    make_card_back_wa("magatama_rw").save(os.path.join(OUT, "final_back_common.png"))  # 汎用裏＝紅白の勾玉
    make_back_safe("vault").save(os.path.join(OUT, "final_back_safe.png"))             # 金庫＝機密保管庫＋封印
    make_back_biodoor("shrine_tech").save(os.path.join(OUT, "final_back_biodoor.png")) # 認証扉＝注連縄鳥居＋走査装置

    # ── 研究論文（4本 × 原本/墨消し） ──
    for pid in range(1, 5):
        make_paper(paper_id=pid, redacted=False).save(os.path.join(OUT, f"final_paper_{pid}_full.png"))
        make_paper(paper_id=pid, redacted=True).save(os.path.join(OUT, f"final_paper_{pid}_redacted.png"))

    # ── ボード・UI素材 ──
    make_board(zones=False).save(os.path.join(OUT, "final_board.png"))
    make_board(zones=True).save(os.path.join(OUT, "final_board_zones.png"))
    make_prologue().save(os.path.join(OUT, "final_prologue.png"))
    make_rules().save(os.path.join(OUT, "final_rules.png"))
    make_phase_bar().save(os.path.join(OUT, "final_phase_bar.png"))
    make_action_matrix().save(os.path.join(OUT, "final_action_matrix.png"))
    markers = [("院", (160, 50, 50)), ("民", (50, 130, 80)),
               ("隊", (50, 80, 160)), ("教", (110, 50, 150))]
    for ch, col in markers:
        make_marker(ch, col).save(os.path.join(OUT, f"final_marker_{ch}.png"))

    print("saved -> outputs/design/ : final_* (採用デザインのみ) + board/prologue/rules/phase_bar/action_matrix/marker")
