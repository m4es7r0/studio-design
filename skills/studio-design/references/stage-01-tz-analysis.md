# Stage 1 · TZ analysis 🧑

## Inputs
- `design/brief/*` (the client's files), `CLIENT.md`, `design/PROJECT.md`.

## Steps
1. For every PDF in `design/brief/`: `~/job/studio-design/scripts/py ~/job/studio-design/scripts/pdf_pages.py brief/<file>.pdf brief/pages/<file-stem> --images` (one folder per PDF, so pages never overwrite each other); copy useful embedded images to `refs/`.
2. Dispatch `tz-analyst` with the brief files and `design/brief/pages/*/`; it writes `design/brief/tz-analysis.md`.
3. Read the analysis. Run `grilling` with the user over the decisions it leaves open, passing: output file `design/decisions.md`, client-questions file `design/questions.md`, fact-finder `tz-analyst` with the brief files as sources.
4. Show the user `design/questions.md`; they send it to the client. 🧑 Stop until the answers come back; record each in `decisions.md` and move it to «Answered».

## Outputs
- `design/brief/tz-analysis.md`, `design/brief/pages/`, `design/decisions.md`, `design/questions.md`.

## Gate
- The grilling frontier is empty and every client answer is recorded in `decisions.md`.

## Skills and agents
- `grilling` (with the three caller options), agent `tz-analyst`.

## Pitfalls
- «Как это должно ощущаться» questions are not grilled; they go to stage 2 as directions.
- Facts come from the brief through `tz-analyst`; never ask the user what the brief says.
