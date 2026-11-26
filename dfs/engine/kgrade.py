"""Grade arbitrary lineup sets (names) incl. players outside the sim pool: append them (Base from DK FPPG-ish) and re-simulate fresh worlds against the SAVED fields."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import Port, FS; from sim import simulate; from fieldprep import thresholds
W, npz = sys.argv[1:3]; files = sys.argv[3:]; P = Port(W, npz); Z = np.load(npz)
EXTRA = {"Zavion Thomas": ("CHI", "DET", "WR", 3200, 3.0, "1:00"), "James Mitchell": ("DAL", "PHI", "TE", 2700, 2.5, "4:30")}
pool = P.pool.copy()
for n, (t, o, p, s, pr, k) in EXTRA.items():
    if n not in set(pool.Name): pool = pd.concat([pool, pd.DataFrame([{"Name": n, "Team": t, "Opponent": o, "Pos": p, "Salary": s, "Proj": pr, "Kick": k}])], ignore_index=True)
ix = {n: i for i, n in enumerate(pool.Name)}; rng = np.random.default_rng(int(os.environ.get('KG_SEED', 4242))); worlds = []
for j in range(int(os.environ.get('KG_WORLDS', 4))):
    Pn = pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn))); S = simulate(Pn, 40000, seed=7000 + j).astype(np.float32)
    worlds.append((S, {f: thresholds(S[:, :len(P.pool)], Z[f"F_{f}"].astype(int)) for f in FS}))
Wt = np.array([120.0, 10.0, 1.0])
def grade(Ls):
    sc, t3, t15 = [], [], []
    for S, T in worlds:
        v = 0
        for f in FS:
            H = np.stack([np.stack([S[:, L].sum(1) >= T[f][:, i] for i in range(3)], 1) for L in Ls], 0)  # lineups x sims x places
            dw = np.array([1 / (1 + P.dup[f].get(tuple(sorted(L)), 0)) if max(L) < len(P.pool) else 1.0 for L in Ls])
            v += ((H * dw[:, None, None]).max(0).mean(0) * Wt).sum(); t3.append(H[:, :, 0].any(0).mean()); t15.append(H[:, :, 1].any(0).mean())
        sc.append(v / 3 * 1e3)
    return np.mean(sc), min(sc), np.mean(t3), np.mean(t15)
for f in files:
    D = pd.read_csv(f); Ls = [[ix[n] for n in d.Name] for _, d in D.groupby("Lineup")]
    m, w, t3, t15 = grade(Ls); uniq = len({tuple(sorted(L)) for L in Ls})
    print(f"{os.path.basename(f):24s} score {m:6.1f} (worst {w:5.1f}) · P(any top-3) {t3*1e4:5.2f}/10k · P(any top-15) {t15*1e3:5.2f}/1k · unique lineups {uniq}")
    for k, L in enumerate(Ls, 1):
        print(f"   L{k}: alone top-3 {np.mean([np.mean([(S[:, L].sum(1) >= T[f][:, 0]).mean() for f in FS]) for S, T in worlds])*1e4:5.2f}/10k · mean pts {np.mean([S[:, L].sum(1).mean() for S, T in worlds]):.1f}")
