# -*- coding: utf-8 -*-
"""GM script markdown -> PDF converter using fpdf2 — styled edition"""

import re
import os
from fpdf import FPDF
from fpdf.enums import WrapMode

INPUT_MD = r"D:\個人研究その2\murder_mystery\dist\GM専用\01_GM進行台本.md"
OUTPUT_PDF = r"D:\個人研究その2\murder_mystery\dist\GM専用\01_GM進行台本.pdf"

# --- Fonts ---
YU_GOTH_B  = r"C:/Windows/Fonts/YuGothB.ttc"   # headers (gothic bold)
YU_MIN     = r"C:/Windows/Fonts/yumin.ttf"      # body regular
YU_MIN_B   = r"C:/Windows/Fonts/yumindb.ttf"   # body bold (demibold)
FALLBACK   = r"C:/Windows/Fonts/meiryo.ttc"
FALLBACK_B = r"C:/Windows/Fonts/meiryob.ttc"

# --- Color palette ---
C_BG          = (250, 247, 240)   # page background (warm cream)
C_TEXT        = (35, 35, 35)      # body text (near-black)
C_INDIGO      = (35, 45, 80)      # H2 band / H3 text / table header
C_INDIGO_LT   = (60, 70, 100)    # H4 text
C_BQ_BG       = (240, 235, 225)  # blockquote background
C_BQ_BORDER   = (140, 100, 60)   # blockquote left border (warm brown)
C_BQ_TEXT     = (50, 40, 30)     # blockquote text
C_TBL_HDR_FG  = (255, 255, 255)  # table header text
C_TBL_ROW0    = (250, 247, 240)  # table even row
C_TBL_ROW1    = (240, 237, 230)  # table odd row
C_TBL_BORDER  = (180, 175, 165)  # table border
C_CODE_BG     = (45, 45, 55)     # code block background
C_CODE_TEXT   = (220, 215, 200)  # code block text
C_FOOTER      = (140, 135, 125)  # footer text
C_HR          = (180, 160, 130)  # horizontal rule (warm brown)


class GmPdf(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=20, top=15, right=20)
        self.set_auto_page_break(auto=True, margin=15)
        self._setup_fonts()
        self._is_title_page = True

    def _setup_fonts(self):
        # Yu Gothic Bold for headers — .ttc needs font_index kwarg
        try:
            self.add_font("YuGoth", style="",  fname=YU_GOTH_B)
            self.add_font("YuGoth", style="B", fname=YU_GOTH_B)
            self._header_font = "YuGoth"
        except Exception:
            self.add_font("Fallback", style="",  fname=FALLBACK)
            self.add_font("Fallback", style="B", fname=FALLBACK_B)
            self._header_font = "Fallback"

        # Yu Mincho for body
        try:
            self.add_font("YuMin", style="",  fname=YU_MIN)
            self.add_font("YuMin", style="B", fname=YU_MIN_B)
            self._body_font = "YuMin"
        except Exception:
            if self._header_font != "Fallback":
                self.add_font("Fallback", style="",  fname=FALLBACK)
                self.add_font("Fallback", style="B", fname=FALLBACK_B)
            self._body_font = "Fallback"

    def header(self):
        # Draw warm cream background on every page
        self.set_fill_color(*C_BG)
        self.set_draw_color(*C_BG)
        self.rect(0, 0, self.w, self.h, style="F")
        self.set_draw_color(0, 0, 0)

    def footer(self):
        if self._is_title_page:
            return
        self.set_y(-12)
        self.set_font(self._body_font, size=8)
        self.set_text_color(*C_FOOTER)
        label = f"『覗きの代』GM進行台本    {self.page_no()}"
        self.cell(0, 5, label, align="C")
        self.set_text_color(*C_TEXT)


def effective_width(pdf: FPDF) -> float:
    return pdf.w - pdf.l_margin - pdf.r_margin


# ---------- Render functions ----------

