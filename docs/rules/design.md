# Design rules

Design doctrine — construction (spacing, edges, siblings, radii), tokens, states, colour, type, motion, interface copy and the check before showing — lives in attmpt-design (`~/.claude/skills/attmpt-design/SKILL.md`, from `~/design-intelligence-agent`). These rules are the pipeline's own.

- Code is the source of truth; Figma mirrors it. No Figma-only component.
- Tokens, states, the error and focus rings, honest gaps and contrast follow attmpt-design (Steps 0, 8, 11).
- Layout budget before components: the densest screens are measured at the target size at stage 3.
- Sample values come from `ds/fixtures/` through the format functions (the doctrine on missing values is attmpt-design Step 11).
- Contrast figures for every pair in every theme are recorded at stages 2, 4 and 8.
- Fonts we propose come from Google Fonts only (the only host the artifact CSP and the Figma MCP runtime allow) and carry every character the project's locale needs. Cyrillic projects pick from `docs/fonts-cyrillic.md` or a face that passes `fonts/font_check.py`.
- Checks are committed scripts (`ds/scripts/sweep.js`, `ds/scripts/measure.js`, `figma/audit.js`, `ds/scripts/check_format.js`, `fonts/font_check.py`); never write a check ad hoc in a session.
- Client material (briefs, references, fonts, screenshots, client names) stays in the client container. The studio repository, including `docs/lessons.md`, holds none; write lessons without client names.
- Stage references name every input file; agents never search for inputs on their own.
