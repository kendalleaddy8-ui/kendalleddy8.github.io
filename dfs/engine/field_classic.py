"""Classic GPP field simulation (handbook roadmap). Synthetic Milly field from ownership with realistic stacking,
then rank our lineups by P(top-15) / P(top-150) / P(1st) out of N entries — the places that actually pay in a Milly.
Pool needs Own (%). Lineup = tuple of 9 pool indices."""
import numpy as np

def sample_field(P, n, seed=1, stack_boost=4.0, bring_boost=1.6, min_sal=48500, batch=40000):
    rng = np.random.default_rng(seed); N = len(P)
    pos = P.Pos.values; team = P.Team.values; opp = P.Opponent.values; sal = P.Salary.values
    w = np.maximum(P.Own.values.astype(float), 0.3)
    idx = {k: np.where(pos == k)[0] for k in ("QB", "RB", "WR", "TE", "DST")}
    flex = np.where(np.isin(pos, ["RB", "WR", "TE"]))[0]
    qb_p = w[idx["QB"]] / w[idx["QB"]].sum(); dst_p = w[idx["DST"]] / w[idx["DST"]].sum()
    out = []; got = 0
    while got < n:
        qb = rng.choice(idx["QB"], batch, p=qb_p)
        W = np.tile(w, (batch, 1))
        same = (team[None, :] == team[qb][:, None]) & np.isin(pos, ["WR", "TE"])[None, :]
        bring = (team[None, :] == opp[qb][:, None]) & np.isin(pos, ["WR", "TE", "RB"])[None, :]
        W = W * np.where(same, stack_boost, 1.0) * np.where(bring, bring_boost, 1.0)
        G = -np.log(rng.random((batch, N))) / W                       # smaller key = picked first
        rb = idx["RB"][np.argsort(G[:, idx["RB"]], 1)[:, :2]]
        wr = idx["WR"][np.argsort(G[:, idx["WR"]], 1)[:, :3]]
        te = idx["TE"][np.argmin(G[:, idx["TE"]], 1)][:, None]
        G2 = G.copy(); r = np.arange(batch)[:, None]
        G2[r, rb] = np.inf; G2[r, wr] = np.inf; G2[r, te] = np.inf
        fx = flex[np.argmin(G2[:, flex], 1)][:, None]
        dst = rng.choice(idx["DST"], batch, p=dst_p)[:, None]
        L = np.hstack([qb[:, None], rb, wr, te, fx, dst])
        s = sal[L].sum(1); keep = (s <= 50000) & (s >= min_sal)
        out.append(np.sort(L[keep], 1)); got += keep.sum()
    F = np.vstack(out)[:n]
    return F

def rank_vs_field(S, F, lineups, places=(1, 15, 150), chunk=40):
    """S: sims x players; F: field lineups (n x 9); lineups: list of index tuples.
    Returns dict place -> array P(our score >= the field's place-th best score) (place=1 means beating every entry)."""
    L = np.array([sorted(l) for l in lineups]); res = {p: np.zeros(len(L)) for p in places}; n = 0
    kmax = max(places)
    for a in range(0, len(S), chunk):
        s = S[a:a + chunk].astype(np.float32)
        fs = np.zeros((len(s), len(F)), np.float32)
        for k in range(F.shape[1]): fs += s[:, F[:, k]]
        top = -np.partition(-fs, kmax - 1, axis=1)[:, :kmax]; top.sort(1); top = top[:, ::-1]
        ours = np.zeros((len(s), len(L)), np.float32)
        for k in range(9): ours += s[:, L[:, k]]
        for p in places:
            thr = top[:, p - 1][:, None]
            res[p] += (ours > thr).sum(0) if p == 1 else (ours >= thr).sum(0)
        n += len(s)
    return {p: v / n for p, v in res.items()}
