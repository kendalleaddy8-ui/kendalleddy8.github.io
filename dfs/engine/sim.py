"""
DFS GPP engine v2 — correlated Monte Carlo + sim-optimal candidates + portfolio selection.
Usage:  python3 engine/sim.py <pool.csv> [--n 3] [--target 230] [--sims 20000] [--cands 150]
pool.csv columns: Name,Pos,Team,Opponent,Salary,Proj[,Own,Kick,Status]
  Proj = adjusted MEDIAN projection (after playbook multipliers). Own = projected ownership % (optional).
Requires pulp==2.8.0, numpy, pandas.
"""
import argparse, numpy as np, pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# ---------- 1. outcome model ----------
CV = {"QB": 0.40, "RB": 0.55, "WR": 0.65, "TE": 0.70, "DST": 0.85}   # sd/mean, DK scoring
# share of each player's variance coming from: game environment, team pass/rush script, own noise
W = {"QB": (0.30, 0.55), "WR": (0.20, 0.45), "TE": (0.20, 0.40), "RB": (0.20, 0.35), "DST": (0.25, 0.0)}

def simulate(pool, sims=20000, seed=7):
    rng = np.random.default_rng(seed)
    teams = sorted(set(pool.Team)); games = sorted({tuple(sorted(p)) for p in zip(pool.Team, pool.Opponent)})
    G = {g: rng.standard_normal(sims) for g in games}                 # shootout vs. slog
    TP = {t: rng.standard_normal(sims) for t in teams}                # team passing success
    TR = {t: 0.35 * TP[t] + np.sqrt(1 - .35**2) * rng.standard_normal(sims) for t in teams}  # rushing (some shared TD equity)
    out = np.empty((sims, len(pool)))
    for j, r in enumerate(pool.itertuples()):
        g = G[tuple(sorted((r.Team, r.Opponent)))]; wg, wt = W[r.Pos]
        if r.Pos == "DST":   # DST: hurt by shootouts and by the opponent's offense playing well
            z = -wg * g - 0.45 * (TP[r.Opponent] + TR[r.Opponent]) / np.sqrt(2 + 2 * .35)
            wt = 0.45
        else:
            team = TR[r.Team] if r.Pos == "RB" else TP[r.Team]
            z = wg * g + wt * team
        z = z + np.sqrt(max(1 - wg**2 - wt**2, 0.05)) * rng.standard_normal(sims)
        z = z / z.std()
        s = np.sqrt(np.log(1 + CV[r.Pos] ** 2))                       # lognormal with MEAN = Proj
        out[:, j] = r.Proj * np.exp(s * z - s * s / 2)
        if r.Pos == "DST": out[:, j] -= 2.0                            # DSTs can go negative
    return out

# ---------- 2. lineup optimizer with an arbitrary objective ----------
def solve(pool, obj, avoid=(), maxov=9, min_stack=1, own_cap=None, lock=(), exclude=()):
    I = range(len(pool)); P = pool.reset_index(drop=True)
    m = LpProblem("d", LpMaximize); x = [LpVariable(f"x{i}", cat="Binary") for i in I]
    m += lpSum(obj[i] * x[i] for i in I)
    m += lpSum(P.Salary[i] * x[i] for i in I) <= 50000; m += lpSum(x) == 9
    cnt = lambda q: lpSum(x[i] for i in I if P.Pos[i] == q)
    m += cnt("QB") == 1; m += cnt("DST") == 1
    m += cnt("RB") >= 2; m += cnt("RB") <= 3; m += cnt("WR") >= 3; m += cnt("WR") <= 4
    m += cnt("TE") >= 1; m += cnt("TE") <= 2
    for q in [i for i in I if P.Pos[i] == "QB"]:                       # QB + own pass catchers
        pcs = [i for i in I if P.Team[i] == P.Team[q] and P.Pos[i] in ("WR", "TE")]
        m += lpSum(x[i] for i in pcs) >= min(min_stack, len(pcs)) * x[q]
    for d in [i for i in I if P.Pos[i] == "DST"]:                    # no offense vs own DST
        for i in I:
            if P.Team[i] == P.Opponent[d] and P.Pos[i] != "DST": m += x[i] + x[d] <= 1
    for t in set(P.Team): m += lpSum(x[i] for i in I if P.Team[i] == t) <= 3
    for prev in avoid: m += lpSum(x[i] for i in I if P.Name[i] in prev) <= maxov
    if own_cap is not None and "Own" in P: m += lpSum(P.Own[i] * x[i] for i in I) <= own_cap
    for i in I:
        if P.Name[i] in lock: m += x[i] == 1
        if P.Name[i] in exclude: m += x[i] == 0
    if m.solve(PULP_CBC_CMD(msg=0)) != 1: return None
    return tuple(i for i in I if x[i].value() > 0.5)

