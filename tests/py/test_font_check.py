import os
import sys
import tempfile
import unittest

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from helpers import REPO

sys.path.insert(0, os.path.join(REPO, 'template', 'design', 'fonts'))
import font_check  # noqa: E402


def make_font(path, codepoints):
    names = ['.notdef'] + ['g%04X' % cp for cp in codepoints]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({cp: 'g%04X' % cp for cp in codepoints})
    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({n: empty for n in names})
    fb.setupHorizontalMetrics({n: (500, 0) for n in names})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({'familyName': 'Test', 'styleName': 'Regular'})
    fb.setupOS2()
    fb.setupPost()
    fb.save(path)


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


if __name__ == '__main__':
    unittest.main()
