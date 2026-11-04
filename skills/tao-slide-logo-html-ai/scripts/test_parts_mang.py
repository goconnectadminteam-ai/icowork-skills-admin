"""Model ghi parts/NN.json dạng mảng nhiều slide (lượt 6) và gõ tên trường có dấu: driver phải tự tách, không văng lỗi."""
import importlib.util, json, tempfile, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("iwork_drv2", Path(__file__).resolve().parent.parent / "iwork.py")
drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)

def w(p, x): p.write_text(json.dumps(x, ensure_ascii=False), encoding="utf-8")

class PartsMang(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp()); (self.work / "parts").mkdir()
        w(self.work / "plan.json", {"meta": {}, "outline": ["Bìa", "Hai", "Ba"]})

    def test_tach_mang_giu_thu_tu(self):
        w(self.work / "parts/01.json", [{"mau": "bìa", "tieuĐề": "Bìa"}, {"mau": "the", "tieuDe": "Hai"}])
        w(self.work / "parts/02.json", {"mau": "the", "tieuDe": "Ba"})
        w(self.work / "parts/03.json", [{"mau": "the", "tieuDe": "Bốn"}])
        note = drv.split_array_parts(self.work)
        self.assertIn("4 tệp", note)
        got = [json.loads((self.work / f"parts/{i:02d}.json").read_text(encoding="utf-8")) for i in range(1, 5)]
        self.assertEqual([g["tieuDe"] for g in got], ["Bìa", "Hai", "Ba", "Bốn"])
        self.assertEqual(got[0]["mau"], "bia")
        plan = json.loads((self.work / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["outline"], ["Bìa", "Hai", "Ba", "Bốn"])

    def test_parts_dung_thi_khong_doi(self):
        for i, t in enumerate(["Bìa", "Hai", "Ba"], 1): w(self.work / f"parts/{i:02d}.json", {"mau": "the", "tieuDe": t})
        self.assertIsNone(drv.split_array_parts(self.work))

    def test_khong_doi_truong_khong_phai_k7(self):
        w(self.work / "parts/01.json", {"mau": "the", "tieuDe": "A", "nộiDung": ["x"]})
        drv.split_array_parts(self.work)
        got = json.loads((self.work / "parts/01.json").read_text(encoding="utf-8"))
        self.assertIn("nộiDung", got)   # không phải tên K7: để kiem-slide báo, không đoán

if __name__ == "__main__":
    unittest.main()
