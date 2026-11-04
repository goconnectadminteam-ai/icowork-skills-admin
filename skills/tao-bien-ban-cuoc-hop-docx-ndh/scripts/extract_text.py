#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_text.py — Lấy văn bản thuần, gọn từ file input (docx/doc/pdf/txt/md/html)
để agent context nhỏ đọc theo từng phần (chunk), không đọc nguyên file Word.

    python3 extract_text.py <input> [--size 10000]          # in thống kê (và toàn văn nếu chỉ 1 phần)
    python3 extract_text.py <input> --chunk 2 [--size 10000] # in phần thứ 2
    python3 extract_text.py <input> --tom-gon              # bản GỌN cho file lớn (nhiều phần): xem bên dưới

Làm sạch: bỏ mốc thời gian đứng riêng của transcript ([00:12], 00:12:30 đầu dòng), từ đệm lặp (alo, à, ừ…),
dòng trùng lặp, khoảng trắng thừa. GIỮ giờ nằm trong câu ("họp lúc 09:30", "trước 17:00") vì đó là thời hạn.
Bản làm sạch lưu ở thư mục tạm của hệ thống, không để file thừa trong thư mục làm việc.

--tom-gon (file lớn): mỗi mục/đoạn dài được cắt ngắn, nhưng câu có việc cần làm, người phụ trách, hạn, quyết định,
kết luận, rủi ro thì giữ gần nguyên văn. File "tóm tắt theo dòng thời gian" của GoMeet được gom mỗi mục một dòng
`[giờ bắt đầu] Tiêu đề: ý đầu; các ý có việc/người/hạn/quyết định/rủi ro`. Biên bản chỉ dài ≤ 700 từ nên không cần đọc hết văn bản gốc.
"""
import email
import hashlib
import html
import os
import re
import sys
import tempfile
import zipfile
from email import policy

import _boot

_boot.utf8_stdio()


def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", "\t", xml)
    xml = re.sub(r"</w:tc>", " | ", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def strip_html(h):
    h = re.sub(r"(?is)<(script|style|head|xml|title)\b.*?</\1>", "", h)   # head/xml: thuộc tính tài liệu Word (tác giả, ngày sửa, đếm chữ)
    h = re.sub(r"(?is)<!--.*?-->", "", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h\d)>", "\n", h)
    h = re.sub(r"(?i)</t[dh]>", " | ", h)
    return html.unescape(re.sub(r"<[^>]+>", "", h))


def decode_part(part):
    """Word lưu .doc dạng MHTML thường khai charset="unicode" (thực chất UTF-16 có BOM), thư viện email không biết tên này."""
    data = part.get_payload(decode=True) or b""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", "replace")
    charset = (part.get_content_charset() or "utf-8").lower()
    for cs in ("utf-16" if charset in ("unicode", "utf-16le", "utf-16") else charset, "utf-8"):
        try:
            return data.decode(cs, "replace")
        except LookupError:
            continue
    return data.decode("utf-8", "replace")


def read_any(path):
    ext = os.path.splitext(path)[1].lower()
    raw = open(path, "rb").read()
    if ext == ".docx" or raw[:2] == b"PK":
        return read_docx(path)
    if raw[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":  # .doc nhị phân kiểu cũ: không đọc được, đừng đưa rác cho model
        sys.exit("=== DỪNG: đây là file Word cũ (.doc nhị phân), chưa đọc được. Báo người dùng: lưu lại thành .docx "
                 "hoặc dán nội dung vào chat. KHÔNG bịa nội dung biên bản. ===")
    if ext == ".pdf":
        _boot.ensure(["pypdf", "PyPDF2", "fitz"], ["pypdf"])
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                import fitz
                with fitz.open(path) as doc:
                    return "\n".join(pg.get_text("text") for pg in doc)
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    text = raw.decode("utf-8", "ignore")
    if text.lstrip().startswith("MIME-Version"):  # .doc dạng MHTML (Word HTML)
        msg = email.message_from_bytes(raw, policy=policy.default)
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return strip_html(decode_part(part))
    if "<html" in text[:2000].lower():
        return strip_html(text)
    return text


RANGE = re.compile(r"^\s*(\d{1,2}):(\d{2}):\d{2}\s*[-–]\s*(\d{1,2}):(\d{2}):\d{2}\s*\|?\s*$")
CUE = re.compile(r"giao (?:việc|cho)|phụ trách|hạn|trước (?:ngày|\d)|deadline|thống nhất|quyết định|kết luận|chốt|"
                 r"chịu trách nhiệm|cam kết|rủi ro|vướng|khó khăn|cần (?:bổ sung|hoàn thiện|thực hiện)|sẽ ", re.I)


def _cut(s, n):
    if len(s) <= n:
        return s
    return s[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _points(body, first=70, full=200):
    """Tách các ý đánh số "1. … 2. …": giữ ý đầu (cắt ngắn, làm ngữ cảnh) và các ý có từ khoá việc/người/hạn/quyết định/rủi ro; bỏ ý còn lại."""
    pts = [re.sub(r"^\d{1,2}\.\s*", "", re.sub(r"\s+", " ", p)).strip()
           for p in re.split(r"(?:(?<=[.;])\s+|\n)(?=\d{1,2}\.\s)", body.strip()) if p.strip()]
    if not pts:
        return ""
    return "; ".join([_cut(pts[0], first)] + [_cut(x, full) for x in pts[1:] if CUE.search(x)])


def digest(raw):
    lines = raw.split("\n")
    marks = [i for i, ln in enumerate(lines) if RANGE.match(ln)]
    if len(marks) >= 3:                       # tóm tắt theo dòng thời gian: mỗi mục một dòng
        head = clean("\n".join(ln for ln in lines[:marks[0]] if "tổng hợp từ AI" not in ln))
        out = [" ".join(head.splitlines())]
        for a, b in zip(marks, marks[1:] + [len(lines)]):
            m = RANGE.match(lines[a])
            rest = [x.strip(" |") for x in lines[a + 1:b] if x.strip(" |")]
            if not rest:
                continue
            title, body = rest[0], "\n".join(rest[1:])
            out.append(f"[{int(m.group(1)):02d}:{m.group(2)}] {title}: {_points(body)}")
        return "\n".join(out)
    out = []                                  # văn bản khác: cắt các đoạn dài, giữ câu có từ khoá
    for ln in clean(raw).splitlines():
        if len(ln) <= 300:
            out.append(ln)
            continue
        sents = re.split(r"(?<=[.!?;])\s+", ln)
        kept = [s_ if CUE.search(s_) else _cut(s_, 90) for s_ in sents]
        out.append(_cut(" ".join(kept), 700))
    return "\n".join(out)


FILLER = r"\b(alo+|à+|ừ+|ờ+|ạ|ừm+|uhm+|ơ+|ấy|thì là|kiểu như)\b[,.]?\s*"


def clean(text):
    text = re.sub(r"[\[(]\s*\d{1,2}:\d{2}(:\d{2})?\s*[\])]", " ", text)           # mốc [00:12] / (00:12:30)
    if len(re.findall(r"(?m)^\s*\d{1,2}:\d{2}(:\d{2})?\b", text)) >= 8:               # transcript: mốc đứng đầu dòng lặp lại nhiều lần
        text = re.sub(r"(?m)^\s*\d{1,2}:\d{2}(:\d{2})?\b[ \t]*", "", text)           # (ít dòng thì là chương trình họp: giữ giờ)
    out, seen = [], set()
    for ln in text.splitlines():
        ln = re.sub(FILLER, "", ln, flags=re.I)
        ln = re.sub(r"\s+", " ", ln).strip(" |-")
        key = ln.lower()
        if len(ln) < 2 or key in seen:
            continue
        out.append(ln)
        seen.add(key)
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    size = int(args[args.index("--size") + 1]) if "--size" in args else 10000
    gon = "--tom-gon" in args
    chunk = int(args[args.index("--chunk") + 1]) if "--chunk" in args else 0
    cache = os.path.join(tempfile.gettempdir(), "tao-bien-ban-ndh")
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, hashlib.md5(os.path.abspath(src).encode("utf-8")).hexdigest()[:10] + ("_gon" if gon else "") + "_clean.txt")
    if chunk and os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
        text = open(out, encoding="utf-8").read()
    else:
        raw = read_any(src)
        text = digest(raw) if gon else clean(raw)
        open(out, "w", encoding="utf-8").write(text)
    parts = [text[i:i + size] for i in range(0, len(text), size)] or [""]
    if chunk:
        print(f"--- Phần {chunk}/{len(parts)} ---")
        print(parts[chunk - 1] if chunk <= len(parts) else "(hết)")
        return
    print(f"Đã trích: {len(text)} ký tự | {len(parts)} phần (mỗi phần {size} ký tự)")
    if len(parts) == 1:
        print("--- Toàn văn ---")
        print(text)
    else:
        print("Đọc lần lượt bằng cùng lệnh này, thêm --chunk 1 ... --chunk", len(parts))


if __name__ == "__main__":
    main()
