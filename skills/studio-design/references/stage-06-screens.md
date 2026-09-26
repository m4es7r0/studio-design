# Stage 6 · Screens (code)

## Inputs
- `design/brief/tz-analysis.md` (screen registry), `design/brief/layout-budget.md`, the components, `design/ds/fixtures/formatted.json`.

## Steps
1. Package «ДС»: the 1–2 templates from the layout budget. Package «ДС + экраны»: every screen and state in the registry.
2. Build each screen as a preview page with the `page` card marker and its width; every value from the fixtures; mark its rails, zones and free areas with `data-zone="<zone name>"`.
3. Measure every screen at every target size with `harness/_measure.html?page=<Name>&w=<W>&h=<H>` (wait until the page title starts with `MEASURE`, then `get_page_text`); paste the first line and the JSON of every run into `progress.md`.
4. Sweep, look, publish; dispatch `studio-design-reviewer` on the screens.

## Outputs
- Screen preview pages; measurements in `progress.md`; a published artifact version.

## Gate
- Every `_measure.html` run prints `MEASURE OK` (every screen fits at every target size; first line and JSON pasted in `progress.md`); the sweep is OK.

## Skills and agents
- Agent `studio-design-reviewer`.

## Pitfalls
- A screen that does not fit changes components, not the budget, unless the user decides otherwise in `decisions.md`.
