# -*- coding: utf-8 -*-
"""
研究論文の「レイアウト構成」と「フォント構成」を直交軸で探索する。
配色(style)は design_card.PAPER_STYLES を流用。
後で「レイアウト × フォント × 配色」のいいとこ取り（最終確定）をするための比較材料。

出力:
  outputs/design/explore/layout_<name>.png   ... 各レイアウトのフルサイズ
  outputs/design/explore/font_<name>.png     ... 各フォント構成のフルサイズ
  outputs/design/layout_contact.png          ... レイアウト一覧（固有ファイル）
  outputs/design/font_contact.png            ... フォント一覧（固有ファイル）
"""
import os
from PIL import Image, ImageDraw, ImageFont
import design_card as dc

F, wrap, _mix = dc.F, dc.wrap_draw, dc._mix
W, H = 1000, 1414

# ---- 論文内容（レイアウトから独立したデータ） ----
C = dict(
    hl="CLASSIFIED ── 内部資料 / 持出厳禁",
    hr="内部紀要  Vol.7 No.3",
    title=["観測者効果による認知崩壊の二経路モデル", "── 共鳴経路と破壊経路の分岐条件について ──"],
    au="霧島 透 ・ 朏 玲奈",
    af="□□大学大学院 認知科学研究室",
    ab=("本研究は、深層認知への直接干渉（観測）が対象の人格構造に及ぼす影響を、共鳴経路と"
        "破壊経路の二系統に分類し、両者を分岐させる臨界条件を定式化する。さらに観測主体の"
        "封じ込めに関する理論的基盤を提示し、依代への転写手順とその失敗時の挙動を論じる。"),
    secs=[
        ("1. 序論", ["深層認知への直接的干渉、すなわち対象の内的表象を外部から観測する行為は、"
                     "長らく理論上の可能性に留まってきた。第四世代観測機構の確立により、本現象は"
                     "再現可能な実験対象となった。"], ()),
        ("2. 二経路モデル", ["観測対象に生じる反応は、共鳴経路と破壊経路の二系統に大別される。"
                          "共鳴経路では表象が部分的に同期し人格の同一性は保持される。破壊経路では"
                          "自己モデルが不可逆的に崩壊し廃人化に至る。",
                          "両経路を分岐させる臨界条件は、観測深度が第三層を超え、被観測者の防衛機制"
                          "が一定閾値を下回った場合に破壊経路へ遷移する。臨界値は個体差が大きい。"], (1,)),
        ("3. 封じ込め手順", ["封じ込めは観測主体を物理的依代へ転写し、外部刺激を遮断することで成立する。",
                          "手順の核心は、依代に特定の符牒を刻み、認証鍵を生体情報と二重に束ねること"
                          "にある。手順を誤れば主体は依代を離脱し最も近い器へ移動する。"], (1,)),
        ("4. 結論", ["本モデルは観測現象の制御可能性を理論的に保証する。ただし臨界条件の個体差に"
                    "ついては追試を要する。"], ()),
    ],
    fig="Fig.1 認知共鳴の模式図",
)

# ---- フォントセット (title, head, body, abst) ----
FONTSETS = {
    "mincho":   ("mincho_b", "mincho_b", "mincho", "mincho"),
    "goth-min": ("goth_b", "goth_b", "mincho", "mincho"),
    "goth":     ("goth_b", "goth_b", "goth_m", "goth_m"),
    "bizud":    ("biz_goth", "biz_goth", "biz_min", "biz_min"),
    "mono-sp":  ("goth_b", "goth_b", "ms_goth", "ms_goth"),
}


