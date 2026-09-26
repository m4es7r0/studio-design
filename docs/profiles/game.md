# Profile: game

From the Mayor Sim effort (`~/job/mayor-sim-design`).

- Target: 1920 × 1080; also the minimum resolution the brief names.
- HUD lives on the edges; the scene in the centre stays free (Mayor: two 460 px rails and 32 px margins leave 936 px). What does not fit goes into a window or a drawer, never into the centre.
- Windows open over the scene and close only through their ×; several windows may stack; one is focused.
- One primary action per screen (Mayor: «Завершить ход»); the brand colour is a signal, not a surface.
- Layout budget (stage 3): the main game screen in every state (active, waiting, windows open) at 1080 height, with the longest labels and the largest numbers from the fixtures.
- Stage 8 checks: every state fits 1080; stress values (64-character names, 100 трлн ₽, the largest window content).
