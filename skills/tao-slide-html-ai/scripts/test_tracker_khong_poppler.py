"""Máy Windows không có poppler (pdftotext/pdftocairo): tracker phải đọc PDF bằng PyMuPDF, không văng FileNotFoundError."""
import os, shutil, subprocess, sys, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracker

try:
    import fitz
except ImportError:
    fitz = None

def _pdf(path, lines):
    doc = fitz.open(); pg = doc.new_page()
    for i, t in enumerate(lines): pg.insert_text((72, 72 + 18 * i), t)
    doc.save(path)

@unittest.skipIf(fitz is None, "cần PyMuPDF")
class KhongPoppler(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.pdf = os.path.join(self.d, "Bao cao co dau cach.pdf")
        _pdf(self.pdf, ["STT Noi dung Trang thai", "1 Viec mot Xong", "2 Viec hai Dang lam"])

    def test_doc_chu_bang_pymupdf_khi_thieu_pdftotext(self):
        with mock.patch("shutil.which", return_value=None):
            pages, page_w, W = tracker.pdf_words(self.pdf)
        self.assertEqual(len(pages), 1)
        self.assertTrue(page_w[0] > 100)
        self.assertIn("STT", [w["t"] for w in W])

    def test_khong_co_pdftocairo_thi_bo_ke_hang(self):
        def boom(*a, **k): raise FileNotFoundError(2, "The system cannot find the file specified")
        with mock.patch("subprocess.run", side_effect=boom):
            self.assertEqual(tracker.row_rules(self.pdf, 1, 600), [])

    def test_pdf_rows_khong_vang_loi(self):
        def boom(*a, **k): raise FileNotFoundError(2, "WinError 2")
        with mock.patch("shutil.which", return_value=None), mock.patch("subprocess.run", side_effect=boom):
            tracker.pdf_rows(self.pdf)  # không được văng lỗi

if __name__ == "__main__":
    unittest.main()
