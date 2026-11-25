"""Engine v4 stress test: 'what if X has a day?' Boost players' means (and widen their tails), re-simulate against the
SAME saved fields (ownership unchanged: the field didn't see it coming), then grade the pick, every finalist and every
hunch/force test from portfolio.py.
  python3 stress.py <week> <thr.npz> <tag> --boost "Joe Milton III:1.15" [--boost "DeVonta Smith:1.05"] [--fat 0.15]"""
import argparse, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim; from fieldprep import thresholds
from portfolio import Port, FS

a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("tag")
a.add_argument("--boost", action="append", default=[]); a.add_argument("--fat", type=float, default=0.15, help="extra CV for boosted players")
a.add_argument("--sims", type=int, default=30000); a = a.parse_args()
P = Port(a.week, a.npz); Z = np.load(a.npz); R = pd.read_pickle(os.path.join(a.week, f"port_{a.tag}.pkl"))
pool = P.pool.copy(); bo = {}
for b in a.boost:
    n, m = b.rsplit(":", 1); bo[n.strip()] = float(m); pool.loc[pool.Name == n.strip(), "Proj"] *= float(m)
S = sim.simulate(pool, a.sims, seed=444).astype(np.float32)
cv0 = dict(sim.CV)
for n in bo:                                     # fatter tail: re-sim with a higher CV and splice those columns in
    pos = pool.Pos[pool.Name == n].iloc[0]; sim.CV[pos] = cv0[pos] + a.fat
    S2 = sim.simulate(pool, a.sims, seed=444).astype(np.float32); m = (pool.Name == n).to_numpy(); S[:, m] = S2[:, m]; sim.CV.update(cv0)
P.S["X"] = S; P.T["X"] = {f: thresholds(S, Z[f"F_{f}"].astype(int)) for f in FS}
rows = [("PICK", R["res"][0][1])] + [(f"finalist{k}", Ls) for k, (_, Ls) in enumerate(R["res"][1:6], 1)] + [(f"TEST {h}", Ls) for h, _, Ls in R["tests"]]
print(f"stress world: {bo} (fat +{a.fat}) — base = final set C")
for nm, Ls in rows:
    print(f"  {nm:45s} base {P.obj('C', Ls):6.1f} · stress {P.obj('X', Ls):6.1f}")
