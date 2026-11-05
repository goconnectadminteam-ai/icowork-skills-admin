"""So từng dòng các bảng có cấu trúc trong hai PDF là hai kỳ của cùng một báo cáo (vd tuần 4 và tuần 5).

Làm bằng code vì model hay nhầm cột (lấy cột "tuần trước" làm kỳ trước) và tự trừ sai. Kết quả là danh sách thay đổi dạng
[mục, chỉ tiêu, kỳ trước, kỳ này] theo từng bảng; driver dựng thành các slide `bang`, model không phải chép lại.
Ba loại bảng: (1) bảng khoá-giá trị (STT | Nội dung | Kết quả), (2) bảng ma trận theo đơn vị (bỏ cột có chữ "trước"),
(3) dòng hệ thống có "(tiến độ tổng X%)" kèm danh sách giai đoạn và % từng giai đoạn.
"""
import re
from pathlib import Path

MAX_TABLE_ROWS = 14          # bảng dài hơn (phụ lục tiến độ, lịch) không so ở đây: ít đổi, nhiều dòng trùng ý
CELL = 160          # K7 bang: ô ≤ 160 (khớp quy-tac-mau.json); driver không cắt chữ dưới mức này
_PCT = re.compile(r'\d+(?:[.,]\d+)?\s*%')
_SO = re.compile(r'^\s*\d\.\s+((?:Sở|Ban|Trung tâm|Phòng|Công ty|UBND)[^\n]{3,60})$')


def _clean(cell):
    return re.sub(r'\s+', ' ', (cell or '').replace('\n', ' ')).strip()


def _cut(text, n=CELL):
    text = _clean(text)
    return text if len(text) <= n else text[:n - 1].rsplit(' ', 1)[0].rstrip(' ,;:/') + '…'


def _norm(text):
    return re.sub(r'\W+', '', _clean(text).lower())


def _heading(page, bbox):
    """Dòng chữ gần nhất ngay phía trên bảng (vd "2. Tiến độ tổng thể:") để đặt tên slide."""
    best = ''
    try:
        blocks = [b for b in page.get_text('blocks') if b[3] <= bbox[1] + 2 and b[6] == 0]
    except Exception:
        return best
    for b in sorted(blocks, key=lambda b: -b[3])[:4]:
        line = _clean(b[4]).strip(' :')
        if 4 <= len(line) <= 90 and re.search(r'[^\W\d_]{3}', line):
            return re.sub(r'^\s*(?:\d+\.|[IVX]+\.|[a-z]\))\s*', '', line)
    return best


def extract_tables(pdf):
    import fitz
    out, so = [], None
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            for line in page.get_text().splitlines():
                m = _SO.match(line)
                if m and i >= 3:
                    so = m.group(1).strip()
            try:
                found = page.find_tables().tables
            except Exception:
                continue
            for t in found:
                rows = [[_clean(c) for c in r] for r in t.extract()]
                out.append({'page': i, 'rows': rows, 'head': _heading(page, t.bbox), 'so': so})
    return _join_continued(out)


def _join_continued(tables):
    """Bảng Word ngắt sang trang sau thì phần sau không còn dòng tiêu đề: nối lại (và nối ô bị cắt dở của dòng cuối)."""
    out = []
    for t in tables:
        prev = out[-1] if out else None
        rows = t['rows']
        if prev and t['page'] == prev['page'] + 1 and rows and prev['rows'] and len(rows[0]) == len(prev['rows'][0]) and len(prev['rows'][0]) >= 3 \
                and not re.search(r'[^\W\d_]{3}', rows[0][0] or '') and not _is_header(rows[0]):
            first = rows[0]
            if not first[0] and any(first):          # dòng đầu là phần còn lại của ô dòng cuối trang trước
                last = prev['rows'][-1]
                for j, c in enumerate(first):
                    if c: last[j] = (last[j] + ' ' + c).strip()
                rows = rows[1:]
            prev['rows'] = prev['rows'] + rows
            continue
        out.append(t)
    return out


def _is_header(row):
    return sum(1 for c in row if re.search(r'[^\W\d_]{2}', c)) >= len(row) - 1 and not re.match(r'^\d+\.?$', row[0] or '')


def _name_col(rows):
    """Cột tên hàng: cột đầu (trong 3 cột đầu) mà đa số ô có chữ; cột kết quả dài không được chọn nhầm làm cột tên."""
    body = rows[1:]
    for j in range(min(3, len(rows[0]))):
        texty = sum(1 for r in body if j < len(r) and len(re.findall(r'[^\W\d_]', r[j])) >= 4)
        if body and texty * 10 >= len(body) * 7: return j
    return 0


