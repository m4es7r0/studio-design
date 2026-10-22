# Stage 5 · Components (code)

## Inputs
- `design/brief/tz-analysis.md` (component registry), `design/brief/layout-budget.md` (with its layout parts), the frozen sketch, `design/ds/project/*`, `design/ds/previews_spec.py`, `design/PROJECT.md` (switches), `~/job/studio-design/docs/rules/design.md`, `~/job/studio-design/docs/profiles/<profile>.md`.
- `design/directions/existing-ds.md` (entry mode «existing DS»: build only what it lists as missing).

## Steps
1. Split the registry into batches of related components, and add the layout parts from the budget sheets before the last batch (lesson 28); per batch:
2. Invoke `attmpt-design`: its «Before code» spec is the only spec (component inventory with what each look needs from the kit, token map, states, interaction, a11y); it adds the components to `bundle.js` and `bundle.css`, types to `index.d.ts`, a README per component without class lists, preview specs to `previews_spec.py`, and registers each component in the `@ds-bundle` header and on `window.<NS>` (`docs/rules/artifact.md` › File formats). On the mobile profile its input is the mobile-design-patterns build-spec.
3. `python3 ds/scripts/gen_previews.py <Names>` and `python3 ds/scripts/build_harness.py`.
4. Start the harness (`preview_start` ds-harness), open `harness/_sweep.html`, wait until the page title starts with `SWEEP`, then `get_page_text`.
5. Look at every new preview in the browser and compare it with the frozen sketch; every difference is fixed or recorded as a `decisions.md` row (lesson 26). Focus each interactive part from the keyboard inside its real scroll container and check all four sides of the ring (attmpt-design Step 12, lesson 29).
6. `npm run check:types`.
7. Publish the batch only with `Artifact: yes` (`rules/artifact.md`).
8. After the last batch, dispatch `studio-design-reviewer` (payload: SKILL.md › Skills and agents) for registry coverage and states, within `Review passes:`.

## Outputs
- Components in the bundle, previews, READMEs, types; with `Artifact: yes`, a published artifact version per batch.

## Gate
- The sweep's first line is `SWEEP OK: … 0 errors, 0 overflows, 0 empty`; `check:types` passes; every new preview is listed in `progress.md` with the verdict after looking at it.

## Skills and agents
- `attmpt-design` (building, Step 12 check); `coss` only when the project rule names it; `mobile-design-patterns` build-spec on the mobile profile; agent `studio-design-reviewer`.

## Pitfalls
- With `Figma: yes`, build continuous-value parts (sliders, progress) so Figma can express the value later (`rules/figma.md`).
- `docs/lessons.md` 28 (layout parts), 29 (focus ring) and 42 (what each look needs from the kit).
