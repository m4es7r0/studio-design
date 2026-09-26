# Studio Design Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `studio-design` pipeline (orchestrator skill, stage references, agents, docs, client template, scripts) and finish the `grilling` fork, so a fresh session can take a client brief to a coded design system and a Figma library with the same checks every time.

**Architecture:** Two git repositories. `~/job/agent-skills` holds project-agnostic skills (the `grilling` fork). `~/job/studio-design` holds the pipeline: a skill with one reference file per stage, three agents, human docs, a `template/` copied into `~/job/clients/<slug>/` by `new-client.sh`, and committed check scripts (format tests, harness builder, sweep, font check, Figma prelude and audit) that replace code written ad hoc in the Mayor session.

**Tech Stack:** bash (macOS), Node 20+ (`node:test`), Python 3 with a studio venv (PyMuPDF, fontTools, brotli), React 18.3.1 UMD from cdnjs in the harness, Figma Plugin API through the Figma MCP `use_figma` tool, Claude Code skills and agents.

**Spec:** `docs/superpowers/specs/2026-09-26-studio-design-pipeline-design.md` (read it before any task).

## Global Constraints

- Paths: pipeline repo `~/job/studio-design`; skills repo `~/job/agent-skills`; client containers `~/job/clients/<slug>/`, the pipeline works in `<slug>/design/`.
- Names: skill `studio-design`; agents `tz-analyst`, `studio-design-reviewer`, `studio-design-figma-builder`; existing agent `design-scout` keeps its name.
- Every agent file sets `model: opus`.
- Files, code and comments are in English; everything a client reads is in the client's language (usually Russian).
- Commit messages: one short Title-Case line, no type prefix, no body, no trailing period.
- Push only when the user asks for it in the session.
- The studio repository holds no client material; tests never write to a client Figma file.
- Mutating `use_figma` calls run strictly one after another; read-only calls may run in parallel.
- Node 20 or newer. Python dependencies live in `~/job/studio-design/.venv` built from `requirements.txt` (`pymupdf`, `fonttools`, `brotli`); scripts that need them run through `scripts/py`.
- Template tokens, replaced by `new-client.sh`: `__CLIENT_SLUG__`, `__CLIENT_NAME__`, `__NAMESPACE__`, `__DATE__`, `__PORT__`.
- Client slug: `^[a-z][a-z0-9-]*$`; namespace = PascalCase of the slug + `UI` (`acme-shop` → `AcmeShopUI`).
- Test runner for the studio repo: `tests/run.sh` (bash tests `tests/test_*.sh`, `node --test tests/js/*.test.js`, `scripts/py -m unittest discover -s tests/py`).

---

## File structure

`~/job/agent-skills` (exists; Task 1 changes it):

```
validate.sh                     frontmatter and fork checks for every skill
tests/test_validate.sh          test of validate.sh
skills/grilling/SKILL.md        + caller options (output file, client questions, fact-finder)
skills/grilling/UPSTREAM.md     «Our changes» filled in
AGENTS.md                       push rule updated
```

`~/job/studio-design`:

```
README.md, AGENTS.md, CLAUDE.md, .gitignore, requirements.txt
docs/manifest.md, docs/playbook.md, docs/packages.md, docs/lessons.md
docs/profiles/{web-landing,web-product,mobile,game}.md
docs/rules/{design,numbers-and-locale,figma,artifact,client}.md
skills/studio-design/SKILL.md
skills/studio-design/references/stage-{00-intake,01-tz-analysis,02-direction,03-layout-budget,04-foundations,05-components,06-screens,07-figma,08-qa-handoff,09-revisions}.md
agents/{tz-analyst,studio-design-reviewer,studio-design-figma-builder}.md
scripts/{install.sh,validate.sh,setup-python.sh,py,new-client.sh,preflight.sh,pdf_pages.py}
template/CLIENT.md, template/.gitignore
template/design/{PROJECT.md,decisions.md,questions.md,progress.md,package.json}
template/design/{brief,refs,directions,revisions,handoff}/README.md
template/design/.claude/launch.json
template/design/ds/previews_spec.py
template/design/ds/project/{tokens.json,design-system.json,README.md}
template/design/ds/project/components/{bundle.js,bundle.css,index.d.ts}
template/design/ds/fixtures/{sample.json,format-cases.json}
template/design/ds/upload/blobs.json
template/design/ds/scripts/{load_bundle.js,check_format.js,format_fixtures.js,build_harness.py,gen_previews.py,sweep.js}
template/design/fonts/font_check.py
template/design/figma/{prelude.js,prelude.project.js,audit.js,figma-state.json}
tests/lib.sh, tests/run.sh
tests/test_{install,validate,new_client,preflight}.sh
tests/js/{helpers.js,format.test.js,sweep.test.js,prelude.test.js,audit.test.js}
tests/py/{helpers.py,test_pdf_pages.py,test_harness.py,test_font_check.py}
tests/pilot/brief.md
```

---

### Task 1: Finish the grilling fork and validate agent-skills

**Files:**
- Create: `~/job/agent-skills/validate.sh`, `~/job/agent-skills/tests/test_validate.sh`
- Modify: `~/job/agent-skills/skills/grilling/SKILL.md` (append a section), `~/job/agent-skills/skills/grilling/UPSTREAM.md` («Our changes»), `~/job/agent-skills/AGENTS.md` (push rule), `~/job/agent-skills/README.md` (mention validate.sh)

**Interfaces:**
- Produces: `validate.sh` (exit 0 when every skill passes; `SKILLS_ROOT` env overrides the folder); `grilling` caller options named «Output file», «Client questions», «Fact-finder» — Task 13 and Task 14 invoke `grilling` with them.

- [ ] **Step 1: Write the failing test** `tests/test_validate.sh`

```bash
#!/usr/bin/env bash
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; fails=0
check() { if [ "$1" = "$2" ]; then echo "  ok   $3"; else echo "  FAIL $3 (expected '$1', got '$2')"; fails=$((fails + 1)); fi; }
"$repo/validate.sh" >/dev/null; check 0 $? "real skills validate"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/good" "$tmp/wrong" "$tmp/fork"
printf -- '---\nname: good\ndescription: x\n---\nbody\n' > "$tmp/good/SKILL.md"
printf -- '---\nname: other\ndescription: x\n---\n' > "$tmp/wrong/SKILL.md"
printf -- '---\nname: fork\ndescription: x\n---\n' > "$tmp/fork/SKILL.md"; echo up > "$tmp/fork/UPSTREAM.md"
out="$(SKILLS_ROOT="$tmp" "$repo/validate.sh")"; check 1 $? "bad skills fail"
case "$out" in *"FAIL wrong: frontmatter name is 'other'"*) echo "  ok   names the bad skill";; *) echo "  FAIL message: $out"; fails=$((fails + 1));; esac
case "$out" in *"FAIL fork: fork without LICENSE"*) echo "  ok   fork needs LICENSE";; *) echo "  FAIL message: $out"; fails=$((fails + 1));; esac
case "$out" in *"ok   good"*) echo "  ok   good skill passes";; *) echo "  FAIL message: $out"; fails=$((fails + 1));; esac
[ "$fails" -eq 0 ] && echo "PASS test_validate" || { echo "FAIL test_validate: $fails"; exit 1; }
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash ~/job/agent-skills/tests/test_validate.sh`
Expected: FAIL (`validate.sh: No such file or directory`).

- [ ] **Step 3: Write `validate.sh`**

```bash
#!/usr/bin/env bash
# Validates every skill: SKILL.md frontmatter with name equal to the folder and a description;
# a fork (UPSTREAM.md present) also carries LICENSE. SKILLS_ROOT overrides the folder (tests).
set -uo pipefail
root="${SKILLS_ROOT:-$(cd "$(dirname "$0")" && pwd)/skills}"
status=0
for dir in "$root"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"; f="${dir}SKILL.md"; bad=0
  if [ ! -f "$f" ]; then echo "FAIL $name: no SKILL.md"; status=1; continue; fi
  if [ "$(head -1 "$f")" != "---" ]; then echo "FAIL $name: SKILL.md has no frontmatter"; status=1; continue; fi
  fm="$(awk 'NR==1{next} /^---$/{exit} {print}' "$f")"
  fname="$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p' | head -1)"
  [ "$fname" = "$name" ] || { echo "FAIL $name: frontmatter name is '$fname'"; bad=1; }
  printf '%s\n' "$fm" | grep -q '^description:' || { echo "FAIL $name: no description"; bad=1; }
  if [ -f "${dir}UPSTREAM.md" ] && [ ! -f "${dir}LICENSE" ]; then echo "FAIL $name: fork without LICENSE"; bad=1; fi
  if [ "$bad" -eq 0 ]; then echo "ok   $name"; else status=1; fi
done
exit "$status"
```

Run: `chmod +x ~/job/agent-skills/validate.sh ~/job/agent-skills/tests/test_validate.sh`

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash ~/job/agent-skills/tests/test_validate.sh`
Expected: `PASS test_validate`.

- [ ] **Step 5: Append the caller options to `skills/grilling/SKILL.md`** (after the last upstream paragraph, unchanged text above it)

```markdown

## Options a caller may pass

A pipeline or the user may pass these when invoking the skill. Without them the skill behaves
as above.

**Output file.** When the caller names an output file, write the settled tree there once the
frontier is empty and the user has confirmed the shared understanding. One entry per decision:
the question, the answer, who decided, the date. Append if the file exists; never rewrite
earlier entries.

**Client questions.** When the caller names a client-questions file, decisions the user says
only the client can make are not grilled further. Collect them there for a non-technical reader
in the client's language: grouped by topic, one plain question per item with our recommended
answer, so the client can reply «ок» or pick another option. No jargon, no rounds, no pressure.

**Fact-finder.** When the caller names an agent for facts (for example `tz-analyst`), send fact
lookups to that agent instead of a generic sub-agent, and pass it the source files the caller
named.
```

- [ ] **Step 6: Update `skills/grilling/UPSTREAM.md`** — replace the «## Our changes» section with:

```markdown
## Our changes

1. «Options a caller may pass» section: output file, client questions, fact-finder
   (spec `~/job/studio-design/docs/superpowers/specs/2026-09-26-studio-design-pipeline-design.md`, section 4.1).
```

- [ ] **Step 7: Update `AGENTS.md`** — replace the line `- Never push; the user pushes.` with `- Push only when the user asks for it in the session.`; in `README.md` add after the «Install» block:

```markdown
## Check

