"""Wednesday pool: Mike Clay's Week 12 Fantasy Playbook projections (ESPN, PPR) -> DK scale, team totals moved halfway
toward Vegas implied: Base = Clay_DK x (Vegas_implied / Clay_team_pts)^0.5. Depth players not in Clay's tables: stand-in Base x the
team's median Clay/stand-in ratio (capped 0.70-1.10). DST: mean(Clay, Vegas formula)."""
import os, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
L = pd.read_csv(os.path.join(H, "lines.csv")); imp = dict(zip(L.Team, L.Total / 2 - L.Spread / 2))
CLAY_PTS = {"DET": 28, "CHI": 24, "DAL": 31, "PHI": 19, "KC": 25, "BUF": 24}
DSTN = {"Bears": "CHI", "Lions": "DET", "Cowboys": "DAL", "Eagles": "PHI", "Chiefs": "KC", "Bills": "BUF"}
clay = pd.read_csv(os.path.join(H, "clay_playbook.csv")); clay["Name"] = clay.Name.replace({"Patrick Mahomes": "Patrick Mahomes II"})
clay.loc[clay.Pos == "DST", "Team"] = clay.loc[clay.Pos == "DST", "Name"].map(DSTN)
clay = clay[clay.Team.isin(CLAY_PTS)]
old = pd.read_csv(os.path.join(H, "..", "espn_pool.csv"))
adj = {t: (imp[t] / CLAY_PTS[t]) ** 0.5 for t in CLAY_PTS}
def dk(r):
    if r.Pos == "QB": return (r.Clay + 0.8) * adj[r.Team]
    if r.Pos == "DST":
        opp = L.set_index("Team").Opponent[r.Team]; return 0.5 * r.Clay + 0.5 * (6.5 - 0.35 * (imp[opp] - 20))
    return r.Clay * (1.04 if r.Clay >= 12 else 1.0) * adj[r.Team]
clay["Base"] = clay.apply(dk, axis=1); cb = dict(zip(clay.Name, clay.Base))
m = old.merge(clay[["Name", "Base"]].rename(columns={"Base": "CB"}), on="Name", how="left")
ratio = m.dropna(subset=["CB"]).assign(r=lambda d: d.CB / d.Base).groupby("Team").r.median().clip(0.70, 1.10).to_dict()
m["Base"] = [round(cb[n], 1) if n in cb else round(b * ratio.get(t, 1.0), 1) for n, b, t in zip(m.Name, m.Base, m.Team)]
m = m.drop(columns="CB"); m.to_csv(os.path.join(H, "espn_pool.csv"), index=False)
print("team adj (Vegas/Clay)^.5:", {k: round(v, 3) for k, v in adj.items()}); print("depth ratio:", {k: round(v, 2) for k, v in ratio.items()})
print(m.sort_values("Base", ascending=False).head(30)[["Name", "Team", "Pos", "Salary", "Base"]].to_string(index=False))
