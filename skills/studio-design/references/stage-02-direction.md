# Stage 2 · Direction 🧑

## Inputs
- `design/brief/tz-analysis.md`, `design/decisions.md` (audience, deliverables, the «Moved to stage 2» rows), `design/PROJECT.md` (entry mode, profile, switches), `design/refs/`, `design/figma/figma-state.json` (only with `Figma: yes`, for the font check).
- `~/job/studio-design/docs/rules/{design,artifact,figma}.md`, `~/job/studio-design/docs/fonts-cyrillic.md` (Cyrillic projects), `~/job/studio-design/scripts/cyrillic_fonts.py`.

## Steps
1. Only when `Artifact:` is not `no`, and in every entry mode except «existing DS»: create the artifact from the Design System type (`Artifact action=quickstart intent=other`), read its `project/design-system.json` and merge it into `ds/project/design-system.json` (keep `createdOnFiles`); record the URL in `PROJECT.md` and `CLIENT.md`.
2. Entry modes «from scratch», «brand book» and «redesign»: invoke `design-agent` (payload: SKILL.md › Skills and agents). It researches through its own research agent (in «redesign» it first audits the current product, screenshots into `design/refs/`), resolves the research summary and hands `attmpt-design` the «Sketch mode» brief: `Directions:` directions, each deciding every part in `Parts:`. In «brand book» colours, fonts and logo are fixed and the directions vary inside them. attmpt-design writes the directions into `design/directions/` and the directions page (step 4).
3. Entry mode «existing DS»: import the client's tokens and components through Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs` (reading the client's Figma needs access even with `Figma: no` for our output); write what exists and what is missing into `design/directions/existing-ds.md`; then go to stage 3.
4. The directions page is a `page` preview card in the group «Направления» (the group name in the client's language), written through `ds/previews_spec.py`, `gen_previews.py` and `build_harness.py` (the reviewer opens it in the harness). It shows:
   - each direction with its own first screen and its own signature section, not one skeleton in three skins; every part labelled, so the client can pick parts from different directions (lesson 25);
   - a states strip: field default / focus / error, primary button pressed / submitting, success, one disclosure open and closed; a focused invalid field shows both the error and the focus ring;
   - unconfirmed facts are marked (dashed outline and «уточнить» in the client's language); nothing is invented;
   - the riskiest element also at the profile's narrowest size;
   - draft copy tagged as a draft;
   - fonts that pass `font_check.py`; text contrast pairs in every theme of `Themes:` meet AA (figures in the direction file).
   With `Artifact: yes` or `checkpoints`, publish it (`rules/artifact.md`).
5. Fonts: every proposed face comes from Google Fonts (the only host the artifact CSP and the Figma MCP runtime allow) and carries every character `Locale:` needs; for Cyrillic projects start from `~/job/studio-design/docs/fonts-cyrillic.md` and run `~/job/studio-design/scripts/py ~/job/studio-design/scripts/cyrillic_fonts.py --family "<Family>"` per face. Only with `Figma: yes`: a read-only `use_figma` (load `figma:figma-use` first; the file key is in `design/figma/figma-state.json`) with `figma.listAvailableFontsAsync()`, filtered to the proposed families (results over about 20 KB are truncated), confirms the weights and their exact style names (`rules/figma.md`). Record the results in the direction file.
6. Dispatch `studio-design-reviewer` (payload: SKILL.md › Skills and agents) on the directions and the directions page; fix what it finds and run it again, at most `Review passes:` passes, re-checking each fix by its finding's repro. If majors remain after the last pass, show the user the open list before the client checkpoint.
7. 🧑 The user shows the directions to the client; record the choice (a whole direction or parts from several) in `decisions.md`. A combined choice gets one combined build, clicked through by you, before the reviewer sees it. At acceptance freeze the prototype (lesson 26): later revisions go into components and screens, and every difference from it becomes a `decisions.md` row. Keep the rejected directions in `design/directions/`; with `Artifact:` not `no`, move the directions card to the group «Архив» (in the client's language) and publish. Remind the user that the artifact and the Figma file, where they exist, are private until they grant the client access.

## Outputs
- `design/directions/*.md`; the frozen combined sketch; with `Artifact:` not `no`, the artifact (URL in `PROJECT.md` and `CLIENT.md`) with the directions page and the merged `ds/project/design-system.json`.

## Gate
- The chosen direction or parts are recorded in `decisions.md`; every proposed face passed `font_check.py` (and, with `Figma: yes`, its Figma font check) in the direction file; contrast figures for every theme are in the direction file; the last `studio-design-reviewer` pass reports no blocker or major findings, or the user saw the open list before the client checkpoint. For entry mode «existing DS»: `design/directions/existing-ds.md` is written and the user's confirmation of the import is recorded in `decisions.md`.

## Skills and agents
- `design-agent` (research, directions brief, audit in «redesign»), `attmpt-design` (Sketch mode), `artifact-design` and `artifact-capabilities` (through the quickstart, when `Artifact:` is not `no`), `figma:figma-use` (font check, only with `Figma: yes`), agent `studio-design-reviewer`.

## Pitfalls
- Brand colour is a signal, not a surface (attmpt-design Step 8).
- Screenshots need the Browser pane visible; if it is hidden, ask the user to show it (a background tab may not repaint).
- `docs/lessons.md` 12 (fonts checked at stage 2), 14 (what the directions page shows), 17 (Figma font check at stage 2), 18 (error ring and focus ring), 25 (parts chosen one by one) and 26 (freeze the prototype).
