"""Stress test (Kendall: 'Milton could have a day, Dallas defense sucks'): Milton mean x1.15 and fatter tail
(QB CV .40 -> .55), PHI pass catchers +5% (correlated via the team-pass factor), field ownership unchanged.
Scores the portfolios from port_<tag>.pkl plus 'Milton-heavy' variants on this world and on the base final set.
  python3 milton_stress.py <folder> <thr.npz> <tag>"""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../engine"))
import sim; from sim import simulate; from field_classic import sample_field; from pipeline import estimate_own
W, NPZ, TAG = sys.argv[1:4]; Z = np.load(NPZ); SC = ["f1", "f2", "f3"]; W15 = 10.0
pool = pd.read_pickle(os.path.join(W, "cands_run.pkl"))[0].reset_index(drop=True); names = pool.Name.to_numpy(object)
R = pd.read_pickle(os.path.join(W, f"port_{TAG}.pkl"))
ov = pd.read_csv(os.path.join(W, "overrides.csv")); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
P2 = pool.copy(); m = P2.Name == "Joe Milton III"; P2.loc[m, "Proj"] *= 1.15
P2.loc[(P2.Team == "PHI") & P2.Pos.isin(["WR", "TE"]), "Proj"] *= 1.05
# fatter Milton tail: simulate twice and splice Milton's column from a high-CV run
SM = simulate(P2, 30000, seed=444).astype(np.float32)
cv0 = sim.CV["QB"]; sim.CV["QB"] = 0.55; SM_hi = simulate(P2, 30000, seed=444).astype(np.float32); sim.CV["QB"] = cv0
SM[:, m.to_numpy()] = SM_hi[:, m.to_numpy()]

def thresholds(S, F, places=(15, 150), chunk=250):
    A = np.zeros((S.shape[1], len(F)), np.float32)
    for k in range(F.shape[1]): A[F[:, k], np.arange(len(F))] += 1
    out = np.zeros((len(S), 2), np.float32)
    for a in range(0, len(S), chunk):
        fs = S[a:a + chunk] @ A; top = -np.partition(-fs, 149, axis=1)[:, :150]; top.sort(1); top = top[:, ::-1]
        out[a:a + len(fs)] = top[:, [14, 149]]
    return out
TM = {}
for k, seed in [("f1", 11), ("f2", 22), ("f3", 33)]:
    r = np.random.default_rng(seed); exn = {n: o * float(np.exp(r.normal(0, 0.30))) for n, o in ex.items()}
    TM[k] = thresholds(SM, sample_field(estimate_own(pool, exn), 150000, seed=seed))
TC = {s: Z[f"C_{s}"] for s in SC}; SCS = Z["SC"]
def obj(S, T, Ls):
    sc = [S[:, L].sum(1) for L in Ls]
    return np.mean([np.logical_or.reduce([a >= T[s][:, 1] for a in sc]).mean() + W15 * np.logical_or.reduce([a >= T[s][:, 0] for a in sc]).mean() for s in SC])
mi = int(np.where(m)[0][0])
rows = []
for k, (vb, va, Ls) in enumerate(R["res"]):
    nm = sum(mi in L for L in Ls)
    rows.append((k, nm, obj(SCS, TC, Ls), obj(SM, TM, Ls), Ls))
for nm, *_ in []: pass
print("portfolio | Milton lineups | base world (final set C) | Milton-boom world")
for k, nm, b, s, Ls in sorted(rows, key=lambda r: -(r[2] + r[3])):
    print(f"  start {k:2d} | {nm} | {b*1e3:6.1f} | {s*1e3:6.1f} | " + " // ".join(n for L in Ls for n in names[L] if pool.Pos[list(L)].eq("QB").any() and n in set(pool.Name[pool.Pos == "QB"])))
pd.to_pickle(rows, os.path.join(W, f"milton_{TAG}.pkl"))

# ---- 2-Milton test: replace each lineup of the best portfolio with the best Milton candidate (distinct-QB rule relaxed) ----
from validate import validate
C = [list(c) for c in pd.read_pickle(os.path.join(W, "cands_run.pkl"))[1] if mi in c]
best = R["res"][0][2]; b0 = (obj(SCS, TC, best), obj(SM, TM, best))
print(f"\nbest portfolio: base {b0[0]*1e3:.1f} · boom {b0[1]*1e3:.1f}")
for k in range(3):
    if mi in best[k]: continue
    keep = [best[j] for j in range(3) if j != k]; sc = []
    for c in C:
        Ls = keep + [c]; e = [x for x in validate([tuple(names[L]) for L in Ls], pool, max_shared=4) if "QB" not in str(x)]
        if e: continue
        sc.append((obj(SCS, TC, Ls), obj(SM, TM, Ls), c))
    sc.sort(key=lambda r: -(r[0] + r[1]))
    for bb, bm, c in sc[:2]:
        print(f"  replace L{k+1} ({[n for n in names[best[k]] if pool.Pos[list(pool.Name).index(n)]=='QB'][0]}) with 2nd Milton: base {bb*1e3:.1f} · boom {bm*1e3:.1f} :: " + ", ".join(names[c]))