def _simple(table):
    """Bảng khoá-giá trị hoặc ma trận: {khoá: {cột: giá trị}} và danh sách cột so sánh."""
    rows = [r for r in table['rows'] if any(r)]
    if not (2 <= len(rows) <= MAX_TABLE_ROWS) or len(rows[0]) < 2 or len(rows[0]) > 8:
        return None
    header = rows[0]
    if sum(1 for c in header if re.search(r'[^\W\d_]{2}', c)) < len(header) - 1: return None
    nc = _name_col(rows)
    cols = [j for j, h in enumerate(header) if j != nc and h and 'trước' not in h.lower() and not re.fullmatch(r'(stt|tt)', h.strip().lower())]
    if not cols: return None
    data = {}
    for r in rows[1:]:
        if nc >= len(r) or not _norm(r[nc]): continue
        data[_norm(r[nc])] = {'name': r[nc], 'cells': {j: (r[j] if j < len(r) else '') for j in cols}}
    return {'sig': _norm(' '.join(header)), 'header': header, 'nc': nc, 'cols': cols, 'data': data, 'page': table['page'], 'head': table['head']}


def _system_rows(table):
    """Dòng hệ thống: tên kèm "(tiến độ tổng X%)", ô danh sách giai đoạn "- a - b" và ô % tương ứng."""
    out = []
    for row in table['rows']:
        cells = [c for c in row if c]
        if len(cells) < 3 or not re.match(r'^\d+\.$', cells[0]): continue
        m = re.search(r'tiến độ\s*(?:tổng|TT)?\s*([\d.,]+)\s*%', ' '.join(cells[:3]), re.I)
        name = re.sub(r'\s*\(tiến độ[^)]*\)?', '', cells[1]).strip()
        items = [x.strip() for x in re.split(r'\s-\s|^-\s', cells[2]) if x.strip()]
        res = _PCT.findall(cells[3]) if len(cells) > 3 else []
        phases = [(i, r.replace(' ', '')) for i, r in zip(items, res)] if items and len(items) == len(res) else []
        out.append({'so': table.get('so'), 'name': name, 'total': (m.group(1).replace('.', ',') + '%') if m and ',' not in m.group(1) and '.' in m.group(1) else (m.group(1) + '%' if m else ''), 'phases': phases})
    return out


def _num(s):
    m = re.search(r'\d+(?:[.,]\d+)?', s or '')
    return float(m.group(0).replace(',', '.')) if m else None


def diff_simple(tabs_a, tabs_b):
    sa = [t for t in (_simple(x) for x in tabs_a) if t]; sb = [t for t in (_simple(x) for x in tabs_b) if t]
    used, out = set(), []
    for tb in sb:
        cand = [k for k, ta in enumerate(sa) if k not in used and ta['sig'] == tb['sig']]
        if not cand: continue
        k = min(cand, key=lambda k: abs(sa[k]['page'] - tb['page'])); used.add(k); ta = sa[k]
        rows = []
        for key, rb in tb['data'].items():
            ra = ta['data'].get(key)
            if not ra: continue
            for j in tb['cols']:
                x, y = _clean(ra['cells'].get(j, '')), _clean(rb['cells'].get(j, ''))
                if x != y and re.search(r'\d', x + y) and _cut(x) != _cut(y):
                    rows.append([_cut(rb['name']), _cut(tb['header'][j]), _cut(x or '—'), _cut(y or '—')])
        if rows: out.append({'title': tb['head'] or f'Thay đổi theo {tb["header"][tb["nc"]].lower() or "mục"}', 'page': tb['page'], 'rows': rows})
    return sorted(out, key=lambda t: t['page'])


_ABBR = [(r'nông nghiệp (?:và|&) môi trường', 'NN&MT'), (r'khoa học (?:và|&) công nghệ', 'KH&CN'), (r'văn hóa[,\s-]*thể thao[,\s-]*(?:và\s+)?du lịch', 'VHTT&DL'),
         (r'quản lý các khu công nghiệp', 'BQL KCN'), (r'tài nguyên (?:và|&) môi trường', 'TN&MT'), (r'thông tin (?:và|&) truyền thông', 'TT&TT'), (r'giao thông vận tải', 'GTVT')]


def _abbr(name):
    """Tên đơn vị gọn cho ô đầu bảng (≤14 ký tự): "Sở Nông nghiệp và Môi trường" → "NN&MT", không cắt cụt giữa chừng."""
    low = re.sub(r'\s+', ' ', name).strip().lower()
    for pat, ab in _ABBR:
        if re.search(pat, low): return ab
    short = re.sub(r'^(?:Sở|Ban Quản lý các|Ban)\s+', '', re.sub(r'\s+', ' ', name).strip())
    if len(short) <= 14: return short
    return ''.join(w[0].upper() for w in short.split() if w[0].isalpha() and w.lower() not in ('và', 'các', 'của'))


