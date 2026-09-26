# Studio Design pipeline: design

Date: 2026-09-26. Status: approved in chat, awaiting review of this file.
Source effort: the «Симулятор мэра» design system (`~/job/mayor-sim-design`, artifact
https://claude.ai/artifact/5XmWyh1fP5rtEPJkY6scxC, Figma file NcLeuYB80bCP3OAeY2qIlh).

## 1. Goal

Turn the Mayor Sim session into a repeatable client service: a client brings a brief (TZ),
and the same model and agents produce a coded design system (Claude Design artifact) and a
quality Figma file, stage by stage, with the same checks every time.

The pipeline must be explicit enough that a fresh session knows, from files alone, which
tools, skills and agents to use at each stage, what is missing, where the work stopped and
what the client has decided.

## 2. Scope

In scope:

- The `studio-design` pipeline repository: orchestrator skill, stage references, agents,
  docs (manifest, playbook, packages, profiles, rules, lessons), client project template,
  scripts.
- A personal skills repository `~/job/agent-skills` with our fork of `grilling`.
- Packages «ДС» and «ДС + экраны»; entry modes «с нуля», «брендбук», «редизайн»,
  «готовая ДС»; platform profiles web-landing, web-product, mobile, game.
- The revision cycle (rounds of client правки).

Out of scope, recorded as not built:

- Package «ДС + код для разработки» (production component library in the client's stack).
  It gets its own spec later. `packages.md` marks it «not built» so the agent says so.
- Other pipelines (`studio-dev`, `studio-deploy`) and a shared `studio-core`. Shared parts
  (revision cycle, manifest pattern, preflight) stay in `studio-design` until a second
  pipeline exists; extraction happens then.
- A `studio-design-ds-builder` agent. Code components stay in the main session for v1;
  revisit after the pilot if context overflows.

## 3. Names

- Pipeline orchestrator skills: `studio-<area>`. This one is `studio-design`.
- Pipeline repository: `~/job/studio-design` (one repository per pipeline).
- Pipeline agents: `studio-design-<role>`. Agents useful to future pipelines have no
  prefix: `tz-analyst`. The existing `design-scout` keeps its name.
- Client container: `~/job/clients/<client-slug>/`; this pipeline works in its `design/`
  folder. Future pipelines use sibling folders (`app/`, `deploy/`).

## 4. Repositories and layout

### 4.1 `~/job/agent-skills` (personal reusable skills)

A git repository of skills that belong to no project. Each skill is symlinked into
`~/.claude/skills/<name>`, the same way `design-agent` is linked from
`~/design-intelligence-agent`.

First resident: `grilling`, forked from `mattpocock/skills`
(`skills/productivity/grilling/SKILL.md`). The skill's `UPSTREAM.md` records the upstream
repository, path, commit and license, and lists our changes, so upstream updates can be
merged by hand. Our changes:

1. Persisted result: when the caller names an output file, the skill writes the settled
   decision tree there when the frontier is empty (upstream writes nothing).
2. Client-questions mode: open items the user cannot decide become a polite, grouped
   question list with a recommended answer per item, for a non-technical reader.
3. Named fact-finder: when the caller names an agent for facts (for example `tz-analyst`),
   the skill dispatches that agent instead of a generic one.

### 4.2 `~/job/studio-design` (the pipeline)

```
studio-design/
  README.md              start a client in ten lines
  AGENTS.md              rules for agents that maintain the pipeline itself
  docs/
    manifest.md          tools, accounts, local deps, skills, agents; per stage; how to check
    playbook.md          the pipeline end to end, for a human reader
    packages.md          packages → stages; «ДС + код» marked not built
    profiles/            web-landing.md, web-product.md, mobile.md, game.md
    rules/               design.md, numbers-and-locale.md, figma.md, artifact.md, client.md
    lessons.md           known pitfalls; appended after every project
    superpowers/specs/   specs of the pipeline itself
  skills/
    studio-design/       SKILL.md + references/stage-00-intake.md … stage-09-revisions.md
  agents/                tz-analyst.md, studio-design-reviewer.md, studio-design-figma-builder.md
  template/              the client container skeleton (4.3)
  scripts/
    install.sh           symlinks skills/ and agents/ into ~/.claude; idempotent
    new-client.sh        copies template/ to ~/job/clients/<slug>/, runs git init there
    preflight.sh         checks local deps; prints a ✅/❌ table with the fix for each ❌
```

### 4.3 Client container `~/job/clients/<client-slug>/`

```
CLIENT.md          client, contacts, language, contract: package, revision rounds included,
                   deadlines, links (artifact, Figma) and who has access
design/
  PROJECT.md       package, platform profile(s), entry mode, target resolutions,
                   current stage, links
  decisions.md     every client and user decision: date, source, text
  questions.md     open questions to the client, grouped, with our recommended answers
  progress.md      stage log with evidence (command output, screenshots paths)
  brief/           original TZ files, tz-analysis.md, layout-budget.md
  refs/            references and images extracted from the TZ
  directions/      direction drafts; the rejected ones stay here as archive
  ds/
    project/       artifact source: tokens.json, README.md, design-system.json,
                   components/ (bundle.js, bundle.css, index.d.ts, <Name>/README.md,
                   <Name>/preview.html), fonts/
    fixtures/      sample data (raw values) shared by code previews and Figma scripts
    scripts/       build_harness.py, gen_previews.py, check_format.js,
                   format_fixtures.js, sweep.js (+ harness page _sweep.html)
    upload/        local copies of uploaded artifact assets (blob id → file)
  figma/           prelude.js, audit.js, figma-state.json
  fonts/           font_check.py, optional patch and conversion scripts
  revisions/       round-NN/source/, round-NN.md
  handoff/         client handoff, in the client's language
  package.json     typescript (for index.d.ts checks) and nothing else
  .claude/launch.json   the harness server of this project
```

`new-client.sh` creates `CLIENT.md` and `design/` from the template, runs `git init` in the
client container and makes the first commit. Client material (TZ, refs, licensed fonts)
never leaves the client container; the studio repository holds none.

## 5. Stages

Every stage reference in `skills/studio-design/references/` lists: exact input paths,
steps, exact output paths, the gate, the skills and agents to use, and the pitfalls from
`lessons.md` that apply. Agents never discover inputs on their own; references name them.

A gate is a binary check with evidence (command output, screenshot path, a decision
entry). The orchestrator does not start the next stage until the gate passes and
`progress.md` records the evidence. 🧑 marks a client checkpoint: the orchestrator prepares
the material and a question list, the user takes it to the client, the answers go to
`decisions.md`.

| # | Stage | Output | Gate |
|---|---|---|---|
| 0 | Intake | `CLIENT.md`, `PROJECT.md`, preflight table | no ❌ in preflight (or each ❌ accepted by the user for this project) |
| 1 | TZ analysis | `brief/tz-analysis.md`, `questions.md`, `decisions.md` | 🧑 client answers recorded; grilling frontier empty |
| 2 | Direction | depends on entry mode; style tile | 🧑 direction chosen and recorded |
| 3 | Layout budget | the 2–3 densest screens at target size as zone boxes with fixture data; `brief/layout-budget.md` | measured zone sizes fit (numbers pasted from the harness) |
| 4 | Foundations | tokens, fonts (+ Figma stand-in), number and locale rules, fixtures, style tile page | format tests pass; font check passes; style tile published |
| 5 | Components (code) | registry batches with every state, README, types | sweep: 0 errors, 0 overflows; `tsc --strict` on `index.d.ts`; screenshots |
| 6 | Screens (code) | key templates (package ДС) or every registry screen (package ДС + экраны) | fit measured at every target size |
| 7 | Figma | variables, styles, components by batch, templates | `audit.js` after every batch on every touched page: all counts 0; screenshots |
| 8 | QA and handoff | stress tests, contrast, final audit, `handoff/` | 🧑 delivery |
| 9 | Revision rounds | `revisions/round-NN.md` | section 8 |

Stage 1 procedure: `tz-analyst` extracts facts first (registry of screens and components
with the TZ's own IDs, states, data types and formats, constraints, contradictions and
gaps, each with a page reference). Then `grilling` runs with the user over decisions only,
with `tz-analyst` as its fact-finder and `design/decisions.md` as its output file. Items
only the client can decide go to `questions.md` in client-questions mode.

Stage 2 by entry mode:

- From scratch: `design-scout` research, three directions under `hallmark` rules, a
  directions page in the artifact; the client picks one.
- Brand book: brand colours, fonts and logo are fixed; the stage decides colour roles,
  contrast and tone, and shows one direction.
- Redesign: audit of the current product (screenshots, UX problems) through
  `design-agent`; one direction that keeps recognisability.
- Existing DS: import the client's tokens and components (Figma MCP `get_libraries`,
  `search_design_system`, `get_variable_defs`); stage 2 is skipped; stages 4–5 build only
  what is missing.

Feel-type decisions («как это должно ощущаться») are not grilled; they are shown as
directions and style tiles.

Packages (`docs/packages.md`):

- «ДС»: stages 0–9; stage 6 codes only the 1–2 key templates from the layout budget, and
  stage 7 builds the components and those templates.
- «ДС + экраны»: all stages; stages 6 and 7 cover every registry screen.
- «ДС + код для разработки»: not built.

Platform profiles (`docs/profiles/`) apply at stages 3, 5 and 8: target sizes and
breakpoints, minimum touch targets, safe areas, navigation patterns, density, what to
check. `game.md` comes from Mayor Sim; the others from `mobile-design-patterns`,
`design-agent` references and `hallmark`.

## 6. Toolchain manifest and preflight

`docs/manifest.md` lists each item with: purpose, stages, how to check, how to fix.

Environment and accounts:

- Claude Code desktop app, Code tab (the only place with the Design System artifact type,
  the built-in browser and the Figma MCP together). Main model and bulk agents: Opus.
- Figma: Professional plan with a full seat (writes need it); the user creates the file
  and gives its URL.
- Font licence check (OFL or commercial) at stage 4.

Session tools:

| Tool | Stages | Purpose |
|---|---|---|
| Artifact, Design System type (quickstart, publish, read, list) | 2, 4–6, 8 | the coded source of truth, previews, client link |
| Figma MCP: `use_figma`, `get_screenshot`, `get_metadata`, `upload_assets` | 7 | build and verify |
| Figma MCP: `get_libraries`, `search_design_system`, `get_variable_defs` | 2, 7 | import an existing client DS |
| Built-in browser (or Claude in Chrome) | 3, 5, 6, 8 | harness, measurements, sweep, screenshots |
| WebFetch, WebSearch | 2 | references |
| AskUserQuestion | 1, 2, 9 | decisions |
| Bash | all | scripts |

Local dependencies (`preflight.sh`): python3 with PyMuPDF (PDF to images), fontTools and
brotli (fonts); node; the client container's `package.json` (typescript); git.

Skills:

| Skill | Stages | Role |
|---|---|---|
| `studio-design` | all | orchestrator |
| `grilling` (from `~/job/agent-skills`) | 1, 9 | decision tree interview |
| `hallmark` | 2, 4, 8 | directions, anti-slop rules, audit |
| `design-agent` + agent `design-scout` | 2 | references, patterns, redesign audit |
| `mobile-design-patterns` | 3, 5 | mobile profile |
| `auditing-accessibility` | 8 | contrast, touch targets, focus |
| `figma:figma-use`, `figma:figma-generate-library`, `figma:figma-generate-design` | 7 | API rules, library build, screen build |
| `artifact-design`, `artifact-capabilities` | 4 | loaded through the artifact quickstart |

In-session preflight (stage 0, by the orchestrator): Figma MCP connected (`whoami`, seat),
Design System artifact type available (quickstart), browser available, which fonts the
Figma MCP runtime can load (`listAvailableFontsAsync` for the chosen family). Output: a
✅/❌ table in `progress.md` with the fix for each ❌.

## 7. Agents

The main session is the orchestrator: it talks to the user, runs stages and gates, makes
and records decisions, publishes. Agent reports are not shown to the user; the
orchestrator relays what matters. Every agent file states exact input and output paths,
allowed tools, forbidden actions (decisions, publishing, client contact) and the report
format with evidence. Model: Opus.

| Agent | Stages | Input → output | Never |
|---|---|---|---|
| `tz-analyst` | 1; fact-finder for grilling | `design/brief/` sources → `brief/tz-analysis.md`, extracted images in `refs/` | decides, fills gaps with guesses |
| `design-scout` (exists) | 2 | question + platform profile → evidence package | picks the direction |
| `studio-design-reviewer` | 2, 5, 6, 8, 9 | artifact, screenshots, `tz-analysis.md`, round file → ranked findings with evidence: registry coverage, states, UX, hallmark slop, UX risk of client правки | fixes anything |
| `studio-design-figma-builder` | 7 | one batch from code + `figma-state.json` + `docs/rules/figma.md` → the batch in Figma, `audit.js` output, node IDs, screenshots, updated ledger | runs in parallel with any other Figma call; edits code |

Code components stay in the main session (user feedback lands there; `bundle.js` is one
file, parallel implementers would conflict).

## 8. Revision rounds and client communication

A round lives in `design/revisions/round-NN/` and `round-NN.md`.

1. Intake: the client's list in any form goes to `source/`; the orchestrator normalises
   it into a table: number, where (screen or component with its registry ID), request,
   the client's words.
2. Triage per item, drafted by the orchestrator with a second opinion from
   `studio-design-reviewer`:
   - ✅ accept as is;
   - 🔁 accept with a change that meets the client's goal without breaking anything;
   - ⚠️ push back: breaks UX, system consistency, the TZ or accessibility; always with a
     reason, evidence (TZ reference, profile rule, contrast figures) and an alternative;
   - ❓ unclear: a question to the client;
   - 💰 outside the package: a change request.
   Each item lists its impact (tokens and components propagate; affected places come from
   the registry).
3. The user decides ⚠️, ❓ and 💰 items through `grilling`; decisions go to
   `decisions.md`.
4. Client reply in the client's language, no jargon: what we do, what we propose instead
   and why, questions. The user sends it. 🧑 The client confirms.
5. Implementation: code, sweep, Figma, audit; before and after screenshots.
6. Round report: status of every item. A правка that repeats across projects becomes a
   rule in `lessons.md`.

Rules: never implement a UX-breaking правка silently; never refuse silently. The number of
included rounds comes from `CLIENT.md`; the orchestrator warns when the included rounds
are used up and the next one is a new order.

Client communication:

- Everything the client reads is in the client's language (usually Russian); files and
  code are in English.
- Checkpoint materials: stage 1 `questions.md` (grouped, recommended answer per question so
  the client can reply «ок»); stage 2 directions page; stage 8 handoff (links, how to use,
  known limitations).
- The artifact and the Figma file are private by default; the user grants access. The
  orchestrator reminds the user at every checkpoint.

## 9. Rules

`docs/rules/` holds the hard rules. The main ones:

- Code is the source of truth; Figma mirrors it. No Figma-only component.
- Sample values come from `ds/fixtures/` through the DS format functions
  (`format_fixtures.js`); nobody types a formatted value by hand. Missing data is marked,
  not invented.
- Stage references name every input file; agents do not discover inputs.
- Checks are committed scripts (`sweep.js`, `audit.js`, `check_format.js`,
  `font_check.py`), not code written ad hoc in a session.
- Layout budget before components (stage 3).
- Figma (`docs/rules/figma.md`, seeded from the Mayor ledger):
  - mutating calls strictly sequential, one page switch per call; read-only audits may
    fan out in parallel;
  - the MCP runtime sees only Google Fonts: text styles bind to Typography variables with a
    Google stand-in; the user swaps the family at the very end;
  - bound paints carry the resolved variable colour;
  - `clone()` of a variant drops property references: re-bind after cloning (the audit
    catches misses);
  - hidden instance sublayers take no fill writes: set fills before hiding;
  - instance children cannot be moved, and constraint-scaled layers ignore resize: build
    continuous-value parts (slider fill, progress) with auto-layout FIXED widths and verify
    an override on an instance before closing the component;
  - plan size variants against the 30-variant cap before building;
  - append to an auto-layout parent before setting FILL;
  - after `setProperties` or `swapComponent`, re-query nested nodes;
  - TEXT property defaults are shared across a set; per-variant samples go to an Examples
    row;
  - body text samples keep units with numbers through no-break spaces;
  - every page gets a Doc frame; `figma-state.json` is updated after every call.
- Artifact (`docs/rules/artifact.md`): create the Design System type once through
  quickstart; publish with `root` = `ds` (the session runs in `design/`), `file_path` = `project/design-system.json`,
  only changed files in `files`; `.d.ts` as `text/plain`; read the index before publishing;
  stamp `lastChange`; previews carry the `@dsCard` marker; uploaded assets are
  `/_blob/<id>` and the harness maps them to `ds/upload/`.
- Client material stays in the client container; the studio repository holds none.

## 10. Scripts to generalise

| Script | From Mayor | Change |
|---|---|---|
| `figma/prelude.js` | IDs of Mayor variables hard-coded | look up variables, text styles, effect styles, `_Frame` and icons by name at run time; no IDs |
| `figma/audit.js` | written inline each time | per page: unbound SOLID paints, unstyled text and default names outside instances; overlapping variants in a set; layers whose property references differ between variants of one set; component properties referenced by no layer; text clipped by a clipping ancestor; returns counts and samples |
| `ds/scripts/sweep.js` | inline iframe loop | harness page `_sweep.html` loads every preview, reports JS errors, overflow over 4 px and empty roots; `data-sweep-ignore` for intentional overhangs; result readable with `get_page_text` |
| `ds/scripts/build_harness.py`, `gen_previews.py` | Mayor names | project name and namespace from `PROJECT.md` and `design-system.json` |
| `ds/scripts/check_format.js` | Mayor cases | cases from `ds/fixtures/format-cases.json` |
| `ds/scripts/format_fixtures.js` | new | renders `fixtures/*.json` through the DS format functions into `fixtures/formatted.json` |
| `fonts/font_check.py` | `patch_font.py` was Pixel Code specific | checks glyph coverage for ₽, U+00A0, U+202F, U+2212, Cyrillic; patching stays optional per project |

Mayor Sim is the reference implementation: stage references point to
`~/job/mayor-sim-design` by path for examples; nothing is copied from it into the studio
repository except the generalised scripts and the prompt structure.

## 11. Seed of `lessons.md`

From the Mayor effort: late layout fit (S-08 over 1080 found at the end); Figma font
runtime found mid-build; Figma defects found late (dropped property references after
clone, overlapping variants, a stray INSTANCE_SWAP property in Window, clipped RoundChart
tick); fixed slider position in instances; missing button size L under the variant cap;
hand-typed sample values; work started inside an unrelated repository; a borrowed
`node_modules` for typescript; no git history in the project folder.

## 12. Verification

The pipeline counts as working when:

1. `install.sh` links every skill and agent; `preflight.sh` on this machine prints no ❌.
2. `audit.js`, run read-only on every page of the Mayor Figma file, returns all counts 0;
   each finding it does report is either a real defect (fixed in the Mayor file after the
   user agrees) or a false positive (fixed in the script). Run on a separate test Figma
   file the user creates for the pipeline, with seeded defects (a cloned variant without
   references, overlapping variants, an unbound paint), it reports each seeded defect. No
   test ever writes to a client file.
3. `sweep.js` on the Mayor harness reports 0 errors and 0 overflows.
4. `check_format.js` and `format_fixtures.js` pass on the template's fixtures.
5. Pilot: `new-client.sh _pilot`, then stages 0–3 on a small sample brief (a landing page,
   web-landing profile) end to end, with gates and evidence in `progress.md`. The pilot
   container is deleted afterwards.

## 13. Implementation order

1. `~/job/agent-skills` with the `grilling` fork and its symlink.
2. `studio-design` skeleton, `install.sh`, docs (manifest, playbook, packages, rules,
   lessons, profiles).
3. Template, `new-client.sh`, `preflight.sh`.
4. Scripts (section 10) with their checks.
5. Skill `studio-design` and the stage references.
6. Agents.
7. Verification (section 12).
