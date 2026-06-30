# -*- coding: utf-8 -*-
"""自己紹介シート（キャラクター導入カード）生成"""
import os, random
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

# ── Palette (shared with charsheet) ──
PAL = dict(
    bg=(245, 240, 225), header_bg=(26, 39, 68), header_fg=(245, 240, 225),
    text=(44, 36, 24), accent=(192, 57, 43), section=(26, 39, 68),
    border=(26, 39, 68),
    tag_bg=(26, 39, 68), tag_fg=(245, 240, 225),
    spec_bg=(235, 232, 220), spec_border=(26, 39, 68),
)

W = 840
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


def wrap_text(d, text, font, max_w):
    lines = []
    for raw_line in text.split("\n"):
        if not raw_line.strip():
            lines.append("")
            continue
        line = ""
        for ch in raw_line:
            test = line + ch
            bbox = d.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)
    return lines


def draw_section_title(d, y, text):
    d.text((MARGIN, y), f"── {text} ──", font=F("mincho_b", 22), fill=PAL["section"])
    d.line([(MARGIN, y + 30), (W - MARGIN, y + 30)], fill=PAL["section"], width=2)
    return y + 40


def draw_body(d, y, text):
    font = F("mincho", 20)
    lines = wrap_text(d, text, font, BODY_W)
    for line in lines:
        if not line:
            y += 14
            continue
        d.text((MARGIN, y), line, font=font, fill=PAL["text"])
        y += 30
    return y


def draw_spec_box(d, y, items):
    font = F("mincho_b", 20)
    item_h = 34
    box_h = len(items) * item_h + 20
    d.rounded_rectangle(
        [(MARGIN, y), (W - MARGIN, y + box_h)],
        radius=6, fill=PAL["spec_bg"])
    d.line([(MARGIN, y), (MARGIN, y + box_h)],
           fill=PAL["spec_border"], width=4)
    by = y + 12
    for item in items:
        d.text((MARGIN + 16, by), "▸", font=F("mincho_b", 16), fill=PAL["accent"])
        d.text((MARGIN + 36, by), item, font=font, fill=PAL["section"])
        by += item_h
    return y + box_h + 12


def make_intro_sheet(role, intro_text, specialties):
    tmp_img = Image.new("RGB", (W, 1200), PAL["bg"])
    tmp_d = ImageDraw.Draw(tmp_img)

    y = HEADER_H + 20
    y = draw_section_title(tmp_d, y, "自己紹介")
    y = draw_body(tmp_d, y, intro_text)
    y += 8
    y = draw_section_title(tmp_d, y, "専門領域")
    y = draw_spec_box(tmp_d, y, specialties)
    y += 20

    total_h = y + MARGIN
    total_h = max(total_h, 400)

    img = Image.new("RGB", (W, total_h), PAL["bg"])
    d = ImageDraw.Draw(img)

    d.rectangle([(0, 0), (W - 1, total_h - 1)], outline=PAL["border"], width=3)

    d.rectangle([(0, 0), (W, HEADER_H)], fill=PAL["header_bg"])

    tag_text = "自己紹介"
    tag_font = F("goth_m", 16)
    tbbox = d.textbbox((0, 0), tag_text, font=tag_font)
    tw = tbbox[2] - tbbox[0]
    tx = W - MARGIN - tw - 16
    d.rounded_rectangle([(tx - 8, 18), (tx + tw + 8, 42)], radius=4,
                        fill=PAL["tag_bg"], outline=PAL["tag_fg"], width=1)
    d.text((tx, 19), tag_text, font=tag_font, fill=PAL["tag_fg"])

    d.text((MARGIN, 24), role, font=F("mincho_b", 40), fill=PAL["header_fg"])
    d.text((MARGIN, 72), "御影村研究所封鎖事案 ── 第二次調査チーム",
           font=F("mincho", 18), fill=PAL["header_fg"])

    y = HEADER_H + 20
    y = draw_section_title(d, y, "自己紹介")
    y = draw_body(d, y, intro_text)
    y += 8
    y = draw_section_title(d, y, "専門領域")
    y = draw_spec_box(d, y, specialties)

    paper_noise(img, amount=3, seed=42)
    return img


# ── Content ──

INVESTIGATOR = dict(
    role="調 査 隊 員",
    intro=(
        "調査チーム所属の調査員。通信と電気設備の専門家として、"
        "これまで数多くの現場を踏んできた。\n\n"
        "今回の任務は、連絡が途絶えた先遣隊の捜索。"
        "先遣隊には一緒に訓練を受けた同僚がいる。"
        "何としても連れて帰る──その一心でここに来た。\n\n"
        "なお、この施設の関係者がチーム内にいる場合、"
        "特定し確保することも任務に含まれている。"
    ),
    specialties=[
        "通信機器・電気設備の操作と修理",
        "現場での調査・証拠収集の実務経験",
        "過去に複数の調査任務を経験",
    ],
)

PROFESSOR = dict(
    role="大 学 教 授",
    intro=(
        "認知科学の研究者。人間の知覚や意識がもたらす力の研究に半生を捧げてきた。\n\n"
        "先遣隊の通信途絶という事態に専門知識が求められ、調査に参加した。"
        "教え子である院生の参加には反対したが、強い志願を受けて同行を許した。\n\n"
        "施設に残された研究資料を読み解くことが、自分の役割だと考えている。"
    ),
    specialties=[
        "認知科学（知覚・意識がもたらす力の研究）",
        "研究資料の学術的読解・分析",
        "院生の指導教官",
    ],
)

FOLKLORIST = dict(
    role="民 俗 学 者",
    intro=(
        "「覗き」「魂抜き」「依代」──"
        "人に化ける異形の伝承を追い続けてきた学者。\n\n"
        "御影村にまつわる古い文献を調べるうち、"
        "この施設の存在を知った。"
        "伝承知識が調査の助けになるだろうと、チームに加わった。"
    ),
    specialties=[
        "異形の伝承・民間信仰の研究",
        "封印・依代・儀式に関する文献知識",
    ],
)

STUDENT = dict(
    role="大 学 院 生",
    intro=(
        "教授のゼミで認知科学を専攻している。"
        "フィールドワークの経験はあるが、こんな施設は初めてだ。\n\n"
        "教授の理論を間近で検証できる好機と捉え、"
        "好奇心から強く志願して参加した。"
        "自分の目で確かめ、自分の頭で考えたい。"
    ),
    specialties=[
        "認知科学専攻（教授の指導下）",
        "フィールドワーク・現地調査の経験",
        "若さゆえの好奇心と行動力",
    ],
)


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "intro_sheet")
    os.makedirs(OUT, exist_ok=True)

    for key, data in [
        ("investigator", INVESTIGATOR),
        ("professor", PROFESSOR),
        ("folklorist", FOLKLORIST),
        ("student", STUDENT),
    ]:
        img = make_intro_sheet(data["role"], data["intro"], data["specialties"])
        path = os.path.join(OUT, f"{key}.png")
        img.save(path)
        print(f"  {key}.png ({img.size[0]}x{img.size[1]})")

    print("\n完了")