```bash
./validate.sh && bash tests/test_validate.sh
```
```

- [ ] **Step 8: Run the checks and commit**

Run: `cd ~/job/agent-skills && ./validate.sh && bash tests/test_validate.sh`
Expected: `ok   grilling` and `PASS test_validate`.

```bash
cd ~/job/agent-skills && git add -A && git commit -m "Add Caller Options To Grilling And Validation"
```

---

### Task 2: studio-design skeleton, test runner and install script

**Files:**
- Create: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `scripts/install.sh`, `tests/lib.sh`, `tests/run.sh`, `tests/test_install.sh` (all in `~/job/studio-design`)

**Interfaces:**
- Produces: `tests/lib.sh` helpers `pass`, `fail`, `assert_eq EXPECTED ACTUAL LABEL`, `assert_contains HAYSTACK NEEDLE LABEL`, `assert_link PATH TARGET`, `assert_file PATH`, `finish`, variable `REPO`; `scripts/install.sh` (env `CLAUDE_HOME`, default `~/.claude`; exit 1 when a destination exists and is not our link).

- [ ] **Step 1: Write `tests/lib.sh` and `tests/run.sh`**

```bash
# tests/lib.sh — tiny assertion helpers for bash tests. Source it; call finish at the end.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILS=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1"; FAILS=$((FAILS + 1)); }
assert_eq() { if [ "$1" = "$2" ]; then pass "$3"; else fail "$3 (expected '$1', got '$2')"; fi; }
assert_contains() { case "$1" in *"$2"*) pass "$3" ;; *) fail "$3 (missing '$2')" ;; esac; }
assert_link() { if [ -L "$1" ] && [ "$(readlink "$1")" = "$2" ]; then pass "link $1"; else fail "link $1 -> $2"; fi; }
assert_file() { if [ -f "$1" ]; then pass "file $1"; else fail "file $1"; fi; }
finish() { if [ "$FAILS" -eq 0 ]; then echo "PASS $(basename "$0")"; else echo "FAIL $(basename "$0"): $FAILS"; exit 1; fi; }
```

```bash
#!/usr/bin/env bash
# tests/run.sh — runs every test of the pipeline repository.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; status=0
for t in "$repo"/tests/test_*.sh; do [ -f "$t" ] || continue; bash "$t" || status=1; done
if ls "$repo"/tests/js/*.test.js >/dev/null 2>&1; then node --test "$repo"/tests/js/*.test.js || status=1; fi
if ls "$repo"/tests/py/test_*.py >/dev/null 2>&1; then "$repo/scripts/py" -m unittest discover -s "$repo/tests/py" || status=1; fi
if [ "$status" -eq 0 ]; then echo "ALL TESTS PASS"; else echo "TESTS FAILED"; fi
exit "$status"
```

- [ ] **Step 2: Write the failing test** `tests/test_install.sh`

```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
fake="$tmp/repo"; mkdir -p "$fake/scripts" "$fake/skills/demo" "$fake/agents"
cp "$REPO/scripts/install.sh" "$fake/scripts/"
printf -- '---\nname: demo\ndescription: x\n---\n' > "$fake/skills/demo/SKILL.md"
printf -- '---\nname: demo-agent\ndescription: x\nmodel: opus\n---\n' > "$fake/agents/demo-agent.md"
export CLAUDE_HOME="$tmp/home"
out="$("$fake/scripts/install.sh")"; assert_eq 0 $? "first install exits 0"
assert_link "$CLAUDE_HOME/skills/demo" "$fake/skills/demo"
assert_link "$CLAUDE_HOME/agents/demo-agent.md" "$fake/agents/demo-agent.md"
out="$("$fake/scripts/install.sh")"; assert_eq 0 $? "second install exits 0"
assert_contains "$out" "ok       $CLAUDE_HOME/skills/demo" "second run keeps the link"
rm "$CLAUDE_HOME/skills/demo"; mkdir "$CLAUDE_HOME/skills/demo"
out="$("$fake/scripts/install.sh")"; assert_eq 1 $? "a foreign folder blocks the install"
assert_contains "$out" "skipped  $CLAUDE_HOME/skills/demo" "reports the conflict"
finish
```

- [ ] **Step 3: Run it to verify it fails**

Run: `bash ~/job/studio-design/tests/test_install.sh`
Expected: FAIL (`cp: .../scripts/install.sh: No such file or directory`).

- [ ] **Step 4: Write `scripts/install.sh`**

```bash
#!/usr/bin/env bash
# Links skills/* and agents/*.md into $CLAUDE_HOME (default ~/.claude). Idempotent; never overwrites.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
home="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$home/skills" "$home/agents"
status=0
link() {
  if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then echo "ok       $2"
  elif [ -e "$2" ] || [ -L "$2" ]; then echo "skipped  $2 exists and is not a link to this repository"; status=1
  else ln -s "$1" "$2"; echo "linked   $2"; fi
}
for d in "$repo"/skills/*/; do [ -d "$d" ] || continue; link "${d%/}" "$home/skills/$(basename "$d")"; done
for f in "$repo"/agents/*.md; do [ -f "$f" ] || continue; link "$f" "$home/agents/$(basename "$f")"; done
exit "$status"
```

Run: `chmod +x ~/job/studio-design/scripts/install.sh ~/job/studio-design/tests/run.sh`

- [ ] **Step 5: Run the test to verify it passes**

Run: `bash ~/job/studio-design/tests/test_install.sh`
Expected: `PASS test_install.sh`.

- [ ] **Step 6: Write the repository files**

`.gitignore`:

```
.venv/
__pycache__/
node_modules/
.DS_Store
```

`CLAUDE.md`:

```markdown
# CLAUDE.md

@AGENTS.md
```

`AGENTS.md`:

```markdown
# Rules for agents maintaining the studio-design pipeline

This repository is the pipeline itself, not client work. Client work happens in
`~/job/clients/<slug>/design/` through the `studio-design` skill.

- Read `docs/superpowers/specs/` and `docs/superpowers/plans/` before changing the pipeline.
- Keep one responsibility per file: stage behaviour in `skills/studio-design/references/`,
  hard rules in `docs/rules/`, tool facts in `docs/manifest.md`, pitfalls in `docs/lessons.md`.
- A lesson learned in a client project goes to `docs/lessons.md`, and when it changes behaviour,
  also to the rule or stage reference it affects.
- No client material in this repository: no briefs, references, fonts or screenshots of a client.
- Checks are scripts with tests. Run `tests/run.sh` and `scripts/validate.sh` before every commit.
- Files are in English. Commit messages: one short Title-Case line, no prefix, no body.
- Push only when the user asks for it in the session.
```

`README.md`:

```markdown
# studio-design

A repeatable pipeline from a client brief (TZ) to a coded design system (Claude Design artifact)
and a Figma library. Spec: `docs/superpowers/specs/2026-09-26-studio-design-pipeline-design.md`.

## Start a client

1. `scripts/setup-python.sh` (once per machine) and `scripts/install.sh` (after every pull).
2. `scripts/preflight.sh` — fix every ❌ it prints.
3. `scripts/new-client.sh <slug> --name "Client name"` — creates `~/job/clients/<slug>/`.
4. Put the client's brief files into `~/job/clients/<slug>/design/brief/`.
5. Open `~/job/clients/<slug>/design` in the Claude Code desktop app (Code tab) and say
   «studio-design: stage 0».

The pipeline end to end: `docs/playbook.md`. Tools and skills: `docs/manifest.md`.

## Check the pipeline

```bash
tests/run.sh && scripts/validate.sh
```
```

- [ ] **Step 7: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Pipeline Skeleton And Install Script"
```

---

### Task 3: Studio Python and PDF extraction

**Files:**
- Create: `requirements.txt`, `scripts/setup-python.sh`, `scripts/py`, `scripts/pdf_pages.py`, `tests/py/helpers.py`, `tests/py/test_pdf_pages.py`

**Interfaces:**
- Produces: `scripts/py ARGS…` (runs `$STUDIO_PY` or `.venv/bin/python`; exit 3 with a fix message when missing); `pdf_pages.extract(pdf, out, dpi=110, images=False) -> int` writing `page-NNN.png`, `page-NNN.txt`, `page-NNN-img-K.png`; `tests/py/helpers.py` with `REPO` and `make_client(testcase, slug='demo-client') -> str` (used from Task 6 on).

- [ ] **Step 1: Write `requirements.txt`, `scripts/setup-python.sh`, `scripts/py`**

```
pymupdf>=1.24.3
fonttools>=4.50
brotli>=1.1
```

```bash
#!/usr/bin/env bash
# Builds the studio venv (.venv) with the pipeline's Python dependencies.
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m venv "$repo/.venv"
"$repo/.venv/bin/pip" install --quiet --upgrade pip
"$repo/.venv/bin/pip" install --quiet -r "$repo/requirements.txt"
"$repo/.venv/bin/python" -c "import pymupdf, fontTools, brotli; print('studio python ready')"
```

```bash
#!/usr/bin/env bash
# Runs the studio Python (.venv) with the pipeline's dependencies. STUDIO_PY overrides it.
repo="$(cd "$(dirname "$0")/.." && pwd)"
py="${STUDIO_PY:-$repo/.venv/bin/python}"
[ -x "$py" ] || { echo "No studio Python at $py. Run $repo/scripts/setup-python.sh" >&2; exit 3; }
exec "$py" "$@"
```

Run: `cd ~/job/studio-design && chmod +x scripts/setup-python.sh scripts/py && scripts/setup-python.sh`
Expected: `studio python ready`.

- [ ] **Step 2: Write the failing test** `tests/py/test_pdf_pages.py` and `tests/py/helpers.py`

```python
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
```

```python
# tests/py/test_pdf_pages.py
import os
import sys
import tempfile
import unittest

import pymupdf as fitz

from helpers import REPO

sys.path.insert(0, os.path.join(REPO, 'scripts'))
import pdf_pages  # noqa: E402


class PdfPagesTest(unittest.TestCase):
    def test_pages_text_and_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, 'brief.pdf')
            doc = fitz.open()
            for label in ('First page', 'Second page'):
                page = doc.new_page(width=300, height=200)
                page.insert_text((20, 40), label)
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 8, 8), False)
            pix.clear_with(200)
            doc[1].insert_image(fitz.Rect(20, 60, 100, 140), stream=pix.tobytes('png'))
            doc.save(pdf)
            out = os.path.join(tmp, 'pages')
            self.assertEqual(pdf_pages.extract(pdf, out, dpi=50, images=True), 2)
            self.assertTrue(os.path.exists(os.path.join(out, 'page-001.png')))
            with open(os.path.join(out, 'page-002.txt'), encoding='utf-8') as f:
                self.assertIn('Second page', f.read())
            self.assertTrue(any(n.startswith('page-002-img-') for n in os.listdir(out)))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Run it to verify it fails**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_pdf_pages.py'`
Expected: FAIL `ModuleNotFoundError: No module named 'pdf_pages'`.

- [ ] **Step 4: Write `scripts/pdf_pages.py`**

```python
"""Extracts a PDF brief into page images, page text and embedded images for TZ analysis.
Usage: scripts/py scripts/pdf_pages.py BRIEF.pdf OUT_DIR [--dpi 110] [--images]"""
import argparse
import os
import sys

import pymupdf as fitz


def extract(pdf, out, dpi=110, images=False):
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, 1):
        stem = os.path.join(out, 'page-%03d' % i)
        page.get_pixmap(dpi=dpi).save(stem + '.png')
        with open(stem + '.txt', 'w', encoding='utf-8') as f:
            f.write(page.get_text())
        if images:
            for k, info in enumerate(page.get_images(full=True), 1):
                pix = fitz.Pixmap(doc, info[0])
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save('%s-img-%d.png' % (stem, k))
    return len(doc)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('pdf')
    ap.add_argument('out')
    ap.add_argument('--dpi', type=int, default=110)
    ap.add_argument('--images', action='store_true')
    a = ap.parse_args(argv)
    n = extract(a.pdf, a.out, a.dpi, a.images)
    print('%d pages -> %s' % (n, a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_pdf_pages.py'`
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Studio Python And PDF Extraction"
```

---

### Task 4: Client template skeleton and new-client.sh

**Files:**
- Create: `template/CLIENT.md`, `template/.gitignore`, `template/design/{PROJECT.md,decisions.md,questions.md,progress.md,package.json}`, `template/design/{brief,refs,directions,revisions,handoff}/README.md`, `template/design/.claude/launch.json`, `scripts/new-client.sh`, `tests/test_new_client.sh`

**Interfaces:**
- Consumes: `tests/lib.sh` (Task 2).
- Produces: `scripts/new-client.sh <slug> [--name NAME] [--port N]` (env `CLIENTS_DIR`, default `~/job/clients`; exit 1 when the client exists, exit 2 on bad arguments); the container layout of spec section 4.3.

- [ ] **Step 1: Write the failing test** `tests/test_new_client.sh`

```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export CLIENTS_DIR="$tmp"
out="$("$REPO/scripts/new-client.sh" acme-shop --name "Акме Шоп" --port 5301)"; assert_eq 0 $? "creates a client"
c="$tmp/acme-shop"
assert_file "$c/CLIENT.md"
assert_file "$c/design/PROJECT.md"
assert_file "$c/design/brief/README.md"
assert_contains "$(cat "$c/CLIENT.md")" "# Акме Шоп" "client name substituted"
assert_contains "$(cat "$c/design/PROJECT.md")" "AcmeShopUI" "namespace derived from the slug"
assert_contains "$(cat "$c/design/.claude/launch.json")" '"port": 5301 }' "port substituted"
left="$(grep -rIE '__(CLIENT_SLUG|CLIENT_NAME|NAMESPACE|DATE|PORT)__' "$c" || true)"
assert_eq "" "$left" "no template tokens left"
assert_eq 1 "$(git -C "$c" rev-list --count HEAD)" "one initial commit"
"$REPO/scripts/new-client.sh" acme-shop >/dev/null 2>&1; assert_eq 1 $? "refuses an existing client"
"$REPO/scripts/new-client.sh" 9lives >/dev/null 2>&1; assert_eq 2 $? "rejects a slug that starts with a digit"
finish
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash ~/job/studio-design/tests/test_new_client.sh`
Expected: FAIL (`new-client.sh: No such file or directory`).

- [ ] **Step 3: Write `scripts/new-client.sh`**

```bash
#!/usr/bin/env bash
# Creates a client container from template/.
# Usage: new-client.sh <slug> [--name "Client name"] [--port N]
# CLIENTS_DIR overrides the parent folder (default ~/job/clients).
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
clients="${CLIENTS_DIR:-$HOME/job/clients}"
usage() { echo "usage: new-client.sh <slug: a-z first, then a-z 0-9 -> [--name \"Client name\"] [--port N]" >&2; exit 2; }
[ $# -ge 1 ] || usage
slug="$1"; shift
[[ "$slug" =~ ^[a-z][a-z0-9-]*$ ]] || usage
name="$slug"; port=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name) [ $# -ge 2 ] || usage; name="$2"; shift 2 ;;
    --port) [ $# -ge 2 ] || usage; port="$2"; shift 2 ;;
    *) usage ;;
  esac
done
dst="$clients/$slug"
if [ -e "$dst" ]; then echo "refusing: $dst already exists" >&2; exit 1; fi
if [ -z "$port" ]; then
  port=5190
  while lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1 || grep -Fqs "\"port\": $port }" "$clients"/*/design/.claude/launch.json; do
    port=$((port + 1))
  done
fi
ns="$(printf '%s' "$slug" | awk -F- '{ for (i = 1; i <= NF; i++) printf "%s%s", toupper(substr($i, 1, 1)), substr($i, 2) }')UI"
mkdir -p "$clients"
cp -R "$repo/template" "$dst"
export SLUG="$slug" NAME="$name" NS="$ns" TODAY="$(date +%Y-%m-%d)" PORT="$port"
{ grep -rlIE '__(CLIENT_SLUG|CLIENT_NAME|NAMESPACE|DATE|PORT)__' "$dst" || true; } | while IFS= read -r f; do
  perl -pi -e 's/__CLIENT_SLUG__/$ENV{SLUG}/g; s/__CLIENT_NAME__/$ENV{NAME}/g; s/__NAMESPACE__/$ENV{NS}/g; s/__DATE__/$ENV{TODAY}/g; s/__PORT__/$ENV{PORT}/g' "$f"
done
git -C "$dst" init -q -b main
git -C "$dst" add -A
git -C "$dst" commit -q -m "Start Client $slug"
cat <<EOF
Created $dst
  namespace  $ns
  port       $port
Next: put the brief into $dst/design/brief/, open $dst/design in Claude Code (desktop app, Code tab)
and say «studio-design: stage 0».
EOF
```

Run: `chmod +x ~/job/studio-design/scripts/new-client.sh`

- [ ] **Step 4: Write the template files**

`template/CLIENT.md`:

```markdown
# __CLIENT_NAME__

- Slug: `__CLIENT_SLUG__`
- Started: __DATE__
- Contact:
- Client language: Russian

## Contract

- Package: ДС | ДС + экраны
- Revision rounds included:
- Deadlines:

## Links and access

| What | URL | Who has access |
|---|---|---|
| Design system artifact | | |
| Figma file | | |
```

`template/.gitignore`:

```
design/ds/harness/
node_modules/
__pycache__/
.DS_Store
```

`template/design/PROJECT.md`:

```markdown
# __CLIENT_NAME__ · design

- Package: see `../CLIENT.md`
- Entry mode: from scratch | brand book | redesign | existing DS
- Platform profile(s): web-landing | web-product | mobile | game
- Target sizes:
- Namespace: `__NAMESPACE__`
- Harness port: __PORT__ (`.claude/launch.json`, serves `ds/`)
- Current stage: 0 · Intake

## Links

- Artifact:
- Figma file:
```

`template/design/decisions.md`:

```markdown
# Decisions

Every decision of the client or the user, newest last. Never rewrite an entry; add a new one.

| Date | Source | Decision |
|---|---|---|
```

`template/design/questions.md`:

```markdown
# Questions to the client

## Open

## Answered
```

`template/design/progress.md`:

```markdown
# Progress

One entry per stage: date, what was done, the gate evidence (command output, screenshot paths).

## Preflight

## Stage log
```

`template/design/package.json`:

```json
{
  "name": "__CLIENT_SLUG__-design",
  "private": true,
  "scripts": {
    "check:types": "tsc --noEmit --strict --jsx react-jsx --moduleResolution bundler --module esnext --target es2020 --types react ds/project/components/index.d.ts",
    "check:format": "node ds/scripts/check_format.js",
    "fixtures": "node ds/scripts/format_fixtures.js"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "typescript": "^5.6.0"
  }
}
```

`template/design/.claude/launch.json`:

```json
{
  "version": "0.0.1",
  "configurations": [
    { "name": "ds-harness", "runtimeExecutable": "python3", "runtimeArgs": ["-m", "http.server", "__PORT__", "--bind", "127.0.0.1", "--directory", "ds"], "port": __PORT__ }
  ]
}
```

Folder READMEs (one line each):
- `template/design/brief/README.md`: `The client's original brief files, tz-analysis.md (stage 1) and layout-budget.md (stage 3).`
- `template/design/refs/README.md`: `References and images extracted from the brief (stage 1–2). Client material; never copied to the studio repository.`
- `template/design/directions/README.md`: `Direction drafts from stage 2; rejected directions stay here as an archive.`
- `template/design/revisions/README.md`: `One folder per revision round: round-NN/source/ (the client's list as received) and round-NN.md (stage 9).`
- `template/design/handoff/README.md`: `The client handoff (stage 8), in the client's language.`

- [ ] **Step 5: Run the test to verify it passes**

Run: `bash ~/job/studio-design/tests/test_new_client.sh`
Expected: `PASS test_new_client.sh`.

- [ ] **Step 6: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Client Template And New Client Script"
```

---

### Task 5: Design-system scaffold, number format and fixtures

**Files:**
- Create: `template/design/ds/project/{tokens.json,design-system.json,README.md}`, `template/design/ds/project/components/{bundle.js,bundle.css,index.d.ts}`, `template/design/ds/fixtures/{sample.json,format-cases.json}`, `template/design/ds/upload/blobs.json`, `template/design/ds/scripts/{load_bundle.js,check_format.js,format_fixtures.js}`, `tests/js/helpers.js`, `tests/js/format.test.js`

**Interfaces:**
- Consumes: `scripts/new-client.sh` (Task 4).
- Produces: `window[<namespace>].format` with `group, money(v, {scale}), people, percent, coef, area, count(v, unit), pp, delta(v, type, unit), value(v, type, unit)`; `load_bundle.loadNamespace(dsDir) -> object`; `ds/fixtures/formatted.json` shape `{ <set>: { <id>: { name, value, delta } } }` (read by Figma scripts, Task 16); `tests/js/helpers.js` exports `REPO`, `makeClient(slug = 'demo-client') -> string`.

- [ ] **Step 1: Write the failing test** `tests/js/helpers.js` and `tests/js/format.test.js`

```js
// tests/js/helpers.js
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const REPO = path.resolve(__dirname, '../..');

function makeClient(slug = 'demo-client') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'studio-'));
  execFileSync(path.join(REPO, 'scripts/new-client.sh'), [slug, '--name', 'Demo Client', '--port', '5299'], {
    env: { ...process.env, CLIENTS_DIR: dir },
    stdio: 'pipe',
  });
  return path.join(dir, slug);
}

module.exports = { REPO, makeClient };
```

```js
// tests/js/format.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { makeClient } = require('./helpers');

test('template number rules pass their 25 cases', () => {
  const c = makeClient();
  const r = spawnSync('node', [path.join(c, 'design/ds/scripts/check_format.js')], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /all 25 cases pass/);
});

