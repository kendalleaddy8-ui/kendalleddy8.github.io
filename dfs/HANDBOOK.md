# NFL DFS GPP Handbook v2 — Kendall × Claude
**DraftKings Classic & Showdown · 2026–27 season · large-field GPPs (Millionaire Maker, $20 TNF/MNF showdowns) · 1–3 lineups**

> Paste this whole file into a new chat with Claude at the start of each slate, along with the kickoff prompt in §0.
> Engine code lives in the repo `kendalleaddy8-ui/kendalleddy8.github.io` under `dfs/` (`engine/sim.py`, weekly folders `dfs/2026-wkNN/`).
> Version history: v1 = original playbook (Weeks 5–8). v2 = Week 9: simulation engine, ownership/leverage, data protocol, calibration loop. **v2.1 = Week 9 self-review: angle matrix, Vegas money signal, rules validator, self-evaluation protocol (§15A), starting-QB verification.**

---

## 0. How to start each week (paste this with the handbook)

```
Week __ · Slate: [Main Classic / TNF Showdown / MNF Showdown / other] · Contest: [Milly Maker / $20 SD / other], field size ____
Lineups: __ · Attached: DKSalaries.csv [yes/no] · Time now: ____ ET
My hunches this week: ____
Players I'm excluding: Omar Cooper Jr., ____
Last week's results (paste scores/finishes if you have them): ____
Run the handbook: data → projections → ownership → sim → portfolio → self-check. Show the best overall lineup first.
```

**Always upload `DKSalaries.csv`** (DK lobby → contest → Export to CSV). It takes 10 seconds and is the single biggest quality lever. In Week 9 there was no CSV. Salaries had to be pieced together from about 25 articles, so roughly 15 relevant players (Jeudy, Barkley, Achane, Waddle, Sutton, Pearsall, the Saints QB…) couldn't be priced, and the optimizer couldn't consider them.

---

## 1. The edge philosophy (why GPPs are different)

