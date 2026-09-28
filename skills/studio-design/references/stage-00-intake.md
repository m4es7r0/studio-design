# Stage 0 · Intake

## Inputs
- `CLIENT.md`, `design/PROJECT.md`, the files in `design/brief/`.
- `~/job/studio-design/docs/manifest.md`, `docs/packages.md`, `docs/profiles/`.

## Steps
1. Run `~/job/studio-design/scripts/preflight.sh`; paste its output into `design/progress.md` › Preflight.
2. Run `npm install --no-audit --no-fund` in `design/` (needed by `npm run check:types`); record ✅/❌ as a row of the Preflight table. Commit `design/package-lock.json` with the stage, so `tsc` stays reproducible.
3. With the user, fill the empty fields of `CLIENT.md` (contact, language, package, rounds, deadlines) and `PROJECT.md` (entry mode, platform profile, target sizes).
4. Ask the user for the Figma file URL for this client; record it in `PROJECT.md`, in `../CLIENT.md` › Links and access, and in `design/figma/figma-state.json` (`fileKey`, `fileUrl`).
5. In-session checks, each as ✅/❌ with a fix in the same table:
   - Figma MCP: `whoami` shows a Full seat and a read-only `use_figma` lists the file's pages (file from step 4). Any authenticated Figma MCP server that offers `use_figma` will do (the claude.ai connector works without an interactive login; the Claude Code plugin server needs OAuth); record which server was used in the Preflight table. Take the page list from `use_figma`, not `get_metadata` (it can omit pages).
   - Artifact: `Artifact action=quickstart intent=other` lists a Design System type.
   - Browser: `preview_start` with the `ds-harness` configuration serves `ds/`; navigate to `http://localhost:<port>/index.html` and see it load. (`http.server` serves `.md` without a charset, so Cyrillic in `/project/README.md` breaks; the sweep page appears with the first previews at stage 5.)
   - Figma fonts: only for font families known at intake (entry mode «brand book» or «existing DS»): in a read-only `use_figma` (load `figma:figma-use` first), `figma.listAvailableFontsAsync()` contains the family; if not, record a Google stand-in to use. Otherwise (entry mode «from scratch» or «redesign») record «deferred to stage 2» in the Preflight table: stage 2 checks every proposed face.

## Outputs
- `design/progress.md` › Preflight table; filled `CLIENT.md` and `PROJECT.md` with the Figma file URL; `figma-state.json` with the file key and URL.

## Gate
- No ❌ in the preflight table, or each ❌ accepted by the user for this project and recorded in `decisions.md`.

## Skills and agents
- None beyond the manifest checks.

## Pitfalls
- `docs/lessons.md` 2 (Figma fonts), 10 (own container), 13 (session root) and 17 (Figma font check at stage 2).
