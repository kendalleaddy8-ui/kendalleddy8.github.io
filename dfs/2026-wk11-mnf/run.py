import sys, time, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from showdown import solve, sal, score; from field import sample_field, win_prob
t0 = time.time(); P = pd.read_csv("pool.csv"); FO = set(P.Name[P.FieldOnly == 1]); NF = 70000
U, cnt, F = sample_field(P, NF, seed=5); print(f"field {NF:,} entries, {len(U):,} unique, max dupes {cnt.max()} ({time.time()-t0:.0f}s)", flush=True)
SC = {"props": {}, "cin_shootout": {"Joe Burrow": 29, "Ja'Marr Chase": 28, "Tee Higgins": 20, "Jayden Daniels": 24, "Stefon Diggs": 14},
      "cin_blowout": {"Chase Brown": 23, "Samaje Perine": 8.5, "Joe Burrow": 26, "Jayden Daniels": 17, "Stefon Diggs": 9, "Jacory Croskey-Merritt": 8},
      "was_keeps_close": {"Jayden Daniels": 24, "Jacory Croskey-Merritt": 14, "Stefon Diggs": 14, "Ja'Marr Chase": 21, "Joe Burrow": 22}}
W = {"props": 0.4, "cin_shootout": 0.2, "cin_blowout": 0.2, "was_keeps_close": 0.2}
ix = {n: i for i, n in enumerate(P.Name)}; sims, C = {}, set()
for k, ch in SC.items():
    Q = P.copy(); Q["Proj"] = [ch.get(n, p) for n, p in zip(Q.Name, Q.Proj)]; S = simulate(Q, 8000, seed=len(k) * 13); sims[k] = S
    rng = np.random.default_rng(len(k))
    for j in rng.choice(len(S), 250, replace=False):
        lu = solve(Q, 0.6 * S[j] + 0.4 * Q.Proj.values, exclude=FO)
        if lu: C.add(lu)
    for i in range(len(Q)):
        if Q.Name[i] in FO or Q.Pos[i] == "DST": continue
        lu = solve(Q, Q.Proj.values, lock_cpt=i, exclude=FO)
        if lu: C.add(lu)
K = (ix["Ja'Marr Chase"], tuple(sorted(ix[n] for n in ["Joe Burrow","Jayden Daniels","J. Endries","Tee Higgins","D. Neal"])))
C = sorted(C | {K}); print(f"{len(C)} candidates ({time.time()-t0:.0f}s)", flush=True)
R = {k: win_prob(S, U, cnt, C) for k, S in sims.items()}
p1 = sum(W[k] * R[k][0] for k in SC); p01 = sum(W[k] * R[k][1] for k in SC)
rows = [dict(j=j, cpt=P.Name[c], flex=", ".join(P.Name[list(f)]), sal=sal(P, (c, f)), dup=int(R["props"][2][j]), p1=p1[j] * 1e4, ptop=p01[j] * 100) for j, (c, f) in enumerate(C)]
D = pd.DataFrame(rows).sort_values(["p1", "ptop"], ascending=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
print("p1 = wins per 10k · ptop = top-0.1% %"); print(D.head(10).drop(columns="j").round(2).to_string(index=False))
print("\nKendall's draft:"); print(D[D.j == C.index(K)].drop(columns="j").round(2).to_string(index=False))
# second lineup marginal value (union of wins, weighted)
best = D.j.iloc[0]
def win_vec(k, j):
    S = sims[k]; c, f = C[j]; ours = score(S, (c, f)); return ours
print(f"done ({time.time()-t0:.0f}s)")
pd.to_pickle((C, D, R, W), "res.pkl")