def render_h1(pdf: GmPdf, text: str):
    pdf.set_font(pdf._header_font, style="B", size=22)
    pdf.set_text_color(*C_INDIGO)
    pdf.ln(8)
    pdf.multi_cell(0, 12, text, align="C", wrapmode=WrapMode.CHAR)
    pdf.ln(4)
    # decorative line under title
    x1, x2 = pdf.l_margin + 20, pdf.w - pdf.r_margin - 20
    y = pdf.get_y()
    pdf.set_draw_color(*C_HR)
    pdf.set_line_width(0.8)
    pdf.line(x1, y, x2, y)
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    pdf.ln(6)


def render_h2(pdf: GmPdf, text: str):
    pdf.add_page()
    pdf._is_title_page = False
    pdf.start_section(text, level=0)

    pdf.ln(2)
    # Full-width dark indigo band
    band_h = 11
    y = pdf.get_y()
    pdf.set_fill_color(*C_INDIGO)
    pdf.set_draw_color(*C_INDIGO)
    pdf.rect(pdf.l_margin, y, effective_width(pdf), band_h, style="F")

    # White text inside band
    pdf.set_font(pdf._header_font, style="B", size=13)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(pdf.l_margin + 3, y + 1.5)
    pdf.multi_cell(effective_width(pdf) - 6, band_h - 3, text,
                   align="L", wrapmode=WrapMode.CHAR)
    pdf.set_y(y + band_h + 3)
    pdf.set_text_color(*C_TEXT)
    pdf.set_draw_color(0, 0, 0)


def render_h3(pdf: GmPdf, text: str):
    pdf.ln(4)
    pdf.start_section(text, level=1)

    # Left border bar
    h3_h = 8
    y = pdf.get_y()
    pdf.set_fill_color(*C_INDIGO)
    pdf.set_draw_color(*C_INDIGO)
    pdf.rect(pdf.l_margin, y, 3, h3_h, style="F")

    pdf.set_font(pdf._header_font, style="B", size=11)
    pdf.set_text_color(*C_INDIGO)
    pdf.set_xy(pdf.l_margin + 5, y + 0.5)
    pdf.multi_cell(effective_width(pdf) - 5, h3_h - 1, text,
                   align="L", wrapmode=WrapMode.CHAR)
    pdf.set_y(max(pdf.get_y(), y + h3_h))
    pdf.ln(1)
    pdf.set_text_color(*C_TEXT)
    pdf.set_draw_color(0, 0, 0)


def render_h4(pdf: GmPdf, text: str):
    pdf.ln(2)
    pdf.set_font(pdf._header_font, style="B", size=10)
    pdf.set_text_color(*C_INDIGO_LT)
    pdf.multi_cell(0, 7, text, align="L", wrapmode=WrapMode.CHAR)
    pdf.ln(1)
    pdf.set_text_color(*C_TEXT)


def render_hr(pdf: GmPdf):
    pdf.ln(2)
    x1 = pdf.l_margin
    x2 = pdf.w - pdf.r_margin
    y = pdf.get_y()
    pdf.set_draw_color(*C_HR)
    pdf.set_line_width(0.4)
    pdf.line(x1, y, x2, y)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.ln(3)


def render_paragraph(pdf: GmPdf, text: str):
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_font(pdf._body_font, size=9.5)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(0, 5.5, text, align="L", markdown=True, wrapmode=WrapMode.CHAR)
    pdf.ln(2)


