# -*- coding: utf-8 -*-
"""
Udonarium 検証データ生成スクリプト（PILのみ・cairosvg非依存）

生成物（本スクリプトと同フォルダ）:
  - map_table.zip   : フィールド（game-table）サンプル
  - clue_card.zip   : 裏表カード（card / front・back とも自前画像）

正解XML構造は実機エクスポート(card_sample / note_sample)との照合で確定済み。
  - game-table : 子要素なし・属性方式。imageIdentifier は拡張子なしハッシュ
  - card       : <node>方式。front/back の値は "ハッシュ.png"（拡張子あり）

zip仕様: フラット構造 / data.xml(UTF-8,XML宣言つき) / 画像名 = SHA-256hex + 拡張子
"""
import os, io, re, zipfile, hashlib
import xml.dom.minidom as MD
from xml.sax.saxutils import escape, quoteattr
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "C:/Windows/Fonts/meiryo.ttc"


def font(sz):
    return ImageFont.truetype(FONT_PATH, sz)


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def png_bytes(img):
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()


def wrap_draw(d, xy, text, fnt, fill, max_chars, line_h):
    """日本語向け簡易折り返し描画（max_chars文字で改行、\\nは段落区切り）"""
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


# ---------------- 画像生成 ----------------
def make_map_image():
    """地下研究施設レイアウト（00_concept.md の舞台・調査ギミックに対応）"""
    W = H = 1000
    img = Image.new("RGB", (W, H), (28, 30, 36))
    d = ImageDraw.Draw(img)
    step = 50
    for x in range(0, W + 1, step):
        d.line([(x, 0), (x, H)], fill=(44, 47, 55), width=1)
    for y in range(0, H + 1, step):
        d.line([(0, y), (W, y)], fill=(44, 47, 55), width=1)
    wall, label, hall = (150, 156, 168), (212, 216, 224), (104, 110, 124)
    # 通路（縦メイン＋各室への接続）
    corridors = [
        (500, 200, 500, 880),   # 縦メイン通路
        (430, 385, 500, 385),   # 研究室 ←
        (500, 385, 570, 385),   # → 資料保管庫
        (430, 715, 500, 715),   # 観察室 ←
        (500, 715, 570, 715),   # → 隔離区画
    ]
    for x0, y0, x1, y1 in corridors:
        d.line([(x0, y0), (x1, y1)], fill=hall, width=5)
    # 区画（concept の調査ギミック対応を併記）
    rooms = [
        ((360, 80, 640, 200), "エントランス", "出口封鎖"),
        ((60, 250, 430, 520), "研究室", "研究資料カード"),
        ((570, 250, 940, 520), "資料保管庫", "鍵付き金庫×2"),
        ((60, 580, 430, 850), "観察室", "生体認証扉"),
        ((570, 580, 940, 850), "隔離区画", "生体認証扉"),
        ((360, 880, 640, 980), "封印室（最奥）", "封印装置"),
    ]
    for (x0, y0, x1, y1), name, gimmick in rooms:
        d.rectangle([x0, y0, x1, y1], outline=wall, width=3)
        d.text((x0 + 16, y0 + 12), name, font=font(30), fill=label)
        d.text((x0 + 16, y0 + 52), "▸ " + gimmick, font=font(22), fill=(150, 150, 160))
    d.text((36, 22), "MIMESIS ── 地下研究施設", font=font(40), fill=(236, 239, 246))
    return png_bytes(img)


def make_card_front(no, title, body):
    W, H = 600, 840
    img = Image.new("RGB", (W, H), (247, 244, 236))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 10, H - 10], outline=(60, 55, 48), width=4)
    d.rectangle([10, 10, W - 10, 124], fill=(120, 30, 38))
    d.text((40, 38), "手がかり #%d" % no, font=font(46), fill=(245, 240, 232))
    d.text((40, 168), title, font=font(40), fill=(40, 36, 32))
    d.line([(40, 232), (W - 40, 232)], fill=(160, 150, 138), width=2)
    wrap_draw(d, (40, 268), body, font(30), (44, 40, 36), max_chars=17, line_h=46)
    return png_bytes(img)


