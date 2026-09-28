"""Checks which Google Fonts families with a Cyrillic subset pass fonts/font_check.py; writes docs/fonts-cyrillic.md.
Usage: scripts/py scripts/cyrillic_fonts.py [--limit N] [--out PATH] [--figma-families PATH]
       scripts/py scripts/cyrillic_fonts.py --family NAME [--family NAME ...] [--figma-families PATH]
Needs the network (fonts.google.com, fonts.googleapis.com, fonts.gstatic.com). --limit checks the N most
popular Cyrillic families only and prints the list unless --out is given. A family whose request fails
is listed as «not checked» with the reason. --family checks just the named families, prints font_check's
✅/❌ lines and exits 1 when any fails or cannot be checked. --figma-families takes a capture of the Figma
MCP runtime's fonts (docs/figma-font-families.json) and marks each family «in Figma» yes or no, matched
on the family name without regard to letter case."""
import argparse
import concurrent.futures
import datetime
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'template', 'design', 'fonts'))
import font_check  # noqa: E402

METADATA_URL = 'https://fonts.google.com/metadata/fonts'
CSS_URL = 'https://fonts.googleapis.com/css2'
PREFIX = ")]}'"
# A modern browser User-Agent, so the CSS names woff2 files.
USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/126.0.0.0 Safari/537.36')
TIMEOUT = 30
WORKERS = 8
DEFAULT_OUT = os.path.join(REPO, 'docs', 'fonts-cyrillic.md')
FIGMA_OPTION = '--figma-families'


def parse_metadata(text):
    """The metadata JSON; strips the «)]}'» prefix Google may put in front of it."""
    text = text.lstrip()
    if text.startswith(PREFIX):
        text = text[len(PREFIX):]
    return json.loads(text)


def cyrillic_families(meta):
    """Families whose subsets include `cyrillic`, most popular first."""
    fams = [f for f in meta.get('familyMetadataList', []) if 'cyrillic' in (f.get('subsets') or [])]
    return sorted(fams, key=lambda f: (f.get('popularity') or 10 ** 9, f['family']))


def style_spec(family):
    """'' when the family has a regular 400; otherwise the first upright weight, or the first italic one."""
    keys = list(family.get('fonts') or {})
    if not keys or '400' in keys:
        return ''
    upright = sorted(int(k) for k in keys if k.isdigit())
    if upright:
        return ':wght@%d' % upright[0]
    italic = sorted(int(k[:-1]) for k in keys if k.endswith('i') and k[:-1].isdigit())
    if italic:
        return ':ital,wght@1,%d' % italic[0]
    raise ValueError('no style in the metadata')


def css_url(family, text):
    """The css2 URL for one style of the family, subset to `text`."""
    name = urllib.parse.quote(family['family']).replace('%20', '+')
    return '%s?family=%s%s&text=%s' % (CSS_URL, name, style_spec(family), urllib.parse.quote(text, safe=''))


def font_urls(css):
    """Every url(...) in the CSS, without quotes."""
    return [u.strip().strip('\'"') for u in re.findall(r'url\(([^)]+)\)', css)]


def required_text():
    return ''.join(chr(cp) for cp in sorted(font_check.REQUIRED))


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read()


def check_family(family, text):
    """{'family', 'category', 'status': pass | fail | not checked, 'missing': [(cp, name)], 'reason'}."""
    out = {'family': family['family'], 'category': family.get('category') or '—', 'missing': [], 'reason': ''}
    try:
        urls = font_urls(fetch(css_url(family, text)).decode('utf-8'))
        if not urls:
            raise ValueError('no font URL in the CSS')
        missing = None
        with tempfile.TemporaryDirectory() as tmp:
            for i, url in enumerate(urls):
                path = os.path.join(tmp, '%d.font' % i)
                with open(path, 'wb') as f:
                    f.write(fetch(url))
                miss = dict(font_check.missing(path))
                missing = miss if missing is None else {cp: n for cp, n in missing.items() if cp in miss}
        out['missing'] = sorted(missing.items())
        out['status'] = 'fail' if out['missing'] else 'pass'
    except Exception as e:  # a family that errors is reported, never fatal
        out['status'] = 'not checked'
        out['reason'] = ('%s: %s' % (type(e).__name__, e)).replace('|', '/')
    return out


