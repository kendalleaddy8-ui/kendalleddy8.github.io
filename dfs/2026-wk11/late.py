"""4pm-only slate: best lineup vs a simulated late-slate field (N entries); report top-0.1% rate comparable to Milly."""
import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from field_classic import sample_field, rank_vs_field; from pipeline import estimate_own; from validate import validate
pool, C = pd.read_pickle("cands_late.pkl"); pool = pool.reset_index(drop=True)
ov = pd.read_csv("overrides.csv"); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o) and n in set(pool.Name)}
N = 30000; places = (1, 3, 30)                                # 30 = top 0.1% of a 30k field
S = simulate(pool, 12000, seed=404); res = []
for ts in (0.8, 1.0, 1.3):
    F = sample_field(estimate_own(pool, ex, temp_scale=ts), N, seed=int(ts * 10), min_sal=47500)
    res.append(rank_vs_field(S, F, list(C), places=places))
p = {k: np.mean([r[k] for r in res], 0) for k in places}
order = np.argsort(-(p[30] + 10 * p[3]))
for j in order[:3]:
    L = pool.iloc[list(C[j])]
    print(f"P(1st) {p[1][j]*1e4:.1f}/10k · top-3 {p[3][j]*1e3:.2f}/1k · top-0.1% {p[30][j]*100:.2f}% · ${int(L.Salary.sum()):,} · "
          f"{validate([tuple(L.Name)], pool) or 'PASS'}: " + ", ".join(L.sort_values('Salary', ascending=False).Name))
pd.to_pickle(C[order[0]], "late_best.pkl")
