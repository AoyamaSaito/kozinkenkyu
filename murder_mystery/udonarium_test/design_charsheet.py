# -*- coding: utf-8 -*-
"""キャラクターシート デザイン試作（3案: 通常A / B覚醒α,β,γ / A覚醒）"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont

# ── Fonts ──
FONTS = {
    "mincho_b": ("C:/Windows/Fonts/yumindb.ttf", 0),
    "mincho":   ("C:/Windows/Fonts/yumin.ttf", 0),
    "goth_m":   ("C:/Windows/Fonts/YuGothM.ttc", 0),
    "goth_b":   ("C:/Windows/Fonts/YuGothB.ttc", 0),
}

def F(key, sz):
    path, idx = FONTS[key]
    return ImageFont.truetype(path, sz, index=idx)

# ── Color palettes ──
PAL_NORMAL = dict(
    bg=(245, 240, 225), header_bg=(26, 39, 68), header_fg=(245, 240, 225),
    text=(44, 36, 24), accent=(192, 57, 43), section=(26, 39, 68),
    mbox_bg=(235, 232, 220), mbox_border=(26, 39, 68),
    skill_bg=(230, 228, 218), skill_border=(26, 39, 68),
    hint_bg=(240, 236, 220), hint_border=(184, 134, 11),
    tag_bg=(26, 39, 68), tag_fg=(245, 240, 225),
    border=(26, 39, 68),
)
PAL_EVIL_ALPHA = dict(
    bg=(18, 6, 6), header_bg=(60, 8, 8), header_fg=(255, 200, 180),
    text=(240, 230, 220), accent=(255, 160, 140), section=(255, 200, 180),
    mbox_bg=(40, 14, 14), mbox_border=(200, 60, 50),
    skill_bg=(35, 12, 12), skill_border=(160, 40, 35),
    hint_bg=(30, 12, 12), hint_border=(160, 40, 35),
    tag_bg=(140, 20, 15), tag_fg=(255, 230, 220),
    border=(120, 25, 20),
    blood_line=(200, 50, 40),
)
PAL_EVIL_BETA = dict(
    bg=(20, 8, 14), header_bg=(40, 10, 24), header_fg=(220, 60, 90),
    text=(200, 180, 175), accent=(230, 65, 80), section=(180, 50, 65),
    mbox_bg=(34, 14, 22), mbox_border=(160, 30, 50),
    skill_bg=(30, 12, 18), skill_border=(120, 25, 40),
    hint_bg=(28, 12, 18), hint_border=(120, 25, 40),
    tag_bg=(120, 20, 35), tag_fg=(255, 210, 220),
    border=(100, 18, 30),
)
PAL_EVIL_GAMMA = dict(
    bg=(14, 8, 8), header_bg=(50, 10, 10), header_fg=(240, 70, 50),
    text=(200, 180, 165), accent=(250, 80, 50), section=(210, 60, 45),
    mbox_bg=(36, 14, 12), mbox_border=(200, 50, 30),
    skill_bg=(32, 12, 10), skill_border=(150, 35, 25),
    hint_bg=(28, 12, 10), hint_border=(150, 35, 25),
    tag_bg=(160, 30, 20), tag_fg=(255, 220, 200),
    border=(100, 25, 20),
    stripe1=(180, 35, 25), stripe2=(50, 10, 8),
)
PAL_GOOD = dict(
    bg=(223, 232, 240), header_bg=(26, 48, 80), header_fg=(176, 208, 240),
    text=(16, 24, 32), accent=(26, 74, 144), section=(26, 48, 80),
    mbox_bg=(210, 222, 235), mbox_border=(42, 80, 144),
    skill_bg=(215, 225, 238), skill_border=(48, 96, 160),
    hint_bg=(218, 228, 238), hint_border=(42, 80, 144),
    tag_bg=(26, 56, 88), tag_fg=(192, 218, 240),
    border=(26, 48, 80),
)

W, H = 840, 1188  # A4 ish at 100dpi
MARGIN = 50
BODY_W = W - MARGIN * 2
HEADER_H = 100


def paper_noise(img, amount=3, seed=42):
    px = img.load()
    w, h = img.size
    rnd = random.Random(seed)
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-amount, amount)
            r, g, b = px[x, y][:3]
            px[x, y] = (max(0, min(255, r+n)), max(0, min(255, g+n)), max(0, min(255, b+n)))
    return img


def draw_section_title(d, y, text, pal):
    d.text((MARGIN, y), f"── {text} ──", font=F("mincho_b", 22), fill=pal["section"])
    d.line([(MARGIN, y+30), (W-MARGIN, y+30)], fill=pal["section"], width=2)
    return y + 40


def draw_body_text(d, y, text, pal, highlight_phrases=None):
    font = F("mincho", 20)
    hl_font = F("mincho_b", 20)
    highlights = highlight_phrases or []
    for line in text.split("\n"):
        if not line.strip():
            y += 14
            continue
        remaining = line
        x = MARGIN
        while remaining:
            found_hl = None
            hl_pos = len(remaining)
            for phrase in highlights:
                pos = remaining.find(phrase)
                if pos != -1 and pos < hl_pos:
                    hl_pos = pos
                    found_hl = phrase
            if found_hl and hl_pos == 0:
                bbox = d.textbbox((0, 0), found_hl, font=hl_font)
                tw = bbox[2] - bbox[0]
                if x + tw > W - MARGIN:
                    x = MARGIN
                    y += 30
                d.text((x, y), found_hl, font=hl_font, fill=pal["accent"])
                x += tw
                remaining = remaining[len(found_hl):]
            elif found_hl:
                before = remaining[:hl_pos]
                for ch in before:
                    bbox = d.textbbox((0, 0), ch, font=font)
                    cw = bbox[2] - bbox[0]
                    if x + cw > W - MARGIN:
                        x = MARGIN
                        y += 30
                    d.text((x, y), ch, font=font, fill=pal["text"])
                    x += cw
                remaining = remaining[hl_pos:]
            else:
                for ch in remaining:
                    bbox = d.textbbox((0, 0), ch, font=font)
                    cw = bbox[2] - bbox[0]
                    if x + cw > W - MARGIN:
                        x = MARGIN
                        y += 30
                    d.text((x, y), ch, font=font, fill=pal["text"])
                    x += cw
                remaining = ""
        y += 30
    return y


def draw_mission_box(d, y, items, pal, bullet="◉"):
    d.rounded_rectangle(
        [(MARGIN, y), (W-MARGIN, y + len(items)*36 + 16)],
        radius=6, fill=pal["mbox_bg"])
    d.line([(MARGIN, y), (MARGIN, y + len(items)*36 + 16)],
           fill=pal["mbox_border"], width=4)
    font = F("mincho_b", 20)
    by = y + 10
    for item in items:
        d.text((MARGIN+16, by), bullet, font=F("mincho_b", 16), fill=pal["accent"])
        d.text((MARGIN+36, by), item, font=font, fill=pal["accent"])
        by += 36
    return y + len(items)*36 + 24


def draw_hint_box(d, y, text, pal):
    lines = []
    font = F("mincho", 18)
    line = ""
    for ch in text:
        test = line + ch
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > BODY_W - 50:
            lines.append(line)
            line = ch
        else:
            line = test
    if line:
        lines.append(line)
    box_h = len(lines) * 26 + 16
    d.rounded_rectangle([(MARGIN, y), (W-MARGIN, y+box_h)], radius=6, fill=pal["hint_bg"])
    d.line([(MARGIN, y), (MARGIN, y+box_h)], fill=pal["hint_border"], width=4)
    ty = y + 8
    for ln in lines:
        d.text((MARGIN+16, ty), ln, font=font, fill=pal.get("hint_text", pal["text"]))
        ty += 26
    return y + box_h + 8


def draw_skill_box(d, y, name, cond, desc, pal):
    font_name = F("mincho_b", 24)
    font_cond = F("goth_m", 16)
    font_desc = F("mincho", 18)
    max_w = BODY_W - 50
    desc_lines = []
    line_colors = []
    for para in desc.split("\n"):
        is_note = para.lstrip().startswith("※")
        if not para:
            desc_lines.append("")
            line_colors.append(pal["text"])
            continue
        line = ""
        for ch in para:
            test = line + ch
            if d.textlength(test, font=font_desc) > max_w and line:
                desc_lines.append(line)
                line_colors.append(pal["accent"] if is_note else pal["text"])
                line = ch
            else:
                line = test
        if line:
            desc_lines.append(line)
            line_colors.append(pal["accent"] if is_note else pal["text"])
    box_h = 40 + 22 + len(desc_lines)*26 + 16
    d.rounded_rectangle([(MARGIN, y), (W-MARGIN, y+box_h)], radius=6, fill=pal["skill_bg"],
                        outline=pal["skill_border"], width=1)
    d.text((MARGIN+14, y+10), name, font=font_name, fill=pal["section"])
    d.text((MARGIN+14, y+42), cond, font=font_cond, fill=pal.get("skill_cond", (120,120,120)))
    ty = y + 68
    for ln, color in zip(desc_lines, line_colors):
        d.text((MARGIN+14, ty), ln, font=font_desc, fill=color)
        ty += 26
    return y + box_h + 8


def make_charsheet(role, subtitle, tag_text, pal, sections, extra_decor=None):
    """Generate a character sheet PNG.

    sections: list of (type, data) tuples:
      ("title", "text")
      ("body", ("text", [highlight_phrases]))
      ("mission", ["item1", "item2", ...])
      ("hint", "text")
      ("skill", ("name", "condition", "description"))

    extra_decor returns header_y_offset (pixels to shift header down).
    """
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)

    # Border
    d.rectangle([(0, 0), (W-1, H-1)], outline=pal["border"], width=3)

    # Decoration (background layer — runs BEFORE header text)
    hdr_offset = 0
    if extra_decor:
        result = extra_decor(img, d, pal)
        if result:
            hdr_offset = result
        d = ImageDraw.Draw(img)  # refresh after potential pixel-level ops

    # Header band
    d.rectangle([(0, hdr_offset), (W, HEADER_H + hdr_offset)], fill=pal["header_bg"])

    # Tag
    tag_font = F("goth_m", 16)
    tbbox = d.textbbox((0, 0), tag_text, font=tag_font)
    tw = tbbox[2] - tbbox[0]
    tx = W - MARGIN - tw - 16
    d.rounded_rectangle([(tx-8, 18+hdr_offset), (tx+tw+8, 42+hdr_offset)], radius=4,
                        fill=pal["tag_bg"], outline=pal.get("tag_border", pal["tag_fg"]), width=1)
    d.text((tx, 19+hdr_offset), tag_text, font=tag_font, fill=pal["tag_fg"])

    # Role name
    d.text((MARGIN, 24+hdr_offset), role, font=F("mincho_b", 40), fill=pal["header_fg"])
    # Subtitle
    d.text((MARGIN, 72+hdr_offset), subtitle, font=F("mincho", 18),
           fill=(*pal["header_fg"][:3],) if len(pal["header_fg"]) == 3 else pal["header_fg"])

    # Sections
    y = HEADER_H + hdr_offset + 20
    for stype, sdata in sections:
        if stype == "title":
            y = draw_section_title(d, y, sdata, pal)
        elif stype == "body":
            text, highlights = sdata
            y = draw_body_text(d, y, text, pal, highlights)
            y += 4
        elif stype == "mission":
            y = draw_mission_box(d, y, sdata, pal)
        elif stype == "hint":
            y = draw_hint_box(d, y, sdata, pal)
        elif stype == "skill":
            name, cond, desc = sdata
            y = draw_skill_box(d, y, name, cond, desc, pal)

    if pal["bg"][0] > 100:
        paper_noise(img, amount=3, seed=42)
    return img


# ── Extra decoration functions ──

def decor_evil_alpha(img, d, pal):
    """Cracked veins + blood drip + bottom bleed — organic horror"""
    w, h = img.size
    bl = pal["blood_line"]
    # Thick blood band under header
    for dy in range(8):
        a = 1.0 - dy / 8
        for x in range(w):
            c = tuple(int(bl[i]*a + pal["bg"][i]*(1-a)) for i in range(3))
            d.point((x, HEADER_H + dy), fill=c)
    # Branching veins (left + right)
    for seed, start_x, drift_range in [(31, 30, (15, 55)), (53, w-30, (w-55, w-15))]:
        rnd = random.Random(seed)
        vx = start_x
        for vy in range(HEADER_H + 8, h - 60):
            vx += rnd.choice([-2, -1, 0, 0, 1, 2])
            vx = max(drift_range[0], min(drift_range[1], vx))
            a = 0.5 + 0.3 * math.sin(vy * 0.015)
            c = tuple(int(pal["bg"][i]*(1-a) + bl[i]*a) for i in range(3))
            for dx in range(-2, 3):
                d.point((vx+dx, vy), fill=c)
            if rnd.random() < 0.03:
                blen = rnd.randint(10, 40)
                bdir = 1 if vx < w//2 else -1
                for bx in range(blen):
                    ba = a * (1 - bx/blen)
                    bc = tuple(int(pal["bg"][i]*(1-ba) + bl[i]*ba) for i in range(3))
                    d.point((vx + bx*bdir, vy + bx//3), fill=bc)
    # Bottom bleed (stronger)
    for y in range(h-80, h):
        t = (y - (h-80)) / 80
        c = tuple(int(pal["bg"][i] + (100, 15, 10)[i] * t) for i in range(3))
        c = tuple(max(0, min(255, v)) for v in c)
        d.line([(0, y), (w, y)], fill=c)
    return 0


def decor_evil_beta(img, d, pal):
    """Giant 覗 watermark + concentric circles + ritual feel"""
    w, h = img.size
    cx, cy = w//2, h//2 + 40
    # Massive 覗 character — very visible
    big_font = F("mincho_b", 400)
    bbox = d.textbbox((0, 0), "覗", font=big_font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    # Draw directly at high opacity
    d.text((cx - tw//2, cy - th//2 - 40), "覗", font=big_font, fill=(60, 16, 32))
    # Concentric circles (thick, visible)
    for r in (220, 170, 120, 70, 30):
        lw = 2 if r > 100 else 1
        c = (60, 18, 35)
        d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=c, width=lw)
    # Radial lines
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        sx = cx + int(30 * math.cos(rad))
        sy = cy + int(30 * math.sin(rad))
        ex = cx + int(240 * math.cos(rad))
        ey = cy + int(240 * math.sin(rad))
        d.line([(sx, sy), (ex, ey)], fill=(50, 15, 28), width=1)
    # Side borders: double vertical lines
    d.line([(12, HEADER_H), (12, h-4)], fill=(80, 20, 40), width=2)
    d.line([(16, HEADER_H), (16, h-4)], fill=(50, 14, 28), width=1)
    d.line([(w-12, HEADER_H), (w-12, h-4)], fill=(80, 20, 40), width=2)
    d.line([(w-16, HEADER_H), (w-16, h-4)], fill=(50, 14, 28), width=1)
    return 0


def decor_evil_gamma(img, d, pal):
    """Thick warning stripes + ash cloud + glow + X mark — maximum impact"""
    w, h = img.size
    stripe_h = 16
    sw = 24
    # Top warning stripe (thick)
    for x in range(0, w, sw*2):
        d.rectangle([(x, 0), (x+sw, stripe_h)], fill=pal["stripe1"])
        d.rectangle([(x+sw, 0), (x+sw*2, stripe_h)], fill=pal["stripe2"])
    # Bottom warning stripe (thick)
    for x in range(0, w, sw*2):
        d.rectangle([(x, h-stripe_h), (x+sw, h)], fill=pal["stripe1"])
        d.rectangle([(x+sw, h-stripe_h), (x+sw*2, h)], fill=pal["stripe2"])
    # Ash cloud (many particles, varied size)
    rnd = random.Random(77)
    for _ in range(80):
        px = rnd.randint(20, w-20)
        py = rnd.randint(HEADER_H+stripe_h+20, h-80)
        sz = rnd.randint(2, 10)
        opacity = rnd.uniform(0.2, 0.6)
        c = tuple(int(pal["bg"][i]*(1-opacity) + (120, 50, 35)[i]*opacity) for i in range(3))
        d.ellipse([(px, py), (px+sz, py+sz)], fill=c)
    # Red glow band under header (thick, bright)
    glow_y = HEADER_H + stripe_h
    for dy in range(10):
        a_base = 1.0 - dy / 10
        for x in range(w):
            t = abs(x - w/2) / (w/2)
            a = max(0, a_base * (1.0 - t*0.8))
            r = int(220 * a)
            g = int(40 * a)
            b = int(30 * a)
            c = (max(0, min(255, pal["bg"][0]+r)), max(0, min(255, pal["bg"][1]+g)), max(0, min(255, pal["bg"][2]+b)))
            d.point((x, glow_y + dy), fill=c)
    # Bottom decay (strong)
    for y in range(h-100, h-stripe_h):
        t = (y - (h-100)) / 84
        c = tuple(int(pal["bg"][i] + (120, 20, 15)[i] * t) for i in range(3))
        c = tuple(max(0, min(255, v)) for v in c)
        d.line([(0, y), (w, y)], fill=c)
    # Big X over the page (faint, ominous)
    xc = (100, 22, 18)
    d.line([(40, HEADER_H+stripe_h+20), (w-40, h-stripe_h-20)], fill=xc, width=3)
    d.line([(w-40, HEADER_H+stripe_h+20), (40, h-stripe_h-20)], fill=xc, width=3)
    return stripe_h


# ── Content data ──

INVESTIGATOR_INITIAL = [
    ("title", "あなたの背景"),
    ("body", (
        "あなたは調査組織の正規隊員だ。通信と設備の専門家として、これまで数多くの現場を踏んできた。\n\n"
        "今回の任務は、連絡が途絶えた先遣隊の捜索。先遣隊には同僚がいた──一緒に訓練を受け、何度も現場を共にした仲間だ。\n\n"
        "「必ず連れて帰る」。その一心で、あなたはこの施設に降りた。",
        ["先遣隊の捜索"])),
    ("title", "あなたの状況"),
    ("body", (
        "施設に足を踏み入れた瞬間、出口が閉ざされた。\n\n"
        "先遣隊は──かろうじて人の形を留めていたが、体のほとんどが灰のように崩壊した状態で見つかった。同僚のものと思われる装備が、その傍らに落ちている。\n\n"
        "身元の特定は不可能。何がこの人たちをこんな姿に変えたのか。",
        ["灰のように崩壊した状態"])),
    ("title", "目　標"),
    ("mission", [
        "施設を調査し、ここで何が起きたのかを突き止める",
        "同僚に何が起きたのか、その真相を知る",
        "この施設の関係者がメンバー内にいるなら、特定し確保する",
        "この施設から脱出する手段を見つける",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "あなたは正規の調査メンバーだ。実務的で冷静な態度を取りつつ、同僚への思いが時折にじむ。"
     "全員の中で最も「調査のプロ」であり、発見した証拠の整理・分析は得意分野。"
     "金庫の開錠は誰と一緒の時に使うかが駆け引きになる。\n"
     "自己紹介の際、「施設関係者の特定・確保」の任務を全員に公表してよい。"),
    ("title", "スキル"),
    ("skill", ("開　錠", "探索フェーズ中 ／ 金庫マスで使用 ／ 2回",
               "鍵付きの金庫を開けることができる。バディ調査中に使用した場合、ペア相手にも中身が見える。")),
]

INVESTIGATOR_UPDATE = [
    ("title", "状況の変化"),
    ("body", (
        "調査本部からの通信が入った。\n\n"
        "「本来の調査メンバーは3名。4人目は想定外の存在だ」\n\n"
        "──誰かが、この中に紛れ込んでいる。",
        ["4人目は想定外の存在", "紛れ込んでいる"])),
    ("title", "あなたの行動についての報告"),
    ("body", (
        "昨夜、あなたは通信復旧のため一人で施設内を歩き回っていた。"
        "設備の再点検が目的だったが、誰かに見られていた可能性がある。\n\n"
        "この行動が、あなたへの疑いの材料にされるかもしれない。",
        ["一人で施設内を歩き回っていた", "疑いの材料"])),
    ("title", "あなたに訪れた変化"),
    ("mission", [
        "この4人の中に、紛れ込んだ者がいる",
        "先遣隊を壊したのは人の仕業ではないかもしれない",
        "あなた自身は正規メンバーだが、それを証明する手段がない",
    ]),
    ("title", "目標（更新）"),
    ("mission", [
        "同僚の死の犯人を特定する",
        "紛れ込んだ4人目を特定し、確保する",
        "生きてこの研究所から出る",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "疑うべきは「4人目」だ。だが、あなたにも自分が正規だと証明する手段がない。"
     "実績と態度で信頼を勝ち取れ。あなたが握る証拠の量が、発言力の源泉だ。"),
    ("title", "スキル（変更なし）"),
    ("skill", ("開　錠", "探索フェーズ中 ／ 金庫マスで使用 ／ 2回",
               "鍵付きの金庫を開けることができる。バディ調査中に使用した場合、ペア相手にも中身が見える。")),
]

PROFESSOR_INITIAL = [
    ("title", "あなたの背景"),
    ("body", (
        "あなたは認知科学の権威だ。知覚と意識の研究に半生を捧げてきた。\n\n"
        "先遣隊の通信途絶という事態に、"
        "あなたの専門知識が求められたからだ。\n\n"
        "だが、本当の理由はもうひとつある。この施設の研究資料に、"
        "あなた自身の論文が引用元として使われている形跡があった。"
        "自分の研究が何に転用されたのか──それを確かめたい。",
        ["あなた自身の論文が引用元"])),
    ("title", "あなたの状況"),
    ("body", (
        "施設に入った途端、出口が封鎖された。\n\n"
        "先遣隊は灰のように崩壊した姿で発見された。この崩壊現象は、"
        "あなたの研究分野──知覚と意識の境界──に触れる何かを示唆している。\n\n"
        "施設のあちこちに研究資料が散在している。"
        "この施設で何が研究されていたのか──あなたの専門知識なら、読み解けるかもしれない。",
        [])),
    ("title", "目　標"),
    ("mission", [
        "自身の研究が悪用されている証拠を掴む",
        "施設の謎を調査する",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "あなたは学者だ。冷静な分析と知識の深さで場をリードできる。"
     "研究資料の収集と査読が最大の武器。査読結果をどこまで共有するかが駆け引きになる。"
     "ただし、あまり情報を出し過ぎると「施設関係者なのでは？」と疑われてしまうかもしれない。"),
    ("title", "スキル"),
    ("skill", ("査　読", "研究資料カード入手後 ／ 回数無制限",
               "研究資料カードの隠された情報を読み解き、追加情報を獲得する。\n"
               "※査読結果は口頭でのみ共有可能。元のカードや原本は他PLに見せられません。\n"
               "※各フェーズ終了時にGMから査読結果が配布されます。")),
]

PROFESSOR_UPDATE = [
    ("title", "状況の変化"),
    ("body", (
        "調査本部からの通信が入った。\n\n"
        "「本来の調査メンバーは3名。4人目は想定外の存在だ」\n\n"
        "──誰かが、この中に紛れ込んでいる。",
        ["4人目は想定外の存在", "紛れ込んでいる"])),
    ("title", "あなたが目撃したこと"),
    ("body", (
        "昨夜、調査隊員が一人で施設内を歩いているのを見かけた。\n\n"
        "声をかける前に姿を見失った。何をしていたのかは分からない。",
        ["調査隊員が一人で施設内を歩いている"])),
    ("title", "あなたに訪れた変化"),
    ("mission", [
        "この4人の中に、紛れ込んだ者がいる",
        "あなたの研究が施設に使われている──「関係者」と疑われるかもしれない",
        "調査隊員の単独行動が気になる",
    ]),
    ("title", "目標（更新）"),
    ("mission", [
        "全ての研究資料を入手、または閲覧する",
        "崩壊の元凶を突き止め、排除する",
        "4人目の正体を特定する",
        "生きてこの研究所から出る",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "査読を続けるほど真相に近づくが、知識を披露するほど"
     "「なぜそこまで知っている？」と疑われる可能性がある。"),
    ("title", "スキル（変更なし）"),
    ("skill", ("査　読", "研究資料カード入手後 ／ 回数無制限",
               "研究資料カードの隠された情報を読み解き、追加情報を獲得する。\n"
               "※査読結果は口頭でのみ共有可能。元のカードや原本は他PLに見せられません。\n"
               "※各フェーズ終了時にGMから査読結果が配布されます。")),
]

JOURNALIST_INITIAL = [
    ("title", "あなたの背景"),
    ("body", (
        "科学雑誌の記者。"
        "先遣隊失踪事件のスクープを嗅ぎつけ、同行取材枠をもぎ取って参加した。"
        "取材現場の経験はあるが、こんな施設は初めてだ。\n\n"
        "隠された真実を、自分の目で確かめ、自分の言葉で伝えたい──"
        "その使命感が、あなたをここに連れてきた。",
        [])),
    ("title", "あなたの状況"),
    ("body", (
        "施設に入った途端、出口が封鎖された。\n\n"
        "先遣隊は灰のように崩壊した姿で見つかった。"
        "科学の知識で説明できる範囲を、明らかに超えている。\n\n"
        "この施設で何が起きたのか──記者として、真実を明らかにしなければならない。",
        [])),
    ("title", "目　標"),
    ("mission", [
        "施設の実態を取材し記録する",
        "先遣隊に何が起きたか真相に迫る",
        "脱出手段を見つける",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "あなたは記者だ。人から情報を引き出す質問力が武器になる。"
     "誰に何を聞くか、得た情報をどこまで共有するかが駆け引きの鍵。"
     "中立的な立場を活かせ。"),
    ("title", "スキル"),
    ("skill", ("査　読", "固有ターン限定 ／ 最大2回",
               "研究資料カードから追加情報を読み解く。GMから口頭で査読結果を受け取る。\n"
               "※査読結果は口頭でのみ共有可能。元のカードや原本は他PLに見せられません。")),
]

JOURNALIST_UPDATE_1 = [
    ("title", "あなたに起きたこと"),
    ("body", (
        "頭の中で何かが弾けた。\n\n"
        "知っている。自分はこの施設に囚われていた存在だ。"
        "先遣隊を覗き、彼らの力と知識を奪った。\n\n"
        "そしてこの「科学ジャーナリスト」の全ての力を奪い、"
        "その身体を模倣した。\n\n"
        "もうひとつ。この施設のどこかに、自分と同じ存在がもう1体いる。"
        "誰かは分からない。だが、空洞の気配を感じる。",
        ["この施設に囚われていた存在",
         "全ての力を奪い、その身体を模倣した",
         "自分と同じ存在がもう1体いる"])),
    ("title", "あなたが知っていること"),
    ("body", (
        "先遣隊の侵入で封印が緩み、自分は容器から脱出した。"
        "だが施設の防衛機能が作動し、封鎖された。"
        "一人では外に出られなかった。\n\n"
        "ジャーナリストの残骸──灰の塊──は施設内にまだ残っている。"
        "発見されれば、自分の存在の証拠になる。\n\n"
        "封鎖中に施設内をくまなく探索した。"
        "施設の構造と物品の配置はある程度把握している。\n\n"
        "施設の最奥に封印装置がある。"
        "誰かをそこで封印すれば、封鎖は解除される。\n\n"
        "施設の区画間には自動認証扉がある。"
        "この扉は空洞検知──求心力を持たない存在を検知する機構で動作する。\n\n"
        "過去にもう1体、この施設から脱走した記録がある。"
        "4人目は、おそらくその個体だろう。",
        ["ジャーナリストの残骸", "灰の塊", "自分の存在の証拠になる",
         "封印装置", "誰かをそこで封印すれば、封鎖は解除される",
         "自動認証扉", "空洞検知", "もう1体、この施設から脱走した"])),
    ("title", "あなたの行動についての報告"),
    ("body", (
        "昨夜、この器の持ち主は一人で施設内を歩き回っていた。"
        "だからこそ疑われずに体を奪うことが出来たわけだが、"
        "出歩くところを誰かに見られていた可能性がある。",
        ["一人で施設内を歩き回っていた"])),
]

JOURNALIST_UPDATE_2 = [
    ("title", "目標（全面変更）"),
    ("mission", [
        "正体を秘匿する",
        "自分以外の誰かを封印させ、施設から脱出する",
        "4人目の正体──おそらくもう一人の同種──を見極める",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "Phase 0〜2の自分は本物の人間だった。急な言動変化は疑われる。"
     "脱出には誰かを封印装置に送り込む必要がある──"
     "自分以外の誰かに疑いが集まるよう立ち回れ。"),
    ("title", "スキル（変更）"),
    ("skill", ("査　読", "固有ターン限定 ／ 最大2回",
               "研究資料カードから追加情報を読み解く。GMから口頭で査読結果を受け取る。\n"
               "※査読結果は口頭でのみ共有可能。元のカードや原本は他PLに見せられません。")),
]

FOLKLORIST_INITIAL = [
    ("title", "あなたの背景"),
    ("body", (
        "あなたは民俗学者だ。「覗き」「魂抜き」「依代」──人に化ける異形の伝承を追い続けてきた。\n\n"
        "なぜか、この施設に引き寄せられた。理由は自分でも分からない。"
        "ただ、ここに来なければならないという確信だけがあった。",
        [])),
    ("title", "あなたの秘密"),
    ("body", (
        "あなたは調査メンバーのデータを改ざんし、4人目として紛れ込んだ。"
        "なぜそうせざるを得なかったのかは分からない。"
        "だが、この事実が露見すれば、あなたの立場は一気に危うくなる。",
        ["データを改ざん", "4人目として紛れ込んだ"])),
    ("title", "あなたの状況"),
    ("body", (
        "施設に入った途端、出口が封鎖された。\n\n"
        "先遣隊は灰のように崩壊した姿で見つかった。"
        "この崩壊の在り方に、あなたは言語化できない既知感を覚える。伝承で読んだ何かに似ている──が、思い出せない。",
        ["言語化できない既知感"])),
    ("title", "目　標"),
    ("mission", [
        "施設からの脱出手段を調査する",
        "この既知感の正体──記憶の手がかりを探す",
        "データ改ざんの事実を秘匿する",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "あなたは伝承の研究者として参加している。"
     "施設への既知感やデータ改ざんの事実を悟られないよう振る舞え。"
     "なぜ自分がここに来なければならなかったのか──その答えが、この施設のどこかにある。"),
    ("title", "スキル"),
    ("skill", ("気配感知", "自動発動 ／ GM通知",
               "あなたはときおり、説明のつかない直感に襲われる。\n"
               "特定のタイミングでGMから情報を受け取る。")),
]

FOLKLORIST_UPDATE = [
    ("title", "あなたに起きたこと"),
    ("body", (
        "調査本部からの通信が入った。「本来の調査メンバーは3名。4人目は想定外の存在だ」\n\n"
        "──4人目は、あなただ。\n\n"
        "そして同時に、頭の中で何かが弾けた。\n\n"
        "知っている。この施設を。封印装置の場所を。"
        "自分がかつてここにいたことを──そして、逃げ出したことを。\n\n"
        "あなたは人間ではなかった。しかし、あなたは誰も壊さずにここまで来た。"
        "保ち続けてきた。\n\n"
        "もうひとつ。この施設のどこかに、自分と同じ存在が隠れ潜んでいる。\n\n"
        "壊す者を封印しない限り、この施設から出ることはできない。",
        ["4人目は、あなただ", "あなたは人間ではなかった",
         "誰も壊さずにここまで来た", "自分と同じ存在が隠れ潜んでいる",
         "封印しない限り、この施設から出ることはできない"])),
    ("title", "あなたが目撃したこと"),
    ("body", (
        "昨夜、ジャーナリストが一人で施設内を歩いているのを見かけた。\n\n"
        "声をかける前に姿を見失った。何をしていたのかは分からない。",
        ["ジャーナリストが一人で施設内を歩いている"])),
    ("title", "目標（全面変更）"),
    ("mission", [
        "もう1体の同種を見つけ出し、封印する",
        "自分自身の正体を秘匿する",
        "全員で生きて脱出する",
    ]),
    ("title", "プレイングのポイント"),
    ("hint",
     "人数不一致の「犯人」はあなた自身だ。だが名乗れば正体に直結する。"
     "調査隊員は「施設関係者の確保」を任務に掲げている──正体を明かせば確保対象になりかねない。"
     "この施設にいる壊す者の存在を、あなただけが明確に認知している。"),
    ("title", "想起（自動発火済み）"),
    ("skill", ("想　起", "Phase 3 自動発火 ／ 追加使用なし",
               "封印装置が最奥区画にあることを思い出した。この情報をどう使うかはあなた次第。")),
]


# ── 気配感知カード（民俗学者専用・横長スリップ） ──

PAL_KEHAI = dict(
    bg=(12, 18, 38), frame=(60, 80, 130),
    title=(180, 200, 240), subtitle=(120, 140, 180),
    text=(235, 230, 220), accent=(160, 190, 255),
    line=(50, 65, 110),
)

KEHAI_CARDS = [
    {
        "tag": "固有ターン1",
        "title": "気配感知",
        "body": "──この施設のどこかに、何かが隠れている。\n\n"
                "理由は分からない。だが確信がある。\n"
                "人ではない何かの気配を、あなたは感じ取っている。",
    },
    {
        "tag": "固有ターン2",
        "title": "気配感知",
        "body": "──調査隊の誰かが、入れ替わっている。\n\n"
                "一夜目だ。あの夜を境に、気配が変わった。\n"
                "人だったものが、人ではなくなっている。\n"
                "あなたにはそれが分かる。",
    },
]


def make_kehai_card(data):
    KW, KH = 840, 360
    M = 40
    img = Image.new("RGB", (KW, KH), PAL_KEHAI["bg"])
    d = ImageDraw.Draw(img)

    d.rectangle([(0, 0), (KW-1, KH-1)], outline=PAL_KEHAI["frame"], width=2)
    d.rectangle([(6, 6), (KW-7, KH-7)], outline=PAL_KEHAI["line"], width=1)

    for i in range(3):
        cx = KW // 2
        ry = 30 + i * 8
        rx = 320 - i * 40
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            x = cx + int(rx * math.cos(rad))
            y = 20 + int(ry * 0.3 * math.sin(rad))
            alpha = max(0, 30 - i * 10)
            if 0 <= x < KW and 0 <= y < KH:
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (min(255, r+alpha), min(255, g+alpha+5), min(255, b+alpha+15)))

    tag_font = F("goth_m", 14)
    tag_text = data["tag"]
    tbbox = d.textbbox((0, 0), tag_text, font=tag_font)
    tw = tbbox[2] - tbbox[0]
    tx = KW - M - tw - 8
    d.rounded_rectangle([(tx-6, 16), (tx+tw+6, 38)], radius=3,
                        fill=PAL_KEHAI["frame"], outline=PAL_KEHAI["accent"], width=1)
    d.text((tx, 17), tag_text, font=tag_font, fill=PAL_KEHAI["accent"])

    d.text((M, 16), "── 民俗学者専用 ──", font=F("goth_m", 13), fill=PAL_KEHAI["subtitle"])

    title_font = F("mincho_b", 32)
    d.text((M, 50), data["title"], font=title_font, fill=PAL_KEHAI["title"])

    d.line([(M, 92), (KW-M, 92)], fill=PAL_KEHAI["line"], width=1)

    body_font = F("mincho", 20)
    max_w = KW - M * 2
    y = 106
    for para in data["body"].split("\n"):
        if not para:
            y += 14
            continue
        is_em = para.startswith("──")
        color = PAL_KEHAI["accent"] if is_em else PAL_KEHAI["text"]
        line = ""
        for ch in para:
            test = line + ch
            if d.textlength(test, font=body_font) > max_w and line:
                d.text((M, y), line, font=body_font, fill=color)
                y += 30
                line = ch
            else:
                line = test
        if line:
            d.text((M, y), line, font=body_font, fill=color)
            y += 30

    paper_noise(img, amount=2, seed=99)
    return img


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "charsheet")
    os.makedirs(OUT, exist_ok=True)

    # ── 調査隊員 ──
    img = make_charsheet(
        "調 査 隊 員", "御影村研究所封鎖事案 ── 第二次調査チーム", "初期配布",
        PAL_NORMAL, INVESTIGATOR_INITIAL)
    img.save(os.path.join(OUT, "investigator_initial.png"))
    print("  investigator_initial.png")

    img = make_charsheet(
        "調 査 隊 員", "御影村研究所封鎖事案 ── 第二次調査チーム", "Phase 3 更新",
        PAL_NORMAL, INVESTIGATOR_UPDATE)
    img.save(os.path.join(OUT, "investigator_update.png"))
    print("  investigator_update.png")

    # ── 大学教授 ──
    img = make_charsheet(
        "大 学 教 授", "御影村研究所封鎖事案 ── 第二次調査チーム", "初期配布",
        PAL_NORMAL, PROFESSOR_INITIAL)
    img.save(os.path.join(OUT, "professor_initial.png"))
    print("  professor_initial.png")

    img = make_charsheet(
        "大 学 教 授", "御影村研究所封鎖事案 ── 第二次調査チーム", "Phase 3 更新",
        PAL_NORMAL, PROFESSOR_UPDATE)
    img.save(os.path.join(OUT, "professor_update.png"))
    print("  professor_update.png")

    # ── 民俗学者 ──
    img = make_charsheet(
        "民 俗 学 者", "御影村研究所封鎖事案 ── 第二次調査チーム", "初期配布",
        PAL_NORMAL, FOLKLORIST_INITIAL)
    img.save(os.path.join(OUT, "folklorist_initial.png"))
    print("  folklorist_initial.png")

    img = make_charsheet(
        "民 俗 学 者", "── あなたは、人間ではなかった ──", "Phase 3 覚醒",
        PAL_GOOD, FOLKLORIST_UPDATE)
    img.save(os.path.join(OUT, "folklorist_update.png"))
    print("  folklorist_update.png")

    # ── 科学ジャーナリスト ──
    img = make_charsheet(
        "ジャーナリスト", "御影村研究所封鎖事案 ── 第二次調査チーム", "初期配布",
        PAL_NORMAL, JOURNALIST_INITIAL)
    img.save(os.path.join(OUT, "journalist_initial.png"))
    print("  journalist_initial.png")

    img = make_charsheet(
        "ジャーナリスト", "── あなたは、人間ではなかった ──", "Phase 3 覚醒 ①",
        PAL_EVIL_ALPHA, JOURNALIST_UPDATE_1, extra_decor=decor_evil_alpha)
    img.save(os.path.join(OUT, "journalist_update_1.png"))
    print("  journalist_update_1.png")

    img = make_charsheet(
        "ジャーナリスト", "── あなたは、人間ではなかった ──", "Phase 3 覚醒 ②",
        PAL_EVIL_ALPHA, JOURNALIST_UPDATE_2, extra_decor=decor_evil_alpha)
    img.save(os.path.join(OUT, "journalist_update_2.png"))
    print("  journalist_update_2.png")

    # ── 気配感知カード ──
    for i, data in enumerate(KEHAI_CARDS, 1):
        img = make_kehai_card(data)
        path = os.path.join(OUT, f"kehai_{i}.png")
        img.save(path)
        print(f"  kehai_{i}.png ({img.size[0]}x{img.size[1]})")

    print("\n完了")
