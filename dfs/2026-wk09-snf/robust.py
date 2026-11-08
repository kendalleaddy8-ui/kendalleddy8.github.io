"""Pick ONE showdown lineup that is best on average across projection scenarios (handbook §8 'all angles')."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate; from showdown import solve, score, sal
base = pd.read_csv("pool.csv"); T = 150
SC = {"base": {},
      "bears_boom": {"Caleb Williams": 22, "D'Andre Swift": 19.5, "Luther Burden III": 16, "Colston Loveland": 12.5, "Rome Odunze": 12},
      "bucs_close": {"Bucky Irving": 18, "Kenneth Gainwell": 10, "Baker Mayfield": 15.5, "Emeka Egbuka": 12.5, "Bears": 5.5},
      "loveland_low": {"Colston Loveland": 9.5},
      "swift_regress": {"D'Andre Swift": 15.0}}
sims, cands = {}, set()
for k, ch in SC.items():
    P = base.copy(); P["Proj"] = [ch.get(n, p) for n, p in zip(P.Name, P.Proj)]
    S = simulate(P, 20000, seed=hash(k) % 999); sims[k] = S
    rng = np.random.default_rng(len(k))
    for j in rng.choice(len(S), 250, replace=False):
        lu = solve(P, 0.5 * S[j] + 0.5 * P.Proj.values)
        if lu: cands.add(lu)
    for i in range(len(P)):
        if P.Pos[i] != "DST":
            lu = solve(P, P.Proj.values, lock_cpt=i)
            if lu: cands.add(lu)
cands = sorted(cands); print(len(cands), "unique lineups across 5 scenarios")
rows = []
for lu in cands:
    ps = {k: float(np.mean(score(S, lu) >= T)) for k, S in sims.items()}
    rows.append(dict(CPT=base.Name[lu[0]], FLEX=", ".join(base.Name[list(lu[1])]), Sal=sal(base, lu), avg=np.mean(list(ps.values())),
                     worst=min(ps.values()), **ps))
R = pd.DataFrame(rows).sort_values("avg", ascending=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
fmt = R.head(8).copy()
for c in ["avg", "worst"] + list(SC): fmt[c] = (fmt[c] * 100).round(2)
print(fmt.to_string(index=False))
print("\nBest avg P by captain:"); print((R.groupby("CPT").avg.max() * 100).round(2).sort_values(ascending=False).to_string())
mine = R[(R.CPT == "Caleb Williams") & R.FLEX.str.contains("Bears") & R.FLEX.str.contains("Durham") & R.FLEX.str.contains("Loveland") & R.FLEX.str.contains("Burden") & R.FLEX.str.contains("Swift")]
print("\nKendall's draft:", (mine[["avg","worst"]]*100).round(2).to_dict("records") if len(mine) else "not in candidate set")
R.to_csv("robust_table.csv", index=False)