# ---------- 3. candidates = lineups that are optimal in some simulated world ----------
def candidates(pool, S, n=150, seed=11, **kw):
    rng = np.random.default_rng(seed); seen = set()
    for k in rng.choice(len(S), size=n, replace=False):
        obj = 0.5 * S[k] + 0.5 * pool.Proj.values                      # shrink toward median: fewer junk builds
        lu = solve(pool, obj, min_stack=2, **kw)
        if lu: seen.add(lu)
    return sorted(seen)

# ---------- 4. portfolio pick: maximize P(at least one lineup >= target) ----------
def pick(pool, S, cands, n=3, target=230.0, max_shared=4, max_exp=None):
    max_exp = max_exp or max(n - 1, 1)                                 # nobody in every lineup (n>=3)
    scores = np.stack([S[:, list(c)].sum(1) for c in cands], 1)        # sims x candidates
    hit = scores >= target
    chosen, covered = [], np.zeros(len(S), bool)
    for _ in range(n):
        best, bv = None, -1
        for j, c in enumerate(cands):
            if j in chosen or any(len(set(c) & set(cands[k])) > max_shared for k in chosen): continue
            used = [i for k in chosen for i in cands[k]]
            if n >= 3 and any(used.count(i) >= max_exp for i in c): continue
            v = (covered | hit[:, j]).mean()
            if v > bv: best, bv = j, v
        chosen.append(best); covered |= hit[:, best]
    return chosen, scores, covered.mean()

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("pool"); a.add_argument("--n", type=int, default=3)
    a.add_argument("--target", type=float, default=215)   # ~top-0.5% score; Milly win ~240+
    a.add_argument("--sims", type=int, default=20000)
    a.add_argument("--cands", type=int, default=150); a.add_argument("--shared", type=int, default=4)
    a = a.parse_args()
    pool = pd.read_csv(a.pool)
    if "Status" in pool: pool = pool[~pool.Status.fillna("").str.upper().isin(["OUT", "D", "DOUBTFUL"])]
    pool = pool.reset_index(drop=True)
    S = simulate(pool, a.sims)
    C = candidates(pool, S, a.cands)
    chosen, scores, pu = pick(pool, S, C, a.n, a.target, a.shared)
    print(f"{len(C)} unique candidates · target {a.target} · P(>=1 lineup hits) = {pu:.1%}\n")
    for r, j in enumerate(chosen, 1):
        lu = pool.iloc[list(C[j])]; sc = scores[:, j]
        print(f"Lineup {r}: ${lu.Salary.sum():,}  median {np.median(sc):.1f}  p90 {np.percentile(sc,90):.1f}  "
              f"p99 {np.percentile(sc,99):.1f}  P(>={a.target:.0f}) {np.mean(sc>=a.target):.2%}")
        for p in lu.sort_values("Salary", ascending=False).itertuples():
            print(f"   {p.Pos:3s} {p.Name:22s} {p.Team:3s} ${p.Salary:,}  {p.Proj:.1f}")
