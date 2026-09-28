# Playbook

The pipeline for a human reader. The agent follows `skills/studio-design/`.

## Before the first client

`scripts/setup-python.sh`, `scripts/install.sh`, `~/job/agent-skills/install.sh`, `scripts/preflight.sh`.

## A new client

1. `scripts/new-client.sh <slug> --name "Client"` → `~/job/clients/<slug>/`.
2. Fill `CLIENT.md` (contact, language, package, rounds, deadlines).
3. Put the brief into `design/brief/`.
4. Open `~/job/clients/<slug>/design` in the Claude Code desktop app and say «studio-design: stage 0»
   (a session opened at the container root still finds the harness through the root
   `.claude/launch.json`, but stage paths assume `design/`).

## Stages and checkpoints

0 Intake → 1 TZ analysis 🧑 → 2 Direction 🧑 → 3 Layout budget → 4 Foundations → 5 Components →
6 Screens → 7 Figma → 8 QA and handoff 🧑 → 9 Revision rounds 🧑. 🧑 = the agent prepares material and
questions, you take them to the client, the answers go to `design/decisions.md`.

## Resuming

Open the client's `design` folder and say «продолжаем studio-design». The agent reads `PROJECT.md`,
`progress.md`, `decisions.md` and `questions.md` and continues from the recorded stage.

## After a project

Add what went wrong to `docs/lessons.md`; when it changes behaviour, also to the rule or stage
reference it affects. Commit in this repository.
