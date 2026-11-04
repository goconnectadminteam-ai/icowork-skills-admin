"""Số và đơn vị nằm ở hai dòng của một cột hẹp trong PDF ("tối thiểu 1" … "Gb/s"): kiểm số không được báo bịa.
Số thật sự không có trong nguồn vẫn phải bị báo."""
import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report
try:
    import fitz
except ImportError:
    fitz = None

@unittest.skipIf(fitz is None, "cần PyMuPDF")
class SoXuongDong(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp()) / "report-output"
        pdf = self.work.parent / "nguon co dau cach.pdf"
        doc = fitz.open(); pg = doc.new_page()
        pg.insert_textbox(fitz.Rect(72, 72, 160, 200), "Cap quang toc do toi thieu 1 Gb/s cho nguoi dung")
        pg.insert_textbox(fitz.Rect(170, 72, 400, 200), "Cot ben canh: 100% ho so so hoa")
        doc.save(str(pdf))
        meta = self.work / "sources" / "01-nguon" / "metadata.json"; meta.parent.mkdir(parents=True)
        meta.write_text(json.dumps({"source": str(pdf), "type": "pdf"}), encoding="utf-8")
        # content.md kiểu giữ bố cục: "1" và "Gb/s" bị chen chữ cột bên cạnh
        self.layout = "toi thieu 1      Cot ben canh: 100% ho so so hoa\nGb/s"

    def rep(self, text):
        return {"slides": [{"mau": "the", "tieuDe": "Ha tang", "the": [{"t": "Cap quang", "d": text}]}]}

    def test_bao_cu_nham_khi_chi_dung_content_md(self):
        self.assertIn("1 Gb", report.check_numbers(self.rep("toi thieu 1 Gb/s"), self.layout))

    def test_khong_bao_nham_khi_doi_chieu_them_chu_pdf(self):
        src = self.layout + "\n" + report.plain_pdf_text(self.work)
        self.assertEqual(report.check_numbers(self.rep("toi thieu 1 Gb/s"), src), {})

    def test_so_bia_van_bi_bao(self):
        src = self.layout + "\n" + report.plain_pdf_text(self.work)
        self.assertIn("10 Gb", report.check_numbers(self.rep("toi thieu 10 Gb/s"), src))

    def test_khong_co_thu_muc_sources_thi_rong(self):
        self.assertEqual(report.plain_pdf_text(Path(tempfile.mkdtemp())), "")

if __name__ == "__main__":
    unittest.main()
