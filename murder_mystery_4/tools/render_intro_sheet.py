# -*- coding: utf-8 -*-
"""導入シート PNG 生成

成果物: dist/配布物/共通/導入シート.png（1成果物=1スクリプト原則）
本文の正: data/配布物/共通/intro_sheet.md  ← 文章の修正はここだけ編集する
見た目の正: tools/templates/intro_sheet.html（デザイン仕様: scenario/07_visual_design.md）
方式: MDをパース → テンプレートに流し込み → tools/mockups/intro_sheet.html を生成
      → Playwright(システムEdge/Chrome)で撮影
"""
import html
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "配布物" / "共通" / "intro_sheet.md"
TEMPLATE = ROOT / "tools" / "templates" / "intro_sheet.html"
GENERATED = ROOT / "tools" / "mockups" / "intro_sheet.html"  # Artifactプレビュー共用（編集禁止）
OUT = ROOT / "dist" / "配布物" / "共通" / "導入シート.png"

WIDTH, HEIGHT = 1600, 1000
SCALE = 2  # 出力 3200x2000

GEN_BANNER = (
    "<!-- 自動生成ファイル（編集禁止）: 文章は data/配布物/共通/intro_sheet.md、"
    "見た目は tools/templates/intro_sheet.html を編集して "
    "python tools/render_intro_sheet.py で再生成 -->\n"
)


# ---------- data/intro_sheet.md のパース ----------

def parse_sections(text: str) -> dict:
    """`## 見出し` 単位でセクション本文（行リスト）に分割する"""
    sections, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def kv(lines: list) -> dict:
    """`キー: 値` 行を辞書に（値側のコロンは保持）"""
    out = {}
    for line in lines:
        m = re.match(r"^(\S+?)[:：]\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def em(s: str) -> str:
    """**強調** → em（白太字）、*用語* → term（淡シアン・固有用語の弱強調）"""
    s = re.sub(r"\*\*(.+?)\*\*", r'<span class="em">\1</span>', s)
    return re.sub(r"\*(.+?)\*", r'<span class="term">\1</span>', s)


def paragraphs(lines: list) -> list:
    """空行区切りの段落リスト（キー行・空行を除いた本文ブロック）"""
    blocks, buf = [], []
    for line in lines:
        if line.strip():
            buf.append(line.strip())
        elif buf:
            blocks.append("".join(buf))
            buf = []
    if buf:
        blocks.append("".join(buf))
    return blocks


def build_tokens(md: str) -> dict:
    sec = parse_sections(md)
    t = {}

    head = kv(sec["ヘッダ"])
    t["EYEBROW"] = esc(head["眉"])
    t["STAMP"] = esc(head["スタンプ"])

    title = kv(sec["タイトル"])
    plain = title["題字"]
    t["TITLE_PLAIN"] = esc(plain)
    title_html = esc(plain)
    if "ルビ" in title and "=" in title["ルビ"]:
        target, reading = title["ルビ"].split("=", 1)
        title_html = title_html.replace(
            esc(target), f"<ruby>{esc(target)}<rt>{esc(reading)}</rt></ruby>", 1
        )
    t["TITLE_HTML"] = title_html
    t["EN_TITLE"] = esc(title["英字"])

    t["LEAD_HTML"] = "\n".join(
        f"            <p>{em(esc(p))}</p>" for p in paragraphs(sec["導入文"])
    )
    t["NOTE_HTML"] = "<br>".join(
        em(esc(p)) for p in paragraphs(sec.get("注記", []))
    )
    t["CLOSING_HTML"] = "<br>".join(
        esc(l.strip()) for l in sec["締め"] if l.strip()
    )

    # 勢力: 見出し行 + `### 対句 | 名前 | 英字` + 説明文
    label = kv(sec["勢力"]).get("見出し", "")
    en_part, _, jp_part = label.partition("—")
    t["PANEL_LABEL_HTML"] = f"{esc(en_part.strip())} <span>— {esc(jp_part.strip())}</span>"
    facs, cur = [], None
    for line in sec["勢力"]:
        m = re.match(r"^### (.+)$", line)
        if m:
            tag, name, en_name = [x.strip() for x in m.group(1).split("|")]
            cur = {"tag": tag, "name": name, "en": en_name, "desc": []}
            facs.append(cur)
        elif cur is not None and line.strip():
            cur["desc"].append(line.strip())
    t["FACS_HTML"] = "\n".join(
        '            <div class="fac">\n'
        f'              <div class="fac-tag">{esc(f["tag"])}</div>\n'
        f'              <div class="fac-name">{esc(f["name"])}<span class="en">{esc(f["en"])}</span></div>\n'
        f"              <div class=\"fac-desc\">{em(esc(''.join(f['desc'])))}</div>\n"
        "            </div>"
        for f in facs
    )

    t["CHIPS_HTML"] = "\n".join(
        f'            <div class="chip">{esc(l.strip())}</div>'
        for l in sec["チップ"] if l.strip()
    )

    band = kv(sec["帯"])
    t["HAZARD_TEXT"] = esc(band["宣言"])
    t["HAZARD_EN"] = esc(band["英字"])

    t["READOUT_HTML"] = "<br>\n".join(
        esc(l.strip()) for l in sec["読み出し"] if l.strip()
    )
    return t


# ---------- 生成と撮影 ----------

def main() -> int:
    for p in (DATA, TEMPLATE):
        if not p.exists():
            print(f"ERROR: not found: {p}")
            return 1

    tokens = build_tokens(DATA.read_text(encoding="utf-8"))
    page_html = TEMPLATE.read_text(encoding="utf-8")
    for key, value in tokens.items():
        page_html = page_html.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", page_html)
    if leftover:
        print(f"ERROR: unfilled tokens: {leftover}")
        return 1

    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.write_text(GEN_BANNER + page_html, encoding="utf-8")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    full_doc = (
        '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        "<style>body{margin:0;background:#0A0E1A}</style></head><body>"
        + page_html + "</body></html>"
    )
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        page_path = Path(td) / "sheet.html"
        page_path.write_text(full_doc, encoding="utf-8")
        with sync_playwright() as pw:
            browser = None
            for channel in ("msedge", "chrome", None):
                try:
                    browser = pw.chromium.launch(channel=channel, headless=True)
                    break
                except Exception:
                    continue
            if browser is None:
                print("ERROR: no Chromium-based browser available")
                return 1
            page = browser.new_page(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=SCALE,
            )
            page.goto(page_path.as_uri())
            page.evaluate("document.fonts.ready")
            page.locator(".sheet").screenshot(path=str(OUT))
            browser.close()

    print(f"OK: {OUT} ({WIDTH * SCALE}x{HEIGHT * SCALE})")
    print(f"OK: {GENERATED} (プレビュー用HTML)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
