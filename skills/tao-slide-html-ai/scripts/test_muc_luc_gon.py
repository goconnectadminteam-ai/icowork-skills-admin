"""Mục lục dựng lại từ slide chương không được cắt giữa cụm từ (lỗi thấy được trên GoConnect 04/11: "Định hướng CĐS của TW và ưu")."""
import importlib.util, sys, unittest
from pathlib import Path

S = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('iwork_mod', S / 'iwork.py'); m = importlib.util.module_from_spec(spec)
argv = sys.argv; sys.argv = ['iwork.py']; spec.loader.exec_module(m); sys.argv = argv

class MucLucGon(unittest.TestCase):
    def test_lay_ve_dau_truoc_lien_tu(self):
        self.assertEqual(m._short_label('Định hướng CĐS của TW và ưu tiên của Hải Phòng', 28), 'Định hướng CĐS của TW')
        self.assertEqual(m._short_label('Chiến lược đồng hành và triển khai CĐS', 28), 'Chiến lược đồng hành')
    def test_khong_de_hu_tu_treo(self):
        r = m._short_label('Đồng hành chiến lược CĐS của VNPT với Hải Phòng', 40)
        self.assertLessEqual(len(r), 40); self.assertFalse(r.split()[-1] in m._TAIL_WORDS)
    def test_ngan_thi_giu_nguyen(self):
        self.assertEqual(m._short_label('Cam kết thực hiện của VNPT', 28), 'Cam kết thực hiện của VNPT')

if __name__ == '__main__': unittest.main()


class KickerKhongCatGiuaCau(unittest.TestCase):
    """Thật (ca thử 04/11): dòng nhỏ trên tiêu đề hiện "Chuyển đổi mô hình đầu tiên mất", "điểm nghẽn: độ chính xác và"."""
    def test_nhan_dai_khong_bi_cat_giua_cau(self):
        for title, mau in [('Chuyển đổi mô hình đầu tiên mất 1 tháng', 'so-lieu'), ('6 điểm nghẽn: độ chính xác và cố định lõi làm chậm triển khai', 'van-de'),
                           ('Tập trung LLM cho Agentic AI và Edge CV để tối ưu hiệu năng', 'the')]:
            label = m._kicker_label(title, mau)
            self.assertLessEqual(len(label), 32)
            self.assertFalse(label.endswith((' và', ' mất', ' của')), label)
            self.assertTrue(label == title or label in title or label in m._KICKER_BY_MAU.values(), label)
        self.assertEqual(m._kicker_label('Tiến độ chung', 'bang'), 'Tiến độ chung')


class SlideThua(unittest.TestCase):
    """Slide thẻ/lộ trình/vấn đề viết cụt (Đối tác ABC 04/11: mô tả thẻ ~55/130 ký tự) được nhắc bổ sung từ nguồn."""
    def make(self, slides):
        import json, tempfile
        work = Path(tempfile.mkdtemp(prefix='thua-')); (work / 'parts').mkdir()
        for i, s in enumerate(slides, 1): (work / 'parts' / f'{i:02d}.json').write_text(json.dumps(s, ensure_ascii=False), encoding='utf-8')
        return work

    def test_phat_hien_the_cut_va_bo_qua_the_day(self):
        short = {'mau': 'the', 'the': [{'t': 'a', 'd': 'Mô tả cụt dưới 70 ký tự.'}] * 3}
        full = {'mau': 'the', 'the': [{'t': 'a', 'd': 'Mô tả đủ ý với chủ thể, con số, mốc và đơn vị lấy từ nguồn, dài hơn bảy mươi ký tự rõ ràng.'}] * 3}
        work = self.make([{'mau': 'bia'}, short, full, {'mau': 'bang', 'cot': ['a'], 'hang': [['x']]}])
        got = m.thin_slides(work)
        self.assertEqual([(n, mau) for n, mau, _ in got], [(2, 'the')])

    def test_van_de_va_lo_trinh(self):
        vd = {'mau': 'van-de', 'vanDe': {'t': 'a', 'y': ['ngắn', 'cũng ngắn']}, 'giaiPhap': {'t': 'b', 'y': ['x' * 90, 'y' * 90]}}
        lt = {'mau': 'lo-trinh', 'buoc': [{'t': 'a', 'd': 'ngắn', 'tg': 'Q1'}, {'t': 'b', 'd': 'ngắn nữa', 'tg': 'Q2'}]}
        got = m.thin_slides(self.make([vd, lt]))
        self.assertEqual(sorted(n for n, _, _ in got), [1, 2])
