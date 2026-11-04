"""So sánh hai kỳ của cùng một báo cáo (tuần 4 và 5): model chỉ phải đọc chỗ khác nhau, không đọc 270 nghìn ký tự."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import so_sanh  # noqa: E402


def doc(n, pct, plan, extra=''):
    lines = [f'# NGUỒN {n}: Bao cao tuan {n}.pdf', '', '- Loại: pdf', '', '## Trang 1', f'Hà Nội, ngày {20 + n} tháng 10 năm 2026']
    lines += [f'Hạng mục số {k} đang triển khai theo đúng kế hoạch của dự án' for k in range(30)]
    lines += ['## Trang 2', f'Tiến độ chung toàn dự án đạt {pct}', f'Kế hoạch đến kỳ báo cáo {plan}'] + [f'Nội dung chung số {k} không đổi giữa hai kỳ báo cáo' for k in range(30)]
    if extra: lines += ['## Trang 3', extra]
    return '\n'.join(lines) + '\n'


class SoSanh(unittest.TestCase):
    def work(self, text):
        d = Path(tempfile.mkdtemp(prefix='ss-')); (d / 'content.md').write_text(text, encoding='utf-8'); return d

    def test_chi_giu_cho_khac_va_noi_ro_huong(self):
        w = self.work(doc(1, '70,5%', '68,4%') + doc(2, '71,3%', '68,1%', 'Rủi ro mới: chậm bàn giao dữ liệu'))
        path, prev, cur, n = so_sanh.build(w)
        text = path.read_text(encoding='utf-8')
        self.assertEqual((prev, cur), ('21/10/2026', '22/10/2026')); self.assertGreaterEqual(n, 2)
        self.assertIn('70,5%', text); self.assertIn('71,3%', text); self.assertIn('MỚI', text); self.assertIn('Rủi ro mới', text)
        self.assertNotIn('Nội dung chung số 7', text)          # chỗ giống nhau không được đưa vào
        self.assertLess(len(text), 6000)

    def test_dao_thu_tu_theo_ngay_bao_cao(self):
        w = self.work(doc(2, '71,3%', '68,1%') + doc(1, '70,5%', '68,4%'))     # kỳ mới đưa trước
        _, prev, cur, _ = so_sanh.build(w)
        self.assertEqual((prev, cur), ('21/10/2026', '22/10/2026'))

    def test_khong_phai_hai_ky_thi_bo_qua(self):
        other = '\n'.join(['# NGUỒN 2: khac.pdf', '', '## Trang 1'] + [f'Một tài liệu hoàn toàn khác biệt dòng {k} nói về chủ đề lạ' for k in range(60)]) + '\n'
        self.assertIsNone(so_sanh.build(self.work(doc(1, '70%', '60%') + other)))
        self.assertIsNone(so_sanh.build(self.work(doc(1, '70%', '60%'))))      # chỉ một nguồn


if __name__ == '__main__':
    unittest.main()
