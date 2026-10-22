# Stage 8 · QA and handoff 🧑

## Inputs
- The built design system and screens; the artifact when `Artifact:` is not `no`; the Figma file with `Figma: yes`; `design/brief/tz-analysis.md`, `design/decisions.md`, `design/PROJECT.md`, `~/job/studio-design/docs/profiles/<profile>.md`, `CLIENT.md`.

## Steps
1. Stress tests from the profile (longest names, largest numbers, most content) in code, and in Figma with `Figma: yes`.
2. Accessibility figures measured in the harness — text and UI contrast of every pair in use in every theme, target sizes against the profile minimum, visible focus on every interactive component — recorded in `progress.md`. Mobile mock-ups: `mobile-design-patterns` audit. A built mobile app on a real device: `auditing-accessibility`.
3. Final sweep, final `harness/_measure.html?page=<Name>&w=<W>&h=<H>` on every screen and layout-budget preview at every target size (wait until the title starts with `MEASURE`, then `get_page_text`; paste the first lines into `progress.md`). With `Figma: yes`, the final `audit.js` on every page. On profiles whose pages scroll (web-landing, web-product, mobile), measure the full page with `h=auto` (width only), and use a fixed `h` only for zones that must stay inside the viewport (shell, rails, sticky bars, the first screen).
4. Dispatch `studio-design-reviewer` (payload: SKILL.md › Skills and agents) for a whole-project review against the named scope; it is the one slop check of the project. Stay within `Review passes:`; re-check each fix of the last pass by its finding's repro.
5. Write `design/handoff/README.md` in the client's language: links, how to use the deliverables, known limitations (for example «in Figma a slider shows one fixed position»), the font swap step if a stand-in was used, and a section «not re-checked by the reviewer» listing the fixes of the last pass (lesson 27). Commit each handoff file as soon as its first draft exists; a scripted edit replaces an exact string and checks that it matched once (lesson 35).
6. With `Artifact:` not `no`, publish the final version and read it back (lesson 34). Before the 🧑 checkpoint, list only the «to confirm» items still open. Remind the user to grant the client access to the artifact and the Figma file, where they exist. 🧑 Delivery.

## Outputs
- `design/handoff/README.md`; QA evidence in `progress.md`.

## Gate
- Sweep OK, every measure run `MEASURE OK`, with `Figma: yes` audit ok on every page, reviewer findings fixed or accepted by the user, handoff written and committed; the user confirms delivery.

## Skills and agents
- Agent `studio-design-reviewer` (it applies the slop rules on marketing surfaces); `mobile-design-patterns` audit for mobile mock-ups; `auditing-accessibility` only for a built mobile app on a real device.

## Pitfalls
- Known limitations go into the handoff, not into silence.
- `docs/lessons.md` 27 (what no reviewer saw again), 33 (grep the handoff after renames), 34 (read the publish back) and 35 (commit handoff drafts).
