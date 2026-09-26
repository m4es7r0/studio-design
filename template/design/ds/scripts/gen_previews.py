"""Writes project/components/<Name>/preview.html from ds/previews_spec.py.
Usage: python3 ds/scripts/gen_previews.py [Name ...] [--ds DIR] [--lang ru]
Without names, writes every preview in the spec."""
import argparse
import importlib.util
import json
import os
import sys

HEAD = '''<!-- @dsCard {card} -->
<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><title>{title}</title>
<style>
  body {{ padding: 24px 32px 32px 24px; }}
  .grid {{ display: grid; gap: 24px 32px; align-items: start; {grid} }}
  .cell {{ display: grid; gap: 8px; justify-items: start; }}
  .cap {{ color: var(--muted); text-transform: uppercase; }}
{css}</style>
</head>
<body>
<div id="root" class="{root_class}"></div>
<script>
  var M = window.{ns}, h = React.createElement;
  function cell(label, node) {{ return h('div', {{ className: 'cell', key: label }}, h('span', {{ className: 'cap' }}, label), node); }}
{js}
</script>
</body>
</html>
'''


def load_spec(ds):
    spec = importlib.util.spec_from_file_location('previews_spec', os.path.join(ds, 'previews_spec.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_previews(ds, names=None, lang='ru'):
    mod = load_spec(ds)
    with open(os.path.join(ds, 'project', 'design-system.json'), encoding='utf-8') as f:
        ns = json.load(f)['namespace']
    written = []
    for name in names or sorted(mod.PREVIEWS):
        card, grid, css, js = mod.PREVIEWS[name]
        folder = os.path.join(ds, 'project', 'components', name)
        os.makedirs(folder, exist_ok=True)
        html = HEAD.format(card=card, lang=lang, title=name + ' — preview', grid=grid, css=css,
                           root_class=getattr(mod, 'ROOT_CLASS', ''), ns=ns, js=js)
        with open(os.path.join(folder, 'preview.html'), 'w', encoding='utf-8') as f:
            f.write(html)
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
