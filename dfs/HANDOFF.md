# HANDOFF: Kendall × Claude DFS (all sessions, Weeks 9–12 of 2026)

Paste this into a fresh chat with "Read dfs/HANDOFF.md, dfs/HANDBOOK.md and dfs/ENGINE.md, then continue."

## 1. Who / goal
- **Kendall** (DraftKings NFL DFS, account K9King15) plays GPPs: mostly Millionaire-style Classic plus Showdowns.
- Goal: win the grand prize, then turn this engine into an app.
- Kendall wants:
  - Every angle (Vegas, injuries, roles, DvP, trenches, WR/CB, TE vs LB/S, DST vs offense, coaching, weather, props, ownership, field sim)
  - Ambitious, outside-the-box thinking
  - A self-evaluation before every handoff
  - Clean tables, best lineup first, positives before negatives
  - His hunches tested with numbers
- Every change gets committed and pushed to branch `claude/inspiring-tesla-hdzf9e` (a stop hook enforces it).
- No guarantees: always give honest odds.

## 2. Where everything is (repo `dfs/`)
- `HANDBOOK.md`: strategy v4, the §8A angle checklist and engine run order, the §12 self-evaluation, and lessons 1–30.
- `ENGINE.md`: the app spec (inputs, 8-step pipeline, rules enforced in code, outputs, roadmap).
- `results.csv`: graded results log.
- `engine/`: all the modules.

| Module | Role |
|---|---|
| `fetch.py` | Downloads, ESPN table, DK injury report, page text |
| `pipeline.py` | Projection multipliers, ownership model, `min_base` |
| `sim.py` | Correlated sims with game script, backfield split, target competition, QB vulture (`QBRUN`) |
| `run_week.py` | Candidate lineups |
| `hunch_cands.py` | Forced-angle candidates |
| `fieldprep.py` | 3 noisy fields × sim sets A/B/C, places 3/15/150 |
| `portfolio.py` | Duplicate-aware iterated local search; `--seed0` for parallel workers; hunch/force tests |
| `merge_port.py` | Merges parallel workers |
| `regrade.py` | Mandatory tie-breaker, default 8 new worlds (10 total) |
| `stress.py` | "X has a day" worlds |
| `warmstart.py` | Search seeded from prior best lineups |
| `best_subset.py` | Best k of n lineups |
| `million.py` | Top-3-heavy variant |
| `cashline.py` | Cash odds |
| `selfeval.py` | Automatic checks (md + json) with §7.2 warnings |
| `slate.py` | One command, reads `<week>/slate.json`, runs forks |
| `validate.py` | Lineup rules |
| `boxscore.py`, `lateswap.py` | Live scoring and late swap |

- Week folders: `2026-wk09…`, `2026-wk10…`, `2026-wk11…`, and `2026-wk12-tg/` (Thanksgiving, see §4).

## 3. Rules that are now law (details in HANDBOOK §8A, §12, lessons)
1. **Projections:** ESPN DK values table, or on holiday/Thursday slates Mike Clay's *Fantasy Playbook* (has every game), with team totals moved halfway to Vegas.
2. **Clay weeks:** matchup layers are small residual nudges only, since Clay already prices matchups. The coaching layer always stays (lessons 28–30).
3. **Layers every slate:**
   - Vegas and line movement
   - Injuries (the report overrides projections; every injury fork is its own folder)
   - Role changes
   - Coaching (pace, PROE, 4th-down aggression, scheme familiarity, OL news)
   - Weather
   - Trenches (ESPN win rates: PBWR vs PRWR, RBWR vs RSWR)
   - WR vs CB and scheme vs scheme (Clay grades, ESPN Matchup Rankings)
   - TE vs LB/S
   - DST vs offense
   - Ownership: explicit Own for every player ≥ $4k on short slates, with σ 0.30 noise
4. **Search:**
   - Full player pool (`min_base` 3.5; punts can hit)
   - ≥ 900 candidates plus hunch/punt locks
   - Duplicate-aware top-3/15/150 objective (40/10/1)
   - 12–24 restarts, run in parallel
   - Warm start after any layer change
