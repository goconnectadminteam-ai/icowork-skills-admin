"""Kiểm phần soát số liệu lệch giữa hai kỳ (kiem_lech.py) và phần chặn nội dung trước build (iwork.authored_checks)."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kiem_lech as k  # noqa: E402

A = """## Trang 3
Kết quả lũy kế
## Trang 16
Khối lượng số hóa lũy kế: 1.989,667 km đường
## Trang 19
xử lý hoàn tất 70/75 ảnh Panorama 360
"""
B = """## Trang 3
Kết quả lũy kế
## Trang 16
đã số hóa 1.989,667 km đường, tạo lập
## Trang 19
xử lý hoàn tất 100/75 ảnh Panorama 360 (đạt 133,3%)
## Trang 45
Khối lượng số hóa lũy kế: 2.233,362 km đường
## Trang 46
Nội dung công việc đã thực hiện: 70/75
## Trang 47
tăng từ 150/247 dự án lên 200/247 dự án; Tiến độ vượt 105% so với kế hoạch
"""


def tab(page, rows):
    return {'page': page, 'rows': rows, 'head': '', 'so': None}


class KiemLech(unittest.TestCase):
    def setUp(self):
        self.pa, self.pb = k._pages(A), k._pages(B)

    def test_vuot_100_bat_ty_le_va_bo_phan_tram_lap(self):
        rows = k.vuot_100(self.pb, self.pa)
        vals = [r[0] for r in rows]
        self.assertIn('100/75 ảnh', vals)
        self.assertNotIn('133,3%', vals)            # cùng ý với 100/75 nên không lặp
        self.assertFalse(any('105' in v for v in vals))   # "vượt 105% so với kế hoạch" không phải lỗi
        self.assertIn('mới ở kỳ này', rows[0][2])

    def test_so_ky_truoc_con_sot(self):
        rows = k.so_cu(self.pa, self.pb)
        joined = ' | '.join(' '.join(r) for r in rows)
        self.assertIn('1.989,667', joined)
        self.assertIn('2.233,362', joined)
        self.assertIn('70/75', joined)              # phụ lục không kèm đơn vị vẫn bắt được
        self.assertNotIn('150/247', joined)         # "tăng từ 150/247" là so sánh hợp lệ

    def test_cot_tuan_truoc_lech_voi_ky_truoc(self):
        head = ['STT', 'Đơn vị', 'Phần mềm tuần trước', 'Phần mềm', 'CSDL tuần trước', 'CSDL']
        ta = [tab(3, [head, ['1', 'Sở Y tế', '99,5%', '99,5%', '93,4%', '93,4%'], ['2', 'Sở Khoa học & Công nghệ', '71,5%', '72,8%', '68,3%', '75,8%']])]
        tb = [tab(3, [head, ['1', 'Sở Y tế', '99,5%', '99,5%', '93,4%', '93,4%'], ['2', 'Sở Khoa học & Công nghệ', '73,8%', '73,8%', '75,8%', '75,8%']])]
        rows = k.cot_truoc(ta, tb, None)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0][0].startswith('KH&CN · Phần mềm'))
        self.assertIn('73,8%', rows[0][1]); self.assertIn('72,8%', rows[0][1])

    def test_moi_het_chi_lay_dong_chu_day_du(self):
        blocks = [{'old': '', 'new': '- Rủi ro đánh giá ATTT cấp độ 3 kéo dài;', 'trang': 23},
                  {'old': 'mềm 0%', 'new': '', 'trang': 10},
                  {'old': 'a', 'new': 'b c', 'trang': 2}]
        rows = k.moi_het(blocks)
        self.assertEqual(rows, [['Mới ở kỳ này', 'Rủi ro đánh giá ATTT cấp độ 3 kéo dài', 'Trang 23']])

    def test_tang_manh_gop_theo_he_thong_moi_he_thong_mot_dong(self):
        """Điểm tiến bộ không được dồn 4 thẻ vào một phần mềm: mỗi hệ thống một dòng, tối đa hai giai đoạn mạnh nhất."""
        rows = [['PM Kho hồ sơ', 'Kiểm thử', '70%', '90%'], ['PM Kho hồ sơ', 'Đào tạo', '70%', '85%'], ['PM Kho hồ sơ', 'Cài đặt', '95%', '100%'], ['CSDL nền', 'Tiếp biên', '62%', '85%']]
        got = k.tang_manh([{'rows': rows}])
        self.assertEqual(len(got), 2)
        self.assertTrue(got[0].startswith('CSDL nền') and got[1].startswith('PM Kho hồ sơ'))
        self.assertEqual(got[1].count('→'), 2)

    def test_tang_manh_xep_theo_muc_tang(self):
        tables = [{'rows': [['A', 'x', '43,4%', '59,5%'], ['B', 'y', '70%', '72%'], ['C', 'z', '75,8%', '70,7%']]}]
        self.assertEqual(k.tang_manh(tables), ['A · x: 43,4% → 59,5%', 'B · y: 70% → 72%'])


class AuthoredChecks(unittest.TestCase):
    def test_chan_thieu_tien_bo_cau_het_han_va_hai_goi(self):
        spec = importlib.util.spec_from_file_location('iwork_mod', HERE.parent / 'iwork.py'); iw = importlib.util.module_from_spec(spec)
        sys.argv = ['iwork.py']; spec.loader.exec_module(iw)
        with tempfile.TemporaryDirectory() as d:
            w = Path(d); (w / 'parts').mkdir(); (w / 'so-sanh-bang.json').write_text('{}', encoding='utf-8')
            slides = [{'mau': 'bia', 'tieuDe': 'So sánh'}, {'mau': 'so-lieu', 'tieuDe': 'Cả hai gói đều tăng'},
                      {'mau': 'the', 'dauMuc': 'Điểm cần chú ý', 'tieuDe': 'x', 'the': [{'t': 'a', 'd': 'Thời gian thi công chỉ còn hơn 02 tháng từ 17/7'}]}]
            for i, s in enumerate(slides, 1): (w / 'parts' / f'{i:02d}.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
            out = iw.authored_checks(w, ['a', 'b', 'c'], {})
            text = ' '.join(out)
            self.assertIn('Điểm tiến bộ', text); self.assertIn('hai gói', text); self.assertIn('02 tháng', text)
            self.assertEqual(iw.authored_checks(w, ['a', 'b', 'c'], {'lint_rounds': 2}), [])   # không lặp mãi


if __name__ == '__main__':
    unittest.main()