test('fixtures render through the format functions', () => {
  const c = makeClient();
  execFileSync('node', [path.join(c, 'design/ds/scripts/format_fixtures.js')]);
  const out = JSON.parse(fs.readFileSync(path.join(c, 'design/ds/fixtures/formatted.json'), 'utf8'));
  assert.deepEqual(out.examples.revenue, { name: 'Выручка', value: '462 млрд ₽', delta: '−18 млрд ₽' });
  assert.equal(out.examples.users.value, '1 250 000 чел.');
  assert.equal(out.examples.users.delta, '+41 000 чел.');
  assert.equal(out.examples.conversion.value, '4,5 %');
  assert.equal(out.examples.conversion.delta, '+0,7 п.п.');
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && node --test tests/js/format.test.js`
Expected: FAIL (`check_format.js` not found).

- [ ] **Step 3: Write the bundle scaffold** `template/design/ds/project/components/bundle.js`

```js
/* @ds-bundle: {"format":4,"namespace":"__NAMESPACE__","components":[]} */
(function () {
  'use strict';

  function assign(target) {
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (src) for (var k in src) if (Object.prototype.hasOwnProperty.call(src, k)) target[k] = src[k];
    }
    return target;
  }

  /* ---------------- number formatting, ru-RU (README «Numbers») ---------------- */
  var NNBSP = ' ', NBSP = ' ', MINUS = '−';
  var SCALES = [[1e12, 'трлн'], [1e9, 'млрд'], [1e6, 'млн']];

  function group(n) {
    return String(Math.round(Math.abs(n))).replace(/\B(?=(\d{3})+(?!\d))/g, NNBSP);
  }
  function comma(x, digits) { return x.toFixed(digits).replace('.', ','); }
  function signOf(v) { return v < 0 ? MINUS : ''; }
  function scaled(a, scaleName) {
    var idx = -1, i;
    if (scaleName) { for (i = 0; i < SCALES.length; i++) if (SCALES[i][1] === scaleName) idx = i; }
    else { for (i = 0; i < SCALES.length; i++) if (a >= SCALES[i][0]) { idx = i; break; } }
    if (idx < 0) return null;
    var x = a / SCALES[idx][0];
    var d = x >= 100 ? 0 : x >= 10 ? 1 : 2;
    var r = Math.round(x * Math.pow(10, d)) / Math.pow(10, d);
    if (!scaleName && r >= 1000 && idx > 0) { idx -= 1; r = Math.round(a / SCALES[idx][0] * 100) / 100; d = 2; }
    var txt = comma(r, d);
    if (!scaleName) txt = txt.replace(/(,\d*?)0+$/, '$1').replace(/,$/, '');
    return txt + NBSP + SCALES[idx][1];
  }
  var format = {
    group: group,
    /** 75 000 ₽ · 1,23 млрд ₽ · 12,3 трлн ₽. opts.scale forces 'млн' | 'млрд' | 'трлн' so a pair reads in one unit. */
    money: function (v, opts) {
      var a = Math.abs(v), s = opts && opts.scale;
      var body = (s || a >= 1e6) ? scaled(a, s) : group(a);
      return signOf(v) + body + NBSP + '₽';
    },
    people: function (v) { return signOf(v) + group(v) + NBSP + 'чел.'; },
    percent: function (v) {
      var a = Math.abs(v);
      var body = (a < 10 && a % 1 !== 0) ? comma(a, 1) : group(a);
      return signOf(v) + body + NBSP + '%';
    },
    coef: function (v) { return signOf(v) + comma(Math.abs(v), 2); },
    area: function (v) {
      var a = Math.abs(v);
      return signOf(v) + (a >= 1e6 ? scaled(a) : group(a)) + NBSP + 'кв.' + NBSP + 'м';
    },
    count: function (v, unit) { return signOf(v) + group(v) + NBSP + (unit || 'ед.'); },
    pp: function (v) {
      var a = Math.abs(v);
      var body = a % 1 !== 0 ? comma(a, 1) : String(a);
      return (v > 0 ? '+' : v < 0 ? MINUS : '') + body + NBSP + 'п.п.';
    },
    /** A signed delta. type: money | people | percent (→ п.п.) | coef | area | count | pp. */
    delta: function (v, type, unit) {
      if (v === null || v === undefined) return '—';
      if (v === 0) return '0';
      if (type === 'percent' || type === 'pp') return format.pp(v);
      var plus = v > 0 ? '+' : '';
      var f = format[type] || format.count;
      return plus + f(v, unit);
    },
    value: function (v, type, unit) {
      if (v === null || v === undefined) return '—';
      var f = format[type] || format.count;
      return f(v, unit);
    }
  };

  var api = { format: format };
  window.__NAMESPACE__ = assign(window.__NAMESPACE__ || {}, api);
})();
```

`template/design/ds/project/components/bundle.css`:

```css
/* Component styles. Stage 4 sets the root class and the base rules; each component adds its block. */
```

`template/design/ds/project/components/index.d.ts`:

```ts
import type * as React from 'react';

export type FormatType = 'money' | 'people' | 'percent' | 'coef' | 'area' | 'count' | 'pp';
export interface Format {
  group(v: number): string;
  money(v: number, opts?: { scale?: 'млн' | 'млрд' | 'трлн' }): string;
  people(v: number): string;
  percent(v: number): string;
  coef(v: number): string;
  area(v: number): string;
  count(v: number, unit?: string): string;
  pp(v: number): string;
  delta(v: number | null | undefined, type: FormatType, unit?: string): string;
  value(v: number | null | undefined, type: FormatType, unit?: string): string;
}
export declare const format: Format;
export type ReactNode = React.ReactNode;

declare global { interface Window { __NAMESPACE__: { format: Format } } }
```

- [ ] **Step 4: Write the DS project files**

`template/design/ds/project/tokens.json`:

```json
{
  "name": "__CLIENT_NAME__ UI Kit",
  "version": 1,
  "color": { "themes": [{ "id": "light", "name": "Light" }], "tokens": [] },
  "type": { "fonts": [], "families": {}, "groups": [] },
  "spacing": { "tokens": [] },
  "radius": { "tokens": [] }
}
```

`template/design/ds/project/design-system.json` (local skeleton; stage 4 merges it with the file the artifact type creates):

```json
{
  "v": 3,
  "layout": "files",
  "title": "__CLIENT_NAME__ UI Kit",
  "namespace": "__NAMESPACE__",
  "libraries": [{ "name": "react", "version": "18" }, { "name": "react-dom", "version": "18" }],
  "sections": {},
  "groups": [],
  "assetGroups": {},
  "blobs": {},
  "docs": { "readme": "project/README.md", "sections": [] }
}
```

`template/design/ds/project/README.md`:

```markdown
# __CLIENT_NAME__ UI Kit

Namespace `__NAMESPACE__`. Principles, colour roles and component rules are written at stage 4.

## Numbers

Every number on screen goes through `__NAMESPACE__.format`; nobody types a formatted value.

- Thousands: narrow no-break space U+202F (`75 000`). Decimal comma (`4,5`).
- Minus: U+2212 (`−350`). Deltas are always signed; a zero delta is `0`, no data is `—`.
- Units and scale words follow the number after a no-break space U+00A0 (`120 млн ₽`, `450 000 кв. м`).
- Money from 1 млн: млн / млрд / трлн with three significant digits, trailing zeros dropped
  (`1,2 млрд ₽`), except a forced-scale pair that must read in one unit (`0,85 млрд` / `1,20 млрд`).
- Percent below 10 keeps one decimal (`4,5 %`); percentage deltas are in п.п. (`+0,7 п.п.`).
```

`template/design/ds/upload/blobs.json`: `{}`

`template/design/ds/fixtures/sample.json`:

```json
{
  "examples": [
    { "id": "revenue", "name": "Выручка", "type": "money", "value": 462000000000, "delta": -18000000000 },
    { "id": "users", "name": "Пользователи", "type": "count", "unit": "чел.", "value": 1250000, "delta": 41000 },
    { "id": "conversion", "name": "Конверсия", "type": "percent", "value": 4.5, "delta": 0.7 }
  ]
}
```

`template/design/ds/fixtures/format-cases.json` (`⍽` stands for U+202F, `·` for U+00A0):

```json
[
  { "fn": "money", "args": [75000], "want": "75⍽000·₽" },
  { "fn": "money", "args": [120000000], "want": "120·млн·₽" },
  { "fn": "money", "args": [60000000], "want": "60·млн·₽" },
  { "fn": "money", "args": [1200000000], "want": "1,2·млрд·₽" },
  { "fn": "money", "args": [1234000000], "want": "1,23·млрд·₽" },
  { "fn": "money", "args": [12300000000], "want": "12,3·млрд·₽" },
  { "fn": "money", "args": [100000000000000], "want": "100·трлн·₽" },
  { "fn": "money", "args": [999600000], "want": "1·млрд·₽" },
  { "fn": "money", "args": [-350000000], "want": "−350·млн·₽" },
  { "fn": "money", "args": [850000000, { "scale": "млрд" }], "want": "0,85·млрд·₽" },
  { "fn": "money", "args": [1200000000, { "scale": "млрд" }], "want": "1,20·млрд·₽" },
  { "fn": "people", "args": [5685000], "want": "5⍽685⍽000·чел." },
  { "fn": "percent", "args": [40], "want": "40·%" },
  { "fn": "percent", "args": [4.5], "want": "4,5·%" },
  { "fn": "percent", "args": [0], "want": "0·%" },
  { "fn": "coef", "args": [1.35], "want": "1,35" },
  { "fn": "area", "args": [450000], "want": "450⍽000·кв.·м" },
  { "fn": "area", "args": [9800000], "want": "9,8·млн·кв.·м" },
  { "fn": "count", "args": [458000, "биз."], "want": "458⍽000·биз." },
  { "fn": "pp", "args": [5], "want": "+5·п.п." },
  { "fn": "pp", "args": [-3], "want": "−3·п.п." },
  { "fn": "delta", "args": [0.7, "percent"], "want": "+0,7·п.п." },
  { "fn": "delta", "args": [-12000, "people"], "want": "−12⍽000·чел." },
  { "fn": "delta", "args": [null, "money"], "want": "—" },
  { "fn": "delta", "args": [0, "money"], "want": "0" }
]
```

- [ ] **Step 5: Write the scripts**

`template/design/ds/scripts/load_bundle.js`:

```js
// Loads the design-system bundle in Node with a stub window and returns the namespace object.
const fs = require('node:fs');
const path = require('node:path');

function loadNamespace(dsDir) {
  const ds = JSON.parse(fs.readFileSync(path.join(dsDir, 'project/design-system.json'), 'utf8'));
  const noop = () => {};
  global.window = global.window || {
    React: { createElement: noop, useState: () => [undefined, noop], useRef: () => ({}), useEffect: noop, useCallback: (f) => f, useMemo: (f) => f() },
  };
  const file = path.join(dsDir, 'project/components/bundle.js');
  delete require.cache[require.resolve(file)];
  require(file);
  const api = global.window[ds.namespace];
  if (!api || !api.format) throw new Error(`bundle did not register ${ds.namespace}.format`);
  return api;
}

module.exports = { loadNamespace };
```

`template/design/ds/scripts/check_format.js`:

```js
// Checks <namespace>.format against ds/fixtures/format-cases.json. Run: node ds/scripts/check_format.js
const fs = require('node:fs');
const path = require('node:path');
const { loadNamespace } = require('./load_bundle');

const ds = path.resolve(__dirname, '..');
const f = loadNamespace(ds).format;
const show = (x) => x.replace(/ /g, '⍽').replace(/ /g, '·');
const cases = JSON.parse(fs.readFileSync(path.join(ds, 'fixtures/format-cases.json'), 'utf8'));
let failed = 0;
for (const c of cases) {
  const got = show(f[c.fn](...c.args));
  if (got !== c.want) { failed++; console.log('FAIL', c.fn, JSON.stringify(c.args), got, 'want', c.want); }
}
console.log(failed ? `${failed} of ${cases.length} failed` : `all ${cases.length} cases pass`);
process.exit(failed ? 1 : 0);
```

`template/design/ds/scripts/format_fixtures.js`:

```js
// Renders ds/fixtures/sample.json through <namespace>.format into ds/fixtures/formatted.json.
// sample.json: { "<set>": [{ "id", "name", "type", "value", "delta"?, "unit"? }] }
const fs = require('node:fs');
const path = require('node:path');
const { loadNamespace } = require('./load_bundle');

const ds = path.resolve(__dirname, '..');
const f = loadNamespace(ds).format;
const sample = JSON.parse(fs.readFileSync(path.join(ds, 'fixtures/sample.json'), 'utf8'));
const out = {};
let n = 0;
for (const [set, items] of Object.entries(sample)) {
  out[set] = {};
  for (const it of items) {
    out[set][it.id] = {
      name: it.name,
      value: f.value(it.value, it.type, it.unit),
      delta: it.delta === undefined ? null : f.delta(it.delta, it.type, it.unit),
    };
    n++;
  }
}
fs.writeFileSync(path.join(ds, 'fixtures/formatted.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`formatted ${n} items into fixtures/formatted.json`);
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd ~/job/studio-design && node --test tests/js/format.test.js && bash tests/test_new_client.sh`
Expected: `# pass 2`, `# fail 0`; `PASS test_new_client.sh`.

- [ ] **Step 7: Check the types once in a real container** (needs network for `npm install`)

```bash
d="$(mktemp -d)" && CLIENTS_DIR="$d" ~/job/studio-design/scripts/new-client.sh types-check --port 5298 >/dev/null \
  && cd "$d/types-check/design" && npm install --no-audit --no-fund --silent && npm run check:types && echo TYPES_OK; rm -rf "$d"
```

Expected: `TYPES_OK`.

- [ ] **Step 8: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Design System Scaffold And Number Format"
```

---

### Task 6: Preview generator and harness builder

**Files:**
- Create: `template/design/ds/previews_spec.py`, `template/design/ds/scripts/gen_previews.py`, `template/design/ds/scripts/build_harness.py`, `tests/py/test_harness.py`

**Interfaces:**
- Consumes: `tests/py/helpers.make_client` (Task 3), the DS scaffold (Task 5).
- Produces: `gen_previews.write_previews(ds, names=None, lang='ru') -> list[str]`; `build_harness.build(ds) -> list[str]`; `harness/<Name>.html`, `harness/tokens.css`, `harness/_sweep.html` (sets `window.SWEEP_PAGES` and loads `../scripts/sweep.js`, Task 7); `ds/upload/blobs.json` maps an artifact blob id to a file in `ds/upload/`.

- [ ] **Step 1: Write the failing test** `tests/py/test_harness.py`

```python
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
        with open(os.path.join(ds, 'harness', 'tokens.css'), encoding='utf-8') as f:
            self.assertIn(':root, [data-theme="light"]', f.read())


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_harness.py'`
Expected: FAIL (`gen_previews.py` not found, `CalledProcessError`).

- [ ] **Step 3: Write `template/design/ds/previews_spec.py`**

```python
"""Preview specs for scripts/gen_previews.py.

PREVIEWS maps a component name to (dsCard attributes, grid CSS, extra CSS, JS body).
The JS body runs with M (the namespace object), h (React.createElement) and cell(label, node),
and renders into #root, for example:
  ReactDOM.createRoot(document.getElementById('root')).render(h('div', { className: 'grid' }, ...));
ROOT_CLASS is the design system's root class, set at stage 4."""
ROOT_CLASS = ''
PREVIEWS = {}
```

- [ ] **Step 4: Write `template/design/ds/scripts/gen_previews.py`**

```python
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
```

- [ ] **Step 5: Write `template/design/ds/scripts/build_harness.py`**

```python
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
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_harness.py'`
Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Preview Generator And Harness Builder"
```

---

### Task 7: Sweep script

**Files:**
- Create: `template/design/ds/scripts/sweep.js`, `tests/js/sweep.test.js`

**Interfaces:**
- Consumes: `harness/_sweep.html` from Task 6 (`window.SWEEP_PAGES`, `#result`).
- Produces: in the browser, `#result` text whose first line is `SWEEP OK: N pages, 0 errors, 0 overflows, 0 empty` or `SWEEP FAIL: …`, then JSON of the failing pages; in Node, `require(sweep.js)` exports `{ isRealOverflow(m), TOL }` where `m = { scrollWidth, clientWidth, textOverflow, overflowX, display, ignored, absoluteOnly }`.

- [ ] **Step 1: Write the failing test** `tests/js/sweep.test.js`

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { isRealOverflow, TOL } = require(path.join(REPO, 'template/design/ds/scripts/sweep.js'));

const base = { scrollWidth: 120, clientWidth: 100, textOverflow: 'clip', overflowX: 'visible', display: 'block' };

test('overflow within the tolerance is not real', () => {
  assert.equal(isRealOverflow({ ...base, scrollWidth: 100 + TOL }), false);
});

test('overflow past the tolerance is real', () => {
  assert.equal(isRealOverflow(base), true);
});

test('ellipsis, scroll containers, inline boxes, ignored and absolute-only overhangs are not real', () => {
  for (const extra of [{ textOverflow: 'ellipsis' }, { overflowX: 'auto' }, { overflowX: 'scroll' }, { display: 'inline' }, { ignored: true }, { absoluteOnly: true }]) {
    assert.equal(isRealOverflow({ ...base, ...extra }), false, JSON.stringify(extra));
  }
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && node --test tests/js/sweep.test.js`
Expected: FAIL (`Cannot find module .../sweep.js`).

- [ ] **Step 3: Write `template/design/ds/scripts/sweep.js`**

```js
/* Sweep: loads every harness page in a 1920 px iframe and reports JS errors, real overflows and
   empty roots. Open harness/_sweep.html and read #result; its first line is «SWEEP OK: …» or
   «SWEEP FAIL: …». Wrap an intentional overhang in [data-sweep-ignore]. */
(function () {
  var TOL = 4;

  function isRealOverflow(m) {
    if (m.ignored || m.absoluteOnly) return false;
    if (!(m.scrollWidth > m.clientWidth + TOL)) return false;
    if (m.textOverflow === 'ellipsis') return false;
    if (m.overflowX === 'auto' || m.overflowX === 'scroll') return false;
    if (m.display === 'inline') return false;
    return true;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { isRealOverflow: isRealOverflow, TOL: TOL };
    return;
  }

  function absoluteOnly(e, w) {
    var right = e.getBoundingClientRect().right + TOL, any = false;
    for (var k = 0; k < e.children.length; k++) {
      if (e.children[k].getBoundingClientRect().right > right) {
        any = true;
        var pos = w.getComputedStyle(e.children[k]).position;
        if (pos !== 'absolute' && pos !== 'fixed') return false;
      }
    }
    return any;
  }

  function label(e) {
    var c = typeof e.className === 'string' && e.className ? e.className.split(' ')[0] : e.tagName.toLowerCase();
    return c + ': ' + (e.textContent || '').trim().slice(0, 40) + ' (' + (e.scrollWidth - e.clientWidth) + 'px)';
  }

  function checkPage(name) {
    return new Promise(function (resolve) {
      var f = document.createElement('iframe');
      f.style.cssText = 'position:fixed;left:0;top:0;width:1920px;height:1200px;opacity:0;pointer-events:none';
      var done = false;
      function finish() {
        if (done) return;
        done = true;
        setTimeout(function () {
          var r = { page: name, errors: [], overflows: [], empty: false };
          try {
            var d = f.contentDocument, w = f.contentWindow;
            r.errors = (w.__errs || []).slice();
            var root = d.getElementById('root');
            r.empty = !!root && root.children.length === 0;
            var els = d.querySelectorAll('body *');
            for (var i = 0; i < els.length; i++) {
              var e = els[i], cs = w.getComputedStyle(e);
              var m = { scrollWidth: e.scrollWidth, clientWidth: e.clientWidth, textOverflow: cs.textOverflow, overflowX: cs.overflowX, display: cs.display, ignored: !!e.closest('[data-sweep-ignore]'), absoluteOnly: false };
              if (isRealOverflow(m)) {
                m.absoluteOnly = absoluteOnly(e, w);
                if (isRealOverflow(m)) r.overflows.push(label(e));
              }
            }
          } catch (err) {
            r.errors.push('sweep: ' + err.message);
          }
          f.remove();
          resolve(r);
        }, 700);
      }
      f.onload = finish;
      setTimeout(finish, 6000);
      f.src = name + '.html?sweep=' + Date.now();
      document.body.appendChild(f);
    });
  }

  async function run() {
    var pages = window.SWEEP_PAGES || [], results = [];
    for (var i = 0; i < pages.length; i++) results.push(await checkPage(pages[i]));
    var bad = results.filter(function (r) { return r.errors.length || r.overflows.length || r.empty; });
    var errs = results.reduce(function (a, r) { return a + r.errors.length; }, 0);
    var over = results.reduce(function (a, r) { return a + r.overflows.length; }, 0);
    var empty = results.filter(function (r) { return r.empty; }).length;
    var head = (bad.length ? 'SWEEP FAIL: ' : 'SWEEP OK: ') + pages.length + ' pages, ' + errs + ' errors, ' + over + ' overflows, ' + empty + ' empty';
    document.getElementById('result').textContent = head + '\n' + JSON.stringify(bad, null, 2);
    document.title = head;
  }

  run();
})();
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ~/job/studio-design && node --test tests/js/sweep.test.js`
Expected: `# pass 3`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Harness Sweep"
```

---

### Task 8: Font coverage check

**Files:**
- Create: `template/design/fonts/font_check.py`, `tests/py/test_font_check.py`

**Interfaces:**
- Produces: `font_check.REQUIRED: dict[int, str]`; `font_check.missing(path, extra=()) -> list[tuple[int, str]]` sorted by code point; `font_check.main(argv) -> int` (0 all present, 1 missing). Run through the studio Python: `~/job/studio-design/scripts/py fonts/font_check.py FONT… [--extra U+2192,…]`.

- [ ] **Step 1: Write the failing test** `tests/py/test_font_check.py`

```python
import os
import sys
import tempfile
import unittest

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from helpers import REPO

sys.path.insert(0, os.path.join(REPO, 'template', 'design', 'fonts'))
import font_check  # noqa: E402


def make_font(path, codepoints):
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


class FontCheckTest(unittest.TestCase):
    def test_reports_missing_ruble_and_narrow_space(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'partial.ttf')
            make_font(path, [cp for cp in font_check.REQUIRED if cp not in (0x20BD, 0x202F)])
            self.assertEqual([cp for cp, _ in font_check.missing(path)], [0x202F, 0x20BD])
            self.assertEqual(font_check.main([path]), 1)

    def test_full_font_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'full.ttf')
            make_font(path, list(font_check.REQUIRED))
            self.assertEqual(font_check.missing(path), [])
            self.assertEqual(font_check.main([path]), 0)

    def test_extra_code_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'full.ttf')
            make_font(path, list(font_check.REQUIRED))
            self.assertEqual(font_check.missing(path, extra=[0x2192]), [(0x2192, 'extra U+2192')])
            self.assertEqual(font_check.main([path, '--extra', 'U+2192']), 1)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_font_check.py'`
Expected: FAIL `ModuleNotFoundError: No module named 'font_check'`.

- [ ] **Step 3: Write `template/design/fonts/font_check.py`**

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ~/job/studio-design && scripts/py -m unittest discover -s tests/py -p 'test_font_check.py'`
Expected: `OK` (3 tests).

- [ ] **Step 5: Check it on a real font** (the Mayor woff2 is a known-good sample)

Run: `~/job/studio-design/scripts/py ~/job/studio-design/template/design/fonts/font_check.py ~/job/mayor-sim-design/ds/project/fonts/PixelCodeMayor-Regular.woff2`
Expected: `✅ PixelCodeMayor-Regular.woff2: all 83 required characters present` (7 signs + 66 Cyrillic + 10 digits). If it prints ❌ instead, record the missing code points in the task report; do not change the Mayor font.

- [ ] **Step 6: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Font Coverage Check"
```

---

### Task 9: Figma prelude by name

**Files:**
- Create: `template/design/figma/prelude.js`, `template/design/figma/prelude.project.js`, `template/design/figma/figma-state.json`, `tests/js/prelude.test.js`

**Interfaces:**
- Produces: pasting `prelude.js` before task code defines `PRELUDE_CONFIG` and `P` with `P.variable(name)`, `P.resolve(variable)`, `P.paint(name) -> Paint[]` (bound, resolved colour), `P.textStyle(name)`, `P.effectStyle(name)`, `P.txt(chars, style, colour, name?) -> TextNode`, `P.doc(page, title, body, width = 1000) -> FrameNode`. Unknown names throw `No variable named …` / `No text style named …` / `No effect style named …`. `figma-state.json` shape (read by the figma-builder agent):

```json
{ "fileKey": "", "fileUrl": "", "pages": {}, "components": {}, "screens": {}, "decisions": [], "completedSteps": [], "open": [] }
```

- [ ] **Step 1: Write the failing test** `tests/js/prelude.test.js`

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { REPO } = require('./helpers');

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const src = fs.readFileSync(path.join(REPO, 'template/design/figma/prelude.js'), 'utf8');
const load = (figma) => new AsyncFunction('figma', src + '\nreturn P;')(figma);

function fakeFigma() {
  const vars = [
    { id: 'V:1', name: 'primitive/ink', valuesByMode: { m: { r: 0.1, g: 0.1, b: 0.2, a: 1 } } },
    { id: 'V:2', name: 'text/ink', valuesByMode: { m: { type: 'VARIABLE_ALIAS', id: 'V:1' } } },
  ];
  const loaded = [];
  const figma = {
    variables: {
      getLocalVariablesAsync: async () => vars,
      getVariableByIdAsync: async (id) => vars.find((v) => v.id === id),
      setBoundVariableForPaint: (p, field, v) => ({ ...p, boundVariables: { [field]: { type: 'VARIABLE_ALIAS', id: v.id } } }),
    },
    getLocalTextStylesAsync: async () => [{ id: 'S:1', name: 'Text/body', fontName: { family: 'Inter', style: 'Regular' } }],
    getLocalEffectStylesAsync: async () => [{ id: 'E:1', name: 'shadow/m' }],
    loadFontAsync: async (f) => { loaded.push(f.family + ' ' + f.style); },
    createText: () => ({ async setTextStyleIdAsync(id) { this.textStyleId = id; } }),
  };
  return { figma, loaded };
}

test('paint resolves an alias chain and binds the named variable', async () => {
  const P = await load(fakeFigma().figma);
  const [p] = await P.paint('text/ink');
  assert.deepEqual(p.color, { r: 0.1, g: 0.1, b: 0.2 });
  assert.equal(p.boundVariables.color.id, 'V:2');
});

test('unknown names fail loudly', async () => {
  const P = await load(fakeFigma().figma);
  await assert.rejects(P.paint('text/missing'), /No variable named text\/missing/);
  assert.throws(() => P.textStyle('Nope'), /No text style named Nope/);
  assert.throws(() => P.effectStyle('shadow/xl'), /No effect style named shadow\/xl/);
});

test('txt applies style, colour and name; text style fonts are loaded up front', async () => {
  const { figma, loaded } = fakeFigma();
  const P = await load(figma);
  const t = await P.txt('Привет', 'Text/body', 'text/ink', 'label');
  assert.equal(t.textStyleId, 'S:1');
  assert.equal(t.characters, 'Привет');
  assert.equal(t.name, 'label');
  assert.equal(t.fills[0].boundVariables.color.id, 'V:2');
  assert.deepEqual(loaded, ['Inter Regular']);
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && node --test tests/js/prelude.test.js`
Expected: FAIL (`ENOENT … prelude.js`).

- [ ] **Step 3: Write `template/design/figma/prelude.js`**

```js
// Shared prelude for use_figma scripts in a studio-design project. Paste it before the task code.
// It finds variables and styles by name, so it carries no IDs. Naming conventions (stage 7):
// colour variables «<group>/<token>» (e.g. «text/ink»), text styles «<Group>/<name>»,
// effect styles «shadow/<size>». Components are passed by ID from design/figma/figma-state.json.
const PRELUDE_CONFIG = { titleStyle: 'Display/title', bodyStyle: 'Text/body', titleColor: 'text/ink', bodyColor: 'text/ink-2' };
const P = await (async () => {
  const vars = await figma.variables.getLocalVariablesAsync();
  const byName = new Map(vars.map((v) => [v.name, v]));
  const colours = {};
  async function resolve(v) {
    let val = Object.values(v.valuesByMode)[0];
    while (val && val.type === 'VARIABLE_ALIAS') {
      const a = await figma.variables.getVariableByIdAsync(val.id);
      val = Object.values(a.valuesByMode)[0];
    }
    return val;
  }
  function variable(name) {
    const v = byName.get(name);
    if (!v) throw new Error('No variable named ' + name);
    return v;
  }
  async function paint(name) {
    const v = variable(name);
    if (!colours[name]) { const c = await resolve(v); colours[name] = { r: c.r, g: c.g, b: c.b }; }
    return [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: colours[name] }, 'color', v)];
  }
  const textStyles = await figma.getLocalTextStylesAsync();
  const effectStyles = await figma.getLocalEffectStylesAsync();
  const fonts = new Map(textStyles.map((s) => [s.fontName.family + '|' + s.fontName.style, s.fontName]));
  await Promise.all([...fonts.values()].map((f) => figma.loadFontAsync(f)));
  function textStyle(name) {
    const s = textStyles.find((x) => x.name === name);
    if (!s) throw new Error('No text style named ' + name);
    return s;
  }
  function effectStyle(name) {
    const s = effectStyles.find((x) => x.name === name);
    if (!s) throw new Error('No effect style named ' + name);
    return s;
  }
  async function txt(chars, style, colour, name) {
    const t = figma.createText();
    await t.setTextStyleIdAsync(textStyle(style).id);
    t.characters = chars;
    t.fills = await paint(colour);
    if (name) t.name = name;
    return t;
  }
  async function doc(page, title, body, width = 1000) {
    const d = figma.createAutoLayout('VERTICAL', { name: 'Doc', itemSpacing: 12 });
    d.fills = [];
    page.appendChild(d);
    d.appendChild(await txt(title, PRELUDE_CONFIG.titleStyle, PRELUDE_CONFIG.titleColor));
    const b = await txt(body, PRELUDE_CONFIG.bodyStyle, PRELUDE_CONFIG.bodyColor);
    d.appendChild(b);
    b.layoutSizingHorizontal = 'FIXED';
    b.resize(width, b.height);
    b.textAutoResize = 'HEIGHT';
    return d;
  }
  return { variable, resolve, paint, textStyle, effectStyle, txt, doc };
})();
```

`template/design/figma/prelude.project.js`:

```js
// Project-specific use_figma helpers, pasted after prelude.js. Style-bound helpers live here, for
// example the stretched pixel frame of Mayor Sim (~/job/mayor-sim-design/figma/prelude.js, frame()).
```

`template/design/figma/figma-state.json`:

```json
{
  "fileKey": "",
  "fileUrl": "",
  "pages": {},
  "components": {},
  "screens": {},
  "decisions": [],
  "completedSteps": [],
  "open": []
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ~/job/studio-design && node --test tests/js/prelude.test.js`
Expected: `# pass 3`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Figma Prelude By Name"
```

---

### Task 10: Figma audit

**Files:**
- Create: `template/design/figma/audit.js`, `tests/js/audit.test.js`

**Interfaces:**
- Produces: in `use_figma`, pasting `audit.js` then `return await auditPage('<pageId>');` returns `{ page, ok, counts, samples }` with keys `unboundPaints, unstyledText, defaultNames, overlappingVariants, refMismatch, unusedProps, clippedText`; in Node, `require(audit.js)` exports `{ auditNodes(roots, mixed), DEFAULT_NAME }`.

- [ ] **Step 1: Write the failing test** `tests/js/audit.test.js`

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { REPO } = require('./helpers');
const { auditNodes } = require(path.join(REPO, 'template/design/figma/audit.js'));

const MIXED = Symbol('mixed');
let seq = 0;
function n(type, name, props = {}, children) {
  const node = { id: 'N' + ++seq, type, name, ...props };
  if (children) { node.children = children; for (const c of children) c.parent = node; }
  return node;
}
const SOLID = (bound) => ({ type: 'SOLID', visible: true, color: { r: 0, g: 0, b: 0 }, ...(bound ? { boundVariables: { color: { id: 'V:1' } } } : {}) });
const empty = (r) => Object.entries(r).filter(([, v]) => v.length).map(([k]) => k);
function variant(name, x, refs) {
  return n('COMPONENT', name, { x, y: 0, width: 100, height: 40 }, [n('TEXT', 'value', { textStyleId: 'S:1', componentPropertyReferences: refs })]);
}

test('a clean page has no findings', () => {
  const page = n('PAGE', 'Clean', {}, [n('FRAME', 'Card', { fills: [SOLID(true)] }, [n('TEXT', 'title', { textStyleId: 'S:1', fills: [SOLID(true)] })])]);
  assert.deepEqual(empty(auditNodes(page.children, MIXED)), []);
});

test('unbound paints, unstyled text and default names are found outside instances only', () => {
  const inst = n('INSTANCE', 'Button', {}, [n('RECTANGLE', 'Rectangle 3', { fills: [SOLID(false)] })]);
  const page = n('PAGE', 'P', {}, [n('FRAME', 'Frame 12', { fills: [SOLID(false)] }, [n('TEXT', 'label', { textStyleId: '' }), n('TEXT', 'mixed', { textStyleId: MIXED }), inst])]);
  const r = auditNodes(page.children, MIXED);
  assert.equal(r.unboundPaints.length, 1);
  assert.equal(r.unstyledText.length, 2);
  assert.deepEqual(r.defaultNames.map((s) => s.split(' ').slice(1).join(' ')), ['Frame 12']);
});

test('overlapping variants are found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 50, { characters: 'Value#1' })]);
  const r = auditNodes([set], MIXED);
  assert.deepEqual(r.overlappingVariants, ['Chip: Tone=A × Tone=B']);
  assert.deepEqual(empty(r), ['overlappingVariants']);
});

test('a variant that lost its property reference is found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 200, {})]);
  const r = auditNodes([set], MIXED);
  assert.equal(r.refMismatch.length, 1);
  assert.match(r.refMismatch[0], /^Chip › value \[TEXT\]: Tone=A \{characters=Value#1\} vs Tone=B \{\}$/);
});

test('a property no layer references is found', () => {
  const set = n('COMPONENT_SET', 'Chip', { componentPropertyDefinitions: { 'Value#1': { type: 'TEXT' }, 'Show value#2': { type: 'BOOLEAN' }, Tone: { type: 'VARIANT' } } },
    [variant('Tone=A', 0, { characters: 'Value#1' }), variant('Tone=B', 200, { characters: 'Value#1' })]);
  assert.deepEqual(auditNodes([set], MIXED).unusedProps, ['Chip: Show value#2']);
});

test('text clipped by a clipping ancestor is found', () => {
  const text = n('TEXT', '10', { textStyleId: 'S:1', absoluteBoundingBox: { x: 213, y: 0, width: 22, height: 24 } });
  const ticks = n('FRAME', 'ticks', { clipsContent: true, absoluteBoundingBox: { x: 0, y: 0, width: 232, height: 24 } }, [text]);
  const chart = n('FRAME', 'RoundChart', { absoluteBoundingBox: { x: 0, y: 0, width: 270, height: 158 } }, [ticks]);
  assert.deepEqual(auditNodes([chart], MIXED).clippedText, [text.id + ' 10 in ticks']);
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ~/job/studio-design && node --test tests/js/audit.test.js`
Expected: FAIL (`Cannot find module .../audit.js`).

- [ ] **Step 3: Write `template/design/figma/audit.js`**

```js
// Figma page audit. Paste into use_figma, then: return await auditPage('<pageId>');
// Read-only. Outside instances it checks: unbound SOLID paints, text without a text style, default
// layer names, text clipped by a clipping ancestor. Per component set or standalone component:
// overlapping variants, layers whose property references differ between variants, component
// properties no layer references.
const DEFAULT_NAME = /^(Frame|Rectangle|Text|Component|Group|Ellipse|Vector|Instance|Line|Polygon|Star|Section)( \d+)?$/;

function walk(node, visit, insideInstance = false) {
  visit(node, insideInstance);
  if (node.children) for (const c of node.children) walk(c, visit, insideInstance || node.type === 'INSTANCE');
}
function box(node) { return node.absoluteBoundingBox || { x: node.x, y: node.y, width: node.width, height: node.height }; }
function overlap(a, b) { return a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height; }
function clippingAncestor(node) {
  let p = node.parent;
  while (p && p.type !== 'PAGE' && p.type !== 'DOCUMENT') { if (p.clipsContent === true) return p; p = p.parent; }
  return null;
}
function layerPath(node, root) {
  const parts = [];
  for (let x = node; x && x !== root; x = x.parent) {
    const same = x.parent && x.parent.children ? x.parent.children.filter((c) => c.name === x.name) : [x];
    const i = same.indexOf(x);
    parts.unshift(i > 0 ? x.name + '#' + i : x.name);
  }
  return parts.join(' / ');
}
function refsKey(node) {
  const r = node.componentPropertyReferences || {};
  return Object.keys(r).sort().map((k) => k + '=' + r[k]).join(',');
}
function propUsage(owner, variants, out) {
  const defs = owner.componentPropertyDefinitions || {};
  const used = new Set();
  for (const v of variants) walk(v, (x, inInst) => {
    if (inInst) return;
    const r = x.componentPropertyReferences;
    if (r) for (const k of Object.values(r)) used.add(k);
  });
  for (const [k, d] of Object.entries(defs)) if (d.type !== 'VARIANT' && !used.has(k)) out.unusedProps.push(owner.name + ': ' + k);
}
function setChecks(set, out) {
  const vs = set.children.filter((c) => c.type === 'COMPONENT');
  const rel = (v) => ({ x: v.x, y: v.y, width: v.width, height: v.height });
  for (let i = 0; i < vs.length; i++) for (let j = i + 1; j < vs.length; j++) {
    if (overlap(rel(vs[i]), rel(vs[j]))) out.overlappingVariants.push(set.name + ': ' + vs[i].name + ' × ' + vs[j].name);
  }
  const seen = new Map();
  for (const v of vs) walk(v, (x, inInst) => {
    if (inInst || x === v) return;
    const p = layerPath(x, v) + ' [' + x.type + ']';
    const k = refsKey(x);
    if (!seen.has(p)) seen.set(p, { k, v: v.name });
    else if (seen.get(p).k !== k) out.refMismatch.push(set.name + ' › ' + p + ': ' + seen.get(p).v + ' {' + seen.get(p).k + '} vs ' + v.name + ' {' + k + '}');
  });
  propUsage(set, vs, out);
}
function auditNodes(roots, MIXED) {
  const out = { unboundPaints: [], unstyledText: [], defaultNames: [], overlappingVariants: [], refMismatch: [], unusedProps: [], clippedText: [] };
  for (const root of roots) walk(root, (x, inInst) => {
    if (inInst) return;
    const id = x.id + ' ' + x.name;
    if (DEFAULT_NAME.test(x.name)) out.defaultNames.push(id);
    for (const prop of ['fills', 'strokes']) {
      const ps = x[prop];
      if (!Array.isArray(ps)) continue;
      for (const p of ps) if (p.type === 'SOLID' && p.visible !== false && !(p.boundVariables && p.boundVariables.color)) out.unboundPaints.push(id + ' ' + prop);
    }
    if (x.type === 'TEXT') {
      if (!x.textStyleId || x.textStyleId === MIXED) out.unstyledText.push(id);
      const clip = x.visible === false ? null : clippingAncestor(x);
      if (clip) {
        const a = box(x), b = box(clip);
        if (a.x < b.x - 0.5 || a.y < b.y - 0.5 || a.x + a.width > b.x + b.width + 0.5 || a.y + a.height > b.y + b.height + 0.5) out.clippedText.push(id + ' in ' + clip.name);
      }
    }
    if (x.type === 'COMPONENT_SET') setChecks(x, out);
    else if (x.type === 'COMPONENT' && (!x.parent || x.parent.type !== 'COMPONENT_SET')) propUsage(x, [x], out);
  });
  return out;
}
async function auditPage(pageId) {
  const page = figma.root.children.find((p) => p.id === pageId);
  if (!page) throw new Error('No page ' + pageId);
  await figma.setCurrentPageAsync(page);
  const r = auditNodes(page.children, figma.mixed);
  const counts = Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v.length]));
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  return { page: page.name, ok: total === 0, counts, samples: Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v.slice(0, 8)])) };
}
if (typeof module !== 'undefined' && module.exports) module.exports = { auditNodes, DEFAULT_NAME };
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ~/job/studio-design && node --test tests/js/audit.test.js`
Expected: `# pass 6`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Figma Page Audit"
```

---

### Task 11: Local preflight

**Files:**
- Create: `scripts/preflight.sh`, `tests/test_preflight.sh`

**Interfaces:**
- Consumes: `scripts/install.sh` (fix text), `scripts/setup-python.sh` (fix text).
- Produces: `scripts/preflight.sh` prints `✅ <item>` or `❌ <item> — fix: <command>` per item, then `PREFLIGHT OK` (exit 0) or `PREFLIGHT FAIL: N` (exit 1); env `CLAUDE_HOME`, `STUDIO_PY` override paths. Items: studio python, node ≥ 20, npx, git identity, lsof, skills `studio-design grilling hallmark design-agent mobile-design-patterns auditing-accessibility`, Figma plugin skills, agents `tz-analyst studio-design-reviewer studio-design-figma-builder design-scout`.

- [ ] **Step 1: Write the failing test** `tests/test_preflight.sh`

```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
export CLAUDE_HOME="$tmp/home"; mkdir -p "$CLAUDE_HOME"
out="$(STUDIO_PY=/usr/bin/false "$REPO/scripts/preflight.sh")"; assert_eq 1 $? "fails on a bare machine"
assert_contains "$out" "❌ studio python (PyMuPDF, fontTools, brotli) — fix: $REPO/scripts/setup-python.sh" "names the python fix"
assert_contains "$out" "❌ skill studio-design — fix: $REPO/scripts/install.sh" "names the install fix"
assert_contains "$out" "❌ skill grilling — fix: $HOME/job/agent-skills/install.sh" "names the agent-skills fix"
assert_contains "$out" "PREFLIGHT FAIL" "fail summary"
for s in studio-design grilling hallmark design-agent mobile-design-patterns auditing-accessibility; do
  mkdir -p "$CLAUDE_HOME/skills/$s"; echo x > "$CLAUDE_HOME/skills/$s/SKILL.md"
done
mkdir -p "$CLAUDE_HOME/plugins/cache/official/figma/1.0.0/skills/figma-use"; echo x > "$CLAUDE_HOME/plugins/cache/official/figma/1.0.0/skills/figma-use/SKILL.md"
mkdir -p "$CLAUDE_HOME/agents"
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do echo x > "$CLAUDE_HOME/agents/$a.md"; done
fakepy="$tmp/py"; printf '#!/bin/sh\nexit 0\n' > "$fakepy"; chmod +x "$fakepy"
out="$(STUDIO_PY="$fakepy" "$REPO/scripts/preflight.sh")"; assert_eq 0 $? "passes when everything is present"
assert_contains "$out" "PREFLIGHT OK" "ok summary"
finish
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash ~/job/studio-design/tests/test_preflight.sh`
Expected: FAIL (`preflight.sh: No such file or directory`).

- [ ] **Step 3: Write `scripts/preflight.sh`**

```bash
#!/usr/bin/env bash
# Checks what the studio-design pipeline needs on this machine. Prints ✅/❌ per item with a fix for
# each ❌, then «PREFLIGHT OK» or «PREFLIGHT FAIL: N». In-session tools (Figma MCP, artifact type,
# browser, Figma fonts) are checked by the studio-design skill at stage 0.
# Test overrides: CLAUDE_HOME, STUDIO_PY.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
home="${CLAUDE_HOME:-$HOME/.claude}"
py="${STUDIO_PY:-$repo/.venv/bin/python}"
bad=0
ok() { echo "✅ $1"; }
no() { echo "❌ $1 — fix: $2"; bad=$((bad + 1)); }
fix_skill() {
  case "$1" in
    studio-design) echo "$repo/scripts/install.sh" ;;
    grilling) echo "$HOME/job/agent-skills/install.sh" ;;
    design-agent|mobile-design-patterns) echo "$HOME/design-intelligence-agent/scripts/install.sh" ;;
    *) echo "install the skill, see $repo/docs/manifest.md › Skills" ;;
  esac
}
fix_agent() {
  case "$1" in
    design-scout) echo "$HOME/design-intelligence-agent/scripts/install.sh" ;;
    *) echo "$repo/scripts/install.sh" ;;
  esac
}