def make_card_back():
    W, H = 600, 840
    img = Image.new("RGB", (W, H), (22, 24, 30))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, W - 20, H - 20], outline=(90, 80, 110), width=4)
    cx, cy = W / 2, H / 2 - 40
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=(120, 108, 150), width=5)
    d.text((cx - 42, cy - 92), "?", font=font(150), fill=(150, 138, 180))
    d.text((cx - 150, H - 96), "MIMESIS", font=font(40), fill=(110, 100, 135))
    return png_bytes(img)


# ---- キャラクター駒（PC番号＋役職＋職種アイコン） ----
def draw_icon(d, cx, cy, kind, color):
    """職種を表す記号的アイコンを図形で描画（写実イラストではない）"""
    r = 80
    if kind == "scroll":  # 民俗学者：巻物
        d.rounded_rectangle([cx - r, cy - 50, cx + r, cy + 50], radius=14,
                            outline=color, width=6)
        for x in (cx - r, cx + r):
            d.ellipse([x - 14, cy - 50, x + 14, cy + 50], outline=color, width=6)
        for dy in (-22, 0, 22):
            d.line([(cx - r + 26, cy + dy), (cx + r - 26, cy + dy)], fill=color, width=3)
    elif kind == "flashlight":  # 調査隊員：懐中電灯の光
        d.polygon([(cx - 60, cy - 70), (cx - 60, cy + 70), (cx + 70, cy + 40),
                   (cx + 70, cy - 40)], outline=color, width=6)
        d.rectangle([cx - 90, cy - 28, cx - 60, cy + 28], outline=color, width=6)
    elif kind == "cap":  # 大学教授：角帽
        d.polygon([(cx, cy - 56), (cx + 92, cy - 14), (cx, cy + 28),
                   (cx - 92, cy - 14)], outline=color, width=6)
        d.line([(cx, cy + 28), (cx, cy + 64)], fill=color, width=5)
        d.line([(cx, cy + 64), (cx + 40, cy + 64)], fill=color, width=5)
        d.line([(cx - 40, cy - 5), (cx - 40, cy + 60)], fill=color, width=5)
    elif kind == "book":  # 大学院生：開いた本
        d.line([(cx, cy - 50), (cx, cy + 60)], fill=color, width=5)
        for s in (-1, 1):
            d.polygon([(cx, cy - 50), (cx + s * 90, cy - 34),
                       (cx + s * 90, cy + 60), (cx, cy + 44)], outline=color, width=6)


def make_character_image(pc_no, role, kind, color):
    W = H = 512
    img = Image.new("RGB", (W, H), (244, 242, 238))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 8, H - 8], outline=color, width=10)
    # 上部帯：PC番号
    d.rectangle([8, 8, W - 8, 96], fill=color)
    d.text((28, 24), "PC%d" % pc_no, font=font(52), fill=(248, 246, 242))
    # 中央：職種アイコン
    draw_icon(d, W // 2, 270, kind, color)
    # 下部：役職名
    rw = d.textlength(role, font=font(52))
    d.text(((W - rw) / 2, 400), role, font=font(52), fill=(40, 38, 34))
    return png_bytes(img)


# ---------------- XML 組み立て ----------------
def xml_game_table(name, img_hash):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<game-table name=%s width="20" height="20" gridSize="50" '
        'imageIdentifier=%s backgroundImageIdentifier="" backgroundFilterType="" '
        'selected="true" gridType="0" gridColor="#000000e6"></game-table>'
        % (quoteattr(name), quoteattr(img_hash))
    )


def xml_character(name, img_hash):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<character location.name="table" location.x="100" location.y="100" '
        'posZ="0" rotate="0" roll="0">'
        '<data name="image">'
        '<data type="image" name="imageIdentifier">%s</data>'
        '</data>'
        '<data name="common">'
        '<data name="name">%s</data>'
        '<data name="size">1</data>'
        '</data>'
        '<data name="detail"></data>'
        '</character>'
        % (img_hash, escape(name))
    )


def xml_card(name, front_file, back_file):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<card location.x="0" location.y="0" location.name="table" posZ="0" '
        'rotate="0" zindex="0" state="0" owner="" isLock="">'
        '<node name="image">'
        '<node name="front" type="image">%s</node>'
        '<node name="back" type="image">%s</node>'
        '</node>'
        '<node name="common">'
        '<node name="name">%s</node>'
        '<node name="size">2</node>'
        '</node>'
        '<node name="detail"></node>'
        '</card>'
        % (escape(front_file), escape(back_file), escape(name))
    )


