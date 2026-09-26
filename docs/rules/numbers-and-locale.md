# Numbers and locale (ru-RU default)

Implemented by `format` in `ds/project/components/bundle.js`, tested by `ds/scripts/check_format.js`.

- Thousands separator U+202F; decimal comma; minus U+2212.
- Units and scale words after a no-break space U+00A0: `120 млн ₽`, `450 000 кв. м`, `4,5 %`.
- Money from 1 млн: млн / млрд / трлн, three significant digits, trailing zeros dropped (`1,2 млрд ₽`), except a forced-scale pair (`0,85 млрд` next to `1,20 млрд`).
- Percent below 10 keeps one decimal. Percentage deltas are in п.п.
- Deltas are signed (`+` / `−`); zero is `0`; no data is `—`.
- Body text in Figma and code keeps a number with its unit through U+00A0 so a line never breaks between them.
- Another locale is a stage 4 decision recorded in `decisions.md`; then `format` and `format-cases.json` change together.
