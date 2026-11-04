# Road to 30 HQ · changelog

The HQ itself lives as a private Claude artifact (it holds personal data, so its source is
intentionally not stored in this public repo). This file records what changed and when.

## v4 · Crew OS (2026-11-04)

Turns the HQ from a set of tabs with agents attached into one command center the whole crew runs on.

- **Mission board (new Board tab).** One task list across Faith, Family, Fitness, Finances,
  Business, PLV and the day job. Every task has an owner on the crew; "Work it with <agent>"
  opens that agent with the task already briefed. Grouped Late / Today / This week / Later /
  Anytime, filter by area, 10 XP per finished task (up to 3 a day). "Up next" shows on Home.
- **Crew huddles.** Ask one question; 2–6 agents weigh in in turn and build on each other, then
  Deacon chairs and returns a plan of 3–5 dated, owned moves. Add any or all to the board, save
  the huddle as a Doc, or pressure-test it with Deacon. Past huddles are kept and can be re-run.
- **Crew memory.** A shared list of decisions and facts injected into every agent's context,
  Deacon included. Add your own, or approve ones an agent suggests.
- **Shared agent tools.** Every chat agent (and Deacon) can read the board, memory and recent
  huddles, and can propose a task, propose a memory, or offer a handoff to the teammate who owns
  the request. Nothing saves without an Approve tap; handoffs open the teammate with a brief.
- **Life crew: two new agents.**
  - **Ledger · Money manager:** cushion, 30% tax set-aside, budget and take-home math; can
    propose updated cushion numbers.
  - **Hart · Family and wedding planner:** date nights, wedding tasks, the shared prayer list;
    can propose items for the Us tab.
  Their strips also appear on the Money and Us tabs.
- **Ask HQ command bar.** Floating button, `/` or Ctrl/Cmd+K. Type anything: it routes to the
  best agent (with alternates), or adds it to the board, starts a huddle, saves it to crew
  memory, or jumps to any tab or card. Arrow keys + Enter.
- One approval system now handles every proposal type for Deacon and the crew alike.
- All new UI is built from the existing era tokens, so it restyles with all seven daily eras.
