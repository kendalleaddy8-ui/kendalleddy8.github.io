"""Merge parallel portfolio.py workers (port_<tag>_w*.pkl) into port_<tag>.pkl (res sorted by B+C; tests concatenated).
  python3 merge_port.py <week> <tag> <n_workers>"""
import os, sys, pandas as pd
W, tag, n = sys.argv[1], sys.argv[2], int(sys.argv[3]); res, tests = [], []
for i in range(n):
    R = pd.read_pickle(os.path.join(W, f"port_{tag}w{i}.pkl")); res += R["res"]; tests += R["tests"]
res.sort(key=lambda r: -(r[0]["B"] + r[0]["C"])); pd.to_pickle({"res": res, "tests": tests}, os.path.join(W, f"port_{tag}.pkl"))
print(len(res), "starts merged; best B+C", round(res[0][0]["B"] + res[0][0]["C"], 1))
