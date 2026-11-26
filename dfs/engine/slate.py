"""ENGINE v4 — one command for a whole slate (the app backend). Reads <week>/slate.json and enforces the rules in code:
  1 pipeline + sim candidates (run_week)        2 forced hunch/angle candidates (hunch_cands)
  3 fields + 3 sim sets (fieldprep)             4 portfolio search, dup-aware top-3/15/150 (portfolio)
  5 MANDATORY 6-world tie-breaker (regrade)     6 stress worlds (stress)
  7 FINAL = best regrade mean -> lineups_FINAL.csv in DK slot order   8 self-evaluation report (selfeval) — always last
Forks (e.g. a player OUT) are separate week folders listed in "forks"; each gets the full chain.
slate.json example:
{"n": 3, "qbs": ["Josh Allen", "Dak Prescott"], "cands": 900, "shared": 4,
 "locks": ["Jahmyr Gibbs+Emmett Johnson", "CeeDee Lamb"], "hunch": ["Jahmyr Gibbs+Emmett Johnson"], "force": ["CeeDee Lamb"],
 "stress": [["Joe Milton III:1.15", "DeVonta Smith:1.05"]], "salaries": "../fp_salaries.csv", "forks": ["../wout"]}
  python3 slate.py <week> [--skip-to 3]"""
import argparse, json, os, subprocess, sys, numpy as np, pandas as pd
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E)
SCR = os.environ.get("DFS_SCRATCH", "/tmp")

def run(cmd, log):
    print("  $", " ".join(cmd)[:160], flush=True)
    with open(log, "a") as f: r = subprocess.run(cmd, cwd=E, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode: raise SystemExit(f"step failed ({r.returncode}); see {log}")

def chain(W, cfg, skip=1):
    W = os.path.abspath(W); tag = cfg.get("tag", "v4"); npz = os.path.join(SCR, f"{os.path.basename(W)}_{tag}.npz"); log = os.path.join(W, f"slate_{tag}.log")
    py = [sys.executable, "-u"]
    if skip <= 1: run(py + ["run_week.py", W, "--n", str(cfg.get("n", 3)), "--target", "200", "--cands", str(cfg.get("cands", 900)),
                           "--shared", str(cfg.get("shared", 4)), "--qbs", ",".join(cfg.get("qbs", [])), "--tag", "run", "--min-base", str(cfg.get("min_base", 3.5))], log)
    if skip <= 2 and cfg.get("locks"): run(py + ["hunch_cands.py", W] + sum([["--lock", l] for l in cfg["locks"]], []), log)
    if skip <= 3: run(py + ["fieldprep.py", W, npz], log)
    if skip <= 4: run(py + ["portfolio.py", W, npz, "--n", str(cfg.get("n", 3)), "--tag", tag, "--starts", str(cfg.get("starts", 12)), "--shared", str(cfg.get("shared", 4))]
                      + sum([["--hunch", h] for h in cfg.get("hunch", [])], []) + sum([["--force", h] for h in cfg.get("force", [])], []), log)
    if skip <= 5: run(py + ["regrade.py", W, npz, tag], log)
    for b in cfg.get("stress", []): run(py + ["stress.py", W, npz, tag] + sum([["--boost", x] for x in b], []), log)
    # 7: FINAL = best 6-world mean (never the raw search pick: lessons 26/28)
    from portfolio import Port
    P = Port(W, npz, cfg.get("shared", 4)); rg = pd.read_pickle(os.path.join(W, f"regrade_{tag}.pkl")); best = rg[0]
    own = pd.read_csv(os.path.join(W, "own_est.csv")).set_index("Name").Own; rows = []
    for k, L in enumerate(best[4], 1):
        d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]; d["Own"] = d.Name.map(own); d["Lineup"] = k; rows.append(d)
    pd.concat(rows).to_csv(os.path.join(W, "lineups_FINAL.csv"), index=False)
    print(f"  FINAL = {best[0]} (6-world mean {best[1]:.1f}, worst {best[3]:.1f})", flush=True)
    sel = py + ["selfeval.py", W, npz, "lineups_FINAL.csv", "--tag", tag, "--shared", str(cfg.get("shared", 4))]
    if cfg.get("salaries"): sel += ["--salaries", os.path.join(W, cfg["salaries"])]
    run(sel, log); print(open(os.path.join(W, f"selfeval_{tag}.md")).read())

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("--skip-to", type=int, default=1); a = a.parse_args()
    cfg = json.load(open(os.path.join(a.week, "slate.json")))
    print(f"== {a.week}"); chain(a.week, cfg, a.skip_to)
    for fk in cfg.get("forks", []):
        fw = os.path.join(a.week, fk); fc = dict(cfg); fc.update(json.load(open(os.path.join(fw, "slate.json"))) if os.path.exists(os.path.join(fw, "slate.json")) else {})
        fc.pop("forks", None); print(f"== fork {fw}"); chain(fw, fc, a.skip_to)
