"""Precompute field thresholds: 3 ownership scenarios x (optimize set A, holdout set B)."""
import sys, time, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from field_classic import sample_field, field_thresholds; from pipeline import estimate_own
t0 = time.time(); pool = pd.read_pickle("cands_run.pkl")[0]
ov = pd.read_csv("overrides.csv"); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}; ex["Jalon Daniels"] = 0.0
SA = simulate(pool, 12000, seed=111); SB = simulate(pool, 12000, seed=222)
out = {"SA": SA.astype(np.float32), "SB": SB.astype(np.float32)}
for k, ts in [("flat", 0.7), ("cal", 1.0), ("chalky", 1.35)]:
    F = sample_field(estimate_own(pool, ex, temp_scale=ts), 150000, seed=int(ts * 100))
    out[f"A_{k}"] = field_thresholds(SA, F); out[f"B_{k}"] = field_thresholds(SB, F)
    print(k, f"{time.time()-t0:.0f}s", flush=True)
np.savez_compressed("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz", **out)
print("saved")
