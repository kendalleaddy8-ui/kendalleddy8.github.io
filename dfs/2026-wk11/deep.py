exec(open("eval_kendall.py").read().split("LU = {")[0])          # reuse pool/sims/climb/metr from eval_kendall.py
import random; random.seed(7)
C = [list(c) for c in pd.read_pickle("cands_run.pkl")[1] if not (set(names[list(c)]) & BAN)]
C.sort(key=lambda L: obj(SA, TA, L), reverse=True)
pick = [ix[n] for n in ["Dak Prescott","Tony Pollard","Cam Skattebo","Ashton Jeanty","CeeDee Lamb","George Pickens","Jalen Nailor","Darren Waller","Steelers"]]
starts = C[:40]
def kick(L):
    for _ in range(50):
        t = list(L)
        for i in random.sample(range(9), 2):
            p = pos[t[i]]; pool_ix = np.where(allowed & ((pos == p) if p in ("QB", "DST") else np.isin(pos, ["RB", "WR", "TE"])))[0]
            t[i] = int(random.choice(pool_ix))
        if len(set(t)) == 9 and sal[t].sum() <= 50000 and slots_ok(list(pos[t])) and not validate([tuple(names[t])], pool): return t
    return L
starts += [kick(pick) for _ in range(40)]
seen, res = set(), []
for s in starts:
    L = climb(s); key = tuple(sorted(L))
    if key in seen: continue
    seen.add(key); res.append((obj(SA, TA, L), L))
res.sort(key=lambda r: -r[0])
print(f"{len(res)} distinct local optima. Top 6 by search set A, confirmed on holdout B:")
for a, L in res[:6]:
    m = metr(SB, TB, L); print(f"A {a*1e3:5.1f} | B top-15 {m[0]:.2f}/1k top-150 {m[1]:.2f}% med {m[2]:.1f} p99 {m[3]:.1f} ${int(sal[L].sum()):,}: " + ", ".join(names[L]))
m = metr(SB, TB, pick); print(f"PICK  | B top-15 {m[0]:.2f}/1k top-150 {m[1]:.2f}% (A {obj(SA, TA, pick)*1e3:.1f})")
pd.to_pickle(res[:6], "deep_top.pkl")
