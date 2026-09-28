# Stage 1 · TZ analysis 🧑

## Inputs
- `design/brief/*` (the client's files), `CLIENT.md`, `design/PROJECT.md`, `~/job/studio-design/docs/packages.md`.

## Steps
1. For every PDF in `design/brief/`: `~/job/studio-design/scripts/py ~/job/studio-design/scripts/pdf_pages.py brief/<file>.pdf brief/pages/<file-stem> --images` (one folder per PDF, so pages never overwrite each other); copy useful embedded images to `refs/`.
2. Dispatch `tz-analyst` (payload: SKILL.md › Agents) with the brief files and `design/brief/pages/*/`; it writes `design/brief/tz-analysis.md`.
3. Compare the brief's deliverables with `~/job/studio-design/docs/packages.md` for the package in `../CLIENT.md`; if the brief asks for more, put a scope question to the client (Decisions).
4. Read the analysis. Run `grilling` with the user over the decisions it leaves open, passing: output file `design/decisions.md`, client-questions file `design/questions.md`, fact-finder `tz-analyst` with the brief files as sources (payload: SKILL.md › Agents); tell `grilling` to append rows in the `| Date | Source | Decision |` table of `design/decisions.md`, and that decision questions go under Decisions, requests for data or files under Materials. "How should it feel" questions are not grilled: write one `decisions.md` row per topic, Source «Studio (grilling)», Decision «Moved to stage 2: <topic>».
5. Show the user `design/questions.md`; they send it to the client. 🧑 Stop until the answers come back; record each in `decisions.md` and move it to «Answered». A Materials item moves to «Answered» only when the material arrives.

## Outputs
- `design/brief/tz-analysis.md`, `design/brief/pages/`, `design/decisions.md`, `design/questions.md`.

## Gate
- The grilling frontier is empty and every client answer is recorded in `decisions.md`.

## Skills and agents
- `grilling` (with the three caller options), agent `tz-analyst`.

## Pitfalls
- «Как это должно ощущаться» questions are not grilled; they go to stage 2 as directions through their `decisions.md` rows (step 4).
- Facts come from the brief through `tz-analyst`; never ask the user what the brief says.
