# Backlog

Open work on the pipeline. The SDD ledger (`.superpowers/sdd/…/progress.md`, git-ignored) keeps the history
and the rulings; this file is the list to act on. Work an item through the usual flow: plan, the user's
approval, tests and `validate.sh`, commit. Remove an item when it lands.

## 1. Fonts in Figma — review of pilot fold-back part 2 (2026-09-28)

Findings from the capture `docs/figma-font-families.json`: of the 10 «no» cells in `docs/fonts-cyrillic.md`,
3 are naming differences, all in the Fail list (the «44 of 46» figure stands): M PLUS Rounded 1c is
«Rounded Mplus 1c» (Bold is a separate family «Rounded Mplus 1c Bold»); Noto Sans Display and Noto Serif
Display are «Display …» styles of «Noto Sans» and «Noto Serif». The other 7 are real absences.

Fixes, no behaviour change:
- `rules/figma.md`: filter the font list by a distinctive word of the name, not the exact name; before calling
  a face missing, look for it under another name and among the styles of its base family (the two examples).
  The 20 KB filter rule makes this urgent: an exact filter misses «Rounded Mplus 1c».
- `cyrillic_fonts.py` Method text (then regenerate `fonts-cyrillic.md`, needs Google): «yes» and «no» match the
  family name only; «no» may be a naming difference; the stage 2 check decides.
- Drop `"?????": ["??"]` from the capture (a non-Latin family name lost in transport); manifest: drop names that
  arrive as question marks when refreshing.
- `stage-04-foundations.md` step 3: for «existing DS» the Figma check was at stage 0, family only (Preflight
  table), so stage 4 confirms every weight it ships.
- Test the in-repository branch of `load_figma` (patch `REPO` to a temporary folder).

Decisions needed (behaviour changes), recommended answer first:
- Q1. Teach the script other Figma names? **A: text only** (all such faces fail anyway, the live check decides)
  / B: base family + style prefix and an alias table. Either way the Figma name found goes into the direction
  file, and stage 7 builds text styles with it.
- Q2. A client font that is not on Google («existing DS», «brand book»). **A: the artifact ships the client's
  files when the licence allows web embedding (same `font_check.py`; the licence is a Materials question in
  `questions.md`); Figma always uses a Google stand-in** / B: a Google stand-in in the artifact too.
- Q3. A weight missing in Figma at stage 2. **A: replace the face, or take the nearest weight present on the
  web and in Figma, before the client sees it; a face fixed by the brand book stays, with the Figma stand-in
  named in the direction card** / B: always show as is and name the stand-in.

## 2. Likely to bite on a client run

Pulled from section 3; fix these before the rest.
- `sweep.js`: a page that was never measured passes (404, missing `#root`, load timeout, zero pages → SWEEP OK).
- `format`: tiny values print a signed zero (`−0 ₽`); scaled numbers of 1000+ lose the U+202F thousands space;
  an unknown scale name prints `null ₽`.
- `new-client.sh`: a failure after `cp -R` leaves a half-built container that blocks a rerun.
- Non-Russian clients: `font_check.py` requires Cyrillic and ₽, and `rules/numbers-and-locale.md` and the stage 3
  fixtures assume ru-RU, so an English-only product narrows its font choice for nothing and the stage 4 locale
  decision comes after the fixtures that use it.
- Package «ДС + код для разработки» is not built: a redesign of a coded product has no stage that maps the
  tokens onto the product's theme (for example shadcn CSS variables) and hands them to development.

## 3. Deferred minors from the build

Copied from the SDD ledger as recorded (2026-09-26 … 2026-09-28). Some may be fixed since: check before working
on one.

### `grilling` fork and `validate.sh` (repository agent-skills) (Task 1)

