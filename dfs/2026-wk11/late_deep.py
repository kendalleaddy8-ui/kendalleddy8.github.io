"""4pm-only slate, full method: pool (all layers + Sunday news) -> 3 ownership-scenario fields (30k entries)
-> thresholds on two independent sim sets -> deep local search (single entry) -> holdout confirmation."""
import sys, random, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from field_classic import sample_field, field_thresholds; from pipeline import estimate_own; from validate import validate, slots_ok
pool, C = pd.read_pickle("cands_late.pkl"); pool = pool.reset_index(drop=True)
names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object)
BAN = {"Omar Cooper Jr."}; allowed = np.array([n not in BAN for n in names]); random.seed(5)
ov = pd.read_csv("overrides.csv"); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o) and n in set(names)}
N = 30000; PL = (1, 3, 30)                                  # 30 = top 0.1%
SA = simulate(pool, 15000, seed=31).astype(np.float32); SB = simulate(pool, 15000, seed=32).astype(np.float32)
SC = {"flat": 0.8, "cal": 1.0, "chalky": 1.3}; TA, TB = {}, {}
for k, ts in SC.items():
    F = sample_field(estimate_own(pool, ex, temp_scale=ts), N, seed=int(ts * 10) + 1, min_sal=47500)
    TA[k] = field_thresholds(SA, F, places=PL); TB[k] = field_thresholds(SB, F, places=PL); print("field", k, flush=True)
W3 = 10.0
def obj(S, T, L): a = S[:, L].sum(1); return np.mean([(a >= T[s][:, 2]).mean() + W3 * (a >= T[s][:, 1]).mean() for s in SC])
def metr(S, T, L):
    a = S[:, L].sum(1)
    return (np.mean([(a > T[s][:, 0]).mean() for s in SC]) * 1e4, np.mean([(a >= T[s][:, 1]).mean() for s in SC]) * 1e3,
            np.mean([(a >= T[s][:, 2]).mean() for s in SC]) * 100, np.median(a), np.percentile(a, 99))
def climb(L):
    L = list(L); cur = obj(SA, TA, L)
    while True:
        best = (cur + 1e-6, None); base = SA[:, L].sum(1)
        for i, old in enumerate(L):
            cand = np.where(allowed & (sal <= 50000 - (sal[L].sum() - sal[old])))[0]; cand = cand[~np.isin(cand, L)]
            cand = cand[pos[cand] == pos[old]] if pos[old] in ("QB", "DST") else cand[np.isin(pos[cand], ["RB", "WR", "TE"])]
            if not len(cand): continue
            new = base[:, None] - SA[:, [old]] + SA[:, cand]
            v = np.mean([(new >= TA[s][:, [2]]).mean(0) + W3 * (new >= TA[s][:, [1]]).mean(0) for s in SC], 0)
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
            p = pos[t[i]]; cs = np.where(allowed & ((pos == p) if p in ("QB", "DST") else np.isin(pos, ["RB", "WR", "TE"])))[0]; t[i] = int(random.choice(cs))
        if len(set(t)) == 9 and sal[t].sum() <= 50000 and slots_ok(list(pos[t])) and not validate([tuple(names[t])], pool): return t
    return L
C = [list(c) for c in C if not (set(names[list(c)]) & BAN)]; C.sort(key=lambda L: obj(SA, TA, L), reverse=True)
starts = C[:30] + [kick(C[0]) for _ in range(25)] + [kick(C[1]) for _ in range(15)]
seen, res = set(), []
for s in starts:
    L = climb(s); k = tuple(sorted(L))
    if k not in seen: seen.add(k); res.append(L)
scored = sorted(((metr(SB, TB, L), L) for L in res), key=lambda r: -(r[0][1] + r[0][2]))
print(f"{len(res)} local optima. HOLDOUT: P(1st)/10k · top-3/1k · top-0.1% · median · p99")
for m, L in scored[:5]:
    print(f"{m[0]:5.1f} {m[1]:5.2f} {m[2]:5.2f}% {m[3]:6.1f} {m[4]:6.1f} ${int(sal[L].sum()):,} own~{pool.Own.values[L].sum():.0f}%: " + ", ".join(names[L]))
pd.to_pickle(scored[:5], "late_deep_top.pkl")
