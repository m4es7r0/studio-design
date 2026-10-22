# Packages

| Package | Stages | Stage 6 and 7 scope |
|---|---|---|
| «ДС» | 0–9 | stage 6 builds the key screens named at stage 1 (by default 1–2 templates from the layout budget); stage 7, with `Figma: yes`, builds the components plus those screens |
| «ДС + экраны» | 0–9 | every screen and state named at stage 1 from the registry of `brief/tz-analysis.md` |
| «ДС + код для разработки» | not built | — |

The package and the number of included revision rounds are set in `CLIENT.md` by the contract.
When a request needs a stage outside the package, it is a change request (💰 in stage 9).

## Deliverable options (stage 0 switches and stage 1 list)

| Option | Values | Default |
|---|---|---|
| Outputs | code always; the artifact (`Artifact: yes / checkpoints / no`); Figma (`Figma: yes / no`) | `Artifact: checkpoints`, `Figma: no` |
| Order | system first (foundations → components → screens) or pages first (foundations → pages → components extracted) | system first for products, pages first for landings and sites; foundations always come first |
| Design-system depth | 1 foundations (tokens, type, colour) · 2 + core components · 3 + full library with every state | 2 |
| Screens | none · key (named) · all in the registry | key |
| Directions | from scratch 3 · brand book 1 · redesign 2 · existing DS 0 | by entry mode |
| Review passes | per stage | 2 |
