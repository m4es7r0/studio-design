"""Extracts a PDF brief into page images, page text and embedded images for TZ analysis.
Usage: scripts/py scripts/pdf_pages.py BRIEF.pdf OUT_DIR [--dpi 110] [--images]"""
import argparse
import os
import sys

import fitz


def extract(pdf, out, dpi=110, images=False):
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, 1):
        stem = os.path.join(out, 'page-%03d' % i)
        page.get_pixmap(dpi=dpi).save(stem + '.png')
        with open(stem + '.txt', 'w', encoding='utf-8') as f:
            f.write(page.get_text())
        if images:
            for k, info in enumerate(page.get_images(full=True), 1):
                pix = fitz.Pixmap(doc, info[0])
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save('%s-img-%d.png' % (stem, k))
    return len(doc)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('pdf')
    ap.add_argument('out')
    ap.add_argument('--dpi', type=int, default=110)
    ap.add_argument('--images', action='store_true')
    a = ap.parse_args(argv)
    n = extract(a.pdf, a.out, a.dpi, a.images)
    print('%d pages -> %s' % (n, a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
