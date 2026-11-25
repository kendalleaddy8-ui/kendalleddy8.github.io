"""Re-grade every finalist portfolio on all three sim sets (A base, B and C projection-noise) — pick by mean(B,C), report worst-case.
  python3 robust_pick.py <folder> <thr.npz> <tag>"""
import sys, os, numpy as np, pandas as pd
W, NPZ, TAG = sys.argv[1:4]; Z = np.load(NPZ); SC = ["f1", "f2", "f3"]; W15 = 10.0
pool = pd.read_pickle(os.path.join(W, "cands_run.pkl"))[0].reset_index(drop=True); names = pool.Name.to_numpy(object); pos = pool.Pos.to_numpy(object)
R = pd.read_pickle(os.path.join(W, f"port_{TAG}.pkl"))
sets = {k: (Z["S" + k], {s: Z[f"{k}_{s}"] for s in SC}) for k in "ABC"}
def obj(S, T, Ls):
    sc = [S[:, L].sum(1) for L in Ls]
    return np.mean([np.logical_or.reduce([a >= T[s][:, 1] for a in sc]).mean() + W15 * np.logical_or.reduce([a >= T[s][:, 0] for a in sc]).mean() for s in SC])
cands = [("search%d" % k, Ls) for k, (vb, va, Ls) in enumerate(R["res"])] + [("+".join(n.split()[1] for n in k[:-1]) + "_port", v[0]) for k, v in R["hunch"].items() if k[-1] == "PORT"]
rows = []
for nm, Ls in cands:
    v = {k: obj(S, T, Ls) * 1e3 for k, (S, T) in sets.items()}
    qbs = " / ".join(names[i] for L in Ls for i in L if pos[i] == "QB")
    rows.append((nm, v["A"], v["B"], v["C"], (v["B"] + v["C"]) / 2, min(v.values()), qbs))
D = pd.DataFrame(rows, columns=["port", "A", "B", "C", "meanBC", "worst", "QBs"]).sort_values("meanBC", ascending=False)
print(D.round(1).to_string(index=False)); D.to_csv(os.path.join(W, f"robust_{TAG}.csv"), index=False)
