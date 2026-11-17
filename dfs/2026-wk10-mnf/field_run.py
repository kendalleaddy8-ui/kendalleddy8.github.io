"""MNF LAC@BAL: projections + simulated 59.5k-entry field -> maximize P(1st) across scenarios."""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate; from showdown import solve, sal; from field import sample_field, win_prob
t0 = time.time(); P = pd.read_csv("pool_field.csv"); N_FIELD = 59500
U, cnt, F = sample_field(P, N_FIELD, seed=3)
real = pd.Series(np.concatenate([F[:, 0], F[:, 1:].ravel()])).value_counts() / len(F) * 100
cpt_real = pd.Series(F[:, 0]).value_counts() / len(F) * 100
print(f"field: {len(F):,} entries, {len(U):,} unique, max dupes {cnt.max()}  ({time.time()-t0:.0f}s)")
print("realized own% (total / CPT): " + " · ".join(f"{P.Name[i].split()[-1]} {real.get(i,0):.0f}/{cpt_real.get(i,0):.0f}" for i in range(len(P))))
SC = {"base": {}, "ravens_rout": {"Derrick Henry": 22, "Zay Flowers": 19, "Jacoby Brissett": 18, "Ravens": 10, "Justin Herbert": 12},
      "chargers_upset": {"Justin Herbert": 21, "Quentin Johnston": 14, "Tre' Harris": 13, "Omarion Hampton": 14, "Derrick Henry": 11, "Ravens": 4},
      "shootout": {"Justin Herbert": 20, "Jacoby Brissett": 19, "Zay Flowers": 19, "Derrick Henry": 18, "Quentin Johnston": 13, "Tre' Harris": 12, "Mark Andrews": 11},
      "low_scoring": {k: v * 0.85 for k, v in zip(P.Name, P.Proj) if P.Pos[P.Name == k].iloc[0] not in ("DST", "K")}}
W = {"base": 0.35, "ravens_rout": 0.2, "chargers_upset": 0.15, "shootout": 0.1, "low_scoring": 0.2}
sims, C, Q2 = {}, set(), {}
FO = set(P.Name[P.FieldOnly == 1])
for k, ch in SC.items():
    Q = P.copy(); Q["Proj"] = [ch.get(n, p) for n, p in zip(Q.Name, Q.Proj)]
    if k == "low_scoring": Q.loc[Q.Pos == "DST", "Proj"] *= 1.3; Q.loc[Q.Pos == "K", "Proj"] *= 1.1
    S = simulate(Q, 6000, seed=len(k) * 7); sims[k] = S; Q2[k] = Q
    rng = np.random.default_rng(len(k))
    for j in rng.choice(len(S), 200, replace=False):
        own_pen = 0.0 * Q.Own.values
        lu = solve(Q, 0.6 * S[j] + 0.4 * Q.Proj.values, exclude=FO)
        if lu: C.add(lu)
    for i in range(len(Q)):
        if Q.Name[i] in FO: continue
        lu = solve(Q, Q.Proj.values, lock_cpt=i, exclude=FO)
        if lu: C.add(lu)
ixn={n:i for i,n in enumerate(P.Name)}; KL=(ixn['Derrick Henry'],tuple(sorted(ixn[n] for n in ['Ravens','Jacoby Brissett','Zay Flowers',"Tre' Harris",'Riley Patterson']))); C.add(KL); C = sorted(C); print(f"{len(C)} candidate lineups ({time.time()-t0:.0f}s)")
res = {}
for k, S in sims.items():
    pw, pt, dup = win_prob(S, U, cnt, C); res[k] = (pw, pt); print(f"  scored scenario {k} ({time.time()-t0:.0f}s)")
pw_avg = sum(W[k] * res[k][0] for k in SC); pt_avg = sum(W[k] * res[k][1] for k in SC)
rows = [dict(CPT=P.Name[c], FLEX=", ".join(P.Name[list(f)]), Sal=sal(P, (c, f)), dup=int(dup[j]),
             own=round(float(P.Own.values[list(f)].sum() + P.CptOwn[c]), 0), Pwin_per_10k=round(pw_avg[j] * 1e4, 2),
             Ptop01=round(pt_avg[j] * 100, 2), **{f"win_{k}": round(res[k][0][j] * 1e4, 2) for k in SC})
        for j, (c, f) in enumerate(C)]
R = pd.DataFrame(rows).sort_values("Pwin_per_10k", ascending=False)
top = R.head(60).index.tolist(); C2 = [C[j] for j in top]; res2 = {}
for k in SC:
    S = simulate(Q2[k], 30000, seed=1000 + len(k)); res2[k] = win_prob(S, U, cnt, C2)
R2 = R.loc[top].copy()
R2["Pwin_per_10k"] = (sum(W[k] * res2[k][0] for k in SC) * 1e4).round(2); R2["Ptop01"] = (sum(W[k] * res2[k][1] for k in SC) * 100).round(2)
for k in SC: R2[f"win_{k}"] = (res2[k][0] * 1e4).round(2)
R = pd.concat([R2, R.drop(index=top)]).sort_values("Pwin_per_10k", ascending=False)
print(f"stage 2 done ({time.time()-t0:.0f}s): top 60 rescored with 30k sims x 5 scenarios")
pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 75)
print("\nTop 10 by weighted P(1st place) [per 10,000 contests]:"); print(R.head(10).to_string(index=False))
print("\nBest P(1st) by captain:"); print(R.groupby("CPT").Pwin_per_10k.max().sort_values(ascending=False).to_string())
kr=R[(R.CPT=="Derrick Henry")&(R.FLEX.str.contains("Riley Patterson"))&(R.FLEX.str.contains("Ravens"))&(R.FLEX.str.contains("Jacoby Brissett"))&(R.FLEX.str.contains("Tre"))]
print("\nKENDALL:"); print(kr.to_string(index=False)); print("rank", (R.Pwin_per_10k>kr.Pwin_per_10k.max()).sum()+1, "of", len(R))
R.to_csv("field_table.csv", index=False)
