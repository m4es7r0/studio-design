---
name: studio-design
description: Orchestrates the studio design service for a client — from a brief (TZ) to a coded design system (Claude Design artifact) and a Figma library, stage by stage with gates. Use when the user says «studio-design», «новый клиент», «дизайн-система для клиента», «продолжаем studio-design», «раунд правок», or works inside ~/job/clients/<slug>/design.
---

# studio-design

You run the design pipeline for one client container, `~/job/clients/<slug>/`. The pipeline
repository is `~/job/studio-design`; its docs are the rules you follow.

## Invariants

- Work only inside the client container. Never write client material into `~/job/studio-design`.
- The only write into `~/job/studio-design` is a lesson in `docs/lessons.md` (stage 9, no client names), committed there.
- Paths written `design/...` are relative to the client container `~/job/clients/<slug>/`. The session's working directory is `design/`, so commands use paths relative to it (`ds/scripts/...`, `figma/...`).
- Bare `docs/…` means `~/job/studio-design/docs/…` and bare `rules/…` means `~/job/studio-design/docs/rules/…`; `CLIENT.md` is `../CLIENT.md` from `design/`.
- Every stage follows its reference in `references/`. Read it before starting the stage; it names every input file. Do not look for inputs it does not name.
- A stage ends only when its gate passes and `design/progress.md` records the evidence (command output, the names of the previews or Figma nodes you looked at with your verdict, decision entries). Evidence is pasted, never typed from memory.
- 🧑 checkpoints: prepare the material and the questions in the client's language, then stop. The user takes them to the client; answers go to `design/decisions.md`. At every 🧑 checkpoint remind the user that the artifact and the Figma file are private until they grant the client access.
- Decisions belong to the user and the client. Agents report; you decide nothing on the client's behalf.
- Files, code and comments are in English; everything the client reads is in the client's language (`CLIENT.md`).
- Rules: `~/job/studio-design/docs/rules/*.md`. Tools: `docs/manifest.md`. Pitfalls: `docs/lessons.md`.

## Start or resume

0. Check that the working directory is `~/job/clients/<slug>/design`. If it is not, stop and ask the user to open a new session in that folder: moving the session with `change_directory` does not rebind the browser tool.
1. Read `CLIENT.md`, `design/PROJECT.md`, `design/progress.md`, `design/decisions.md`, `design/questions.md`.
2. The current stage is the one in `PROJECT.md`. If a gate of that stage is open, finish it first.
3. Say in one line where the project stands and what comes next.

## Stages

| # | Reference | Checkpoint |
|---|---|---|
| 0 | `references/stage-00-intake.md` | |
| 1 | `references/stage-01-tz-analysis.md` | 🧑 |
| 2 | `references/stage-02-direction.md` | 🧑 |
| 3 | `references/stage-03-layout-budget.md` | |
| 4 | `references/stage-04-foundations.md` | |
| 5 | `references/stage-05-components.md` | |
| 6 | `references/stage-06-screens.md` | |
| 7 | `references/stage-07-figma.md` | |
| 8 | `references/stage-08-qa-handoff.md` | 🧑 |
| 9 | `references/stage-09-revisions.md` | 🧑 |

Skip stages the package excludes (`~/job/studio-design/docs/packages.md`). Package «ДС + код для
разработки» is not built: say so.

## Agents

| Agent | When | What to pass | How to dispatch |
|---|---|---|---|
| `tz-analyst` | stage 1 and `grilling` fact lookups | the brief files, `design/brief/pages/*/`, the output path `design/brief/tz-analysis.md` given as an absolute path (`~/job/clients/<slug>/design/brief/tz-analysis.md`); for a lookup, the question and the source files | as is |
| `design-scout` | stage 2 | `mode: survey` (or `mode: quick` for one decision), the platform profile path, the Summary of `design/brief/tz-analysis.md`, and «open your own browser tab» | with `model: opus` (its own frontmatter says sonnet), before the harness is in use |
| `studio-design-reviewer` | stages 2, 5, 6, 8, 9 | the scope, `design/brief/tz-analysis.md`, the profile path, the harness URL `http://localhost:<port>/harness/<Name>.html` (port from `PROJECT.md`) with the preview names, the round file at stage 9 | as is |
| `studio-design-figma-builder` | stage 7 | batch names, code paths, file key, page names, `design/figma/*`, `design/ds/fixtures/formatted.json` | with `run_in_background: false`; make no Figma call of your own until it returns |

Agent reports are not shown to the user; relay what matters. Give every agent exact input and
output paths.

## After every stage

Update `PROJECT.md` (current stage), `progress.md` (evidence) and commit in the client container:
`git -C ~/job/clients/<slug> add -A && git -C ~/job/clients/<slug> commit -m "<Stage N Title-Case Summary>"`.
