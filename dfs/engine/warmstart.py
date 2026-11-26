"""Warm-start portfolio search: start iterated local search from the best lineups already found (any lineup CSVs),
re-optimised under the current pool/fields. Faster and usually better than cold greedy starts.
  python3 warmstart.py <week> <thr.npz> --n 3 --seed-file a.csv --seed-file b.csv [--tag warm]"""
import argparse, itertools, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import Port
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("--n", type=int, default=3)
a.add_argument("--seed-file", action="append", default=[]); a.add_argument("--tag", default="warm"); a = a.parse_args()
P = Port(a.week, a.npz); P.n = a.n
so = lambda L: sum(w * v for w, v in zip(P.w, P.single("A", L).values())); P.C.sort(key=so, reverse=True)
seeds = []
for f in a.seed_file:
    F = pd.read_csv(f)
    for _, d in F.groupby("Lineup"):
        if all(n in P.ix for n in d.Name): seeds.append([P.ix[n] for n in d.Name])
seeds = [list(x) for x in {tuple(sorted(s)) for s in seeds}]; print(len(seeds), "seed lineups", flush=True)
starts = []
for combo in itertools.combinations(range(len(seeds)), a.n):
    Ls = [seeds[i] for i in combo]
    if P.ok(Ls): starts.append(Ls)
starts.sort(key=lambda Ls: -P.obj("A", Ls)); res = []
for k, st in enumerate(starts[:8]):
    Ls, v = P.ils(st, kicks=3, seed=k); g = P.grade(Ls); res.append((g, Ls))
    print(f"warm {k}: A {g['A']:.1f} B {g['B']:.1f} C {g['C']:.1f}", flush=True)
res.sort(key=lambda r: -(r[0]["B"] + r[0]["C"]))
rows = []
for k, L in enumerate(res[0][1], 1):
    d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Lineup"] = k; rows.append(d)
pd.concat(rows).to_csv(os.path.join(a.week, f"lineups_{a.tag}.csv"), index=False); print("saved", f"lineups_{a.tag}.csv")
