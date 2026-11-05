"""Soát số liệu đáng ngờ khi so hai kỳ của cùng một báo cáo (vd tuần 4 và tuần 5), bằng code chứ không giao model.

Bốn loại, đều chỉ dựa trên chữ và bảng có trong hai nguồn (không suy đoán):
1. Cột "tuần trước" của kỳ này khác cột "tuần này" của kỳ trước (báo cáo kỳ này tự ghi sai kỳ trước).
2. Tỷ lệ vượt 100%: "100/75 ảnh", "59.045/45.941 trường", "đạt 133,3%" (không tính câu "vượt X% so với kế hoạch").
3. Số kỳ trước còn sót trong kỳ này: một chỉ tiêu đã đổi giá trị (cùng nhãn, cùng đơn vị) nhưng chỗ khác của kỳ này vẫn ghi số cũ.
4. Mới hoặc hết: dòng chữ chỉ có ở một kỳ (vd rủi ro mới bổ sung).
Ngoài ra `tang_manh` xếp các dòng tăng từ bảng thay đổi để model viết mục "Điểm tiến bộ" (chỉ để sắp xếp, không in số tự tính).
"""
import re

CELL = 80
_UNIT = r'(ảnh|trường|bản ghi|dự án|KCN|xã|phường|km|ha|trang|bộ|hồ sơ|đối tượng|hạng mục|thông tin|tài liệu|lớp|điểm)'
_RATIO = re.compile(r'(?<![\d/.,])(\d{1,3}(?:\.\d{3})*|\d+)(?:,\d+)?\s*/\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,\d+)?\s*' + _UNIT + r'\b', re.I)
_PCT_OVER = re.compile(r'(đạt|hoàn thành|tỷ lệ[^:\n]{0,30}:)\s*(?:gần\s+)?(\d{3}(?:,\d+)?)\s*%', re.I)
_VAL = re.compile(r'(?<![\d/.,])(\d[\d.]*(?:,\d+)?(?:\s*/\s*\d[\d.]*(?:,\d+)?)?)\s*' + _UNIT + r'\b', re.I)
_WORD = re.compile(r'[^\W\d_]{2,}')


def _cut(text, n=CELL):
    text = re.sub(r'\s+', ' ', text or '').strip()
    return text if len(text) <= n else text[:n - 1].rsplit(' ', 1)[0].rstrip(' ,;:/(') + '…'


def _int(s):
    return int(s.replace('.', '')) if s else 0


def _pages(body):
    """[(trang, chữ của trang đã gộp dòng)] từ một khối nguồn của content.md."""
    out, page, buf = [], 0, []
    for raw in body.splitlines():
        m = re.match(r'## Trang (\d+)', raw)
        if m:
            if page: out.append((page, re.sub(r'\s+', ' ', ' '.join(buf))))
            page, buf = int(m.group(1)), []
            continue
        if page: buf.append(raw)
    if page: out.append((page, re.sub(r'\s+', ' ', ' '.join(buf))))
    return out


def _ctx(text, start, end, before=46, after=24):
    a = max(0, start - before); b = min(len(text), end + after)
    s = text[a:b]
    if a: s = '…' + s.split(' ', 1)[-1]
    if b < len(text): s = s.rsplit(' ', 1)[0] + '…'
    return s.strip()


# 1. Cột "tuần trước" ---------------------------------------------------------------------------

_ABBR = [(r'nông nghiệp (?:và|&) môi trường', 'NN&MT'), (r'khoa học (?:và|&) công nghệ', 'KH&CN'), (r'văn hóa', 'VHTT&DL'),
         (r'khu công nghiệp', 'BQL KCN'), (r'xây dựng', 'Sở XD'), (r'y tế', 'Sở Y tế')]


def _abbr(name):
    low = name.lower()
    for pat, ab in _ABBR:
        if re.search(pat, low): return ab
    return name


def _topic(text, start, end):
    """Nhãn ngắn cho biết số nói về gì: 3 từ ngay trước số (vd "số hóa lũy kế"), thêm tên riêng viết hoa ngay sau số nếu có (vd "Panorama 360")."""
    label = _label(text, start, 4)
    m = re.match(r'\s*(?:[^\W\d_]+\s+)?([A-ZĐ][^\s,;:()]*(?:\s+\d+)?)', text[end:end + 40])
    return (label + (' · ' + m.group(1) if m else '')).strip(' ·')


def _base(header):
    return re.sub(r'\s*(?:của\s+)?(?:tuần|kỳ|tháng|quý)\s+trước|\s+trước\b', '', header, flags=re.I).strip().lower()