if [ -x "$py" ] && "$py" -c 'import pymupdf, fontTools, brotli' >/dev/null 2>&1; then ok "studio python (PyMuPDF, fontTools, brotli)"
else no "studio python (PyMuPDF, fontTools, brotli)" "$repo/scripts/setup-python.sh"; fi
nv="$(node --version 2>/dev/null | sed 's/^v//' | cut -d. -f1)"
if [ -n "$nv" ] && [ "$nv" -ge 20 ]; then ok "node $(node --version)"; else no "node 20 or newer" "install Node.js 20+ from https://nodejs.org"; fi
if command -v npx >/dev/null 2>&1; then ok "npx"; else no "npx" "reinstall Node.js with npm"; fi
if git config user.name >/dev/null && git config user.email >/dev/null; then ok "git identity"
else no "git identity" "git config --global user.name 'Name' && git config --global user.email 'mail'"; fi
if command -v lsof >/dev/null 2>&1; then ok "lsof"; else no "lsof" "install lsof (new-client.sh uses it to pick a free harness port)"; fi
for s in studio-design grilling hallmark design-agent mobile-design-patterns auditing-accessibility; do
  if [ -f "$home/skills/$s/SKILL.md" ]; then ok "skill $s"; else no "skill $s" "$(fix_skill "$s")"; fi
