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
