"""Cash odds for the final lineups (Kendall: 'if I don't win the million, will I win something?').
Per sim: the field's cash-line score (rank = cash_frac x field size) in each saved field; report P(each lineup cashes),
P(at least one cashes), expected cashing lineups. Graded on the final set C (projection noise, never searched on).
  python3 cashline.py <week> <thr.npz> <lineups_tag.csv> [--cash-frac 0.22]"""
import argparse, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FS = ["f1", "f2", "f3"]

def cash_odds(Z, Ls, cash_frac=0.22, sims=20000):
    """Z: loaded thr.npz; Ls: list of index lists. Returns dict(per=[...], any=float, expected=float, line=float)."""
    S = Z["SC"][:sims]; res = np.zeros((len(FS), len(Ls) + 1)); lines = []
    for fi, f in enumerate(FS):
        F = Z[f"F_{f}"].astype(int); A = np.zeros((S.shape[1], len(F)), np.float32)
        for k in range(F.shape[1]): A[F[:, k], np.arange(len(F))] += 1
        rank = int(cash_frac * len(F)); thr = np.zeros(len(S), np.float32)
        for c in range(0, len(S), 250):
            fs = S[c:c + 250] @ A; thr[c:c + 250] = -np.partition(-fs, rank - 1, axis=1)[:, rank - 1]
        ours = np.stack([S[:, l].sum(1) for l in Ls], 1); hit = ours >= thr[:, None]
        res[fi, :len(Ls)] = hit.mean(0); res[fi, -1] = hit.any(1).mean(); lines.append(float(np.median(thr)))
    m = res.mean(0)
    return {"per": [float(x) for x in m[:-1]], "any": float(m[-1]), "expected": float(m[:-1].sum()), "line": float(np.mean(lines))}

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("lineups")
    a.add_argument("--cash-frac", type=float, default=0.22); a.add_argument("--sims", type=int, default=20000); a = a.parse_args()
    Z = np.load(a.npz); pool = pd.read_pickle(os.path.join(a.week, "cands_run.pkl"))[0].reset_index(drop=True)
    ix = {n: i for i, n in enumerate(pool.Name)}; L = pd.read_csv(os.path.join(a.week, a.lineups))
    Ls = [[ix[n] for n in d.Name] for _, d in L.groupby("Lineup")]
    r = cash_odds(Z, Ls, a.cash_frac, a.sims)
    print(f"cash line (top {a.cash_frac:.0%}): median score {r['line']:.1f}")
    for k, p in enumerate(r["per"]): print(f"  L{k+1}: P(cash) {p*100:.1f}%")
    print(f"  P(at least one of {len(Ls)} cashes) {r['any']*100:.1f}% · expected cashing lineups {r['expected']:.2f}")
