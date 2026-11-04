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
