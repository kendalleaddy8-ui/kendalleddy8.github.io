# Week 11 (Sun Nov 22 2026) — final
Sources: ESPN DK values wk11 (salaries/proj, all of Kendall's screen salaries matched except C. Allen = screen), DK Network injury report (Sat 4:30 PM), chalk board, DvP, Swift/Monangai + EJ articles; ESPN odds (open→now); 4for4 wk11 trenches.
News: Walker OUT (EJ lead, 55-80% own) · ARI QB Josh Johnson (Beck OUT) · Ferguson OUT · Kincaid D · McConkey/Bowers/Waller/Tate/Mayfield Q · Monangai back.
Method: engine (720 cands) → Classic field sim (150k-entry Milly, ownership model, stacking) → 3 ownership scenarios × 10k sims (field_final.txt) → lesson-21 variant check.
Final: L1 Geno/Cook/Javonte/Hampton/Lamb/Mitchell/Odunze/M.Taylor/Steelers (p15 1.10/1k, p150 0.77%) ·
L2 Dak/Pollard/Coleman/Lamb/Pickens/Ayomanor/Otton/Helm/Chiefs (p15 0.90/1k, p150 0.63%) · shared: Lamb only · validator PASS.
Kendall A 0.00/1k · Kendall B 0.17/1k (p15).

## FINAL v2 (Sat 11:50 PM ET) — all layers: props/ATD market calibration, coaching (PROE/pace/Payton/blowout pulls), weather, Thanksgiving short week, off-bye
Pair from holdout-validated local search (B-score 42.8 vs 35.7 for v1 pair):
- L1 Bryce Young / Javonte / Pollard / Lamb / McMillan / Ja'Kobi Lane / Tremble / FLEX Hampton / Steelers — top-150 0.74%
- L2 Bo Nix / Javonte / Pollard / Pickens / Waddle / Metcalf / Engram / FLEX Skattebo / Chiefs — top-150 0.72%
- L3 (optional, +39% Milly top-150 odds: 1.45% -> 2.02%) Geno / Cook / EJ / Lamb / G. Wilson / Mitchell / Waller / FLEX Hampton / Buccaneers
- 4pm slate (top-0.1% of 30k field 1.70%): Geno / Coleman / Skattebo / Nabers / G. Wilson / Mitchell / Likely / FLEX Hampton / Broncos
Pivots: Tremble OUT -> Cade Otton + (Pollard -> Emmett Johnson). Waller OUT -> Cade Otton.

## FINAL v3 (Sun 9:50 AM ET) — Sunday news + 24k/24k sims, 67 local optima from 94 starts
Dak / Pollard / Hampton / Lamb / Pickens / G. Wilson / Waller / FLEX Tremble / Steelers — holdout top-15 2.38/1k, top-150 1.33%
(old pick re-scored with Sunday news: 1.29/1k, 0.87%). Pivots: Waller OUT -> Mason Taylor; Tremble OUT -> Dawson Knox; both -> Knox + Mark Andrews.

## FINAL PAIR (Sun 11:45 AM ET) — pair search on 24k/24k sims, holdout union top-15 4.21/1k, top-150 2.38%
L1 Dak / Pollard / Hampton / Lamb / Pickens / G. Wilson / Waller / FLEX Tremble / Steelers (alone 2.38/1k, 1.33%)
L2 Bo Nix / Pollard / Coleman / Lamb / Pickens / Ayomanor / Engram / FLEX Hampton / Chiefs (alone 1.86/1k, 1.14%)
Shares 4 (Pollard, Hampton, Lamb, Pickens): concentration on DAL-TEN beats best <=3-shared pair (3.25/1k, 1.93%). Q-TE hedge: CAR TEs only in L1.

## 4PM-ONLY (Sun 2:05 PM ET) — 30k-entry field x3 ownership scenarios, 15k/15k sims, 22 local optima
Nix / Coleman / Tuten / G. Wilson / Waddle / Mitchell / Likely / FLEX Skattebo / Jets — holdout P(1st) 34.7/10k, top-3 6.89/1k, top-0.1% 3.06%
