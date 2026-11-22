"""Marginal value of a 3rd Milly lineup on top of the optimized pair (search on set A, measure on holdout B)."""
import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
pool = pd.read_pickle("cands_run.pkl")[0].reset_index(drop=True); C = pd.read_pickle("cands_run.pkl")[1]
Z = np.load("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz")
SC = ["flat", "cal", "chalky"]; names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object)
BAN = {"Jalon Daniels", "Omar Cooper Jr."}; W15 = 10.0
best = pd.read_pickle("improve_best.pkl"); P1, P2 = best[1]
def hits(S, T, L): a = S[:, L].sum(1); return {s: (a >= T[s][:, 0], a >= T[s][:, 1]) for s in SC}
def union_val(S, T, Ls):
    H = [hits(S, T, L) for L in Ls]; v = 0
    for s in SC:
        h15 = np.any([h[s][0] for h in H], 0); h150 = np.any([h[s][1] for h in H], 0); v += h150.mean() + W15 * h15.mean()
    return v / len(SC)
def per(S, T, Ls):
    H = [hits(S, T, L) for L in Ls]
    return np.mean([np.any([h[s][0] for h in H], 0).mean() for s in SC]), np.mean([np.any([h[s][1] for h in H], 0).mean() for s in SC])
def ok3(L3):
    trio = [P1, P2, L3]
    if validate([tuple(names[L]) for L in trio], pool, max_shared=3): return False
    for o in (P1, P2):
        if any(sal[i] < 5000 or pos[i] == "DST" for i in set(o) & set(L3)): return False
    return True
SA, SB = Z["SA"], Z["SB"]; TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}
cands = [list(c) for c in C if not (set(names[list(c)]) & BAN)]
cands.sort(key=lambda L: union_val(SA, TA, [P1, P2, L]), reverse=True)
pick = next(L for L in cands if ok3(L))
# local polish of the 3rd lineup (single swaps) on set A
cur = union_val(SA, TA, [P1, P2, pick]); improved = True
while improved:
    improved = False
    for i in range(9):
        for j in np.argsort(-sal):
            if names[j] in BAN or j in pick: continue
            t = list(pick); t[i] = j
            if sal[t].sum() > 50000 or not slots_ok(list(pos[t])) or not ok3(t): continue
            v = union_val(SA, TA, [P1, P2, t])
            if v > cur + 1e-6: pick, cur, improved = t, v, True
pair15, pair150 = per(SB, TB, [P1, P2]); tri15, tri150 = per(SB, TB, [P1, P2, pick]); s15, s150 = per(SB, TB, [pick])
print(f"HOLDOUT  pair: top-15 {pair15*1e3:.2f}/1k  top-150 {pair150*100:.2f}%")
print(f"HOLDOUT  pair+3rd: top-15 {tri15*1e3:.2f}/1k  top-150 {tri150*100:.2f}%   (gain {100*(tri150/pair150-1):+.0f}% on top-150)")
print(f"3rd alone: top-15 {s15*1e3:.2f}/1k  top-150 {s150*100:.2f}%  (random entry baseline: 0.01/1k, 0.10%)")
print(f"3rd lineup ${int(sal[pick].sum()):,}: " + ", ".join(names[pick]))
pd.to_pickle(pick, "third_best.pkl")
