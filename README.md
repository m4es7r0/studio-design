# studio-design

A repeatable pipeline from a client brief (TZ) to a coded design system (Claude Design artifact)
and a Figma library. Spec: `docs/superpowers/specs/2026-09-26-studio-design-pipeline-design.md`.

## Start a client

1. `scripts/setup-python.sh` (once per machine) and `scripts/install.sh` (after every pull).
2. `scripts/preflight.sh` — fix every ❌ it prints.
3. `scripts/new-client.sh <slug> --name "Client name"` — creates `~/job/clients/<slug>/`.
4. Put the client's brief files into `~/job/clients/<slug>/design/brief/`.
5. Open `~/job/clients/<slug>/design` in the Claude Code desktop app (Code tab) and say
   «studio-design: stage 0».

The pipeline end to end: `docs/playbook.md`. Tools and skills: `docs/manifest.md`.

## Check the pipeline

```bash
tests/run.sh && scripts/validate.sh
```
