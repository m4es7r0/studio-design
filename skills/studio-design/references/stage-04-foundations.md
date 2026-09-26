# Stage 4 · Foundations

## Inputs
- The chosen direction, `design/brief/layout-budget.md`, `design/ds/project/*`, `~/job/studio-design/docs/rules/{design,numbers-and-locale,artifact}.md`.
- `design/directions/existing-ds.md` (entry mode «existing DS»: build only what it lists as missing).

## Steps
1. Create the artifact if it does not exist: `Artifact action=quickstart intent=other`, create from the Design System type, read its `project/design-system.json` and merge it into `design/ds/project/design-system.json`; record the URL in `PROJECT.md` and `CLIENT.md`.
2. Write tokens (`tokens.json`), the root class and base styles (`bundle.css`), README principles.
3. Fonts: put the woff2 files into `ds/project/fonts/` with the licence; run `~/job/studio-design/scripts/py fonts/font_check.py ds/project/fonts/*.woff2`. For the chosen family run a read-only `use_figma` (load `figma:figma-use` first) with `figma.listAvailableFontsAsync()`; if the family is not available, pick a Google stand-in and record «Figma stand-in: <stand-in> for <real family>» as a `design/decisions.md` row.
4. Numbers: adjust `format` and `ds/fixtures/format-cases.json` if the locale or units differ; run `npm run check:format`.
5. Extend `ds/fixtures/sample.json` to every value type the components will show; run `npm run fixtures`.
6. Publish the style tile (`rules/artifact.md`).

## Outputs
- `tokens.json`, `bundle.css`, `README.md`, fonts, `fixtures/formatted.json`, the published style tile; the Figma stand-in row in `decisions.md` when one is needed.

## Gate
- `npm run check:format` prints `all N cases pass`; `font_check.py` prints only ✅; the style tile is published.

## Skills and agents
- `hallmark`, `artifact-design` and `artifact-capabilities` (through the quickstart), `figma:figma-use` (font check).

## Pitfalls
- `docs/lessons.md` 2 and 9.
