import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import k7_build


class HideLanguageSwitchTest(unittest.TestCase):
    PAGE = '<html><head><title>x</title></head><body><div class="tren__ngon-ngu"><button data-lang-btn="vi">VI</button><button data-lang-btn="en">EN</button></div></body></html>'

    def test_hides_with_css_and_keeps_buttons_for_the_frame_script(self):
        out = k7_build.hide_language_switch(self.PAGE)
        self.assertIn('.tren__ngon-ngu{display:none!important}', out)
        self.assertIn('data-lang-btn="en"', out)            # nút vẫn còn trong trang để JS của khung không lỗi

    def test_is_idempotent(self):
        once = k7_build.hide_language_switch(self.PAGE)
        self.assertEqual(k7_build.hide_language_switch(once), once)


if __name__ == '__main__':
    unittest.main()
