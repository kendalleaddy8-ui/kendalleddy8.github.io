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

## 6. FINAL: Thanksgiving 3 lineups (Wed 10:40 PM ET)
**PLAY = `2026-wk12-tg/wed3d/lineups_MILLION.csv`** (fresh-world fair test vs the balanced pick: score 166.5 vs 154.6, P(any top-3) 18.5 vs 15.6 per 10k, P(≥1 cash) 83% vs 78%; worst case 72.8 vs 132.7)

| # | QB | RB | RB | WR | WR | WR | TE | FLEX | DST |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Goff | Swift | Javonte | Burden | Jameson Williams | Raymond | LaPorta | Lamb | Cowboys |
| 2 | Caleb | Gibbs | Barkley | Odunze | D. Smith | D. Cooper | Loveland | Javonte | Bills |
| 3 | Milton | Gibbs | Swift | Odunze | St. Brown | D. Cooper | Spann-Ford | Lamb | Chiefs |

- Safer alternative: `wed3d/lineups_FINAL.csv` (balanced; best worst case).
- Self-check: validator PASS, salaries match, injuries clean, no duplicates. One warning: Darius Cooper in 2 lineups (lesson 21, kept on purpose: "punts can hit").
- Exposure: Swift, Javonte, Lamb, Gibbs, Odunze and Cooper each in 2/3.
- Watch at 11:40 AM: Swift, Gibbs, Barkley, Lamb, Cooper, Spann-Ford (Ferguson OUT assumed).
- New tool tonight: `engine/fairtest.py` grades lineup sets on fresh worlds no search has seen. Use it for the final call between finalists.

## 7. UPDATE: Kendall added 2 lineups (5 total)
Lineups 1–3 = `lineups_MILLION.csv` (locked, already entered). New 4–5 = `wed3d/lineups_ADD2_NEW.csv`; all 5 = `wed3d/lineups_FIVE_FINAL.csv`.
| # | QB | RB | RB | WR | WR | WR | TE | FLEX | DST |
|---|---|---|---|---|---|---|---|---|---|
| 4 | Dak | Gibbs | Barkley | D. Smith | Flournoy | D. Cooper | LaPorta | Cook | Lions |
| 5 | Allen | Gibbs | Barkley | Odunze | D. Smith | DJ Moore | Kelce | Shakir | Eagles |
- Fresh-world test: 5-set score 203.3 (worst 124.7), P(any top-3) 22.2/10k, top-15 7.47/1k, P(>=1 cash) 91% in sim, vs the 3-set 166.5 / 18.5 / 6.07 / 83%. All 3 parallel workers converged to the same pair.
- Warnings: Cooper 3/5, Gibbs 4/5. The cheap Lions/Eagles DSTs face 28+ implied, but forced by the no-shared-DST rule; the shared-Chiefs alternative tested worse (202.2).

## 8. FINAL ENTRY (Thu 12 AM): engine #1-4 + Kendall K4 replacing the Allen lineup
Fresh-world test: 413.8 vs 393.3, top-3 24.0 vs 22.7 per 10k. Caleb in 2 lineups (rule waived on numbers). `wed3d/ENTRY_SHEET.csv`.
- Update: #3 DeVonta Smith -> George Pickens (fresh-world 401.8 vs 401.2; removes 0% Pickens exposure; Dak+Pickens stack).

## 9. ULTIMATE FINAL ENTRY (Thu ~12:30 AM): `wed3d/ENTRY_SHEET.csv` (= ult_w0_0)
Warm full run: 4 workers x 5 starts, all lineups unlocked, seeded from every strong lineup, million objective, dup-QB allowed. Fresh-world test vs previous entry: 537.4 vs 422.1, top-3 31.5 vs 24.5 per 10k, top-15 10.4 vs 8.3 per 1k, worst 337.5 vs 264.3. P(>=1 cash) 81%. Kincaid (Q) in #5: late-swap pivot Spann-Ford or Noah Gray.

## 10. GAME-DAY FINAL (Thu 10:15 AM): `2026-wk12-tg/thu/ENTRY_SHEET.csv`
Rebuilt on Thursday news (totals CHI-DET 56.5, PHI-DAL 49.5, KC-BUF 45.5; CHI CB Gordon OUT; DAL S Locke OUT), 24 + 20 warm searches seeded from all prior bests, 8-world fresh grade: 560.7, top-3 33.75/10k, top-15 10.42/1k, P(>=1 cash) 90%. Overnight run: container restarted mid-run; the 48 unconstrained searches completed, the roles phase was rerun this morning.
- 11:40 AM check: all rostered players active (LaPorta active; Benedet LT plays). DET S Clark + DE Wonnum OUT, CHI S Hicks OUT (same direction as model, no rerun). DAL -9.5. Late-swap checks scheduled 4:12 PM and 8:03 PM ET.
- 4:12 PM late swap: CHI-DET points locked (Gibbs 49.6!). Locked: #3 139.3, #2 113.1, #4 77.3, #1 77.1, #5 23.1. No swaps recommended.
- 8:03 PM: after CHI-DET + PHI-DAL: #3 209.1 FINAL, #2 176.8 (+Bills DST), #4 164.4 (done), #1 154.7 (+Chiefs DST), #5 72.0 (+Allen/Moore/Worthy/Cook). DeVonta Smith 42.6, Gibbs 49.6. KC-BUF: Benford OUT, Kincaid/Gray active. No swaps.
