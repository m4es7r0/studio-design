# Rules for agents maintaining the studio-design pipeline

This repository is the pipeline itself, not client work. Client work happens in
`~/job/clients/<slug>/design/` through the `studio-design` skill.

- Read `docs/superpowers/specs/` and `docs/superpowers/plans/` before changing the pipeline.
- Keep one responsibility per file: stage behaviour in `skills/studio-design/references/`,
  hard rules in `docs/rules/`, tool facts in `docs/manifest.md`, pitfalls in `docs/lessons.md`.
- A lesson learned in a client project goes to `docs/lessons.md`, and when it changes behaviour,
  also to the rule or stage reference it affects.
- No client material in this repository: no briefs, references, fonts or screenshots of a client.
- Checks are scripts with tests. Run `tests/run.sh` and `scripts/validate.sh` before every commit.
- Files are in English. Commit messages: one short Title-Case line, no prefix, no body.
- Push only when the user asks for it in the session.
