"""Fair final test: grade lineup sets on K FRESH projection-noise worlds (seed never used by any search): standard objective,
P(any top-3), P(any top-15), P(>=1 cash).  python3 fairtest.py <week> <npz> a.csv b.csv ..."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import Port, FS; from sim import simulate; from fieldprep import thresholds
W, npz = sys.argv[1:3]; files = sys.argv[3:]; P = Port(W, npz); Z = np.load(npz); rng = np.random.default_rng(4242); keys = []
for j in range(4):
    Pn = P.pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn)))
    k = f"F{j}"; P.S[k] = simulate(Pn, 40000, seed=7000 + j).astype(np.float32); P.T[k] = {f: thresholds(P.S[k], Z[f"F_{f}"].astype(int)) for f in FS}; keys.append(k)
for f in files:
    Ls = [[P.ix[n] for n in d.Name] for _, d in pd.read_csv(f).groupby("Lineup")]
    sc = [P.obj(k, Ls) for k in keys]
    t3 = np.mean([np.logical_or.reduce([P.S[k][:, L].sum(1) >= P.T[k][fl][:, 0] for L in Ls]).mean() for k in keys for fl in FS])
    t15 = np.mean([np.logical_or.reduce([P.S[k][:, L].sum(1) >= P.T[k][fl][:, 1] for L in Ls]).mean() for k in keys for fl in FS])
    print(f"{os.path.basename(os.path.dirname(f))}/{os.path.basename(f):28s} score {np.mean(sc):6.1f} (worst {min(sc):5.1f}) · P(any top-3) {t3*1e4:5.2f}/10k · P(any top-15) {t15*1e3:5.2f}/1k")