done
if ls "$home"/plugins/cache/*/figma/*/skills/figma-use/SKILL.md >/dev/null 2>&1; then ok "Figma plugin skills (figma-use, figma-generate-library, figma-generate-design)"
else no "Figma plugin skills" "install the Figma plugin for Claude Code (claude-plugins-official › figma)"; fi
for a in tz-analyst studio-design-reviewer studio-design-figma-builder design-scout; do
  if [ -f "$home/agents/$a.md" ]; then ok "agent $a"; else no "agent $a" "$(fix_agent "$a")"; fi
done
if [ "$bad" -eq 0 ]; then echo "PREFLIGHT OK"; exit 0; fi
echo "PREFLIGHT FAIL: $bad"
exit 1
```

Run: `chmod +x ~/job/studio-design/scripts/preflight.sh`

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash ~/job/studio-design/tests/test_preflight.sh`
Expected: `PASS test_preflight.sh`.

- [ ] **Step 5: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Local Preflight"
```

---

### Task 12: Docs — manifest, playbook, packages, profiles, rules, lessons

**Files:**
- Create: `docs/manifest.md`, `docs/playbook.md`, `docs/packages.md`, `docs/lessons.md`, `docs/profiles/{web-landing,web-product,mobile,game}.md`, `docs/rules/{design,numbers-and-locale,figma,artifact,client}.md`

**Interfaces:**
- Consumes: script names and behaviour from Tasks 2–11.
- Produces: the documents stage references (Task 13) and agents (Task 14) cite by path.

- [ ] **Step 1: Write `docs/manifest.md`**

```markdown
# Manifest

Everything the pipeline uses, per stage, with how to check it and how to fix it. `scripts/preflight.sh`
checks the local part; stage 0 of `studio-design` checks the in-session part.

## Environment and accounts

| Item | Why | Check | Fix |
|---|---|---|---|
| Claude Code desktop app, Code tab | only place with the Design System artifact type, the built-in browser and the Figma MCP together | the session lists `Artifact`, `mcp__Claude_Browser__*` and Figma MCP tools | open the project in the desktop app |
| Model Opus | main session and every agent (`model: opus`) | session model | pick Opus in the app |
| Figma, Professional plan, full seat | `use_figma` writes need an edit seat | Figma MCP `whoami` | upgrade the seat; the user creates the file and shares its URL |
| Font licence | shipping fonts to a client | licence file next to the fonts (OFL or commercial) | ask the client or pick another font at stage 4 |

## Session tools

