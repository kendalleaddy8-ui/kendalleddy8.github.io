import sys; sys.path.insert(0,"../engine")
exec(open("modelA.py").read().split("res=[]")[0])
import numpy as np
from sim import simulate
S=simulate(dk,20000); ix={n:i for i,n in enumerate(dk.Name)}
sc=lambda L:S[:,[ix[n] for n in L]].sum(1)
def gsL(lock,ex=[]):
    def f(p,x,I): p+=lpSum(x[i] for i in I if dk.Team[i]=="JAC" and dk.Pos[i] in('WR','TE'))>=2
    return build(lock=lock,exclude=ex,extra=f)
cands={
 "Best (Lawrence GS)":["Trevor Lawrence","James Cook III","Chuba Hubbard","Emmett Johnson","Colby Parkinson","Justin Jefferson","Parker Washington","Jakobi Meyers","Rams"],
 "B-fixed":["Drew Lock","James Cook III","Chuba Hubbard","Emmett Johnson","Michael Mayer","Jaxon Smith-Njigba","Justin Jefferson","Tutu Atwell","Vikings"],
 "A-fixed":["Kirk Cousins","Christian McCaffrey","Emmett Johnson","Travis Kelce","T.J. Hockenson","Jaxon Smith-Njigba","Justin Jefferson","Laquon Treadwell","Colts"],
}
L=gsL(["Trevor Lawrence"],["Justin Jefferson","Emmett Johnson"]); cands["Lawrence no JJ/EJ"]=list(L.Name); show(L,"Lawrence no JJ/EJ")
L=gsL(["Trevor Lawrence"],["Emmett Johnson"]); cands["Lawrence no EJ"]=list(L.Name); show(L,"Lawrence no EJ")
L=build(lock=["Kirk Cousins","Christian McCaffrey","Travis Kelce","T.J. Hockenson","Jaxon Smith-Njigba","Justin Jefferson"],exclude=["Emmett Johnson"]); cands["A-fixed no EJ"]=list(L.Name); show(L,"A-fixed no EJ")
for k,v in cands.items():
    s=sc(v); print(f"{k:22} ${dk.set_index('Name').loc[v].Salary.sum():,} med {np.median(s):.1f} p99 {np.percentile(s,99):.1f} P210 {np.mean(s>=210):.2%}")
def port(names):
    M=np.column_stack([sc(cands[n]) for n in names]).max(1); return np.mean(M>=210)
import itertools
for combo in [("Best (Lawrence GS)","B-fixed"),("Lawrence no EJ","B-fixed"),("Best (Lawrence GS)","B-fixed","A-fixed"),("Lawrence no EJ","B-fixed","A-fixed"),("Lawrence no JJ/EJ","B-fixed","A-fixed"),("Best (Lawrence GS)","B-fixed","A-fixed no EJ"),("Lawrence no EJ","B-fixed","A-fixed no EJ")]:
    sh=[len(set(cands[a])&set(cands[b])) for a,b in itertools.combinations(combo,2)]
    allc=set.intersection(*[set(cands[c]) for c in combo]) if len(combo)==3 else set()
    print(f"{' + '.join(combo):70} P(any>=210) {port(combo):.2%} shared {sh} in-all {sorted(allc)}")
cands["A-fixed BB"]=["Kirk Cousins","Christian McCaffrey","Emmett Johnson","Travis Kelce","T.J. Hockenson","Jaxon Smith-Njigba","Justin Jefferson","Savion Williams","Browns"]
for combo in [("Lawrence no JJ/EJ","B-fixed","A-fixed BB"),("Best (Lawrence GS)","B-fixed","A-fixed BB")]:
    sh=[len(set(cands[a])&set(cands[b])) for a,b in itertools.combinations(combo,2)]
    print(combo, f"{port(combo):.2%}", sh, sorted(set.intersection(*[set(cands[c]) for c in combo])))
from validate import validate
fin=[cands["Lawrence no JJ/EJ"],cands["B-fixed"],cands["A-fixed BB"]]
print("VALIDATE trio:", validate([tuple(x) for x in fin], dk, max_shared=4) or "PASS")
print("VALIDATE pair:", validate([tuple(cands["Best (Lawrence GS)"]),tuple(cands["B-fixed"])], dk, max_shared=4) or "PASS")
for k in ["Kendall A","Kendall B"]: pass
s=sc(cands["A-fixed BB"]); print("A-fixed BB P210",f"{np.mean(s>=210):.2%}", "med",np.median(s).round(1))
rows=[]
for tag in ["Best (Lawrence GS)","B-fixed","A-fixed BB","Lawrence no JJ/EJ"]:
    for n in cands[tag]: r=dk[dk.Name==n].iloc[0]; rows.append(dict(Lineup=tag,Name=n,Pos=r.Pos,Team=r.Team,Opp=r.Opponent,Salary=r.Salary,Proj=r.Proj,Own=r.Own,Kick=r.Kick))
pd.DataFrame(rows).to_csv("final_lineups.csv",index=False)
