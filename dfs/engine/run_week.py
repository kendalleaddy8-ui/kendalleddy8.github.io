"""One command per week (after fetch + lines.csv + overrides.csv exist):
  python3 run_week.py ../2026-wkNN [--n 3] [--target 240] [--cands 250]
Runs pipeline -> sim portfolio -> validator; writes lineups_run.csv + report.txt in the week folder."""
import argparse, os, sys, numpy as np, pandas as pd
from pipeline import build; from sim import simulate, candidates, pick; from validate import validate
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("--n", type=int, default=3)
a.add_argument("--target", type=float, default=240); a.add_argument("--cands", type=int, default=250)
a.add_argument("--qbs", default="", help="comma list of QB angles to force-explore (Kendall's hunches)")
a = a.parse_args(); W = a.week; J = lambda f: os.path.join(W, f)
ov = pd.read_csv(J("overrides.csv")) if os.path.exists(J("overrides.csv")) else pd.DataFrame()
pool = build(pd.read_csv(J("espn_pool.csv")), pd.read_csv(J("injuries.csv")), pd.read_csv(J("lines.csv")), ov)
pool.to_csv(J("pool_v3.csv"), index=False)
S = simulate(pool, 20000); C = candidates(pool, S, n=a.cands, seed=3)
angles = [q.strip() for q in a.qbs.split(",") if q.strip()]
for q in angles: C += candidates(pool, S, n=15, seed=hash(q) % 9999, qbs={q})
C = sorted(set(C)); chosen, sc, pu = pick(pool, S, C, n=a.n, target=a.target, max_shared=3)
out = []; rep = [f"{len(pool)} players · {len(C)} candidates · target {a.target} · P(>=1 hits) {pu:.2%}"]
for r, j in enumerate(chosen, 1):
    L = pool.iloc[list(C[j])].sort_values("Salary", ascending=False); s = sc[:, j]
    rep.append(f"\nLINEUP {r}: ${L.Salary.sum():,} · med {np.median(s):.1f} · p99 {np.percentile(s,99):.1f} · "
               f"P>={a.target:.0f} {np.mean(s>=a.target):.2%} · own~{L.Own.sum():.0f}%")
    rep += [f"   {p.Pos:3s} {p.Name:22s} {p.Team:3s} vs {p.Opponent:3s} ${p.Salary:,} proj {p.Proj:5.1f} {p.Kick} {p.Status}" for p in L.itertuples()]
    out.append(L.assign(Lineup=r))
best = {}
for c in C:
    q = pool.Name.iloc[[i for i in c if pool.Pos.iloc[i] == "QB"][0]]
    best[q] = max(best.get(q, 0), float(np.mean(S[:, list(c)].sum(1) >= a.target)))
rep.append("\nAngle table (best P>=target per QB): " + " · ".join(f"{q} {p:.2%}" for q, p in sorted(best.items(), key=lambda z: -z[1])[:12]))
errs = validate([tuple(L.Name) for L in out], pool, max_shared=3)
rep.append("VALIDATOR: " + ("PASS" if not errs else str(errs)))
q = pool[pool.Status.str.upper() == "QUESTIONABLE"].Name.tolist()
rep.append("Questionable in pool (have a pivot): " + ", ".join(q))
pd.concat(out).to_csv(J("lineups_run.csv"), index=False); open(J("report.txt"), "w").write("\n".join(rep)); print("\n".join(rep))
