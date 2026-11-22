"""Build the sim-ready pool: ESPN pool + injuries + lines + overrides -> pool_adj.csv (handbook §4).
  python3 pipeline.py --pool espn.csv --inj injuries.csv --lines lines.csv [--overrides overrides.csv] --out pool_adj.csv
lines.csv:     Team,Opponent,Spread,Total,OpenTotal,Kick,PROE      (one row per team; Spread<0 = favorite)
overrides.csv: Name,Base,Mult,Own,Status,Tag,Note   (any blank; Tag in {rushQB, alphaWR, leadRB, exclude})
"""
import argparse, numpy as np, pandas as pd
EXCLUDE_ALWAYS = {"Omar Cooper Jr."}
VOL = {"QB": 1.45, "RB": 1.5, "WR": 1.65, "TE": 1.6, "DST": 2.0}

def build(pool, inj, lines, ov, trenches=None):
    """trenches: optional DataFrame Team,PassProEdge,RunBlockEdge,Source with edges in -2..+2 (team's OL vs opp DL).
    PassPro: QB/WR/TE x(1+0.025*e), opposing DST x(1-0.05*e) · RunBlock: RB x(1+0.04*e).
    Do NOT also put the same trench factors in overrides.Mult (double-apply)."""
    d = pool.merge(lines, on=["Team", "Opponent"], how="left")
    if d.Spread.isna().any(): raise SystemExit(f"missing lines for {sorted(set(d[d.Spread.isna()].Team))}")
    norm = lambda s: s.str.replace("’", "'").str.replace(r"\s+(Jr\.|Sr\.|II|III|IV)$", "", regex=True).str.lower()
    st = dict(zip(norm(inj.Name), inj.Status)) if len(inj) else {}
    d["Status"] = [st.get(k, "") for k in norm(d.Name)]
    if len(ov):
        miss = sorted(set(ov.Name) - set(pool.Name) - EXCLUDE_ALWAYS)
        if miss: print(f"WARNING overrides with no salary-table match (no-op, verify name/salary): {miss}")
    ov = ov.set_index("Name") if len(ov) else pd.DataFrame()
    g = lambda n, c, dflt=None: ov.at[n, c] if n in ov.index and c in ov and pd.notna(ov.at[n, c]) else dflt
    d["Status"] = [g(n, "Status", s) for n, s in zip(d.Name, d.Status)]
    d["Base"] = [float(g(n, "Base", b)) for n, b in zip(d.Name, d.Base)]
    tags = {n: str(g(n, "Tag", "")) for n in d.Name}
    d = d[~d.Status.str.upper().isin(["OUT", "IR", "DOUBTFUL"]) & ~d.Name.isin(EXCLUDE_ALWAYS)
          & ~d.Name.map(lambda n: "exclude" in tags[n])].copy()
    d = d[(d.Base >= 5.5) | (d.Pos == "DST")].reset_index(drop=True)
    lead = set(d[d.Pos == "RB"].sort_values("Base").groupby("Team").tail(1).Name) | {n for n, t in tags.items() if "leadRB" in t}
    alpha = set(d[(d.Pos == "WR") & (d.Base >= 18)].Name) | {n for n, t in tags.items() if "alphaWR" in t}
    def adj(r):
        s, p = r.Spread, r.Base
        if r.Pos == "RB" and r.Name in lead: p *= 1.06 if s <= -7 else 1.03 if s <= -3.5 else 0.92 if s >= 7 else 1
        if r.Pos in ("WR", "TE") and s >= 7: p *= 0.94
        if r.Pos == "WR" and s <= -9: p *= 0.96
        proe = r.get("PROE", np.nan)
        if pd.notna(proe):
            if proe >= 3 and r.Pos in ("WR", "TE"): p *= 1.03
            if proe <= -4.5: p *= 0.97 if r.Pos in ("WR", "TE") else 1.02 if r.Pos == "RB" else 1
        if r.Pos != "DST" and pd.notna(r.get("Pace", np.nan)): p *= float(r.Pace)   # coaching pace multiplier (lines.csv)
        if r.Pos != "DST" and pd.notna(r.get("OpenTotal", np.nan)):         # Vegas money signal
            mv = r.Total - r.OpenTotal; p *= 1.03 if mv >= 3 else 0.98 if mv <= -3 else 1
        p *= float(g(r.Name, "Mult", 1.0))
        if trenches is not None:
            tp = trenches.set_index("Team")
            if r.Pos in ("QB", "WR", "TE") and r.Team in tp.index: p *= 1 + 0.025 * float(tp.at[r.Team, "PassProEdge"] or 0)
            if r.Pos == "RB" and r.Team in tp.index: p *= 1 + 0.04 * float(tp.at[r.Team, "RunBlockEdge"] or 0)
            if r.Pos == "DST" and r.Opponent in tp.index: p *= 1 - 0.05 * float(tp.at[r.Opponent, "PassProEdge"] or 0)
        p = min(max(p, r.Base * 0.80), r.Base * 1.25)                       # cap the multiplier stack
        c = VOL[r.Pos] + (0.05 if r.Name in alpha or "rushQB" in tags[r.Name] else 0)
        return pd.Series({"Proj": round(p, 2), "Adj": round(p * c, 2)})
    d[["Proj", "Adj"]] = d.apply(adj, axis=1)
    d["Implied"] = (d.Total / 2 - d.Spread / 2).round(2)
    d["Own"] = [float(g(n, "Own", max(1.5, round((s - 3000) / 1000 * 1.2, 1)))) for n, s in zip(d.Name, d.Salary)]
    return d

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    for k in ("pool", "inj", "lines", "out"): a.add_argument("--" + k, required=True)
    a.add_argument("--overrides"); a = a.parse_args()
    ov = pd.read_csv(a.overrides) if a.overrides else pd.DataFrame()
    d = build(pd.read_csv(a.pool), pd.read_csv(a.inj), pd.read_csv(a.lines), ov)
    d.to_csv(a.out, index=False)
    print(f"{len(d)} players -> {a.out}  (removed OUT/IR/D; statuses kept: {d.Status.replace('', 'OK').value_counts().to_dict()})")

