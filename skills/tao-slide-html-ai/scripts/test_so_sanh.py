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


class KhongBocDuocBang(unittest.TestCase):
    """Hai nguồn không phải PDF có bảng (DOCX/PPTX): so-sanh.md vẫn phải gọn và không nói "driver tự thêm bảng"."""
    def test_so_sanh_van_gon_va_noi_dung_dung(self):
        import importlib.util, json
        S = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location('iwork_mod2', S / 'iwork.py'); m = importlib.util.module_from_spec(spec)
        argv = sys.argv; sys.argv = ['iwork.py']; spec.loader.exec_module(m); sys.argv = argv
        d = Path(tempfile.mkdtemp(prefix='kbb-'))
        (d / 'content.md').write_text(doc(1, '70,5%', '68,4%') + doc(2, '71,3%', '68,1%'), encoding='utf-8')
        (d / 'iwork-state.json').write_text(json.dumps({'files': [str(d / 'a.docx'), str(d / 'b.docx')]}), encoding='utf-8')
        self.assertIsNotNone(m.compare_periods(d))
        self.assertFalse((d / 'so-sanh-bang.json').exists())
        text = (d / 'so-sanh.md').read_text(encoding='utf-8')
        self.assertIn('Hai nguồn không có bảng có cấu trúc', text); self.assertNotIn('do driver TỰ THÊM', text); self.assertLess(len(text), 12000)


class CoSoSanhHayKhongDoNguoiDungNho(unittest.TestCase):
    """So sánh hay không do người dùng nhờ (model thêm --so-sanh), không do hai tệp trông giống nhau."""
    def run_start(self, extra):
        import subprocess, fitz
        S = Path(__file__).resolve().parent.parent
        d = Path(tempfile.mkdtemp(prefix='ssflag-'))
        for name, date in (('bao_cao_1.pdf', '23'), ('bao_cao_2.pdf', '30')):
            doc = fitz.open(); page = doc.new_page()
            lines = [f'Hà Nội, ngày {date} tháng 10 năm 2026'] + [f'Hạng mục số {k} đang triển khai theo đúng kế hoạch của dự án giai đoạn hai' for k in range(45)] + [f'Tiến độ chung toàn dự án đạt {70 if date == "23" else 71},5%']
            for i, line in enumerate(lines): page.insert_text((36, 36 + i * 15.5), line, fontsize=9)
            doc.save(d / name); doc.close()
        r = subprocess.run([sys.executable, str(S / 'iwork.py'), 'start', 'bao_cao_1.pdf', 'bao_cao_2.pdf', '--work', 'out', *extra], cwd=d, capture_output=True, text=True, encoding='utf-8', timeout=300)
        return r.stdout + r.stderr, d

    def test_khong_co_co_thi_lam_slide_binh_thuong_va_chi_nhac_nhe(self):
        out, d = self.run_start([])
        self.assertNotIn('HAI KỲ CỦA CÙNG MỘT BÁO CÁO', out); self.assertIn('--so-sanh', out)      # chỉ nhắc, không tự bật
        self.assertFalse((d / 'out' / 'so-sanh.md').exists())

    def test_co_co_so_sanh_thi_bat_che_do_so_sanh(self):
        out, d = self.run_start(['--so-sanh'])
        self.assertIn('HAI KỲ CỦA CÙNG MỘT BÁO CÁO', out); self.assertTrue((d / 'out' / 'so-sanh.md').exists())
        self.assertNotIn('ĐỌC (một lần): out/content.md', out)       # không in thêm lệnh đọc content.md mâu thuẫn với "chỉ đọc so-sanh.md"

    def test_word_va_powerpoint_cung_so_sanh_duoc(self):
        """Thật: mốc `## Slide n` (PowerPoint) và `## Toàn văn` (Word) không được nhận nên so sánh hai bản .pptx/.docx im lặng bỏ qua."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import so_sanh
        pptx = '# NGUỒN 1: a.pptx\n\n- Loại: pptx\n\n## Slide 1\n\nTiêu đề báo cáo dự án\nTiến độ đạt 70%\n\n## Slide 2\n\nRủi ro cần xử lý ngay\n'
        docx = '# NGUỒN 1: a.docx\n\n- Loại: docx\n\n## Toàn văn\n\nBáo cáo tiến độ dự án tháng mười\n## I. Tổng quan\nĐã tích hợp 9.360 thiết bị\n'
        self.assertEqual([p for p, _ in so_sanh._lines(pptx)], [1, 1, 2])
        self.assertEqual([p for p, _ in so_sanh._lines(docx)], [1, 1, 1])


if __name__ == '__main__':
    unittest.main()
