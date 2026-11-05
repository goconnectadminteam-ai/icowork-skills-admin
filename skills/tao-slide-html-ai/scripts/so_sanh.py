"""So sánh hai kỳ của cùng một báo cáo (vd tuần 4 và tuần 5): chỉ giữ những chỗ khác nhau, để model đọc vài nghìn ký tự thay vì hàng trăm nghìn.

Đầu vào là content.md do extract.py tạo (mỗi nguồn một khối `# NGUỒN n:` gồm các `## Trang n`). Đầu ra là so-sanh.md.
Không bóc bảng: bảng Word xuất PDF bị gộp ô nên bóc sai; so theo dòng chữ đã chuẩn hoá thì chắc hơn.
"""
import difflib
import re
from pathlib import Path

MIN_SIMILARITY = 0.5      # hai nguồn giống nhau dưới mức này thì không phải hai kỳ của một báo cáo
MAX_CHARS = 36000         # so-sanh.md dài hơn thì ưu tiên chỗ có số liệu/ngày
_NUM = re.compile(r'\d[\d.,]*\s*%?')
_DATE = re.compile(r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})')


def _split_sources(text):
    parts = re.split(r'^# NGUỒN \d+:\s*', text, flags=re.M)[1:]
    out = []
    for part in parts:
        name, _, body = part.partition('\n')
        out.append((name.strip(), body))
    return out


def _lines(body):
    """[(trang, dòng đã chuẩn hoá)] bỏ phần đầu (metadata), dòng quá ngắn và số trang trơ trọi."""
    out, page = [], 0
    for raw in body.splitlines():
        m = re.match(r'## Trang (\d+)', raw)
        if m:
            page = int(m.group(1)); continue
        if not page:
            continue
        s = re.sub(r'\s+', ' ', raw).strip()
        if len(s) < 4 or re.fullmatch(r'\d{1,3}', s):
            continue
        out.append((page, s))
    return out


def _report_date(lines):
    for _, s in lines[:40]:
        m = _DATE.search(s)
        if m:
            d, mo, y = map(int, m.groups()); return (y, mo, d), f'{d:02d}/{mo:02d}/{y}'
    return None, ''


def _short(rows, limit=360, max_lines=8):
    text = ' / '.join(s for _, s in rows[:max_lines])
    if len(rows) > max_lines: text += f' / … (+{len(rows) - max_lines} dòng)'
    return text if len(text) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'


def _trend(old, new):
    if re.search(r'\d/\d|ngày|tháng', old + new): return ''   # dòng có ngày tháng: tăng/giảm vô nghĩa
    a, b = _NUM.findall(old), _NUM.findall(new)
    if a and len(a) == len(b) and a != b:
        def val(x):
            try: return float(x.replace('%', '').strip().replace('.', '').replace(',', '.')) if ',' in x or '.' not in x else float(x.replace('%', '').strip())
            except ValueError: return None
        marks = []
        for x, y in zip(a, b):
            vx, vy = val(x), val(y)
            if vx is not None and vy is not None and vx != vy: marks.append('▲ tăng' if vy > vx else '▼ giảm')
        if marks and len(set(marks)) == 1: return ' (' + marks[0] + ')'   # lẫn tăng và giảm trong cùng một khối thì bỏ, để model tự đọc
    return ''


def _key_numbers(text):
    """Số đáng đối chiếu của một chỗ thay đổi (bỏ ngày tháng): phần trăm và số từ 3 chữ số trở lên."""
    text = re.sub(r'\d{1,2}/\d{1,2}(?:/\d{2,4})?|\d{1,2}\s+tháng\s+\d{1,2}|năm\s+\d{4}', ' ', text)
    return sorted({n.strip() for n in _NUM.findall(text) if '%' in n or len(re.sub(r'\D', '', n)) >= 3})


def similar(work):
    """Độ giống (0..1) nếu content.md có đúng hai nguồn đủ dài, không thì None. Chỉ để nhắc model; KHÔNG quyết định có so sánh hay không (do người dùng nhờ)."""
    content = Path(work) / 'content.md'
    if not content.is_file(): return None
    sources = _split_sources(content.read_text(encoding='utf-8'))
    if len(sources) != 2: return None
    A, B = _lines(sources[0][1]), _lines(sources[1][1])
    if len(A) < 20 or len(B) < 20: return None
    return difflib.SequenceMatcher(None, [x[1] for x in A], [x[1] for x in B], autojunk=False).ratio()


