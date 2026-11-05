"""Mẫu `bang` chứa tới 12 hàng; dòng thừa bị cắt trong khung phải bị báo tràn (K7 gốc không thấy)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import k7_build  # noqa: E402
from export_pdf import find_browser  # noqa: E402

COT = ['Đơn vị', 'Hạng mục', 'Tiến độ', 'Ghi chú']


def deck(n, cell):
    hang = [[f'Sở {i + 1}'] + [('Nội dung chi tiết hạng mục %d cột %d ' % (i, j) + 'x' * 80)[:cell] for j in (1, 2, 3)] for i in range(n)]
    return {'meta': {'id': 't', 'ten': {'vi': 'Thử'}}, 'slides': [
        {'mau': 'bang', 'dauMuc': 'Phần', 'tieuDe': 'Tiến độ theo đơn vị', 'cot': COT, 'hang': hang, 'nguon': 'Nguồn: thử', 'loiThoai': 'x'}]}


class BangNhieuDong(unittest.TestCase):
    def codes(self, n):
        return [x['ma'] for x in k7_build.kiem_k7(deck(n, 30)) if x['muc'] == 'loi']

    def test_cap_so_hang_la_12(self):
        self.assertNotIn('M4', self.codes(12))
        self.assertIn('M4', self.codes(13))

    @unittest.skipUnless(find_browser(), 'cần Chrome/Chromium để đo')
    def test_do_tran_that_bang_dong_ngan_va_dong_dai(self):
        browser = find_browser()
        with tempfile.TemporaryDirectory() as d:
            def tran(n, cell):
                path = Path(d) / 't.html'
                path.write_text(k7_build.render_k7(deck(n, cell)), encoding='utf-8')
                over, err = k7_build.check_overflow_k7(browser, path)
                self.assertIsNone(err)
                return bool(over)
            self.assertFalse(tran(12, 40))   # 12 hàng, mỗi ô một dòng: vừa khung
            self.assertFalse(tran(8, 80))    # 8 hàng, ô dài nhất: vừa
            self.assertTrue(tran(12, 80))    # 12 hàng ô dài: dòng cuối bị cắt, phải bị báo (trước đây không ai báo)


class GioiHanMoi(unittest.TestCase):
    """Giới hạn ký tự các mẫu đã nới theo số đo Chrome (thẻ 130, bước 100, ý vấn đề 120, nhãn số liệu 100); vượt xa mức đó vẫn là lỗi."""
    def issues(self, slide):
        base = {'dauMuc': 'P', 'tieuDe': 'T', 'loiThoai': 'x', 'nguon': 'n'}
        d = {'meta': {'id': 't', 'ten': {'vi': 'T'}}, 'slides': [dict(base, **slide)]}
        return [x for x in k7_build.kiem_k7(d) if x['ma'] == 'M2' and x['muc'] == 'loi']

    def test_the_130_ok_va_300_loi(self):
        mk = lambda n: {'mau': 'the', 'the': [{'icon': 'ai', 't': 'Tiêu đề', 'd': 'x' * n}] * 3}
        self.assertEqual(self.issues(mk(130)), [])
        self.assertTrue(self.issues(mk(300)))

    def test_vuot_nhe_gioi_han_chi_la_nhac_khong_chan_giao_file(self):
        """Thẻ 149/130 ký tự (vượt 15%) chỉ là nhắc: tràn thật do phép đo trình duyệt (M7) quyết định, không bắt model sửa rồi dừng giữa chừng."""
        mk = lambda n: {'mau': 'the', 'the': [{'icon': 'ai', 't': 'Tiêu đề', 'd': 'x' * n}] * 3}
        d = {'meta': {'id': 't', 'ten': {'vi': 'T'}}, 'slides': [dict({'dauMuc': 'P', 'tieuDe': 'T', 'loiThoai': 'x', 'nguon': 'n'}, **mk(149))]}
        self.assertEqual([x for x in k7_build.kiem_k7(d) if x['ma'] == 'M2' and x['muc'] == 'loi'], [])
        d['slides'][0] = dict(d['slides'][0], **mk(400))
        self.assertTrue([x for x in k7_build.kiem_k7(d) if x['ma'] == 'M2' and x['muc'] == 'loi'])      # quá xa giới hạn thì vẫn là lỗi

    def test_buoc_vandenghi_va_nhan_so_lieu(self):
        self.assertEqual(self.issues({'mau': 'lo-trinh', 'buoc': [{'icon': 'ai', 't': 'B', 'd': 'x' * 100, 'tg': 'Q1'}] * 3}), [])
        self.assertEqual(self.issues({'mau': 'van-de', 'vanDe': {'t': 'a', 'y': ['x' * 120] * 2}, 'giaiPhap': {'t': 'b', 'y': ['x' * 120] * 2}}), [])
        self.assertEqual(self.issues({'mau': 'so-lieu', 'so': [{'so': '1', 'nhan': 'x' * 100, 'icon': 'ai'}] * 3}), [])


if __name__ == '__main__':
    unittest.main()