| Tool | Stages | Purpose | Check at stage 0 |
|---|---|---|---|
| Artifact, type Design System (quickstart, publish, read, list) | 2, 4–6, 8 | coded source of truth, previews, client link | `Artifact action=quickstart intent=other` lists a Design System type |
| Figma MCP `use_figma`, `get_screenshot`, `get_metadata`, `upload_assets` | 7 | build and verify | `whoami` answers; a read-only `use_figma` listing pages works |
| Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs` | 2, 7 | import an existing client DS | same as above |
| Built-in browser (`mcp__Claude_Browser__*`) or Claude in Chrome | 3, 5, 6, 8 | harness, measurements, sweep, screenshots | `preview_start` with `ds-harness` opens `harness/_sweep.html` |
| WebFetch, WebSearch | 2 | references | a fetch of a public page works |
| AskUserQuestion | 1, 2, 9 | decisions | always present |
| Bash | all | scripts | always present |

## Local dependencies (`scripts/preflight.sh`)

| Item | Why | Fix |
|---|---|---|
| studio Python `.venv` with PyMuPDF, fontTools, brotli | `pdf_pages.py`, `font_check.py`, font conversion | `scripts/setup-python.sh` |
| Node 20+, npx | format checks, fixtures, `tsc` through the client `package.json` | install Node.js |
| git with user.name and user.email | every client container is a git repository | `git config --global …` |
| lsof | `new-client.sh` picks a free harness port | install lsof |

## Skills

| Skill | Source | Stages | Role |
|---|---|---|---|
| `studio-design` | this repository, `scripts/install.sh` | all | orchestrator |
| `grilling` | `~/job/agent-skills`, `install.sh` | 1, 9 | decision-tree interview with output file, client questions and fact-finder options |
| `hallmark` | `~/.agents/skills/hallmark` (linked into `~/.claude/skills`) | 2, 4, 8 | directions, anti-slop rules, audit |
| `design-agent` | `~/design-intelligence-agent`, `scripts/install.sh` | 2 | references, patterns, redesign audit |
| `mobile-design-patterns` | `~/design-intelligence-agent` | 3, 5 | mobile profile |
| `auditing-accessibility` | `~/.claude/skills/auditing-accessibility` | 8 | contrast, touch targets, focus |
| `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design` | Claude Code plugin `figma` | 7 | Plugin API rules, library build, screen build |
| `artifact-design`, `artifact-capabilities` | loaded through the artifact quickstart | 4 | page contract of the artifact |

## Agents

| Agent | Source | Stages |
|---|---|---|
| `tz-analyst` | this repository | 1 (and fact-finder for `grilling`) |
| `design-scout` | `~/design-intelligence-agent` | 2 |
| `studio-design-reviewer` | this repository | 2, 5, 6, 8, 9 |
| `studio-design-figma-builder` | this repository | 7 |

## Not built

- Package «ДС + код для разработки»: no stages exist; say so to the user.
- Agent `studio-design-ds-builder`: code components stay in the main session (revisit after the pilot).
```

- [ ] **Step 2: Write `docs/packages.md` and `docs/playbook.md`**

`docs/packages.md`:

```markdown
# Packages

| Package | Stages | Stage 6 and 7 scope |
|---|---|---|
| «ДС» | 0, 1, 2, 3, 4, 5, 7, 8, 9 | components plus 1–2 key templates (from the layout budget) |
| «ДС + экраны» | 0–9 | every screen and state in the registry of `brief/tz-analysis.md` |
| «ДС + код для разработки» | not built | — |

The package and the number of included revision rounds are set in `CLIENT.md` by the contract.
When a request needs a stage outside the package, it is a change request (💰 in stage 9).
```

`docs/playbook.md`:

```markdown
# Playbook

The pipeline for a human reader. The agent follows `skills/studio-design/`.

## Before the first client

`scripts/setup-python.sh`, `scripts/install.sh`, `~/job/agent-skills/install.sh`, `scripts/preflight.sh`.

## A new client

1. `scripts/new-client.sh <slug> --name "Client"` → `~/job/clients/<slug>/`.
2. Fill `CLIENT.md` (contact, language, package, rounds, deadlines).
3. Put the brief into `design/brief/`.
4. Open `~/job/clients/<slug>/design` in the Claude Code desktop app and say «studio-design: stage 0».

## Stages and checkpoints

0 Intake → 1 TZ analysis 🧑 → 2 Direction 🧑 → 3 Layout budget → 4 Foundations → 5 Components →
6 Screens → 7 Figma → 8 QA and handoff 🧑 → 9 Revision rounds 🧑. 🧑 = the agent prepares material and
questions, you take them to the client, the answers go to `design/decisions.md`.

## Resuming

Open the client's `design` folder and say «продолжаем studio-design». The agent reads `PROJECT.md`,
`progress.md`, `decisions.md` and `questions.md` and continues from the recorded stage.

## After a project

Add what went wrong to `docs/lessons.md`; when it changes behaviour, also to the rule or stage
reference it affects. Commit in this repository.
```

- [ ] **Step 3: Write the four profiles**

`docs/profiles/web-landing.md`:

```markdown
# Profile: web-landing

- Target widths: design at 1440; check 1920, 1280, 768, 414, 375, 320. Content container 1200–1280.
- No horizontal scroll at any width; buttons and nav links never wrap to two lines; image grid tracks use `minmax(0, 1fr)` (hallmark mobile rules).
- Layout budget (stage 3): the hero at 1440 and 375; the densest section (pricing, features or a comparison) at 375.
- Touch targets on mobile widths at least 44 × 44 px.
- Stage 8 checks: every section at 320 / 375 / 414 / 768 without overflow; contrast AA; the primary CTA visible without scrolling at 1440 and 375.
```

`docs/profiles/web-product.md`:

```markdown
# Profile: web-product

- Target widths: design at 1440; minimum desktop 1280; check 1920. Mobile or tablet only when the brief asks for it.
- Shell: sidebar 240–280 px or a top bar; content max width set at stage 3.
- Density: table rows 40–48 px; form fields 40–44 px; keyboard focus visible on every control.
- Layout budget (stage 3): the densest table or dashboard at 1280, the longest form, the navigation shell with the longest labels.
- Stage 8 checks: 1280 without overflow; empty, loading and error states for every data view; contrast AA; keyboard path through the main flow.
```

`docs/profiles/mobile.md`:

```markdown
# Profile: mobile

- Targets: iOS 393 × 852 pt (primary), 375 × 667 (small), 430 × 932 (large); Android 360 × 800 and 412 × 915 dp.
- Touch targets: at least 44 × 44 pt on iOS, 48 × 48 dp on Android. Respect safe areas (status bar, home indicator, notch).
- Navigation: tab bar for 3–5 top destinations; platform back behaviour; sheets over full-screen modals where the platform expects them (see `mobile-design-patterns`).
- Layout budget (stage 3): the densest list or detail screen at 375 × 667 with the keyboard open, and the longest form.
- Stage 8 checks: 375 × 667 without clipping; larger text size (Dynamic Type / font scale) on the key screens; contrast AA.
```

`docs/profiles/game.md`:

```markdown
# Profile: game

From the Mayor Sim effort (`~/job/mayor-sim-design`).

- Target: 1920 × 1080; also the minimum resolution the brief names.
- HUD lives on the edges; the scene in the centre stays free (Mayor: two 460 px rails and 32 px margins leave 936 px). What does not fit goes into a window or a drawer, never into the centre.
- Windows open over the scene and close only through their ×; several windows may stack; one is focused.
- One primary action per screen (Mayor: «Завершить ход»); the brand colour is a signal, not a surface.
- Layout budget (stage 3): the main game screen in every state (active, waiting, windows open) at 1080 height, with the longest labels and the largest numbers from the fixtures.
- Stage 8 checks: every state fits 1080; stress values (64-character names, 100 трлн ₽, the largest window content).
```

- [ ] **Step 4: Write the five rules**

`docs/rules/design.md`:

```markdown
# Design rules

- Code is the source of truth; Figma mirrors it. No Figma-only component.
- Tokens are locked: every colour and font in code comes from a token; a missing value becomes a new token first (hallmark).
- Every interactive component ships default, hover, focus, pressed and disabled; add loading, error and success where the component can be in them.
- Layout budget before components: the densest screens are measured at the target size at stage 3.
- Sample values come from `ds/fixtures/` through the format functions; missing data is marked `—` or «to confirm», never invented. No invented metrics in client-visible copy.
- Contrast: WCAG AA (4.5:1 body text, 3:1 large text and UI parts).
- One primary action per view; the brand colour signals, it does not fill surfaces.
```

`docs/rules/numbers-and-locale.md`:

```markdown
# Numbers and locale (ru-RU default)

Implemented by `format` in `ds/project/components/bundle.js`, tested by `ds/scripts/check_format.js`.

- Thousands separator U+202F; decimal comma; minus U+2212.
- Units and scale words after a no-break space U+00A0: `120 млн ₽`, `450 000 кв. м`, `4,5 %`.
- Money from 1 млн: млн / млрд / трлн, three significant digits, trailing zeros dropped (`1,2 млрд ₽`), except a forced-scale pair (`0,85 млрд` next to `1,20 млрд`).
- Percent below 10 keeps one decimal. Percentage deltas are in п.п.
- Deltas are signed (`+` / `−`); zero is `0`; no data is `—`.
- Body text in Figma and code keeps a number with its unit through U+00A0 so a line never breaks between them.
- Another locale is a stage 4 decision recorded in `decisions.md`; then `format` and `format-cases.json` change together.
```

`docs/rules/figma.md`:

```markdown
# Figma rules

Read before every `use_figma` call. Load the `figma:figma-use` skill (and `figma-generate-library` for components, `figma-generate-design` for screens).

## Workflow per batch

1. Read `design/figma/figma-state.json`.
2. Paste `design/figma/prelude.js` (and `prelude.project.js`) before the task code; pass component IDs from the ledger.
3. Build one component or one screen per call; return every created and mutated node ID.
4. Run `design/figma/audit.js` on every touched page (read-only calls may run in parallel); all counts must be 0.
5. `get_screenshot` of every new component set and screen; look at it.
6. Update `figma-state.json` (IDs, decisions, completed steps) and add or update the page's Doc frame.

## API rules

- Mutating calls strictly sequential; one page switch per call.
- The MCP runtime sees only Google Fonts: text styles bind to Typography variables with a Google stand-in; the user swaps the family to the real font at the very end, because edits fail after the swap.
- A bound paint carries the resolved variable colour (`P.paint`), otherwise an instance override equal to the main value renders the placeholder colour.
- `clone()` of a variant drops property references: re-bind TEXT, BOOLEAN and INSTANCE_SWAP references after cloning; the audit reports misses as `refMismatch`.
- Hidden instance sublayers take no fill writes: set fills before hiding.
- Instance children cannot be moved, and constraint-scaled layers ignore resize: build continuous-value parts (slider fill, progress) with auto-layout FIXED widths and try an override on an instance before closing the component.
- Plan size variants against the 30-variant cap before building (Mayor had no button size L).
- Append a node to its auto-layout parent before setting FILL.
- After `setProperties` or `swapComponent`, query nested nodes again; earlier references go stale.
- TEXT property defaults are shared across a set; per-variant sample values go to an Examples row of instances.
- A script that throws is rolled back; read the canvas before retrying only when the error says the retry is unsafe.
- Every page gets a Doc frame; component purpose goes into the component or set description.
- Tests and experiments never run in a client file.
```

`docs/rules/artifact.md`:

```markdown
# Artifact rules (Design System type)

- Create the artifact once at stage 4 through `Artifact action=quickstart` and the Design System type; record its URL in `PROJECT.md` and `CLIENT.md`.
- Read the artifact's `project/design-system.json` right before every publish; merge, never overwrite fields the type owns.
- Publish with `url` = the artifact, `root` = `design/ds`, `file_path` = `project/design-system.json`, and only changed files in `files`.
- `index.d.ts` is published with `contentType: text/plain`.
- Stamp `lastChange` (by, via, at, note) in `design-system.json` on every publish.
- Every preview starts with the `<!-- @dsCard … -->` marker; full-page templates add `page` and a width.
- Uploaded assets live at `/_blob/<id>`; keep the local copy in `ds/upload/` and the mapping in `ds/upload/blobs.json` so the harness shows it.
- The artifact is private; the user grants the client access. Remind them at every checkpoint.
```

`docs/rules/client.md`:

```markdown
# Client communication

- Everything the client reads is in the client's language (`CLIENT.md`), plain, without jargon.
- Questions (`questions.md`) are grouped by topic; each has our recommended answer so the client can reply «ок».
- Push back on a request that breaks UX, system consistency, the brief or accessibility — always with the reason, evidence (brief page, profile rule, contrast figures) and an alternative. Never implement it silently; never refuse silently.
- Anything outside the package or beyond the included rounds is a change request, said plainly.
- Every answer goes to `decisions.md` with the date and the source (who, where).
- The user sends everything to the client; the agent never contacts the client.
```

- [ ] **Step 5: Write `docs/lessons.md`**

```markdown
# Lessons

Symptom → cause → rule. Append after every project; when a lesson changes behaviour, update the
rule or stage reference it names.

1. S-08 did not fit 1080, found at the very end → components were built before any screen → stage 3 layout budget (`stage-03-layout-budget.md`).
2. The custom font could not be used in Figma, found mid-build → the Figma MCP runtime sees only Google Fonts → stage 0 font check and Typography variables with a stand-in (`rules/figma.md`).
3. A cloned variant lost its Name and Value bindings → `clone()` drops property references → re-bind after cloning; `audit.js` `refMismatch`.
4. Variants overlapped inside a set → positions not re-laid after adding variants → `audit.js` `overlappingVariants`.
5. The Unfocused window showed a pink button instead of content → a stray INSTANCE_SWAP property bound the slot → `audit.js` `unusedProps` and `refMismatch`.
6. The «10» tick of a chart was cut → a clipping frame narrower than its text → `audit.js` `clippedText`.
7. Sliders in templates stuck at 25 % → handle position cannot be overridden in an instance → build continuous parts with auto-layout widths (`rules/figma.md`).
8. No button size L in Figma → the 30-variant cap was hit → plan size variants first (`rules/figma.md`).
9. Sample values typed by hand → no shared data → `ds/fixtures/` and `format_fixtures.js`.
10. Work started inside an unrelated repository and borrowed its `node_modules` → no own project container → `new-client.sh` and the client `package.json`.
11. No history of the design folder → it was not a git repository → every client container is one.
```

- [ ] **Step 6: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Manifest Playbook Rules Profiles And Lessons"
```

---

### Task 13: The studio-design skill and stage references

**Files:**
- Create: `skills/studio-design/SKILL.md`, `skills/studio-design/references/stage-00-intake.md` … `stage-09-revisions.md`, `scripts/validate.sh`, `tests/test_validate.sh`

**Interfaces:**
- Consumes: every script (Tasks 2–11), docs (Task 12), `grilling` options (Task 1).
- Produces: `scripts/validate.sh` (exit 0 when skills, agents and all ten stage references pass; every stage reference has the headings `## Inputs`, `## Steps`, `## Outputs`, `## Gate`, `## Skills and agents`, `## Pitfalls`); agent names used by Task 14.

- [ ] **Step 1: Write the failing test** `tests/test_validate.sh`

```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
"$REPO/scripts/validate.sh" >/dev/null; assert_eq 0 $? "the real pipeline validates"
fake="$tmp/repo"; mkdir -p "$fake/scripts" "$fake/agents" "$fake/skills/studio-design/references"
cp "$REPO/scripts/validate.sh" "$fake/scripts/"
printf -- '---\nname: studio-design\ndescription: x\n---\n' > "$fake/skills/studio-design/SKILL.md"
printf -- '---\nname: bad-agent\ndescription: x\nmodel: sonnet\n---\n' > "$fake/agents/bad-agent.md"
printf '## Inputs\n## Steps\n' > "$fake/skills/studio-design/references/stage-00-intake.md"
out="$("$fake/scripts/validate.sh")"; assert_eq 1 $? "a broken pipeline fails"
assert_contains "$out" "FAIL agent bad-agent" "agent without opus fails"
assert_contains "$out" "FAIL stage-00-intake: missing [## Outputs] [## Gate] [## Skills and agents] [## Pitfalls]" "missing headings are named"
assert_contains "$out" "FAIL stage-01-tz-analysis.md missing" "missing stage file is named"
finish
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash ~/job/studio-design/tests/test_validate.sh`
Expected: FAIL (`validate.sh: No such file or directory`).

- [ ] **Step 3: Write `scripts/validate.sh`**

