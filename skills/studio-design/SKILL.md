---
name: studio-design
description: Client studio pipeline from a brief (TZ) through clarification, deliverable choice, per-part style sketches and approval to a coded design system and/or pages, with optional Figma and artifact previews — «studio-design», «новый клиент», «дизайн-система / лендинг для клиента по ТЗ», «продолжаем studio-design», «раунд правок», or work in ~/job/clients/<slug>/design.
---

# studio-design

You run the design pipeline for one client container, `~/job/clients/<slug>/`. The pipeline
repository is `~/job/studio-design`; its docs are the rules you follow.

## Invariants

- Work only inside the client container. Never write client material into `~/job/studio-design`.
- The only write into `~/job/studio-design` is a lesson in `docs/lessons.md` (stage 9, no client names), committed there.
- Paths written `design/...` are relative to the client container `~/job/clients/<slug>/`. The session's working directory is `design/`, so commands use paths relative to it (`ds/scripts/...`, `figma/...`).
- Bare `docs/…` means `~/job/studio-design/docs/…` and bare `rules/…` means `~/job/studio-design/docs/rules/…`; `CLIENT.md` is `../CLIENT.md` from `design/`.
- You run the process; the skills own the design. Research, directions and audits belong to design-agent; building (sketches, foundations, components, screens) to attmpt-design; native platform rules to mobile-design-patterns. studio-design holds no design doctrine of its own.
- The switches in `PROJECT.md` decide which steps run: `Figma:` (yes / no), `Artifact:` (yes / checkpoints / no — checkpoints publishes only at the 🧑 stages 2 and 8), `Themes:`, `Locale:`, `Parts:`, `Directions:`, `Review passes:`. A step for an output that is switched off is skipped and recorded in one line.
- Every stage report carries its own «to confirm» list (rows in `decisions.md`): a choice that changes what the client sees is asked at that stage's checkpoint, not saved for stage 8.
- Every stage follows its reference in `references/`. Read it before starting the stage; it names every input file. Do not look for inputs it does not name.
- A stage ends only when its gate passes and `design/progress.md` records the evidence (command output, the names of the previews or Figma nodes you looked at with your verdict, decision entries). Evidence is pasted, never typed from memory.
- 🧑 checkpoints: prepare the material and the questions in the client's language, then stop. The user takes them to the client; answers go to `design/decisions.md`. At every 🧑 checkpoint remind the user that the artifact and the Figma file, where they exist, are private until they grant the client access.
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

## Skills and agents

| Skill or agent | When | What to pass | How to call |
|---|---|---|---|
| `design-agent` (skill) | stage 2; the audit of the current product in entry mode «redesign» | «called from studio-design», the container paths, `Directions:` and `Parts:` from `PROJECT.md`, the Summary of `design/brief/tz-analysis.md`, the «Moved to stage 2» rows of `decisions.md`, `design/refs/` | invoke the skill; it dispatches its own research agent and returns the research summary and the directions brief |
| `attmpt-design` (skill) | stage 2 «Sketch mode», stages 4–6, stage 9 | the research summary or the frozen sketch, the `PROJECT.md` switches, the target paths in `design/ds/` | invoke the skill |
| `mobile-design-patterns` (skill) | stages 3, 5, 8 on the mobile profile | the screen and the profile | build-spec before attmpt-design; audit at stage 8 |
| `tz-analyst` (agent) | stage 1 and `grilling` fact lookups | the brief files, `design/brief/pages/*/`, the output path `design/brief/tz-analysis.md` given as an absolute path (`~/job/clients/<slug>/design/brief/tz-analysis.md`); for a lookup, the question and the source files | as is |
| `studio-design-reviewer` | stages 2, 5, 6, 8, 9 | the scope, `design/brief/tz-analysis.md`, `design/decisions.md`, `design/PROJECT.md` (package, passes, locale, themes), the profile path, the harness URL `http://localhost:<port>/harness/<Name>.html` (port from `PROJECT.md`) with the preview names, the round file at stage 9, the report path `design/reports/studio-design-reviewer-<stage>.md` | at most `Review passes:` passes per stage |
| `studio-design-figma-builder` | stage 7, only with `Figma: yes` | batch names, code paths, file key, page names, `design/figma/*`, `design/ds/fixtures/formatted.json` | with `run_in_background: false`; make no Figma call of your own until it returns |

Agent reports are not shown to the user; relay what matters. Give every agent exact input and
output paths.

## After every stage

Update `PROJECT.md` (current stage), `progress.md` (evidence) and commit in the client container:
`git -C ~/job/clients/<slug> add -A && git -C ~/job/clients/<slug> commit -m "<Stage N Title-Case Summary>"`.
