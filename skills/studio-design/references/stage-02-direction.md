# Stage 2 · Direction 🧑

## Inputs
- `design/brief/tz-analysis.md`, `design/decisions.md` (audience, the «Moved to stage 2» rows), `design/PROJECT.md` (entry mode, profile), `design/refs/`, `design/figma/figma-state.json` (Figma file key for the font check).
- `~/job/studio-design/docs/rules/{design,artifact,figma}.md`, `~/job/studio-design/docs/fonts-cyrillic.md` (Cyrillic projects), `~/job/studio-design/scripts/cyrillic_fonts.py`.

## Steps
1. Every entry mode except «existing DS»: create the artifact from the Design System type (`Artifact action=quickstart intent=other`), read its `project/design-system.json` and merge it into `ds/project/design-system.json` (keep `createdOnFiles`); record the URL in `PROJECT.md` and `CLIENT.md`.
2. Entry mode «from scratch»: dispatch `design-scout` (payload: SKILL.md › Agents) with the platform profile and the brief's genre, before the harness is in use, and tell it to open its own browser tab. It can run 20+ minutes: meanwhile prepare palettes with contrast figures and the page skeleton, and fill the Evidence sections of the direction files when its report lands. Write three directions under `hallmark` rules into `design/directions/` and the directions page (step 7). hallmark asks audience, use case and tone before designing: answer from `decisions.md` (audience from the brief or grilling; the three directions supply the tones; record the catalog or custom route). If a value is missing, ask the user once and record it.
3. Entry mode «brand book»: colours, fonts and logo are fixed; write one direction that sets colour roles, contrast and tone.
4. Entry mode «redesign»: audit the current product through `design-agent` (screenshots into `design/refs/`), then one direction that keeps recognisability.
5. Entry mode «existing DS»: import the client's tokens and components through Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs`; write what exists and what is missing into `design/directions/existing-ds.md`; then go to stage 3.
6. Fonts: every proposed face comes from Google Fonts (the only host the artifact CSP and the Figma MCP runtime allow) and passes `font_check.py` before the client sees it; for Cyrillic projects start from `~/job/studio-design/docs/fonts-cyrillic.md`. For each proposed face run `~/job/studio-design/scripts/py ~/job/studio-design/scripts/cyrillic_fonts.py --family "<Family>"` (it prints `font_check.py`'s ✅/❌ line and exits 1 on a miss). Then, for every proposed face, run a read-only `use_figma` (load `figma:figma-use` first; the file key is in `design/figma/figma-state.json`) with `figma.listAvailableFontsAsync()`, filtered to the proposed families (results over about 20 KB are truncated), and confirm that the weights the direction uses exist in the Figma MCP runtime, with their exact style names (`rules/figma.md`); otherwise the client would pick a direction whose Figma library needs a stand-in. The «In Figma» column of `fonts-cyrillic.md` is a dated capture and does not replace this check. Record both results in the direction file.
7. The directions page is a `page` preview card in the group «Направления» (the group name in the client's language), written through `ds/previews_spec.py`, `gen_previews.py` and `build_harness.py` (the reviewer opens it in the harness), and published (`rules/artifact.md`). It shows:
   - each direction has its own first screen and its own signature section, not one skeleton in three skins;
   - a states strip: field default / focus / error, primary button pressed / submitting, success, one disclosure open and closed; a focused invalid field shows both the error and the focus ring;
   - unconfirmed facts are marked (dashed outline and «уточнить» in the client's language); nothing is invented;
   - the riskiest element is also shown at 375;
   - draft copy is tagged as a draft;
   - fonts pass `font_check.py`; text contrast pairs meet AA (figures in the direction file).
8. Dispatch `studio-design-reviewer` (payload: SKILL.md › Agents) on the directions and the directions page (slop, fit to the brief, the list of step 7); fix what it finds and run it again until it reports no blocker or major findings, at most three passes. If majors remain after the third pass, show the user the open list before the client checkpoint.
9. 🧑 The user shows the directions to the client; record the choice in `decisions.md`; keep the rejected ones in `design/directions/`; move the directions card to the group «Архив» (in the client's language) and publish. Remind the user that the artifact and the Figma file are private until they grant the client access.

## Outputs
- `design/directions/*.md`; the artifact (URL in `PROJECT.md` and `CLIENT.md`) with the directions page or a style tile; the merged `ds/project/design-system.json`.

## Gate
- The chosen direction is recorded in `decisions.md`; every proposed face passed `font_check.py` and its Figma font check is recorded in the direction file; the last `studio-design-reviewer` pass reports no blocker or major findings, or the user saw the open list before the client checkpoint. For entry mode «existing DS»: `design/directions/existing-ds.md` is written and the user's confirmation of the import is recorded in `decisions.md`.

## Skills and agents
- `hallmark`, `design-agent`, `artifact-design` and `artifact-capabilities` (through the quickstart), `figma:figma-use` (font check), agents `design-scout`, `studio-design-reviewer`.

## Pitfalls
- Brand colour is a signal, not a surface (`rules/design.md`).
- hallmark's worked examples are not style references (`rules/design.md`).
- Screenshots need the Browser pane visible; if it is hidden, ask the user to show it (a background tab may not repaint).
- `docs/lessons.md` 12 (fonts checked at stage 2), 14 (what the directions page shows), 17 (Figma font check at stage 2) and 18 (error ring and focus ring).
