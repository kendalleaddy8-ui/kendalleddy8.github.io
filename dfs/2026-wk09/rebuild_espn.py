"""v2.2: rebuild the Week 9 pool from ESPN's full DK table (salary + projection for every player),
keep playbook multipliers + injury overrides, then re-run sim portfolio + angles + validator."""
import re, html, sys, numpy as np, pandas as pd
sys.path.insert(0, "../engine"); from sim import simulate, candidates, pick; from validate import validate
import model                                                     # spreads, multipliers, game-script rules
src = sys.argv[1]
t = open(src, encoding="utf-8", errors="ignore").read()
rows = []
for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
    c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
    if len(c) == 7 and c[0] != "Player":
        rows.append(dict(Name=c[0], Team=c[2], Opponent=c[3].lstrip("@"), Pos=c[4], Base=float(c[5]),
                         Salary=int(c[6].replace("$", "").replace(",", ""))))
dk = pd.DataFrame(rows).drop_duplicates("Name")
dk["Name"] = dk.Name.str.replace(" D/ST", "", regex=False)
# status: OUT / doubtful / always-excluded (sources: NFL.com, Yahoo, Inquirer, ESPN 11/4-11/8)
drop = {"Garrett Wilson", "Treylon Burks", "Cam Skattebo", "Omar Cooper Jr.", "Brian Robinson Jr."}
dk = dk[~dk.Name.isin(drop)]
# role overrides where news post-dates ESPN's projection
over = {"Devin Singletary": 12.5}            # Skattebo doubtful -> lead back
dk["Base"] = [over.get(n, b) for n, b in zip(dk.Name, dk.Base)]
dk = dk[(dk.Base >= 5.5) | (dk.Pos == "DST")].reset_index(drop=True)   # prune irrelevant punts
kick = {t: "4:05" for t in ["HOU", "LAC", "LV", "SF"]} | {t: "4:25" for t in ["GB", "NE", "ARI", "SEA"]}
dk["Kick"] = dk.Team.map(kick).fillna("1:00"); dk["Spread"] = dk.Team.map(model.spread)
lead = set(dk[dk.Pos == "RB"].sort_values("Base").groupby("Team").tail(1).Name)
model.lead_rb.clear(); model.lead_rb.update(lead)
model.alpha_wr.discard("Jaxon Smith-Njigba"); model.alpha_wr.add("Jaxon Smith-Njigba")
dk[["Proj", "Adj"]] = dk.apply(model.adj, axis=1)
vegas = {("DET","MIA"):1.03,("KC","NYJ"):1.03,("CAR","DEN"):1.02,("LAR","WAS"):0.98,("NYG","PHI"):0.98}
k = np.array([vegas.get(tuple(sorted((a, b))), 1.0) for a, b in zip(dk.Team, dk.Opponent)])
dk.loc[dk.Pos != "DST", "Proj"] = (dk.Proj * k)[dk.Pos != "DST"].round(2)
prev = pd.read_csv("pool_adj.csv").set_index("Name").Own
dk["Own"] = [prev.get(n, round(max(1.5, (s - 3000) / 1000 * 1.2), 1)) for n, s in zip(dk.Name, dk.Salary)]
dk.loc[dk.Name == "J.J. McCarthy", "Own"] = 8; dk.loc[dk.Name == "Kenneth Walker III", "Own"] = 14
dk.to_csv("pool_espn.csv", index=False)
print(f"pool: {len(dk)} players (ESPN salaries+projections)")
S = simulate(dk, 20000); C = candidates(dk, S, n=260, seed=5)
for qb in ["J.J. McCarthy", "Drew Lock", "Shedeur Sanders", "Joe Milton III", "Malik Willis", "Brock Purdy", "Patrick Mahomes"]:
    for req in ([{"Jahmyr Gibbs"}, {"Jaxon Smith-Njigba", "Puka Nacua"}], [{"Jahmyr Gibbs"}], []):
        C += candidates(dk, S, n=12, seed=hash((qb, len(req))) % 9999, qbs={qb}, require_any=req)
C = sorted(set(C)); print(len(C), "candidates")
chosen, scores, pu = pick(dk, S, C, n=3, target=240, max_shared=3)
def show(c, title):
    L = dk.iloc[list(c)].sort_values("Salary", ascending=False); sc = S[:, list(c)].sum(1)
    print(f"\n{title}: ${L.Salary.sum():,} · med {np.median(sc):.1f} · p99 {np.percentile(sc,99):.1f} · "
          f"P≥240 {np.mean(sc>=240):.2%} · own≈{L.Own.sum():.0f}%")
    for p in L.itertuples(): print(f"   {p.Pos:3s} {p.Name:22s} {p.Team:3s} vs {p.Opponent:3s} ${p.Salary:,} proj {p.Proj:5.1f} {p.Kick}")
for r, j in enumerate(chosen, 1): show(C[j], f"LINEUP {r}")
print(f"\nPortfolio P(≥1 ≥240) = {pu:.2%}")
L = [tuple(dk.Name.iloc[list(C[j])]) for j in chosen]
print("VALIDATOR:", validate(L, dk, max_shared=3) or "PASS")
print("\nAngle table (best P≥240 per QB among candidates):")
tab = []
for c in C:
    q = dk.iloc[list(c)].query("Pos=='QB'").Name.iloc[0]; tab.append((q, np.mean(S[:, list(c)].sum(1) >= 240)))
print(pd.DataFrame(tab, columns=["QB", "p"]).groupby("QB").p.max().sort_values(ascending=False).head(12).map("{:.2%}".format).to_string())
# re-score the v2.1 portfolio on the corrected pool
old = [["Malik Willis","Jahmyr Gibbs","Christian McCaffrey","Jaxon Smith-Njigba","Malik Washington","Efton Chism III","Darren Waller","Greg Dulcich","Saints"],
       ["Brock Purdy","Jahmyr Gibbs","Ollie Gordon II","Puka Nacua","Antonio Williams","Efton Chism III","Greg Dulcich","George Kittle","Cardinals"],
       ["Daniel Jones","Christian McCaffrey","Jonah Coleman","CeeDee Lamb","Josh Downs","Keenan Allen","George Kittle","Demario Douglas","Giants"]]
print("\nv2.1 portfolio re-scored on ESPN pool:")
for k2, o in enumerate(old, 1):
    idx = [dk.index[dk.Name == n][0] for n in o if (dk.Name == n).any()]
    print(f"  L{k2}: found {len(idx)}/9  P≥240 {np.mean(S[:, idx].sum(1) >= 240):.2%}" if len(idx) == 9 else f"  L{k2}: missing {set(o)-set(dk.Name)}")
