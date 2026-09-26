# Stage 8 · QA and handoff 🧑

## Inputs
- The artifact, the Figma file, `design/brief/tz-analysis.md`, `~/job/studio-design/docs/profiles/<profile>.md`, `CLIENT.md`.

## Steps
1. Stress tests from the profile (longest names, largest numbers, most content) in code and Figma.
2. Accessibility pass with `auditing-accessibility`: contrast, touch targets, focus.
3. Final sweep and final `audit.js` on every page.
4. Dispatch `studio-design-reviewer` for a whole-project review against the registry.
5. Write `design/handoff/README.md` in the client's language: links, how to use the library and the artifact, known limitations (for example «in Figma a slider shows one fixed position»), the font swap step if a stand-in was used.
6. Remind the user to grant the client access to the artifact and the Figma file. 🧑 Delivery.

## Outputs
- `design/handoff/README.md`; QA evidence in `progress.md`.

## Gate
- Sweep OK, audit ok on every page, reviewer findings fixed or accepted by the user, handoff written; the user confirms delivery.

## Skills and agents
- `auditing-accessibility`, `hallmark` audit; agent `studio-design-reviewer`.

## Pitfalls
- Known limitations go into the handoff, not into silence.
