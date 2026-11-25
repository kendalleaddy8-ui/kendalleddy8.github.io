"""Kendall: 'What if I did 5 lineups?'  (A) keep the 3 finals locked + add the best 2; (B) best 5 from scratch.
Graded on B, C + 4 new projection-noise worlds (regrade-style); marginal value of lineups 4 and 5; P(cash) for each.
  python3 five.py <thr.npz>"""
import os, sys, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "../../engine"))
from portfolio import Port, FS; from sim import simulate; from fieldprep import thresholds; from validate import validate
NPZ = sys.argv[1]; P = Port(H, NPZ); Z = np.load(NPZ)
so = lambda L: sum(w * v for w, v in zip(P.w, P.single("A", L).values())); P.C.sort(key=so, reverse=True)
rng = np.random.default_rng(77); keys = ["B", "C"]
for j in range(4):
    Pn = P.pool.copy(); Pn["Proj"] = Pn.Proj * np.exp(rng.normal(0, 0.12, len(Pn)))
    k = f"N{j}"; P.S[k] = simulate(Pn, 40000, seed=900 + j).astype(np.float32)
    P.T[k] = {f: thresholds(P.S[k], Z[f"F_{f}"].astype(int)) for f in FS}; keys.append(k)
grade = lambda Ls: np.mean([P.obj(k, Ls) for k in keys])
F = pd.read_csv(os.path.join(H, "lineups_FINAL.csv")); base3 = [[P.ix[n] for n in d.Name] for _, d in F.groupby("Lineup")]
# (A) 3 locked + 2
P.n = 5; resA = []
for st in range(5):
    order = list(np.random.default_rng(st).permutation(min(300, len(P.C)))) + list(range(len(P.C)))
    g = P.greedy(order=order) if False else None
    pk = [list(L) for L in base3]
    for j in order:
        c = P.C[j]
        if P.ok(pk + [c]): pk.append(c)
        if len(pk) == 5: break
    if len(pk) < 5: continue
    Ls, _ = P.ils(pk, locks=[set(L) for L in base3] + [set(), set()], kicks=3, seed=st); resA.append((grade(Ls), Ls)); print("A start", st, round(resA[-1][0], 1), flush=True)
# (B) 5 from scratch
resB = []
for st in range(5):
    order = list(range(len(P.C))) if st == 0 else list(np.random.default_rng(10 + st).permutation(min(300, len(P.C)))) + list(range(len(P.C)))
    g = P.greedy(order=order)
    if not g: continue
    Ls, _ = P.ils(g, kicks=3, seed=st); resB.append((grade(Ls), Ls)); print("B start", st, round(resB[-1][0], 1), flush=True)
gA, LA = max(resA, key=lambda r: r[0]); gB, LB = max(resB, key=lambda r: r[0]); g3 = grade(base3)
print(f"\n3 finals: {g3:.1f} | A (3 + best 2): {gA:.1f} | B (best 5 from scratch): {gB:.1f}")
# marginal value: best 4 inside each 5-set
for nm, Ls in (("A", LA), ("B", LB)):
    print(f"  {nm}: " + " · ".join(f"first {k}: {grade(Ls[:k]):.1f}" for k in (3, 4, 5)) if nm == "A" else f"  {nm}: 5 = {grade(Ls):.1f}")
print("validator A:", validate([tuple(P.names[L]) for L in LA], P.pool, max_shared=4) or "PASS", "| B:", validate([tuple(P.names[L]) for L in LB], P.pool, max_shared=4) or "PASS")
own = pd.read_csv(os.path.join(H, "own_est.csv")).set_index("Name").Own; slots = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]
for nm, Ls in (("A", LA), ("B", LB)):
    rows = []
    for r, L in enumerate(Ls, 1):
        d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = slots; d["Own"] = d.Name.map(own); d["Lineup"] = r; rows.append(d)
        x = P.single("C", L); print(f"{nm}{r} ${d.Salary.sum():,} top-15 {x[15]*1e3:.2f}/1k top-150 {x[150]*100:.2f}% | " + " | ".join(f"{t.Slot} {t.Name}" for t in d.itertuples()))
    pd.concat(rows).to_csv(os.path.join(H, f"lineups_five_{nm}.csv"), index=False)
