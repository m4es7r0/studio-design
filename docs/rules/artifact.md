# Artifact rules (Design System type)

- Create the artifact once at stage 4 through `Artifact action=quickstart` and the Design System type; record its URL in `PROJECT.md` and `CLIENT.md`.
- Read the artifact's `project/design-system.json` right before every publish; merge, never overwrite fields the type owns.
- Publish with `url` = the artifact, `root` = `design/ds`, `file_path` = `project/design-system.json`, and only changed files in `files`.
- `index.d.ts` is published with `contentType: text/plain`.
- Stamp `lastChange` (by, via, at, note) in `design-system.json` on every publish.
- Every preview starts with the `<!-- @dsCard … -->` marker; full-page templates add `page` and a width.
- Uploaded assets live at `/_blob/<id>`; keep the local copy in `ds/upload/` and the mapping in `ds/upload/blobs.json` so the harness shows it.
- The artifact is private; the user grants the client access. Remind them at every checkpoint.
