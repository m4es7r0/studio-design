# Stage 3 · Layout budget

## Inputs
- `design/brief/tz-analysis.md` (screen registry), the chosen direction, `~/job/studio-design/docs/profiles/<profile>.md`, `design/ds/fixtures/`.

## Steps
1. Pick the 2–3 densest screens named in the profile's «Layout budget» line.
2. Build them in code as zone boxes (plain blocks with the zone name and size) at the target sizes, with the longest labels and the largest values from the fixtures; add them as preview pages (`ds/previews_spec.py`, `gen_previews.py`, `build_harness.py`).
3. In the browser, measure every zone (`getBoundingClientRect`) at every target size; paste the numbers into `design/brief/layout-budget.md` with the zone sizes the components must respect.

## Outputs
- `design/brief/layout-budget.md`, the layout-budget preview pages.

## Gate
- Every zone fits its screen at every target size; the measured numbers are pasted.

## Skills and agents
- Platform skills from the profile (`mobile-design-patterns` for mobile).

## Pitfalls
- `docs/lessons.md` 1: this stage exists because S-08 did not fit 1080 at the end.
