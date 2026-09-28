import gc
import os
import sys
import tempfile
import unittest
import warnings

from helpers import REPO, make_font

sys.path.insert(0, os.path.join(REPO, 'template', 'design', 'fonts'))
import font_check  # noqa: E402


class FontCheckTest(unittest.TestCase):
    def test_reports_missing_ruble_and_narrow_space(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'partial.ttf')
            make_font(path, [cp for cp in font_check.REQUIRED if cp not in (0x20BD, 0x202F)])
            self.assertEqual([cp for cp, _ in font_check.missing(path)], [0x202F, 0x20BD])
            self.assertEqual(font_check.main([path]), 1)

    def test_full_font_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'full.ttf')
            make_font(path, list(font_check.REQUIRED))
            self.assertEqual(font_check.missing(path), [])
            self.assertEqual(font_check.main([path]), 0)

    def test_extra_code_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'full.ttf')
            make_font(path, list(font_check.REQUIRED))
            self.assertEqual(font_check.missing(path, extra=[0x2192]), [(0x2192, 'extra U+2192')])
            self.assertEqual(font_check.main([path, '--extra', 'U+2192']), 1)

    def test_closes_the_font_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'full.ttf')
            make_font(path, list(font_check.REQUIRED))
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always', ResourceWarning)
                font_check.missing(path)
                gc.collect()
            self.assertEqual([str(w.message) for w in caught if issubclass(w.category, ResourceWarning)], [])


if __name__ == '__main__':
    unittest.main()
