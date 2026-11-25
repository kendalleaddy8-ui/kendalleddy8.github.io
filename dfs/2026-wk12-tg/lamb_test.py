"""Kendall: 'What happened to CeeDee?' Force Lamb into lineup k (others re-optimised by ILS), grade on A/B/C vs current.
  python3 lamb_test.py <folder> <thr.npz>"""
import sys, os, numpy as np, pandas as pd
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tg_port2.py")).read()
src = src[:src.index("C = [list(c) for c in C]")]                    # reuse obj/ils/ok/hits definitions only
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], "lambtest"]; exec(src)
C = [list(c) for c in C]; so = lambda L: (lambda p: p[1] + W15 * p[0])(single(SA, TA, L)); C.sort(key=so, reverse=True)
def grade(Ls):
    return {k: obj(S, T, Ls) * 1e3 for k, (S, T) in {"A": (SA, TA), "B": (SB, TB), "C": (SCS, TC)}.items()}
R = pd.read_pickle(os.path.join(W, "port_v3.pkl")); best = R["res"][0][2]; g0 = grade(best)
print("current      ", {k: round(v, 1) for k, v in g0.items()}, "mean", round(np.mean(list(g0.values())), 1))
la = ix["CeeDee Lamb"]; out = []
for k in range(3):
    for c in [c for c in C if la in c][:60]:
        trial = [c if q == k else best[q] for q in range(3)]
        if ok(trial): break
    else: continue
    Ls, _ = ils(SA, TA, trial, locks=[{la} if q == k else set() for q in range(3)], kicks=3, seed=k)
    g = grade(Ls); out.append((np.mean(list(g.values())), g, Ls))
    print(f"Lamb in L{k+1}  ", {q: round(v, 1) for q, v in g.items()}, "mean", round(np.mean(list(g.values())), 1))
    L = [L for L in Ls if la in L][0]; p = single(SCS, TC, L)
    print("    Lamb lineup:", ", ".join(names[L]), f"| top-15 {p[0]*1e3:.2f}/1k top-150 {p[1]*100:.2f}%")
d = pool.set_index("Name").loc[["CeeDee Lamb", "George Pickens", "DeVonta Smith", "Jahmyr Gibbs", "Kenneth Walker III", "Javonte Williams"]]
own = pd.read_csv(os.path.join(W, "own_est.csv")).set_index("Name").Own
for n, r in d.iterrows():
    s = SA[:, ix[n]]; print(f"  {n:20s} ${r.Salary:,} proj {r.Proj:5.1f} pts/$1k {r.Proj/r.Salary*1e3:.2f} own {own[n]:.0f}% · P(30+) {np.mean(s>=30)*100:4.1f}% · P(30+)/own {np.mean(s>=30)*100/own[n]:.2f}")
pd.to_pickle(out, os.path.join(W, "lamb_test.pkl"))
