# Week 9 2026 — DK Classic Main Slate (Sun Nov 8, 11 games)

Built from the GPP playbook. `pool.csv` = 76 players whose DK salary was confirmed in Week 9 2026 articles
(no DKSalaries.csv was uploaded). `python3 model.py` reproduces everything (`pulp==2.8.0`).

**Games / implied totals:** SF 30.75–LV 21.25 · KC 28.75–NYJ 19.25 · DET 28.5–MIA 22.0 · DAL 28.0–IND 23.5 ·
LAR 26.0–WAS 21.5 · NE 24.0–GB 21.5 · SEA 24.0–ARI 15.5 · DEN 23.5–CAR 21.0 · HOU 23.25–LAC 17.25 ·
NO 22.75–CLE 19.75 · NYG 20.75–PHI 17.75. Late games: HOU@LAC, LV@SF 4:05 · GB@NE, ARI@SEA 4:25.

**Key news:** SF WR Evans & Deebo OUT · SEA Darnold OUT (Lock starts) · NE A.J. Brown OUT, Henderson OUT ·
PHI DeVonta Smith & Wicks OUT, **Joe Milton III named starter** (Hurts out for season) · NYJ Garrett Wilson OUT, Breece Hall back (limited) ·
NYG Skattebo doubtful · CLE Watson inactive (Shedeur starts) · WAS McLaurin IR · St. Brown (ribs) expected to play.

| | L1 Purdy (best) | L2 Willis | L3 Daniels |
|---|---|---|---|
| QB | Brock Purdy SF $6,800 | Malik Willis MIA $5,100 | Jayden Daniels WAS $6,000 |
| RB | Christian McCaffrey SF $8,000 | Jahmyr Gibbs DET $10,000 | Jahmyr Gibbs DET $10,000 |
| RB | Jonah Coleman DEN $5,300 | Chuba Hubbard CAR $6,500 | Ollie Gordon II MIA $5,600 |
| WR | Puka Nacua LAR $8,800 | Malik Nabers NYG $7,300 | Puka Nacua LAR $8,800 |
| WR | Demario Douglas NE $4,800 | Malik Washington MIA $4,700 | Malik Washington MIA $4,700 |
| WR | Efton Chism III NE $3,600 | Adonai Mitchell NYJ $4,500 | Antonio Williams WAS $4,100 |
| TE | Greg Dulcich MIA $3,100 | Greg Dulcich MIA $3,100 | Harold Fannin Jr. CLE $4,700 |
| FLEX | George Kittle SF $6,000 | Jonah Coleman DEN $5,300 | Efton Chism III NE $3,600 |
| DST | Texans $3,500 | Texans $3,500 | Eagles $2,500 |
| Salary | $49,900 | $50,000 | $50,000 |
| Proj / Ceiling | 151.3 / 241.2 | 149.3 / 237.2 | 144.8 / 231.3 |

Walker option for L2: Walker + Lemon in for Hubbard + Nabers → ceiling 234.9, same median, $49,900, Walker at 4:25.

## v2.1 — final after self-review (sim portfolio, `final.py`; validator PASS)
| | L1 Willis (DET–MIA shootout) | L2 Purdy (SF blowout) | L3 D. Jones (DAL–IND shootout) |
|---|---|---|---|
| QB | Malik Willis $5,100 | Brock Purdy $6,800 | Daniel Jones $4,700 |
| RB | Jahmyr Gibbs $10,000 | Jahmyr Gibbs $10,000 | Christian McCaffrey $8,000 |
| RB | Christian McCaffrey $8,000 | Ollie Gordon II $5,600 | Jonah Coleman $5,300 |
| WR | Jaxon Smith-Njigba $9,300 | Puka Nacua $8,800 | CeeDee Lamb $8,300 |
| WR | Malik Washington $4,700 | Antonio Williams $4,100 | Josh Downs $5,100 |
| WR | Efton Chism III $3,600 | Efton Chism III $3,600 | Keenan Allen $4,900 |
| TE | Darren Waller $3,300 | Greg Dulcich $3,100 | George Kittle $6,000 |
| FLEX | Greg Dulcich $3,100 | George Kittle $6,000 | Demario Douglas $4,800 |
| DST | Saints $2,900 | Cardinals $2,000 | Giants $2,800 |
| P(≥240) | 1.47% | 1.30% | 0.77% |
Portfolio P(≥1 lineup ≥240) = 3.17%. Alternates (validator PASS): Lock+JSN+McBride+Gibbs 0.89% · Shedeur+Fannin+Concepcion+Olave+Gibbs+Walker 0.94% · Milton+Lemon+Singletary+Gibbs+Puka 1.02%.
