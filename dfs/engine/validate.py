"""Hard-rule validator (handbook §15). validate(lineups, pool) -> list of (lineup#, problem). Empty = pass."""
from collections import Counter
EXCLUDE_ALWAYS = {"Omar Cooper Jr."}
def slots_ok(pos):
    c = Counter(pos)
    return (c["QB"] == 1 and c["DST"] == 1 and 2 <= c["RB"] <= 3 and 3 <= c["WR"] <= 4 and 1 <= c["TE"] <= 2
            and c["RB"] + c["WR"] + c["TE"] == 7)
def validate(lineups, pool, blowout=-9, max_shared=4):
    P = pool.set_index("Name"); errs = []
    for k, names in enumerate(lineups, 1):
        L = P.loc[list(names)]
        if len(L) != 9: errs.append((k, "not 9 players"))
        if L.Salary.sum() > 50000: errs.append((k, f"salary {L.Salary.sum()}"))
        if not slots_ok(list(L.Pos)): errs.append((k, "invalid positions"))
        for t, n in Counter(L.Team).items():
            if n > 3: errs.append((k, f"{n} players from {t}"))
        d = L[L.Pos == "DST"].iloc[0]
        if ((L.Team == d.Opponent) & (L.Pos != "DST")).any(): errs.append((k, f"offense vs own DST {d.name}"))
        q = L[L.Pos == "QB"].iloc[0]
        own_pc = ((L.Team == q.Team) & L.Pos.isin(["WR", "TE"])).sum()
        if own_pc < 1: errs.append((k, "QB with no own pass catcher"))
        if "Spread" in L and q.Spread > blowout and not ((L.Team == q.Opponent) & (L.Pos != "DST")).any():
            errs.append((k, "no bring-back (not a blowout)"))
        if "Status" in L and L.Status.fillna("").str.upper().isin(["OUT", "D", "DOUBTFUL"]).any():
            errs.append((k, "OUT/Doubtful player"))
        if EXCLUDE_ALWAYS & set(names): errs.append((k, "excluded player"))
    qbs = [P.loc[list(n)].query("Pos=='QB'").index[0] for n in lineups]
    if len(set(qbs)) < len(qbs): errs.append((0, f"duplicate QB across lineups {qbs}"))
    for a in range(len(lineups)):
        for b in range(a + 1, len(lineups)):
            s = len(set(lineups[a]) & set(lineups[b]))
            if s > max_shared: errs.append((0, f"lineups {a+1}&{b+1} share {s}"))
    if len(lineups) >= 3:
        common = set.intersection(*map(set, lineups))
        if common: errs.append((0, f"in every lineup: {sorted(common)}"))
    return errs
