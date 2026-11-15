import sys; sys.path.insert(0,"../engine")
import numpy as np, pandas as pd
from sim import simulate
p=pd.read_csv("pool_run.csv"); S=simulate(p,20000)
ix={n:i for i,n in enumerate(p.Name)}
L={
"Kendall A":["Kirk Cousins","Ollie Gordon II","Christian McCaffrey","Josh Downs","Justin Jefferson","Jaxon Smith-Njigba","Travis Kelce","Noah Gray","Cardinals"],
"Kendall B":["Carson Beck","James Cook III","Chuba Hubbard","KC Concepcion","Justin Jefferson","Jaxon Smith-Njigba","Kenyon Sadiq","Emmett Johnson","Vikings"],
"A fixed (EJ for Gordon, Parkinson for Gray, Vikings DST)":["Kirk Cousins","Emmett Johnson","Christian McCaffrey","Josh Downs","Justin Jefferson","Jaxon Smith-Njigba","Travis Kelce","Colby Parkinson","Vikings"],
"A fixed2 (EJ, Hockenson for Gray+Downs->Meyers, Vikings)":["Kirk Cousins","Emmett Johnson","Christian McCaffrey","Jakobi Meyers","Justin Jefferson","Jaxon Smith-Njigba","Travis Kelce","T.J. Hockenson","Vikings"],
"B fixed (Lock for Beck, Meyers, Knox)":["Drew Lock","James Cook III","Chuba Hubbard","Jakobi Meyers","Justin Jefferson","Jaxon Smith-Njigba","Dawson Knox","Emmett Johnson","Vikings"],
"B fixed2 (Cousins for Beck, Atwell)":["Kirk Cousins","James Cook III","Chuba Hubbard","Tutu Atwell","Justin Jefferson","Jaxon Smith-Njigba","Kenyon Sadiq","Emmett Johnson","Vikings"],
"Model A best ceiling":["Drew Lock","James Cook III","Zach Charbonnet","Emmett Johnson","Colby Parkinson","Jaxon Smith-Njigba","Justin Jefferson","Jakobi Meyers","Rams"],
"Model A Lawrence GS":["Trevor Lawrence","James Cook III","Chuba Hubbard","Emmett Johnson","Colby Parkinson","Justin Jefferson","Parker Washington","Jakobi Meyers","Rams"],
}
extra=sys.argv[1:] 
for k,v in L.items():
    miss=[n for n in v if n not in ix]
    if miss: print(k,"MISSING",miss); continue
    s=S[:,[ix[n] for n in v]].sum(1); sal=p.set_index("Name").loc[v].Salary.sum(); own=p.set_index("Name").loc[v].Own.sum()
    print(f"{k:58} ${sal:,} med {np.median(s):5.1f} p90 {np.percentile(s,90):5.1f} p99 {np.percentile(s,99):5.1f} P>=200 {np.mean(s>=200):6.2%} P>=210 {np.mean(s>=210):6.2%} own {own:.0f}")
