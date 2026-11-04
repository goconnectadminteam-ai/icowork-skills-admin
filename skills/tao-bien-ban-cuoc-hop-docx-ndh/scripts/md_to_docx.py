#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md_to_docx.py — Chuyển Markdown biên bản họp (khung trong SKILL.md) thành .docx
theo mẫu MeetingMinutes. Nhận 1 hoặc nhiều file .md (ghép theo thứ tự).

    python3 md_to_docx.py phan1.md [phan2.md ...] BienBanHop_xxx.docx [--xoa-nhap]

--xoa-nhap: tạo xong thì xoá các file .md đầu vào (để thư mục làm việc chỉ còn file kết quả).

- Thiếu/để trống mục "Danh sách công việc phân theo người phụ trách" -> tự sinh
  từ bảng "Danh sách hành động".
- Nội dung quá ngắn / chỉ là đường dẫn -> báo lỗi, không tạo file.

Cần python-docx: thiếu thì script tự cài vào môi trường riêng (xem _boot.py).
"""
import os
import re
import sys

import _boot

_boot.utf8_stdio()
_boot.ensure(["docx"], ["python-docx"])

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "Times New Roman"
BLACK, GREY = RGBColor(0, 0, 0), RGBColor(0x55, 0x55, 0x55)
WIDTHS = {3: [1.3, 4.2, 10.5], 4: [3.8, 4.6, 3.0, 4.6],
          7: [1.4, 3.6, 2.5, 2.3, 2.0, 2.0, 2.2]}


def font(run, size=12, bold=False, italic=False, color=BLACK):
    run.font.name = FONT
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), FONT)
    run.font.size, run.font.bold, run.font.italic = Pt(size), bold, italic
    run.font.color.rgb = color


def fmt(p, before=0, after=6, line=1.5, align=None, indent=None):
    f = p.paragraph_format
    f.space_before, f.space_after = Pt(before), Pt(after)
    f.line_spacing_rule, f.line_spacing = WD_LINE_SPACING.MULTIPLE, line
    if align is not None:
        p.alignment = align
    if indent is not None:
        f.left_indent = indent


def inline(p, text, size=12, bold=False):
    """Ghi text, hỗ trợ **đậm** và tô vàng [điền …]."""
    text = (text or "").strip() or "[điền …]"
    for tok in re.split(r"(\*\*[^*]+\*\*|\[điền[^\]]*\])", text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            font(p.add_run(tok[2:-2]), size, True)
        elif tok.startswith("[điền"):
            r = p.add_run(tok)
            font(r, size, bold)
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            font(p.add_run(tok), size, bold)


def heading(doc, text, size, center=False, before=14):
    p = doc.add_paragraph()
    fmt(p, before, 6, 1.15, WD_ALIGN_PARAGRAPH.CENTER if center else None)
    p.paragraph_format.keep_with_next = True
    font(p.add_run(text), size, True)


def xml(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def table_props(t, widths, borders=True, indent=None):
    pr = t._element.tblPr
    pr.append(xml("w:tblLayout", type="fixed"))
    old = pr.find(qn("w:tblW"))
    if old is not None:
        pr.remove(old)
    pr.append(xml("w:tblW", w=int(sum(w.twips for w in widths)), type="dxa"))
    if indent:
        pr.append(xml("w:tblInd", w=indent, type="dxa"))
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(xml(f"w:{edge}", val="single", sz=4, color="CBD5E1") if borders
                 else xml(f"w:{edge}", val="nil"))
    pr.append(b)
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", 80 if borders else 30), ("left", 140 if borders else 0),
                 ("bottom", 80 if borders else 30), ("right", 140)):
        mar.append(xml(f"w:{k}", w=v, type="dxa"))
    pr.append(mar)
    for i, gc in enumerate(t._element.tblGrid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(widths[i].twips)))
    for row in t.rows:
        for i, c in enumerate(row.cells):
            c.width = widths[i]


def add_table(doc, rows):
    n = len(rows[0])
    rows = [r + [""] * (n - len(r)) for r in rows]
    t = doc.add_table(rows=len(rows), cols=n)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for ri, r in enumerate(rows):
        for ci, v in enumerate(r[:n]):
            c = t.rows[ri].cells[ci]
            p = c.paragraphs[0]
            fmt(p, 0, 0, 1.15)
            inline(p, v, bold=(ri == 0))
            if ri == 0:
                tcPr = c._element.get_or_add_tcPr()
                tcPr.append(xml("w:shd", val="clear", color="auto", fill="F8FAFC"))
    for ri, row in enumerate(t.rows):  # không tách 1 dòng sang 2 trang
        trPr = row._tr.get_or_add_trPr()
        trPr.append(xml("w:cantSplit", val="true"))
        if ri == 0:
            trPr.append(xml("w:tblHeader", val="true"))
    widths = WIDTHS.get(n, [16.0 / n] * n)
    table_props(t, [Cm(w) for w in widths])
    fmt(doc.add_paragraph(), 0, 6, 1.0)


def add_info(doc, items):
    t = doc.add_table(rows=len(items), cols=2)
    t.autofit = False
    for i, (k, v) in enumerate(items):
        p1, p2 = t.rows[i].cells[0].paragraphs[0], t.rows[i].cells[1].paragraphs[0]
        fmt(p1, 0, 0, 1.25)
        fmt(p2, 0, 0, 1.25)
        font(p1.add_run(f"- {k}:"), 12, True)
        inline(p2, v)
    table_props(t, [Pt(120), Cm(11.5)], borders=False, indent=480)
    fmt(doc.add_paragraph(), 0, 6, 1.0)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


OWNER_H = "Danh sách công việc phân theo người phụ trách"


def _owner_lines(table_rows):
    hdr = [h.lower() for h in table_rows[0]]
    def col(name):
        return next((i for i, h in enumerate(hdr) if name in h), None)
    cv, pt, ut, th = col("công việc"), col("phụ trách"), col("ưu tiên"), col("thời hạn")
    groups = {}
    for r in table_rows[1:]:
        g = lambda i: (r[i].strip() if i is not None and i < len(r) else "") or "-"
        groups.setdefault(g(pt), []).append(
            f"- {g(cv)} (Ưu tiên: {g(ut)}, Thời hạn: {g(th)})")
    out = []
    for k, v in groups.items():
        out += [f"**{k}**"] + v + [""]
    return out


def ensure_owner_section(md):
    """Tự sinh mục phân theo người phụ trách nếu thiếu hoặc rỗng (theo từng khối)."""
    lines, out, last_act, has_owner = md.splitlines(), [], None, False
    def flush_missing():
        if last_act and not has_owner:
            out.extend(["", "### " + OWNER_H] + _owner_lines(last_act))
    i = 0
    while i < len(lines):
        ln = lines[i]
        t = ln.strip()
        if re.match(r"###\s+[A-Z]\.\s", t):  # bắt đầu khối A./B.
            flush_missing()
            last_act, has_owner = None, False
        if t.startswith("|"):
            blk = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                blk.append(lines[i]); i += 1
            out.extend(blk)
            rows = [cells(b) for b in blk if not re.fullmatch(r"[\s|:\-]+", b.strip())]
            if rows and any("phụ trách" in h.lower() for h in rows[0]) and \
               any("công việc" in h.lower() for h in rows[0]):
                last_act = rows
            continue
        if t.startswith("#") and OWNER_H.lower() in t.lower():
            has_owner = True
            out.append(ln)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if (j >= len(lines) or lines[j].strip().startswith("#")) and last_act:
                out.extend(_owner_lines(last_act))
            i += 1
            continue
        out.append(ln)
        i += 1
    flush_missing()
    return "\n".join(out)


def validate(md):
    t = md.strip()
    if len(t) < 300 or "## II" not in t or re.fullmatch(r"(file:/+)?[A-Za-z]:?[\\/].*", t.splitlines()[0]):
        sys.exit("LỖI: Nội dung Markdown không hợp lệ (quá ngắn, thiếu '## II. Nội dung' "
                 "hoặc chỉ là đường dẫn). Hãy ghi TOÀN VĂN biên bản vào file .md rồi chạy lại.")


def convert(md, out):
    validate(md)
    md = ensure_owner_section(md)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(2.5), Cm(2), Cm(2), Cm(2)
    doc.styles["Normal"].font.name = FONT
    doc.styles["Normal"].font.size = Pt(12)

    heading(doc, "BIÊN BẢN CUỘC HỌP", 16, center=True, before=0)
    fmt(doc.add_paragraph(), 0, 6, 1.0)

    lines = md.splitlines()
    i, section, info = 0, "", []
    while i < len(lines):
        raw = lines[i]
        ln = raw.strip()
        i += 1
        if info and not (section.startswith("I.") and ln.startswith(("-", "•"))):
            add_info(doc, info)
            info = []
        if not ln or ln.startswith("# ") or (ln.startswith("*") and "tổng hợp từ AI" in ln):
            continue
        if ln.startswith("## "):
            section = ln[3:].strip()
            heading(doc, section, 14, before=6 if section.startswith("I.") else 14)
            continue
        if ln.startswith("### "):
            h = ln[4:].strip()
            heading(doc, h, 16 if h.lower().startswith("tóm tắt") else 14)
            continue
        if ln.startswith("|"):
            block = [ln]
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [cells(b) for b in block if not re.fullmatch(r"[\s|:\-]+", b)]
            if rows:
                add_table(doc, rows)
            continue
        if ln.startswith(("- ", "• ", "* ")):
            body = ln[2:].strip()
            if section.startswith("I.") and ":" in body:
                k, v = body.split(":", 1)
                info.append((k.strip(), v.strip()))
                continue
            p = doc.add_paragraph()
            fmt(p, 0, 3, 1.5, indent=Cm(1.0))
            p.paragraph_format.first_line_indent = Cm(-0.5)
            font(p.add_run("•  "))
            inline(p, body)
            continue
        if re.fullmatch(r"\*\*[^*]+\*\*", ln):
            p = doc.add_paragraph()
            fmt(p, 4, 2, 1.5)
            p.paragraph_format.keep_with_next = True
            inline(p, ln)
            continue
        p = doc.add_paragraph()
        fmt(p, 0, 6, 1.5, WD_ALIGN_PARAGRAPH.JUSTIFY)
        inline(p, ln)
    if info:
        add_info(doc, info)
    doc.core_properties.title = "Biên bản cuộc họp"
    doc.save(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--xoa-nhap"]
    if len(args) < 2:
        sys.exit(__doc__)
    text = "\n\n".join(open(f, encoding="utf-8-sig").read() for f in args[:-1])
    convert(text, args[-1])
    from docx import Document as _D
    n = sum(len(p.text) for p in _D(args[-1]).paragraphs)
    if "--xoa-nhap" in sys.argv:
        for f in args[:-1]:
            os.remove(f)
    print(f"Đã tạo: {args[-1]} ({n} ký tự văn bản ngoài bảng)")
