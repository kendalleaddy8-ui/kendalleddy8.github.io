"""Add k lineups to a locked set (Kendall already entered 3): million-weighted objective, many starts, ILS with the base lineups locked.
  python3 add_k.py <week> <npz> <base.csv> --k 2 --out lineups_ADD2.csv"""
import argparse, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio; portfolio.WP = {3: 120.0, 15: 10.0, 150: 1.0}
from portfolio import Port
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("base"); a.add_argument("--k", type=int, default=2)
a.add_argument("--starts", type=int, default=10); a.add_argument("--out", default="lineups_ADD2.csv"); a = a.parse_args()
P = Port(a.week, a.npz); P.w = np.array([portfolio.WP[p] for p in P.places]); P.n = 3 + a.k
base = [[P.ix[n] for n in d.Name] for _, d in pd.read_csv(os.path.join(a.week, a.base)).groupby("Lineup")]
P.C.sort(key=lambda L: -sum(w * v for w, v in zip(P.w, P.single("A", L).values())))
locks = [set(L) for L in base] + [set()] * a.k; res = []
for st in range(a.starts):
    rng = np.random.default_rng(st); order = list(range(len(P.C))) if st == 0 else list(rng.permutation(min(300, len(P.C)))) + list(range(len(P.C)))
    pk = [list(L) for L in base]
    for j in order:
        if P.ok(pk + [P.C[j]]): pk.append(P.C[j])
        if len(pk) == 3 + a.k: break
    if len(pk) < 3 + a.k: continue
    Ls, _ = P.ils(pk, locks=locks, kicks=3, seed=st); g = P.grade(Ls); res.append(((g["B"] + g["C"]) / 2, Ls)); print(f"start {st}: B {g['B']:.1f} C {g['C']:.1f}", flush=True)
res.sort(key=lambda r: -r[0]); Ls = res[0][1]
own = pd.read_csv(os.path.join(a.week, "own_est.csv")).set_index("Name").Own; rows = []
for k, L in enumerate(Ls, 1):
    d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Own"] = d.Name.map(own); d["Lineup"] = k; rows.append(d)
pd.concat(rows).to_csv(os.path.join(a.week, a.out), index=False)
pd.concat(rows[3:]).assign(Lineup=lambda d: d.Lineup - 3).to_csv(os.path.join(a.week, a.out.replace(".csv", "_new.csv")), index=False)
pd.to_pickle(res, os.path.join(a.week, a.out.replace(".csv", ".pkl"))); print("saved")