def load_figma(path):
    """{'captured', 'path', 'refresh', 'names'} from a capture {"captured", "source", "families": {family: [styles]}}.
    `names` holds the family names in lower case; inside the repository `path` is relative to it and `refresh`
    starts with ~/job/studio-design/, elsewhere both are the path as given."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    full = os.path.abspath(path)
    inside = full.startswith(REPO + os.sep)
    rel = os.path.relpath(full, REPO) if inside else path
    return {'captured': str(data['captured']), 'path': rel, 'refresh': '~/job/studio-design/' + rel if inside else path,
            'names': {k.lower() for k in data['families']}}


def in_figma(figma, family):
    return 'yes' if family.lower() in figma['names'] else 'no'


def describe(missing):
    if len(missing) <= 3:
        return ', '.join('U+%04X %s' % m for m in missing)
    shown = ', '.join('U+%04X' % cp for cp, _ in missing[:8])
    return shown + (', … (%d in all)' % len(missing) if len(missing) > 8 else '')


def render(results, today, cyrillic_count, family_count, figma=None):
    by = lambda r: (r['category'], r['family'])  # noqa: E731
    passed = sorted((r for r in results if r['status'] == 'pass'), key=by)
    failed = sorted((r for r in results if r['status'] == 'fail'), key=by)
    skipped = sorted((r for r in results if r['status'] == 'not checked'), key=by)
    refresh = '~/job/studio-design/scripts/py ~/job/studio-design/scripts/cyrillic_fonts.py'
    lines = [
        '# Cyrillic Google Fonts that pass `font_check.py`',
        '',
        'Generated by `scripts/cyrillic_fonts.py` on %s: %d of the %d Google Fonts families with a' % (today, len(results), cyrillic_count),
        '`cyrillic` subset checked (%d families in the catalogue); %d pass, %d fail, %d not checked.' % (family_count, len(passed), len(failed), len(skipped)),
    ]
    if figma:
        lines.append('%d of the %d passing families are in the Figma capture of %s.'
                     % (sum(in_figma(figma, r['family']) == 'yes' for r in passed), len(passed), figma['captured']))
        refresh += ' %s %s' % (FIGMA_OPTION, figma['refresh'])
    lines += [
        'Refresh: `%s`.' % refresh,
        '',
        '## Method',
        '',
        '1. `%s` lists the families; those whose subsets include `cyrillic` are checked.' % METADATA_URL,
        '2. For each family, `%s?family=<Family>&text=<the characters of font_check.REQUIRED>`,' % CSS_URL,
        '   fetched with a modern browser User-Agent, names a woff2 subset that holds the requested characters',
        '   the face has. One style is checked: 400, or the first upright weight when there is no 400.',
        '3. The woff2 is downloaded and checked with `font_check.missing()` from',
        '   `template/design/fonts/font_check.py`, the same check as stage 4 (U+202F is required: `format`',
        '   prints it as the thousands separator).',
        '',
        'To check one face at stage 2 the same way:',
        '`~/job/studio-design/scripts/py ~/job/studio-design/scripts/cyrillic_fonts.py --family "<Family>"`.',
        'At stage 4 check the woff2 files of every weight you ship.',
        '',
        'Google\'s regular CSS (without `text=`) serves per-range woff2 files that drop U+202F even from',
        'faces that have it (a preview that links it draws U+202F in a fallback face). Stage 4 takes the',
        'files from the full family in the google/fonts repository (`stage-04-foundations.md` step 3).',
        '',
    ]
    if figma:
        lines += [
            '«In Figma» matches the family name, without regard to letter case, against `%s`,' % figma['path'],
            'captured %s from `figma.listAvailableFontsAsync()` in the Figma MCP runtime. The Figma list' % figma['captured'],
            'changes, so the per-face Figma check at stage 2 stays mandatory (`stage-02-direction.md`).',
            '',
        ]
    col = (lambda r: ' %s |' % in_figma(figma, r['family'])) if figma else (lambda r: '')  # noqa: E731
    head, rule = (' In Figma |', '---|') if figma else ('', '')
    lines += ['## Pass (%d)' % len(passed), '', '| Family | Category |' + head, '|---|---|' + rule]
    lines += ['| %s | %s |' % (r['family'], r['category']) + col(r) for r in passed]
    lines += ['', '## Fail (%d)' % len(failed), '', '| Family | Category | Missing |' + head, '|---|---|---|' + rule]
    lines += ['| %s | %s | %s |' % (r['family'], r['category'], describe(r['missing'])) + col(r) for r in failed]
    lines += ['', '## Not checked (%d)' % len(skipped), '', '| Family | Category | Reason |', '|---|---|---|']
    lines += ['| %s | %s | %s |' % (r['family'], r['category'], r['reason']) for r in skipped]
    return '\n'.join(lines) + '\n'


def check_named(meta, names, text, figma=None):
    """Checks the named families (catalogue entry by name when there is one) and prints font_check lines,
    each followed by «· in Figma: yes|no» when a Figma capture is given."""
    by_name = {f['family'].lower(): f for f in meta.get('familyMetadataList', [])}
    status = 0
    for name in names:
        r = check_family(by_name.get(name.lower(), {'family': name}), text)
        if r['status'] == 'pass':
            line = '✅ %s: all %d required characters present' % (r['family'], len(font_check.REQUIRED))
        elif r['status'] == 'fail':
            line = '❌ %s: %d missing: %s' % (r['family'], len(r['missing']), ', '.join('U+%04X %s' % m for m in r['missing']))
        else:
            line = '❌ %s: not checked: %s' % (r['family'], r['reason'])
        if r['status'] != 'pass':
            status = 1
        print(line + (' · in Figma: %s' % in_figma(figma, r['family']) if figma else ''))
    return status


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--limit', type=int, default=0, help='check only the N most popular Cyrillic families; prints unless --out is given')
    ap.add_argument('--out', help='where to write the list (default: docs/fonts-cyrillic.md; stdout with --limit)')
    ap.add_argument('--family', action='append', default=[], metavar='NAME',
                    help='check just this family (repeatable); prints ✅/❌ lines, exit 1 if any fails')
    ap.add_argument(FIGMA_OPTION, metavar='PATH',
                    help='capture of the Figma MCP runtime fonts (docs/figma-font-families.json); adds «In Figma»')
    a = ap.parse_args(argv)
    figma = None
    if a.figma_families:
        try:
            figma = load_figma(a.figma_families)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            ap.error('%s: cannot read %s: %s: %s' % (FIGMA_OPTION, a.figma_families, type(e).__name__, e))
    meta = parse_metadata(fetch(METADATA_URL).decode('utf-8'))
    text = required_text()
    if a.family:
        return check_named(meta, a.family, text, figma)
    fams = cyrillic_families(meta)
    todo = fams[:a.limit] if a.limit > 0 else fams
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        results = list(ex.map(lambda f: check_family(f, text), todo))
    md = render(results, datetime.date.today().isoformat(), len(fams), len(meta.get('familyMetadataList', [])), figma)
    out = a.out or (None if a.limit > 0 else DEFAULT_OUT)
    if out is None:
        sys.stdout.write(md)
    else:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(md)
    counts = {s: sum(r['status'] == s for r in results) for s in ('pass', 'fail', 'not checked')}
    in_fig = ''
    if figma:
        in_fig = ', %d of the passing in Figma' % sum(r['status'] == 'pass' and in_figma(figma, r['family']) == 'yes'
                                                     for r in results)
    print('checked %d of %d Cyrillic families: %d pass, %d fail, %d not checked%s -> %s'
          % (len(results), len(fams), counts['pass'], counts['fail'], counts['not checked'], in_fig, out or 'stdout'),
          file=sys.stderr)
    return 0

if __name__ == '__main__':
    sys.exit(main())
