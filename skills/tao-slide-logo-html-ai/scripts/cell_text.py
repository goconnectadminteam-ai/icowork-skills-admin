"""Làm gọn chữ trong một ô bảng: bỏ gạch đầu dòng, giữ trọn câu, không cắt giữa câu và không thêm "…".
Ô của nguồn hay là cả đoạn có nhiều gạch đầu dòng ("- Đang rà soát … - Tích hợp 2FA …"); đổ nguyên vào bảng thì thành cả đoạn văn, cắt cứng thì thành "…"."""
import re

HARD = 160     # K7: ô bảng tối đa 160 ký tự; câu đầu dài hơn thì cắt ở hết một vế, không cắt giữa vế


def segments(text):
    """Tách ô thành các ý: theo dòng, theo gạch đầu dòng (- • +) và theo hết câu."""
    s = str(text or '').replace('\r', '\n')
    s = re.sub(r"(?:(?<=\s)|^)['\"]?[-•+–]\s+(?=\S)", '\n', s)           # gạch đầu dòng giữa câu hoặc đầu dòng
    parts = []
    for line in s.split('\n'):
        for sent in re.split(r'(?<=[.;!?])\s+(?=[A-ZÀ-ỸĐ0-9])', line):
            sent = re.sub(r'\s+', ' ', sent).strip(" \t'\"-•+–;")
            if sent: parts.append(sent)
    return parts


def clause_cut(text, limit):
    """Cắt ở hết một vế (dấu phẩy, chấm phẩy, ' - ') gần `limit` nhất; không có thì cắt ở ranh giới từ. Không thêm "…"."""
    if len(text) <= limit: return text
    head = text[:limit]
    cut = max(head.rfind(', '), head.rfind('; '), head.rfind(' - '))
    if cut < limit * 0.4: cut = head.rfind(' ')
    return head[:cut].rstrip(' ,;:/-–·') if cut > 0 else head


def tidy_cell(text, limit=100):
    """Ý đầu giữ trọn (tối đa HARD ký tự); thêm các ý sau chừng nào còn vừa `limit`, nối bằng '; '."""
    segs = segments(text)
    if not segs: return ''
    out = segs[0].rstrip('.;')
    if len(out) > HARD: out = clause_cut(out, HARD)
    for seg in segs[1:]:
        seg = seg.rstrip('.;')
        if len(out) + 2 + len(seg) <= limit: out += (' ' if out.endswith(':') else '; ') + seg      # sau tiêu đề kết thúc bằng ':' thì nối bằng khoảng trắng, không ':;'
        else: break
    return out
