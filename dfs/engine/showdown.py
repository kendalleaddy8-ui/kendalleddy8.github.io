"""Showdown mode (handbook §10): CPT (1.5x pts & salary) + 5 FLEX, $50k, both teams, no DST + opposing QB.
  python3 showdown.py <pool.csv> [--target 170] [--n 2] [--cands 400] [--score "CPT|F1|F2|F3|F4|F5"]
pool.csv: Name,Pos,Team,Opponent,Salary(FLEX),Proj[,Own,CptOwn]"""
import argparse, numpy as np, pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
from sim import simulate

def solve(P, obj, avoid=(), max_shared=4, lock_cpt=None, exclude=()):
    I = range(len(P)); m = LpProblem("sd", LpMaximize)
    x = [LpVariable(f"f{i}", cat="Binary") for i in I]; c = [LpVariable(f"c{i}", cat="Binary") for i in I]
    m += lpSum(obj[i] * x[i] + 1.5 * obj[i] * c[i] for i in I)
    m += lpSum(c) == 1; m += lpSum(x) == 5
    m += lpSum(P.Salary[i] * x[i] + 1.5 * P.Salary[i] * c[i] for i in I) <= 50000
    for i in I: m += x[i] + c[i] <= 1
    for t in set(P.Team): m += lpSum(x[i] + c[i] for i in I if P.Team[i] == t) >= 1
    for d in [i for i in I if P.Pos[i] == "DST"]:
        for q in [i for i in I if P.Pos[i] == "QB" and P.Team[i] == P.Opponent[d]]: m += x[d] + c[d] + x[q] + c[q] <= 1
    for (cp, fl) in avoid:                                     # different CPT and limited FLEX overlap
        m += lpSum(c[i] for i in I if i == cp) == 0
        m += lpSum(x[i] + c[i] for i in I if i in fl or i == cp) <= max_shared
    if lock_cpt is not None: m += c[lock_cpt] == 1
    for i in I:
        if P.Name[i] in exclude: m += x[i] + c[i] == 0
    if m.solve(PULP_CBC_CMD(msg=0)) != 1: return None
    return (next(i for i in I if c[i].value() > .5), tuple(i for i in I if x[i].value() > .5))

def score(S, lu): cp, fl = lu; return 1.5 * S[:, cp] + S[:, list(fl)].sum(1)
def sal(P, lu): cp, fl = lu; return int(1.5 * P.Salary[cp] + P.Salary[list(fl)].sum())

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("pool"); a.add_argument("--target", type=float, default=170)
    a.add_argument("--n", type=int, default=2); a.add_argument("--cands", type=int, default=400); a.add_argument("--score", default="")
    a = a.parse_args(); P = pd.read_csv(a.pool); S = simulate(P, 20000, seed=21)
    rng = np.random.default_rng(4); C = set()
    for k in rng.choice(len(S), a.cands, replace=False):
        lu = solve(P, 0.5 * S[k] + 0.5 * P.Proj.values)
        if lu: C.add(lu)
    for i in range(len(P)):                                    # every player as CPT at least once
        if P.Pos[i] != "DST":
            lu = solve(P, P.Proj.values * 1.0, lock_cpt=i)
            if lu: C.add(lu)
    C = sorted(C); hit = np.stack([score(S, lu) >= a.target for lu in C], 1)
    print(f"{len(C)} unique showdown lineups · target {a.target}")
    cpt = {}
    for j, lu in enumerate(C): cpt[P.Name[lu[0]]] = max(cpt.get(P.Name[lu[0]], 0), hit[:, j].mean())
    print("Best P(>=target) by CAPTAIN: " + " · ".join(f"{k} {v:.2%}" for k, v in sorted(cpt.items(), key=lambda z: -z[1])))
    chosen, cov = [], np.zeros(len(S), bool)
    for _ in range(a.n):
        best = max((j for j in range(len(C)) if all(C[j][0] != C[k][0] and len(({C[j][0], *C[j][1]}) & ({C[k][0], *C[k][1]})) <= 4 for k in chosen)),
                   key=lambda j: (cov | hit[:, j]).mean())
        chosen.append(best); cov |= hit[:, best]
    for r, j in enumerate(chosen, 1):
        cp, fl = C[j]; sc = score(S, C[j])
        print(f"\nLINEUP {r}: ${sal(P, C[j]):,} · median {np.median(sc):.1f} · p99 {np.percentile(sc, 99):.1f} · P>={a.target:.0f} {np.mean(sc >= a.target):.2%}")
        print(f"   CPT  {P.Name[cp]:20s} {P.Team[cp]} ${int(1.5*P.Salary[cp]):,}")
        for i in sorted(fl, key=lambda i: -P.Salary[i]): print(f"   FLEX {P.Name[i]:20s} {P.Team[i]} ${P.Salary[i]:,}")
    print(f"\nPortfolio P(>=1 hits) = {cov.mean():.2%}")
    if a.score:
        names = a.score.split("|"); idx = {n: i for i, n in enumerate(P.Name)}
        lu = (idx[names[0]], tuple(idx[n] for n in names[1:])); sc = score(S, lu)
        print(f"\nSCORED (yours): ${sal(P, lu):,} · median {np.median(sc):.1f} · p99 {np.percentile(sc, 99):.1f} · P>={a.target:.0f} {np.mean(sc >= a.target):.2%}")
