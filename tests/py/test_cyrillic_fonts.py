import os
import sys
import unittest

from helpers import REPO

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


if __name__ == '__main__':
    unittest.main()
