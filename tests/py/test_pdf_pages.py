# tests/py/test_pdf_pages.py
import os
import sys
import tempfile
import unittest

import pymupdf as fitz

from helpers import REPO

sys.path.insert(0, os.path.join(REPO, 'scripts'))
import pdf_pages  # noqa: E402


class PdfPagesTest(unittest.TestCase):
    def test_pages_text_and_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, 'brief.pdf')
            doc = fitz.open()
            for label in ('First page', 'Second page'):
                page = doc.new_page(width=300, height=200)
                page.insert_text((20, 40), label)
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 8, 8), False)
            pix.clear_with(200)
            doc[1].insert_image(fitz.Rect(20, 60, 100, 140), stream=pix.tobytes('png'))
            doc.save(pdf)
            out = os.path.join(tmp, 'pages')
            self.assertEqual(pdf_pages.extract(pdf, out, dpi=50, images=True), 2)
            self.assertTrue(os.path.exists(os.path.join(out, 'page-001.png')))
            with open(os.path.join(out, 'page-002.txt'), encoding='utf-8') as f:
                self.assertIn('Second page', f.read())
            self.assertTrue(any(n.startswith('page-002-img-') for n in os.listdir(out)))


if __name__ == '__main__':
    unittest.main()
