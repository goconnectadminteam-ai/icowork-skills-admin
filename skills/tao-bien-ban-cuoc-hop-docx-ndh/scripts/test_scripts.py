# -*- coding: utf-8 -*-
"""Test cho md_to_docx.py và extract_text.py (các lỗi thật gặp ở 3 skill trước: bảng mã Windows, mất giờ/hạn, .doc nhị phân, file thừa)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAU = HERE.parent / "assets" / "mau_bien_ban.md"


def run(script, *args, cwd=None, env=None):
    e = {**os.environ, **(env or {})}
    return subprocess.run([sys.executable, str(HERE / script), *args], cwd=cwd, capture_output=True, env=e)


def out(r):
    return (r.stdout + r.stderr).decode("utf-8", "replace")


class MdToDocx(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_tao_docx_tu_mau(self):
        r = run("md_to_docx.py", str(MAU), "kq.docx", cwd=self.d)
        self.assertEqual(r.returncode, 0, out(r))
        self.assertTrue((self.d / "kq.docx").stat().st_size > 5000)

    def test_bang_ma_khong_phai_utf8_van_thanh_cong(self):
        """Windows cp125x/ascii: lệnh in 'Đã tạo' không được làm script thoát lỗi sau khi đã tạo file."""
        env = {"LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"}
        env_clean = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING",)}
        r = subprocess.run([sys.executable, "-X", "utf8=0", str(HERE / "md_to_docx.py"), str(MAU), "kq.docx"], cwd=self.d,
                           capture_output=True, env={**env_clean, **env})
        self.assertEqual(r.returncode, 0, out(r))
        self.assertIn("Đã tạo", out(r))

    def test_xoa_nhap_chi_con_file_ket_qua(self):
        md = self.d / "p1.md"; md.write_text(MAU.read_text(encoding="utf-8"), encoding="utf-8")
        r = run("md_to_docx.py", "p1.md", "kq.docx", "--xoa-nhap", cwd=self.d)
        self.assertEqual(r.returncode, 0, out(r))
        self.assertEqual(sorted(p.name for p in self.d.iterdir()), ["kq.docx"])

    def test_noi_dung_la_duong_dan_bi_tu_choi(self):
        (self.d / "p.md").write_text("C:\\Users\\a\\bien-ban.md", encoding="utf-8")
        r = run("md_to_docx.py", "p.md", "kq.docx", cwd=self.d)
        self.assertNotEqual(r.returncode, 0); self.assertFalse((self.d / "kq.docx").exists())


class ExtractText(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_giu_gio_va_han_trong_cau(self):
        (self.d / "t.txt").write_text("Anh Nam: nộp báo cáo trước 17:00 ngày 12/11. Họp lúc 09:30 phòng B.\nChị Lan gửi hợp đồng trước 15:45.\n", encoding="utf-8")
        o = out(run("extract_text.py", "t.txt", cwd=self.d))
        for gio in ("17:00", "09:30", "15:45"):
            self.assertIn(gio, o)

    def test_bo_moc_transcript(self):
        dong = "".join(f"[00:{i:02d}:10] Anh A: nội dung số {i}\n" for i in range(10))
        o = out(run("extract_text.py", "tr.txt" if (self.d / "tr.txt").write_text(dong, encoding="utf-8") else "", cwd=self.d))
        self.assertNotIn("[00:", o); self.assertIn("nội dung số 3", o)

    def test_chuong_trinh_hop_it_dong_giu_gio(self):
        (self.d / "a.txt").write_text("09:00 Khai mạc\n10:30 Báo cáo tiến độ\n14:00 Kết luận\n", encoding="utf-8")
        o = out(run("extract_text.py", "a.txt", cwd=self.d))
        self.assertIn("09:00", o); self.assertIn("14:00", o)

    def test_khong_de_file_thua_trong_thu_muc_lam_viec(self):
        (self.d / "t.txt").write_text("Nội dung ngắn của cuộc họp.\n", encoding="utf-8")
        run("extract_text.py", "t.txt", cwd=self.d)
        self.assertEqual(sorted(p.name for p in self.d.iterdir()), ["t.txt"])

    def test_doc_nhi_phan_bi_chan_ro_rang(self):
        (self.d / "cu.doc").write_bytes(bytes.fromhex("D0CF11E0A1B11AE1") + bytes(range(1, 200)) * 3)
        r = run("extract_text.py", "cu.doc", cwd=self.d)
        self.assertNotEqual(r.returncode, 0); self.assertIn("DỪNG", out(r)); self.assertIn(".docx", out(r))

    def test_docx_doc_duoc(self):
        run("md_to_docx.py", str(MAU), "bb.docx", cwd=self.d)
        o = out(run("extract_text.py", "bb.docx", cwd=self.d))
        self.assertIn("BIÊN BẢN CUỘC HỌP", o)

    def test_in_tieng_viet_duoi_bang_ma_ascii(self):
        (self.d / "t.txt").write_text("Đồng chí Nguyễn Văn Ánh báo cáo.\n", encoding="utf-8")
        env_clean = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
        r = subprocess.run([sys.executable, "-X", "utf8=0", str(HERE / "extract_text.py"), "t.txt"], cwd=self.d, capture_output=True,
                           env={**env_clean, "LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"})
        self.assertEqual(r.returncode, 0, out(r)); self.assertIn("Nguyễn Văn Ánh", out(r))


class TomGon(unittest.TestCase):
    """File lớn (GoMeet 'tóm tắt theo dòng thời gian', 70 mục, ~39k ký tự, 7 phần) làm agent chậm và dễ dừng giữa chừng."""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        mucs = []
        for i in range(30):
            gio = f"16:{i:02d}:00 - 16:{i + 1:02d}:00"
            mucs.append(f"{gio}\nChủ đề số {i}\n1. Thảo luận chung về nội dung thứ {i} của hệ thống điều hành hàng ngày và các bước thực hiện liên quan. "
                        f"2. Mô tả thêm bối cảnh dài dòng không có việc cần làm cụ thể nào cả, chỉ là trao đổi. "
                        f"3. Anh Nam phụ trách hoàn thiện kịch bản {i} trước ngày 15/11.")
        self.f = self.d / "tl.txt"
        self.f.write_text("NỘI DUNG TÓM TẮT THEO DÒNG THỜI GIAN\nNội dung được tổng hợp từ AI có thể chưa đầy đủ.\nI. Thông tin\nID: 1\nII. Nội dung\n" + "\n".join(mucs), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_gon_hon_ban_day_du_nhung_giu_viec_nguoi_han(self):
        day = out(run("extract_text.py", "tl.txt", cwd=self.d)); gon = out(run("extract_text.py", "tl.txt", "--tom-gon", cwd=self.d))
        n = lambda s: int(s.split("Đã trích:")[1].split("ký tự")[0])
        self.assertLess(n(gon), n(day) * 0.7)
        self.assertEqual(gon.count("phụ trách hoàn thiện kịch bản"), 30)          # mọi việc có người và hạn đều còn
        self.assertEqual(gon.count("trước ngày 15/11"), 30)
        self.assertNotIn("không có việc cần làm cụ thể", gon)                    # ý nền dài dòng bị bỏ
        self.assertNotIn("tổng hợp từ AI", gon)

    def test_doc_mhtml_charset_unicode(self):
        html = "<html><head><title>x</title></head><body><p>BIÊN BẢN CUỘC HỌP</p><p>Anh Nam phụ trách việc A.</p></body></html>".encode("utf-16")
        import base64
        raw = ("MIME-Version: 1.0\r\nContent-Type: multipart/related; boundary=\"B\"\r\n\r\n--B\r\nContent-Type: text/html; charset=\"unicode\"\r\n"
               "Content-Transfer-Encoding: base64\r\n\r\n" + base64.encodebytes(html).decode() + "\r\n--B--\r\n")
        (self.d / "mau.doc").write_bytes(raw.encode("ascii"))
        o = out(run("extract_text.py", "mau.doc", cwd=self.d))
        self.assertIn("Anh Nam phụ trách việc A", o); self.assertNotIn("Traceback", o)


class TuCaiThuVien(unittest.TestCase):
    def test_thieu_thu_vien_va_khong_cai_duoc_thi_dung_ro_rang(self):
        d = Path(tempfile.mkdtemp()); fake = d / "fake"; fake.mkdir()
        (fake / "docx.py").write_text('raise ImportError("thiếu docx")\n', encoding="utf-8")
        try:
            r = run("md_to_docx.py", str(MAU), "x.docx", cwd=d, env={"PYTHONPATH": str(fake), "BIENBAN_BOOTSTRAPPED": "1"})
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("=== DỪNG", out(r)); self.assertIn("Cách B", out(r)); self.assertNotIn("Traceback", out(r))
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
