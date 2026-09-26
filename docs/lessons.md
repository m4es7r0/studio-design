# Lessons

Symptom → cause → rule. Append after every project; when a lesson changes behaviour, update the
rule or stage reference it names.

1. S-08 did not fit 1080, found at the very end → components were built before any screen → stage 3 layout budget (`stage-03-layout-budget.md`).
2. The custom font could not be used in Figma, found mid-build → the Figma MCP runtime sees only Google Fonts → stage 0 font check and Typography variables with a stand-in (`rules/figma.md`).
3. A cloned variant lost its Name and Value bindings → `clone()` drops property references → re-bind after cloning; `audit.js` `refMismatch`.
4. Variants overlapped inside a set → positions not re-laid after adding variants → `audit.js` `overlappingVariants`.
5. The Unfocused window showed a pink button instead of content → a stray INSTANCE_SWAP property bound the slot → `audit.js` `unusedProps` and `refMismatch`.
6. The «10» tick of a chart was cut → a clipping frame narrower than its text → `audit.js` `clippedText`.
7. Sliders in templates stuck at 25 % → handle position cannot be overridden in an instance → build continuous parts with auto-layout widths (`rules/figma.md`).
8. No button size L in Figma → the 30-variant cap was hit → plan size variants first (`rules/figma.md`).
9. Sample values typed by hand → no shared data → `ds/fixtures/` and `format_fixtures.js`.
10. Work started inside an unrelated repository and borrowed its `node_modules` → no own project container → `new-client.sh` and the client `package.json`.
11. No history of the design folder → it was not a git repository → every client container is one.
