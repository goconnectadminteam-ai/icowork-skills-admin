"""So từng dòng bảng của hai kỳ báo cáo: đúng cột, không tự trừ, hệ thống + giai đoạn."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bang_so_sanh as bs  # noqa: E402


def table(rows, page=2, head='Tiến độ'):
    return {'page': page, 'rows': rows, 'head': head, 'so': None}


class SoBang(unittest.TestCase):
    def test_bang_khoa_gia_tri_chon_dung_cot_ten(self):
        a = table([['STT', 'Nội dung', 'Kết quả'], ['1', 'Tiến độ chung toàn dự án', '70,5%'], ['2', 'Kế hoạch đến kỳ báo cáo', '68,4%'], ['3', 'Giải ngân', '0%']])
        b = table([['STT', 'Nội dung', 'Kết quả'], ['1', 'Tiến độ chung toàn dự án', '71,3%'], ['2', 'Kế hoạch đến kỳ báo cáo', '68,1%'], ['3', 'Giải ngân', '0%']])
        out = bs.diff_simple([a], [b])
        self.assertEqual([r[0] for r in out[0]['rows']], ['Tiến độ chung toàn dự án', 'Kế hoạch đến kỳ báo cáo'])
        self.assertEqual(out[0]['rows'][0][2:], ['70,5%', '71,3%'])        # Giải ngân không đổi nên không có mặt

    def test_bo_cot_tuan_truoc_de_khong_so_nham_cot(self):
        hdr = ['STT', 'Đơn vị', 'Phần mềm tuần trước', 'Phần mềm', 'CSDL tuần trước', 'CSDL']
        a = table([hdr, ['1', 'Sở KH&CN', '71,5%', '72,8%', '68,3%', '75,8%']], page=3)
        b = table([hdr, ['1', 'Sở KH&CN', '73,8%', '73,8%', '75,8%', '75,8%']], page=3)
        rows = bs.diff_simple([a], [b])[0]['rows']
        self.assertEqual(rows, [['Sở KH&CN', 'Phần mềm', '72,8%', '73,8%']])    # không phải 71,5% → 73,8%

    def test_he_thong_va_giai_doan(self):
        def tb(total, dev):
            return table([['', '', '', '', ''], ['1.', f'Phần mềm X (tiến độ tổng {total}%)', '- Lập kế hoạch - Phát triển phần mềm', f'100% {dev}%', 'mô tả']], page=5)
        out = bs.diff_systems([tb('60,5', 70)], [tb('65,5', 80)])
        self.assertEqual(out[0]['rows'][0][2:], ['60,5%', '65,5%'])
        self.assertEqual(out[1]['rows'], [['Phần mềm X', 'Phát triển phần mềm', '70%', '80%']])

    def test_bang_dai_hon_gioi_han_khong_so(self):
        rows = [['STT', 'Hạng mục', 'Tiến độ']] + [[str(i), f'Việc số {i}', '10%'] for i in range(30)]
        self.assertEqual(bs.diff_simple([table(rows)], [table(rows)]), [])


class QuaHan(unittest.TestCase):
    def test_chi_dao_den_han_chua_xong(self):
        hdr = ['TT', 'Chỉ đạo', 'Hạn thực hiện', 'Đánh giá']
        t = table([hdr, ['1.', 'Việc đã xong', '16/9/2 026', 'Hoàn thành'], ['2.', 'Việc chưa xong', '30/10/ 2026', 'Đang thực hiện, cần gia hạn'],
                   ['3.', 'Việc chưa hoàn thành', '15/10/2026', 'Quy hoạch đô thị chưa hoàn thành'], ['4.', 'Việc chưa tới hạn', '30/11/2026', 'Đang làm']], page=21)
        got = bs.overdue([t], (2026, 10, 30))
        self.assertEqual([r[0] for r in got], ['Việc chưa xong', 'Việc chưa hoàn thành'])
        self.assertEqual(got[0][1], '30/10/2026')

    def test_noi_bang_ngat_trang(self):
        a = table([['STT', 'Nội dung', 'Hạn', 'Tiến độ'], ['1', 'Việc một', '30/9/2026', 'Đã hoàn thành'], ['2', 'Việc hai', '15/10/2026', 'Đang chờ Quy hoạch']], page=20)
        b = table([['', '', '', 'chung của Tỉnh'], ['3', 'Việc ba', '30/10/2026', 'Đang xử lý']], page=21)
        joined = bs._join_continued([a, b])
        self.assertEqual(len(joined), 1)
        self.assertEqual(joined[0]['rows'][2][3], 'Đang chờ Quy hoạch chung của Tỉnh'); self.assertEqual(joined[0]['rows'][3][1], 'Việc ba')


class ChenSlide(unittest.TestCase):
    def _iwork(self):
        spec = importlib.util.spec_from_file_location('iwork_mod', HERE.parent / 'iwork.py'); m = importlib.util.module_from_spec(spec)
        argv = sys.argv; sys.argv = ['iwork.py']; spec.loader.exec_module(m); sys.argv = argv
        return m

    def _workdir(self, rows):
        w = Path(tempfile.mkdtemp(prefix='cmp-')); (w / 'parts').mkdir()
        slides = [{'mau': 'bia', 'tieuDe': 'a'}, {'mau': 'so-lieu', 'tieuDe': 'b'}, {'mau': 'the', 'tieuDe': 'c'}]
        for i, s in enumerate(slides, 1): (w / 'parts' / f'{i:02d}.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
        (w / 'plan.json').write_text(json.dumps({'meta': {}, 'outline': ['a', 'b', 'c']}), encoding='utf-8')
        (w / 'so-sanh-bang.json').write_text(json.dumps({'labels': ['23/10/2026', '30/10/2026'], 'tables': [{'title': 'Tiến độ tổng thể', 'page': 2, 'rows': rows}]}, ensure_ascii=False), encoding='utf-8')
        return w

    def test_add_compare_slides_chen_sau_slide_2_va_chia_theo_chieu_cao_do_that(self):
        """Đo thật bằng Chrome: từ 5 hàng chữ nhỏ, hàng một dòng cao 50px, nên 10 hàng ngắn vừa MỘT slide; 14 hàng ngắn vượt tối đa 12 hàng nên chia hai slide."""
        m = self._iwork()
        w = self._workdir([[f'Mục {k}', 'Chỉ tiêu', '1%', '2%'] for k in range(10)])
        note = m.add_compare_slides(w)
        self.assertIn('1 slide bảng', note)
        got = [json.loads((w / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 5)]
        self.assertEqual([g['mau'] for g in got], ['bia', 'so-lieu', 'bang', 'the'])
        self.assertEqual(len(got[2]['hang']), 10); self.assertIn('Kỳ trước 23/10', got[2]['cot'][2])
        w2 = self._workdir([[f'Mục {k}', 'Chỉ tiêu', '1%', '2%'] for k in range(14)])
        self.assertIn('2 slide bảng', m.add_compare_slides(w2))

    def test_cot_dai_len_dau_thi_dua_cot_ngan_len_truoc_va_bo_dau_cuoi_o(self):
        """Thật (f-cmp): cột đầu K7 chỉ ~16 ký tự mỗi dòng, ô "Nội dung" dài 100 ký tự cao 6 dòng nên bảng xé 5 slide; ô còn đuôi ';' '.'."""
        m = self._iwork()
        cols, rows = m.shape_table(['Nội dung', 'Hạn', 'Tình trạng kỳ này'],
                                   [['Xây dựng công cụ quản lý công việc có chat, giao việc, đôn đốc, cập nhật và lưu vết xử lý.', '30/9/2026', 'Đang bàn giao;']])
        self.assertEqual(cols, ['Hạn', 'Nội dung', 'Tình trạng kỳ này'])
        self.assertEqual(rows[0][0], '30/9/2026'); self.assertFalse(rows[0][1].endswith('.')); self.assertEqual(rows[0][2], 'Đang bàn giao')
        cols, rows = m.shape_table(['Mục', 'Chỉ tiêu', 'Kỳ trước', 'Kỳ này'], [['Hệ thống quản lý cơ sở dữ liệu Khu công nghiệp và hỗ trợ xúc tiến đầu tư', 'Kiểm thử', '30%', '35%']])
        self.assertEqual(cols, ['Chỉ tiêu', 'Mục', 'Kỳ trước', 'Kỳ này'])      # cột "Kỳ trước/Kỳ này" không bao giờ lên đầu
        cols, rows = m.shape_table(['Mục', 'Chỉ tiêu', 'Kỳ trước', 'Kỳ này'], [['Ngắn', 'Kiểm thử', '30%', '35%']])
        self.assertEqual(cols, ['Mục', 'Chỉ tiêu', 'Kỳ trước', 'Kỳ này'])      # cột đầu đã ngắn: giữ nguyên thứ tự

    def test_chia_hang_khong_bao_gio_de_lo_rong_hoac_mot_hang(self):
        """Thật (n-w2): bảng 5 hàng chia thành "(1/3) (2/3) (3/3)" với lô giữa rỗng (hang: []), build lỗi M4 và lượt không giao."""
        m = self._iwork()
        import itertools
        for lens in itertools.product((10, 60, 120), repeat=5):
            rows = [[('A' * a), 'Kết quả', '1%', '2%'] for a in lens]
            chunks = m.chunk_rows(rows)
            self.assertTrue(all(len(c) >= 1 for c in chunks) and sum(len(c) for c in chunks) == 5 and all(len(c) <= 12 for c in chunks), (lens, [len(c) for c in chunks]))
            self.assertTrue(all(len(c) >= 2 or len(chunks) == 1 or m._table_height(c, [10, 10, 10]) > 0 for c in chunks))
        for n in range(2, 14):
            chunks = m.chunk_rows([[f'Mục {k}', 'x', '1', '2'] for k in range(n)])
            self.assertTrue(all(len(c) >= 2 for c in chunks) and sum(len(c) for c in chunks) == n, (n, [len(c) for c in chunks]))      # hàng ngắn: luôn chia được thành lô ≥ 2 hàng

    def test_hang_dai_chia_theo_so_dong_va_khong_cat_chu(self):
        """Thật: ô dài bị cắt bằng "…" ở 36-48 ký tự làm nhiều hàng thành cùng một chữ. Nay giữ nguyên chữ và chia thêm slide."""
        m = self._iwork()
        rows = [[f'Hệ thống thông tin số {k} của sở ngành địa phương', 'Tiến độ toàn khối đạt mức cao theo kế hoạch', 'Hoàn thành khảo sát chi tiết 75% và thiết kế 60%', 'Hoàn thành khảo sát chi tiết 80% và thiết kế 70%'] for k in range(10)]
        w = self._workdir(rows)
        m.add_compare_slides(w)
        plan = json.loads((w / 'plan.json').read_text(encoding='utf-8'))
        parts = [json.loads((w / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, len(plan['outline']) + 1)]
        tables = [p for p in parts if p['mau'] == 'bang']
        self.assertGreaterEqual(len(tables), 2)
        self.assertTrue(all(2 <= len(t['hang']) <= 12 for t in tables))
        cells = [c for t in tables for r in t['hang'] for c in r]
        self.assertFalse(any('…' in c for c in cells))
        self.assertEqual(sorted(r[0] for t in tables for r in t['hang']), sorted(r[0] for r in rows))      # đủ 10 hàng, không mất hàng nào


if __name__ == '__main__':
    unittest.main()
