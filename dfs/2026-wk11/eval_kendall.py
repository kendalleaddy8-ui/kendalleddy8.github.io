"""Score Kendall's two lineups vs the Dak pick on holdout sims, then hill-climb from each (single-entry objective)."""
import sys, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from validate import validate, slots_ok
pool = pd.read_pickle("cands_run.pkl")[0].reset_index(drop=True)
Z = np.load("/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/wk11_thr.npz")
SC = ["flat", "cal", "chalky"]; SA, SB = Z["SA"], Z["SB"]; TA = {s: Z[f"A_{s}"] for s in SC}; TB = {s: Z[f"B_{s}"] for s in SC}
# Knox (Kincaid doubtful -> BUF top TE): proxy column = Shakir's sims scaled to Knox projection 7.0
sh = pool.index[pool.Name == "Khalil Shakir"][0]
row = pool.loc[sh].copy(); row["Name"], row["Pos"], row["Salary"], row["Proj"], row["Own"], row["Status"] = "Dawson Knox", "TE", 2800, 7.0, 3.0, ""
pool = pd.concat([pool, row.to_frame().T], ignore_index=True)
for c in ("Salary", "Proj", "Own", "Spread", "Total"): pool[c] = pd.to_numeric(pool[c])
k = 7.0 / float(pool.loc[sh, "Proj"]); SA = np.hstack([SA, SA[:, [sh]] * k]); SB = np.hstack([SB, SB[:, [sh]] * k])
names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); ix = {n: i for i, n in enumerate(names)}
BAN = {"Jalon Daniels", "Omar Cooper Jr."}; allowed = np.array([n not in BAN for n in names]); W15 = 10.0
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
LU = {"Kendall 1 (Mahomes)": ["Patrick Mahomes","James Cook III","Jahmyr Gibbs","Josh Downs","Ja'Kobi Lane","Carnell Tate","Darren Waller","Emmett Johnson","Giants"],
      "Kendall 2 (Dak)": ["Dak Prescott","Emmett Johnson","Tony Pollard","Josh Downs","CeeDee Lamb","George Pickens","Colston Loveland","Dawson Knox","Giants"],
      "My pick (Dak)": ["Dak Prescott","Tony Pollard","Cam Skattebo","Ashton Jeanty","CeeDee Lamb","George Pickens","Jalen Nailor","Darren Waller","Steelers"]}
out = []
for nm, L in LU.items():
    I = [ix[n] for n in L]; print(nm, "validator:", validate([tuple(L)], pool) or "PASS", f"${int(sal[I].sum()):,}")
    out.append((nm, I))
    if nm.startswith("Kendall"):
        J = climb(I); changes = [f"{names[a]}->{names[b]}" for a, b in zip(I, J) if a != b]
        out.append((nm + " improved [" + ("; ".join(changes) or "no change") + "]", J))
print("\nHOLDOUT: top-15 per 1k · top-150 % · median · 1-in-100 ceiling")
for nm, L in out:
    m = metr(SB, TB, L); print(f"{m[0]:5.2f}  {m[1]:5.2f}%  {m[2]:6.1f}  {m[3]:6.1f}  {nm}")
    if "improved" in nm: print("        " + ", ".join(names[L]) + f"  ${int(sal[L].sum()):,}")
