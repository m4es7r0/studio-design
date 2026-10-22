# Stage 6 · Screens (code)

## Inputs
- `design/decisions.md` (the named list of screens and states from stage 1), `design/brief/tz-analysis.md` (screen registry), `design/brief/layout-budget.md`, the components, `design/ds/fixtures/formatted.json`, `design/PROJECT.md` (switches).

## Steps
1. Build exactly the screens and states named at stage 1 (package «ДС»: the key templates; «ДС + экраны»: every screen and state in the registry).
2. Invoke `attmpt-design` for each screen: a preview page with the `page` card marker and its width; every value from the fixtures; rails, zones and free areas marked with `data-zone="<zone name>"`. A screen defines no reusable part of its own: a missing part goes back to stage 5 (lesson 28).
3. Measure every screen at every target size with `harness/_measure.html?page=<Name>&w=<W>&h=<H>` (wait until the page title starts with `MEASURE`, then `get_page_text`); paste the first line and the JSON of every run into `progress.md`. On profiles whose pages scroll (web-landing, web-product, mobile), measure the full page with `h=auto` (width only), and use a fixed `h` only for zones that must stay inside the viewport (shell, rails, sticky bars, the first screen); mark only those zones with `data-zone` on the fixed-height run, or run the fixed-height check on a preview of that part alone.
4. Sweep and look; publish only with `Artifact: yes`; dispatch `studio-design-reviewer` (payload: SKILL.md › Skills and agents) on the screens, within `Review passes:`.

## Outputs
- Screen preview pages; measurements in `progress.md`; with `Artifact: yes`, a published artifact version.

## Gate
- Every `_measure.html` run prints `MEASURE OK` (every screen fits at every target size; first line and JSON pasted in `progress.md`); the sweep is OK; every screen named at stage 1 exists.

## Skills and agents
- `attmpt-design`; agent `studio-design-reviewer`.

## Pitfalls
- A screen that does not fit changes components, not the budget, unless the user decides otherwise in `decisions.md`.
- `docs/lessons.md` 22 (named scope) and 28 (no screen-local parts).
