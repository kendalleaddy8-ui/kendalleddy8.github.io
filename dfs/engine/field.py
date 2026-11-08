"""Field simulation for GPPs (handbook roadmap #1). Builds a synthetic contest field from ownership,
then scores candidate lineups by P(1st place) incl. duplicate splits — not just P(score >= target).
Showdown version: CPT + 5 FLEX. Pool needs Own (total %) and CptOwn (%)."""
import numpy as np, pandas as pd

def sample_field(P, n_entries, seed=1, min_sal=46000, batch=200000):
    rng = np.random.default_rng(seed); N = len(P)
    sal = P.Salary.values; team = P.Team.values; pos = P.Pos.values; opp = P.Opponent.values
    cpt_p = P.CptOwn.values / P.CptOwn.sum(); flex_w = np.maximum(P.Own.values - P.CptOwn.values, 0.1)
    out = []
    while sum(len(o) for o in out) < n_entries:
        cp = rng.choice(N, batch, p=cpt_p)
        g = -np.log(rng.random((batch, N))) / flex_w                 # Gumbel-style weighted sampling w/o replacement
        g[np.arange(batch), cp] = np.inf
        fl = np.argsort(g, 1)[:, :5]
        s = 1.5 * sal[cp] + sal[fl].sum(1)
        ok = (s <= 50000) & (s >= min_sal)
        both = np.array([len(set(team[f]) | {team[c]}) == 2 for c, f in zip(cp, fl)])
        bad_dst = np.array([any(pos[i] == "DST" and any(pos[j] == "QB" and team[j] == opp[i] for j in [c, *f]) for i in [c, *f])
                            for c, f in zip(cp, fl)])
        keep = ok & both & ~bad_dst
        out.append(np.column_stack([cp[keep], np.sort(fl[keep], 1)]))
    F = np.vstack(out)[:n_entries]
    U, cnt = np.unique(F, axis=0, return_counts=True)
    return U, cnt, F

def win_prob(S, U, cnt, lineups, chunk=400):
    """S: sims x players. U: unique field lineups [cpt, f1..f5] (flex sorted); cnt: counts.
    lineups: list of (cpt, flex tuple). Returns (P(1st) with dupes splitting the prize, P(top 0.1%), dup counts)."""
    L = [np.array([c, *sorted(f)]) for c, f in lineups]
    key = {tuple(u): k for k, u in enumerate(U)}
    col = [key.get(tuple(l), -1) for l in L]
    dup = np.array([cnt[c] if c >= 0 else 0 for c in col])
    top_k = max(1, int(round(cnt.sum() * 0.001)))
    pw = np.zeros(len(L)); pt = np.zeros(len(L)); n = 0
    for a in range(0, len(S), chunk):
        s = S[a:a + chunk].astype(np.float32); r = np.arange(len(s))
        fs = 1.5 * s[:, U[:, 0]] + s[:, U[:, 1:]].sum(2)               # chunk x unique field lineups
        order = np.argsort(-fs, 1)
        srt = np.take_along_axis(fs, order, 1); cum = np.cumsum(cnt[order], 1)
        thr = srt[r, np.minimum((cum < top_k).sum(1), srt.shape[1] - 1)]
        top1, top2, arg1 = srt[:, 0], srt[:, 1], order[:, 0]
        for k, l in enumerate(L):
            ours = 1.5 * s[:, l[0]] + s[:, l[1:]].sum(1)
            best_other = np.where(arg1 == col[k], top2, top1) if col[k] >= 0 else top1
            pw[k] += ((ours > best_other) / (dup[k] + 1)).sum()
            pt[k] += (ours >= thr).sum()
        n += len(s)
    return pw / n, pt / n, dup
