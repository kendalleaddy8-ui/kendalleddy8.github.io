# Thanksgiving 2026 (CHI@DET 1:00 · PHI@DAL 4:30 · KC@BUF 8:20) — 3-lineup Milly portfolio

Provisional run Tue night (no ESPN values table yet). Pool = FantasyPros DK salaries + prior ESPN Base rescaled to Vegas implied totals,
35% blend with FantasyPros top-10 projections (`build_pool.py`). Explicit Thanksgiving ownership in `overrides.csv`.
Field: 150k entries x 3 samples, top-15/top-150 thresholds (`tg_prep.py`); 3-lineup local search with holdout (`tg_port.py` -> `port.txt`, `lineups_final.csv`).

Portfolio (holdout): P(any top-150) ~1.3% · P(any top-15) ~0.18% (random 3 entries ~0.30% / 0.03%).
Re-run Wed 6:30 PM ET with the ESPN table, final injury designations (Walker, Ferguson, Kincaid), and the Buffalo weather.

## v3 (Tue night, after Kendall: "do better, x100, outside the box")
Upgrades: DvP layer (FantasyPros points-allowed: DAL D #4 QB / #1 RB / #3 WR allowed, BUF stingy vs QB, KC fewest to WRs,
DET most TE yds, DET D without Hutchinson/Campbell), Walker-in and Walker-out worlds, ownership noise (3 fields, sigma .30), projection noise
on holdout sets B and C (sigma .12), 50k sims x 3 sets, 1,142 candidates incl. forced hunch builds, iterated local search (10 starts x 4 kicks),
robust pick by mean(B,C) (`robust_pick.py`), Milton-boom stress test (`milton_stress.py`).

Final (Walker plays) = `lineups_v3.csv`: Dak/PHI-DAL game stack · Milton+Smith+Goedert · Goff+ARSB+LaPorta. #1 on mean(B,C) 45.6 AND #1 in the Milton-boom world.
- Kendall's Gibbs+Walker portfolio: 43.2 (close 2nd, ~5% worse). Gibbs+Walker+E.Johnson: 30.6. Gibbs+E.Johnson: 25.5.
- 2nd Milton lineup instead of Goff: A 35.8 vs 35.1, B 29.9 vs 42.1 -> rejected (C-only win was selection bias).
- Walker OUT before lock -> use wout portfolio "search1" (most robust: mean 38.0, worst 34.7). Walker game-time -> keep v3, late-swap Walker -> Emmett Johnson (KC 8:20).

## v4 FINAL (engine v4: script/backfield/vulture sim, dup-aware top-3/15/150 objective, rain+wind BUF, 6-world tie-breaker)
Walker plays -> `lineups_finalist1.csv` (6-world mean 102.1, Milton-boom 111.4 = best of all; includes Gibbs+Walker and Milton+Lamb).
Walker OUT before lock -> `wout/lineups_PICK.csv` (77.5, most robust). Walker game-time -> keep finalist1; FLEX Walker -> Emmett Johnson at 8:05.
Cash odds (synthetic field, optimistic vs a real sharp field): P(>=1 of 3 cashes) 73% (finalist1) / 74% (wout).
Search pick (v4) placed 5th of 10 on the 6-world regrade: lesson 26 again, regrade.py is now mandatory.
