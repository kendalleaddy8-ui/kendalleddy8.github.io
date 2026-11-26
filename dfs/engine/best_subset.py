"""Best k of an n-lineup portfolio (Kendall: 'out of the 5 give me the best 3'). Grades EVERY k-subset of the top regrade
portfolios (plus any extra lineup files given) on the same 6 worlds regrade used (seed 77), picks the best mean, writes
lineups_BEST<k>.csv in DK slot order.
  python3 best_subset.py <week> <thr.npz> <tag> --k 3 [--extra ../wed/lineups_FINAL.csv] [--top 3]"""
import argparse, itertools, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import Port, FS; from sim import simulate; from fieldprep import thresholds
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("tag"); a.add_argument("--k", type=int, default=3)
a.add_argument("--extra", action="append", default=[]); a.add_argument("--top", type=int, default=3); a = a.parse_args()
P = Port(a.week, a.npz); Z = np.load(a.npz); rng = np.random.default_rng(77); keys = ["B", "C"]
for j in range(4):
    Pn = P.pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn)))
    k = f"N{j}"; P.S[k] = simulate(Pn, 40000, seed=900 + j).astype(np.float32); P.T[k] = {f: thresholds(P.S[k], Z[f"F_{f}"].astype(int)) for f in FS}; keys.append(k)
g6 = lambda Ls: (float(np.mean([P.obj(k, Ls) for k in keys])), float(min(P.obj(k, Ls) for k in keys)))
rg = pd.read_pickle(os.path.join(a.week, f"regrade_{a.tag}.pkl"))
pool_lineups = {}
for r in rg[:a.top]:
    for L in r[4]: pool_lineups[tuple(sorted(L))] = f"{r[0]}"
for e in a.extra:
    F = pd.read_csv(e)
    for _, d in F.groupby("Lineup"):
        if all(n in P.ix for n in d.Name): pool_lineups[tuple(sorted(P.ix[n] for n in d.Name))] = os.path.basename(e)
cands = [list(L) for L in pool_lineups]; print(f"{len(cands)} distinct lineups -> {len(list(itertools.combinations(range(len(cands)), a.k)))} {a.k}-subsets", flush=True)
res = []
for idx in itertools.combinations(range(len(cands)), a.k):
    Ls = [cands[i] for i in idx]
    if not P.ok(Ls): continue
    m, w = g6(Ls); res.append((m, w, Ls))
res.sort(key=lambda r: -r[0])
for m, w, Ls in res[:5]:
    print(f"  {m:6.1f} worst {w:5.1f} :: " + " / ".join(P.names[i] for L in Ls for i in L if P.pos[i] == "QB"))
m, w, best = res[0]; own = pd.read_csv(os.path.join(a.week, "own_est.csv")).set_index("Name").Own; rows = []
for k, L in enumerate(best, 1):
    d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Own"] = d.Name.map(own); d["Lineup"] = k; rows.append(d)
pd.concat(rows).to_csv(os.path.join(a.week, f"lineups_BEST{a.k}.csv"), index=False)
print(f"BEST {a.k}: 6-world {m:.1f} (worst {w:.1f}) · full {len(rg[0][4])}-set: {g6(rg[0][4])[0]:.1f}")
