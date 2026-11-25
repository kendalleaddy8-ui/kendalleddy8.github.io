# Thanksgiving 2026 (CHI@DET 1:00 · PHI@DAL 4:30 · KC@BUF 8:20) — 3-lineup Milly portfolio

Provisional run Tue night (no ESPN values table yet). Pool = FantasyPros DK salaries + prior ESPN Base rescaled to Vegas implied totals,
35% blend with FantasyPros top-10 projections (`build_pool.py`). Explicit Thanksgiving ownership in `overrides.csv`.
Field: 150k entries x 3 samples, top-15/top-150 thresholds (`tg_prep.py`); 3-lineup local search with holdout (`tg_port.py` -> `port.txt`, `lineups_final.csv`).

Portfolio (holdout): P(any top-150) ~1.3% · P(any top-15) ~0.18% (random 3 entries ~0.30% / 0.03%).
Re-run Wed 6:30 PM ET with the ESPN table, final injury designations (Walker, Ferguson, Kincaid), and the Buffalo weather.
