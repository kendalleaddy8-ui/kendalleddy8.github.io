# NFL DFS GPP Handbook v3 — Kendall × Claude
**DraftKings Classic & Showdown · 2026–27 season · large-field GPPs (Millionaire Maker, $20 TNF/MNF showdowns) · 1–3 lineups**

> **How to use:** paste this whole file into a new chat at the start of each slate, along with the kickoff prompt in §0.
> **Code:** repo `kendalleaddy8-ui/kendalleddy8.github.io`, folder `dfs/`. The engine is in `dfs/engine/`, and each week gets a folder `dfs/2026-wkNN/`.
> **v3 (Week 9, after the DK Network + ESPN access was turned on):** rebuilt around a real data pipeline (ESPN full salary table + DK Network injury report → simulator → rules check). This replaces v1/v2, so don't paste older versions alongside it.

---

## 0. Kickoff prompt (paste with the handbook)

```
Week __ · Slate: [Main Classic / TNF Showdown / MNF Showdown / other] · Contest: [Milly / $20 SD / other], field ~____
Lineups: __ · DKSalaries.csv attached: [yes/no] · Time now: ____ ET
My hunches / players to test: ____            (every one gets a number in the angle table)
Always exclude: Omar Cooper Jr., ____
Last week's results (scores, finishes, notes): ____
Run Handbook v3: fetch → verify → model → sim + angle matrix → portfolio → self-evaluation → handoff. Best overall lineup first.
```

**Upload `DKSalaries.csv` when you can** (DK lobby → contest → Export). It's the only source that settles salary conflicts (Week 9 example: DK Network listed Tyler Shough at $6,000 and ESPN at $5,700). Without it, ESPN's table is the fallback (§3).

---

## 1. Edge philosophy

