# -*- coding: utf-8 -*-
"""
研究論文デザインのテイスト探索。design_card.make_paper の全 style を生成し、
1枚のコンタクトシート（比較一覧）にまとめる。取っ散らからないよう個別はサブフォルダへ隔離。

出力:
  outputs/design/paper_styles/paper_<style>.png   ... 各テイストのフルサイズ
  outputs/design/paper_styles_contact.png         ... 全テイスト一覧（固有ファイル）
"""
import os
from PIL import Image, ImageDraw, ImageFont
import design_card as dc

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_DIR = os.path.join(HERE, "outputs", "design", "paper_styles")
os.makedirs(STYLE_DIR, exist_ok=True)

# 各テイストの原本（無修正）を生成
thumbs = []
for name in dc.PAPER_STYLES:
    img = dc.make_paper(redacted=False, style=name)
    img.save(os.path.join(STYLE_DIR, "paper_%s.png" % name))
    thumbs.append((name, img))

# コンタクトシート
COLS = 4
TW = 360
TH = int(TW * 1414 / 1000)
PAD = 24
LABEL_H = 38
rows = (len(thumbs) + COLS - 1) // COLS
SW = COLS * TW + (COLS + 1) * PAD
SH = rows * (TH + LABEL_H + PAD) + PAD
sheet = Image.new("RGB", (SW, SH), (58, 60, 66))
d = ImageDraw.Draw(sheet)
flabel = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 26)

for i, (name, img) in enumerate(thumbs):
    r, c = divmod(i, COLS)
    x = PAD + c * (TW + PAD)
    y = PAD + r * (TH + LABEL_H + PAD)
    sheet.paste(img.resize((TW, TH)), (x, y))
    d.text((x + 4, y + TH + 6), name, font=flabel, fill=(238, 239, 244))

contact = os.path.join(HERE, "outputs", "design", "paper_styles_contact.png")
sheet.save(contact)
print("styles:", list(dc.PAPER_STYLES.keys()))
print("contact ->", contact)
