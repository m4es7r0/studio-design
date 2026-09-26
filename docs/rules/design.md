# Design rules

- Code is the source of truth; Figma mirrors it. No Figma-only component.
- Tokens are locked: every colour and font in code comes from a token; a missing value becomes a new token first (hallmark).
- Every interactive component ships default, hover, focus, pressed and disabled; add loading, error and success where the component can be in them.
- Layout budget before components: the densest screens are measured at the target size at stage 3.
- Sample values come from `ds/fixtures/` through the format functions; missing data is marked `—` or «to confirm», never invented. No invented metrics in client-visible copy.
- Contrast: WCAG AA (4.5:1 body text, 3:1 large text and UI parts).
- One primary action per view; the brand colour signals, it does not fill surfaces.
