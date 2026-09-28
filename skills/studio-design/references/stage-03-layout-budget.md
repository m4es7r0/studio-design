# Stage 3 · Layout budget

## Inputs
- `design/brief/tz-analysis.md` (screen registry), the chosen direction, `~/job/studio-design/docs/profiles/<profile>.md`, `design/ds/fixtures/`, `design/ds/fixtures/sample.json`.

## Steps
1. Fill `ds/fixtures/sample.json` with the brief's longest names and largest values from `design/brief/tz-analysis.md` (Data section) and run `npm run fixtures`.
2. Pick the 2–3 densest screens named in the profile's «Layout budget» line.
3. Build them in code as zone boxes (plain blocks with the zone name and size) at the target sizes, with the longest labels and the largest values from the fixtures; every zone carries `data-zone="<zone name>"`. Add them as preview pages (`ds/previews_spec.py` with `group="Layout budget"` in their `@dsCard` attributes, `gen_previews.py`, `build_harness.py`).
4. Start the harness (`preview_start` ds-harness). Measure every preview at every target size with `harness/_measure.html?page=<Name>&w=<W>&h=<H>`: wait until the page title starts with `MEASURE`, then `get_page_text`. Paste the first line and the JSON of every run into `design/brief/layout-budget.md` with the zone sizes the components must respect. On profiles whose pages scroll (web-landing, web-product, mobile), measure the full page with `h=auto` (width only), and use a fixed `h` only for zones that must stay inside the viewport (shell, rails, sticky bars, the first screen); mark only those zones with `data-zone` on the fixed-height run, or run the fixed-height check on a preview of that part alone.

## Outputs
- `design/brief/layout-budget.md`, the layout-budget preview pages.

## Gate
- Every `_measure.html` run prints `MEASURE OK` (every zone fits its screen at every target size); the first line and the JSON of every run are pasted in `design/brief/layout-budget.md`.

## Skills and agents
- Platform skills from the profile (`mobile-design-patterns` for mobile).

## Pitfalls
- `docs/lessons.md` 1: this stage exists because S-08 did not fit 1080 at the end.
