# Stage 8 · QA and handoff 🧑

## Inputs
- The artifact, the Figma file, `design/brief/tz-analysis.md`, `~/job/studio-design/docs/profiles/<profile>.md`, `CLIENT.md`.

## Steps
1. Stress tests from the profile (longest names, largest numbers, most content) in code and Figma.
2. Accessibility: the `hallmark` audit plus figures measured in the harness — text/background contrast of every text colour pair in use, target sizes against the profile minimum, visible focus on every interactive component — recorded in `progress.md`. `auditing-accessibility` only for a built mobile app on a real device.
3. Final sweep, final `harness/_measure.html?page=<Name>&w=<W>&h=<H>` on every screen and layout-budget preview at every target size (wait until the title starts with `MEASURE`, then `get_page_text`; paste the first lines into `progress.md`), and final `audit.js` on every page. On profiles whose pages scroll (web-landing, web-product, mobile), measure the full page with `h=auto` (width only), and use a fixed `h` only for zones that must stay inside the viewport (shell, rails, sticky bars, the first screen); mark only those zones with `data-zone` on the fixed-height run, or run the fixed-height check on a preview of that part alone.
4. Dispatch `studio-design-reviewer` (payload: SKILL.md › Agents) for a whole-project review against the registry.
5. Write `design/handoff/README.md` in the client's language: links, how to use the library and the artifact, known limitations (for example «in Figma a slider shows one fixed position»), the font swap step if a stand-in was used.
6. Remind the user to grant the client access to the artifact and the Figma file. 🧑 Delivery.

## Outputs
- `design/handoff/README.md`; QA evidence in `progress.md`.

## Gate
- Sweep OK, every measure run `MEASURE OK`, audit ok on every page, reviewer findings fixed or accepted by the user, handoff written; the user confirms delivery.

## Skills and agents
- `hallmark` audit; `auditing-accessibility` only for a built mobile app on a real device; agent `studio-design-reviewer`.

## Pitfalls
- Known limitations go into the handoff, not into silence.
