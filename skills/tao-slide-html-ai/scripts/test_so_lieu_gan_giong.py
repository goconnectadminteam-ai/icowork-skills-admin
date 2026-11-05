import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report


class SourceVariantsTest(unittest.TestCase):
    """Thật (n-sl2, n-sl2b): số không khớp nguyên văn làm model grep nhiều lần rồi dừng giữa chừng; driver tự nêu sẵn dạng gần giống."""

    SRC = "Tổng kinh phí 25,100 triệu đồng; mã 25100; ngày 24/9/2026"

    def test_finds_same_digits_with_other_separator(self):
        got = report.source_variants("25.100", self.SRC)
        self.assertTrue(any('"25,100"' in g and "Tổng kinh phí" in g for g in got), got)

    def test_nothing_close_gives_empty_list(self):
        self.assertEqual(report.source_variants("99.999", self.SRC), [])

    def test_too_short_tokens_are_ignored(self):
        self.assertEqual(report.source_variants("5", self.SRC), [])


if __name__ == "__main__":
    unittest.main()