def build(work):
    """Tạo work/so-sanh.md nếu content.md có đúng hai nguồn giống nhau. Trả về (Path, kỳ trước, kỳ này, số chỗ khác) hoặc None."""
    content = Path(work) / 'content.md'
    if not content.is_file(): return None
    sources = _split_sources(content.read_text(encoding='utf-8'))
    if len(sources) != 2: return None
    (name_a, body_a), (name_b, body_b) = sources
    A, B = _lines(body_a), _lines(body_b)
    if len(A) < 20 or len(B) < 20: return None
    da, label_a = _report_date(A); db, label_b = _report_date(B)
    if da and db and da > db:                      # đảo để A luôn là kỳ trước
        A, B, name_a, name_b, label_a, label_b = B, A, name_b, name_a, label_b, label_a
    sm = difflib.SequenceMatcher(None, [x[1] for x in A], [x[1] for x in B], autojunk=False)
    if sm.ratio() < MIN_SIMILARITY: return None
    blocks, meta = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': continue
        old, new = A[i1:i2], B[j1:j2]
        where = f'trang {old[0][0] if old else "-"} (kỳ trước) / trang {new[0][0] if new else "-"} (kỳ này)'
        if old and new:
            head = 'ĐỔI'; body = f'- Kỳ trước: {_short(old)}\n- Kỳ này: {_short(new)}' + (_trend(' '.join(s for _, s in old), ' '.join(s for _, s in new)) and '\n- Hướng:' + _trend(' '.join(s for _, s in old), ' '.join(s for _, s in new)))
        elif new:
            head = 'MỚI (chỉ có ở kỳ này)'; body = f'- Kỳ này: {_short(new)}'
        else:
            head = 'BỎ (chỉ có ở kỳ trước)'; body = f'- Kỳ trước: {_short(old)}'
        blocks.append((head, where, body))
        meta.append({'old': _short(old, 140, 3) if old else '', 'new': _short(new, 140, 3) if new else '', 'trang': new[0][0] if new else (old[0][0] if old else 0),
                     'nums': _key_numbers(' '.join(x for _, x in new))})
    out = [f'# So sánh hai kỳ (driver tạo tự động)', f'- Kỳ trước: {name_a}' + (f' · ngày báo cáo {label_a}' if label_a else ''),
           f'- Kỳ này: {name_b}' + (f' · ngày báo cáo {label_b}' if label_b else ''),
           f'- {len(blocks)} chỗ khác nhau (phần còn lại của hai báo cáo GIỐNG nhau, không cần đọc). Độ giống: {sm.ratio():.0%}.',
           '- Chỉ dùng chữ/số trong tệp này làm căn cứ; số "kỳ trước" và "kỳ này" đều có trong content.md.', '']
    size, kept = sum(len(x) for x in out), []
    ranked = sorted(range(len(blocks)), key=lambda k: (0 if re.search(r'\d', blocks[k][2]) else 1, k))
    for k in ranked:
        cost = sum(len(x) for x in blocks[k]) + 12
        if size + cost > MAX_CHARS: continue
        kept.append(k); size += cost
    for n, k in enumerate(sorted(kept), 1):
        head, where, body = blocks[k]
        out += [f'## {n}. {head} — {where}', body, '']
    if len(kept) < len(blocks): out.append(f'(đã bỏ {len(blocks) - len(kept)} chỗ ít số liệu để tệp gọn; cần thì đọc content.md theo trang)')
    path = Path(work) / 'so-sanh.md'; path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    import json
    (Path(work) / 'so-sanh.json').write_text(json.dumps({'order': [name_a, name_b], 'labels': [label_a, label_b], 'blocks': [dict(m, id=k + 1) for k, m in enumerate(meta)]}, ensure_ascii=False), encoding='utf-8')
    return path, label_a or name_a, label_b or name_b, len(blocks)
