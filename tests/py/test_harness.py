import json
import os
import subprocess
import sys
import unittest

from helpers import make_client

DEMO = ("\nPREVIEWS['Demo'] = ('group=\"Demo\" height=120', 'grid-template-columns: 1fr;', '', "
        "\"  ReactDOM.createRoot(document.getElementById('root')).render(h('p', null, M.format.money(75000)));\")\n")


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


if __name__ == '__main__':
    unittest.main()
