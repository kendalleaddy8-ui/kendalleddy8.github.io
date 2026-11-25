"""v2 field thresholds (Thanksgiving). Upgrades vs tg_prep.py:
 - 3 field samples with OWNERSHIP NOISE (explicit owns x lognormal sigma .30, renormalised by the sampler) — my owns are guesses
 - holdout sims B use PROJECTION NOISE (each player's mean x lognormal sigma .12) — my projections are guesses too
 - matmul thresholds (fast).
  python3 tg_prep2.py <folder> <out.npz>"""
import sys, os, time, numpy as np, pandas as pd; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../engine"))
from sim import simulate; from field_classic import sample_field; from pipeline import estimate_own
W, OUT = sys.argv[1], sys.argv[2]; t0 = time.time()
pool = pd.read_pickle(os.path.join(W, "cands_run.pkl"))[0].reset_index(drop=True)
ov = pd.read_csv(os.path.join(W, "overrides.csv")); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
estimate_own(pool, ex)[["Name", "Pos", "Team", "Salary", "Proj", "Own"]].to_csv(os.path.join(W, "own_est.csv"), index=False)

def thresholds(S, F, places=(15, 150), chunk=250):
    A = np.zeros((S.shape[1], len(F)), np.float32)
    for k in range(F.shape[1]): A[F[:, k], np.arange(len(F))] += 1
    out = np.zeros((len(S), len(places)), np.float32); kmax = max(places)
    for a in range(0, len(S), chunk):
        fs = S[a:a + chunk].astype(np.float32) @ A
        top = -np.partition(-fs, kmax - 1, axis=1)[:, :kmax]; top.sort(1); top = top[:, ::-1]
        out[a:a + len(fs)] = top[:, [p - 1 for p in places]]
    return out

NS = 50000
SA = simulate(pool, NS, seed=111).astype(np.float32)
rng = np.random.default_rng(5); Pn = pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn)))
SB = simulate(Pn, NS, seed=222).astype(np.float32)
Pc = pool.copy(); Pc["Proj"] = Pc.Proj * np.exp(rng.normal(0, 0.12, len(Pc)))      # final-report set, never searched on
SC_ = simulate(Pc, NS, seed=333).astype(np.float32)
out = {"SA": SA, "SB": SB, "SC": SC_}
for k, seed in [("f1", 11), ("f2", 22), ("f3", 33)]:
    r = np.random.default_rng(seed); exn = {n: o * float(np.exp(r.normal(0, 0.30))) for n, o in ex.items()}
    F = sample_field(estimate_own(pool, exn), 150000, seed=seed)
    out[f"A_{k}"] = thresholds(SA, F); out[f"B_{k}"] = thresholds(SB, F); out[f"C_{k}"] = thresholds(SC_, F)
    print(k, f"{time.time()-t0:.0f}s", "median top-15/150:", np.median(out[f"A_{k}"], 0).round(1), flush=True)
np.savez_compressed(OUT, **out); print("saved", OUT)