# ---- 共通ヘルパ ----
def _section(d, x, y, w, head, paras, ridx, fh, fb, ink, lh=36):
    rects = []
    d.text((x, y), head, font=fh, fill=ink)
    y += 44
    mc = max(8, int(w // fb.size))
    for i, p in enumerate(paras):
        y0 = y
        y = wrap(d, (x, y), p, fb, ink, mc, lh)
        if i in ridx:
            rects.append((x - 2, y0 - 2, x + w + 2, y - 8))
        y += 14
    return y, rects


def _bar(d, rects, s, ink):
    col = _mix(s["c"][0], (255, 255, 255), 0.35) if sum(ink) > 380 else (16, 14, 12)
    for x0, y0, x1, y1 in rects:
        d.rectangle([x0, y0, x1, y1], fill=col)


def _finish(img, s):
    stx, sang, scol = s["st"]
    st = dc.stamp(stx, scol, 44, angle=sang)
    img = img.convert("RGBA")
    img.alpha_composite(st, (img.width - 84 - st.width, 74))
    return img.convert("RGB")


def _footer(d, ft, ink, sub):
    d.line([(84, H - 72), (W - 84, H - 72)], fill=sub, width=1)
    d.text(((W - d.textlength("- 1 -", font=F(ft[2], 20))) / 2, H - 60),
           "- 1 -", font=F(ft[2], 20), fill=sub)


# ---- レイアウト群 ----
def render_2col(style, fsname, redacted=False):
    s, ft = dc.PAPER_STYLES[style], FONTSETS[fsname]
    ink, acc, sub = s["ink"], s["acc"], s["sub"]
    M = 84
    img = dc._paper_bg((W, H), s)
    d = ImageDraw.Draw(img)
    colw = (W - M * 2 - 44) // 2
    lx, rx = M, M + colw + 44
    d.text((M, 34), C["hl"], font=F(ft[3], 20), fill=acc)
    d.text((W - M - d.textlength(C["hr"], font=F(ft[3], 20)), 34), C["hr"], font=F(ft[3], 20), fill=sub)
    d.line([(M, 64), (W - M, 64)], fill=sub, width=1)
    ty = 100
    for i, ln in enumerate(C["title"]):
        f = F(ft[0], 40 if i == 0 else 27)
        d.text(((W - d.textlength(ln, font=f)) / 2, ty), ln, font=f, fill=ink)
        ty += 56 if i == 0 else 46
    d.text(((W - d.textlength(C["au"], font=F("goth_m", 23))) / 2, ty + 8), C["au"], font=F("goth_m", 23), fill=ink)
    d.text(((W - d.textlength(C["af"], font=F(ft[3], 20))) / 2, ty + 44), C["af"], font=F(ft[3], 20), fill=sub)
    ay, abh = ty + 92, 184
    d.rectangle([M, ay, W - M, ay + abh], outline=sub, width=1)
    d.text((M + 18, ay + 14), "Abstract", font=F(ft[1], 22), fill=ink)
    wrap(d, (M + 18, ay + 52), C["ab"], F(ft[2], 21), ink, (W - 2 * M - 36) // 21, 32)
    body = ay + abh + 34
    fh, fb = F(ft[1], 25), F(ft[2], 22)
    rects, yL = [], body
    for hd, pr, ri in C["secs"][:2]:
        yL, rc = _section(d, lx, yL, colw, hd, pr, ri, fh, fb, ink); rects += rc
    yR = body
    for hd, pr, ri in C["secs"][2:]:
        yR, rc = _section(d, rx, yR, colw, hd, pr, ri, fh, fb, ink); rects += rc
    fy = yR + 12
    d.rectangle([rx, fy, rx + colw, fy + 150], outline=sub, width=1)
    d.line([(rx, fy), (rx + colw, fy + 150)], fill=sub, width=1)
    d.line([(rx, fy + 150), (rx + colw, fy)], fill=sub, width=1)
    d.text((rx, fy + 158), C["fig"], font=F(ft[2], 18), fill=sub)
    if redacted:
        _bar(d, rects, s, ink)
    _footer(d, ft, ink, sub)
    return _finish(img, s)


def render_1col(style, fsname, redacted=False):
    s, ft = dc.PAPER_STYLES[style], FONTSETS[fsname]
    ink, acc, sub = s["ink"], s["acc"], s["sub"]
    M = 112
    img = dc._paper_bg((W, H), s)
    d = ImageDraw.Draw(img)
    cw = W - 2 * M
    d.text((M, 40), C["hl"], font=F(ft[3], 19), fill=acc)
    d.text((W - M - d.textlength(C["hr"], font=F(ft[3], 19)), 40), C["hr"], font=F(ft[3], 19), fill=sub)
    d.line([(M, 70), (W - M, 70)], fill=sub, width=1)
    ty = 120
    d.text((M, ty), C["title"][0], font=F(ft[0], 44), fill=ink); ty += 62
    d.text((M, ty), C["title"][1], font=F(ft[0], 25), fill=sub); ty += 54
    d.text((W - M - d.textlength(C["au"], font=F("goth_m", 22)), ty), C["au"], font=F("goth_m", 22), fill=ink)
    ty += 42
    d.line([(M, ty), (W - M, ty)], fill=sub, width=1); ty += 22
    d.line([(M, ty), (M, ty + 150)], fill=acc, width=3)
    yb = wrap(d, (M + 20, ty), C["ab"], F(ft[2], 20), ink, (cw - 20) // 20, 33)
    ty = yb + 24
    fh, fb = F(ft[1], 25), F(ft[2], 22)
    rects = []
    for hd, pr, ri in C["secs"]:
        ty, rc = _section(d, M, ty, cw, hd, pr, ri, fh, fb, ink, lh=36); rects += rc
    d.text((M, ty + 4), C["fig"], font=F(ft[2], 18), fill=sub)
    if redacted:
        _bar(d, rects, s, ink)
    _footer(d, ft, ink, sub)
    return _finish(img, s)


def render_sidebar(style, fsname, redacted=False):
    s, ft = dc.PAPER_STYLES[style], FONTSETS[fsname]
    ink, acc, sub = s["ink"], s["acc"], s["sub"]
    img = dc._paper_bg((W, H), s)
    d = ImageDraw.Draw(img)
    SB, pad = 322, 28
    sb_bg = _mix(s["c"][0], ink, 0.9)
    d.rectangle([0, 0, SB, H], fill=sb_bg)
    lt = _mix(sb_bg, (255, 255, 255), 0.82)
    lts = _mix(sb_bg, (255, 255, 255), 0.55)
    d.text((pad, 56), "内部紀要", font=F(ft[1], 24), fill=lt)
    d.text((pad, 92), C["hr"], font=F(ft[3], 17), fill=lts)
    wrap(d, (pad, 168), C["title"][0], F(ft[0], 30), lt, (SB - 2 * pad) // 30, 42)
    wrap(d, (pad, 360), C["title"][1], F(ft[3], 18), lts, (SB - 2 * pad) // 18, 28)
    meta = [("分類", "CLASSIFIED"), ("持出", "厳禁"), ("作成者", C["au"]), ("所属", "□□大学大学院"), ("図版", C["fig"])]
    my = 470
    for k, v in meta:
        d.text((pad, my), k, font=F(ft[3], 16), fill=lts)
        d.text((pad, my + 22), v, font=F(ft[2], 18), fill=lt)
        my += 64
    bx, bw = SB + 44, W - (SB + 44) - 60
    d.text((bx, 60), C["hl"], font=F(ft[3], 19), fill=acc)
    d.line([(bx, 92), (W - 60, 92)], fill=sub, width=1)
    fh, fb = F(ft[1], 24), F(ft[2], 22)
    rects, yy = [], 120
    for hd, pr, ri in C["secs"]:
        yy, rc = _section(d, bx, yy, bw, hd, pr, ri, fh, fb, ink); rects += rc
    if redacted:
        _bar(d, rects, s, ink)
    return _finish(img, s)


def render_report(style, fsname, redacted=False):
    s, ft = dc.PAPER_STYLES[style], FONTSETS[fsname]
    ink, acc, sub = s["ink"], s["acc"], s["sub"]
    M = 84
    img = dc._paper_bg((W, H), s)
    d = ImageDraw.Draw(img)
    d.rectangle([M, 40, W - M, 122], outline=ink, width=2)
    d.text((M + 16, 60), C["title"][0], font=F(ft[0], 32), fill=ink)
    ty = 146
    rows = [("文書番号", C["hr"]), ("分類", "CLASSIFIED ── 持出厳禁"),
            ("作成者", C["au"]), ("所属", C["af"])]
    rh = 44
    for i, (k, v) in enumerate(rows):
        yy = ty + i * rh
        d.rectangle([M, yy, W - M, yy + rh], outline=sub, width=1)
        d.line([(M + 170, yy), (M + 170, yy + rh)], fill=sub, width=1)
        d.text((M + 14, yy + 10), k, font=F(ft[1], 20), fill=ink)
        d.text((M + 184, yy + 10), v, font=F(ft[2], 20), fill=ink)
    ty += len(rows) * rh + 26
    d.text((M, ty), "概要", font=F(ft[1], 24), fill=ink); ty += 40
    yb = wrap(d, (M, ty), C["ab"], F(ft[2], 21), ink, (W - 2 * M) // 21, 33)
    ty = yb + 22
    fh, fb = F(ft[1], 24), F(ft[2], 22)
    rects = []
    for hd, pr, ri in C["secs"]:
        ty, rc = _section(d, M, ty, W - 2 * M, hd, pr, ri, fh, fb, ink); rects += rc
    if redacted:
        _bar(d, rects, s, ink)
    _footer(d, ft, ink, sub)
    return _finish(img, s)


# ---- コンタクトシート ----
def contact(thumbs, fname, cols):
    TW = 360
    TH = int(TW * H / W)
    PAD, LH = 24, 38
    rows = (len(thumbs) + cols - 1) // cols
    SW = cols * TW + (cols + 1) * PAD
    SH = rows * (TH + LH + PAD) + PAD
    sheet = Image.new("RGB", (SW, SH), (58, 60, 66))
    d = ImageDraw.Draw(sheet)
    fl = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 26)
    for i, (n, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x, y = PAD + c * (TW + PAD), PAD + r * (TH + LH + PAD)
        sheet.paste(im.resize((TW, TH)), (x, y))
        d.text((x + 4, y + TH + 6), n, font=fl, fill=(238, 239, 244))
    out = os.path.join(HERE, "outputs", "design", fname)
    sheet.save(out)
    return out


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    EXP = os.path.join(HERE, "outputs", "design", "explore")
    os.makedirs(EXP, exist_ok=True)

    # レイアウト軸（配色mono・フォントgoth-min 固定）
    LAYOUTS = {"2col": render_2col, "1col": render_1col,
               "sidebar": render_sidebar, "report": render_report}
    lay = []
    for name, fn in LAYOUTS.items():
        im = fn("mono", "goth-min", redacted=False)
        im.save(os.path.join(EXP, "layout_%s.png" % name))
        lay.append((name, im))

    # フォント軸（レイアウト2col・配色mono 固定）
    fnt = []
    for name in FONTSETS:
        im = render_2col("mono", name, redacted=False)
        im.save(os.path.join(EXP, "font_%s.png" % name))
        fnt.append((name, im))

    c1 = contact(lay, "layout_contact.png", cols=4)
    c2 = contact(fnt, "font_contact.png", cols=5)
    print("layouts:", list(LAYOUTS.keys()))
    print("fonts  :", list(FONTSETS.keys()))
    print("contact:", c1)
    print("contact:", c2)
