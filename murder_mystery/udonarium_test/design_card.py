# -*- coding: utf-8 -*-
"""
カードデザイン試作（A案：PIL作り込み）。
テーマ＝機密研究ファイルの「物的証拠タグ」。本体 build_udon.py とは独立。
確定したら make_card_front を差し替える。
"""
import os, tempfile, random
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
    foot = "MIMESIS ── 地下研究施設 調査記録"
    f_ft = F("goth_m", 20)
    fw = d.textlength(foot, font=f_ft)
    d.text(((W - fw) / 2, H - 58), foot, font=f_ft, fill=(112, 102, 92))

    return img.convert("RGB")


def make_card_back():
    """全カード共通の汎用裏面（表と同じデザイン言語＋MIMESISエンブレム）"""
    W, H = 600, 840
    ink = (46, 41, 36)
    accent = (150, 36, 38)
    img = vgrad((W, H), (234, 230, 220), (206, 200, 187))
    img = paper_noise(img, 5)
    d = ImageDraw.Draw(img)
    d.rectangle([18, 18, W - 18, H - 18], outline=ink, width=4)
    d.rectangle([28, 28, W - 28, H - 28], outline=ink, width=1)
    for x, y, sx, sy in [(40, 40, 1, 1), (W - 40, 40, -1, 1),
                         (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)]:
        corner(d, x, y, sx, sy, accent)
    cx, cy = W // 2, H // 2 - 40
    for r in (152, 122):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    d.polygon([(cx, cy - 74), (cx + 74, cy), (cx, cy + 74), (cx - 74, cy)],
              outline=accent, width=4)
    fM = F("mincho_b", 116)
    bb = d.textbbox((0, 0), "M", font=fM)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
           "M", font=fM, fill=ink)
    t1 = "MIMESIS"
    f1 = F("mincho_b", 56)
    d.text(((W - d.textlength(t1, font=f1)) / 2, cy + 210), t1, font=f1, fill=ink)
    t2 = "C O N F I D E N T I A L"
    f2 = F("goth_m", 24)
    d.text(((W - d.textlength(t2, font=f2)) / 2, cy + 286), t2, font=f2, fill=accent)
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
    rh, f_rh = "MIMESIS-RP  Vol.7 No.3", F(f_bd, 20)
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
    make_evidence_card(
        1, "血の付いたナイフ",
        "食堂のテーブル下から発見された。\n刃には乾いた血痕。\n柄の指紋は丁寧に拭き取られている。\n──誰かが、痕跡を消した。",
    ).save(os.path.join(OUT, "design_sample.png"))
    make_evidence_card(
        1, "二経路モデル",
        "観測者効果による認知崩壊に関する研究資料。\n全文はGMより配布。\n教授の査読で墨消し部が開示される。",
        header="研究資料", prefix="R",
    ).save(os.path.join(OUT, "research_card_sample.png"))
    make_card_back().save(os.path.join(OUT, "design_back.png"))
    make_paper(redacted=True, style="warm").save(os.path.join(OUT, "paper_redacted.png"))
    make_paper(redacted=False, style="warm").save(os.path.join(OUT, "paper_full.png"))
    make_paper(redacted=True, style="mono").save(os.path.join(OUT, "paper_mono_redacted.png"))
    make_paper(redacted=False, style="mono").save(os.path.join(OUT, "paper_mono_full.png"))
    print("saved -> outputs/design/ : card front/back + paper warm/mono x full/redacted")