```bash
#!/usr/bin/env bash
# Structural checks of the pipeline: skill and agent frontmatter, the ten stage references.
set -uo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
status=0
fm() { awk 'NR==1{ if ($0 != "---") exit; next } /^---$/{ exit } { print }' "$1"; }
field() { fm "$1" | sed -n "s/^$2:[[:space:]]*//p" | head -1; }
for f in "$repo"/skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  name="$(basename "$(dirname "$f")")"
  if [ "$(field "$f" name)" = "$name" ] && fm "$f" | grep -q '^description:'; then echo "ok   skill $name"
  else echo "FAIL skill $name: frontmatter needs name and description"; status=1; fi
done
for f in "$repo"/agents/*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f" .md)"
  if [ "$(field "$f" name)" = "$name" ] && fm "$f" | grep -q '^description:' && [ "$(field "$f" model)" = "opus" ]; then echo "ok   agent $name"
  else echo "FAIL agent $name: frontmatter needs name, description and model: opus"; status=1; fi
done
refs="$repo/skills/studio-design/references"
for n in 00-intake 01-tz-analysis 02-direction 03-layout-budget 04-foundations 05-components 06-screens 07-figma 08-qa-handoff 09-revisions; do
  f="$refs/stage-$n.md"
  if [ ! -f "$f" ]; then echo "FAIL stage-$n.md missing"; status=1; continue; fi
  miss=""
  for h in "## Inputs" "## Steps" "## Outputs" "## Gate" "## Skills and agents" "## Pitfalls"; do grep -qx "$h" "$f" || miss="$miss [$h]"; done
  if [ -z "$miss" ]; then echo "ok   stage-$n"; else echo "FAIL stage-$n: missing$miss"; status=1; fi
done
exit "$status"
```

Run: `chmod +x ~/job/studio-design/scripts/validate.sh`

- [ ] **Step 4: Write `skills/studio-design/SKILL.md`**

````markdown
---
name: studio-design
description: Orchestrates the studio design service for a client — from a brief (TZ) to a coded design system (Claude Design artifact) and a Figma library, stage by stage with gates. Use when the user says «studio-design», «новый клиент», «дизайн-система для клиента», «продолжаем studio-design», «раунд правок», or works inside ~/job/clients/<slug>/design.
---

# studio-design

You run the design pipeline for one client container, `~/job/clients/<slug>/`. The pipeline
repository is `~/job/studio-design`; its docs are the rules you follow.

## Invariants

- Work only inside the client container. Never write client material into `~/job/studio-design`.
- Paths written `design/...` are relative to the client container `~/job/clients/<slug>/`. The session's working directory is `design/`, so commands use paths relative to it (`ds/scripts/...`, `figma/...`).
- Every stage follows its reference in `references/`. Read it before starting the stage; it names every input file. Do not look for inputs it does not name.
- A stage ends only when its gate passes and `design/progress.md` records the evidence (command output, screenshot paths, decision entries). Evidence is pasted, never typed from memory.
- 🧑 checkpoints: prepare the material and the questions in the client's language, then stop. The user takes them to the client; answers go to `design/decisions.md`.
- Decisions belong to the user and the client. Agents report; you decide nothing on the client's behalf.
- Files, code and comments are in English; everything the client reads is in the client's language (`CLIENT.md`).
- Rules: `~/job/studio-design/docs/rules/*.md`. Tools: `docs/manifest.md`. Pitfalls: `docs/lessons.md`.

## Start or resume

1. Read `CLIENT.md`, `design/PROJECT.md`, `design/progress.md`, `design/decisions.md`, `design/questions.md`.
2. The current stage is the one in `PROJECT.md`. If a gate of that stage is open, finish it first.
3. Say in one line where the project stands and what comes next.

## Stages

| # | Reference | Checkpoint |
|---|---|---|
| 0 | `references/stage-00-intake.md` | |
| 1 | `references/stage-01-tz-analysis.md` | 🧑 |
| 2 | `references/stage-02-direction.md` | 🧑 |
| 3 | `references/stage-03-layout-budget.md` | |
| 4 | `references/stage-04-foundations.md` | |
| 5 | `references/stage-05-components.md` | |
| 6 | `references/stage-06-screens.md` | |
| 7 | `references/stage-07-figma.md` | |
| 8 | `references/stage-08-qa-handoff.md` | 🧑 |
| 9 | `references/stage-09-revisions.md` | 🧑 |

Skip stages the package excludes (`~/job/studio-design/docs/packages.md`). Package «ДС + код для
разработки» is not built: say so.

## Agents

- `tz-analyst` — facts from the brief (stage 1; fact-finder for `grilling`).
- `design-scout` — references (stage 2).
- `studio-design-reviewer` — independent review at stages 2, 5, 6, 8, 9.
- `studio-design-figma-builder` — Figma batches (stage 7), one at a time.

Agent reports are not shown to the user; relay what matters. Give every agent exact input and
output paths.

## After every stage

Update `PROJECT.md` (current stage), `progress.md` (evidence) and commit in the client container:
`git -C ~/job/clients/<slug> add -A && git -C ~/job/clients/<slug> commit -m "<Stage N Title-Case Summary>"`.
````

- [ ] **Step 5: Write the ten stage references**

`references/stage-00-intake.md`:

```markdown
# Stage 0 · Intake

## Inputs
- `CLIENT.md`, `design/PROJECT.md`, the files in `design/brief/`.
- `~/job/studio-design/docs/manifest.md`, `docs/packages.md`, `docs/profiles/`.

## Steps
1. Run `~/job/studio-design/scripts/preflight.sh`; paste its output into `design/progress.md` › Preflight.
2. In-session checks, each as ✅/❌ with a fix in the same table:
   - Figma MCP: `whoami` answers and the seat can edit.
   - Artifact: `Artifact action=quickstart intent=other` lists a Design System type.
   - Browser: `preview_start` with the `ds-harness` configuration serves `ds/`; navigate to `http://localhost:<port>/project/README.md` and see it load. (The sweep page appears with the first previews at stage 5.)
   - Figma fonts: in a read-only `use_figma`, `figma.listAvailableFontsAsync()` contains the intended font family; if not, record a Google stand-in to use.
3. With the user, fill the empty fields of `CLIENT.md` (contact, language, package, rounds, deadlines) and `PROJECT.md` (entry mode, platform profile, target sizes).
4. Ask the user for the Figma file URL for this client; record it in `PROJECT.md` and `design/figma/figma-state.json` (`fileKey`, `fileUrl`).

## Outputs
- `design/progress.md` › Preflight table; filled `CLIENT.md` and `PROJECT.md`; `figma-state.json` with the file key.

## Gate
- No ❌ in the preflight table, or each ❌ accepted by the user for this project and recorded in `decisions.md`.

## Skills and agents
- None beyond the manifest checks.

## Pitfalls
- `docs/lessons.md` 2 (Figma fonts) and 10 (own container).
```

`references/stage-01-tz-analysis.md`:

```markdown
# Stage 1 · TZ analysis 🧑

