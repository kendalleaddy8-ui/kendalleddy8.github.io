"""Local search on the PAIR objective vs the simulated field; confirm on holdout sims."""
import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
pool = pd.read_pickle("cands_run.pkl")[0].reset_index(drop=True)
Z = np.load("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz")
SC = ["flat", "cal", "chalky"]; ix = {n: i for i, n in enumerate(pool.Name)}
sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); names = pool.Name.to_numpy(object)
BAN = {"Ladd McConkey", "Jalon Daniels", "Omar Cooper Jr."}
allowed = np.array([n not in BAN for n in names])
W15 = 10.0                                                    # top-15 weighted 10x vs top-150 (similar event counts)

def score_pair(S, T, L1, L2):
    a = S[:, L1].sum(1); b = S[:, L2].sum(1); v = 0
    for s in SC:
        t = T[s]; v += ((a >= t[:, 1]) | (b >= t[:, 1])).mean() + W15 * ((a >= t[:, 0]) | (b >= t[:, 0])).mean()
    return v / len(SC)

def single(S, T, L):
    a = S[:, L].sum(1); return {s: ((a >= T[s][:, 0]).mean(), (a >= T[s][:, 1]).mean()) for s in SC}

def ok_pair(L1, L2):
    n1, n2 = names[L1].tolist(), names[L2].tolist()
    if validate([tuple(n1), tuple(n2)], pool, max_shared=3): return False
    shared = set(L1) & set(L2)
    if any(sal[i] < 5000 or pos[i] == "DST" for i in shared): return False          # lesson 21
    return True

def search(S, T, L1, L2, max_iter=30):
    L = [list(L1), list(L2)]; cur = score_pair(S, T, *L)
    for it in range(max_iter):
        best = (cur + 1e-6, None)
        for k in (0, 1):
            other = L[1 - k]; o = S[:, other].sum(1)
            base = S[:, L[k]].sum(1)
            for i, old in enumerate(L[k]):
                cand = np.where(allowed & (sal <= 50000 - (sal[L[k]].sum() - sal[old])))[0]
                cand = cand[~np.isin(cand, L[k])]
                if pos[old] == "QB": cand = cand[pos[cand] == "QB"]
                elif pos[old] == "DST": cand = cand[pos[cand] == "DST"]
                else: cand = cand[np.isin(pos[cand], ["RB", "WR", "TE"])]
                if len(cand) == 0: continue
                new = base[:, None] - S[:, [old]] + S[:, cand]
                v = np.zeros(len(cand))
                for s in SC:
                    t = T[s]
                    v += ((new >= t[:, [1]]) | (o >= t[:, 1])[:, None]).mean(0) + W15 * ((new >= t[:, [0]]) | (o >= t[:, 0])[:, None]).mean(0)
                v /= len(SC)
                for j in np.argsort(-v)[:12]:
                    if v[j] <= best[0]: break
                    trial = list(L[k]); trial[i] = cand[j]
                    if not slots_ok(list(pos[trial])): continue
                    pair = [trial, other] if k == 0 else [other, trial]
                    if ok_pair(*pair): best = (v[j], (k, i, cand[j])); break
        if best[1] is None: break
        k, i, j = best[1]; L[k][i] = j; cur = best[0]
    return L, cur

T_A = {s: Z[f"A_{s}"] for s in SC}; T_B = {s: Z[f"B_{s}"] for s in SC}; SA, SB = Z["SA"], Z["SB"]
cur1 = ["Geno Smith","James Cook III","Javonte Williams","Omarion Hampton","CeeDee Lamb","Adonai Mitchell","Rome Odunze","Mason Taylor","Steelers"]
cur2 = ["Dak Prescott","Tony Pollard","Jonah Coleman","CeeDee Lamb","George Pickens","Elic Ayomanor","Cade Otton","Gunnar Helm","Chiefs"]
starts = [("current", cur1, cur2)]
C = [list(c) for c in pd.read_pickle("cands_run.pkl")[1] if not (set(names[list(c)]) & BAN)]
def single_obj(L):
    a = SA[:, L].sum(1); return np.mean([(a >= T_A[s][:, 1]).mean() + W15 * (a >= T_A[s][:, 0]).mean() for s in SC])
C.sort(key=single_obj, reverse=True)
print("top single candidates (set A):"); [print(f"  {single_obj(c)*1e3:.2f}", ", ".join(names[c])) for c in C[:8]]
tops = [list(names[c]) for c in C[:8]]
for a in range(len(tops)):
    for b in range(a + 1, len(tops)):
        if ok_pair([ix[n] for n in tops[a]], [ix[n] for n in tops[b]]): starts.append((f"fin{a}+{b}", tops[a], tops[b]))
starts = starts[:6]
res = []
for nm, a, b in starts:
    L, v = search(SA, T_A, [ix[n] for n in a], [ix[n] for n in b])
    res.append((nm, L, v, score_pair(SB, T_B, *L), score_pair(SB, T_B, [ix[n] for n in a], [ix[n] for n in b])))
    print(f"start {nm:10s} optimized A {v*1e3:.2f} · holdout B {res[-1][3]*1e3:.2f} (start on B {res[-1][4]*1e3:.2f})", flush=True)
best = max(res, key=lambda r: r[3])
print(f"\nBEST by holdout: {best[0]}  B-score {best[3]*1e3:.2f} vs current pair on B {score_pair(SB, T_B, [ix[n] for n in cur1], [ix[n] for n in cur2])*1e3:.2f}")
for k, L in enumerate(best[1], 1):
    d = pool.iloc[L]; sb = single(SB, T_B, L)
    p15 = np.mean([sb[s][0] for s in SC]); p150 = np.mean([sb[s][1] for s in SC])
    print(f"L{k} ${int(d.Salary.sum()):,} holdout p15 {p15*1e3:.2f}/1k p150 {p150*100:.2f}%: " + ", ".join(d.Name))
for k, L in enumerate([cur1, cur2], 1):
    sb = single(SB, T_B, [ix[n] for n in L]); print(f"current L{k} holdout p15 {np.mean([sb[s][0] for s in SC])*1e3:.2f}/1k p150 {np.mean([sb[s][1] for s in SC])*100:.2f}%")
pd.to_pickle(best, "improve_best.pkl")
