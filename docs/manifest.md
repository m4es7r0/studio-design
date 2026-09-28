# Manifest

Everything the pipeline uses, per stage, with how to check it and how to fix it. `scripts/preflight.sh`
checks the local part; stage 0 of `studio-design` checks the in-session part.

## Environment and accounts

| Item | Why | Check | Fix |
|---|---|---|---|
| Claude Code desktop app, Code tab | only place with the Design System artifact type, the built-in browser and the Figma MCP together | the session lists `Artifact`, `mcp__Claude_Browser__*` and Figma MCP tools | open the project in the desktop app |
| Model Opus | main session and every agent (`model: opus`) | session model | pick Opus in the app |
| Figma, Professional plan, full seat | `use_figma` writes need an edit seat | Figma MCP `whoami` shows a Full seat | upgrade the seat; the user creates the file and shares its URL |
| Font licence | shipping fonts to a client | licence file next to the fonts (OFL or commercial) | ask the client or pick another font at stage 4 |

## Session tools

| Tool | Stages | Purpose | Check at stage 0 |
|---|---|---|---|
| Artifact, type Design System (quickstart, publish, read, list) | 2, 4–6, 8 | coded source of truth, previews, client link | `Artifact action=quickstart intent=other` lists a Design System type |
| Figma MCP `use_figma`, `get_screenshot`, `get_metadata`, `upload_assets` | 7 | build and verify | `whoami` shows a Full seat and a read-only `use_figma` lists the file's pages |
| Figma MCP `get_libraries`, `search_design_system`, `get_variable_defs` | 2, 7 | import an existing client DS | same as above |
| Figma MCP runtime fonts | 0, 4, 7 | which fonts `use_figma` can load (the stand-in for Figma text styles) | read-only `use_figma`: `figma.listAvailableFontsAsync()` contains the family |
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

## Skills

| Skill | Source | Stages | Role |
|---|---|---|---|
| `studio-design` | this repository, `scripts/install.sh` | all | orchestrator |
| `grilling` | `~/job/agent-skills`, `install.sh` | 1, 9 | decision-tree interview with output file, client questions and fact-finder options |
| `hallmark` | `~/.agents/skills/hallmark` (linked into `~/.claude/skills`) | 2, 4, 8 | directions, anti-slop rules, audit |
| `design-agent` | `~/design-intelligence-agent`, `scripts/install.sh` | 2 | references, patterns, redesign audit |
| `mobile-design-patterns` | `~/design-intelligence-agent` | 3, 5 | mobile profile |
| `auditing-accessibility` | `~/.claude/skills/auditing-accessibility` | 8, optional | real-device audit of a built mobile app only; not required by preflight |
| `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design` | Claude Code plugin `figma` | 7 | Plugin API rules, library build, screen build |
| `artifact-design`, `artifact-capabilities` | loaded through the artifact quickstart | 4 | page contract of the artifact |

## Agents

| Agent | Source | Stages |
|---|---|---|
| `tz-analyst` | this repository | 1 (and fact-finder for `grilling`) |
| `design-scout` | `~/design-intelligence-agent` | 2 (dispatched with `model: opus`; its own frontmatter says sonnet) |
| `studio-design-reviewer` | this repository | 2, 5, 6, 8, 9 |
| `studio-design-figma-builder` | this repository | 7 |

## Not built

- Package «ДС + код для разработки»: no stages exist; say so to the user.
- Agent `studio-design-ds-builder`: code components stay in the main session (revisit after the pilot).
