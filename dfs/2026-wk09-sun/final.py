import sys, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate, pick; from validate import validate
pool = pd.read_csv("pool_adj.csv"); S = simulate(pool, 20000)
R = pd.read_pickle("scenarios.pkl"); C = sorted(set(R.c))
chosen, scores, pu = pick(pool, S, C, n=3, target=240, max_shared=3)
kt = {"1:00":0,"4:05":1,"4:25":2}; need = {"RB":2,"WR":3,"TE":1}; order = {"QB":0,"RB":1,"WR":2,"TE":3,"FLEX":4,"DST":5}
def slot(L):
    L = L.copy(); L["Slot"] = L.Pos
    cand = [i for pos, n in need.items() if (L.Pos == pos).sum() > n for i in L.index[L.Pos == pos]]
    L.loc[max(cand, key=lambda i: (kt[L.Kick[i]], -L.Salary[i])), "Slot"] = "FLEX"
    return L.assign(o=L.Slot.map(order)).sort_values(["o","Salary"], ascending=[True, False])
def report(c, title):
    L = slot(pool.iloc[list(c)]); sc = S[:, list(c)].sum(1)
    print(f"\n{title}  ${L.Salary.sum():,} (${50000-L.Salary.sum()} left) · median {np.median(sc):.1f} · p99 {np.percentile(sc,99):.1f}"
          f" · P≥215 {np.mean(sc>=215):.2%} · P≥240 {np.mean(sc>=240):.2%} · own≈{L.Own.sum():.0f}%")
    for p in L.itertuples(): print(f"  {p.Slot:4s} {p.Name:22s} {p.Team:3s} vs {p.Opponent:3s} ${p.Salary:,}  proj {p.Proj:5.1f}  {p.Kick}")
lineups = [tuple(pool.Name.iloc[list(C[j])]) for j in chosen]
for r, j in enumerate(chosen, 1): report(C[j], f"LINEUP {r}")
print(f"\nPortfolio P(≥1 lineup ≥240) = {pu:.2%}")
errs = validate(lineups, pool, max_shared=3); print("VALIDATOR:", "PASS" if not errs else errs)
# Kendall's angles: best build for each requested QB (any config), shown as alternates
print("\n--- Requested angles (best P≥240 build per QB) ---")
for qb in ["Drew Lock", "Shedeur Sanders", "Joe Milton III"]:
    b = R[R.QB == qb].sort_values("p240", ascending=False).iloc[0]
    report(b.c, f"{qb} [{b.Cfg}]"); e = validate([tuple(pool.Name.iloc[list(b.c)])], pool); print("  validator:", "PASS" if not e else e)
