# Stage 4 · Foundations

## Inputs
- The frozen sketch (`design/directions/frozen/`) and the chosen direction, `design/brief/layout-budget.md`, `design/ds/project/*`, `design/PROJECT.md` (switches, themes, locale), `~/job/studio-design/docs/rules/{design,numbers-and-locale,artifact,figma}.md`, `~/job/studio-design/docs/fonts-cyrillic.md`, `design/figma/figma-state.json` (only with `Figma: yes`, for the font confirmation).
- `design/directions/existing-ds.md` (entry mode «existing DS»: build only what it lists as missing).

## Steps
1. Only when `Artifact:` is not `no`: if the artifact does not exist yet (entry mode «existing DS» skips stage 2), create it now as in stage 2 step 1.
2. Invoke `attmpt-design` for the foundations: its Step 0 reads the frozen sketch as the existing system and extracts the tokens from it — never derive them again. It writes the tokens (`tokens.json`, format in `docs/rules/artifact.md` › File formats), the root class and base styles (`bundle.css`), the README principles; set `ROOT_CLASS` in `ds/previews_spec.py`. When `Themes:` lists a dark theme, keep its values under the same token names in a `.dark { … }` block in `bundle.css` and give every preview a `<Name>Dark` twin, until the harness supports themes (lesson 19). A font feature and an elevation token are tried on the real strings and the darkest real content before they become rules (lesson 41).
3. Fonts: take the chosen faces from the full family files, not from the Google Fonts CSS — its per-range woff2 files drop U+202F even from faces that have it (`~/job/studio-design/docs/fonts-cyrillic.md` › Method). Source: `https://github.com/google/fonts`, folder `ofl/`, `apache/` or `ufl/` + the family name in lower case without spaces, with its licence file. For each weight you ship: a variable TTF first gets the weight cut with `~/job/studio-design/scripts/py -m fontTools.varLib.instancer "fonts/src/<Family>[wght].ttf" wght=<W> -o fonts/src/<Family>-<W>.ttf`; then `~/job/studio-design/scripts/py -m fontTools.ttLib.woff2 compress -o ds/project/fonts/<Family>-<W>.woff2 fonts/src/<Family>-<W>.ttf`. Put the licence next to them and run `~/job/studio-design/scripts/py fonts/font_check.py ds/project/fonts/*.woff2`. Remove the chosen direction's URL from `FONT_LINKS` in `ds/previews_spec.py` (the faces now come from `type.fonts`), keep `FONT_LOADS`, and regenerate every preview. Only with `Figma: yes`: confirm the chosen family in a read-only `use_figma` (load `figma:figma-use` first) with `figma.listAvailableFontsAsync()` — every weight you ship, by its exact style name; if a weight is missing, pick a Google stand-in and record «Figma stand-in: <stand-in> for <real family>» as a `design/decisions.md` row.
4. Numbers: the locale was set at stage 0; `npm run check:format` still passes after the tokens.
5. Extend `ds/fixtures/sample.json` to every value type the components will show; run `npm run fixtures`.
6. Contrast figures of every text and UI pair in every theme go into `progress.md`.
7. Publish the style tile only with `Artifact: yes` (`rules/artifact.md`); with `Artifact: checkpoints` it is published at stage 8.
8. If this stage's «to confirm» rows are not empty, run `grilling` with the user over them and hold a 🧑 mini-checkpoint before the gate (lesson 31).

## Outputs
- `tokens.json`, `bundle.css`, `README.md`, fonts, `fixtures/formatted.json`; the style tile (published only with `Artifact: yes`); the Figma stand-in row in `decisions.md` when one is needed.

## Gate
- `npm run check:format` prints `all N cases pass`; `font_check.py` prints only ✅; contrast figures for every theme are in `progress.md`; with `Artifact: yes`, the style tile is published.

## Skills and agents
- `attmpt-design` (foundations), `artifact-design` and `artifact-capabilities` (through the quickstart, when `Artifact:` is not `no`), `figma:figma-use` (font confirmation, only with `Figma: yes`).

## Pitfalls
- `docs/lessons.md` 2, 9, 19 (themes), 20 (contrast from stage 2 on) and 41 (try tokens on real content).
