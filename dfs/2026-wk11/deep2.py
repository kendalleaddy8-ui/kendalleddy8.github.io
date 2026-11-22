"""Sunday AM deep search (single entry): 24k+24k sims, all layers + Sunday news; select on A, confirm on holdout B."""
import sys, random, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
pool, C = pd.read_pickle("cands_run.pkl"); pool = pool.reset_index(drop=True)
Z = np.load("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz")
SC = ["flat", "cal", "chalky"]; SA, SB = Z["SA"], Z["SB"]; TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}
names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); ix = {n: i for i, n in enumerate(names)}
BAN = {"Jalon Daniels", "Omar Cooper Jr."}; allowed = np.array([n not in BAN for n in names]); W15 = 10.0; random.seed(11)
def obj(S, T, L): a = S[:, L].sum(1); return np.mean([(a >= T[s][:, 1]).mean() + W15 * (a >= T[s][:, 0]).mean() for s in SC])
def metr(S, T, L):
    a = S[:, L].sum(1); return np.mean([(a >= T[s][:, 0]).mean() for s in SC]) * 1e3, np.mean([(a >= T[s][:, 1]).mean() for s in SC]) * 100, np.median(a), np.percentile(a, 99)
def climb(L):
    L = list(L); cur = obj(SA, TA, L)
    while True:
        best = (cur + 1e-6, None); base = SA[:, L].sum(1)
        for i, old in enumerate(L):
            cand = np.where(allowed & (sal <= 50000 - (sal[L].sum() - sal[old])))[0]; cand = cand[~np.isin(cand, L)]
            cand = cand[pos[cand] == pos[old]] if pos[old] in ("QB", "DST") else cand[np.isin(pos[cand], ["RB", "WR", "TE"])]
            if not len(cand): continue
            new = base[:, None] - SA[:, [old]] + SA[:, cand]
            v = np.mean([(new >= TA[s][:, [1]]).mean(0) + W15 * (new >= TA[s][:, [0]]).mean(0) for s in SC], 0)
            for j in np.argsort(-v)[:15]:
                if v[j] <= best[0]: break
                t = list(L); t[i] = cand[j]
                if slots_ok(list(pos[t])) and not validate([tuple(names[t])], pool): best = (v[j], (i, cand[j])); break
        if best[1] is None: return L
        L[best[1][0]] = best[1][1]; cur = best[0]
def kick(L):
    for _ in range(60):
        t = list(L)
        for i in random.sample(range(9), 2):
            p = pos[t[i]]; cands = np.where(allowed & ((pos == p) if p in ("QB", "DST") else np.isin(pos, ["RB", "WR", "TE"])))[0]
            t[i] = int(random.choice(cands))
        if len(set(t)) == 9 and sal[t].sum() <= 50000 and slots_ok(list(pos[t])) and not validate([tuple(names[t])], pool): return t
    return L
named = {"My pick": ["Dak Prescott","Tony Pollard","Cam Skattebo","Ashton Jeanty","CeeDee Lamb","George Pickens","Jalen Nailor","Darren Waller","Steelers"],
         "Kendall Dak": ["Dak Prescott","Emmett Johnson","Tony Pollard","Josh Downs","CeeDee Lamb","George Pickens","Colston Loveland","Dawson Knox","Giants"],
         "Kendall Mahomes A": ["Patrick Mahomes","James Cook III","Jahmyr Gibbs","Josh Downs","Ja'Kobi Lane","Carnell Tate","Darren Waller","Emmett Johnson","Giants"],
         "Kendall Mahomes B": ["Patrick Mahomes","James Cook III","Jahmyr Gibbs","Josh Downs","Makai Lemon","Rome Odunze","Evan Engram","Emmett Johnson","Giants"]}
NI = {k: [ix[n] for n in v] for k, v in named.items() if all(n in ix for n in v)}
print("missing from pool:", {k: [n for n in v if n not in ix] for k, v in named.items() if k not in NI})
C = [list(c) for c in C if not (set(names[list(c)]) & BAN)]; C.sort(key=lambda L: obj(SA, TA, L), reverse=True)
starts = C[:40] + list(NI.values())
starts += [kick(NI["My pick"]) for _ in range(30)] + [kick(C[0]) for _ in range(20)]
seen, res = set(), []
for s in starts:
    L = climb(s); key = tuple(sorted(L))
    if key not in seen: seen.add(key); res.append(L)
scored = sorted(((metr(SB, TB, L), L) for L in res), key=lambda r: -(r[0][0] + r[0][1]))
print(f"{len(res)} distinct local optima from {len(starts)} starts. HOLDOUT top-15/1k · top-150% · median · p99")
for m, L in scored[:6]: print(f"{m[0]:5.2f} {m[1]:5.2f}% {m[2]:6.1f} {m[3]:6.1f} ${int(sal[L].sum()):,}: " + ", ".join(names[L]))
print("\nNamed lineups (holdout):")
for k, L in NI.items(): m = metr(SB, TB, L); print(f"{m[0]:5.2f} {m[1]:5.2f}% {m[2]:6.1f} {m[3]:6.1f}  {k}")
pd.to_pickle(scored[:6], "deep2_top.pkl")