def cot_truoc(tabs_a, tabs_b, simple):
    """Bảng ma trận có cột "... tuần trước": giá trị ở kỳ này phải bằng cột "..." tương ứng của kỳ trước."""
    def mats(tabs):
        out = []
        for t in tabs:
            rows = [r for r in t['rows'] if any(r)]
            if len(rows) < 2 or len(rows[0]) < 3: continue
            header = [re.sub(r'\s+', ' ', h or '').strip() for h in rows[0]]
            if not any('trước' in h.lower() for h in header): continue
            sig = re.sub(r'\W+', '', ' '.join(header).lower())
            out.append({'sig': sig, 'header': header, 'rows': rows[1:], 'page': t['page']})
        return out
    ma, mb = mats(tabs_a), mats(tabs_b)
    found = []
    for tb in mb:
        ta = next((t for t in ma if t['sig'] == tb['sig']), None)
        if not ta: continue
        h = tb['header']; nc = 1 if len(h) > 2 and re.fullmatch(r'(stt|tt)', h[0].lower()) else 0
        keyed_a = {re.sub(r'\W+', '', (r[nc] if nc < len(r) else '').lower()): r for r in ta['rows']}
        for j, col in enumerate(h):
            if 'trước' not in col.lower(): continue
            base = next((k for k, c in enumerate(h) if k != j and c.lower() == _base(col)), None)
            if base is None: continue
            for r in tb['rows']:
                name = r[nc] if nc < len(r) else ''
                ra = keyed_a.get(re.sub(r'\W+', '', name.lower()))
                if not ra or j >= len(r) or base >= len(ra): continue
                said, real = (r[j] or '').strip(), (ra[base] or '').strip()
                if said and real and re.search(r'\d', said + real) and re.sub(r'\s', '', said) != re.sub(r'\s', '', real):
                    shown = re.sub(r'\s*(?:của\s+)?(?:tuần|kỳ|tháng|quý)\s+trước|\s+trước\b', '', col, flags=re.I).strip()
                    found.append([_cut(f'{_abbr(name)} · {shown}', 24), f'Bảng trang {tb["page"]}, cột "tuần trước" ghi {said}; báo cáo kỳ trước ghi {real}',
                                  'Đọc riêng kỳ này sẽ tưởng không đổi'])
    return found


# 2. Tỷ lệ vượt 100% ---------------------------------------------------------------------------

def vuot_100(pages_b, pages_a=()):
    found, seen = [], set()
    old_text = ' '.join(t for _, t in pages_a)
    ratios = []
    for page, text in pages_b:
        for m in _RATIO.finditer(text):
            x, y = _int(m.group(1)), _int(m.group(2))
            if y and x > y and not re.search(r'/\d{4}$', m.group(0)):
                key = (m.group(1), m.group(2))
                if key in seen: continue
                seen.add(key); ratios.append(x / y * 100)
                found.append((page, _topic(text, m.start(), m.end()), f'{m.group(1)}/{m.group(2)} {m.group(3)}'))
        for m in _PCT_OVER.finditer(text):
            v = float(m.group(2).replace(',', '.'))
            near = text[max(0, m.start() - 30):m.start()].lower()
            if any(abs(v - r) < 0.1 for r in ratios): continue
            if v > 100 and 'vượt' not in near and 'so với' not in text[m.end():m.end() + 20].lower():
                key = m.group(2)
                if key in seen: continue
                seen.add(key)
                found.append((page, _label(text, m.start()), m.group(2) + '%'))
    rows, pages_used = [], set()
    for page, ctx, val in found:
        if val.endswith('%') and page in pages_used: continue       # cùng trang đã có dạng a/b thì bỏ dòng % lặp ý
        pages_used.add(page)
        core = re.sub(r'\s+', '', val.split(' ')[0])
        had = core in re.sub(r'\s+', '', old_text) if old_text else False
        rows.append((had, [_cut(val, 24), _cut(f'Trang {page}' + (f', {ctx}' if ctx else ''), 60), 'Vượt 100% khối lượng' + (' (có từ kỳ trước)' if had else ' (mới ở kỳ này)')]))
    rows.sort(key=lambda x: x[0])                    # mới ở kỳ này lên trước
    return [r for _, r in rows]


# 3. Số kỳ trước còn sót ----------------------------------------------------------------------

def _label(text, start, n=3):
    """n từ có chữ ngay trước con số làm nhãn (vd "số hóa lũy kế"); bỏ dấu câu."""
    words = _WORD.findall(text[max(0, start - 80):start].lower())
    return ' '.join(words[-n:])


def _occ(pages):
    out = []
    for page, text in pages:
        for m in _VAL.finditer(text):
            val = re.sub(r'\s+', '', m.group(1))
            digits = re.sub(r'\D', '', val)
            if len(digits) < 3 and '/' not in val: continue
            before = text[max(0, m.start() - 48):m.start()].lower()
            after = text[m.end():m.end() + 16].lower()
            out.append({'page': page, 'val': val, 'unit': m.group(2).lower(), 'label': _label(text, m.start()),
                        'from': bool(re.search(r'\btừ\s*$|(tăng|giảm) từ|trước\s*:?\s*$', before) or re.match(r'\s*(lên|→|so với)', after)),
                        'ctx': _ctx(text, m.start(), m.end()), 'topic': _topic(text, m.start(), m.end())})
    return out


