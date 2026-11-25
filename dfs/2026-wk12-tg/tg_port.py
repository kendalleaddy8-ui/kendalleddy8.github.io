"""3-lineup portfolio vs simulated Thanksgiving Milly field. Objective on sims A:
mean over ownership scenarios of P(any lineup >= top-150) + 10 * P(any >= top-15). Confirm on holdout sims B."""
import sys, itertools, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
Z = np.load(sys.argv[1]); SC = ["flat", "cal", "chalky"]; W15 = 10.0
pool, C = pd.read_pickle("cands_run.pkl"); pool = pool.reset_index(drop=True)
sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); names = pool.Name.to_numpy(object)
TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}; SA, SB = Z["SA"], Z["SB"]

def hits(S, T, L):                           # per scenario: (hit15, hit150) boolean arrays
    a = S[:, L].sum(1); return {s: (a >= T[s][:, 0], a >= T[s][:, 1]) for s in SC}
def obj(S, T, Ls):
    H = [hits(S, T, L) for L in Ls]; v = 0
    for s in SC:
        h15 = np.logical_or.reduce([h[s][0] for h in H]); h150 = np.logical_or.reduce([h[s][1] for h in H])
        v += h150.mean() + W15 * h15.mean()
    return v / len(SC)
def single(S, T, L):
    h = hits(S, T, L); return np.mean([h[s][0].mean() for s in SC]), np.mean([h[s][1].mean() for s in SC])
def ok(Ls):
    if validate([tuple(names[L]) for L in Ls], pool, max_shared=4): return False
    for a, b in itertools.combinations(Ls, 2):
        if any(pos[i] == "DST" for i in set(a) & set(b)): return False
    return True

def search(S, T, Ls, iters=40):
    Ls = [list(L) for L in Ls]; cur = obj(S, T, Ls)
    for _ in range(iters):
        best = (cur + 1e-6, None)
        for k in range(len(Ls)):
            others = [Ls[j] for j in range(len(Ls)) if j != k]; Ho = [hits(S, T, L) for L in others]
            o15 = {s: np.logical_or.reduce([h[s][0] for h in Ho]) for s in SC}
            o150 = {s: np.logical_or.reduce([h[s][1] for h in Ho]) for s in SC}
            base = S[:, Ls[k]].sum(1)
            for i, old in enumerate(Ls[k]):
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

C = [list(c) for c in C]
so = lambda L: (lambda p: p[1] + W15 * p[0])(single(SA, TA, L))
C.sort(key=so, reverse=True)
print("top single candidates (set A, p15 per 1k / p150 %):")
for c in C[:10]:
    p = single(SA, TA, c); print(f"  {p[0]*1e3:5.2f} {p[1]*100:5.2f}%  " + ", ".join(names[c]))
# greedy starts from the top-25 singles, several orderings
starts = []
for seed in range(6):
    rng = np.random.default_rng(seed); order = list(range(25)) if seed == 0 else list(rng.permutation(40))
    pick = []
    for j in order:
        if ok(pick + [C[j]]) or len(pick) == 0: pick.append(C[j])
        if len(pick) == 3: break
    if len(pick) == 3: starts.append(pick)
res = []
for n, st in enumerate(starts):
    Ls, v = search(SA, TA, st); vb = obj(SB, TB, Ls)
    res.append((vb, v, Ls)); print(f"start {n}: start A {obj(SA, TA, st)*1e3:.1f} -> A {v*1e3:.1f} · holdout B {vb*1e3:.1f}", flush=True)
vb, va, best = max(res, key=lambda r: r[0])
print(f"\nBEST portfolio holdout B {vb*1e3:.1f} (A {va*1e3:.1f})")
H = [hits(SB, TB, L) for L in best]
for s in SC:
    print(f"  {s:7s}: P(any top-15) {np.logical_or.reduce([h[s][0] for h in H]).mean()*100:.2f}% · P(any top-150) {np.logical_or.reduce([h[s][1] for h in H]).mean()*100:.2f}%")
own = pd.read_csv("own_est.csv").set_index("Name").Own
rows = []
for k, L in enumerate(best, 1):
    p = single(SB, TB, L); d = pool.iloc[L].copy(); d["Own"] = d.Name.map(own); d["Lineup"] = k
    print(f"\nL{k} ${int(d.Salary.sum()):,} proj {d.Proj.sum():.1f} own {d.Own.sum():.0f}% · top-15 {p[0]*1e3:.2f}/1k · top-150 {p[1]*100:.2f}%")
    for r in d.sort_values("Salary", ascending=False).itertuples(): print(f"   {r.Pos:3s} {r.Name:22s} {r.Team} ${r.Salary:,} {r.Proj:5.1f} own {r.Own:4.1f}%")
    rows.append(d)
print("VALIDATOR:", validate([tuple(names[L]) for L in best], pool, max_shared=4) or "PASS")
pd.concat(rows).to_csv("lineups_final.csv", index=False); pd.to_pickle(res, "port_res.pkl")