1. **GPPs pay the top.** Maximize **P(lineup reaches the first-place score range)**, not average points. A lineup that scores 150 typically but can't reach 240 is worth less than one that scores 140 typically and reaches 240 one week in fifty.
2. **Three levers:** **Ceiling** (players who can score 2–3× their median) × **Correlation** (ceilings that happen together) × **Uniqueness** (when we hit, we don't split first place).
3. **Role changes are the most repeatable edge.** DK prices are set by Wednesday, and injury news after that creates mispriced players (Lesson 2: Bernard 25.7 on a 5.5 average).
4. **Field awareness.** Fade chalk that's *fragile* (a narrow path to points). Play chalk that's *robust* (workhorse RB on a big favorite: Lesson 1, Gibbs 32.7 when faded).
5. **Test Kendall's hunches with numbers** (Lesson 5). Week 9: the sim on its own picked workhorse RBs (Walker, McCaffrey, Gibbs). On full ESPN data, the Shedeur angle ranked #2 of 13 QBs.
6. **Honesty about uncertainty.** The top ~10 QB angles are usually within ~0.5 points of each other. That's smaller than our projection error, so inside that band football judgment and Kendall's read break the tie.

---

## 2. Weekly timeline (ET)

| When | Task |
|---|---|
| **Mon/Tue** | Post-mortem (§13). Log results in `dfs/results.csv`. Update lessons. |
| **Tue–Wed** | Salaries post. ESPN DK values article + DK Network first looks. Record **opening lines** in `lines.csv` (`OpenTotal`). |
| **Wed–Fri** | Practice reports. Role-change board (§5.3). Line moves. |
| **Fri PM** | First full run (§3–§9). |
| **Sat** | DK Network injury report (final statuses + IR lists). Ownership firms up. Second run. |
| **Sun 9:30** | Weather, final line moves, morning reports. Third run. |
| **Sun 11:30** | 1:00 inactives → swap → re-run with 1:00 players locked. |
| **Sun ~2:35/2:55** | Late inactives → late swap (§11). |
| **TNF/MNF** | Showdown (§10). Inactives ~90 min before kick. |

---

## 3. Data pipeline (what runs, in order)

### 3.1 Source map: who gives what
| Source | Access | What it reliably gives | Watch out for |
|---|---|---|---|
| **DKSalaries.csv** (user upload) | upload | Truth for salary, position, team, game | Not available unless uploaded |
| **ESPN "DraftKings DFS values"** (weekly article, `espn.com/fantasy/football/story/...draftkings-nfl-dfs-values-week-N`) | ✅ curl | **Full slate table, ~170 players: name, team, opponent, position, projection, DK salary, value rating.** The backbone of the pool. | Projections can lag injury news (Week 9: listed Treylon Burks, who was OUT). Team assignments are correct for 2026, so trust them over memory. |
| **DK Network injury report** (`dknetwork.draftkings.com/YYYY/MM/DD/nfl-injury-report-week-N/`) | ✅ curl | Per-team Out/Doubtful/Questionable with beat-writer notes, plus **"On IR/Reserve" lists**. Parsed automatically. | Grep by full name; surnames collide (Luke vs Christian McCaffrey). |
| **DK Network DvP** (`nfl-defense-vs-position-week-N-draftkings-dfs`) | ✅ curl | Yards and targets allowed per position with salary context → DvP multipliers. | Article covers selected players only. |
| **DK Network value / tournament / Millionaire / best plays** | ✅ curl | Season stats, snap shares, stack ideas, contrarian angles → role overrides and ownership hints. | Writers disagree. Use them for facts, not conclusions. |
| **Web search** (CBS/Fox/Covers/VegasInsider/SportsBettingDime) | search | Spreads, totals, **opening vs current lines**, sharp/public splits. | Snippets mix in older seasons. Confirm the year. |
| **NFL.com / Yahoo / CBS live trackers** | search | Sunday inactives, starting-QB news. | Verify within 72 hours. |

**Access notes:** `dknetwork.draftkings.com` and `www.espn.com` are allowed in the Default environment. Fetch them with `curl` (`engine/fetch.py get`), because the `WebFetch` tool still can't reach them. To add more sites (rotowire, fantasylabs, footballguys, nfl.com, 4for4), ask Claude to add the host to the environment.

### 3.2 Commands
```bash
pip install pulp==2.8.0 pandas numpy                     # pulp v4 breaks cat=
DL=<scratch>/dl; W=dfs/2026-wkNN; mkdir -p $DL $W
python3 -I dfs/engine/fetch.py get "<ESPN DK values URL>"      $DL/espn.html
python3 -I dfs/engine/fetch.py get "<DK Network injury URL>"   $DL/inj.html
python3 -I dfs/engine/fetch.py espn     $DL/espn.html $W/espn_pool.csv      # salaries+proj+teams
python3 -I dfs/engine/fetch.py injuries $DL/inj.html  $W/injuries.csv       # Out/Doubtful/Q/IR
python3 -I dfs/engine/fetch.py text     $DL/<article>.html $DL/<article>.txt # read DK picks/DvP
# write $W/lines.csv and $W/overrides.csv (formats below), then:
cd dfs/engine && python3 run_week.py ../2026-wkNN --target 240 --cands 500 --qbs "Hunch QB1,Hunch QB2"
```
- Downloads stay in a separate data directory, and anything that parses them runs with `python3 -I`.
- `run_week.py` = pipeline → sim portfolio → angle table → validator → `lineups_run.csv` + `report.txt` in the week folder.

### 3.3 The two hand-made files
**`lines.csv`** (one row per team): `Team,Opponent,Spread,Total,OpenTotal,Kick,PROE`
- `Spread` is negative for the favorite. Implied total = Total/2 − Spread/2.
- `OpenTotal` drives the Vegas money signal.
- `Kick` = 1:00 / 4:05 / 4:25.

**`overrides.csv`**: `Name,Base,Mult,Own,Status,Tag,Note`
- `Base` = role-change projection (replaces ESPN's).
- `Mult` = DvP/trench/red-zone multiplier (§4.2).
- `Own` = projected ownership %.
- `Status` = OUT etc. when news beats the injury report.
- `Tag` ∈ {`rushQB`, `alphaWR`, `leadRB`, `exclude`}.
- `Note` = the reason (always fill it in, since it's our audit trail).

### 3.4 Verification rules (non-negotiable)
1. **Salary:** CSV, or ESPN plus one other source. Conflicts → CSV wins, otherwise flag and use the higher salary.
2. **Team:** from the salary table, never from memory (Week 9: Walker is a **Chief**, not a Seahawk).
3. **Starting QB for all teams:** news less than 72 hours old (Week 9: Joe Milton III was named the PHI starter over McKee, and J.J. McCarthy starts for NYG because Dart is on IR).
4. **Status:** DK Network injury report > ESPN projection. If a player is OUT anywhere credible, exclude him.
5. **Names:** normalize spellings across sources before joining ("DeMario"/"Demario", Jr./II, curly apostrophes). The pipeline does this for injuries; check overrides by hand.
6. **Unknown salary → exclude the player.** Never guess.

---

## 4. Projection model

### 4.1 Base
- `Base` = ESPN projection (already includes Vegas). A role-change override replaces it.
- If blending a second source, take the median and drop outliers more than 25% off.
- ⚠️ Apply `× implied/22` **only** to a season average, never to a published projection (no double-counting Vegas).
- DST base = average × (22 / opponent implied total), used only when no projection exists.

### 4.2 Multipliers (`pipeline.py` applies the automatic ones; the rest go in `overrides.Mult`)
The combined multiplier is capped at 0.80–1.25× Base.

| Factor | Rule | Auto? |
|---|---|---|
| Favorite's lead RB | ×1.06 (spread ≤ −7) · ×1.03 (≤ −3.5) | ✅ (lead RB = top-projected RB per team, or `leadRB` tag) |
| Underdog lead RB | ×0.92 (spread ≥ +7) | ✅ |
| Trailing WR/TE | ×0.94 (spread ≥ +7) | ✅ |
| Big-favorite WRs | ×0.96 (spread ≤ −9: TDs spread out, starters sit late) | ✅ |
| PROE | ≥ +3: WR/TE ×1.03 · ≤ −4.5: WR/TE ×0.97, RB ×1.02 | ✅ if `PROE` filled |
| **Vegas money signal** | Total up ≥3 from open: offense ×1.03 · down ≥3: ×0.98 | ✅ |
| Red zone | Heavy inside-10/inside-5 usage ×1.03–1.08 ("due" players at the top) | `Mult` |
| DvP | (points allowed to position / league avg)^0.35, capped 0.85–1.15. DK Network DvP gives the yards/targets. | `Mult` |
| Trenches | Bad pass-pro vs strong rush: QB/WR/TE ×0.90–0.95 · run-block edge: RB ×1.05–1.10 · DST vs a broken offense ×1.15 | `Mult` |
| Weather | Wind ≥15 mph: QB/WR/TE ×0.92 · heavy rain: pass ×0.95, RB ×1.02 | `Mult` |
| Pace | Both teams top-8 pace ×1.03 · both bottom-8 ×0.97 | `Mult` |
| First game back from soft-tissue injury | ×0.80–0.90 (Week 9: Breece Hall) | `Mult` |
| Backup QB on team | Own pass catchers ×0.90 · opposing DST only ×1.05 (Lesson 4) | `Mult` |

### 4.3 Ceiling (deterministic model A)
Proj × position volatility: **QB 1.45, RB 1.5, WR 1.65, TE 1.6, DST 2.0**, plus +0.05 for `rushQB` and alpha WRs (projected ≥18, or tagged).

### 4.4 Distribution (sim model B)
Lognormal with **mean = Proj** and coefficient of variation (sd/mean) **QB 0.40 · RB 0.55 · WR 0.65 · TE 0.70 · DST 0.85**.
- **Calibration check:** a good lineup should show median ~135–145, p90 ~190 and p99 ~235–250, which matches real Milly winners. If p99 runs past ~270, the CVs are too high.
- Re-fit the CVs from `results.csv` every 4 weeks.

---

## 5. Roles, ownership & leverage

### 5.1 Ownership (fill `overrides.Own` for the 25–40 most relevant players)
- Sources: Fantasy Footballers GPP article, FantasyLabs, Fantasy Team Advice, DK Network chalk notes.
- **The default heuristic in `pipeline.py` is weak for studs** (it gave Lamb and St. Brown ~6%). Always override the top-salary players at each position.
- Typical chalk:
  - a cheap RB inheriting a role → 20–35%
  - the top RB in the best spot → 20–30%
  - a min-priced starting QB → 8–15%
  - the most-written-about WR → 25–30%
  - a TE with vacated targets → "very chalky"
  - anyone featured in 4+ outlets → +5–10%

### 5.2 Leverage
`Leverage = P(player reaches his ceiling, from the sim) − Own%`.
- Fade fragile chalk in at least one lineup.
- Keep robust chalk and get unique elsewhere.
- **Total lineup ownership targets** (sum of 9 players):

| Contest | Target total | Requirement |
|---|---|---|
| Milly | 90–140% | ≥2 players under 5% owned |
| Mid-size GPP | 110–160% | |
| Showdown | Captain ownership is the main lever (§10) | |

- In big fields, leaving **$200–$1,000** unused cuts duplicate lineups when it costs under ~1.5 ceiling points.

### 5.3 Role-change engine
When a starter is OUT, reallocate his targets, carries and red-zone looks:
- 50–60% to the direct replacement, 20–30% to the next man, the rest spread out.
- Rebuild the projection: targets × catch rate × yards per target + TD share × team implied TDs.
- Apply a ×0.90 rookie discount unless snaps confirm the role.
- Put it in `overrides.Base` with a `Note`.

Week 9 board, for reference:

| Out | Who gains |
|---|---|
| NE A.J. Brown | Douglas, Chism, Hollins, Raridon |
| NE Henderson | Stevenson |
| SF Evans & Deebo (plus Pearsall, out for the season) | Kittle, McCaffrey, Watkins, Robinson |
| PHI Smith & Wicks, with Milton at QB | Makai Lemon |
| NYJ G. Wilson | Adonai Mitchell, Mason Taylor |
| NYG Skattebo (Tracy on IR, Harris released) | Singletary |
| MIA Achane (out for the season) | Ollie Gordon II |
| WAS McLaurin and Burks | Antonio Williams, Diggs, Okonkwo |
| SEA Darnold and Shaheed | Lock, Smith-Njigba |

---

## 6. Correlation & game stories

### 6.1 Approximate DK correlations (industry-typical; refine from our logs)
| Pair | r |
|---|---|
| QB – own WR1 | **+0.45** |
| QB – own TE1 | +0.35 |
| QB – own WR2 | +0.30 |
| QB – opposing WR1 | +0.20 |
| QB – own RB1 | +0.10 (pass-catching RB +0.20) |
| RB1 – own DST | +0.15 to 0.20 |
| WR1 – WR2 (same team) | ~0 to +0.10 |
| RB1 – same-team RB2 | **−0.20** |
| DST – opposing offense | **−0.30 to −0.40** (hard rule: never) |

The sim produces these through shared game, team-pass and team-rush factors. DSTs are negatively tied to the opposing offense.

### 6.2 Build each lineup around a story
| Story | Recipe | Week 9 example |
|---|---|---|
| **Shootout** | QB + 2 pass catchers + 1–2 bring-backs; high total, close spread | Lions–Dolphins 50.5 (sharp money on the over): Willis + Bell + Dulcich vs Gibbs + St. Brown + LaPorta |
| **Blowout** | Favorite's QB + RB + 1–2 pass catchers (+ DST); no bring-back | 49ers −9.5: Purdy + Kittle (+ McCaffrey) |
| **Role-change smash** | Promoted player + his QB | Maye + Douglas/Chism |
| **Contrarian QB** | Low-owned QB + top 2 targets + bring-back | Shedeur + Boston + Fannin + Kendre Miller |
| **Slog fade** | Skip the game; use its DST and/or workhorse RB | Giants–Eagles 38.5 |

Each of your 1–3 lineups tells a **different story**.

---

## 7. Construction rules (Classic)

### 7.1 Hard rules (enforced in code by `engine/validate.py`)
- $50,000 cap. Positions: QB, 2 RB, 3 WR, TE, FLEX (RB/WR/TE), DST.
- **≤3 players per team** (Lesson 3).
- **No offensive player against your own DST.**
- **QB + ≥1 own pass catcher**, and ≥2 when the team has two viable ones.
- **Bring-back required** unless the QB's team is favored by 9 or more.
- Nobody OUT, IR or Doubtful. Omar Cooper Jr. never.
- Across lineups: **a different QB in each lineup**, at most 3–4 shared players per pair, and nobody in every lineup (3+ lineups).

### 7.2 Strong defaults (break only with a stated reason)
- Lead RB on a −7 or bigger favorite is a core play.
- DSTs vs backup/rookie QBs get only a modest boost.
- At most 2 near-punts (projected under ~6 with no new role).
- Questionable players only with a late-game pivot or "expected to play" news.
- Late-window players in FLEX.
- No same-team RB+RB.
- A second TE only with a target/red-zone path.

---

## 8. Simulation engine & angle matrix

**`engine/sim.py`:**
1. 20,000 correlated slate simulations.
2. ~250–500 **sim-optimal candidates**: the optimizer solved against a blend of one simulated world and the median projections, with all hard rules, bring-backs and forced players.
3. **Greedy portfolio pick** maximizing P(at least one lineup ≥ target), with overlap and exposure caps and a distinct QB per lineup.

**Angle matrix (every week, and always for Kendall's hunches):**
- Every relevant QB × a set of star requirements, for example: Gibbs + (Smith-Njigba or Nacua), Gibbs only, (Smith-Njigba or Nacua), Open.
- Print P(≥240) for each cell. That turns "what about Shedeur / Milton / Lock / McCarthy?" into a number.
- Week 9 full matrix (ESPN pool), chance of 240+:

| QB | Chance |
|---|---|
| Malik Willis | 1.39% |
| Shedeur Sanders | 1.12% |
| Brock Purdy | 1.07% |
| Patrick Mahomes | 0.94% |
| J.J. McCarthy | 0.86% |
| Drew Lock | 0.85% |
| Joe Milton III | 0.71% |

- `run_week.py --qbs "..."` does a quick version.

**Search breadth matters.** Week 9: 310 candidates found a best of 1.04% where 512 candidates (with forced-star configs) found 1.39%. Use **≥500 candidates** for the final portfolio, and treat gaps under ~0.3 points as ties.

**Targets:**
- Milly first-place range ≈ 230–260, so use `--target 240`.
- For a top-1% balance use 215. Mid-size GPPs: ~200.
- **P(≥240) is not P(win).** You also have to outscore everyone else who hits that week.

**Two-model rule:** show both the deterministic ceiling optimizer (model A, `2026-wk09/model.py` style) and the sim portfolio (model B). Where they agree = core. Where they disagree = decide with football reasoning plus Kendall's read.

---

## 9. Portfolio for 1–3 lineups

- **1 lineup:** the highest P(≥target) lineup that passes the story test. Robust chalk plus 1–2 leverage spots.
- **2 lineups:** two stories, different QBs, ≤3 shared players. One chalk-robust, one contrarian.
- **3 lineups:** three stories (for example blowout / shootout / contrarian QB), ≤3–4 shared players per pair, nobody in all 3.
- Each lineup should differ at QB, the main stack, the DST, and at least 2 RB/WR spots.

---

## 10. Showdown (TNF/MNF)

- **Format:** CPT (1.5× points and salary) + 5 FLEX, $50,000, both teams represented. **Never** a DST with the opposing QB or opposing pass catchers at CPT.
- **Captain choice:** P(top scorer in the game) × (1 − CPT ownership). The field over-captains the QB and WR1. Pivot captains: the favorite's workhorse RB, a WR2 with a role change, a red-zone TE.
- **Team splits by story:**
  - Favorite dominates → 5-1 or 4-2 (CPT the favorite's RB or WR1).
  - Shootout → 3-3 or 4-2 with both QBs.
  - Slog → DST + K in FLEX, CPT a RB.
- **Kickers:** fine as FLEX in low totals. Rarely CPT.
- **Backup-QB games:** the opposing DST is strong, and the backup's WR1 still gets catch-up targets.
- **Salary:** leaving $1,000–$2,500 unused is a legitimate way to avoid duplicates.
- **Multiple lineups:** a different CPT in each, ≤4 shared FLEX.

---

## 11. Sunday protocol & late swap

1. **11:30:** 1:00 inactives. Re-fetch the injury report → swap → re-run with 1:00 players locked.
2. Keep 4:05/4:25 players in FLEX and the late RB/WR slots.
3. **~3:30:**
   - A lineup that needs a ceiling → pivot its late slots to higher-variance, lower-owned players.
   - A lineup that's already strong → stay robust.
4. **~2:35/2:55:** late inactives → swap.
5. After **every** swap, re-run `validate.py` (DST conflict, stack, team caps).

---

## 12. Self-evaluation protocol (before EVERY handoff, and shown in the answer)

1. **Validator** on the final lineups and every alternate → PASS or the exact failures.
2. **Data-freshness audit:**
   - starting QBs verified less than 72 hours ago
   - injury report re-fetched today
   - single-source salaries listed
   - lines compared open → now
3. **Player-status sweep:** grep the DK injury report for **every rostered player's full name**, and report any Q/D/OUT with a quote.
4. **Soft-rule deviations** (§7.2), each with its reason.
5. **Adversarial pass:** how does each lineup lose? Name the most fragile piece and any cheap hedge.
6. **Requested angles:** every player/QB Kendall named has a number in the angle table, and is either in the portfolio or listed as an alternate with a reason.
7. **Blind spots, stated plainly:** heuristic ownership, CVs/correlations not yet calibrated, TD scoring lumpier than the lognormal shows, no field simulation, how much results depend on search breadth.
8. **What changed because of this review.** If nothing changed, say why.

---

## 13. Post-mortem & calibration

`dfs/results.csv`: `Week,Name,Pos,Salary,Base,Proj,Own_proj,Own_actual,Actual,Rostered,Note`. Log the rostered players plus the top 30 projected.
1. Misses of more than 50%: role, script, injury, or TD variance? Is it repeatable or noise?
2. Multipliers that consistently push the wrong way → adjust by up to ±0.02 every 4 weeks.
3. Sim p99 vs actual winning scores → re-fit the CVs.
4. Where was ownership wrong (ours vs the field's)?
5. Kendall hunch log, hit or miss. The hit rate is data.
6. Add a lesson in §14 **only if it changes a rule.**

---

## 14. Lessons (each one is a rule)

| # | Week | What happened | Rule |
|---|---|---|---|
| 1 | 5 | Faded Gibbs on a big favorite → 32.7 | Lead RBs on big favorites = core |
| 2 | 6 | Bernard 25.7 on a 5.5 average | Current role > season average |
| 3 | 6 | Four Rams in a busted game | ≤3 per team |
| 4 | 6 | Panthers DST vs a backup QB scored 4 | Modest DST boost vs backups |
| 5 | — | Kendall's instincts hit (Bernard, Chase/Ravens, Walker) | Test hunches in the model |
| 6 | 9 | No CSV → ~15 relevant players unpriceable | Upload the CSV, or parse ESPN's full table. Never guess salaries |
| 7 | 9 | Projections already include Vegas | `implied/22` only on season averages |
| 8 | 9 | Same players in all 3 lineups by eye | Exposure and distinct-QB rules enforced in code |
| 9 | 9 | Stale QB (McKee vs Milton); Walker's team from memory (SEA vs KC); McCarthy's NYG start missed | Teams from the salary table; QBs from news less than 72 hours old |
| 10 | 9 | ESPN projected Burks, who was OUT | The injury report overrides projections |
| 11 | 9 | Search breadth changed the best angle 1.04% → 1.39% | ≥500 candidates; gaps under 0.3 points are ties |
| 12 | 9 | **Results:** _fill in after games_ | |

---

## 15. Kendall's profile & output format

- **Goal:** win large-field GPPs with 1–3 lineups. Wants every angle: film-style reasoning, coaching tendencies, trenches, Vegas (including money movement), DK Network, stats.
- **Likes:** workhorse RBs (Gibbs, Walker, McCaffrey), contrarian QBs (Shedeur, Milton, Lock, McCarthy), sleepers with history (Jeudy–Shedeur). **Always excludes Omar Cooper Jr.**
- **Output order:**
  1. Self-evaluation (§12)
  2. **Best overall lineup**
  3. The portfolio table (salary, chance of 240+, ownership, kickoff)
  4. Alternates for requested angles
  5. Before-lock checklist
  6. Sources
- **When reviewing Kendall's lineups:** positives before negatives.
- **Season rule:** 2026–27 only. The uploaded CSV beats articles.

---

## 16. Final checklist

- [ ] 9 players · ≤ $50,000 · valid positions · ≤3 per team · no DST conflict · QB stack · bring-back or a blowout reason → `validate.py` PASS
- [ ] Every rostered player grepped in today's injury report · nobody OUT/IR/D · Questionables have a pivot
- [ ] Salaries confirmed (CSV, or ESPN plus one) · teams from the salary table · starting QBs less than 72 hours old · no 2025 data
- [ ] Lines open → now recorded · Vegas signal applied · weather checked
- [ ] Angle table shown with Kendall's hunches · ≥500 candidates for the final portfolio
- [ ] Different stories and QBs across lineups · overlap ≤3–4 · nobody in all 3
- [ ] Total ownership in the contest range · ≥1 leverage spot per lineup
- [ ] Kickoff times listed · late players in FLEX
- [ ] Omar Cooper Jr. excluded

---

## 17. Engine reference

| File | Purpose |
|---|---|
| `engine/fetch.py` | `get` (curl through proxy) · `espn` (table → pool CSV) · `injuries` (DK report → statuses + IR) · `text` (article → text) |
| `engine/pipeline.py` | pool + injuries + lines + overrides → `pool_v3.csv` (status filter, multipliers, caps, implied totals, ownership) |
| `engine/sim.py` | correlated simulation · `solve()` (rules, bring-backs, `require_any`, `qbs`, `lock`/`exclude`, overlap) · `candidates()` · `pick()` |
| `engine/validate.py` | hard-rule checker (§7.1) |
| `engine/run_week.py` | one command: pipeline → sim → angles → validator → `lineups_run.csv` + `report.txt` |
| `2026-wk09/` | worked example: `lines.csv`, `overrides.csv`, `espn_pool.csv`, `injuries.csv`, `scenarios.py` (full angle matrix), `rebuild_espn.py`, outputs |

**Roadmap:**
- [ ] Better default ownership (salary rank × game total × projection value) to replace the weak heuristic.
- [ ] Field simulation (5k field lineups from ownership) → the real target score and a duplicate penalty.
- [ ] Showdown mode in `sim.py`.
- [ ] Auto-fetch lines.
- [ ] Parse the DK Network DvP article into `Mult` suggestions.
- [ ] CV/correlation calibration from `results.csv`.

---

## 18. Responsible play
DFS GPPs are long shots even with optimal lineups. Week 9's best 3-lineup portfolio had about a 3% chance that *any* lineup reaches the first-place score range, and winning outright is far rarer. Set a fixed weekly budget you're comfortable losing, don't chase losses, and treat a big week as variance, not proof.
