"""Ultimate warm run (Thanksgiving last call): n lineups, ALL unlocked, seeded from every strong lineup found tonight,
million objective (top-3 120 / top-15 10 / top-150 1), duplicate-QB rule relaxed (other rules kept), many ILS starts with kicks.
Worker w runs starts [w*S, (w+1)*S).  python3 ultimate.py <week> <npz> <worker> <starts> <seed csv>..."""
import os, sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio; portfolio.WP = {3: 120.0, 15: 10.0, 150: 1.0}
from portfolio import Port; from validate import validate
W, npz, wk, ns = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); seeds_f = sys.argv[5:]
P = Port(W, npz); P.w = np.array([120.0, 10.0, 1.0]); P.n = 5
def ok(Ls):
    e = [x for x in validate([tuple(P.names[L]) for L in Ls], P.pool, max_shared=5) if "duplicate QB" not in str(x)]
    if e: return False
    if len({tuple(sorted(L)) for L in Ls}) < len(Ls): return False
    return not any(P.pos[i] == "DST" for a, b in itertools.combinations(Ls, 2) for i in set(a) & set(b))
P.ok = ok
P.C.sort(key=lambda L: -sum(w * v for w, v in zip(P.w, P.single("A", L).values())))
def load(f):
    D = pd.read_csv(f)
    if "Name" in D: return [[P.ix[n] for n in d.Name] for _, d in D.groupby("Lineup") if all(n in P.ix for n in d.Name)]
    return [[P.ix[n] for n in list(r)[1:10]] for r in D.itertuples(index=False) if all(n in P.ix for n in list(r)[1:10])]
seeds = [list(s) for s in {tuple(sorted(s)) for f in seeds_f for s in load(f)}]
rng = np.random.default_rng(1000 + wk); res = []
for st in range(ns):
    order = list(rng.permutation(len(seeds))) + [None] * 0
    pk = []
    for j in order:
        if ok(pk + [seeds[j]]) or not pk: pk.append(seeds[j])
        if len(pk) == 5: break
    for c in P.C:
        if len(pk) == 5: break
        if ok(pk + [list(c)]): pk.append(list(c))
    Ls, _ = P.ils(pk, kicks=8, seed=wk * 100 + st); g = P.grade(Ls); res.append(((g["B"] + g["C"]) / 2, Ls))
    print(f"w{wk} start {st}: A {g['A']:.1f} B {g['B']:.1f} C {g['C']:.1f}", flush=True)
res.sort(key=lambda r: -r[0])
for k, (v, Ls) in enumerate(res[:2]):
    rows = []
    for j, L in enumerate(Ls, 1):
        d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Lineup"] = j; rows.append(d)
    pd.concat(rows).to_csv(os.path.join(W, f"ult_w{wk}_{k}.csv"), index=False)
print("done", flush=True)