- grilling Output file option has no «caller's format» clause (callers state the table format today).
- Client questions option lacks append/placement rule (questions.md «## Open»).
- client-deferred items and the frontier rule unstated.
- example names `tz-analyst` inside a project-agnostic skill; Cyrillic «ок» in an English file.
- validate.sh passes on an empty/missing root; frontmatter parsing edge cases; three failure branches untested.
- one commit bundles the grilling change with validation files.

### Skeleton, test runner, `install.sh` (Task 2)

- AGENTS.md commit rule lacks «no trailing period».
- test_install does not cover a foreign or dangling symlink conflict (-L branch) or the agents-side conflict.
- re-run test asserts output only, not the link again.
- install.sh link ownership is a path-string match (symlinked checkout reports its own links as foreign; fails safe).

### `pdf_pages.py` (Task 3)

- pdf_pages.py never closes the document (use a with block).
- image extraction has no per-image error handling and ignores the soft mask.
- re-extracting into an existing folder leaves stale page files.
- missing or password-protected PDF gives a raw traceback.
- tests do not cover images=False, the CLI, the CMYK branch, page-002.png or the scripts/py exit-3 contract.
- path-label comments at the top of tests/py/helpers.py and test_pdf_pages.py.
- the 1.24.3 floor for the `pymupdf` module name is not verified against the oldest release (1.28.2 installed and works).

### Client template, `new-client.sh` (Task 4)

- --port is not validated (non-numeric writes invalid JSON).
- a failure after cp -R leaves a half-built client that blocks a rerun (no cleanup trap).
- sibling-port scan and its test depend on the exact `"port": N }` formatting.
- test_new_client lacks auto-port, --name default, other exit-2 cases, and JSON-parse checks after substitution.
- unused `out` variable in test_new_client.sh.

### `format` and fixtures (Task 5)

- scaled numbers of 1000+ lose the U+202F thousands space (inherited from Mayor).
- tiny values print a signed zero (−0 ₽, +0 ₽) instead of 0 (inherited).
- unknown scale name prints `null ₽`.
- literal U+202F/U+00A0 in check_format.js and format.test.js (plan-mandated) — prefer escapes.
- DS README examples typed with ASCII spaces.
- tests/js makeClient leaks temp dirs (plan-mandated).
- format test does not cover an item without delta (null branch) or names of all items.

### `gen_previews.py`, `build_harness.py` (Task 6)

- build_harness html/head rewrites fail silently on unusual tags (no injection, no warning).
- blob rewrite is substring replacement (prefix ids).
- only themes[0] is emitted; a second theme is never exercised.
- gen_previews unknown name → bare KeyError, possibly after partial writes.
- gen_previews does not strip leading/trailing newlines of the JS body (Mayor did).
- INJECT goes before <meta charset> (safe within the 1024-byte prescan today).
- no unit test for token_css ({ref}, fonts, groups, families) or gen_previews names/--lang.

### `sweep.js` (Task 7)

- a page never measured passes (404 / missing #root, load timeout without onload, zero pages → SWEEP OK).
- TOL 4 equals the pressed-state translate exactly.
- the DOM path of sweep.js has no automated test beyond the pure helpers.
- in-flow pseudo-element text overflow (and long <input> values) now suppressed.
- inFlowFits compares to the border-box right while the gate uses the padding box (up to TOL + border suppressed).
- leftward (RTL) overflow suppressed.
- plan text for Task 7 still shows the old absoluteOnly code and exports (code superseded by f578aa7).

### `font_check.py` (Task 8)

- TTFont never closed (ResourceWarning under -X dev).
- tests print ❌/✅ lines into the suite output.
- --extra count and label wrong for repeats or already-required code points.
- bad --extra or unreadable font exits 1 like a coverage failure.
- no woff2 or multi-font test.
- test import leaves template/design/fonts/__pycache__ copied into new clients on disk.

### Figma `prelude.js` (Task 9)

- resolve() reads the first mode, not the collection default mode.
- duplicate variable names across collections are silently dropped by the name map.
- all text-style fonts load up front (one missing font breaks every call).
- paint() does not check resolvedType COLOR; dangling alias gives a raw TypeError.
- doc() untested; long title can exceed width.
- prelude tests miss direct colour, effectStyle success, font dedup.
- template/design/figma/prelude.project.js names Mayor Sim and its local path, and new-client.sh copies it into every client container — conflicts with keeping one client's references out of another's container.
- suite output carries ❌/✅ lines from the font-check tests (Task 8).

### Figma `audit.js` (Task 10)

- only the nearest clipping ancestor is checked.
- auditPage switches the user's current page (page.loadAsync would not).
- walk descends into instance subtrees needlessly (slow on big files).
- SECTION fills/names and UI-default component-set strokes would count as unbound paints/default names — policy undecided.
- mixed-fill text skips the paint check.
- refMismatch compares to the first variant seen, can blame the wrong one.
- box() falls back to relative x/y when absoluteBoundingBox is null.
- DEFAULT_NAME misses Union, Subtract, Intersect, Exclude, Slice, Arrow.
- no auditPage shape/cap/No-page test; weak count-only assertion; no negative clippedText, stroke or hidden-paint cases.
- getStyledTextSegments stubs ignore their argument (wrong field list would pass tests).

### `preflight.sh` (Task 11)

- ✅ line names three Figma skills but checks only figma-use (any cached version).
- the «everything present» half of the test depends on the host's node, npx, git identity, lsof.
- test asserts only 3 fix routings, not design-agent/design-scout/fallback/Figma or the FAIL count.
- default python path duplicated from scripts/py.
- git identity check reads repo-local config; fix text says global.

### Docs: manifest, playbook, rules (Task 12)

- numbers doc examples use ASCII spaces.
- «percent below 10 keeps one decimal» imprecise (only when fractional; ≥10 rounds).
- manifest session tools lack a Fix column and the Figma-runtime fonts row; auditing-accessibility source is its own install path.
- playbook setup list omits design-intelligence-agent install and the Figma plugin.
- mobile sizes are iPhone 14/15 generation; label as studio defaults.
- only the artifact gets a privacy reminder, not the Figma file.

### Skill and stage references (Task 13)

- bare `docs/…`, `rules/…`, `CLIENT.md` paths ambiguous from `design/` (no convention line for them).
- access reminder only at stage 8, not at every checkpoint.
- stage 2 may create the artifact but omits rules/artifact.md (which says create at stage 4).
- some inputs not named as files (chosen direction, components, stand-in font record, stage 2 profile file).
- stage 0 checks differ from manifest «Check at stage 0»; Figma URL not recorded in CLIENT.md links table.
- stage 8/9 confirmation evidence location unstated; stage 9 writes to studio lessons without restating the no-client-names rule and the commit.
- stage 4 font gate cannot pass for non-Russian clients (hard-coded Cyrillic and ₽).
- validate.sh silent on a missing studio-design SKILL.md; no bad-skill-frontmatter test.
- stage-09 step 6 «before and after screenshots» should use the names+verdicts form in round-NN.md.
- stage-02 redesign screenshots should say the client or user supplies them.
- stage-02 step 4 lacks an explicit «show existing-ds.md, record confirmation» step.
- SKILL.md «Evidence is pasted» vs written verdicts wording.
- stage-05 steps/outputs do not say to write preview names with verdicts to progress.md.
- existing-DS gaps — stage 7 lacks existing-ds.md input; stage 3 «chosen direction» has no counterpart; imported tokens into tokens.json unstated.
- stage 3 fixtures use ru-RU format before the stage-4 locale decision.
- plan Task 13 text no longer byte-identical to the fixed files (plan historical).

### Agents (Task 14)

- reviewer cannot look at Figma or the artifact directions page (scope unstated).
- figma-builder names figma-generate-library / figma-generate-design without the `figma:` prefix.
- figma-builder description says it returns screenshots (contradicts names+verdict output).
- suite output noise from font-check fixtures (Task 8).

### Verification on Mayor Sim (Task 16)

- default variant names like `Property 1=Default` are not flagged by DEFAULT_NAME.

### Final review of the build (ledger)

- `_sweep.html` title `sweeping…` still starts with «sweep» case-insensitively.
- stage 8 contrast «measured in the harness» has no committed script (rules forbid ad hoc checks).
- SKILL.md «only write into studio-design is a lesson» vs setup-python.sh building .venv there.
- SKILL.md absolute-path example uses `~`.
- «sweep page appears at stage 5» stale (harness exists from stage 3); lesson 2 still says «stage 0 font check»; spec §4 tree and §9 list lack measure.js; test_preflight still stubs auditing-accessibility.

### Pilot fold-back, part 1 (ledger)

- font that fails to load goes unnoticed (fonts.load empty list; measure ignores __errs).
- stage 2 step 7 does not say to put all three directions' faces in FONT_LINKS/FONT_LOADS.
- questions headings language vs English names in references; grilling Materials items have no recommended answer.
- «existing DS skips stage 2» wording inaccurate.
- stale FIXTURES in previews not regenerated.
- escape every `<` in embedded JSON.
- string-level tests for fontsReady/rethrow; render()/check_family() untested.
- stage 4 step 3 lacks `mkdir -p ds/project/fonts fonts/src`, a download URL pattern, multi-axis/italic files, and a build_harness rerun; manifest lacks the GitHub host; weight naming differs from the artifact.md example; cyrillic_fonts.py PEP 8 blank line and --limit/--out ignored with --family.

## 4. Gaps found preparing the first real run (2026-09-30)

A redesign of a coded product with an English UI, both themes and no Figma. The run's prompt works around each
of these; fix them in the pipeline before the next such client.
- Both themes: `build_harness.py` emits only `color.themes[0]` and a token has one value; aliased tokens resolve
  on `:root`, so a `dark` class on `#root` does not recolour them. Workaround: literal `oklch()` tokens, a `.dark`
  block in `bundle.css`, and a `<Name>Dark` twin of every preview. Fix: a real second theme in tokens, harness,
  sweep, measure and the artifact.
- No committed contrast script, although stages 2, 4 and 8 need figures (rules forbid ad hoc checks). Workaround:
  a client copy of a small oklch → WCAG script. Fix: `ds/scripts/contrast.py` in the template, reading tokens and
  the dark block.
- Locale: `format`, fixtures and `gen_previews.py` default to ru-RU, and the directions page (stage 2) already
  uses them, so a non-ru locale decided at stage 4 comes too late. Fix: decide the locale at stage 0 and ship an
  en-US `format` variant.
- Packages: «ДС» allows 1–2 layout-budget templates, but a redesign owner may want specific key screens; and
  there is still no «ДС + код» stage. Workaround: a recorded deviation plus `handoff/code-mapping.md`
  (token → CSS variable, component → kit component, screen → route). Fix: a package with named key screens and a
  code-mapping handoff.
- `studio-design-reviewer` does not read `decisions.md`, so accepted deviations (locale, density, scope) come back
  as findings. Fix: add `decisions.md` and the package scope to its payload in SKILL.md.
- Entry mode «redesign» allows one direction; an owner may want 2–3 on a fixed base. Fix: let the owner choose.
- Figma is woven into stage 0 outputs, stage 2 and 4 font checks, stage 7 and stage 8 (`audit.js`); a no-Figma
  project needs a single «no Figma» switch instead of accepting ❌ one by one.
- Redesign before/after screenshots: the run built a reusable Playwright capture script (pages, widths, states,
  read-only, skips «new» items). Fix: a template `refs/capture.mjs` with a per-project route list.
- Web-product profile: fields 40–44 px conflicts with compact kit presets (shadcn Mira 28 px); record density as
  a stage 2 decision instead of a fixed profile value.
