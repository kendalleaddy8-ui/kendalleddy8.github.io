"""Append forced-angle candidates (Kendall's hunches + DvP angles) to cands_run.pkl.  python3 gen_hunch.py <folder>"""
import sys, os, pandas as pd; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../engine"))
from sim import simulate, candidates
W = sys.argv[1]; pool, C = pd.read_pickle(os.path.join(W, "cands_run.pkl")); S = simulate(pool, 20000)
names = set(pool.Name); n0 = len(C)
LOCKS = [("Jahmyr Gibbs", "Kenneth Walker III"), ("Jahmyr Gibbs", "Kenneth Walker III", "Emmett Johnson"),
         ("Jahmyr Gibbs", "Emmett Johnson"), ("Colston Loveland",), ("Joe Milton III", "DeVonta Smith"),
         ("Josh Allen",), ("Patrick Mahomes II",), ("Saquon Barkley",), ("Jahmyr Gibbs", "James Cook III"), ("CeeDee Lamb",), ("Joe Milton III", "CeeDee Lamb"), ("Joe Milton III", "Saquon Barkley")]
for k, lk in enumerate(LOCKS):
    if not set(lk) <= names: continue
    C += candidates(pool, S, n=40, seed=500 + k, lock=set(lk))
C = sorted(set(C)); pd.to_pickle((pool, C), os.path.join(W, "cands_run.pkl")); print(f"{n0} -> {len(C)} candidates")