def so_cu(pages_a, pages_b):
    A, B = _occ(pages_a), _occ(pages_b)
    def by_key(occ):
        d = {}
        for o in occ:
            if o['label'] and not o['from']: d.setdefault((o['label'], o['unit']), set()).add(o['val'])
        return d
    ka, kb = by_key(A), by_key(B)
    for page, text in pages_b:                       # tỷ lệ a/b không kèm đơn vị (vd "đã thực hiện: 70/75") vẫn so được
        for m in re.finditer(r'(?<![\d/.,])(\d[\d.]*\s*/\s*\d[\d.]*)(?![\d/])', text):
            val = re.sub(r'\s+', '', m.group(1)); x, _, y = val.partition('/')
            if max(_int(x), _int(y)) <= 31: continue
            if not any(o['page'] == page and o['val'] == val for o in B):
                before = text[max(0, m.start() - 48):m.start()].lower()
                B.append({'page': page, 'val': val, 'unit': '', 'label': '', 'from': bool(re.search(r'(tăng|giảm) từ|\btừ\s*$', before)), 'ctx': _ctx(text, m.start(), m.end()), 'topic': _topic(text, m.start(), m.end())})
    rows, seen = [], set()
    for key, va in ka.items():
        vb = kb.get(key)
        if not vb or len(va) != 1 or len(vb) != 1 or va == vb: continue
        old, new = next(iter(va)), next(iter(vb))
        for o in B:
            if o['val'] == old and (o['unit'] == key[1] or (not o['unit'] and '/' in old)) and not o['from'] and (o['label'], o['unit']) != key and (old, o['page']) not in seen:
                seen.add((old, o['page']))
                pages_new = sorted({b['page'] for b in B if b['val'] == new and b['page'] != o['page']}) or sorted({b['page'] for b in B if b['val'] == new})
                rows.append([_cut(f'{old} {key[1]}'.strip(), 24), _cut(f'Trang {o["page"]} ({o["topic"]}) vẫn ghi {old}; trang {", ".join(map(str, pages_new[:3]))} ghi {new}', 80),
                             'Số kỳ trước còn sót trong kỳ này'])
    return rows


# 4. Mới hoặc hết -----------------------------------------------------------------------------

def moi_het(blocks, limit=8):
    rows = []
    for b in blocks:
        old, new = (b.get('old') or '').strip(), (b.get('new') or '').strip()
        if bool(old) == bool(new): continue
        text = new or old
        first = re.split(r'\s/\s', text)[0].strip()
        if len(_WORD.findall(first)) < 5: continue
        digits = len(re.sub(r'\D', '', first))
        if digits * 3 > len(first): continue
        rows.append(['Mới ở kỳ này' if new else 'Không còn ở kỳ này', _cut(first.lstrip('-•· ').rstrip(';'), 80), f'Trang {b.get("trang", "")}'])
        if len(rows) >= limit: break
    return rows


# Gợi ý điểm tiến bộ --------------------------------------------------------------------------

def _pct(s):
    m = re.fullmatch(r'\s*(\d+(?:,\d+)?)\s*%\s*', s or '')
    return float(m.group(1).replace(',', '.')) if m else None


def tang_manh(tables, limit=10):
    """Các dòng tăng (kỳ trước → kỳ này đều là %) từ bảng thay đổi, xếp theo mức tăng giảm dần."""
    groups = {}
    for t in tables:
        for r in t.get('rows', []):
            if len(r) < 4: continue
            a, b = _pct(r[-2]), _pct(r[-1])
            if a is not None and b is not None and b > a:
                groups.setdefault(r[0], []).append((b - a, f'{r[1]}: {r[-2]} → {r[-1]}'))
    ranked = sorted(((max(d for d, _ in v), k, sorted(set(v), key=lambda x: -x[0])[:2]) for k, v in groups.items()), key=lambda x: -x[0])
    # mỗi hệ thống MỘT dòng (tối đa hai giai đoạn tăng mạnh nhất): thẻ "Điểm tiến bộ" không bị dồn vào một phần mềm
    return [f'{k} · ' + '; '.join(txt for _, txt in items) for _, k, items in ranked[:limit]]


def build(tabs_a, tabs_b, body_a, body_b, blocks, simple=None):
    """Trả về dict: lech (hàng bảng Chỗ | Số liệu | Vì sao cần kiểm), moi_het (Loại | Nội dung | Trang)."""
    pa, pb = _pages(body_a), _pages(body_b)
    lech = cot_truoc(tabs_a, tabs_b, simple) + so_cu(pa, pb) + vuot_100(pb, pa)
    return {'lech': lech[:8], 'moi_het': moi_het(blocks)}
