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
    def test_add_compare_slides_chen_sau_slide_2_va_chia_8_hang(self):
        spec = importlib.util.spec_from_file_location('iwork_mod', HERE.parent / 'iwork.py'); m = importlib.util.module_from_spec(spec)
        argv = sys.argv; sys.argv = ['iwork.py']; spec.loader.exec_module(m); sys.argv = argv
        w = Path(tempfile.mkdtemp(prefix='cmp-')); (w / 'parts').mkdir()
        slides = [{'mau': 'bia', 'tieuDe': 'a'}, {'mau': 'so-lieu', 'tieuDe': 'b'}, {'mau': 'the', 'tieuDe': 'c'}]
        for i, s in enumerate(slides, 1): (w / 'parts' / f'{i:02d}.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
        (w / 'plan.json').write_text(json.dumps({'meta': {}, 'outline': ['a', 'b', 'c']}), encoding='utf-8')
        rows = [[f'Mục {k}', 'Chỉ tiêu', '1%', '2%'] for k in range(10)]
        (w / 'so-sanh-bang.json').write_text(json.dumps({'labels': ['23/10/2026', '30/10/2026'], 'tables': [{'title': 'Tiến độ tổng thể', 'page': 2, 'rows': rows}]}, ensure_ascii=False), encoding='utf-8')
        note = m.add_compare_slides(w)
        self.assertIn('2 slide bảng', note)
        plan = json.loads((w / 'plan.json').read_text(encoding='utf-8'))
        self.assertEqual(len(plan['outline']), 5)
        got = [json.loads((w / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 6)]
        self.assertEqual([g['mau'] for g in got], ['bia', 'so-lieu', 'bang', 'bang', 'the'])
        self.assertEqual([len(g['hang']) for g in got[2:4]], [5, 5]); self.assertIn('Kỳ trước 23/10', got[2]['cot'][2])


if __name__ == '__main__':
    unittest.main()
