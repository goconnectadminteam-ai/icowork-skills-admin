"""Lượt 6 vnptai: số chương 02 nhưng nhãn "Phần 03"; hai slide "Cảm ơn" liền nhau ở cuối."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("iwork_drv4", Path(__file__).resolve().parent.parent / "iwork.py")
drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)

def w(p, x): p.write_text(json.dumps(x, ensure_ascii=False), encoding="utf-8")
def r(p): return json.loads(p.read_text(encoding="utf-8"))

class ChuongVaSlideKet(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp()); (self.work / "parts").mkdir()

    def deck(self, slides):
        for i, s in enumerate(slides, 1): w(self.work / f"parts/{i:02d}.json", s)
        w(self.work / "plan.json", {"meta": {}, "outline": [s.get("tieuDe", "") for s in slides]})

    def test_hai_cam_on_cuoi_giu_mot(self):
        self.deck([{"mau": "bia", "tieuDe": "B"}, {"mau": "the", "tieuDe": "X"},
                   {"mau": "cam-on", "tieuDe": "Cảm ơn", "phu": "cũ"}, {"mau": "cam-on", "tieuDe": "Cảm ơn", "phu": "mới"}])
        self.assertIn("bỏ 1", drv.drop_duplicate_closing(self.work))
        self.assertFalse((self.work / "parts/04.json").exists())
        self.assertEqual(r(self.work / "parts/03.json")["phu"], "mới")
        self.assertEqual(len(r(self.work / "plan.json")["outline"]), 3)

    def test_mot_cam_on_khong_doi(self):
        self.deck([{"mau": "bia", "tieuDe": "B"}, {"mau": "cam-on", "tieuDe": "Cảm ơn"}])
        self.assertIsNone(drv.drop_duplicate_closing(self.work))

    def test_nhan_chuong_theo_so_moi(self):
        slides = [{"mau": "bia", "tieuDe": "B"}, {"mau": "chuong", "so": "01", "tieuDe": "Phần 01"},
                  {"mau": "the", "tieuDe": "X", "dauMuc": "X"}, {"mau": "chuong", "so": "03", "tieuDe": "Phần 03"},
                  {"mau": "the", "tieuDe": "Y", "dauMuc": "Y"}]
        self.deck(slides)
        drv.autofix_parts(self.work, [s["tieuDe"] for s in slides], {"bieu-do"})
        ch = r(self.work / "parts/04.json")
        self.assertEqual(ch["so"], "2"); self.assertEqual(ch["tieuDe"], "Phần 02")

if __name__ == "__main__":
    unittest.main()