5. **Pick:** the best mean over all projection-noise worlds (regrade), never the raw search pick (lessons 26 and 28). Report the worst case. Stress-test Kendall's "X has a day."
6. **Self-evaluation always last** (`selfeval.py`):
   - validator, salary match, injury sweep, exposures, duplicates, cash odds
   - warnings: same cheap punt in 2+ lineups, more than 2 near-punts, same-team RB+RB, two TEs, a DST facing 27+ implied
7. **Hard lineup rules:**
   - ≤ 3 per team
   - QB stack plus bring-back (unless the spread is ≤ −9)
   - distinct QBs and no shared DST
   - nobody in every lineup
   - latest kick in FLEX
8. **Kendall's lessons:**
   - Lead RBs on big favorites are core (L1).
   - Never fade a smash-spot chalk workhorse on ownership alone (L22).
   - Vary cheap punts across lineups (L21), but punts can hit.
   - Average duplicates over ≥ 3 fields (L23).

## 4. Thanksgiving 2026 (Thu Nov 26: CHI@DET 1:00 · PHI@DAL 4:30 · KC@BUF 8:20), 3 lineups
- **Salaries:** FantasyPros DK salary-changes page (`2026-wk12-tg/fp_salaries.csv`).
- **Projections:** Clay's Week 12 Playbook (`wed*/clay_playbook.csv`).
- **News:**
  - Walker OUT (Emmett Johnson leads)
  - KC LT Jaylon Moore OUT
  - PHI CB Jonathan Jones OUT
  - Kincaid, Noah Gray, Benford Q
  - Ferguson DNP all week (treated OUT)
  - Hurts on IR (Milton starts)
- **Lines:** CHI −1.5 / 55.5 · DAL −8.5 / 47.5 · BUF −2.5 / 46.5 (opened 49.5; rain about 88%, gusts in the 20s).
- **Run history:**
  - Tue stand-in run → v3 → v4 engine
  - Wed `wed/` (Clay) → `wed5/` (5 lineups, full pool) → `wed3c/` (coaching restored) → `wed3t`/`wed3m`/`wed3x` (trenches, WR/CB + scheme, TE/LB/S) → **`wed3d/` = FINAL** (all layers plus DST vs offense, 24 parallel restarts, 10-world regrade, warm start, contender showdown)
  - `lineups_MILLION.csv` = the top-3-heavy alternative
- **Kendall's hunch tests:** Gibbs+Walker(+E. Johnson), Lamb, Milton+Lamb, Allen, Loveland. Each was graded every run, and they're in `port_v4.txt` / `regrade_v4.pkl`.
- **FINAL lineups:** see §6 (filled in when the run finishes).

## 5. Scheduled tasks and next steps
1. **Thu 11:40 AM ET** (scheduled task `trig_01Q3AouHX6HbJdk17P48mCwi`):
   - re-pull the DK injury report, ESPN inactives and the BUF weather
   - swap if needed, then schedule late-swap checks at about 4:15 and 8:05 PM ET
2. **Late swap:** KC–BUF players kick at 8:20 and can be changed until then.
3. **Fri:** Kendall sends results → `boxscore.py` → `results.csv` → post-mortem → recalibrate.
4. **Open items:**
   - prop/ATD market data (no reachable source)
   - Dallas G Booker missing from the trench layer
   - DK salary CSV upload would be nice to have
   - "dynamic workflows" / ultracode is an app setting Claude can't toggle
5. **Token-saver mod** (origin/main `claude-mods/token-saver`):
   - installed byte-identical in `/root/.claude/dev-mods/<session>/token-saver`, validated, 3/3 tests pass
   - loaded; the `token-saver:scout` agent is active
   - keep the Input Router from condensing DFS number tables: read them in ranges, or say "full output"

## 6. FINAL (filled when the run finishes)
_pending_
