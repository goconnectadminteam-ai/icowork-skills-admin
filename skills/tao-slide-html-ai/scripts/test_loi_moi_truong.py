"""Build hỏng do trình duyệt treo (lỗi môi trường) không được bắt model sửa parts."""
import importlib.util, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("iwork_drv3", Path(__file__).resolve().parent.parent / "iwork.py")
drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)

class LoiMoiTruong(unittest.TestCase):
    def test_trinh_duyet_treo(self):
        log = "[1] Cấu trúc: OK\nTraceback (most recent call last):\n  File x\nsubprocess.TimeoutExpired: Command '['chrome']' timed out after 180 seconds"
        self.assertIn("trình duyệt", drv.env_failure(log))
    def test_thieu_cong_cu(self):
        self.assertTrue(drv.env_failure("Traceback (most recent call last):\nFileNotFoundError: [WinError 2] The system cannot find the file specified"))
    def test_loi_noi_dung_khong_phai_moi_truong(self):
        self.assertEqual(drv.env_failure("[3] Số liệu: LỖI – 1 số không thấy trong nguồn"), "")

if __name__ == "__main__":
    unittest.main()
