# Week 10 (Sun Nov 15 2026) — Kendall's lineups A/B review + portfolio
Sources: ESPN DK values wk10 (salaries+proj, 15/15 matched Kendall's DK screens), DK Network injury report / chalk / picks / Millionaire (Nov 13-14),
EatDrinkAndSleepFootball odds (Sat 12:01 ET), 4for4 wk10 trenches. Kicks: SEA-LV & LAR-ARI 4:05, SF-DAL 4:25 (DK screen); rest 1:00.
Key news: Walker III OUT -> Emmett Johnson lead KC RB (Base 15.5 override). Puka IR, Adams IR, Jacobs OUT. Lock starts (no designation). Beck first career start.
Sim P(>=210): Kendall A 1.21% · Kendall B 2.13% · A-fixed BB 2.16% · B-fixed 3.75% · Best (Lawrence GS) 5.83%.
Portfolio: 1 = Best · 2 = Best + B-fixed (8.23%) · 3 = Lawrence no JJ/EJ + B-fixed + A-fixed BB (8.76%, nobody in all 3; 9.30% if rule ignored).
Files: modelA.py (ceiling optimizer + game-stack search), evaluate.py, variants.py, portfolio.py, final_lineups.csv, run.txt (engine).

## v2 re-run (Sun 8 AM ET)
New news: Hockenson OUT (kills v1 "A-fixed"), Jennings OUT + Addison Q (GTD) -> Jefferson target funnel; Micah Parsons OUT (GB) -> MIN pass-pro +2;
SEA LT Cross + Q. Nelson OUT (Lock x0.95); HOU Hunter OUT / Anderson Q (CLE +1); NO OL Fuaga+McCoy OUT; DAL Jake Ferguson OUT; Rams Avila + T. Ferguson OUT;
Higbee 59% routes vs Parkinson 37% (FantasyLabs); Gordon 73% snaps/82% inside-5 vs IND 4th-most to RBs (Fantasy Life) -> x1.06; EJ own ~50-60% (4for4).
Weather (ffbeacon): no concerns; NYJ gusts 22, CLE light rain. Walker: DK Net says OUT Sat; NFL.com page still Q -> confirm at inactives.
Sim P(>=210): Best v1 5.65% (unchanged #1) · Lock GS 4.60% · Cousins hunch (GB BB) 2.49% · B-fixed v1 3.46% · Kendall A 1.47% · Kendall B 2.09%.
Portfolio: 2 = Best v1 + Lock GS 8.66% · 3 = Best v1 + B-fixed v1 + Cousins hunch 9.05% (only JJ in all 3). Files: v2.py, v2port*.py, v2.txt, final_lineups_v2.csv.
