import os,sys,pickle; os.environ["POOL"]="pool_v2.csv"; sys.path.insert(0,"../engine")
import numpy as np, pandas as pd, itertools
from sim import simulate
dk=pd.read_csv("pool_v2.csv"); S=simulate(dk,20000); ix={n:i for i,n in enumerate(dk.Name)}
sc=lambda L:S[:,[ix[n] for n in L]].sum(1)
C=pickle.load(open("v2_cands.pkl","rb")); P=dk.set_index("Name")
qb=lambda v:[n for n in v if P.Pos[n]=="QB"][0]; M={k:sc(v)>=210 for k,v in C.items()}
out=[]
for combo in itertools.combinations(C,3):
    if len({qb(C[c]) for c in combo})<3: continue
    if any(len(set(C[a])&set(C[b]))>4 for a,b in itertools.combinations(combo,2)): continue
    allin=set.intersection(*[set(C[c]) for c in combo])
    out.append((np.mean(np.any([M[c] for c in combo],0)),combo,sorted(allin)))
out.sort(key=lambda z:-z[0])
for p,c,a in out[:8]: print(f"{p:.2%} {c} in-all={a}")
print("--- with nobody in all 3 except JJ:")
for p,c,a in [o for o in out if set(o[2])<= {"Justin Jefferson"}][:4]: print(f"{p:.2%} {c} in-all={a}")
