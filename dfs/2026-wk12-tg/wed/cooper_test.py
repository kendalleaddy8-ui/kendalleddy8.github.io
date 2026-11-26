"""selfeval flag (lesson 21): Darius Cooper ($3,600, 5% owned) is in 2 of the 3 finals. For each of those lineups, swap Cooper
for the best legal alternative (chosen on sims A), then grade all variants on the same 6 worlds regrade used (seed 77).
  python3 cooper_test.py <thr.npz>"""
import os, sys, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "../../engine"))
from portfolio import Port, FS; from sim import simulate; from fieldprep import thresholds; from validate import slots_ok
P = Port(H, sys.argv[1]); Z = np.load(sys.argv[1]); rng = np.random.default_rng(77); keys = ["B", "C"]
for j in range(4):
    Pn = P.pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn)))
    k = f"N{j}"; P.S[k] = simulate(Pn, 40000, seed=900 + j).astype(np.float32); P.T[k] = {f: thresholds(P.S[k], Z[f"F_{f}"].astype(int)) for f in FS}; keys.append(k)
g6 = lambda Ls: (np.mean([P.obj(k, Ls) for k in keys]), min(P.obj(k, Ls) for k in keys))
F = pd.read_csv(os.path.join(H, "lineups_FINAL.csv")); base = [[P.ix[n] for n in d.Name] for _, d in F.groupby("Lineup")]
ci = P.ix["Darius Cooper"]; m, w = g6(base); print(f"FINAL (Cooper x2): 6-world {m:.1f} · worst {w:.1f}")
for q in [q for q in range(3) if ci in base[q]]:
    L = base[q]; i = L.index(ci); room = 50000 - (P.sal[L].sum() - P.sal[ci]); res = []
    for c in np.where((P.sal <= room) & np.isin(P.pos, ["RB", "WR", "TE"]))[0]:
        if c in L: continue
        tr = list(L); tr[i] = c
        if not slots_ok(list(P.pos[tr])): continue
        Ls = [tr if r == q else base[r] for r in range(3)]
        if P.ok(Ls): res.append((P.obj("A", Ls), c, Ls))
    res.sort(key=lambda r: -r[0])
    for _, c, Ls in res[:3]:
        m2, w2 = g6(Ls); print(f"  L{q+1}: Cooper -> {P.names[c]:20s} ${int(P.sal[c]):,}: 6-world {m2:.1f} · worst {w2:.1f}")
