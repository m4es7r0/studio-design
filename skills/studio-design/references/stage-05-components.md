# Stage 5 · Components (code)

## Inputs
- `design/brief/tz-analysis.md` (component registry), `design/brief/layout-budget.md`, `design/ds/project/*`, `design/ds/previews_spec.py`, `~/job/studio-design/docs/rules/design.md`.

## Steps
1. Split the registry into batches of related components; per batch:
2. Add the components to `bundle.js` and `bundle.css`, types to `index.d.ts`, a README per component, preview specs to `previews_spec.py`.
3. `python3 ds/scripts/gen_previews.py <Names>` and `python3 ds/scripts/build_harness.py`.
4. Start the harness (`preview_start` ds-harness), open `harness/_sweep.html`, read `#result`.
5. Look at every new preview in the browser; fix what looks wrong.
6. `npm run check:types`.
7. Publish the batch (`rules/artifact.md`).
8. After the last batch, dispatch `studio-design-reviewer` for registry coverage and states.

## Outputs
- Components in the bundle, previews, READMEs, types; a published artifact version per batch.

## Gate
- The sweep's first line is `SWEEP OK: … 0 errors, 0 overflows, 0 empty`; `check:types` passes; screenshots of every new preview are in `progress.md`.

## Skills and agents
- `hallmark`; agent `studio-design-reviewer`.

## Pitfalls
- Build continuous-value parts (sliders, progress) so Figma can express the value later (`rules/figma.md`).