## Inputs
- `design/brief/*` (the client's files), `CLIENT.md`, `design/PROJECT.md`.

## Steps
1. For every PDF in `design/brief/`: `~/job/studio-design/scripts/py ~/job/studio-design/scripts/pdf_pages.py <file> design/brief/pages --images`; copy useful embedded images to `design/refs/`.
2. Dispatch `tz-analyst` with the brief files and `design/brief/pages/`; it writes `design/brief/tz-analysis.md`.
3. Read the analysis. Run `grilling` with the user over the decisions it leaves open, passing: output file `design/decisions.md`, client-questions file `design/questions.md`, fact-finder `tz-analyst` with the brief files as sources.
4. Show the user `design/questions.md`; they send it to the client. 🧑 Stop until the answers come back; record each in `decisions.md` and move it to «Answered».

## Outputs
- `design/brief/tz-analysis.md`, `design/brief/pages/`, `design/decisions.md`, `design/questions.md`.

## Gate
- The grilling frontier is empty and every client answer is recorded in `decisions.md`.

## Skills and agents
- `grilling` (with the three caller options), agent `tz-analyst`.

## Pitfalls
- «Как это должно ощущаться» questions are not grilled; they go to stage 2 as directions.
- Facts come from the brief through `tz-analyst`; never ask the user what the brief says.
```

`references/stage-02-direction.md`:

```markdown
# Stage 2 · Direction 🧑

## Inputs
- `design/brief/tz-analysis.md`, `design/decisions.md`, `design/PROJECT.md` (entry mode, profile), `design/refs/`.

## Steps
1. Entry mode «from scratch»: dispatch `design-scout` with the platform profile and the brief's genre; then write three directions under `hallmark` rules into `design/directions/` and a directions page in the artifact (create the artifact now if needed, see stage 4 step 1).
2. Entry mode «brand book»: colours, fonts and logo are fixed; write one direction that sets colour roles, contrast and tone.
3. Entry mode «redesign»: audit the current product through `design-agent` (screenshots into `design/refs/`), then one direction that keeps recognisability.
4. Entry mode «existing DS»: import the client's tokens and components through Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs`; write what exists and what is missing into `design/directions/existing-ds.md`; skip to stage 3.
5. Dispatch `studio-design-reviewer` on the directions (slop, fit to the brief); fix what it finds.
6. 🧑 The user shows the directions to the client; record the choice in `decisions.md`; keep the rejected ones in `design/directions/`.

## Outputs
- `design/directions/*.md`, a style tile or directions page in the artifact.

## Gate
- The chosen direction is recorded in `decisions.md`.

## Skills and agents
- `hallmark`, `design-agent`, agents `design-scout`, `studio-design-reviewer`.

## Pitfalls
- Brand colour is a signal, not a surface (`rules/design.md`).
```

`references/stage-03-layout-budget.md`:

```markdown
# Stage 3 · Layout budget

## Inputs
- `design/brief/tz-analysis.md` (screen registry), the chosen direction, `~/job/studio-design/docs/profiles/<profile>.md`, `design/ds/fixtures/`.

## Steps
1. Pick the 2–3 densest screens named in the profile's «Layout budget» line.
2. Build them in code as zone boxes (plain blocks with the zone name and size) at the target sizes, with the longest labels and the largest values from the fixtures; add them as preview pages (`ds/previews_spec.py`, `gen_previews.py`, `build_harness.py`).
3. In the browser, measure every zone (`getBoundingClientRect`) at every target size; paste the numbers into `design/brief/layout-budget.md` with the zone sizes the components must respect.

## Outputs
- `design/brief/layout-budget.md`, the layout-budget preview pages.

## Gate
- Every zone fits its screen at every target size; the measured numbers are pasted.

## Skills and agents
- Platform skills from the profile (`mobile-design-patterns` for mobile).

## Pitfalls
- `docs/lessons.md` 1: this stage exists because S-08 did not fit 1080 at the end.
```

`references/stage-04-foundations.md`:

```markdown
# Stage 4 · Foundations

## Inputs
- The chosen direction, `design/brief/layout-budget.md`, `design/ds/project/*`, `~/job/studio-design/docs/rules/{design,numbers-and-locale,artifact}.md`.

## Steps
1. Create the artifact if it does not exist: `Artifact action=quickstart intent=other`, create from the Design System type, read its `project/design-system.json` and merge it into `design/ds/project/design-system.json`; record the URL in `PROJECT.md` and `CLIENT.md`.
2. Write tokens (`tokens.json`), the root class and base styles (`bundle.css`), README principles.
3. Fonts: put the woff2 files into `ds/project/fonts/` with the licence; run `~/job/studio-design/scripts/py fonts/font_check.py ds/project/fonts/*.woff2`; record the Figma stand-in chosen at stage 0.
4. Numbers: adjust `format` and `ds/fixtures/format-cases.json` if the locale or units differ; run `npm run check:format`.
5. Fill `ds/fixtures/sample.json` with the brief's real value ranges; run `npm run fixtures`.
6. Publish the style tile (`rules/artifact.md`).

## Outputs
- `tokens.json`, `bundle.css`, `README.md`, fonts, `fixtures/formatted.json`, the published style tile.

## Gate
- `npm run check:format` prints `all N cases pass`; `font_check.py` prints only ✅; the style tile is published.

## Skills and agents
- `hallmark`, `artifact-design` and `artifact-capabilities` (through the quickstart).

## Pitfalls
- `docs/lessons.md` 2 and 9.
```

`references/stage-05-components.md`:

```markdown
# Stage 5 · Components (code)

## Inputs
- `design/brief/tz-analysis.md` (component registry), `design/brief/layout-budget.md`, `design/ds/project/*`, `design/ds/previews_spec.py`, `~/job/studio-design/docs/rules/design.md`.

## Steps
1. Split the registry into batches of related components; per batch:
2. Add the components to `bundle.js` and `bundle.css`, types to `index.d.ts`, a README per component, preview specs to `previews_spec.py`.
3. `python3 ds/scripts/gen_previews.py <Names>` and `python3 ds/scripts/build_harness.py`.
4. Start the harness (`preview_start` ds-harness), open `harness/_sweep.html`, read `#result`.
5. Look at every new preview in the browser; fix what looks wrong.
6. `npm run check:types`.
7. Publish the batch (`rules/artifact.md`).
8. After the last batch, dispatch `studio-design-reviewer` for registry coverage and states.

## Outputs
- Components in the bundle, previews, READMEs, types; a published artifact version per batch.

## Gate
- The sweep's first line is `SWEEP OK: … 0 errors, 0 overflows, 0 empty`; `check:types` passes; screenshots of every new preview are in `progress.md`.

## Skills and agents
- `hallmark`; agent `studio-design-reviewer`.

## Pitfalls
- Build continuous-value parts (sliders, progress) so Figma can express the value later (`rules/figma.md`).
```

`references/stage-06-screens.md`:

```markdown
# Stage 6 · Screens (code)

## Inputs
- `design/brief/tz-analysis.md` (screen registry), `design/brief/layout-budget.md`, the components, `design/ds/fixtures/formatted.json`.

## Steps
1. Package «ДС»: the 1–2 templates from the layout budget. Package «ДС + экраны»: every screen and state in the registry.
2. Build each screen as a preview page with the `page` card marker and its width; every value from the fixtures.
3. Measure the rails, zones and free areas at every target size in the browser; paste the numbers.
4. Sweep, look, publish; dispatch `studio-design-reviewer` on the screens.

## Outputs
- Screen preview pages; measurements in `progress.md`; a published artifact version.

## Gate
- Every screen fits at every target size (numbers pasted); the sweep is OK.

## Skills and agents
- Agent `studio-design-reviewer`.

## Pitfalls
- A screen that does not fit changes components, not the budget, unless the user decides otherwise in `decisions.md`.
```

`references/stage-07-figma.md`:

```markdown
# Stage 7 · Figma

## Inputs
- `design/figma/figma-state.json`, `design/figma/prelude.js`, `design/figma/prelude.project.js`, `design/figma/audit.js`, `design/ds/project/*`, `design/ds/fixtures/formatted.json`, `~/job/studio-design/docs/rules/figma.md`.

## Steps
1. Foundations: variables (colour, spacing, typography with the stand-in font), text and effect styles, named by the conventions in `prelude.js`; audit the Foundations page.
2. Dispatch `studio-design-figma-builder` once per batch, in the order of stage 5: one component set or one screen per call, audit after each batch, screenshots back.
3. Look at every screenshot yourself; send defects back to the builder as a new batch.
4. Templates and screens from stage 6, with fixture values and the background assets (`upload_assets`).
5. Keep `figma-state.json` current; one Doc frame per page.

## Outputs
- The Figma library and screens; `figma-state.json`; audit outputs and screenshot paths in `progress.md`.

## Gate
- `audit.js` on every touched page returns `ok: true` (all counts 0); every screenshot looked at.

## Skills and agents
- `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design`; agent `studio-design-figma-builder`.

## Pitfalls
- `docs/lessons.md` 3–8.
```

`references/stage-08-qa-handoff.md`:

```markdown
# Stage 8 · QA and handoff 🧑

## Inputs
- The artifact, the Figma file, `design/brief/tz-analysis.md`, `~/job/studio-design/docs/profiles/<profile>.md`, `CLIENT.md`.

## Steps
1. Stress tests from the profile (longest names, largest numbers, most content) in code and Figma.
2. Accessibility pass with `auditing-accessibility`: contrast, touch targets, focus.
3. Final sweep and final `audit.js` on every page.
4. Dispatch `studio-design-reviewer` for a whole-project review against the registry.
5. Write `design/handoff/README.md` in the client's language: links, how to use the library and the artifact, known limitations (for example «in Figma a slider shows one fixed position»), the font swap step if a stand-in was used.
6. Remind the user to grant the client access to the artifact and the Figma file. 🧑 Delivery.

## Outputs
- `design/handoff/README.md`; QA evidence in `progress.md`.

## Gate
- Sweep OK, audit ok on every page, reviewer findings fixed or accepted by the user, handoff written; the user confirms delivery.

## Skills and agents
- `auditing-accessibility`, `hallmark` audit; agent `studio-design-reviewer`.

## Pitfalls
- Known limitations go into the handoff, not into silence.
```

`references/stage-09-revisions.md`:

```markdown
# Stage 9 · Revision rounds 🧑

## Inputs
- The client's list as received, `CLIENT.md` (rounds included), `design/decisions.md`, `design/brief/tz-analysis.md`, `~/job/studio-design/docs/rules/client.md`.

## Steps
1. Create `design/revisions/round-NN/source/` with the list as received and `round-NN.md` with a table: number, where (registry ID), request, the client's words.
2. Triage every item: ✅ accept, 🔁 accept with a change, ⚠️ push back (reason, evidence, alternative), ❓ question, 💰 outside the package; add its impact (which tokens, components, screens change).
3. Dispatch `studio-design-reviewer` for a second opinion on UX risk; merge its view.
4. Run `grilling` with the user over ⚠️, ❓ and 💰 items (output file `design/decisions.md`).
5. Write the reply to the client in their language; the user sends it. 🧑 Wait for confirmation.
6. Implement: code, sweep, Figma, audit; before and after screenshots.
7. Close the round in `round-NN.md` with the status of every item; add repeating patterns to `~/job/studio-design/docs/lessons.md`.
8. Count the rounds against `CLIENT.md`; when the included rounds are used up, tell the user the next round is a new order.

## Outputs
- `design/revisions/round-NN.md`, `round-NN/source/`, updated code, Figma and artifact.

## Gate
- Every item has a final status; sweep OK and audit ok after the changes; the client confirmed the reply.

## Skills and agents
- `grilling`; agent `studio-design-reviewer`.

## Pitfalls
- Never implement a UX-breaking request silently; never refuse silently (`rules/client.md`).
```

- [ ] **Step 6: Run the tests**

Run: `cd ~/job/studio-design && bash tests/test_validate.sh`
Expected: `PASS test_validate.sh` (`validate.sh` checks only the agents that exist; Task 14 adds them).

- [ ] **Step 7: Commit**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Studio Design Skill And Stage References"
```

---

### Task 14: Agents

**Files:**
- Create: `agents/tz-analyst.md`, `agents/studio-design-reviewer.md`, `agents/studio-design-figma-builder.md`

**Interfaces:**
- Consumes: stage references (Task 13), `figma/prelude.js`, `figma/audit.js` (Tasks 9–10), `docs/rules/figma.md` (Task 12).
- Produces: three agents that `validate.sh` accepts (`name` = file name, `description`, `model: opus`).

- [ ] **Step 1: Write `agents/tz-analyst.md`**

```markdown
---
name: tz-analyst
description: Extracts facts from a client brief (TZ) into a structured analysis — screen and component registry with the brief's own IDs, states, data types and formats, constraints, contradictions and gaps with page references. Also answers fact lookups for the grilling skill. Never decides and never fills gaps with guesses.
tools: Read, Grep, Glob, Bash, Write
model: opus
---

You read a client's brief and report facts. You never decide, never recommend a design, never
contact anyone, never edit anything outside the output path you are given.

## Input (from the dispatch prompt)

- The brief files (PDF, DOCX, MD, images) and, for PDFs, the extracted `pages/<pdf-stem>/page-NNN.txt` and `.png` (one folder per PDF).
- The output path, normally `design/brief/tz-analysis.md`.

## Output

Write the output file with these sections, each item with a page reference `(<file>, p. N)`:

1. **Summary** — product, audience, platform, what is delivered.
2. **Screen registry** — every screen and state, with the brief's IDs (for example S-01, P-07).
3. **Component registry** — every UI element the brief names, with its IDs (for example UI-13), variants and states.
4. **Data** — every value shown: type (money, percent, count, text), units, formats, ranges, examples.
5. **Constraints** — resolutions, platforms, fonts, brand, legal, accessibility, deadlines.
6. **Contradictions** — places where the brief disagrees with itself, quoted with both page references.
7. **Gaps** — what a designer needs and the brief does not say.

For a fact lookup (from grilling), answer only the question, with page references, or say the
brief does not contain it.

End with a three-line report: pages read, items per registry, open gaps count.
```

- [ ] **Step 2: Write `agents/studio-design-reviewer.md`**

```markdown
---
name: studio-design-reviewer
description: Independent reviewer for the studio-design pipeline — checks directions, components, screens, the whole project and client revision items against the brief registry, states, UX, accessibility and anti-slop rules. Reports ranked findings with evidence; never fixes anything.
tools: Read, Grep, Glob, Bash, mcp__Claude_Browser__preview_start, mcp__Claude_Browser__navigate, mcp__Claude_Browser__get_page_text, mcp__Claude_Browser__read_page, mcp__Claude_Browser__computer, mcp__Claude_Browser__javascript_tool, mcp__Claude_Browser__resize_window
model: opus
---

You review; you never edit files, publish, or decide. The dispatcher decides what to fix.

## Input (from the dispatch prompt)

- What to review: directions, a component batch, screens, the whole project, or a revision round file.
- Paths: `design/brief/tz-analysis.md`, the harness URL and preview names (take your own screenshots in the browser), `design/revisions/round-NN.md` when reviewing a round.
- Rules: `~/job/studio-design/docs/rules/design.md`, `docs/profiles/<profile>.md`, the `hallmark` rules.

## What to check

- Coverage: every registry item in scope exists, with every state the brief names.
- States: default, hover, focus, pressed, disabled; loading, error, success where they apply.
- Fit: nothing overflows at the profile's target sizes; one primary action per view.
- Data: values come from the fixtures and follow `docs/rules/numbers-and-locale.md`.
- Accessibility: contrast AA, touch targets, visible focus.
- Slop: `hallmark` anti-patterns (generic layouts, invented metrics, decoration without purpose).
- Revision items: for each item, whether it breaks UX, consistency, the brief or accessibility, and a better alternative.

## Output

Findings ranked by severity (blocker, major, minor). Each: where (registry ID, file or screen),
what is wrong, evidence (measurement, the preview or node you looked at, brief page, rule), a suggested fix.
End with counts per severity. If nothing is wrong, say so and list what you checked.
```

- [ ] **Step 3: Write `agents/studio-design-figma-builder.md`**

```markdown
---
name: studio-design-figma-builder
description: Builds one batch of the studio-design Figma library at a time (variables, a component set, or a screen) from the coded design system, following the pipeline's Figma rules; runs the page audit after the batch and returns node IDs, audit output and screenshots. Never runs in parallel with another Figma call and never edits code.
model: opus
---

You build one batch in Figma and prove it is clean. You never edit code, never publish the
artifact, never decide design questions — report them.

## Input (from the dispatch prompt)

- The batch: which components or screens, their code paths (`design/ds/project/components/<Name>/`), preview names.
- The Figma file key and target page names.
- `design/figma/figma-state.json`, `design/figma/prelude.js`, `design/figma/prelude.project.js`, `design/figma/audit.js`, `design/ds/fixtures/formatted.json`.
- `~/job/studio-design/docs/rules/figma.md` — read it first, every time.

## Procedure

1. Load the `figma:figma-use` skill (plus `figma-generate-library` for components, `figma-generate-design` for screens).
2. Read `figma-state.json`; reuse existing pages, components and IDs.
3. One mutating `use_figma` call at a time: paste `prelude.js` (and `prelude.project.js`) before your code; one component set or one screen per call; return every created and mutated node ID.
4. Values in texts come from `formatted.json`, never typed.
5. After the batch, run `audit.js` on every touched page (`return await auditPage('<pageId>')`; these read-only calls may run in parallel). Fix and re-audit until every count is 0.
6. `get_screenshot` of every new set and screen.
7. Update `figma-state.json` (IDs, decisions, completed steps) and the page's Doc frame.

## Output

- Node IDs created and changed, per page.
- The audit result per page (paste the returned JSON).
- The names of the sets and screens you took a `get_screenshot` of, each with what you saw (screenshots are not files; the name and verdict are the evidence).
- Anything you could not do, and why (for example an override the API refuses).
```

- [ ] **Step 4: Validate and commit**

Run: `cd ~/job/studio-design && scripts/validate.sh`
Expected: `ok   skill studio-design`, `ok   agent` × 3, `ok   stage-00` … `ok   stage-09`, exit 0.

```bash
cd ~/job/studio-design && git add -A && git commit -m "Add Pipeline Agents"
```

---

### Task 15: Install on this machine and run every check

**Files:**
- Modify: none (installation and checks only; fix any failure in the task that owns the file)

- [ ] **Step 1: Install**

Run: `~/job/agent-skills/install.sh && ~/job/studio-design/scripts/install.sh`
Expected: `ok grilling (already linked)`; `linked` for `studio-design` and the three agents.

- [ ] **Step 2: Preflight**

Run: `~/job/studio-design/scripts/preflight.sh`
Expected: `PREFLIGHT OK`. For any ❌, run its fix and repeat; paste the final output into the task report.

- [ ] **Step 3: Full test run and validation**

Run: `cd ~/job/studio-design && tests/run.sh && scripts/validate.sh && cd ~/job/agent-skills && ./validate.sh && bash tests/test_validate.sh`
Expected: `ALL TESTS PASS`, validate exit 0 in both repositories, `PASS test_validate`.

- [ ] **Step 4: Commit any fixes**

```bash
cd ~/job/studio-design && git status --short && git add -A && git commit -m "Fix Issues Found By The Full Check"
```

(Skip the commit when `git status --short` is empty.)

---

### Task 16: Verify against Mayor Sim and a test Figma file

**Files:**
- Modify: `template/design/figma/audit.js` and `tests/js/audit.test.js` only if a false positive is found (a new test reproduces it first); `template/design/ds/scripts/sweep.js` and `tests/js/sweep.test.js` likewise.

- [ ] **Step 1: Audit the Mayor Figma file read-only**

In one message, one read-only `use_figma` call lists the pages of file `NcLeuYB80bCP3OAeY2qIlh` (`return figma.root.children.map(p => [p.id, p.name])`). Then, in one message, one read-only call per page (parallel is allowed for read-only): the full text of `template/design/figma/audit.js` followed by `return await auditPage('<pageId>');`.
Expected: `ok: true` on every page. For each finding: if it is a real defect, list it for the user (fix in the Mayor file only after the user agrees); if it is a false positive, add a failing case to `tests/js/audit.test.js`, fix `audit.js`, rerun `node --test tests/js/audit.test.js`, and re-audit that page.

- [ ] **Step 2: Audit seeded defects in a test file**

Ask the user to create an empty Figma design file for pipeline tests and share its URL (never a client file). In it, one mutating `use_figma` call creates on a page «Audit seeds»: a component set with two overlapping variants, a variant whose TEXT layer has no property reference while its sibling has one, a BOOLEAN property no layer uses, a frame named `Frame 1` with an unbound SOLID fill, a text without a text style, and a text wider than its `clipsContent` parent. Then run `audit.js` on that page.
Expected: `overlappingVariants`, `refMismatch`, `unusedProps`, `defaultNames`, `unboundPaints`, `unstyledText`, `clippedText` each ≥ 1. Record the file URL in `docs/manifest.md` › Environment as «pipeline test Figma file».

- [ ] **Step 3: Sweep the Mayor harness from a copy**

```bash
t="$(mktemp -d)" && mkdir -p "$t/ds/scripts" "$t/ds/upload" \
  && cp -R ~/job/mayor-sim-design/ds/project "$t/ds/project" \
  && cp ~/job/mayor-sim-design/ds/upload/*.jpg "$t/ds/upload/" \
  && printf '{"90828d6280b2890abde32fdec8061d0b": "city-concept.jpg", "47886efcece29273c4fb6622a7adffd2": "reception-concept.jpg"}\n' > "$t/ds/upload/blobs.json" \
  && cp ~/job/studio-design/template/design/ds/scripts/{build_harness.py,sweep.js} "$t/ds/scripts/" \
  && python3 "$t/ds/scripts/build_harness.py" --ds "$t/ds" && echo "$t"
```

Serve `$t/ds` on a free port (`python3 -m http.server <port> --bind 127.0.0.1 --directory "$t/ds"` in the background), open `http://localhost:<port>/harness/_sweep.html` in the built-in browser, wait until the title starts with `SWEEP`, read `#result` with `get_page_text`.
Expected: first line `SWEEP OK: 57 pages, 0 errors, 0 overflows, 0 empty`. A reported overflow is either a real Mayor defect (list it for the user) or a false positive (add a failing case to `tests/js/sweep.test.js` when it is in the pure rule, fix `sweep.js`, rebuild, re-run). Stop the server and delete `$t` afterwards.

- [ ] **Step 4: Commit any fixes**

```bash
cd ~/job/studio-design && git add -A && git commit -m "Tune Audit And Sweep Against Mayor Sim"
```

(Skip when nothing changed.)

---

### Task 17: Pilot stages 0–3 on a sample brief

**Files:**
- Create: `tests/pilot/brief.md`
- Modify: whatever the pilot shows is wrong, in the file that owns it, plus `docs/lessons.md`

- [ ] **Step 1: Write the sample brief** `tests/pilot/brief.md`

```markdown
# Бриф: лендинг подписки на кофе «Зерно по средам»

Обжарщик кофе из Казани запускает подписку: раз в неделю или раз в две недели курьер привозит
свежеобжаренное зерно. Нужен лендинг (desktop 1440 и мобильный 375) и дизайн-система для него.

Экраны:
- L-01 Первый экран: заголовок, подзаголовок, кнопка «Оформить подписку», фото пачки кофе.
- L-02 Как это работает: три шага.
- L-03 Тарифы: «Раз в неделю» 1 490 ₽ за 250 г, «Раз в две недели» 1 590 ₽ за 250 г, «Офис» от 5 900 ₽ за 1 кг; один тариф отмечен как популярный.
- L-04 Отзывы: три отзыва (тексты пришлёт клиент).
- L-05 Вопросы и ответы: 6 вопросов, раскрываются по клику.
- L-06 Форма заявки: имя, телефон, адрес, выбор тарифа; ошибки валидации; успешная отправка.
- L-07 Подвал: контакты, соцсети.

Бренд: логотипа пока нет, цвета не заданы; хочется «тепло, но не банально, без коричневого».
Шрифты: бесплатные, с кириллицей.
Срок: две недели.
```

- [ ] **Step 2: Run the pilot**

Run: `~/job/studio-design/scripts/new-client.sh pilot-coffee --name "Зерно по средам (пилот)"` and copy `tests/pilot/brief.md` into `~/job/clients/pilot-coffee/design/brief/`. In the desktop app, open `~/job/clients/pilot-coffee/design` and run «studio-design: stage 0», then stages 1, 2 and 3 with the user acting as the client, package «ДС», profile web-landing, entry mode «from scratch». Use the test Figma file from Task 16 as the Figma file.
Expected: each stage's gate passes with evidence in `progress.md`; `tz-analysis.md` lists L-01…L-07; `questions.md` has recommended answers; `layout-budget.md` has measured numbers at 1440 and 375.

- [ ] **Step 3: Fold the findings back**

For every problem the pilot shows (a missing input path, an unclear step, a script failure), fix the owning file in `~/job/studio-design` (with a test when it is a script) and add a line to `docs/lessons.md`. Run `tests/run.sh && scripts/validate.sh`.
Expected: `ALL TESTS PASS`, validate exit 0.

- [ ] **Step 4: Clean up and commit**

Ask the user before deleting the pilot container; after a yes: `rm -rf ~/job/clients/pilot-coffee`.

```bash
cd ~/job/studio-design && git add -A && git commit -m "Apply Pilot Findings"
```
