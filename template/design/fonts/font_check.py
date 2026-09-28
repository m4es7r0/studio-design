"""Checks that fonts cover the characters the design system prints.
Usage: ~/job/studio-design/scripts/py fonts/font_check.py FONT [FONT ...] [--extra U+2192,U+2190]
Exit 1 when any font misses a required character."""
import argparse
import os
import sys

from fontTools.ttLib import TTFont

REQUIRED = {
    0x20BD: 'ruble sign ₽', 0x00A0: 'no-break space', 0x202F: 'narrow no-break space',
    0x2212: 'minus sign −', 0x2014: 'em dash —', 0x00AB: 'guillemet «', 0x00BB: 'guillemet »',
}
REQUIRED.update({cp: 'Cyrillic ' + chr(cp) for cp in list(range(0x0410, 0x0450)) + [0x0401, 0x0451]})
REQUIRED.update({cp: 'digit ' + chr(cp) for cp in range(0x30, 0x3A)})


def missing(path, extra=()):
    cmap = TTFont(path, lazy=True).getBestCmap() or {}
    need = dict(REQUIRED)
    need.update({cp: 'extra U+%04X' % cp for cp in extra})
    return [(cp, name) for cp, name in sorted(need.items()) if cp not in cmap]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('fonts', nargs='+')
    ap.add_argument('--extra', default='', help='comma-separated code points, e.g. U+2192,U+2190')
    a = ap.parse_args(argv)
    extra = [int(x.strip().upper().replace('U+', ''), 16) for x in a.extra.split(',') if x.strip()]
    status = 0
    for path in a.fonts:
        miss = missing(path, extra)
        if miss:
            status = 1
            print('❌ %s: %d missing: %s' % (os.path.basename(path), len(miss), ', '.join('U+%04X %s' % m for m in miss)))
        else:
            print('✅ %s: all %d required characters present' % (os.path.basename(path), len(REQUIRED) + len(extra)))
    return status


if __name__ == '__main__':
    sys.exit(main())
