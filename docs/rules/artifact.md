# Artifact rules (Design System type)

Paths written `design/...` are relative to the client container `~/job/clients/<slug>/`; the session runs in `design/`, so commands use paths relative to it.

- Create the artifact once at stage 4 through `Artifact action=quickstart` and the Design System type; record its URL in `PROJECT.md` and `CLIENT.md`.
- Read the artifact's `project/design-system.json` right before every publish; merge, never overwrite fields the type owns.
- Publish with `url` = the artifact, `root` = `ds`, `file_path` = `project/design-system.json`, and only changed files in `files`.
- `index.d.ts` is published with `contentType: text/plain`.
- Stamp `lastChange` (by, via, at, note) in `design-system.json` on every publish.
- Every preview starts with the `<!-- @dsCard … -->` marker; full-page templates add `page` and a width.
- Uploaded assets live at `/_blob/<id>`; keep the local copy in `ds/upload/` and the mapping in `ds/upload/blobs.json` so the harness shows it.
- The artifact is private; the user grants the client access. Remind them at every checkpoint.

## File formats

Paths are relative to `design/`. Examples: `~/job/mayor-sim-design/ds/project/tokens.json`,
`~/job/mayor-sim-design/ds/project/components/bundle.js`,
`~/job/mayor-sim-design/ds/project/components/Button/preview.html`.

- `ds/project/tokens.json`:
  - `color.themes`: `[{ "id", "name" }]`; the first theme is used by the harness.
  - `color.tokens`: `[{ "name", "value" }]`; a value `{other}` is an alias to the token `other`.
  - `type.fonts`: `[{ "family", "file", "weight" }]`; `file` is a path under `ds/project/` (for example `fonts/<Family>-Regular.woff2`).
  - `type.families`: `{ "<key>": "<CSS font stack>" }`; each becomes `--font-<key>`.
  - `type.groups`: text styles `[{ "name", "family", "styles": [{ "name", "fontSize", "lineHeight", "fontWeight", "sample", "usage" }] }]`, where `family` is a `type.families` key; the harness does not read them.
  - Any other group (`spacing`, `radius`, …): `{ "tokens": [{ "name", "value" }] }`; every token becomes a CSS variable `--<name>`.
- `ds/project/components/bundle.js`: one IIFE.
  - First line: `/* @ds-bundle: {"format":4,"namespace":"<NS>","components":[{"name":"<Component>"}, …]} */`, listing every component.
  - Preamble: `var React = window.React; var h = React.createElement;`.
  - Every component is exported on `window.<NS>`.
- `ds/project/components/<Name>/preview.html`: first line `<!-- @dsCard group="…" height=… [width=…] [page] subtitle="…" -->`, written by `ds/scripts/gen_previews.py` from `ds/previews_spec.py`.
