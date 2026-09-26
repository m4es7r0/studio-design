"""Builds harness/<Name>.html for every component preview (real tokens, fonts, bundle and React)
and harness/_sweep.html for scripts/sweep.js.
Usage: python3 ds/scripts/build_harness.py [--ds DIR]"""
import argparse
import json
import os
import re
import sys

INJECT = ('<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="../project/components/bundle.css">'
          '<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"></script>'
          '<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"></script>'
          '<script>window.__errs=[];window.addEventListener("error",function(e){window.__errs.push(String(e.message))});</script>'
          '<script src="../project/components/bundle.js"></script>')

SWEEP_PAGE = '''<!doctype html>
<html><head><meta charset="utf-8"><title>Sweep</title></head>
<body><pre id="result">running…</pre>
<script>window.SWEEP_PAGES = __PAGES__;</script>
<script src="../scripts/sweep.js"></script>
</body></html>
'''


def token_css(t):
    fonts = t.get('type', {}).get('fonts', [])
    css = ["@font-face { font-family: '%s'; src: url('../project/%s') format('woff2'); font-weight: %s; font-display: block; }"
           % (f['family'], f['file'], f['weight']) for f in fonts]
    themes = t.get('color', {}).get('themes') or [{'id': 'default'}]
    theme = themes[0]['id']
    col = []
    for tok in t.get('color', {}).get('tokens', []):
        m = re.fullmatch(r'\{(.+)\}', str(tok['value']))
        col.append('--%s: %s;' % (tok['name'], 'var(--%s)' % m.group(1) if m else tok['value']))
    css.append(':root, [data-theme="%s"] { %s }' % (theme, ' '.join(col)))
    other = []
    for key, grp in t.items():
        if key in ('color', 'type') or not isinstance(grp, dict):
            continue
        other += ['--%s: %s;' % (tok['name'], tok['value']) for tok in grp.get('tokens', [])]
    other += ['--font-%s: %s;' % (k, v) for k, v in t.get('type', {}).get('families', {}).items()]
    css.append(':root { %s }' % ' '.join(other))
    return '\n'.join(css), theme


def build(ds):
    project = os.path.join(ds, 'project')
    out = os.path.join(ds, 'harness')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(project, 'tokens.json'), encoding='utf-8') as f:
        css, theme = token_css(json.load(f))
    with open(os.path.join(out, 'tokens.css'), 'w', encoding='utf-8') as f:
        f.write(css)
    blobs = {}
    blobs_file = os.path.join(ds, 'upload', 'blobs.json')
    if os.path.exists(blobs_file):
        with open(blobs_file, encoding='utf-8') as f:
            blobs = json.load(f)
    names = []
    comp = os.path.join(project, 'components')
    for name in sorted(os.listdir(comp)):
        src = os.path.join(comp, name, 'preview.html')
        if not os.path.isfile(src):
            continue
        with open(src, encoding='utf-8') as f:
            s = f.read()
        if s.startswith('<!-- @dsCard'):
            s = s.split('\n', 1)[1]
        s = re.sub(r'<html lang="([\w-]+)">', r'<html lang="\1" data-theme="%s">' % theme, s, count=1)
        s = s.replace('<head>', '<head>' + INJECT, 1)
        for blob, fname in blobs.items():
            s = s.replace('/_blob/' + blob, '../upload/' + fname)
        with open(os.path.join(out, name + '.html'), 'w', encoding='utf-8') as f:
            f.write(s)
        names.append(name)
    with open(os.path.join(out, '_sweep.html'), 'w', encoding='utf-8') as f:
        f.write(SWEEP_PAGE.replace('__PAGES__', json.dumps(names)))
    return names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--ds', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args(argv)
    print('harness: %d pages' % len(build(a.ds)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
