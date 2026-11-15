import os,sys,pickle; os.environ["POOL"]="pool_v2.csv"; sys.path.insert(0,"../engine")
exec(open("modelA.py").read().split("res=[]")[0])
import numpy as np, itertools
from sim import simulate
S=simulate(dk,20000); ix={n:i for i,n in enumerate(dk.Name)}
sc=lambda L:S[:,[ix[n] for n in L]].sum(1)
C=pickle.load(open("v2_cands.pkl","rb"))
def gs(team,opp,n=2,bbreq=True,noaddison=True):
    def f(p,x,I):
        p+=lpSum(x[i] for i in I if dk.Team[i]==team and dk.Pos[i] in('WR','TE'))>=n
        if bbreq: p+=lpSum(x[i] for i in I if dk.Team[i]==opp and dk.Pos[i]!='DST')>=1
    return f
new={
 "Hunch: Cousins/JJ/Gordon/Cook +GB BB":dict(lock=["Kirk Cousins","Justin Jefferson","Ollie Gordon II","James Cook III"],exclude=["Jordan Addison"],extra=gs("MIN","GB",1)),
 "Hunch: Cousins/JJ/JSN/CMC/Gordon +GB BB":dict(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey","Ollie Gordon II"],exclude=["Jordan Addison"],extra=gs("MIN","GB",1)),
 "Hunch: Cousins/JJ/JSN/Cook/EJ +GB BB":dict(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","James Cook III","Emmett Johnson"],exclude=["Jordan Addison"],extra=gs("MIN","GB",1)),
 "Lawrence GS Higbee":dict(lock=["Trevor Lawrence","Tyler Higbee"],extra=gs("JAC","TEN",2,False)),
 "Lock/JSN + Cook/Hubbard/EJ/Vikings (B core)":dict(lock=["Drew Lock","Jaxon Smith-Njigba","James Cook III","Chuba Hubbard","Emmett Johnson","Vikings"],extra=gs("SEA","LV",1)),
}
for k,kw in new.items():
    L=build(**kw)
    if L is None: print(k,"INFEASIBLE"); continue
    C[k]=list(L.Name); show(L,k); s=sc(C[k]); print(f"   SIM P210 {np.mean(s>=210):.2%} med {np.median(s):.1f}")
for k in ["Kendall A","Kendall B"]: C.pop(k,None)
qb=lambda v:[n for n in v if dk.set_index("Name").Pos[n]=="QB"][0]
M={k:sc(v)>=210 for k,v in C.items()}
best=[]
for r in (2,3):
    out=[]
    for combo in itertools.combinations(C,r):
        if len({qb(C[c]) for c in combo})<r: continue
        if any(len(set(C[a])&set(C[b]))>4 for a,b in itertools.combinations(combo,2)): continue
        if r==3 and set.intersection(*[set(C[c]) for c in combo]): continue
        out.append((np.mean(np.any([M[c] for c in combo],0)),combo))
    out.sort(key=lambda z:-z[0])
    print(f"\nTop {r}-lineup portfolios:")
    for p,c in out[:6]: print(f"  {p:.2%}  {c}")
pickle.dump(C,open("v2_cands.pkl","wb"))
