# Design rules

- Code is the source of truth; Figma mirrors it. No Figma-only component.
- Tokens are locked: every colour and font in code comes from a token; a missing value becomes a new token first (hallmark).
- Every interactive component ships default, hover, focus, pressed and disabled; add loading, error and success where the component can be in them.
- Layout budget before components: the densest screens are measured at the target size at stage 3.
- Sample values come from `ds/fixtures/` through the format functions; missing data is marked `—` or «to confirm», never invented. No invented metrics in client-visible copy.
- Contrast: WCAG AA (4.5:1 body text, 3:1 large text and UI parts).
- One primary action per view; the brand colour signals, it does not fill surfaces.
- Checks are committed scripts (`ds/scripts/sweep.js`, `ds/scripts/measure.js`, `figma/audit.js`, `ds/scripts/check_format.js`, `fonts/font_check.py`); never write a check ad hoc in a session.
- Client material (briefs, references, fonts, screenshots, client names) stays in the client container. The studio repository, including `docs/lessons.md`, holds none; write lessons without client names.
- Stage references name every input file; agents never search for inputs on their own.
