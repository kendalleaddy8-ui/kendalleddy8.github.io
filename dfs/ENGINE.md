# DFS Engine v4: app spec (Kendall × Claude)

Built from Weeks 9–12 of 2026. The goal: one command per slate today, an app tomorrow. Strategy and lessons live in `HANDBOOK.md`. This file is the *system*: inputs, pipeline, rules enforced in code, outputs.

## 1. One command
```
cd dfs/engine
DFS_SCRATCH=<scratch dir> python3 slate.py ../2026-wkNN            # reads ../2026-wkNN/slate.json, runs every fork too
python3 slate.py ../2026-wkNN --skip-to 4                          # re-run from the portfolio step
```

## 2. Inputs (one folder per slate; one sub-folder per injury fork)

| File | What | Source |
|---|---|---|
| `espn_pool.csv` | Name, Team, Opponent, Pos, Base, Salary | ESPN DK values table, or Clay's Fantasy Playbook + a salary list (`build_pool*.py`) |
| `injuries.csv` | Name, Status | DK Network injury report (`fetch.py injuries`) |
| `lines.csv` | Team, Opponent, Spread, Total, OpenTotal, Kick, PROE, Pace, WxPass, WxRun, WxDST | ESPN odds + weather + coaching notes |
| `overrides.csv` | Name, Base, Mult, Own, Status, Tag, Note | analyst layer: roles, ownership, coaching, news (every row has a Note) |
| `trenches.csv` (optional) | Team, PassProEdge, RunBlockEdge | OL/DL notes |
| `slate.json` | n, qbs, cands, shared, locks, hunch, force, stress, salaries, forks | the run config: Kendall's hunches go here |

## 3. Pipeline (`slate.py`)

| # | Step | Module | Rule it enforces |
|---|---|---|---|
| 1 | Projections + sim candidates | `pipeline.py`, `run_week.py`, `sim.py` | OUT/IR/D removed; multiplier stack capped 0.80–1.25×; ≥ 900 candidates; every QB explored |
| 2 | Forced-angle candidates | `hunch_cands.py` | every hunch/angle gets real candidates, not just a mention |
| 3 | Fields + sim sets | `fieldprep.py` | 3 noisy-ownership fields (σ 0.30); A for search; B and C with projection noise (σ 0.12); places 3/15/150 |
| 4 | Portfolio search | `portfolio.py` | dup-aware top-3/15/150 objective; 12 restarts × kicks; validator on every move; no shared DST; hunch/force tests |
| 5 | Tie-breaker | `regrade.py` | **mandatory**: 4 new projection-noise worlds; rank by 6-world mean |
| 6 | Stress worlds | `stress.py` | "X has a day": the final must hold up there too |
| 7 | FINAL | `slate.py` | final = best 6-world mean (never the raw search pick); DK slot order with the latest kick in FLEX |
| 8 | Self-evaluation | `selfeval.py` | always last; writes `selfeval_<tag>.md/.json` |

## 4. Simulation model (`sim.py`)
- Lognormal outcomes with mean = Proj. CV: QB 0.40, RB 0.55, WR 0.65, TE 0.70, DST 0.85.
- Shared factors: game (shootout/slog), team pass success, team rush success (ρ 0.35).
- SCRIPT layers:
  - game-script margin (leading team's RBs/DST up, trailing team's passing up)
  - zero-sum backfield split (same-team RBs ≈ −0.10)
  - zero-sum target competition
  - rushing-QB goal-line vulture (`QBRUN`)
- DSTs fall when the opponent's offense succeeds or the game shoots out.

## 5. Hard rules (code)
- **Lineup rules (`validate.py`):**
  - 9 players, ≤ $50,000, DK slots
  - ≤ 3 per team (excluding DST)
  - no DST vs your own players
  - QB stack + bring-back unless spread ≤ −9
  - distinct QBs
  - ≤ `shared` overlap per pair
  - nobody in every lineup
- No shared DST across lineups.
- Final pick by 6-world mean; report the worst case.
- Self-evaluation before every handoff; warnings are shown to Kendall, never hidden.

## 6. Soft rules (selfeval warns)
- The same cheap punt (≤ $4,000) in 2+ lineups (lesson 21).
- Questionable players rostered → name the pivot.
- A lineup duplicated ≥ 3× in a simulated field.
- A rostered player ruled OUT or doubtful → hard warning.

## 7. Outputs (app screens)

| File | Screen |
|---|---|
| `lineups_FINAL.csv` | "Your lineups": Slot, Name, Team, Salary, Proj, Own, Kick, Lineup |
| `selfeval_<tag>.json` | "Checks": validator, salary match, injury flags, exposures, QBs/DSTs, per-lineup top-3/15/150, cash %, dups, swappable players, warnings, 6-world grades |
| `regrade_<tag>.pkl`, `port_<tag>.txt` | "Why this pick": finalists, hunch tests and their scores |
| `stress` output | "What if X goes off" |

## 8. Roadmap to the app
1. Data connectors: DK salary CSV upload, injury report, odds, weather, Clay playbook (all scripted in `fetch.py` / `build_pool*.py`).
2. `slate.py` as the API: config in, JSON out.
3. UI: lineup cards in DK slot order; a hunch box that writes `slate.json` locks/forces; a fork toggle ("if Walker OUT"); a late-swap screen (`lateswap.py`); a results/calibration log (`results.csv`).
4. Calibration loop: after every slate, `boxscore.py` → `results.csv` → refit CVs, correlations, ownership.