# ---- ownership model (Week 11): replaces the weak salary heuristic for players without an explicit Own ----
POS_TOTAL = {"QB": 100.0, "RB": 235.0, "WR": 345.0, "TE": 120.0, "DST": 100.0}     # DK classic slot usage incl. FLEX
POS_TEMP = {"QB": 1.4, "RB": 1.5, "WR": 1.3, "TE": 1.4, "DST": 0.9}
POS_CAP = {"QB": 22.0, "RB": 40.0, "WR": 30.0, "TE": 28.0, "DST": 20.0}           # cap for modelled (non-explicit) players

def estimate_own(d, explicit=None, temp_scale=1.0):
    """Per position: score = 0.6*z(Proj) + 0.4*z(points per $1k); own ∝ exp(temp*score), scaled to the position's
    slot usage, capped (excess redistributed). Players in `explicit` (name -> own%) keep their value.
    temp_scale <1 = flatter field, >1 = chalkier field (use both to test robustness)."""
    import numpy as np
    explicit = explicit or {}; d = d.copy(); out = np.zeros(len(d))
    for pos, tot in POS_TOTAL.items():
        m = (d.Pos == pos).values
        if not m.any(): continue
        pr = d.Proj.values[m].astype(float); val = pr / (d.Salary.values[m] / 1000.0)
        z = lambda x: (x - x.mean()) / (x.std() + 1e-9)
        w = np.exp(POS_TEMP[pos] * temp_scale * (0.6 * z(pr) + 0.4 * z(val)))
        names = d.Name.values[m]; fixed = np.array([n in explicit for n in names])
        left = max(tot - sum(explicit[n] for n in names[fixed]), tot * 0.15)
        o = np.array([explicit.get(n, 0.0) for n in names], float); free = ~fixed
        for _ in range(20):                                          # water-filling under the cap
            capped = free & (o >= POS_CAP[pos])
            rest = free & ~capped
            if not rest.any(): break
            o[rest] = w[rest] / w[rest].sum() * (left - o[capped].sum())
            if (o[rest] <= POS_CAP[pos] + 1e-9).all(): break
            o[rest & (o > POS_CAP[pos])] = POS_CAP[pos]
        out[m] = o
    d["Own"] = np.round(out, 1); return d
