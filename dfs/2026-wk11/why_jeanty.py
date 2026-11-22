exec(open("eval_kendall.py").read().split("LU = {")[0])
P = pool.set_index("Name")
print(P.loc[["Ashton Jeanty","Jalen Nailor","Makai Lemon"] if "Makai Lemon" in set(names) else ["Ashton Jeanty","Jalen Nailor"]][["Team","Opponent","Salary","Base","Proj","Own","Spread","Kick"]].to_string())
k3 = ["Patrick Mahomes","James Cook III","Jahmyr Gibbs","Josh Downs","Makai Lemon","Rome Odunze","Evan Engram","Emmett Johnson","Giants"]
pick = ["Dak Prescott","Tony Pollard","Cam Skattebo","Ashton Jeanty","CeeDee Lamb","George Pickens","Jalen Nailor","Darren Waller","Steelers"]
for nm, L in (("Kendall 3 (Mahomes/Gibbs/Cook)", k3), ("My pick", pick)):
    if all(n in ix for n in L):
        I = [ix[n] for n in L]; m = metr(SB, TB, I)
        print(f"{nm}: {validate([tuple(L)], pool) or 'PASS'} ${int(sal[I].sum()):,} | top-15 {m[0]:.2f}/1k top-150 {m[1]:.2f}% med {m[2]:.1f} p99 {m[3]:.1f}")
    else: print(nm, "missing:", [n for n in L if n not in ix])
# Jeanty's contribution: swap him for every affordable RB/WR/TE and score on holdout
I = [ix[n] for n in pick]; j = I.index(ix["Ashton Jeanty"]); room = 50000 - sal[I].sum() + sal[I[j]]
rows = []
for c in np.where(allowed & np.isin(pos, ["RB"]) & (sal <= room))[0]:
    if c in I: continue
    t = list(I); t[j] = c
    if validate([tuple(names[t])], pool): continue
    m = metr(SB, TB, t); rows.append((m[1] + m[0], names[c], int(sal[c]), pool.Own[c], m[0], m[1]))
rows.sort(reverse=True)
print("\nJeanty's slot filled by other RBs (holdout): top-15/1k · top-150%")
m = metr(SB, TB, I); print(f"  Ashton Jeanty ${int(sal[I[j]])} own {pool.Own[I[j]]:.0f}%: {m[0]:.2f} · {m[1]:.2f}%  <- current")
for r in rows[:6]: print(f"  {r[1]} ${r[2]} own {r[3]:.0f}%: {r[4]:.2f} · {r[5]:.2f}%")
