"""v2 3-lineup portfolio search (Thanksgiving). Objective on sims A over 3 noisy-ownership fields:
P(any >= top-150) + 10*P(any >= top-15). Iterated local search (kicks), many starts, holdout on noisy-projection sims B.
Also tests Kendall's hunch (Gibbs + Walker [+ Emmett Johnson]) head-to-head.
  python3 tg_port2.py <folder> <thr.npz> <tag>"""
import sys, os, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../engine"))
from validate import validate, slots_ok
W, NPZ, TAG = sys.argv[1:4]; Z = np.load(NPZ); SC = ["f1", "f2", "f3"]; W15 = 10.0
pool, C = pd.read_pickle(os.path.join(W, "cands_run.pkl")); pool = pool.reset_index(drop=True)
sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); names = pool.Name.to_numpy(object)
ix = {n: i for i, n in enumerate(names)}; kick = pool.Kick.astype(str).to_numpy(object)
TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}; SA, SB = Z["SA"], Z["SB"]; TC = {s: Z[f"C_{s}"] for s in SC}; SCS = Z["SC"]
log = []; P = lambda *a: (print(*a, flush=True), log.append(" ".join(map(str, a))))

def hits(S, T, L):
    a = S[:, L].sum(1); return {s: (a >= T[s][:, 0], a >= T[s][:, 1]) for s in SC}
def obj(S, T, Ls):
    H = [hits(S, T, L) for L in Ls]
    return np.mean([np.logical_or.reduce([h[s][1] for h in H]).mean() + W15 * np.logical_or.reduce([h[s][0] for h in H]).mean() for s in SC])
def single(S, T, L):
    h = hits(S, T, L); return np.mean([h[s][0].mean() for s in SC]), np.mean([h[s][1].mean() for s in SC])
def ok(Ls):
    if validate([tuple(names[L]) for L in Ls], pool, max_shared=4): return False
    return not any(pos[i] == "DST" for a, b in itertools.combinations(Ls, 2) for i in set(a) & set(b))

def search(S, T, Ls, locks=None, iters=60):
    Ls = [list(L) for L in Ls]; locks = locks or [set() for _ in Ls]; cur = obj(S, T, Ls)
    for _ in range(iters):
        best = (cur + 1e-7, None)
        for k in range(len(Ls)):
            others = [Ls[j] for j in range(len(Ls)) if j != k]; Ho = [hits(S, T, L) for L in others]
            o15 = {s: np.logical_or.reduce([h[s][0] for h in Ho]) if Ho else np.zeros(len(S), bool) for s in SC}
            o150 = {s: np.logical_or.reduce([h[s][1] for h in Ho]) if Ho else np.zeros(len(S), bool) for s in SC}
            base = S[:, Ls[k]].sum(1)
            for i, old in enumerate(Ls[k]):
                if old in locks[k]: continue
                cand = np.where(sal <= 50000 - (sal[Ls[k]].sum() - sal[old]))[0]; cand = cand[~np.isin(cand, Ls[k])]
                cand = cand[pos[cand] == pos[old]] if pos[old] in ("QB", "DST") else cand[np.isin(pos[cand], ["RB", "WR", "TE"])]
                if not len(cand): continue
                new = base[:, None] - S[:, [old]] + S[:, cand]; v = np.zeros(len(cand))
                for s in SC:
                    t = T[s]; v += ((new >= t[:, [1]]) | o150[s][:, None]).mean(0) + W15 * ((new >= t[:, [0]]) | o15[s][:, None]).mean(0)
                v /= len(SC)
                for j in np.argsort(-v)[:15]:
                    if v[j] <= best[0]: break
                    tr = list(Ls[k]); tr[i] = cand[j]
                    if not slots_ok(list(pos[tr])): continue
                    trial = [tr if q == k else Ls[q] for q in range(len(Ls))]
                    if ok(trial): best = (v[j], (k, i, cand[j])); break
        if best[1] is None: break
        k, i, j = best[1]; Ls[k][i] = j; cur = best[0]
    return Ls, cur

def ils(S, T, Ls, locks=None, kicks=4, seed=0):
    """iterated local search: converge, then swap one lineup for a random good candidate (kick), re-converge."""
    rng = np.random.default_rng(seed); Ls, cur = search(S, T, Ls, locks)
    for _ in range(kicks):
        k = int(rng.integers(len(Ls)))
        if locks and locks[k]: pool_c = [c for c in C[:200] if locks[k] <= set(c)]
        else: pool_c = C[:200]
        if not pool_c: continue
        trial = [list(pool_c[int(rng.integers(len(pool_c)))]) if q == k else Ls[q] for q in range(len(Ls))]
        if not ok(trial): continue
        t2, v2 = search(S, T, trial, locks)
        if v2 > cur: Ls, cur = t2, v2
    return Ls, cur

