"""Cash odds for the final lineups (Kendall: 'if I don't win the million, will I win something?').
Per sim: the field's cash-line score (rank = cash_frac x field size) in each saved field; report P(each lineup cashes),
P(at least one cashes), expected cashing lineups. Graded on the final set C (projection noise, never searched on).
  python3 cashline.py <week> <thr.npz> <lineups_tag.csv> [--cash-frac 0.22]"""
import argparse, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import FS
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("lineups")
a.add_argument("--cash-frac", type=float, default=0.22); a.add_argument("--sims", type=int, default=20000); a = a.parse_args()
Z = np.load(a.npz); pool = pd.read_pickle(os.path.join(a.week, "cands_run.pkl"))[0].reset_index(drop=True)
ix = {n: i for i, n in enumerate(pool.Name)}; L = pd.read_csv(os.path.join(a.week, a.lineups))
Ls = [[ix[n] for n in d.Name] for _, d in L.groupby("Lineup")]
S = Z["SC"][:a.sims]; cash = {}; res = np.zeros((len(FS), len(Ls) + 1))
for fi, f in enumerate(FS):
    F = Z[f"F_{f}"].astype(int); A = np.zeros((S.shape[1], len(F)), np.float32)
    for k in range(F.shape[1]): A[F[:, k], np.arange(len(F))] += 1
    rank = int(a.cash_frac * len(F)); thr = np.zeros(len(S), np.float32)
    for c in range(0, len(S), 250):
        fs = S[c:c + 250] @ A; thr[c:c + 250] = -np.partition(-fs, rank - 1, axis=1)[:, rank - 1]
    ours = np.stack([S[:, l].sum(1) for l in Ls], 1); hit = ours >= thr[:, None]
    res[fi, :len(Ls)] = hit.mean(0); res[fi, -1] = hit.any(1).mean(); cash[f] = float(np.median(thr))
m = res.mean(0)
print(f"cash line (top {a.cash_frac:.0%}): median score {np.mean(list(cash.values())):.1f}")
for k in range(len(Ls)): print(f"  L{k+1}: P(cash) {m[k]*100:.1f}%")
print(f"  P(at least one of {len(Ls)} cashes) {m[-1]*100:.1f}% · expected cashing lineups {m[:-1].sum():.2f}")
