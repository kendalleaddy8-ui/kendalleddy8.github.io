"""Engine v4 tie-breaker: re-grade the pick, top finalists and every hunch/force test on K NEW projection-noise worlds
(same saved fields), so close calls aren't decided by one noisy holdout. Ranks by the mean over B, C and the K new sets.
  python3 regrade.py <week> <thr.npz> <tag> [--k 4] [--sims 40000]"""
import argparse, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import simulate; from fieldprep import thresholds; from portfolio import Port, FS
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("tag")
a.add_argument("--k", type=int, default=8); a.add_argument("--sims", type=int, default=40000); a.add_argument("--sigma", type=float, default=0.12)
a = a.parse_args(); P = Port(a.week, a.npz); Z = np.load(a.npz); R = pd.read_pickle(os.path.join(a.week, f"port_{a.tag}.pkl"))
rng = np.random.default_rng(77); keys = ["B", "C"]
for j in range(a.k):
    Pn = P.pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, a.sigma, len(Pn)))
    k = f"N{j}"; P.S[k] = simulate(Pn, a.sims, seed=900 + j).astype(np.float32)
    P.T[k] = {f: thresholds(P.S[k], Z[f"F_{f}"].astype(int)) for f in FS}; keys.append(k); print("world", k, "ready", flush=True)
rows = [("PICK", R["res"][0][1])] + [(f"finalist{i}", Ls) for i, (_, Ls) in enumerate(R["res"][1:6], 1)] + [(f"TEST {h}", Ls) for h, _, Ls in R["tests"]]
out = []
for nm, Ls in rows:
    v = np.array([P.obj(k, Ls) for k in keys]); out.append((nm, v.mean(), v.std() / np.sqrt(len(v)), v.min(), Ls))
out.sort(key=lambda r: -r[1])
print(f"\nmean over {len(keys)} projection-noise worlds (± s.e.), worst:")
for nm, m, se, mn, Ls in out:
    qbs = " / ".join(P.names[i] for L in Ls for i in L if P.pos[i] == "QB")
    print(f"  {nm:48s} {m:6.1f} ± {se:4.1f} · worst {mn:5.1f} · {qbs}")
pd.to_pickle(out, os.path.join(a.week, f"regrade_{a.tag}.pkl"))