# ---------------- zip ----------------
def write_zip(path, xml_str, images):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("data.xml", xml_str.encode("utf-8"))
        for fn, b in images.items():
            z.writestr(fn, b)


# ---------------- 機械検証 ----------------
def verify_zip(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    res = []
    # C1 フラット構造
    res.append(("C1 flat", all("/" not in n for n in names)))
    # C2 data.xml が UTF-8 well-formed
    try:
        xml = z.read("data.xml").decode("utf-8")
        MD.parseString(xml)
        c2 = True
    except Exception:
        c2, xml = False, ""
    res.append(("C2 xml well-formed", c2))
    # C3 画像名 = SHA256(bytes)
    imgs = [n for n in names if n != "data.xml"]
    c3 = all(os.path.splitext(n)[0] == sha256_hex(z.read(n)) for n in imgs)
    res.append(("C3 name=sha256", c3))
    # C4 XML参照 ⊆ zip画像（identifier=拡張子除去で比較）
    img_ids = {os.path.splitext(n)[0] for n in imgs}
    refs = set(re.findall(r'imageIdentifier="([0-9a-f]{64})"', xml))          # game-table 属性
    refs |= {os.path.splitext(m)[0] for m in re.findall(r'>([0-9a-f]{64}\.png)<', xml)}  # card 要素(拡張子付)
    refs |= set(re.findall(r'>([0-9a-f]{64})<', xml))                         # character 要素(拡張子なし)
    c4 = len(refs) > 0 and refs <= img_ids
    res.append(("C4 refs subset imgs", c4))
    return res, names


def main():
    # ---- フィールド ----
    mb = make_map_image()
    mh = sha256_hex(mb)
    OUT = os.path.join(HERE, "outputs", "udonarium")
    os.makedirs(OUT, exist_ok=True)
    map_zip = os.path.join(OUT, "map_table.zip")
    write_zip(map_zip, xml_game_table("MIMESIS 地下研究施設", mh), {mh + ".png": mb})

    # ---- 裏表カード ----
    fb = make_card_front(
        1, "血の付いたナイフ",
        "食堂のテーブル下から発見された。\n刃には乾いた血痕。\n柄の指紋は拭き取られている。",
    )
    bb = make_card_back()
    fh, bh = sha256_hex(fb), sha256_hex(bb)
    card_zip = os.path.join(OUT, "clue_card.zip")
    write_zip(card_zip, xml_card("血の付いたナイフ", fh + ".png", bh + ".png"),
              {fh + ".png": fb, bh + ".png": bb})

    # ---- キャラクター駒 4体（PC番号＋役職＋職種アイコン） ----
    # (pc_no, 役職, スキル, アイコン種別, 枠色)  ※正体[善A/悪B]は駒に出さない
    ROLE_DEFS = [
        (1, "民俗学者", "想起", "scroll", (122, 92, 50)),
        (2, "調査隊員", "開錠", "flashlight", (54, 96, 120)),
        (3, "大学教授", "査読", "cap", (92, 70, 112)),
        (4, "大学院生", "覗き見", "book", (112, 78, 78)),
    ]
    char_zips = []
    for pc_no, role, skill, kind, color in ROLE_DEFS:
        cb = make_character_image(pc_no, role, kind, color)
        ch = sha256_hex(cb)
        cz = os.path.join(OUT, "char_pc%d.zip" % pc_no)
        write_zip(cz, xml_character(role, ch), {ch + ".png": cb})
        char_zips.append((cz, role, ch))

    print("=== 生成 ===")
    print("map_table.zip   image:", mh)
    print("clue_card.zip   front:", fh)
    print("                back :", bh)
    for cz, role, ch in char_zips:
        print("%-16s %s  %s" % (os.path.basename(cz), role, ch))

    print("\n=== 機械検証 ===")
    allok = True
    for path in (map_zip, card_zip) + tuple(c[0] for c in char_zips):
        res, names = verify_zip(path)
        print("[%s] entries=%s" % (os.path.basename(path), names))
        for label, ok in res:
            allok &= ok
            print("    %s %s" % ("OK " if ok else "NG ", label))
    print("\nRESULT:", "ALL PASS" if allok else "FAILED")


if __name__ == "__main__":
    main()