def render_blockquote(pdf: GmPdf, lines: list):
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    text = "\n".join(lines)
    line_h = 5.5

    indent = 8
    bq_x = 20 + indent       # 28mm
    border_x = bq_x - 5      # left border position
    bq_width = effective_width(pdf) - indent

    # Estimate height
    char_per_line = max(1, int(bq_width / 2.5))
    est_lines = sum(max(1, len(ln) // char_per_line + 1) for ln in lines)
    est_h = est_lines * line_h + 6

    y0 = pdf.get_y()

    # Draw background
    pdf.set_fill_color(*C_BQ_BG)
    pdf.set_draw_color(*C_BQ_BG)
    pad = 3
    pdf.rect(bq_x - pad, y0, bq_width + pad * 2, est_h, style="F")
    pdf.set_draw_color(0, 0, 0)

    # Render text
    try:
        pdf.set_left_margin(bq_x)
        pdf.set_y(y0 + 2)
        pdf.set_x(bq_x)
        pdf.set_font(pdf._body_font, size=9.5)
        pdf.set_text_color(*C_BQ_TEXT)
        pdf.multi_cell(bq_width, line_h, text, align="L",
                       markdown=True, wrapmode=WrapMode.CHAR)
        y1 = pdf.get_y() + 2
    finally:
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

    # Left border
    pdf.set_draw_color(*C_BQ_BORDER)
    pdf.set_line_width(3)
    pdf.line(border_x, y0, border_x, max(y1, y0 + est_h))
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_text_color(*C_TEXT)
    pdf.ln(3)


def render_list_item(pdf: GmPdf, text: str, ordered: bool, index: int):
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_font(pdf._body_font, size=9.5)
    pdf.set_text_color(*C_TEXT)
    indent = 8
    bullet_w = 8

    y_save = pdf.get_y()

    if ordered:
        bullet = f"{index}."
    else:
        if text.startswith("[ ] "):
            bullet = "□"
            text = text[4:]
        elif text.startswith("[x] ") or text.startswith("[X] "):
            bullet = "■"
            text = text[4:]
        else:
            bullet = "・"

    content_x = 20 + indent + bullet_w
    content_w = effective_width(pdf) - indent - bullet_w

    pdf.set_x(20 + indent)
    pdf.set_font(pdf._body_font, size=9.5)
    pdf.cell(bullet_w, 5.5, bullet)
    pdf.set_xy(content_x, y_save)

    try:
        pdf.set_left_margin(content_x)
        pdf.multi_cell(content_w, 5.5, text, align="L",
                       markdown=True, wrapmode=WrapMode.CHAR)
    finally:
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)


def render_code_block(pdf: GmPdf, lines: list):
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    text = "\n".join(lines)
    line_h = 5.0

    code_x = 22
    code_w = effective_width(pdf) - 4

    # Estimate height
    est_lines = max(len(lines), 1)
    est_h = est_lines * line_h + 6

    y0 = pdf.get_y()
    pdf.set_fill_color(*C_CODE_BG)
    pdf.set_draw_color(*C_CODE_BG)
    pdf.rect(code_x - 2, y0, code_w + 4, est_h, style="F")
    pdf.set_draw_color(0, 0, 0)

    try:
        pdf.set_left_margin(code_x)
        pdf.set_x(code_x)
        pdf.set_y(y0 + 2)
        pdf.set_font(pdf._body_font, size=8.5)
        pdf.set_text_color(*C_CODE_TEXT)
        pdf.multi_cell(code_w, line_h, text, align="L", wrapmode=WrapMode.CHAR)
    finally:
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

    pdf.set_text_color(*C_TEXT)
    pdf.ln(3)


def parse_table(lines: list):
    rows = []
    for line in lines:
        line = line.strip().strip("|")
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return [], []
    headers = rows[0]
    data_rows = rows[2:]
    return headers, data_rows


def render_table(pdf: GmPdf, lines: list):
    headers, data_rows = parse_table(lines)
    if not headers:
        return

    n_cols = len(headers)
    total_w = effective_width(pdf)
    col_w = total_w / n_cols
    row_h = 7

    pdf.set_font(pdf._header_font, style="B", size=9)
    pdf.set_fill_color(*C_INDIGO)
    pdf.set_text_color(*C_TBL_HDR_FG)
    pdf.set_draw_color(*C_TBL_BORDER)
    pdf.set_line_width(0.3)

    for header in headers:
        pdf.cell(col_w, row_h, header, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font(pdf._body_font, size=9)
    pdf.set_text_color(*C_TEXT)

    for i, row in enumerate(data_rows):
        while len(row) < n_cols:
            row.append("")
        row = row[:n_cols]

        approx_chars = max(1, int(col_w / 2.8))
        max_lines = max(max(1, len(c) // approx_chars + 1) for c in row)
        h = row_h * max_lines

        fill_color = C_TBL_ROW1 if (i % 2 == 1) else C_TBL_ROW0
        pdf.set_fill_color(*fill_color)

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        for j, cell in enumerate(row):
            pdf.set_xy(x_start + j * col_w, y_start)
            cell_clean = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
            pdf.multi_cell(col_w, row_h, cell_clean, border=1, fill=True,
                           align="L", wrapmode=WrapMode.CHAR)

        pdf.set_xy(x_start, y_start + h)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.ln(3)


# ---------- TOC renderer ----------

def render_toc(pdf: GmPdf, outline):
    """Render Table of Contents — called by fpdf2 after all pages are laid out."""
    pdf.set_font(pdf._header_font, style="B", size=14)
    pdf.set_text_color(*C_INDIGO)
    pdf.ln(6)
    pdf.cell(0, 10, "目  次", align="C")
    pdf.ln(12)

    for section in outline:
        if section.level == 0:
            # H2 entries
            pdf.set_font(pdf._header_font, style="B", size=10)
            pdf.set_text_color(*C_TEXT)
            title = section.name
            page_str = str(section.page_number)
            max_title_w = effective_width(pdf) - 15
            # Dot leaders
            title_w = pdf.get_string_width(title)
            dots_w = max_title_w - title_w
            dots = ""
            dot_unit = pdf.get_string_width(" .")
            if dot_unit > 0:
                n = max(0, int(dots_w / dot_unit))
                dots = " ." * n
            pdf.cell(max_title_w, 7, title + dots, align="L")
            pdf.set_font(pdf._body_font, size=10)
            pdf.cell(15, 7, page_str, align="R")
            pdf.ln()
        elif section.level == 1:
            # H3 entries (indented, smaller)
            pdf.set_font(pdf._body_font, size=9)
            pdf.set_text_color(*C_INDIGO_LT)
            title = "    " + section.name
            page_str = str(section.page_number)
            max_title_w = effective_width(pdf) - 15
            title_w = pdf.get_string_width(title)
            dots_w = max_title_w - title_w
            dot_unit = pdf.get_string_width(" .")
            dots = ""
            if dot_unit > 0:
                n = max(0, int(dots_w / dot_unit))
                dots = " ." * n
            pdf.cell(max_title_w, 6, title + dots, align="L")
            pdf.set_font(pdf._body_font, size=9)
            pdf.cell(15, 6, page_str, align="R")
            pdf.ln()

    pdf.set_text_color(*C_TEXT)


# ---------- Block-level state machine ----------

class BlockType:
    NONE = "none"
    PARAGRAPH = "paragraph"
    BLOCKQUOTE = "blockquote"
    CODE = "code"
    TABLE = "table"
    LIST = "list"


def flush_block(pdf: GmPdf, btype: str, buf: list, list_state: dict):
    if not buf and btype == BlockType.NONE:
        return
    if btype == BlockType.BLOCKQUOTE:
        render_blockquote(pdf, buf)
    elif btype == BlockType.CODE:
        render_code_block(pdf, buf)
    elif btype == BlockType.TABLE:
        render_table(pdf, buf)
    elif btype == BlockType.PARAGRAPH:
        text = " ".join(buf).strip()
        if text:
            render_paragraph(pdf, text)
    elif btype == BlockType.LIST:
        for item in buf:
            render_list_item(pdf, item["text"], item.get("ordered", False), item.get("index", 1))
        pdf.ln(1)


def process_markdown(pdf: GmPdf, md_text: str, with_toc: bool = False):
    """Parse markdown and render to pdf. with_toc=True inserts TOC after H1."""
    lines = md_text.splitlines()

    btype = BlockType.NONE
    buf = []
    in_code = False
    list_ordered_counter = 0
    toc_inserted = False
    h1_rendered = False

    def flush():
        nonlocal btype, buf, list_ordered_counter
        flush_block(pdf, btype, buf, {})
        buf = []
        btype = BlockType.NONE
        list_ordered_counter = 0

    for raw_line in lines:
        line = raw_line.rstrip()

        # Code block toggle
        if line.startswith("```"):
            if in_code:
                flush_block(pdf, BlockType.CODE, buf, {})
                buf = []
                btype = BlockType.NONE
                in_code = False
            else:
                flush()
                in_code = True
                btype = BlockType.CODE
            continue

        if in_code:
            buf.append(line)
            continue

        # Headers (match longest prefix first)
        h4 = re.match(r"^#{4}\s+(.*)", line)
        h3 = re.match(r"^#{3}\s+(.*)", line)
        h2 = re.match(r"^#{2}\s+(.*)", line)
        h1 = re.match(r"^#{1}\s+(.*)", line)

        if h4 and not h3:
            flush()
            render_h4(pdf, h4.group(1))
            continue
        if h3 and not h2:
            flush()
            render_h3(pdf, h3.group(1))
            continue
        if h2 and not h1:
            flush()
            render_h2(pdf, h2.group(1))
            continue
        if h1:
            flush()
            render_h1(pdf, h1.group(1))
            h1_rendered = True
            # Insert TOC placeholder after H1 (only once, for main document)
            if with_toc and not toc_inserted:
                pdf.insert_toc_placeholder(render_toc, pages=2)
                toc_inserted = True
                pdf._is_title_page = False
            continue

        # Horizontal rule
        if re.match(r"^---+\s*$", line):
            flush()
            render_hr(pdf)
            continue

        # Table row
        if line.startswith("|"):
            if btype != BlockType.TABLE:
                flush()
                btype = BlockType.TABLE
            buf.append(line)
            continue
        else:
            if btype == BlockType.TABLE:
                flush()

        # Blockquote
        bq_match = re.match(r"^>\s?(.*)", line)
        if bq_match:
            if btype != BlockType.BLOCKQUOTE:
                flush()
                btype = BlockType.BLOCKQUOTE
            buf.append(bq_match.group(1))
            continue
        else:
            if btype == BlockType.BLOCKQUOTE:
                flush()

        # Ordered list
        ol_match = re.match(r"^(\d+)\.\s+(.*)", line)
        if ol_match:
            if btype != BlockType.LIST:
                flush()
                btype = BlockType.LIST
                list_ordered_counter = 0
            list_ordered_counter += 1
            buf.append({"text": ol_match.group(2), "ordered": True, "index": list_ordered_counter})
            continue

        # Unordered list
        ul_match = re.match(r"^[-*]\s+(.*)", line)
        if ul_match:
            if btype != BlockType.LIST:
                flush()
                btype = BlockType.LIST
            buf.append({"text": ul_match.group(1), "ordered": False, "index": 0})
            continue
        else:
            if btype == BlockType.LIST:
                flush()

        # Blank line
        if not line.strip():
            if btype in (BlockType.PARAGRAPH, BlockType.LIST):
                flush()
            continue

        # Regular paragraph text
        if btype != BlockType.PARAGRAPH:
            flush()
            btype = BlockType.PARAGRAPH
        buf.append(line)

    flush()


def main():
    # --- Main GM document (with TOC) ---
    with open(INPUT_MD, encoding="utf-8") as f:
        md_text = f.read()

    pdf = GmPdf()
    pdf.add_page()
    pdf._is_title_page = True

    process_markdown(pdf, md_text, with_toc=True)
    pdf.output(OUTPUT_PDF)

    size = os.path.getsize(OUTPUT_PDF)
    print(f"[01] PDF written: {OUTPUT_PDF}")
    print(f"     File size  : {size:,} bytes ({size / 1024:.1f} KB)")
    print(f"     Page count : {pdf.page}")

    # --- Truth document (no TOC) ---
    truth_md  = r"D:\個人研究その2\murder_mystery\dist\GM専用\02_真相編.md"
    truth_pdf = r"D:\個人研究その2\murder_mystery\dist\GM専用\02_真相編.pdf"

    if os.path.exists(truth_md):
        with open(truth_md, encoding="utf-8") as f:
            md2 = f.read()
        pdf2 = GmPdf()
        pdf2.add_page()
        pdf2._is_title_page = True
        process_markdown(pdf2, md2, with_toc=False)
        pdf2.output(truth_pdf)
        size2 = os.path.getsize(truth_pdf)
        print(f"[02] PDF written: {truth_pdf}")
        print(f"     File size  : {size2:,} bytes ({size2 / 1024:.1f} KB)")
        print(f"     Page count : {pdf2.page}")
    else:
        print(f"[02] Skipped (not found): {truth_md}")


if __name__ == "__main__":
    main()
