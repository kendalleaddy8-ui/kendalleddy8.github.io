"""Week 11: rank candidates + Kendall's drafts vs a simulated 150k-entry Milly field."""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate; from field_classic import sample_field, rank_vs_field; from validate import validate
t0 = time.time(); pool, C = pd.read_pickle("cands_run.pkl")
C = [c for c in C if "Jalon Daniels" not in set(pool.Name.iloc[list(c)])]          # Mayfield expected to start
if "C. Allen (KC)" not in set(pool.Name):      # Kendall's screen salary; pipeline prunes Base<5.5 — append (indices of C unchanged)
    row = pool[pool.Name == "Josh Downs"].iloc[0].copy()
    row["Name"], row["Salary"], row["Base"], row["Proj"], row["Adj"], row["Own"], row["Status"] = "C. Allen (KC)", 3200, 3.0, 3.0, 4.95, 1.0, ""
    pool = pd.concat([pool, row.to_frame().T], ignore_index=True)
    for c in ("Salary", "Base", "Proj", "Adj", "Own", "Spread", "Total"): pool[c] = pd.to_numeric(pool[c])
from pipeline import estimate_own
ov = pd.read_csv("overrides.csv"); explicit = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}
explicit.update({"C. Allen (KC)": 0.5, "Jalon Daniels": 0.0})
pool = estimate_own(pool, explicit)
print("own model, top by position:", " | ".join(f"{p}: " + ", ".join(f"{n} {o:.0f}" for n, o in pool[pool.Pos == p].sort_values("Own", ascending=False).head(4)[["Name", "Own"]].values) for p in ["QB", "RB", "WR", "TE", "DST"]))
ix = {n: i for i, n in enumerate(pool.Name)}
A = ["Patrick Mahomes","Emmett Johnson","D'Andre Swift","CeeDee Lamb","George Pickens","Jordyn Tyson","Darren Waller","C. Allen (KC)","Panthers"]
B = ["Patrick Mahomes","Jahmyr Gibbs","Emmett Johnson","Josh Downs","Tez Johnson","Jordyn Tyson","Colston Loveland","Tony Pollard","Giants"]
mine = {"Kendall A": tuple(ix[n] for n in A), "Kendall B": tuple(ix[n] for n in B)}
print("validator Kendall A/B:", validate([tuple(A)], pool) or "PASS", "/", validate([tuple(B)], pool) or "PASS")
F = sample_field(pool, 150000, seed=11)
real = pd.Series(F.ravel()).value_counts() / len(F) * 100
print(f"field {len(F):,} lineups, {len(np.unique(F, axis=0)):,} unique ({time.time()-t0:.0f}s). Realized own vs input (top 14):")
print("  " + " · ".join(f"{pool.Name[i]} {real[i]:.0f}/{pool.Own[i]:.0f}" for i in real.index[:14]))
S = simulate(pool, 3000, seed=5)
allL = list(C) + list(mine.values())
r = rank_vs_field(S, F, allL, places=(1, 15, 150))
R = pd.DataFrame({"lu": allL, "p1": r[1], "p15": r[15], "p150": r[150]})
R["name"] = [", ".join(pool.Name.iloc[list(l)].tolist()) for l in allL]
R["qb"] = [pool.Name.iloc[[i for i in l if pool.Pos.iloc[i] == "QB"][0]] for l in allL]
R["own"] = [pool.Own.iloc[list(l)].sum() for l in allL]; R["sal"] = [pool.Salary.iloc[list(l)].sum() for l in allL]
R["tag"] = [next((k for k, v in mine.items() if v == l), "") for l in allL]
print(f"stage 1 ({time.time()-t0:.0f}s)")
# stage 2: top 30 by P(top-15) + Kendall's -> 15k sims
top = R.sort_values(["p15", "p150"], ascending=False).head(30)
top = pd.concat([top, R[R.tag != ""]]).drop_duplicates("name")
S2 = simulate(pool, 15000, seed=99)
r2 = rank_vs_field(S2, F, list(top.lu), places=(1, 15, 150))
top = top.assign(p1=r2[1], p15=r2[15], p150=r2[150]).sort_values(["p15", "p1"], ascending=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 150)
show = top[["tag", "qb", "sal", "own", "p1", "p15", "p150", "name"]].copy()
show["p1"] = (show.p1 * 1e4).round(1); show["p15"] = (show.p15 * 1e3).round(2); show["p150"] = (show.p150 * 100).round(2)
print(f"stage 2 ({time.time()-t0:.0f}s). p1 = wins per 10k slates · p15 = top-15 finishes per 1k · p150 = top-150 (top 0.1%) %")
print(show.head(15).to_string(index=False)); print(show[show.tag != ""].to_string(index=False))
top.to_pickle("field_top.pkl"); R.to_pickle("field_all.pkl")
