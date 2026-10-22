# Stage 9 · Revision rounds 🧑

## Inputs
- The client's list as received, `CLIENT.md` (rounds included), `design/decisions.md`, `design/brief/tz-analysis.md`, `~/job/studio-design/docs/rules/client.md`.

## Steps
1. Create `design/revisions/round-NN/source/` with the list as received and `round-NN.md` with a table: number, where (registry ID), request, the client's words.
2. Triage every item: ✅ accept, 🔁 accept with a change, ⚠️ push back (reason, evidence, alternative), ❓ question, 💰 outside the package; add its impact (which tokens, components, screens change).
3. Dispatch `studio-design-reviewer` (payload: SKILL.md › Skills and agents) for a second opinion on UX risk; merge its view.
4. Run `grilling` with the user over ⚠️, ❓ and 💰 items (output file `design/decisions.md`); tell `grilling` to append rows in the `| Date | Source | Decision |` table of `design/decisions.md`.
5. Write the reply to the client in their language; the user sends it. Remind the user that the artifact and the Figma file, where they exist, are private until they grant the client access. 🧑 Wait for confirmation.
6. Implement through `attmpt-design` (its style-change protocol lists the files before editing): code and sweep; with `Figma: yes` Figma and `audit.js`; with `Artifact:` not `no` publish. Record before and after previews by name with verdicts in `round-NN.md`.
7. Close the round in `round-NN.md` with the status of every item; add repeating patterns to `~/job/studio-design/docs/lessons.md`.
8. Count the rounds against `CLIENT.md`; when the included rounds are used up, tell the user the next round is a new order.

## Outputs
- `design/revisions/round-NN.md`, `round-NN/source/`, updated code; Figma with `Figma: yes`; the artifact when `Artifact:` is not `no`.

## Gate
- Every item has a final status; sweep OK after the changes (and audit ok with `Figma: yes`); the client confirmed the reply.

## Skills and agents
- `grilling`, `attmpt-design`; agent `studio-design-reviewer`.

## Pitfalls
- Never implement a UX-breaking request silently; never refuse silently (`rules/client.md`).
