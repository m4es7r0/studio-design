# Stage 0 · Intake

## Inputs
- `CLIENT.md`, `design/PROJECT.md`, the files in `design/brief/`.
- `~/job/studio-design/docs/manifest.md`, `docs/packages.md`, `docs/profiles/`.

## Steps
1. Run `~/job/studio-design/scripts/preflight.sh`; paste its output into `design/progress.md` › Preflight.
2. In-session checks, each as ✅/❌ with a fix in the same table:
   - Figma MCP: `whoami` answers and the seat can edit.
   - Artifact: `Artifact action=quickstart intent=other` lists a Design System type.
   - Browser: `preview_start` with the `ds-harness` configuration serves `ds/`; navigate to `http://localhost:<port>/project/README.md` and see it load. (The sweep page appears with the first previews at stage 5.)
   - Figma fonts: in a read-only `use_figma`, `figma.listAvailableFontsAsync()` contains the intended font family; if not, record a Google stand-in to use.
3. With the user, fill the empty fields of `CLIENT.md` (contact, language, package, rounds, deadlines) and `PROJECT.md` (entry mode, platform profile, target sizes).
4. Ask the user for the Figma file URL for this client; record it in `PROJECT.md` and `design/figma/figma-state.json` (`fileKey`, `fileUrl`).

## Outputs
- `design/progress.md` › Preflight table; filled `CLIENT.md` and `PROJECT.md`; `figma-state.json` with the file key.

## Gate
- No ❌ in the preflight table, or each ❌ accepted by the user for this project and recorded in `decisions.md`.

## Skills and agents
- None beyond the manifest checks.

## Pitfalls
- `docs/lessons.md` 2 (Figma fonts) and 10 (own container).
