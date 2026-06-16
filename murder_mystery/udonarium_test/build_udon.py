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
    W = H = 1000
    img = Image.new("RGB", (W, H), (38, 40, 46))
    d = ImageDraw.Draw(img)
    step = 50
    for x in range(0, W + 1, step):
        d.line([(x, 0), (x, H)], fill=(55, 58, 66), width=1)
    for y in range(0, H + 1, step):
        d.line([(0, y), (W, y)], fill=(55, 58, 66), width=1)
    rooms = [
        ((60, 90, 460, 440), "ホール"),
        ((520, 90, 940, 320), "書斎"),
        ((520, 360, 940, 620), "食堂"),
        ((60, 490, 460, 940), "客間"),
        ((520, 660, 940, 940), "地下室"),
    ]
    for (x0, y0, x1, y1), name in rooms:
        d.rectangle([x0, y0, x1, y1], outline=(150, 156, 168), width=3)
        d.text((x0 + 16, y0 + 12), name, font=font(34), fill=(210, 214, 222))
    d.text((36, 24), "MIMESIS — 館 1F", font=font(42), fill=(235, 238, 245))
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


# ---------------- XML 組み立て ----------------
def xml_game_table(name, img_hash):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<game-table name=%s width="20" height="20" gridSize="50" '
        'imageIdentifier=%s backgroundImageIdentifier="" backgroundFilterType="" '
        'selected="true" gridType="0" gridColor="#000000e6"></game-table>'
        % (quoteattr(name), quoteattr(img_hash))
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
    refs = set(re.findall(r'imageIdentifier="([0-9a-f]{64})"', xml))
    refs |= {os.path.splitext(m)[0] for m in re.findall(r'>([0-9a-f]{64}\.png)<', xml)}
    c4 = len(refs) > 0 and refs <= img_ids
    res.append(("C4 refs subset imgs", c4))
    return res, names


def main():
    # ---- フィールド ----
    mb = make_map_image()
    mh = sha256_hex(mb)
    map_zip = os.path.join(HERE, "map_table.zip")
    write_zip(map_zip, xml_game_table("MIMESIS 館 1F", mh), {mh + ".png": mb})

    # ---- 裏表カード ----
    fb = make_card_front(
        1, "血の付いたナイフ",
        "食堂のテーブル下から発見された。\n刃には乾いた血痕。\n柄の指紋は拭き取られている。",
    )
    bb = make_card_back()
    fh, bh = sha256_hex(fb), sha256_hex(bb)
    card_zip = os.path.join(HERE, "clue_card.zip")
    write_zip(card_zip, xml_card("血の付いたナイフ", fh + ".png", bh + ".png"),
              {fh + ".png": fb, bh + ".png": bb})

    print("=== 生成 ===")
    print("map_table.zip   image:", mh)
    print("clue_card.zip   front:", fh)
    print("                back :", bh)

    print("\n=== 機械検証 ===")
    allok = True
    for path in (map_zip, card_zip):
        res, names = verify_zip(path)
        print("[%s] entries=%s" % (os.path.basename(path), names))
        for label, ok in res:
            allok &= ok
            print("    %s %s" % ("OK " if ok else "NG ", label))
    print("\nRESULT:", "ALL PASS" if allok else "FAILED")


if __name__ == "__main__":
    main()
