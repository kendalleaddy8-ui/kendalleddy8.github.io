"""Robust final ranking: 3 ownership scenarios (flat / calibrated / chalky) x 20k sims each, vs 150k-entry field."""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate; from field_classic import sample_field, rank_vs_field
from pipeline import estimate_own; from validate import validate
t0 = time.time(); top = pd.read_pickle("field_top.pkl"); allR = pd.read_pickle("field_all.pkl")
pool, C = pd.read_pickle("cands_run.pkl")
if "C. Allen (KC)" not in set(pool.Name):
    row = pool[pool.Name == "Josh Downs"].iloc[0].copy()
    row["Name"], row["Salary"], row["Base"], row["Proj"], row["Adj"], row["Own"], row["Status"] = "C. Allen (KC)", 3200, 3.0, 3.0, 4.95, 1.0, ""
    pool = pd.concat([pool, row.to_frame().T], ignore_index=True)
    for c in ("Salary", "Base", "Proj", "Adj", "Own", "Spread", "Total"): pool[c] = pd.to_numeric(pool[c])
ov = pd.read_csv("overrides.csv"); explicit = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
explicit.update({"C. Allen (KC)": 0.5, "Jalon Daniels": 0.0})
# candidate set: stage-1 top 40 by p15 and by p150 (from the first field run) + Kendall's
cand = pd.concat([allR.sort_values("p15", ascending=False).head(40), allR.sort_values("p150", ascending=False).head(40), allR[allR.tag != ""]]).drop_duplicates("name")
L = list(cand.lu); print(f"{len(L)} finalists")
S = simulate(pool, 10000, seed=2026)
res = []
for k, ts in [("flat", 0.7), ("calibrated", 1.0), ("chalky", 1.35)]:
    P2 = estimate_own(pool, explicit, temp_scale=ts)
    if k == "calibrated":
        print("calibrated own, top by position:", " | ".join(f"{p}: " + ", ".join(f"{n} {o:.0f}" for n, o in P2[P2.Pos == p].sort_values("Own", ascending=False).head(4)[["Name", "Own"]].values) for p in ["QB", "RB", "WR", "TE", "DST"]))
    F = sample_field(P2, 150000, seed=7 + int(ts * 10))
    r = rank_vs_field(S, F, L, places=(1, 15, 150)); res.append(r)
    print(f"  scenario {k} done ({time.time()-t0:.0f}s)")
cand = cand.assign(p1=np.mean([r[1] for r in res], 0), p15=np.mean([r[15] for r in res], 0), p150=np.mean([r[150] for r in res], 0),
                   p15_min=np.min([r[15] for r in res], 0))
cand["own_cal"] = [estimate_own(pool, explicit).Own.values[list(l)].sum() for l in cand.lu]
cand = cand.sort_values(["p15", "p150"], ascending=False)
show = cand[["tag", "qb", "sal", "own_cal", "p1", "p15", "p15_min", "p150", "name"]].copy()
for c, f in [("p1", 1e4), ("p15", 1e3), ("p15_min", 1e3), ("p150", 100)]: show[c] = (show[c] * f).round(2)
pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 150)
print("p1 = wins/10k · p15 = top-15 per 1k (avg of 3 own scenarios) · p15_min = worst scenario · p150 = top-0.1% %")
print(show.head(15).to_string(index=False)); print(show[show.tag != ""].to_string(index=False))
cand.to_pickle("field_final.pkl")