def diff_systems(tabs_a, tabs_b):
    def keyed(tabs):
        seen, out = {}, {}
        for t in tabs:
            if t['page'] > 20: continue
            for s in _system_rows(t):
                k = (s['so'], _norm(s['name'])); seen[k] = seen.get(k, 0) + 1
                out[k + (seen[k],)] = s
        return out
    sys_a = keyed(tabs_a)
    totals, phases = [], []
    for k, s in keyed(tabs_b).items():
        if True:
            a = sys_a.get(k)
            if not a: continue
            short = _abbr(s['so'] or '')
            label = _cut(s['name'])
            if s['total'] and a['total'] and s['total'] != a['total']:
                totals.append([short, label, a['total'], s['total']])
            pa = dict(a['phases'])
            for ph, v in s['phases']:
                if ph in pa and pa[ph] != v:
                    phases.append([label, _cut(ph), pa[ph], v])
    out = []
    if totals: out.append({'title': 'Hệ thống đổi tiến độ tổng', 'page': 3, 'rows': totals, 'cot': ['Đơn vị', 'Hệ thống', 'Kỳ trước', 'Kỳ này']})
    if phases: out.append({'title': 'Giai đoạn thay đổi theo hệ thống', 'page': 4, 'rows': phases})
    return out


_DONE = re.compile(r'hoàn thành|đã xử lý|tuân thủ|đã hoàn', re.I)


def _date(text):
    flat = re.sub(r'(?<=\d)\s+(?=\d)', '', re.sub(r'\s*/\s*', '/', text or ''))
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', flat)
    return (int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def overdue(tabs, report_date):
    """Dòng có hạn <= ngày báo cáo mà tình trạng chưa hoàn thành (vd chỉ đạo của Chủ đầu tư). Không phụ thuộc kỳ trước nên bắt được cả việc không đổi."""
    if not report_date: return []
    rows = []
    for t in tabs:
        if len(t['rows']) < 2 or len(t['rows'][0]) < 3 or not _is_header(t['rows'][0]): continue
        header = [h.lower() for h in t['rows'][0]]
        due = next((j for j, h in enumerate(header) if re.search(r'hạn|mốc', h)), None)
        stat = next((j for j, h in enumerate(header) if re.search(r'tiến độ|tình trạng|đánh giá', h) and j != due), None)
        if due is None or stat is None: continue
        nc = _name_col(t['rows'])
        for r in t['rows'][1:]:
            d = _date(r[due]) if due < len(r) else None
            st = r[stat] if stat < len(r) else ''
            if d and d <= report_date and st and not _DONE.search(re.sub(r'chưa\s+(?:được\s+)?hoàn thành', '', st, flags=re.I)):
                rows.append([_cut(r[nc]), f'{d[2]}/{d[1]}/{d[0]}', _cut(st)])
    return rows


def snapshot(tabs, max_tables=4, max_chars=4500):
    """Các bảng tổng hợp nhỏ của kỳ này (cả dòng không đổi) dạng văn bản, để model nêu được cả điều không đổi nhưng đáng chú ý (hạn, giải ngân...)."""
    out, size = [], 0
    for t in tabs:
        rows = [r for r in t['rows'] if any(r)]
        if t['page'] > 4 or not (2 <= len(rows) <= 14) or len(rows[0]) > 8 or not _is_header(rows[0]): continue
        lines = [f'### Bảng trang {t["page"]}' + (f': {t["head"]}' if t['head'] else ''), ' | '.join(_cut(c, 40) for c in rows[0])]
        lines += [' | '.join(_cut(c, 120) for c in r) for r in rows[1:]]
        text = '\n'.join(lines)
        if size + len(text) > max_chars: break
        out.append(text); size += len(text)
        if len(out) >= max_tables: break
    return '\n\n'.join(out)


def build(pdf_a, pdf_b, report_date=None):
    """Danh sách bảng thay đổi giữa hai kỳ (a = kỳ trước, b = kỳ này) và các dòng quá hạn của kỳ này; rỗng nếu không bóc được bảng nào."""
    ta, tb = extract_tables(pdf_a), extract_tables(pdf_b)
    out = diff_simple(ta, tb) + diff_systems(ta, tb)
    late = overdue(tb, report_date)
    if late: out.append({'title': 'Chỉ đạo đã đến hạn chưa xong', 'page': 99, 'rows': late, 'cot': ['Nội dung', 'Hạn', 'Tình trạng kỳ này']})
    return out
