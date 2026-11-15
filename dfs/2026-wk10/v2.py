import os,sys; os.environ["POOL"]="pool_v2.csv"; sys.path.insert(0,"../engine")
exec(open("modelA.py").read().split("res=[]")[0])
import numpy as np, itertools
from sim import simulate
S=simulate(dk,20000); ix={n:i for i,n in enumerate(dk.Name)}
sc=lambda L:S[:,[ix[n] for n in L]].sum(1)
def rep(k,v):
    miss=[n for n in v if n not in ix]
    if miss: print(f"{k:34} MISSING {miss}"); return
    s=sc(v); d=dk.set_index("Name").loc[v]
    print(f"{k:34} ${d.Salary.sum():,} med {np.median(s):5.1f} p99 {np.percentile(s,99):5.1f} P210 {np.mean(s>=210):6.2%} own {d.Own.sum():.0f}")
C={
"Kendall A":["Kirk Cousins","Ollie Gordon II","Christian McCaffrey","Josh Downs","Justin Jefferson","Jaxon Smith-Njigba","Travis Kelce","Noah Gray","Cardinals"],
"Kendall B":["Carson Beck","James Cook III","Chuba Hubbard","KC Concepcion","Justin Jefferson","Jaxon Smith-Njigba","Kenyon Sadiq","Emmett Johnson","Vikings"],
"Best v1 (Lawrence GS)":["Trevor Lawrence","James Cook III","Chuba Hubbard","Emmett Johnson","Colby Parkinson","Justin Jefferson","Parker Washington","Jakobi Meyers","Rams"],
"B-fixed v1":["Drew Lock","James Cook III","Chuba Hubbard","Emmett Johnson","Michael Mayer","Jaxon Smith-Njigba","Justin Jefferson","Tutu Atwell","Vikings"],
}
for k,v in C.items(): rep(k,v)
def gs(team,opp,n=2,bbreq=True):
    def f(p,x,I):
        p+=lpSum(x[i] for i in I if dk.Team[i]==team and dk.Pos[i] in('WR','TE'))>=n
        if bbreq: p+=lpSum(x[i] for i in I if dk.Team[i]==opp and dk.Pos[i]!='DST')>=1
    return f
tests=[
 ("Best v2 Lawrence GS",dict(lock=["Trevor Lawrence"],extra=gs("JAC","TEN",2,False))),
 ("Lawrence GS fade EJ",dict(lock=["Trevor Lawrence"],exclude=["Emmett Johnson"],extra=gs("JAC","TEN",2,False))),
 ("Cousins GS (+GB BB)",dict(lock=["Kirk Cousins"],extra=gs("MIN","GB"))),
 ("Cousins GS no BB",dict(lock=["Kirk Cousins"],extra=gs("MIN","GB",1,False))),
 ("A-fix v2: Cousins/JJ/JSN/CMC/Kelce/Gordon",dict(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey","Travis Kelce","Ollie Gordon II"])),
 ("A-fix v2 +EJ",dict(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey","Travis Kelce","Emmett Johnson"])),
 ("B-fix v2 Lock",dict(lock=["Drew Lock","James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Vikings"],extra=gs("SEA","LV",1))),
 ("B-fix v2 Cousins",dict(lock=["Kirk Cousins","James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Vikings"])),
 ("B-fix v2 Watson/Concepcion",dict(lock=["Deshaun Watson","KC Concepcion","James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba"])),
 ("Bryce Young GS",dict(lock=["Bryce Young"],extra=gs("CAR","NO"))),
 ("Watson GS",dict(lock=["Deshaun Watson"],extra=gs("CLE","HOU"))),
 ("Lock GS",dict(lock=["Drew Lock"],extra=gs("SEA","LV"))),
 ("Unconstrained",dict()),
]
for k,kw in tests:
    L=build(**kw)
    if L is None: print(k,"INFEASIBLE"); continue
    C[k]=list(L.Name); show(L,k); rep("   sim",C[k])
import pickle; pickle.dump(C,open("v2_cands.pkl","wb"))
