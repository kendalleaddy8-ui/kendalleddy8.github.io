"""Thanksgiving field thresholds: 3 ownership scenarios x (optimize set A, holdout set B), 150k-entry Milly."""
import sys, time, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from field_classic import sample_field, field_thresholds; from pipeline import estimate_own
SCR = sys.argv[1]
t0 = time.time(); pool = pd.read_pickle("cands_run.pkl")[0]
ov = pd.read_csv("overrides.csv"); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
own = estimate_own(pool, ex)
print(own.sort_values("Own", ascending=False)[["Name", "Pos", "Salary", "Proj", "Own"]].head(30).to_string(index=False))
own[["Name", "Pos", "Team", "Salary", "Proj", "Own"]].to_csv("own_est.csv", index=False)
SA = simulate(pool, 20000, seed=111); SB = simulate(pool, 20000, seed=222)
out = {"SA": SA.astype(np.float32), "SB": SB.astype(np.float32)}
for k, ts in [("flat", 0.7), ("cal", 1.0), ("chalky", 1.35)]:
    F = sample_field(estimate_own(pool, ex, temp_scale=ts), 150000, seed=int(ts * 100))
    out[f"A_{k}"] = field_thresholds(SA, F); out[f"B_{k}"] = field_thresholds(SB, F)
    print(k, f"{time.time()-t0:.0f}s", "median top-15 / top-150:", np.median(out[f"A_{k}"], 0).round(1), flush=True)
np.savez_compressed(SCR, **out); print("saved")
