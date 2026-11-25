"""Thanksgiving pool (no ESPN values article yet): FantasyPros DK salaries + prior ESPN projections
rescaled to this week's Vegas implied totals, blended with FantasyPros' free top-10 projections.
  python3 build_pool.py   -> espn_pool.csv (Name,Rating,Team,Opponent,Pos,Base,Salary)
Re-run with the real ESPN table once it publishes (then use fetch.py espn instead)."""
import pandas as pd, numpy as np, os
H = os.path.dirname(os.path.abspath(__file__)); R = lambda *p: os.path.join(H, "..", *p)
imp = lambda L: dict(zip(L.Team, L.Total / 2 - L.Spread / 2))
now = imp(pd.read_csv(os.path.join(H, "lines.csv")))
sal = pd.read_csv(os.path.join(H, "fp_salaries.csv"))

# priors: latest ESPN Base per player (wk11, then wk10, wk9), normalised by that week's implied total
pri = {}
for wk in ("2026-wk09", "2026-wk10", "2026-wk11"):
    P = pd.read_csv(R(wk, "espn_pool.csv")); I = imp(pd.read_csv(R(wk, "lines.csv")))
    for r in P.itertuples():
        if r.Team in now and r.Team in I: pri[(r.Name.replace("Patrick Mahomes", "Patrick Mahomes II"), r.Team)] = (r.Base, I[r.Team], wk)

def dst_proj(opp_imp, team):                     # wk11 fit: ~6.5 at 20 implied, -0.35 per point
    return round(6.5 - 0.35 * (opp_imp - 20), 1)

# manual priors for players with no ESPN history on these teams / role changes (sources in Note)
MANUAL = {
    "Kenneth Walker III": 20.0,   # wk10 27.9 at 25.5 implied; groin, limited Tue; FP 19.9 -> haircut for EJ share
    "Emmett Johnson": 9.0,        # 23-105-1 with Walker out wk11; if Walker plays he is the change-up (wk9-10: 6.5-7.6)
    "Patrick Mahomes II": 18.5,   # wk10 19.1 @25.5, wk11 23.5 @28.5 -> 22.25 implied; FP < 18.05 (not top 10)
    "Dontayvion Wicks": 4.5,      # salary -$1,300, unranked by FP ECR -> role collapse
    "Darius Cooper": 6.5, "Will Shipley": 6.0, "Tank Bigsby": 3.5, "KaVontae Turpin": 4.5,
    "Cyrus Allen": 4.5, "Noah Gray": 4.0, "Ray Davis": 4.0, "Kendre Miller": 4.0, "Isaac TeSlaa": 3.5,
    "Roschon Johnson": 3.0, "Tanner McKee": 3.0,
}
fp = pd.read_csv(os.path.join(H, "fp_proj.csv")); fpm = dict(zip(fp.Name, fp.FP_fpts))
rows = []
for r in sal.itertuples():
    if r.Pos == "DST":
        b = dst_proj(now[r.Opponent], r.Team)
    elif r.Name in MANUAL:
        b = MANUAL[r.Name]
    elif (r.Name, r.Team) in pri:
        b0, i0, _ = pri[(r.Name, r.Team)]; e = 1.0 if r.Pos == "QB" else 0.85
        b = b0 * (now[r.Team] / i0) ** e
    else:
        continue                                  # no projection = punt-level depth, excluded
    if r.Name in fpm and r.Pos != "DST":          # FP PPR ~ DK minus bonuses; blend 35%
        b = 0.65 * b + 0.35 * (fpm[r.Name] + (0.6 if fpm[r.Name] >= 17 else 0.2))
    rows.append(dict(Name=r.Name, Rating="", Team=r.Team, Opponent=r.Opponent, Pos=r.Pos, Base=round(b, 1), Salary=r.Salary))
out = pd.DataFrame(rows).sort_values("Base", ascending=False)
out.to_csv(os.path.join(H, "espn_pool.csv"), index=False)
print(len(out), "players"); print(out.head(45).to_string(index=False))