1. **GPP payouts are top-heavy.** First place in the Milly is worth more than everything from 2nd to 100th combined. So we maximize **P(lineup finishes ~top 0.1%)**, not expected points. A 150-median lineup with a fat right tail beats a 155-median lineup that can't reach 240.
2. **Three levers, in order:** **Ceiling** (players who can score 2–3× their median) × **Correlation** (players whose ceilings happen *together*) × **Uniqueness** (when we hit, we don't split first place with 40 duplicates).
3. **Role changes are our biggest repeatable edge** (Lesson 2: Bernard). DK prices lag news by 2–5 days. Injury news after Wednesday's pricing usually creates mispriced players.
4. **Being right about the field matters as much as being right about football.** If a 30%-owned player busts, 30% of the field busts with him. If he booms, we only keep pace. Leverage is fading chalk that is *fragile* and playing low-owned players with *real paths* to a ceiling.
5. **Test Kendall's hunches in the model, don't dismiss them** (Lesson 5). Week 9: the unconstrained sim independently chose Walker + McCaffrey (workhorse RBs) and a contrarian Shedeur stack, both Kendall instincts.

---

## 2. Weekly operating timeline (ET)

| When | Task |
|---|---|
| **Mon night / Tue** | Post-mortem last week (§12): log projection vs actual, finish, ownership. Update the lessons log. |
| **Tue–Wed** | DK salaries post. First look: mispricings, role changes already known, game totals. Note early-week lines. |
| **Wed–Fri** | Practice reports (DNP/LP/FP). Build the **role-change board** (who inherits volume). Track line moves (sharp money moves totals by 1+ pt). |
| **Fri afternoon** | Final injury reports (Out/Doubtful/Questionable). First full model + sim run. |
| **Sat** | Saturday updates/elevations. Ownership projections firm up. Second sim run. |
| **Sun 9:30 AM** | Weather (wind ≥15 mph, heavy rain), line moves, morning reports (Schefter/Rapoport/Pelissero-level news). |
| **Sun 11:30 AM** | **1:00 inactives.** Re-run. Lock 1:00 decisions. |
| **Sun ~2:35/2:55 PM** | **4:05/4:25 inactives.** Late swap (§11). |
| **TNF/MNF** | Showdown (§10). Inactives ~90 min before kick. |

---

## 3. Data acquisition protocol

### 3.1 Inputs (priority order) and the source for each
1. **Salaries:** `DKSalaries.csv` (truth). Fallbacks: ESPN "DraftKings DFS values" tables, FTN, The Huddle "Fantasy Domination", Footballguys "Cracking DK", FantasyLabs, DK Network. **Rule: a salary needs 2 sources, or 1 source plus a user screenshot, before a player is "confirmed". Single-source salaries are flagged `?`.**
2. **Starting QB for every team (verify from news within the last 72 hours, not depth charts or season pages).** Week 9 miss: I listed Tanner McKee for PHI, but Joe Milton III was named the starter on 11/4. Search `"<team> starting quarterback week N <year>"` for every team with any QB uncertainty.
3. **Vegas:** spread and total for every game. **Implied team total = total/2 − spread/2** (favorite has the negative spread). Example: SF −9.5, 52 → SF 30.75 / LV 21.25. Use the *latest* line. Sources: CBS, Fox, Covers, VegasInsider, RotoWire.
4. **Injuries/inactives:** NFL.com injuries-to-monitor and official reports, Yahoo injury tracker, CBS live inactives, RotoWire, Sharp Football (all 32 teams).
5. **Role changes:** snap %, route %, target share, carries inside the 10 (§4.3).
6. **DvP:** DK Network DvP article, Pro Football Network.
7. **Trenches:** 4for4 OL/DL matchups (pressure rate, adjusted line yards, blown-block rate).
8. **Tendencies:** PROE (muffed.ai), pace (seconds/play), red-zone usage (Fantasy Footballers Red Zone report).
9. **Ownership:** Fantasy Footballers GPP article, FantasyLabs, Fantasy Team Advice. Use a range, not a point estimate.
10. **Weather:**
11. **Line movement (open → now) and betting splits:** SportsBettingDime "biggest odds movement", VegasInsider, TheOddsBreakers sharp money, Yahoo betting buzz. Record open and current spread/total for every game. game-day forecast for outdoor stadiums.

### 3.2 The player-pool CSV schema (one row per player)
```
Name,Pos,Team,Opponent,Salary,Base,Proj,Own,Kick,Status,Conf,Note
```
- `Base` = raw source projection (median DK points). `Proj` = after the multipliers in §4. `Own` = projected ownership %.
- `Kick` = 1:00 / 4:05 / 4:25 / SNF. `Status` = OK/Q/D/OUT. `Conf` = H/M/L (data confidence: salary verified, role clear).
- Save each week's pool, model and lineups to `dfs/2026-wkNN/` so we can calibrate later.

### 3.3 Session/network notes (Claude-side)
- If Claude's cloud session can't open DK Network/ESPN pages directly (Week 9: dknetwork.draftkings.com was blocked), allow these domains in the environment's network settings: `dknetwork.draftkings.com, www.espn.com, www.rotowire.com, www.fantasylabs.com, www.footballguys.com, ftnfantasy.com, www.nfl.com, www.covers.com, www.4for4.com`. Search-result snippets work as a fallback, but they are lossy.
- If a needed number truly can't be found, **exclude the player rather than guess a salary.** Say so in the output.

---

## 4. Projection model v2

### 4.1 Base projection
- **Preferred:** a blend of 2–3 published projections (ESPN, FTN, Footballguys, FantasyLabs consensus). Weight the median, and drop an outlier if it's >25% off the others.
- **No published projection:** season DK avg × (team implied total / 22).
- ⚠️ **Don't double-count Vegas.** Published projections already include the implied total. Only apply the `× implied/22` step to a season average, never to a source projection.
- **DST:** base × (22 / opponent implied total).

### 4.2 Multipliers (applied to Base → Proj). Cap the combined stack at 0.80–1.25.
| Factor | Rule |
|---|---|
| **Game script: favorite lead RB** | ×1.06 if spread ≤ −7 · ×1.03 if ≤ −3.5 |
| **Game script: underdog RB** | ×0.92 if spread ≥ +7 |
| **Trailing pass catchers** | WR/TE ×0.94 if spread ≥ +7 (projected garbage time is already priced in) |
| **Big-favorite WRs** | ×0.95–0.96 if spread ≤ −9 (TDs spread out, starters sit late) |
| **Pass tendency** | PROE ≥ +3: WR/TE ×1.03 · PROE ≤ −4.5: WR/TE ×0.97, RB ×1.02 |
| **Red zone** | Heavy inside-10/inside-5 usage ×1.03–1.08, most for players "due" (lots of goal-line work, few TDs) |
| **DvP** | (pts allowed to position / league avg)^0.35, capped 0.85–1.15 |
| **Trenches** | QB/pass catchers ×0.90–0.95 behind a bad pass-pro OL vs a strong rush · RB ×1.05–1.10 with a clear run-blocking edge · DST ×1.15 vs a bad OL/offense |
| **Weather** | Wind ≥15 mph: QB/WR/TE ×0.92, K ×0.85 · heavy rain: pass ×0.95, RB ×1.02 |
| **Pace** | Both teams top-8 pace: all offense ×1.03 · both bottom-8: ×0.97 |
| **Injury-limited return** | First game back from soft-tissue injury: ×0.80–0.90 (Week 9: Breece Hall) |
| **Vegas money signal** | Total up ≥3 pts from open, or sharp % on the over: that game's offenses ×1.02–1.03 · total down ≥3: ×0.98 · sharp money on a favorite (spread grows ≥1 with money% > tickets%): favorite's lead RB +0.02. Week 9: DET–MIA 47.5→50.5 with sharp over and DET −6.5→−7 (Gibbs) · NYJ–KC 41.5→47.5 · DEN–CAR 41→44.5 · LAR–WAS 51.5→47.5 · NYG–PHI 44.5→38.5 (Milton named starter) |
| **QB downgrade on team** | Backup QB: own pass catchers ×0.90, opposing DST only ×1.05 (Lesson 4) |

### 4.3 Role-change engine (highest-leverage step)
When a starter is OUT, reallocate his **targets, carries and red-zone looks** explicitly. Don't just bump a backup.
1. Take the missing player's per-game targets/carries/RZ looks.
2. Distribute by depth chart and route share: roughly 50–60% to the direct replacement, 20–30% to the next man, 10–20% spread out (plus some to the TE/RB on passing downs).
3. Rebuild the projection: targets × team catch rate × yards per target + TD share × team implied TDs.
4. Apply a rookie/unknown discount of 0.90 unless snap data already confirms the role.
5. Flag every role-change player `Conf=M` and list it in the output so Kendall can apply judgment.
- Week 9 examples: NE A.J. Brown OUT → Douglas/Chism · SF Evans & Deebo OUT → Kittle/McCaffrey target concentration · PHI DeVonta Smith & Wicks OUT → Makai Lemon · NYJ G. Wilson OUT → Adonai Mitchell · NYG Skattebo doubtful → Singletary · NE Henderson OUT → Stevenson.

### 4.4 Distribution parameters (for the sim)
Coefficient of variation (sd/mean) by position: **QB 0.40 · RB 0.55 · WR 0.65 · TE 0.70 · DST 0.85**. Then:
- Rushing QBs: CV −0.03 (higher floor), but keep a ceiling boost via the projection.
- Boom/bust deep threats and TD-dependent TEs: CV +0.10.
- Workhorse RBs (≥70% snaps, goal-line role): CV −0.05.
- **Calibrate these from our logged results every 4 weeks (§12).**

---

## 5. Ownership & leverage

### 5.1 Ownership sources and heuristics
Use published projections when available. Without them, the field's chalk is predictable:
- **Cheap RB who inherits a starter's role** (Week 9: Jonah Coleman $5,300) → 20–35%.
- **Top RB in the best spot** (Gibbs $10,000, DET 28.75 implied) → 20–30%.
- **Min-priced starting QB** (Lock / Shedeur $4,000) → 8–15%.
- **Top WR in the highest-total game, or the most-written-about value** (Nacua ~29%).
- **TE with a vacated-target story** (Kittle with Evans/Deebo out) → "very chalky".
- Articles that appear in 4+ outlets (DK Network, FantasyLabs, Footballguys, FTN) → add 5–10%.

### 5.2 Leverage score
`Leverage = P(player hits ceiling, from sim) − Own%`. Positive = under-owned relative to his boom rate.
- Prefer +leverage players at the same salary tier.
- **Fragile chalk** (big ownership with a narrow path: a backup RB in a timeshare, a WR needing a long TD) → fade in at least one lineup.
- **Robust chalk** (a workhorse RB on a big favorite) → play it. Lesson 1: Gibbs 32.7 when faded. Don't fade good chalk just to be different. Get different elsewhere.

### 5.3 Lineup-level ownership targets (sum of 9 players' Own%)
| Contest | Target total ownership | Notes |
|---|---|---|
| Milly Maker (~1M+ entries) | **90–140%** | Need ≥2 players under 5%. At least one "game story" the field is light on. |
| Mid-field GPP (10k–100k) | 110–160% | One contrarian angle is enough. |
| $20 showdown (large) | CPT ownership is the key lever (§10) | |
- **Duplication control:** leaving **$200–$1,000 unused** in big fields reduces dupes (most of the field uses $49,800–$50,000). Use it when the cost to ceiling is under ~1.5 points.

---

## 6. Correlation & game theory

### 6.1 Approximate DK correlations (industry-typical; refine with our logs)
| Pair | r |
|---|---|
| QB – own WR1 | **+0.45** |
| QB – own TE1 | +0.35 |
| QB – own WR2 | +0.30 |
| QB – opposing WR1 (bring-back) | +0.20 |
| QB – own RB1 | +0.10 (pass-catching RB +0.20) |
| RB1 – own DST | +0.15 to +0.20 (winning script) |
| Own WR1 – WR2 | ~0 to +0.10 |
| RB1 – same-team RB2 | **−0.20** (avoid unless a blowout/backfield split narrative) |
| DST – opposing offense | **−0.30 to −0.40** (hard rule: never) |
| QB – own DST | ~0 |
The sim (`engine/sim.py`) builds these through shared **game**, **team-pass** and **team-rush** factors, plus DSTs negatively tied to the opposing offense.

### 6.2 Build around a game story, not a list of good plays
Pick the story first, then fill it in:
- **Shootout:** QB + 2 pass catchers + 1–2 bring-backs (high total, close spread; Week 9: DAL–IND 51.5, DET–MIA 50.5).
- **Blowout:** QB + RB + 1–2 pass catchers from the favorite + that team's DST. No bring-back needed (Week 9: SF −9.5 with Purdy/McCaffrey/Kittle).
- **Defensive slog:** fade the game entirely. Use that DST plus a workhorse RB.
- **Role-change smash:** the newly promoted player plus his QB (Week 9: Maye + Douglas + Chism).
- **Contrarian QB:** a low-owned QB in a good matchup with his top 2 targets (Week 9: Shedeur + Fannin + Concepcion vs NO).
- Each of your 1–3 lineups should tell a **different story**.

---

## 7. Construction rules (Classic)

### 7.1 Hard rules (never break)
- $50,000 cap; QB, 2 RB, 3 WR, TE, FLEX (RB/WR/TE), DST.
- **Max 3 players per team** (Lesson 3: four Rams sank Week 6).
- **No offensive player against your own DST** (Week 5 Shough + Vikings DST, Week 8 Dolphins DST).
- **QB + ≥1 own pass catcher**; ≥2 when the team has two viable ones.
- Nobody OUT/Doubtful. Questionables only with a 4:05/4:25 pivot available, or with confirmed "expected to play" news.
- **≤ 2 near-zero punts** (avg < ~5 with no new role). No 0.0-average backups unless a role change is confirmed.

### 7.2 Strong defaults (break only with a stated reason)
- Bring-back from the opponent preferred, unless the QB's team is favored by ≥9 (blowout story).
- Lead RB on a favorite of −7 or more = core (Lesson 1).
- DST vs a backup/rookie QB: modest boost only (Lesson 4: Panthers DST scored 4).
- Late-game players (4:05/4:25) in FLEX for late-swap flexibility.
- Avoid same-team RB + RB, and avoid a QB with his own RB as the only "stack".
- TE in FLEX only if the TE2 has a target/red-zone path (Week 9: Dulcich vs DET's 28.3 DK pts/g to TEs).

---

## 8. Simulation engine (how we pick lineups now)

**What it does** (`dfs/engine/sim.py`):
1. **Simulate** 20,000 slates. Each player = lognormal(mean = Proj, CV by position), correlated through game, team-pass and team-rush factors. DSTs are negatively tied to the opponent offense.
2. **Generate candidates:** solve the optimizer ~150 times against blended objectives (½ one simulated world + ½ median). Each candidate is optimal in some plausible world, and all hard rules are enforced.
3. **Pick the portfolio:** greedily choose lineups that maximize **P(at least one lineup ≥ target score)**. Shared players are limited (default ≤4) and nobody is in all 3 lineups.

**Run it:**
```bash
pip install pulp==2.8.0 pandas numpy        # pulp v4 breaks cat=
python3 dfs/engine/sim.py dfs/2026-wkNN/pool_adj.csv --n 3 --target 215 --sims 20000 --cands 150
```
**Targets (calibrate with our results):** Milly first-place range is roughly 230–260 DK pts, so use `--target 230–240` for a pure first-place chase and `215` to balance the top-1% finish rate. Mid-field GPPs: ~200.
**Week 9 calibration check:** good lineups showed median ~140–145, p90 ~190 and p99 ~240, consistent with real Milly winning scores. If p99 drifts above ~270, the CVs are too high.

**Two-model rule:** always show both
- **(A)** the deterministic "ceiling optimizer" (v1 multiplier method, `dfs/2026-wk09/model.py`), and
- **(B)** the sim portfolio.
Where they agree = core. Where they disagree = decide with football reasoning + Kendall's hunch. The sim doesn't enforce bring-backs yet, so check them by hand.

**Angle matrix (run every week, and always when Kendall names players/QBs):** `dfs/2026-wk09/scenarios.py` builds the best sims for every QB × a set of star requirements (e.g., Gibbs+JSN, Gibbs+Puka, Gibbs, JSN|Puka, Open) and prints P(≥240) for each cell. That turns "what about Shedeur / Milton / Lock?" into a number instead of an opinion. Week 9 result: the best cell was Willis + Gibbs + JSN at 1.46%; Lock, Shedeur and Milton came in at 0.88–1.02%, viable but not superior. The top ~10 QBs sat inside a ~0.6-point band, which is below our projection error, so football judgment and Kendall's read should decide within that band.

**Reading the numbers honestly:** P(≥240) means "scores in the Milly first-place range". It does **not** mean P(win). Winning also requires beating ~1M other lineups that hit on the same Sunday, so the true win probability is a small fraction of P(≥240).

**Engine roadmap (next upgrades):**
- [x] `Spread` column → bring-backs enforced in the sim (done Wk9 v2.1). Distinct QB per lineup enforced. Hard-rule validator `engine/validate.py`.
- [ ] Game-script multipliers applied inside the sim from `Spread` (currently done upstream in `model.py`).
- [ ] Ownership-aware objective: penalize lineups by expected duplicates (product of ownerships).
- [ ] Field simulation: build 5,000 "field" lineups from ownership to get the real target score per contest.
- [ ] Showdown mode (CPT slot, 1.5× multipliers).
- [ ] Calibrate CVs and correlations from our logged weekly results.

---

## 9. Portfolio strategy for 1–3 lineups

- **1 lineup:** the highest P(≥target) lineup that also passes the "story" test. Take some chalk where it's robust and get your leverage at one or two spots.
- **2 lineups:** two different game stories, no shared QB, ≤3 shared players. One leans chalk-robust, one leans contrarian.
- **3 lineups:** three stories (e.g., blowout favorite / shootout / contrarian QB), ≤3–4 shared players per pair, and no player in all 3 unless that's deliberate and stated (e.g., a workhorse RB at a price the field won't pay).
- **Exposure sanity:** each lineup should differ at QB, the main stack, the DST, and at least 2 of the RBs/WRs.

---

## 10. Showdown v2 (TNF/MNF, $20)

- **Format:** CPT (1.5× points and salary) + 5 FLEX, $50,000. Both teams must be represented.
- **Hard rule:** never pair a DST with the opposing QB (or with opposing pass catchers as CPT).
- **Captain selection:** rank by **P(top-scoring player in the game) × (1 − CPT ownership)**. The field over-captains the QB and alpha WR. Pivot CPTs: the workhorse RB on the favorite, the WR2 with a role change, the TE in a red-zone-heavy offense.
- **Composition by story:**
  - Favorite dominates → **5-1 or 4-2** favorite (CPT the RB or WR1 from the favorite).
  - Shootout → 3-3 or 4-2 with both QBs.
  - Defensive game → DST + K in FLEX, CPT a RB.
- **Kickers:** viable FLEX in low totals or when the favorite stalls in the red zone. Rarely CPT.
- **Backup-QB games:** the opposing DST is strong, and the backup's WR1 still gets catch-up targets.
- **Salary:** most of the field spends the full $50,000. Leaving $1,000–$2,500 is a legitimate dupe-avoider in showdown.
- **Multiple lineups:** a different CPT in each (QB in one, RB/WR in another), and ≤4 shared FLEX.

---

## 11. Sunday late-swap protocol

1. 11:30 AM: process the 1:00 inactives. Swap any inactive 1:00 player, then re-run the sim with the 1:00 players locked.
2. Keep **4:05/4:25 players in FLEX** (and in the latest RB/WR slots possible).
3. Around 3:30 PM, with the 1:00 games mostly done: check where each lineup stands.
   - If a lineup needs a ceiling outcome, pivot late slots to **higher-variance, lower-owned** players.
   - If it's already strong, keep the late slots chalky and robust.
4. ~2:35/2:55 PM: late inactives. Swap anyone ruled out.
5. Re-check the "no offense vs own DST" rule after every swap.

---

## 12. Post-mortem & calibration loop (do this every week)

Log one row per player we rostered **and** for the top 30 projected players:
```
Week,Name,Pos,Salary,Base,Proj,Ceiling,Own_proj,Own_actual,Actual,Rostered,Note
```
Then answer:
1. Which projections missed by more than 50%, and why: role, game script, injury, TD variance? Is the miss **repeatable** (model error) or **noise**?
2. Did any multiplier consistently push the wrong way? Every 4 weeks, adjust its size by up to ±0.02.
3. Did the sim's p99 match the actual winning scores? Adjust the CVs.
4. Ownership: what did the field get wrong (and right) that we can exploit next week?
5. Did Kendall's hunch hit? Log it. Hunch hit rate is data.
6. Write any new lesson into §13 **only if it changes a rule**.

---

## 13. Lessons log (rules learned from results)

1. **Wk5:** faded Gibbs on a big favorite → he scored 32.7. **Lead RBs on big favorites = core.**
2. **Wk6:** Germie Bernard scored 25.7 on a 5.5 average → **current role > season average.**
3. **Wk6:** four Rams in one lineup in a game that busted → **max 3 per team.**
4. **Wk6:** Panthers DST vs a backup QB scored 4 → **don't overrate DSTs vs backups.**
5. **Kendall's instincts hit** (Bernard, Chase/Ravens history, Walker) → **test his hunches in the model, don't dismiss them.**
6. **Wk9 (process):** no salary CSV meant ~15 relevant players couldn't be priced → **always upload the CSV; exclude players with unknown prices, never guess.**
7. **Wk9 (process):** published projections already include Vegas → **apply `implied/22` only to season averages** (no double-counting).
8. **Wk9 (process):** a deterministic optimizer put Coleman and Dulcich in all 3 lineups → **enforce the exposure cap in code, not by eye.**
9. **Wk9 (process):** the first sim portfolio put Purdy in two lineups → **distinct QB per lineup is now enforced in code** (`pick(distinct_qb=True)`) and checked by `validate.py`.
10. **Wk9 (process):** a stale starting QB (McKee vs Milton) slipped into the first handoff → **verify all 32 starting QBs from news less than 72 hours old** (§3.1 #2).
11. **Wk9 results:** _fill in after games: final portfolio = Willis/Gibbs/JSN/CMC · Purdy/Gibbs/Puka/Kittle · D. Jones/Lamb/CMC/Kittle; alternates Lock/JSN/Gibbs, Shedeur/Fannin/Gibbs/Walker, Milton/Lemon/Gibbs/Puka._

---

## 14. Kendall's profile & communication preferences

- **Goal:** win large-field GPPs. Usually 1–3 lineups.
- **Wants every angle:** film-style football reasoning, coaching tendencies, trenches, Vegas, DK Network, stats.
- **Likes:** workhorse RBs (Gibbs, Walker, McCaffrey), contrarian QBs, sleepers with history (e.g., Jeudy–Shedeur).
- **Always excludes:** Omar Cooper Jr.
- **Output format:**
  - Show the **overall best lineup first**, alongside any other answer.
  - When reviewing Kendall's lineups, give **positives before negatives**.
  - Note kickoff times for late swap. State which data was missing or uncertain.
  - **Always self-check before sending (§15).**
- **Season rule:** 2026–27 data only. Trust the uploaded salary CSV over articles when they conflict.

---

## 15A. Self-evaluation protocol (run before EVERY handoff, and show the results)

Claude must do all of this and write a short "Self-evaluation" block in the answer, **before** the lineups:
1. **Run the validator** (`engine/validate.py`) on the final lineups and every alternate. Report PASS or the exact failures.
2. **Data-freshness audit:** list every input older than 24 hours or single-sourced (salaries, starting QBs, injury tags, lines). Re-search anything that would change a lineup.
3. **Rules beyond the validator:** soft defaults from §7.2 (bring-back, lead RB on big favorite, late players in FLEX, punt DSTs). List each deviation with its reason.
4. **Adversarial pass:** "How does each lineup lose?" Name the single most fragile piece of each lineup and whether a cheap hedge exists.
5. **Requested angles:** every player/QB Kendall named must appear in the angle matrix with a number, and in the portfolio or as an alternate with a reason.
6. **Blind spots, stated plainly:** heuristic ownership, single-source salaries, uncalibrated CVs/correlations, TD lumpiness the lognormal doesn't model, no field simulation.
7. **What changed after review:** list the fixes made because of this self-evaluation. If nothing changed, say why.

## 15. Self-check before sending any lineup

- [ ] 9 players · salary ≤ $50,000 (prefer ≤ $500 left, or a deliberate dupe-avoidance leftover) · positions valid
- [ ] ≤ 3 per team · no offense vs own DST · QB + ≥1 own pass catcher (2 when available) · bring-back or a stated blowout reason
- [ ] Nobody OUT/Doubtful · Questionables have a stated plan · ≤ 2 punts
- [ ] Every salary confirmed (CSV, or 2 sources) · no 2025 data
- [ ] Kickoff times listed · late-game players in FLEX
- [ ] Across lineups: different QB/stories · pairwise overlap ≤ 3–4 · nobody in all 3 unless deliberate
- [ ] Total ownership within the contest target (§5.3) · ≥1 leverage angle per lineup
- [ ] Both models shown (deterministic + sim) · Kendall's hunches tested and reported · angle-matrix numbers shown for every requested player/QB
- [ ] Starting QBs verified from news less than 72 hours old · line moves (open → now) checked · validator PASS
- [ ] Omar Cooper Jr. excluded

---

## 16. Code reference (compact)

**Deterministic ceiling optimizer** (v1, still used as model A). Full version: `dfs/2026-wk09/model.py`.
```python
import pandas as pd
from pulp import *
def build(dk, lock=[], exclude=[], avoid=[], maxov=9, min_stack=2, bringback_team=None):
    I=dk.index; p=LpProblem("d",LpMaximize); x={i:LpVariable(f"x{i}",cat="Binary") for i in I}
    p+=lpSum(x[i]*dk.Adj[i] for i in I); p+=lpSum(x[i]*dk.Salary[i] for i in I)<=50000; p+=lpSum(x.values())==9
    P=lambda q: lpSum(x[i] for i in I if dk.Pos[i]==q)
    p+=P('QB')==1; p+=P('DST')==1; p+=P('RB')>=2; p+=P('RB')<=3; p+=P('WR')>=3; p+=P('WR')<=4; p+=P('TE')>=1; p+=P('TE')<=2
    for q in I[dk.Pos=='QB']:
        pcs=[i for i in I if dk.Team[i]==dk.Team[q] and dk.Pos[i] in('WR','TE')]
        p+=lpSum(x[i] for i in pcs)>=min(min_stack,len(pcs))*x[q]
    opp=dict(zip(dk.Team,dk.Opponent))
    if bringback_team: p+=lpSum(x[i] for i in I if dk.Team[i]==bringback_team and dk.Pos[i]!='DST')>=1
    for d in I[dk.Pos=='DST']:
        for i in I[(dk.Team==opp[dk.Team[d]])&(dk.Pos!='DST')]: p+=x[i]+x[d]<=1
    for t in dk.Team.unique(): p+=lpSum(x[i] for i in I if dk.Team[i]==t)<=3
    for prev in avoid: p+=lpSum(x[i] for i in I if dk.Name[i] in prev)<=maxov
    for i in I:
        if dk.Name[i] in lock: p+=x[i]==1
        if dk.Name[i] in exclude: p+=x[i]==0
    p.solve(PULP_CBC_CMD(msg=0)); return dk[[x[i].value()==1 for i in I]]
```
Loop over every QB (lock QB + ≥2 own pass catchers + bring-back unless the team is favored by ≥9) and keep the highest-ceiling build. Lineups 2 and 3 use `avoid=[previous lineups], maxov=3`, a different game stack, and exclude anyone already in both earlier lineups.
**Simulation engine** (model B): `dfs/engine/sim.py` (§8).
**Playbook ceiling multipliers** (model A): QB 1.45, RB 1.5, WR 1.65, TE 1.6, DST 2.0; +0.05 for rushing QBs and alpha WRs.

---

## 17. Responsible play
DFS GPPs are long shots even with optimal lineups. Week 9's final sim portfolio had about a 3% chance that *any* of the 3 lineups reaches the first-place score range (240+), and winning outright is far rarer than that. Set a fixed weekly budget you're comfortable losing, don't chase losses, and treat a winning week as variance, not proof.
