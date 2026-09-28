# Stage 4 · Foundations

## Inputs
- The chosen direction, `design/brief/layout-budget.md`, `design/ds/project/*`, `~/job/studio-design/docs/rules/{design,numbers-and-locale,artifact}.md`, `~/job/studio-design/docs/fonts-cyrillic.md`.
- `design/directions/existing-ds.md` (entry mode «existing DS»: build only what it lists as missing).

## Steps
1. If the artifact does not exist yet (entry mode «existing DS» skips stage 2), create it now as in stage 2 step 1.
2. Write tokens (`tokens.json`, format in `docs/rules/artifact.md` › File formats), the root class and base styles (`bundle.css`), README principles; set `ROOT_CLASS` in `ds/previews_spec.py`.
3. Fonts: take the chosen faces from the full family files, not from the Google Fonts CSS — its per-range woff2 files drop U+202F even from faces that have it (`~/job/studio-design/docs/fonts-cyrillic.md` › Method). Source: `https://github.com/google/fonts`, folder `ofl/`, `apache/` or `ufl/` + the family name in lower case without spaces, with its licence file. For each weight you ship: a variable TTF first gets the weight cut with `~/job/studio-design/scripts/py -m fontTools.varLib.instancer "fonts/src/<Family>[wght].ttf" wght=<W> -o fonts/src/<Family>-<W>.ttf`; then `~/job/studio-design/scripts/py -m fontTools.ttLib.woff2 compress -o ds/project/fonts/<Family>-<W>.woff2 fonts/src/<Family>-<W>.ttf`. Put the licence next to them and run `~/job/studio-design/scripts/py fonts/font_check.py ds/project/fonts/*.woff2`. Remove the chosen direction's URL from `FONT_LINKS` in `ds/previews_spec.py` (the faces now come from `type.fonts`), keep `FONT_LOADS`, and regenerate every preview. The Figma check was done for every proposed face at stage 2 (recorded in the direction file); confirm it for the chosen family: a read-only `use_figma` (load `figma:figma-use` first) with `figma.listAvailableFontsAsync()` lists every weight you ship, by its exact style name. If a weight is missing, pick a Google stand-in and record «Figma stand-in: <stand-in> for <real family>» as a `design/decisions.md` row.
4. Numbers: adjust `format` and `ds/fixtures/format-cases.json` if the locale or units differ; run `npm run check:format`.
5. Extend `ds/fixtures/sample.json` to every value type the components will show; run `npm run fixtures`.
6. Publish the style tile (`rules/artifact.md`).

## Outputs
- `tokens.json`, `bundle.css`, `README.md`, fonts, `fixtures/formatted.json`, the published style tile; the Figma stand-in row in `decisions.md` when one is needed.

## Gate
- `npm run check:format` prints `all N cases pass`; `font_check.py` prints only ✅; the style tile is published.

## Skills and agents
- `hallmark`, `artifact-design` and `artifact-capabilities` (through the quickstart), `figma:figma-use` (font confirmation).

## Pitfalls
- `docs/lessons.md` 2 and 9.
