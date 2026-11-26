"""Engine v4 automatic self-evaluation (handbook §12) — run before EVERY handoff. App-ready: writes selfeval_<tag>.md + .json.
Checks: validator · salary match vs the salary source · injury sweep for every rostered player · exposures + nobody-in-all ·
distinct QBs/DSTs · field duplicates · per-lineup top-3/15/150 (final set C) · cash odds · late-swap map (who is still swappable
after each window) · fragile pieces (Q players, cheap punts in 2+ lineups) · optional 6-world grade from regrade_<tag>.pkl.
  python3 selfeval.py <week> <thr.npz> <lineups.csv> --tag final [--salaries ../2026-wk12-tg/fp_salaries.csv]"""
import argparse, collections, json, os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio import Port, FS; from validate import validate; from cashline import cash_odds

def main():
    a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("lineups")
    a.add_argument("--tag", default="final"); a.add_argument("--salaries"); a.add_argument("--shared", type=int, default=4)
    a = a.parse_args(); P = Port(a.week, a.npz, a.shared); Z = np.load(a.npz)
    L = pd.read_csv(os.path.join(a.week, a.lineups)); groups = [d for _, d in L.groupby("Lineup")]
    Ls = [[P.ix[n] for n in d.Name] for d in groups]; names = [tuple(d.Name) for d in groups]
    out = {"lineups": len(Ls), "checks": {}, "warnings": []}; W = out["warnings"]
    errs = validate(names, P.pool, max_shared=a.shared); out["checks"]["validator"] = "PASS" if not errs else str(errs)
    if a.salaries:
        sal = pd.read_csv(a.salaries).set_index("Name").Salary
        mm = [n for n, s in zip(L.Name, L.Salary) if n not in sal or int(sal[n]) != int(s)]
        out["checks"]["salary_match"] = "PASS" if not mm else mm
    inj = pd.read_csv(os.path.join(a.week, "injuries.csv")); st = dict(zip(inj.Name, inj.Status))
    ov = pd.read_csv(os.path.join(a.week, "overrides.csv")); st.update({n: s for n, s in zip(ov.Name, ov.Status) if isinstance(s, str) and s})
    flags = sorted({(n, st[n]) for n in L.Name if n in st}); out["checks"]["injury_flags"] = flags or "none"
    if any(s.upper() in ("OUT", "IR", "DOUBTFUL") for _, s in flags): W.append(f"rostered player ruled out/doubtful: {flags}")
    ex = collections.Counter(L.Name); out["exposure"] = {n: v for n, v in ex.most_common() if v > 1}
    if len(Ls) >= 3 and max(ex.values()) == len(Ls): W.append("a player is in EVERY lineup")
    qbs = [d[d.Pos == "QB"].Name.iloc[0] for d in groups]; dsts = [d[d.Pos == "DST"].Name.iloc[0] for d in groups]
    out["qbs"], out["dsts"] = qbs, dsts
    if len(set(qbs)) < len(qbs): W.append(f"repeated QB: {qbs}")
    cheap = [n for n, v in ex.items() if v >= 2 and int(L[L.Name == n].Salary.iloc[0]) <= 4000]
    if cheap: W.append(f"same cheap punt in 2+ lineups (lesson 21 says vary them): {cheap}")
    q = [n for n, s in flags if s.upper() == "QUESTIONABLE"]
    if q: W.append(f"questionable players rostered (have a pivot): {q}")
    # §7.2 strong defaults + Thanksgiving additions (warn, never block: "punts can hit")
    lines = pd.read_csv(os.path.join(a.week, "lines.csv")); imp = dict(zip(lines.Team, lines.Total / 2 - lines.Spread / 2))
    for k, d in enumerate(groups, 1):
        punts = d[(d.Pos != "DST") & (d.Proj < 6.0)].Name.tolist()
        if len(punts) > 2: W.append(f"L{k}: {len(punts)} near-punts (proj < 6): {punts} (default max 2)")
        rb = d[d.Pos == "RB"].Team.value_counts()
        if (rb >= 2).any(): W.append(f"L{k}: same-team RB+RB {list(rb[rb >= 2].index)} (backfields split)")
        if (d.Pos == "TE").sum() >= 2: W.append(f"L{k}: two TEs: {d[d.Pos == 'TE'].Name.tolist()} (needs a target/red-zone reason)")
        dst = d[d.Pos == "DST"].iloc[0]
        if imp.get(dst.Opponent, 0) >= 27: W.append(f"L{k}: {dst.Name} DST faces {dst.Opponent} implied {imp[dst.Opponent]:.1f} (cheap-salary punt?)")
    per = []
    for k, (d, Lx) in enumerate(zip(groups, Ls), 1):
        x = P.single("C", Lx); dups = [P.dup[f].get(tuple(sorted(Lx)), 0) for f in FS]
        late = d[d.Kick.astype(str) != d.Kick.astype(str).min()].Name.tolist() if "Kick" in d else []
        per.append({"lineup": k, "salary": int(d.Salary.sum()), "proj": round(float(d.Proj.sum()), 1), "own_sum": round(float(d.Own.sum()), 0) if "Own" in d else None,
                    "top3_per10k": round(x[3] * 1e4, 2), "top15_per1k": round(x[15] * 1e3, 2), "top150_pct": round(x[150] * 100, 2), "field_dups": dups,
                    "swappable_after_first_window": late})
        if max(dups) >= 3: W.append(f"L{k} duplicated {max(dups)}x in a simulated field (prize split risk)")
    c = cash_odds(Z, Ls); out["cash"] = {"per_lineup_pct": [round(p * 100, 1) for p in c["per"]], "any_pct": round(c["any"] * 100, 1), "cash_line": round(c["line"], 1),
                                         "note": "synthetic field is softer than a real one: discount ~5-15 points"}
    for k, p in enumerate(per): p["cash_pct"] = out["cash"]["per_lineup_pct"][k]
    out["per_lineup"] = per
    out["portfolio_grade"] = {k: round(P.obj(k, Ls), 1) for k in "ABC"}
    rg = os.path.join(a.week, f"regrade_{a.tag}.pkl")
    if os.path.exists(rg): out["regrade"] = [(r[0], round(r[1], 1), round(r[3], 1)) for r in pd.read_pickle(rg)][:6]
    json.dump(out, open(os.path.join(a.week, f"selfeval_{a.tag}.json"), "w"), indent=1, default=str)
    md = [f"# Self-evaluation — {a.lineups}", "", "| Check | Result |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in out["checks"].items()]
    md += [f"| QBs | {' / '.join(qbs)} |", f"| DSTs | {' / '.join(dsts)} |", f"| exposure 2+ | {out['exposure']} |",
           f"| P(>=1 cashes) | {out['cash']['any_pct']}% (cash line {out['cash']['cash_line']}) |", "",
           "| L | $ | proj | top-3/10k | top-15/1k | top-150 % | cash % | dups |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {p['lineup']} | {p['salary']:,} | {p['proj']} | {p['top3_per10k']} | {p['top15_per1k']} | {p['top150_pct']} | {p['cash_pct']} | {p['field_dups']} |" for p in per]
    md += ["", "**Warnings:** " + ("; ".join(W) if W else "none")]
    open(os.path.join(a.week, f"selfeval_{a.tag}.md"), "w").write("\n".join(md)); print("\n".join(md))

if __name__ == "__main__": main()
