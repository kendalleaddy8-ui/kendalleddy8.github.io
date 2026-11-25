"""Engine v4 field prep (Thanksgiving 2026). For a week folder with cands_run.pkl + overrides.csv:
  - 3 sim sets: A (search), B and C (projection noise sigma .12, never searched on; C is the final report)
  - 3 synthetic Milly fields with OWNERSHIP NOISE (explicit Own x lognormal sigma .30)
  - per-sim score thresholds for places 3 / 15 / 150 (matmul, fast) and the fields themselves (for duplicate counts)
  python3 fieldprep.py <week_folder> <out.npz> [--sims 50000] [--field 150000]"""
import argparse, os, sys, time, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import simulate; from field_classic import sample_field; from pipeline import estimate_own
PLACES = (3, 15, 150)

def thresholds(S, F, places=PLACES, chunk=250):
    A = np.zeros((S.shape[1], len(F)), np.float32)
    for k in range(F.shape[1]): A[F[:, k], np.arange(len(F))] += 1
    out = np.zeros((len(S), len(places)), np.float32); kmax = max(places)
    for a in range(0, len(S), chunk):
        fs = S[a:a + chunk].astype(np.float32) @ A
        top = -np.partition(-fs, kmax - 1, axis=1)[:, :kmax]; top.sort(1); top = top[:, ::-1]
        out[a:a + len(fs)] = top[:, [p - 1 for p in places]]
    return out

def main():
    a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("out")
    a.add_argument("--sims", type=int, default=50000); a.add_argument("--field", type=int, default=150000)
    a.add_argument("--own-sigma", type=float, default=0.30); a.add_argument("--proj-sigma", type=float, default=0.12)
    a = a.parse_args(); t0 = time.time()
    pool = pd.read_pickle(os.path.join(a.week, "cands_run.pkl"))[0].reset_index(drop=True)
    ov = pd.read_csv(os.path.join(a.week, "overrides.csv")); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
    estimate_own(pool, ex)[["Name", "Pos", "Team", "Salary", "Proj", "Own"]].to_csv(os.path.join(a.week, "own_est.csv"), index=False)
    rng = np.random.default_rng(5); out = {"places": np.array(PLACES)}
    out["SA"] = simulate(pool, a.sims, seed=111).astype(np.float32)
    for k, sd in (("SB", 222), ("SC", 333)):
        Pn = pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, a.proj_sigma, len(Pn)))
        out[k] = simulate(Pn, a.sims, seed=sd).astype(np.float32)
    for k, seed in [("f1", 11), ("f2", 22), ("f3", 33)]:
        r = np.random.default_rng(seed); exn = {n: o * float(np.exp(r.normal(0, a.own_sigma))) for n, o in ex.items()}
        F = sample_field(estimate_own(pool, exn), a.field, seed=seed); out[f"F_{k}"] = F.astype(np.int16)
        for s in "ABC": out[f"{s}_{k}"] = thresholds(out["S" + s], F)
        print(k, f"{time.time()-t0:.0f}s median top-3/15/150:", np.median(out[f"A_{k}"], 0).round(1), flush=True)
    np.savez_compressed(a.out, **out); print("saved", a.out)

if __name__ == "__main__": main()
