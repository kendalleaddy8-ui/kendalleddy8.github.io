import pandas as pd, itertools
from pulp import *
dk=pd.read_csv("pool_run.csv").reset_index(drop=True)
def build(lock=[],exclude=[],obj="Adj",extra=None):
    I=dk.index; p=LpProblem("d",LpMaximize); x={i:LpVariable(f"x{i}",cat="Binary") for i in I}
    p+=lpSum(x[i]*dk[obj][i] for i in I); p+=lpSum(x[i]*dk.Salary[i] for i in I)<=50000; p+=lpSum(x.values())==9
    P=lambda q: lpSum(x[i] for i in I if dk.Pos[i]==q)
    p+=P('QB')==1; p+=P('DST')==1; p+=P('RB')>=2; p+=P('RB')<=3; p+=P('WR')>=3; p+=P('WR')<=4; p+=P('TE')>=1; p+=P('TE')<=2
    for q in I[dk.Pos=='QB']: p+=lpSum(x[i] for i in I if dk.Team[i]==dk.Team[q] and dk.Pos[i] in('WR','TE'))>=x[q]
    opp=dict(zip(dk.Team,dk.Opponent))
    for d in I[dk.Pos=='DST']:
        for i in I[(dk.Team==opp[dk.Team[d]])&(dk.Pos!='DST')]: p+=x[i]+x[d]<=1
    for t in dk.Team.unique(): p+=lpSum(x[i] for i in I if dk.Team[i]==t)<=3
    for i in I:
        if dk.Name[i] in lock: p+=x[i]==1
        if dk.Name[i] in exclude: p+=x[i]==0
    if extra: extra(p,x,I)
    p.solve(PULP_CBC_CMD(msg=0))
    if p.status!=1: return None
    return dk[[x[i].value()>0.5 for i in I]]
def show(L,t):
    print(f"\n== {t}: ${L.Salary.sum():,} proj {L.Proj.sum():.1f} ceil {L.Adj.sum():.1f} own {L.Own.sum():.0f}")
    for r in L.sort_values(['Pos','Salary'],ascending=[True,False]).itertuples(): print(f"  {r.Pos:3} {r.Name:22} {r.Team}-{r.Opponent} ${r.Salary:,} {r.Proj:.1f}/{r.Adj:.1f} own{r.Own:.0f} {r.Kick}")
res=[]
for q in dk[dk.Pos=='QB'].Name:
    qt=dk[dk.Name==q].Team.iloc[0]; op=dk[dk.Name==q].Opponent.iloc[0]
    sp=dk[dk.Name==q].Spread.iloc[0]
    def ex(p,x,I,qt=qt,op=op,sp=sp):
        p+=lpSum(x[i] for i in I if dk.Team[i]==qt and dk.Pos[i] in('WR','TE'))>=2
        if sp>-9: p+=lpSum(x[i] for i in I if dk.Team[i]==op and dk.Pos[i]!='DST')>=1
    L=build(lock=[q],extra=ex)
    if L is not None: res.append((L.Adj.sum(),q,L))
res.sort(key=lambda z:-z[0])
print("QB game-stack ceilings:", " | ".join(f"{q} {a:.1f}" for a,q,_ in res[:12]))
for a,q,L in res[:3]: show(L,"GS "+q)
show(build(),"Unconstrained ceiling")
show(build(obj="Proj"),"Unconstrained median")
# Kendall-core variants
show(build(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey"]),"A-core fix (Cousins/JJ/JSN/CMC)")
show(build(lock=["Justin Jefferson","Jaxon Smith-Njigba","James Cook III","Emmett Johnson"]),"B-core fix (JJ/JSN/Cook/EJ)")
show(build(lock=["Justin Jefferson","Jaxon Smith-Njigba","James Cook III","Emmett Johnson","Vikings"],exclude=[]),"B-core +Vikings")
