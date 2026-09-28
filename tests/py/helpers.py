# tests/py/helpers.py
import os
import subprocess
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def make_client(testcase, slug='demo-client'):
    """Creates a client container from the template in a temp folder; returns its path."""
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    env = dict(os.environ, CLIENTS_DIR=tmp.name)
    subprocess.run([os.path.join(REPO, 'scripts', 'new-client.sh'), slug, '--name', 'Demo Client', '--port', '5299'],
                   check=True, env=env, stdout=subprocess.DEVNULL)
    return os.path.join(tmp.name, slug)


def make_font(path, codepoints):
    """Writes a minimal TrueType font whose cmap holds exactly these code points."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
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
