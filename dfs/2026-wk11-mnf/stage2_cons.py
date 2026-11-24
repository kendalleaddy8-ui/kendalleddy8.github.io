import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine"); import sim as _s; _s.CV["TE"] = 0.55; _s.CV["K"] = 0.45; _s.CV["DST"] = 0.60
from sim import simulate; from field import sample_field
C, D, R, W = pd.read_pickle("res.pkl"); P = pd.read_csv("pool.csv")
SC = {"props": {}, "cin_shootout": {"Joe Burrow": 29, "Ja'Marr Chase": 28, "Tee Higgins": 20, "Jayden Daniels": 24, "Stefon Diggs": 14},
      "cin_blowout": {"Chase Brown": 23, "Samaje Perine": 8.5, "Joe Burrow": 26, "Jayden Daniels": 17, "Stefon Diggs": 9, "Jacory Croskey-Merritt": 8},
      "was_keeps_close": {"Jayden Daniels": 24, "Jacory Croskey-Merritt": 14, "Stefon Diggs": 14, "Ja'Marr Chase": 21, "Joe Burrow": 22}}
top = list(dict.fromkeys(list(D.sort_values("p1", ascending=False).j.head(14)) + list(D.sort_values("ptop", ascending=False).j.head(10))))
U, cnt, F = sample_field(P, 70000, seed=5); key = {tuple(u): k for k, u in enumerate(U)}
L = [np.array([C[j][0], *sorted(C[j][1])]) for j in top]; col = [key.get(tuple(l), -1) for l in L]; dup = [cnt[c] if c >= 0 else 0 for c in col]
win, tops = {k: [] for k in SC}, {k: [] for k in SC}
for k, ch in SC.items():
    Q = P.copy(); Q["Proj"] = [ch.get(n, p) for n, p in zip(Q.Name, Q.Proj)]; S = simulate(Q, 32000, seed=99 + len(k)).astype(np.float32)
    w = np.zeros((len(S), len(L)), np.float32); t = np.zeros((len(S), len(L)), bool); topk = max(1, int(cnt.sum() * 0.001))
    for a in range(0, len(S), 2000):
        s = S[a:a + 2000]; fs = 1.5 * s[:, U[:, 0]] + s[:, U[:, 1:]].sum(2)
        order = np.argsort(-fs, 1); srt = np.take_along_axis(fs, order, 1); cum = np.cumsum(cnt[order], 1)
        thr = srt[np.arange(len(s)), (cum < topk).sum(1)]
        for i, l in enumerate(L):
            ours = 1.5 * s[:, l[0]] + s[:, l[1:]].sum(1)
            other = np.where(order[:, 0] == col[i], srt[:, 1], srt[:, 0]) if col[i] >= 0 else srt[:, 0]
            w[a:a + 2000, i] = (ours > other) / (dup[i] + 1); t[a:a + 2000, i] = ours >= thr
    win[k], tops[k] = w, t
Wt = {"props": 0.4, "cin_shootout": 0.2, "cin_blowout": 0.2, "was_keeps_close": 0.2}
p1 = sum(Wt[k] * win[k].mean(0) for k in SC) * 1e4; pt = sum(Wt[k] * tops[k].mean(0) for k in SC) * 100
order = np.argsort(-(p1 + 10 * pt))
print("STAGE 2 (32k sims x 4 scenarios): wins/10k · top-0.1% · dupes")
for i in order[:8]:
    c, f = C[top[i]]; tag = " <= KENDALL" if P.Name[c] == "Ja'Marr Chase" and set(P.Name[list(f)]) == {"Joe Burrow","Jayden Daniels","J. Endries","Tee Higgins","D. Neal"} else ""
    print(f"{p1[i]:5.2f} · {pt[i]:5.2f}% · dup {dup[i]:2d} · CPT {P.Name[c]} + {', '.join(P.Name[list(f)])}{tag}")
b = order[0]; best2 = None
for i in range(len(L)):
    if i == b or P.Name[C[top[i]][0]] == P.Name[C[top[b]][0]]: continue
    u1 = sum(Wt[k] * np.maximum(win[k][:, b], win[k][:, i]).mean() for k in SC) * 1e4 + 0
    ut = sum(Wt[k] * (tops[k][:, b] | tops[k][:, i]).mean() for k in SC) * 100
    if best2 is None or u1 + 10 * ut > best2[0]: best2 = (u1 + 10 * ut, i, u1, ut)
_, i, u1, ut = best2; c, f = C[top[i]]
print(f"\nBEST 2nd lineup (different CPT): CPT {P.Name[c]} + {', '.join(P.Name[list(f)])}")
print(f"  one lineup: {p1[b]:.2f}/10k wins, {pt[b]:.2f}% top-0.1%  ->  two lineups: {u1:.2f}/10k wins, {ut:.2f}% top-0.1%")
