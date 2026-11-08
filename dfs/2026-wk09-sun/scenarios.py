"""Week 9 angle matrix: every QB angle x star-requirement, scored by the correlated sim."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate, candidates, pick
pool = pd.read_csv("pool_adj.csv"); S = simulate(pool, 20000)
QBS = ["Drew Lock","Shedeur Sanders","Joe Milton III","Brock Purdy","Malik Willis","Jared Goff",
       "Patrick Mahomes","Drake Maye","Jayden Daniels","Dak Prescott","Daniel Jones","Bo Nix","Matthew Stafford"]
CFG = {"Gibbs+JSN":[{"Jahmyr Gibbs"},{"Jaxon Smith-Njigba"}], "Gibbs+Puka":[{"Jahmyr Gibbs"},{"Puka Nacua"}],
       "Gibbs":[{"Jahmyr Gibbs"}], "JSN|Puka":[{"Jaxon Smith-Njigba","Puka Nacua"}], "Open":[]}
T1, T2 = 215, 240
rows, allc = [], {}
for qb in QBS:
    for cname, req in CFG.items():
        C = candidates(pool, S, n=25, seed=hash((qb,cname)) % 9999, qbs={qb}, require_any=req)
        for c in C:
            sc = S[:, list(c)].sum(1)
            allc[c] = (qb, cname)
            rows.append(dict(QB=qb, Cfg=cname, c=c, p215=(sc>=T1).mean(), p240=(sc>=T2).mean(),
                             p99=np.percentile(sc,99), med=np.median(sc), own=pool.Own.values[list(c)].sum(),
                             sal=pool.Salary.values[list(c)].sum()))
R = pd.DataFrame(rows)
best = R.sort_values("p240", ascending=False).groupby(["QB","Cfg"]).head(1)
tab = best.pivot(index="QB", columns="Cfg", values="p240").reindex(columns=list(CFG)) * 100
tab["best"] = tab.max(1); tab = tab.sort_values("best", ascending=False)
pd.set_option("display.width", 200)
print("P(lineup >= 240, Milly first-place range) %, best build per QB x requirement\n")
print(tab.round(2).to_string())
R.to_pickle("scenarios.pkl")
# portfolio over ALL angles
C = list(allc); chosen, scores, pu = pick(pool, S, C, n=3, target=T2, max_shared=3)
print(f"\nPortfolio (target {T2}): P(>=1 of 3 lineups >= {T2}) = {pu:.2%}")
for r, j in enumerate(chosen, 1):
    lu = pool.iloc[list(C[j])]; sc = scores[:, j]
    print(f"\nLineup {r} [{allc[C[j]][0]} | {allc[C[j]][1]}]  ${lu.Salary.sum():,}  med {np.median(sc):.1f}  "
          f"p99 {np.percentile(sc,99):.1f}  P>=215 {np.mean(sc>=215):.2%}  P>=240 {np.mean(sc>=240):.2%}  own {lu.Own.sum():.0f}%")
    for p in lu.sort_values("Salary", ascending=False).itertuples():
        print(f"   {p.Pos:3s} {p.Name:22s} {p.Team:3s} ${p.Salary:,}  proj {p.Proj:.1f}  own {p.Own:.0f}%  {p.Kick}")
pd.to_pickle((C, chosen), "portfolio.pkl")
