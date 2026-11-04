"""Ngày gợi ý phải là ngày của tài liệu, không phải ngày của văn bản được trích dẫn trong đó."""
import importlib.util, os, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("iwork_drv", Path(__file__).resolve().parent.parent / "iwork.py")
drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)

HEAD = "ĐỀ XUẤT CĐS HẢI PHÒNG\n BỘ CHÍNH TRỊ · NQ 57-NQ/TW (22/12/2024)\n Luật Dữ liệu (01/07/2025)\n NĐ 278/2025/NĐ-CP (22/10/2025)"

class NgayNguon(unittest.TestCase):
    def test_lay_ngay_trong_ten_tep(self):
        self.assertEqual(drv.source_date(["VNPT_De_xuat_CDS_Hai_Phong_30.10.2026_11h45.pdf"], HEAD), "30/10/2026")
    def test_bo_ngay_van_ban_duoc_trich(self):
        self.assertEqual(drv.source_date(["bao-cao.pdf"], "NQ 57-NQ/TW (22/12/2024)\nHải Phòng, ngày 30/10/2026"), "30/10/2026")
    def test_chi_co_ngay_trich_thi_van_dung(self):
        self.assertEqual(drv.source_date(["bao-cao.pdf"], "NQ 57-NQ/TW (22/12/2024)"), "22/12/2024")
    def test_ten_tep_so_vo_nghia_khong_dung(self):
        self.assertEqual(drv.source_date(["ban_45.13.2026.pdf"], "ngày 05/11/2026"), "05/11/2026")

if __name__ == "__main__":
    unittest.main()
