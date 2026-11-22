"""Optimize each lineup as a SINGLE entry (top-15/top-150 vs simulated field), confirm on holdout."""
import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
pool = pd.read_pickle("cands_run.pkl")[0].reset_index(drop=True); C = pd.read_pickle("cands_run.pkl")[1]
Z = np.load("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz")
SC = ["flat", "cal", "chalky"]; names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object)
ix = {n: i for i, n in enumerate(names)}; BAN = {"Jalon Daniels", "Omar Cooper Jr."}; W15 = 10.0
allowed = np.array([n not in BAN for n in names])
SA, SB = Z["SA"], Z["SB"]; TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}
def obj(S, T, L):
    a = S[:, L].sum(1); return np.mean([(a >= T[s][:, 1]).mean() + W15 * (a >= T[s][:, 0]).mean() for s in SC])
def metr(S, T, L):
    a = S[:, L].sum(1); return (np.mean([(a >= T[s][:, 0]).mean() for s in SC]), np.mean([(a >= T[s][:, 1]).mean() for s in SC]),
                                float(np.median(a)), float(np.percentile(a, 99)))
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
cur = {"L1": ["Bryce Young","Javonte Williams","Tony Pollard","Omarion Hampton","CeeDee Lamb","Tetairoa McMillan","Ja'Kobi Lane","Tommy Tremble","Steelers"],
       "L2": ["Bo Nix","Javonte Williams","Tony Pollard","Cam Skattebo","George Pickens","Jaylen Waddle","DK Metcalf","Evan Engram","Chiefs"],
       "L3": ["Geno Smith","James Cook III","Emmett Johnson","Omarion Hampton","CeeDee Lamb","Garrett Wilson","Adonai Mitchell","Darren Waller","Buccaneers"]}
rows = []
for k, L in cur.items():
    L0 = [ix[n] for n in L]; L1 = climb(L0)
    rows.append((k + " original", L0)); rows.append((k + " improved", L1))
cands = [list(c) for c in C if not (set(names[list(c)]) & BAN)]
cands.sort(key=lambda L: obj(SA, TA, L), reverse=True)
seen = set()
for L in cands[:10]:
    L1 = climb(L); key = tuple(sorted(L1))
    if key not in seen: seen.add(key); rows.append(("global", L1))
out = []
for tag, L in rows:
    p15, p150, med, p99 = metr(SB, TB, L)
    out.append(dict(tag=tag, p15=p15 * 1e3, p150=p150 * 100, med=med, p99=p99, sal=int(sal[L].sum()), lu=", ".join(names[L]), idx=L))
R = pd.DataFrame(out); R["score"] = R.p150 + R.p15
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140)
print("HOLDOUT (never optimized on): p15 = top-15 per 1k · p150 = top-150 % · med/p99 DK pts")
print(R[R.tag != "global"][["tag","p15","p150","med","p99","sal","lu"]].round(2).to_string(index=False))
print("\nGlobal search best 3:"); print(R[R.tag == "global"].sort_values("score", ascending=False).head(3)[["p15","p150","med","p99","sal","lu"]].round(2).to_string(index=False))
R.to_pickle("single_results.pkl")
