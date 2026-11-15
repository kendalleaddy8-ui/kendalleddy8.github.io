import sys; sys.path.insert(0,"../engine")
exec(open("modelA.py").read().split("res=[]")[0])
import numpy as np
from sim import simulate
S=simulate(dk,20000); ix={n:i for i,n in enumerate(dk.Name)}
def ev(L,t):
    s=S[:,[ix[n] for n in L.Name]].sum(1); show(L,t)
    print(f"   SIM med {np.median(s):.1f} p99 {np.percentile(s,99):.1f} P>=210 {np.mean(s>=210):.2%}")
def bb(team,opp,n=2):
    def f(p,x,I):
        p+=lpSum(x[i] for i in I if dk.Team[i]==team and dk.Pos[i] in('WR','TE'))>=n
        p+=lpSum(x[i] for i in I if dk.Team[i]==opp and dk.Pos[i]!='DST')>=1
    return f


ev(build(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey","Emmett Johnson","Vikings"]),"A-plus w/ Vikings DST")
ev(build(lock=["Kirk Cousins","Justin Jefferson","Jaxon Smith-Njigba","Christian McCaffrey","Emmett Johnson","Travis Kelce","T.J. Hockenson"]),"A-plus Kelce+Hock")
ev(build(lock=["James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Vikings","Drew Lock"],extra=bb("SEA","LV",1)),"B-plus: Lock-JSN + LV BB")
ev(build(lock=["James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Vikings","Kirk Cousins"]),"B-plus: Cousins-JJ")
ev(build(lock=["James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Drew Lock"],extra=bb("SEA","LV",1)),"B-plus: Lock, any DST")
ev(build(lock=["Carson Beck","James Cook III","Chuba Hubbard","Emmett Johnson","Justin Jefferson","Jaxon Smith-Njigba","Vikings"]),"B keeping Beck (+ARI catcher)")
