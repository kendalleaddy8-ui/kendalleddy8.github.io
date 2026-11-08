"""Week 9 2026 DK Classic model -- follows the GPP playbook (sections 2-3)."""
import pandas as pd
from pulp import *

dk = pd.read_csv("pool.csv")
# spread for each team (negative = favorite), implied totals from latest consensus lines
spread = {"DEN":-2.5,"CAR":2.5,"DAL":-4.5,"IND":4.5,"KC":-9.5,"NYJ":9.5,"DET":-6.5,"MIA":6.5,
          "NO":-3,"CLE":3,"NYG":-3,"PHI":3,"LAR":-4.5,"WAS":4.5,"HOU":-6,"LAC":6,
          "SF":-9.5,"LV":9.5,"NE":-2.5,"GB":2.5,"SEA":-8.5,"ARI":8.5}
lead_rb = {"Jahmyr Gibbs","Kenneth Walker III","Christian McCaffrey","Kyren Williams","Jonathan Taylor",
           "Javonte Williams","Josh Jacobs","Chuba Hubbard","Rhamondre Stevenson","Ollie Gordon II",
           "Jonah Coleman","Devin Singletary","Ashton Jeanty","Breece Hall","Alvin Kamara","Omarion Hampton"}
# red zone / DvP / trenches / matchup multipliers (playbook sec. 2)
mult = {"Christian McCaffrey":1.04,"Jahmyr Gibbs":1.04,"Kenneth Walker III":1.03,"Jonah Coleman":1.05,
        "Greg Dulcich":1.15,"Harold Fannin Jr.":1.06,"Sam LaPorta":1.06,"Malik Nabers":1.07,"Darren Waller":1.05,
        "Brock Purdy":1.06,"Patrick Mahomes":1.05,"Texans":1.15,"Saints":1.03,
        "Justin Herbert":0.92,"Ladd McConkey":0.93,"Omarion Hampton":0.95,"Demario Douglas":1.03,
        "Adonai Mitchell":1.04}
vol = {"QB":1.45,"RB":1.5,"WR":1.65,"TE":1.6,"DST":2.0}
rushing_qb = {"Malik Willis","Jayden Daniels","Drake Maye","Bo Nix","Daniel Jones","Patrick Mahomes"}
alpha_wr = {"Jaxon Smith-Njigba","Puka Nacua","CeeDee Lamb","Amon-Ra St. Brown","Malik Nabers"}

def adj(r):
    s, p = spread[r.Team], r.Base
    if r.Pos == "RB" and r.Name in lead_rb:
        p *= 1.06 if s <= -7 else 1.03 if s <= -3.5 else 0.92 if s >= 7 else 1
    if r.Pos in ("WR","TE"):
        if s >= 7: p *= 0.94
        if s <= -9 and r.Pos == "WR": p *= 0.96
    p *= mult.get(r.Name, 1)
    c = vol[r.Pos] + (0.05 if r.Name in rushing_qb or r.Name in alpha_wr else 0)
    return pd.Series({"Proj": round(p,2), "Adj": round(p*c,2)})

dk[["Proj","Adj"]] = dk.apply(adj, axis=1)
opp = dict(zip(dk.Team, dk.Opponent))

def build(qb, lock=[], exclude=[], avoid=[], maxov=9, min_stack=2, bringback=True):
    I = dk.index; p = LpProblem("d", LpMaximize); x = {i: LpVariable(f"x{i}", cat="Binary") for i in I}
    p += lpSum(x[i]*dk.Adj[i] for i in I)
    p += lpSum(x[i]*dk.Salary[i] for i in I) <= 50000; p += lpSum(x.values()) == 9
    P = lambda q: lpSum(x[i] for i in I if dk.Pos[i] == q)
    p += P("QB")==1; p += P("DST")==1; p += P("RB")>=2; p += P("RB")<=3
    p += P("WR")>=3; p += P("WR")<=4; p += P("TE")>=1; p += P("TE")<=2
    t = dk.Team[dk.Name == qb].iloc[0]
    p += lpSum(x[i] for i in I if dk.Name[i] == qb) == 1
    p += lpSum(x[i] for i in I if dk.Team[i]==t and dk.Pos[i] in ("WR","TE")) >= min_stack
    if bringback: p += lpSum(x[i] for i in I if dk.Team[i]==opp[t] and dk.Pos[i]!="DST") >= 1
    for d in I[dk.Pos=="DST"]:
        for i in I[(dk.Team==opp[dk.Team[d]]) & (dk.Pos!="DST")]: p += x[i]+x[d] <= 1
    for tm in dk.Team.unique(): p += lpSum(x[i] for i in I if dk.Team[i]==tm) <= 3
    for prev in avoid: p += lpSum(x[i] for i in I if dk.Name[i] in prev) <= maxov
    for i in I:
        if dk.Name[i] in lock: p += x[i]==1
        if dk.Name[i] in exclude: p += x[i]==0
    if p.solve(PULP_CBC_CMD(msg=0)) != 1: return None
    return dk[[x[i].value()==1 for i in I]]

