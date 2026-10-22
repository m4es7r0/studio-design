# Figma rules

Paths written `design/...` are relative to the client container `~/job/clients/<slug>/`; the session runs in `design/`, so commands use paths relative to it.

Read before every `use_figma` call. Load the `figma:figma-use` skill (and `figma:figma-generate-library` for components, `figma:figma-generate-design` for screens). These rules apply only with `Figma: yes` in `PROJECT.md`.

- When attmpt-design scaled the design from a reference frame (web-landing), Figma variables hold the values at that frame's width, and the scale factor is written next to the tokens.
- The figma-generate-library ledger lives in the client container, never in `/tmp`.
- Mutations run one at a time; image capture into a temporary frame may run in parallel with the semantic build.

## Workflow per batch

1. Read `design/figma/figma-state.json`.
2. Paste `design/figma/prelude.js` (and `prelude.project.js`) before the task code; pass component IDs from the ledger.
3. Build one component or one screen per call; return every created and mutated node ID.
4. Run `design/figma/audit.js` on every touched page (read-only calls may run in parallel); all counts must be 0.
5. `get_screenshot` of every new component set and screen; look at it.
6. Update `figma-state.json` (IDs, decisions, completed steps) and add or update the page's Doc frame.

## API rules

- Mutating calls strictly sequential; one page switch per call.
- A file's page list comes from `use_figma` (`figma.root.children`), not `get_metadata`, which can omit pages.
- The MCP runtime sees only Google Fonts: text styles bind to Typography variables with a Google stand-in; the user swaps the family to the real font at the very end, because edits fail after the swap.
- Take style names from `figma.listAvailableFontsAsync()`; they differ between families (for example «SemiBold» in Ysabeau Office, «Semi Bold» in Inter). Filter inside the script and return only the families you check: `use_figma` results over about 20 KB are truncated, and a family cut from a truncated list looks like a face Figma lacks.
- A bound paint carries the resolved variable colour (`P.paint`), otherwise an instance override equal to the main value renders the placeholder colour.
- `clone()` of a variant drops property references: re-bind TEXT, BOOLEAN and INSTANCE_SWAP references after cloning; the audit reports misses as `refMismatch`.
- Hidden instance sublayers take no fill writes: set fills before hiding.
- Instance children cannot be moved, and constraint-scaled layers ignore resize: build continuous-value parts (slider fill, progress) with auto-layout FIXED widths and try an override on an instance before closing the component.
- Plan size variants against the 30-variant cap before building (Mayor had no button size L).
- Append a node to its auto-layout parent before setting FILL.
- After `setProperties` or `swapComponent`, query nested nodes again; earlier references go stale.
- TEXT property defaults are shared across a set; per-variant sample values go to an Examples row of instances.
- A script that throws is rolled back; read the canvas before retrying only when the error says the retry is unsafe.
- Every page gets a Doc frame; component purpose goes into the component or set description.
- Tests and experiments never run in a client file.
