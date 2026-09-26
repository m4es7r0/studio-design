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