CORE_LOCKS = {"Brock Purdy": ["Christian McCaffrey"]}  # Lesson 1: lead RB on -9.5 fav, ties top ceiling

def best_for_each_qb(avoid=[], maxov=9, skip=[], exclude=[]):
    out = []
    for qb in dk.Name[dk.Pos=="QB"]:
        if qb in skip: continue
        t = dk.Team[dk.Name==qb].iloc[0]
        n_pc = ((dk.Team==t) & dk.Pos.isin(["WR","TE"])).sum()
        bb = spread[t] > -9          # bring-back optional only in projected blowouts
        lu = build(qb, lock=CORE_LOCKS.get(qb, []), exclude=exclude, avoid=avoid, maxov=maxov,
                   min_stack=min(2, n_pc), bringback=bb)
        if lu is not None: out.append((lu.Adj.sum(), qb, lu))
    return sorted(out, key=lambda z: -z[0])

order = {"QB":0,"RB":1,"WR":2,"TE":3,"FLEX":4,"DST":5}
kt = {"1:00":0,"4:05":1,"4:25":2}
def slot(lu):
    lu = lu.copy(); lu["Slot"] = lu.Pos
    need = {"RB":2,"WR":3,"TE":1}
    cand = []
    for pos, n in need.items():
        g = lu[lu.Pos==pos]
        if len(g) > n: cand += list(g.index)
    # FLEX = the latest-kickoff player among positions with a surplus (ties -> cheaper)
    f = max(cand, key=lambda i: (kt[lu.Kick[i]], -lu.Salary[i]))
    lu.loc[f, "Slot"] = "FLEX"; return lu
def show(lu, title):
    lu = slot(lu); lu["o"] = lu.Slot.map(order); lu = lu.sort_values(["o","Salary"], ascending=[True,False])
    print(f"\n=== {title} ===  salary ${lu.Salary.sum():,}  (${50000-lu.Salary.sum()} left)  "
          f"proj {lu.Proj.sum():.1f}  ceiling {lu.Adj.sum():.1f}")
    print(lu[["Slot","Name","Team","Opponent","Salary","Proj","Adj","Kick"]].to_string(index=False))

if __name__ == "__main__":
    ranks = best_for_each_qb()
    print("QB loop (best ceiling build per QB):")
    for s, qb, lu in ranks: print(f"  {qb:18s} ceiling {s:6.1f}  proj {lu.Proj.sum():5.1f}  ${lu.Salary.sum():,}")
    L1 = ranks[0][2]; show(L1, f"LINEUP 1 - {ranks[0][1]} stack")
    used_qbs = [ranks[0][1]]
    used_games = {frozenset((L1[L1.Pos=='QB'].Team.iloc[0], L1[L1.Pos=='QB'].Opponent.iloc[0]))}
    lineups = [L1]
    for k in (2, 3):
        # exposure: nobody in all 3 lineups
        excl = list(set(lineups[0].Name) & set(lineups[1].Name)) if k == 3 else []
        r = best_for_each_qb(avoid=[list(l.Name) for l in lineups], maxov=3, skip=used_qbs, exclude=excl)
        # different QB/game stack
        r = [z for z in r if frozenset((z[2][z[2].Pos=='QB'].Team.iloc[0], z[2][z[2].Pos=='QB'].Opponent.iloc[0])) not in used_games]
        s, qb, lu = r[0]; show(lu, f"LINEUP {k} - {qb} stack"); lineups.append(lu); used_qbs.append(qb)
        used_games.add(frozenset((lu[lu.Pos=='QB'].Team.iloc[0], lu[lu.Pos=='QB'].Opponent.iloc[0])))
    # exposure check
    allp = pd.concat(lineups).Name.value_counts()
    print("\nExposure (players in 2+ lineups):"); print(allp[allp>1].to_string())
    pd.concat([l.assign(Lineup=i+1) for i,l in enumerate(lineups)]).to_csv("lineups.csv", index=False)
