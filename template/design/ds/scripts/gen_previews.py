"""Writes project/components/<Name>/preview.html from ds/previews_spec.py.
Usage: python3 ds/scripts/gen_previews.py [Name ...] [--ds DIR] [--lang ru]
Without names, writes every preview in the spec. A card with the `page` token gets no body padding.
Every preview links the spec's FONT_LINKS, waits for its FONT_LOADS (window.fontsReady) before
running its JS body, and embeds ds/fixtures/copy.json and formatted.json as window.FIXTURES."""
import argparse
import html
import importlib.util
import json
import os
import re
import sys

HEAD = '''<!-- @dsCard {card} -->
<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><title>{title}</title>
{links}<style>
  body {{ {body_padding} }}
  .grid {{ display: grid; gap: 24px 32px; align-items: start; {grid} }}
  .cell {{ display: grid; gap: 8px; justify-items: start; }}
  .cap {{ color: var(--muted); text-transform: uppercase; }}
{css}</style>
<script>
  var FONT_LOADS = {font_loads};
  window.fontsReady = Promise.all(FONT_LOADS.map(function (f) {{ return document.fonts.load(f); }}))
    .catch(function (e) {{ setTimeout(function () {{ throw e; }}); }});
</script>
<script>window.FIXTURES = {fixtures};</script>
</head>
<body>
<div id="root" class="{root_class}"></div>
<script>
  var M = window.{ns}, h = React.createElement;
  function cell(label, node) {{ return h('div', {{ className: 'cell', key: label }}, h('span', {{ className: 'cap' }}, label), node); }}
  window.fontsReady.then(function () {{
{js}
  }}).catch(function (e) {{ setTimeout(function () {{ throw e; }}); }});
</script>
</body>
</html>
'''


def load_spec(ds):
    spec = importlib.util.spec_from_file_location('previews_spec', os.path.join(ds, 'previews_spec.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def script_json(value):
    """JSON for an inline <script>: a «</» in a string cannot close the script."""
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def read_fixture(ds, name):
    path = os.path.join(ds, 'fixtures', name)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def is_page(card):
    """True when the @dsCard attributes carry the bare `page` token (quoted values do not count)."""
    return 'page' in re.sub(r'"[^"]*"', ' ', card).split()


def write_previews(ds, names=None, lang='ru'):
    mod = load_spec(ds)
    with open(os.path.join(ds, 'project', 'design-system.json'), encoding='utf-8') as f:
        ns = json.load(f)['namespace']
    links = ''.join('<link rel="stylesheet" href="%s">\n' % html.escape(url) for url in getattr(mod, 'FONT_LINKS', []))
    font_loads = script_json(list(getattr(mod, 'FONT_LOADS', [])))
    fixtures = script_json({'copy': read_fixture(ds, 'copy.json'), 'formatted': read_fixture(ds, 'formatted.json')})
    written = []
    for name in names or sorted(mod.PREVIEWS):
        card, grid, css, js = mod.PREVIEWS[name]
        folder = os.path.join(ds, 'project', 'components', name)
        os.makedirs(folder, exist_ok=True)
        page = HEAD.format(card=card, lang=lang, title=name + ' — preview', links=links,
                           body_padding='padding: 0;' if is_page(card) else 'padding: 24px 32px 32px 24px;',
                           grid=grid, css=css, font_loads=font_loads, fixtures=fixtures,
                           root_class=getattr(mod, 'ROOT_CLASS', ''), ns=ns, js=js)
        with open(os.path.join(folder, 'preview.html'), 'w', encoding='utf-8') as f:
            f.write(page)
        written.append(name)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('names', nargs='*')
    ap.add_argument('--ds', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--lang', default='ru')
    a = ap.parse_args(argv)
    for name in write_previews(a.ds, a.names or None, a.lang):
        print('preview', name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
