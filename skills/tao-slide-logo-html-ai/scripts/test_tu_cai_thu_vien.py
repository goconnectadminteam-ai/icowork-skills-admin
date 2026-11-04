# -*- coding: utf-8 -*-
"""Máy mới thiếu thư viện: driver tự cài vào môi trường riêng (không để model gõ pip install) và dừng rõ khi không cài được."""
import importlib.util, os, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("iwork_boot", Path(__file__).resolve().parent.parent / "iwork.py")
drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)


class TuCaiThuVien(unittest.TestCase):
    def setUp(self):
        self.real_find = drv.importlib.util.find_spec
        self.old = os.environ.get("IWORK_BOOTSTRAPPED")

    def tearDown(self):
        drv.importlib.util.find_spec = self.real_find
        if self.old is None: os.environ.pop("IWORK_BOOTSTRAPPED", None)
        else: os.environ["IWORK_BOOTSTRAPPED"] = self.old

    def thieu(self, *modules):
        drv.importlib.util.find_spec = lambda name, *a, **k: None if name in modules else self.real_find(name, *a, **k)

    def test_du_thu_vien_thi_khong_lam_gi(self):
        self.assertIsNone(drv.bootstrap_libs())

    def test_thieu_thu_vien_va_da_chay_lai_ma_van_thieu_thi_dung_ro_rang(self):
        os.environ["IWORK_BOOTSTRAPPED"] = "1"; self.thieu("docx")
        with self.assertRaises(SystemExit) as cm: drv.bootstrap_libs()
        msg = str(cm.exception.code)
        self.assertIn("=== DỪNG", msg); self.assertIn("python-docx", msg); self.assertIn("vc_redist", msg); self.assertIn("KHÔNG tự làm slide bằng tay", msg)

    def test_thong_bao_khong_lo_duong_dan_moi_truong(self):
        os.environ["IWORK_BOOTSTRAPPED"] = "1"; self.thieu("pptx")
        with self.assertRaises(SystemExit) as cm: drv.bootstrap_libs()
        self.assertNotIn(str(Path.home()), str(cm.exception.code)); self.assertNotIn("pip install", str(cm.exception.code))

    def test_core_missing_ghi_ten_goi(self):
        self.thieu("PIL"); self.assertEqual(drv.core_missing().get("PIL"), "Pillow")


if __name__ == "__main__":
    unittest.main()