C = [list(c) for c in C]
so = lambda L: (lambda p: p[1] + W15 * p[0])(single(SA, TA, L)); C.sort(key=so, reverse=True)
P(f"[{TAG}] {len(pool)} players, {len(C)} candidates")
P("top singles (A: top-15 per 1k / top-150 %):")
for c in C[:8]: p = single(SA, TA, c); P(f"  {p[0]*1e3:5.2f} {p[1]*100:5.2f}%  " + ", ".join(names[c]))

starts = []
for seed in range(10):
    rng = np.random.default_rng(seed); order = list(range(len(C))) if seed == 0 else list(rng.permutation(min(150, len(C)))) + list(range(len(C))); pick = []
    for j in order:
        if not pick or ok(pick + [C[j]]): pick.append(C[j])
        if len(pick) == 3: break
    if len(pick) == 3: starts.append(pick)
res = []
for n, st in enumerate(starts):
    Ls, v = ils(SA, TA, st, seed=n); vb = obj(SB, TB, Ls); res.append((vb, v, Ls))
    P(f"start {n}: A {obj(SA, TA, st)*1e3:.1f} -> {v*1e3:.1f} · holdout B {vb*1e3:.1f}")
res.sort(key=lambda r: -r[0]); vb, va, best = res[0]
for q in res[:5]: P(f"  top by B {q[0]*1e3:.1f} -> final C {obj(SCS, TC, q[2])*1e3:.1f}")

# ---- Kendall's hunch: best lineup containing Gibbs + Walker (+/- Emmett Johnson) ----
hunch = {}
for lk in [("Jahmyr Gibbs", "Kenneth Walker III"), ("Jahmyr Gibbs", "Kenneth Walker III", "Emmett Johnson"), ("Jahmyr Gibbs", "Emmett Johnson")]:
    if not set(lk) <= set(names): continue
    L0 = [c for c in C if {ix[n] for n in lk} <= set(c)]
    if not L0: continue
    Ls, _ = ils(SA, TA, [L0[0]], locks=[{ix[n] for n in lk}], kicks=3)
    hunch[lk] = Ls[0]; p = single(SCS, TC, Ls[0])
    P(f"\nHUNCH {' + '.join(lk)}: best single holdout top-15 {p[0]*1e3:.2f}/1k · top-150 {p[1]*100:.2f}% :: " + ", ".join(names[Ls[0]]))
    # forced into the portfolio: hunch lineup + best compatible pair from top candidates, then ILS
    pk = [Ls[0]]
    for c in [L for L in best] + C:
        if ok(pk + [c]): pk.append(c)
        if len(pk) == 3: break
    if len(pk) == 3:
        T3, v3 = ils(SA, TA, pk, locks=[{ix[n] for n in lk}, set(), set()], kicks=3)
        P(f"   portfolio WITH this lineup: final-set score {obj(SCS, TC, T3)*1e3:.1f} vs best {obj(SCS, TC, best)*1e3:.1f}")
        hunch[lk + ("PORT",)] = (T3, obj(SCS, TC, T3))
bs = [single(SCS, TC, L) for L in best]
P(f"\nBEST portfolio holdout B {vb*1e3:.1f} (A {va*1e3:.1f}) · FINAL set C {obj(SCS, TC, best)*1e3:.1f}")
H = [hits(SCS, TC, L) for L in best]
for s in SC:
    P(f"  {s}: P(any top-15) {np.logical_or.reduce([h[s][0] for h in H]).mean()*100:.2f}% · P(any top-150) {np.logical_or.reduce([h[s][1] for h in H]).mean()*100:.2f}%")
own = pd.read_csv(os.path.join(W, "own_est.csv")).set_index("Name").Own; rows = []
order = np.argsort([-(b[0] * W15 + b[1]) for b in bs])
for r, k in enumerate(order, 1):
    L = best[k]; p = bs[k]; d = pool.iloc[L].copy(); d["Own"] = d.Name.map(own); d["Lineup"] = r
    P(f"\nL{r} ${int(d.Salary.sum()):,} proj {d.Proj.sum():.1f} own {d.Own.sum():.0f}% · top-15 {p[0]*1e3:.2f}/1k · top-150 {p[1]*100:.2f}%")
    for q in d.sort_values("Salary", ascending=False).itertuples():
        P(f"   {q.Pos:3s} {q.Name:22s} {q.Team} ${q.Salary:,} {q.Proj:5.1f} own {q.Own:4.1f}% {q.Kick}")
    rows.append(d)
P("VALIDATOR:", validate([tuple(names[L]) for L in best], pool, max_shared=4) or "PASS")
pd.concat(rows).to_csv(os.path.join(W, f"lineups_{TAG}.csv"), index=False)
pd.to_pickle({"res": res, "hunch": hunch}, os.path.join(W, f"port_{TAG}.pkl")); open(os.path.join(W, f"port_{TAG}.txt"), "w").write("\n".join(log))
