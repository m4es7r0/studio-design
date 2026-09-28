import json
import os
import subprocess
import sys
import unittest

from helpers import make_client

DEMO = ("\nPREVIEWS['Demo'] = ('group=\"Demo\" height=120', 'grid-template-columns: 1fr;', '', "
        "\"  ReactDOM.createRoot(document.getElementById('root')).render(h('p', null, M.format.money(75000)));\")\n")

PAGES = ("\nPREVIEWS['Page'] = ('group=\"Layout budget\" page width=1440 height=720', '', '', '  page();')\n"
         "PREVIEWS['Card'] = ('group=\"Landing page\" height=120', '', '', '  card();')\n")

FONTS = ("\nFONT_LINKS = ['https://fonts.googleapis.com/css2?family=Onest:wght@400;700&display=block']\n"
         "FONT_LOADS = ['700 18px \"Onest\"']\n")


def generate(testcase, spec_extra):
    """Creates a client, appends spec_extra to its previews_spec.py, runs gen_previews.py; returns ds."""
    ds = os.path.join(make_client(testcase), 'design', 'ds')
    with open(os.path.join(ds, 'previews_spec.py'), 'a', encoding='utf-8') as f:
        f.write(spec_extra)
    return ds


def run_gen(ds):
    subprocess.run([sys.executable, os.path.join(ds, 'scripts', 'gen_previews.py')], check=True, stdout=subprocess.DEVNULL)


def read_preview(ds, name):
    with open(os.path.join(ds, 'project', 'components', name, 'preview.html'), encoding='utf-8') as f:
        return f.read()


class HarnessTest(unittest.TestCase):
    def test_previews_and_harness(self):
        ds = os.path.join(make_client(self), 'design', 'ds')
        with open(os.path.join(ds, 'previews_spec.py'), 'a', encoding='utf-8') as f:
            f.write(DEMO)
        with open(os.path.join(ds, 'upload', 'blobs.json'), 'w', encoding='utf-8') as f:
            json.dump({'abc123': 'city.jpg'}, f)
        subprocess.run([sys.executable, os.path.join(ds, 'scripts', 'gen_previews.py')], check=True, stdout=subprocess.DEVNULL)
        preview_path = os.path.join(ds, 'project', 'components', 'Demo', 'preview.html')
        with open(preview_path, encoding='utf-8') as f:
            preview = f.read()
        self.assertTrue(preview.startswith('<!-- @dsCard group="Demo" height=120 -->\n'))
        self.assertIn('var M = window.DemoClientUI', preview)
        with open(preview_path, 'a', encoding='utf-8') as f:
            f.write('<img src="/_blob/abc123">')
        subprocess.run([sys.executable, os.path.join(ds, 'scripts', 'build_harness.py')], check=True, stdout=subprocess.DEVNULL)
        with open(os.path.join(ds, 'harness', 'Demo.html'), encoding='utf-8') as f:
            page = f.read()
        self.assertNotIn('@dsCard', page)
        self.assertIn('<html lang="ru" data-theme="light">', page)
        self.assertIn('react.production.min.js', page)
        self.assertIn('../upload/city.jpg', page)
        with open(os.path.join(ds, 'harness', '_sweep.html'), encoding='utf-8') as f:
            self.assertIn('window.SWEEP_PAGES = ["Demo"]', f.read())
        with open(os.path.join(ds, 'harness', '_measure.html'), encoding='utf-8') as f:
            measure = f.read()
        self.assertIn('<pre id="result">measuring…</pre>', measure)
        self.assertIn('<script src="../scripts/measure.js"></script>', measure)
        with open(os.path.join(ds, 'harness', 'tokens.css'), encoding='utf-8') as f:
            self.assertIn(':root, [data-theme="light"]', f.read())

    def test_page_card_has_no_body_padding(self):
        ds = generate(self, PAGES)
        run_gen(ds)
        page, card = read_preview(ds, 'Page'), read_preview(ds, 'Card')
        self.assertIn('body { padding: 0; }', page)
        self.assertNotIn('padding: 24px 32px 32px 24px', page)
        self.assertIn('body { padding: 24px 32px 32px 24px; }', card)

    def test_font_links_and_fonts_ready(self):
        ds = generate(self, DEMO + FONTS)
        run_gen(ds)
        preview = read_preview(ds, 'Demo')
        self.assertIn('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@400;700&amp;display=block">', preview)
        self.assertIn('var FONT_LOADS = ["700 18px \\"Onest\\""];', preview)
        self.assertIn('window.fontsReady = Promise.all(FONT_LOADS.map(function (f) { return document.fonts.load(f); }))', preview)
        self.assertIn('window.fontsReady.then(function () {', preview)
        self.assertLess(preview.index('<link rel="stylesheet"'), preview.index('window.fontsReady = '))
        self.assertLess(preview.index('window.fontsReady = '), preview.index('M.format.money(75000)'))

    def test_no_fonts_resolves_at_once(self):
        ds = generate(self, DEMO)
        run_gen(ds)
        preview = read_preview(ds, 'Demo')
        self.assertIn('var FONT_LOADS = [];', preview)
        self.assertNotIn('<link rel="stylesheet"', preview)

    def test_fixtures_are_embedded(self):
        ds = generate(self, DEMO)
        with open(os.path.join(ds, 'fixtures', 'formatted.json'), 'w', encoding='utf-8') as f:
            json.dump({'examples': {'odd': {'name': '</script><b>', 'value': '1'}}}, f, ensure_ascii=False)
        run_gen(ds)
        preview = read_preview(ds, 'Demo')
        self.assertIn('<script>window.FIXTURES = {"copy": {', preview)
        self.assertIn('"button": "Основное действие"', preview)
        self.assertIn('"formatted": {"examples": {"odd": {"name": "<\\/script><b>"', preview)
        self.assertNotIn('</script><b>', preview)

    def test_missing_fixtures_embed_empty_objects(self):
        ds = generate(self, DEMO)
        os.remove(os.path.join(ds, 'fixtures', 'copy.json'))
        run_gen(ds)
        self.assertIn('<script>window.FIXTURES = {"copy": {}, "formatted": {}};</script>', read_preview(ds, 'Demo'))


if __name__ == '__main__':
    unittest.main()
