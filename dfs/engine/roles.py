"""Role-structured portfolio (Kendall, Thanksgiving): per-lineup role constraints + million objective + parallel ILS.
roles: L1-L2 'top2games' (only CHI-DET + PHI-DAL players), L3 'anomaly' (sum own <= 150%), L4-L5 'allgames' (>=1 player from each game).
  python3 roles.py <week> <npz> <worker> <starts> <seed csv>..."""
import os, sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio; portfolio.WP = {3: 120.0, 15: 10.0, 150: 1.0}
from portfolio import Port; from validate import validate
W, npz, wk, ns = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); seeds_f = sys.argv[5:]
P = Port(W, npz); P.w = np.array([120.0, 10.0, 1.0]); P.n = 5
own = pd.read_csv(os.path.join(W, "own_est.csv")).set_index("Name").Own.reindex(P.names).fillna(1.0).to_numpy()
team = P.pool.Team.to_numpy(object); GAME = {"CHI": 0, "DET": 0, "PHI": 1, "DAL": 1, "KC": 2, "BUF": 2}
game = np.array([GAME[t] for t in team]); ROLES = ["top2games", "top2games", "anomaly", "allgames", "allgames"]
def role_ok(L, r):
    if r == "top2games": return bool((game[L] <= 1).all())
    if r == "anomaly": return own[L].sum() <= 150
    if r == "allgames": return len(set(game[L])) == 3
    return True
def ok(Ls):
    if any(not role_ok(L, ROLES[q]) for q, L in enumerate(Ls)): return False
    e = [x for x in validate([tuple(P.names[L]) for L in Ls], P.pool, max_shared=5) if "duplicate QB" not in str(x)]
    if e or len({tuple(sorted(L)) for L in Ls}) < len(Ls): return False
    return not any(P.pos[i] == "DST" for a, b in itertools.combinations(Ls, 2) for i in set(a) & set(b))
P.ok = ok
P.C.sort(key=lambda L: -sum(w * v for w, v in zip(P.w, P.single("A", L).values())))
def load(f):
    D = pd.read_csv(f)
    if "Name" in D: return [[P.ix[n] for n in d.Name] for _, d in D.groupby("Lineup") if all(n in P.ix for n in d.Name)]
    return [[P.ix[n] for n in list(r)[1:10]] for r in D.itertuples(index=False) if all(n in P.ix for n in list(r)[1:10])]
pool_c = [list(s) for s in {tuple(sorted(s)) for f in seeds_f for s in load(f)}] + [list(c) for c in P.C]
rng = np.random.default_rng(2000 + wk); res = []
for st in range(ns):
    order = list(rng.permutation(min(400, len(pool_c)))) + list(range(len(pool_c))); pk = []
    for q in range(5):
        for j in order:
            c = pool_c[j]
            if role_ok(c, ROLES[q]) and ok(pk + [c]) if q == 0 else role_ok(c, ROLES[q]) and _partial(pk + [c]) if False else role_ok(c, ROLES[q]):
                trial = pk + [c]
                e = [x for x in validate([tuple(P.names[L]) for L in trial], P.pool, max_shared=5) if "duplicate QB" not in str(x)]
                if not e and len({tuple(sorted(L)) for L in trial}) == len(trial) and not any(P.pos[i] == "DST" for a, b in itertools.combinations(trial, 2) for i in set(a) & set(b)):
                    pk.append(c); break
    if len(pk) < 5: print("start", st, "could not seed"); continue
    Ls, _ = P.ils(pk, kicks=6, seed=wk * 100 + st); g = P.grade(Ls); res.append(((g["B"] + g["C"]) / 2, Ls))
    print(f"w{wk} start {st}: A {g['A']:.1f} B {g['B']:.1f} C {g['C']:.1f}", flush=True)
res.sort(key=lambda r: -r[0])
for k, (v, Ls) in enumerate(res[:2]):
    rows = []
    for j, L in enumerate(Ls, 1):
        d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Lineup"] = j; d["Role"] = ROLES[j - 1]; rows.append(d)
    pd.concat(rows).to_csv(os.path.join(W, f"roles_w{wk}_{k}.csv"), index=False)
print("done", flush=True)
