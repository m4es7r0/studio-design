import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.parse
from unittest import mock

from helpers import REPO, make_font

sys.path.insert(0, os.path.join(REPO, 'scripts'))
import cyrillic_fonts  # noqa: E402

META = ''')]}'
{"familyMetadataList": [
  {"family": "Zeta Sans", "category": "Sans Serif", "subsets": ["latin", "cyrillic"], "popularity": 30, "fonts": {"400": {}, "700": {}}},
  {"family": "Latin Only", "category": "Serif", "subsets": ["latin"], "popularity": 1, "fonts": {"400": {}}},
  {"family": "Alpha Serif", "category": "Serif", "subsets": ["cyrillic-ext", "cyrillic"], "popularity": 5, "fonts": {"300": {}, "300i": {}}},
  {"family": "Ext Only", "category": "Display", "subsets": ["cyrillic-ext"], "popularity": 2, "fonts": {"400": {}}}
]}'''

CSS = '''/* cyrillic */
@font-face {
  font-family: 'Zeta Sans';
  font-style: normal;
  font-weight: 400;
  src: url(https://fonts.gstatic.com/l/font?kit=abc&skey=def&v=v1) format('woff2');
}
@font-face {
  font-family: 'Zeta Sans';
  src: url('https://fonts.gstatic.com/s/zetasans/v1/second.woff2') format('woff2');
}
'''


class CyrillicFontsTest(unittest.TestCase):
    def test_metadata_prefix_is_stripped(self):
        self.assertEqual(len(cyrillic_fonts.parse_metadata(META)['familyMetadataList']), 4)
        self.assertEqual(cyrillic_fonts.parse_metadata('{"familyMetadataList": []}'), {'familyMetadataList': []})

    def test_cyrillic_filter_keeps_cyrillic_subsets_by_popularity(self):
        fams = cyrillic_fonts.cyrillic_families(cyrillic_fonts.parse_metadata(META))
        self.assertEqual([(f['family'], f['category']) for f in fams], [('Alpha Serif', 'Serif'), ('Zeta Sans', 'Sans Serif')])

    def test_font_urls_from_css(self):
        self.assertEqual(cyrillic_fonts.font_urls(CSS), [
            'https://fonts.gstatic.com/l/font?kit=abc&skey=def&v=v1',
            'https://fonts.gstatic.com/s/zetasans/v1/second.woff2',
        ])
        self.assertEqual(cyrillic_fonts.font_urls('/* nothing */'), [])

    def test_css_url_names_the_family_weight_and_text(self):
        fams = {f['family']: f for f in cyrillic_fonts.cyrillic_families(cyrillic_fonts.parse_metadata(META))}
        self.assertEqual(cyrillic_fonts.css_url(fams['Zeta Sans'], 'а ₽'),
                         'https://fonts.googleapis.com/css2?family=Zeta+Sans&text=%D0%B0%E2%80%AF%E2%82%BD')
        self.assertEqual(cyrillic_fonts.css_url(fams['Alpha Serif'], '1'),
                         'https://fonts.googleapis.com/css2?family=Alpha+Serif:wght@300&text=1')


class FakeNet:
    """Stands in for cyrillic_fonts.fetch: the metadata above, one CSS per family, fonts built here.
    Zeta Sans and Latin Only have every required character; Alpha Serif misses U+202F."""

    def __init__(self, tmp):
        full = list(cyrillic_fonts.font_check.REQUIRED)
        self.fonts = {}
        for name, cps in (('Zeta Sans', full), ('Latin Only', full), ('Alpha Serif', [cp for cp in full if cp != 0x202F])):
            path = os.path.join(tmp, name + '.ttf')
            make_font(path, cps)
            with open(path, 'rb') as f:
                self.fonts[name] = f.read()
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        if url == cyrillic_fonts.METADATA_URL:
            return META.encode('utf-8')
        if url.startswith(cyrillic_fonts.CSS_URL):
            family = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)['family'][0].split(':')[0]
            if family not in self.fonts:
                raise OSError('HTTP Error 400: Bad Request')
            return ("@font-face { src: url(https://fonts.test/%s.ttf) format('truetype'); }" % urllib.parse.quote(family)).encode()
        return self.fonts[urllib.parse.unquote(url.rsplit('/', 1)[1][:-4])]


class MainTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.net = FakeNet(self.tmp)
        self.default_out = os.path.join(self.tmp, 'fonts-cyrillic.md')
        for target, value in (('fetch', self.net), ('DEFAULT_OUT', self.default_out)):
            patcher = mock.patch.object(cyrillic_fonts, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = cyrillic_fonts.main(list(argv))
        return code, out.getvalue()

    def test_no_options_write_the_default_file(self):
        code, out = self.run_main()
        self.assertEqual(code, 0)
        with open(self.default_out, encoding='utf-8') as f:
            md = f.read()
        self.assertIn('## Pass (1)', md)
        self.assertIn('| Zeta Sans | Sans Serif |', md)
        self.assertIn('| Alpha Serif | Serif | U+202F narrow no-break space |', md)
        self.assertNotIn('Latin Only', md)
        self.assertNotIn('# Cyrillic Google Fonts', out)

    def test_limit_without_out_prints_to_stdout(self):
        code, out = self.run_main('--limit', '1')
        self.assertEqual(code, 0)
        self.assertIn('# Cyrillic Google Fonts', out)
        self.assertIn('| Alpha Serif |', out)
        self.assertNotIn('Zeta Sans', out)
        self.assertFalse(os.path.exists(self.default_out))

    def test_limit_with_out_writes_that_file(self):
        path = os.path.join(self.tmp, 'some.md')
        code, out = self.run_main('--limit', '2', '--out', path)
        self.assertEqual(code, 0)
        with open(path, encoding='utf-8') as f:
            self.assertIn('| Zeta Sans | Sans Serif |', f.read())
        self.assertNotIn('# Cyrillic Google Fonts', out)
        self.assertFalse(os.path.exists(self.default_out))

    def test_family_prints_check_lines_and_fails_on_a_miss(self):
        code, out = self.run_main('--family', 'Zeta Sans', '--family', 'Alpha Serif')
        self.assertEqual(code, 1)
        n = len(cyrillic_fonts.font_check.REQUIRED)
        self.assertEqual(out.splitlines(), [
            '✅ Zeta Sans: all %d required characters present' % n,
            '❌ Alpha Serif: 1 missing: U+202F narrow no-break space',
        ])
        self.assertTrue(any('family=Alpha+Serif:wght@300&' in u for u in self.net.urls), 'style from the catalogue')
        self.assertFalse(os.path.exists(self.default_out))

    def test_family_needs_no_cyrillic_subset(self):
        code, out = self.run_main('--family', 'Latin Only')
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith('✅ Latin Only: all '))

    def test_family_that_errors_is_not_checked_and_fails(self):
        code, out = self.run_main('--family', 'Nowhere Sans')
        self.assertEqual(code, 1)
        self.assertEqual(out.strip(), '❌ Nowhere Sans: not checked: OSError: HTTP Error 400: Bad Request')

    def figma_fixture(self):
        """A small capture: Zeta Sans in other letter case, Alpha Serif absent."""
        path = os.path.join(self.tmp, 'figma-font-families.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'captured': '2026-01-02', 'source': 'fixture',
                       'families': {'ZETA sans': ['Regular', 'Semi Bold'], 'Latin Only': ['Regular']}}, f)
        return path

    def test_no_figma_families_no_in_figma_column(self):
        self.run_main()
        with open(self.default_out, encoding='utf-8') as f:
            self.assertNotIn('In Figma', f.read())

    def test_figma_families_add_the_in_figma_column(self):
        fixture = self.figma_fixture()
        code, _ = self.run_main('--figma-families', fixture)
        self.assertEqual(code, 0)
        with open(self.default_out, encoding='utf-8') as f:
            md = f.read()
        self.assertIn('cyrillic_fonts.py --figma-families %s`' % fixture, md, 'refresh command keeps the option')
        self.assertIn('| Family | Category | In Figma |', md)
        self.assertIn('| Zeta Sans | Sans Serif | yes |', md)
        self.assertIn('| Family | Category | Missing | In Figma |', md)
        self.assertIn('| Alpha Serif | Serif | U+202F narrow no-break space | no |', md)
        self.assertIn('1 of the 1 passing families are in the Figma capture of 2026-01-02', md)
        method = md.split('## Method', 1)[1].split('## Pass', 1)[0]
        self.assertIn('captured 2026-01-02', method)
        self.assertIn('stays mandatory', method)

    def test_family_mode_appends_in_figma(self):
        code, out = self.run_main('--family', 'Zeta Sans', '--family', 'Alpha Serif', '--family', 'Nowhere Sans',
                                  '--figma-families', self.figma_fixture())
        self.assertEqual(code, 1)
        n = len(cyrillic_fonts.font_check.REQUIRED)
        self.assertEqual(out.splitlines(), [
            '✅ Zeta Sans: all %d required characters present · in Figma: yes' % n,
            '❌ Alpha Serif: 1 missing: U+202F narrow no-break space · in Figma: no',
            '❌ Nowhere Sans: not checked: OSError: HTTP Error 400: Bad Request · in Figma: no',
        ])

    def test_unreadable_figma_families_is_a_usage_error(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(err):
            cyrillic_fonts.main(['--figma-families', os.path.join(self.tmp, 'missing.json')])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn('--figma-families: cannot read', err.getvalue())
        self.assertEqual(self.net.urls, [], 'fails before any request')


if __name__ == '__main__':
    unittest.main()
