# Stage 2 · Direction 🧑

## Inputs
- `design/brief/tz-analysis.md`, `design/decisions.md`, `design/PROJECT.md` (entry mode, profile), `design/refs/`.

## Steps
1. Entry mode «from scratch»: dispatch `design-scout` (payload: SKILL.md › Agents) with the platform profile and the brief's genre; then write three directions under `hallmark` rules into `design/directions/` and a directions page in the artifact (create the artifact now if needed, see stage 4 step 1).
2. Entry mode «brand book»: colours, fonts and logo are fixed; write one direction that sets colour roles, contrast and tone.
3. Entry mode «redesign»: audit the current product through `design-agent` (screenshots into `design/refs/`), then one direction that keeps recognisability.
4. Entry mode «existing DS»: import the client's tokens and components through Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs`; write what exists and what is missing into `design/directions/existing-ds.md`; then go to stage 3.
5. Dispatch `studio-design-reviewer` (payload: SKILL.md › Agents) on the directions (slop, fit to the brief); fix what it finds.
6. 🧑 The user shows the directions to the client; record the choice in `decisions.md`; keep the rejected ones in `design/directions/`.

## Outputs
- `design/directions/*.md`, a style tile or directions page in the artifact.

## Gate
- The chosen direction is recorded in `decisions.md`; for entry mode «existing DS»: `design/directions/existing-ds.md` is written and the user's confirmation of the import is recorded in `decisions.md`.

## Skills and agents
- `hallmark`, `design-agent`, agents `design-scout`, `studio-design-reviewer`.

## Pitfalls
- Brand colour is a signal, not a surface (`rules/design.md`).
