# Stage 7 · Figma

Runs only with `Figma: yes`. With `Figma: no` the stage is skipped: record one line in `progress.md` and go to stage 8.

## Inputs
- `design/figma/figma-state.json`, `design/figma/prelude.js`, `design/figma/prelude.project.js`, `design/figma/audit.js`, `design/ds/project/*`, `design/ds/fixtures/formatted.json`, `~/job/studio-design/docs/rules/figma.md`.
- `design/decisions.md` (the «Figma stand-in» row: the Google family the Figma typography uses).

## Steps
1. Foundations: variables (colour, spacing, typography with the stand-in font from `decisions.md`), text and effect styles, named by the conventions in `prelude.js`; create the text styles `Display/title`, `Text/body` and the colour variables `text/ink`, `text/ink-2` that the Doc frames use, or edit `PRELUDE_CONFIG` in `figma/prelude.js` to name existing ones; audit the Foundations page.
2. Dispatch `studio-design-figma-builder` (payload: SKILL.md › Skills and agents) once per batch, in the order of stage 5: one component set or one screen per call, audit after each batch, node IDs back.
3. Take your own `get_screenshot` of each node ID the builder returns and record the verdict: write the names of the sets and screens looked at, with verdicts, in `progress.md`; send defects back to the builder as a new batch (payload: SKILL.md › Skills and agents). A spot-check of the screenshots is enough when the builder's audit is clean (lesson 44).
4. Templates and screens from stage 6, with fixture values and the background assets (`upload_assets`).
5. Keep `figma-state.json` current (the figma-generate-library ledger lives in the container, not in `/tmp`); one Doc frame per page.
6. If this stage's «to confirm» rows are not empty, run `grilling` with the user over them and hold a 🧑 mini-checkpoint before the gate (lesson 31).

## Outputs
- The Figma library and screens; `figma-state.json`; audit outputs and the names of the sets and screens looked at, with verdicts, in `progress.md`.

## Gate
- `audit.js` on every touched page returns `ok: true` (all counts 0); every node ID the builder returned has your own `get_screenshot`, and the names of the sets and screens looked at, with verdicts, are in `progress.md`.

## Skills and agents
- `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design`; agent `studio-design-figma-builder`.

## Pitfalls
- `docs/lessons.md` 3–8.
