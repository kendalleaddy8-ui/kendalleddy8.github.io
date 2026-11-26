"""'Win the million' variant: same search, objective re-weighted toward top-3 (weights 120/10/1 vs 40/10/1),
warm-started from the final contenders. Reports top-3 / top-15 / cash odds for it and the balanced pick.
  python3 million.py <week> <thr.npz> <balanced.csv> <seed.csv>..."""
import os, sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio; portfolio.WP = {3: 120.0, 15: 10.0, 150: 1.0}
from portfolio import Port; from cashline import cash_odds
W, npz, bal = sys.argv[1:4]; seeds_f = sys.argv[4:]
P = Port(W, npz); P.w = np.array([portfolio.WP[p] for p in P.places]); P.n = 3; Z = np.load(npz)
P.C.sort(key=lambda L: -sum(w * v for w, v in zip(P.w, P.single("A", L).values())))
def load(f): return [[P.ix[n] for n in d.Name] for _, d in pd.read_csv(f).groupby("Lineup") if all(n in P.ix for n in d.Name)]
seeds = list({tuple(sorted(s)) for f in seeds_f for s in load(f)}); seeds = [list(s) for s in seeds]
starts = [list(c) for c in itertools.combinations(seeds, 3) if P.ok(list(c))]
starts.sort(key=lambda Ls: -P.obj("A", Ls)); res = []
for k, st in enumerate(starts[:6]):
    Ls, _ = P.ils(st, kicks=3, seed=k); g = P.grade(Ls); res.append(((g["B"] + g["C"]) / 2, Ls)); print(f"million start {k}: B {g['B']:.1f} C {g['C']:.1f}", flush=True)
best = max(res, key=lambda r: r[0])[1]
def report(nm, Ls):
    s = [P.single("C", L) for L in Ls]; c = cash_odds(Z, Ls)
    anyt3 = np.mean([np.logical_or.reduce([P.S["C"][:, L].sum(1) >= P.T["C"][f][:, 0] for L in Ls]).mean() for f in ["f1", "f2", "f3"]])
    print(f"{nm}: P(any top-3) {anyt3*1e4:.2f}/10k · top-15 per lineup {[round(x[15]*1e3,2) for x in s]}/1k · P(>=1 cash) {c['any']*100:.1f}%")
report("BALANCED", load(bal)); report("MILLION", best)
rows = []
for k, L in enumerate(best, 1):
    d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Lineup"] = k; rows.append(d)
    print(k, d.Salary.sum(), " | ".join(f"{a} {b}" for a, b in zip(d.Slot, d.Name)))
pd.concat(rows).to_csv(os.path.join(W, "lineups_MILLION.csv"), index=False)
