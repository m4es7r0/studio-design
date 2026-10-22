# Manifest

Everything the pipeline uses, per stage, with how to check it and how to fix it. `scripts/preflight.sh`
checks the local part; stage 0 of `studio-design` checks the in-session part.

## Environment and accounts

| Item | Why | Check | Fix |
|---|---|---|---|
| Claude Code desktop app, Code tab | only place with the Design System artifact type, the built-in browser and the Figma MCP together | the session lists `Artifact`, `mcp__Claude_Browser__*` and Figma MCP tools | open the project in the desktop app |
| Models | main session opus; `studio-design-reviewer` opus; `tz-analyst` and `studio-design-figma-builder` sonnet | session model and agent frontmatter | pick Opus in the app |
| Figma, Professional plan, full seat | `use_figma` writes need an edit seat | Figma MCP `whoami` shows a Full seat | upgrade the seat; the user creates the file and shares its URL |
| Font licence | shipping fonts to a client | licence file next to the fonts (OFL or commercial) | ask the client or pick another font at stage 4 |

## Session tools

| Tool | Stages | Purpose | Check at stage 0 |
|---|---|---|---|
| Artifact, type Design System (quickstart, publish, read, list) | 2, 4–6, 8 | coded source of truth, previews, client link | `Artifact action=quickstart intent=other` lists a Design System type |
| Figma MCP `use_figma`, `get_screenshot`, `get_metadata`, `upload_assets` | 7 | build and verify | `whoami` shows a Full seat and a read-only `use_figma` lists the file's pages |
| Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs` | 2, 7 | import an existing client DS | same as above |
| Figma MCP runtime fonts | 0, 2, 4, 7 | which fonts `use_figma` can load (the stand-in for Figma text styles) | read-only `use_figma`: `figma.listAvailableFontsAsync()` contains the family |
| Built-in browser (`mcp__Claude_Browser__*`) or Claude in Chrome | 3, 5, 6, 8 | harness, measurements, sweep, screenshots | `preview_start` with `ds-harness` serves `ds/`; navigate to `/index.html` and see it load (`http.server` serves `.md` without a charset; the sweep page `harness/_sweep.html` appears with the first previews at stage 5) |
| WebFetch, WebSearch | 2 | references | a fetch of a public page works |
| AskUserQuestion | 1, 2, 9 | decisions | always present |
| Bash | all | scripts | always present |

Figma MCP server: any authenticated Figma MCP server that offers `use_figma` will do. The claude.ai
connector works without an interactive login; the Claude Code plugin server (`plugin:figma:figma`)
needs OAuth. Stage 0 records which server was used in the Preflight table. Take a file's page list
from `use_figma`, not `get_metadata` (it can omit pages).

## Local dependencies (`scripts/preflight.sh`)

| Item | Why | Fix |
|---|---|---|
| studio Python `.venv` with PyMuPDF, fontTools, brotli | `pdf_pages.py`, `font_check.py`, font conversion | `scripts/setup-python.sh` |
| Node 20+, npx | format checks, fixtures, `tsc` through the client `package.json` | install Node.js |
| git with user.name and user.email | every client container is a git repository | `git config --global …` |
| lsof | `new-client.sh` picks a free harness port | install lsof |

Studio scripts run through `scripts/py`: `scripts/pdf_pages.py` (stage 1) and `scripts/cyrillic_fonts.py`,
which checks every Google Fonts family with a Cyrillic subset with `font_check.py` and rewrites
`docs/fonts-cyrillic.md` (`--limit N` prints the first N instead), or with `--family "<Family>"` (repeatable)
checks just those faces and prints `font_check.py`'s ✅/❌ lines, exit 1 on a miss (stage 2). It needs
fonts.google.com, fonts.googleapis.com and fonts.gstatic.com. `--figma-families docs/figma-font-families.json`
adds an «In Figma» column to the list (and `· in Figma: yes|no` to each `--family` line), matched on the
family name without regard to letter case. That file is a dated capture of `figma.listAvailableFontsAsync()`
(`{"captured", "source", "families": {family: [styles]}}`), taken with a read-only `use_figma` on the
pipeline test Figma file (key `GPcPfsQUSrt2eMQnPbGedm`), never a client file. To refresh it, read the list in
chunks (for example by the family's first letter), because `use_figma` results over about 20 KB are truncated.
The Figma list changes, so stage 2 still checks every proposed face live.

## Skills

| Skill | Source | Stages | Role |
|---|---|---|---|
| `studio-design` | this repository, `scripts/install.sh` | all | orchestrator |
| `grilling` | `~/job/agent-skills`, `install.sh` | 1, 9 | decision-tree interview with output file, client questions and fact-finder options |
| `design-agent` | `~/design-intelligence-agent`, `scripts/install.sh` | 2 | research, directions brief, redesign audit (dispatches its own design-scout) |
| `attmpt-design` | `~/design-intelligence-agent`, `scripts/install.sh` | 2 (Sketch mode), 4, 5, 6, 9 | building: sketches, foundations, components, screens |
| `mobile-design-patterns` | `~/design-intelligence-agent` | 3, 5, 8 | mobile build-spec and audit |
| `auditing-accessibility` | `~/.claude/skills/auditing-accessibility` | 8, optional | real-device audit of a built mobile app only; not required by preflight |
| `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design` | Claude Code plugin `figma` | only with `Figma: yes`: 0, 2, 4 (`figma-use`: access and font checks), 7 | Plugin API rules, library build, screen build |
| `artifact-design`, `artifact-capabilities` | loaded through the artifact quickstart | 2, 4 when `Artifact:` is not `no` | page contract of the artifact |

hallmark (`~/.agents/skills/hallmark`, not a linked skill) is read only by `studio-design-reviewer` as the slop audit of marketing surfaces, with `design-agent/references/hallmark-waivers.md`. The map of every design skill: `~/job/agent-skills/docs/design-skills-role-map.md`.

## Agents

| Agent | Source | Stages |
|---|---|---|
| `tz-analyst` | this repository, sonnet | 1 (and fact-finder for `grilling`) |
| `studio-design-reviewer` | this repository, opus | 2, 5, 6, 8, 9 |
| `studio-design-figma-builder` | this repository, sonnet | 7 (only with `Figma: yes`) |

## Not built

- Package «ДС + код для разработки»: no stages exist; say so to the user.
- Agent `studio-design-ds-builder`: code components stay in the main session (revisit after the pilot).
