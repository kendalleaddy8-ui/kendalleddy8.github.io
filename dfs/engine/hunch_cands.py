"""Append forced-angle candidates to <week>/cands_run.pkl (Kendall's hunches, DvP angles, stack locks).
  python3 hunch_cands.py <week> --lock "Jahmyr Gibbs+Emmett Johnson" --lock "CeeDee Lamb" [--per 40]"""
import argparse, os, sys, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import simulate, candidates
a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("--lock", action="append", default=[]); a.add_argument("--per", type=int, default=40)
a = a.parse_args(); pool, C = pd.read_pickle(os.path.join(a.week, "cands_run.pkl")); S = simulate(pool, 20000); names = set(pool.Name); n0 = len(C)
for k, lk in enumerate(a.lock):
    s = {n.strip() for n in lk.split("+")}
    if not s <= names: print("skip (not in pool):", s - names); continue
    C += candidates(pool, S, n=a.per, seed=500 + k, lock=s)
C = sorted(set(C)); pd.to_pickle((pool, C), os.path.join(a.week, "cands_run.pkl")); print(f"{n0} -> {len(C)} candidates")
