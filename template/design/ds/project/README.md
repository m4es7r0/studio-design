# __CLIENT_NAME__ UI Kit

If the client sees the artifact before stage 4, put a short note in the client's language at the top of this file.

Namespace `__NAMESPACE__`. Principles, colour roles and component rules are written at stage 4.

## Numbers

Every number on screen goes through `__NAMESPACE__.format`; nobody types a formatted value.

- Thousands: narrow no-break space U+202F (`75 000`). Decimal comma (`4,5`).
- Minus: U+2212 (`−350`). Deltas are always signed; a zero delta is `0`, no data is `—`.
- Units and scale words follow the number after a no-break space U+00A0 (`120 млн ₽`, `450 000 кв. м`).
- Money from 1 млн: млн / млрд / трлн with three significant digits, trailing zeros dropped
  (`1,2 млрд ₽`), except a forced-scale pair that must read in one unit (`0,85 млрд` / `1,20 млрд`).
- Percent below 10 keeps one decimal (`4,5 %`); percentage deltas are in п.п. (`+0,7 п.п.`).
