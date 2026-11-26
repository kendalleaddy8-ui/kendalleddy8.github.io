"""Engine v4 portfolio search (Thanksgiving 2026, generalises tg_port2/robust_pick/lamb_test).
Objective per field f: sum_p W_p * P(best lineup reaches place p), each lineup's hit weighted 1/(1+duplicates in field f)
(a duplicated lineup splits the prize). Places 3/15/150 with weights 40/10/1 (top-3 stands in for 1st: P(1st) is too rare to simulate).
Search: iterated local search (single-player swaps + kicks) on sims A; finalists re-graded on B and C (projection noise);
pick = best mean(B,C). Then hunch tests (--hunch "A+B"), forced-exposure tests (--force "Name"), DK slot order (latest kick in FLEX).
  python3 portfolio.py <week> <thr.npz> --n 3 --tag v4 [--hunch "Jahmyr Gibbs+Kenneth Walker III"] [--force "CeeDee Lamb"]"""
import argparse, itertools, os, sys, collections, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import validate, slots_ok
WP = {3: 40.0, 15: 10.0, 150: 1.0}; FS = ["f1", "f2", "f3"]

class Port:
    def __init__(s, week, npz, shared=4):
        Z = np.load(npz); s.places = [int(p) for p in Z["places"]]; s.shared = shared
        s.pool, C = pd.read_pickle(os.path.join(week, "cands_run.pkl")); s.pool = s.pool.reset_index(drop=True)
        s.sal = s.pool.Salary.to_numpy(float); s.pos = s.pool.Pos.to_numpy(object); s.names = s.pool.Name.to_numpy(object)
        s.ix = {n: i for i, n in enumerate(s.names)}; s.C = [list(c) for c in C]
        s.S = {k: Z["S" + k] for k in "ABC"}; s.T = {k: {f: Z[f"{k}_{f}"] for f in FS} for k in "ABC"}
        s.dup = {f: collections.Counter(map(tuple, np.sort(Z[f"F_{f}"].astype(int), 1))) for f in FS}
        s.w = np.array([WP[p] for p in s.places])
    def dw(s, L):                                   # per-field duplicate weight
        t = tuple(sorted(int(i) for i in L)); return {f: 1.0 / (1 + s.dup[f].get(t, 0)) for f in FS}
    def contrib(s, k, L):                           # per field: (sims x places) weighted hit matrix
        a = s.S[k][:, L].sum(1); d = s.dw(L)
        return {f: (a[:, None] >= s.T[k][f]) * d[f] for f in FS}
    def obj(s, k, Ls):
        H = [s.contrib(k, L) for L in Ls]
        return float(np.mean([(np.max([h[f] for h in H], 0).mean(0) * s.w).sum() for f in FS])) * 1e3
    def single(s, k, L):
        a = s.S[k][:, L].sum(1); return {p: float(np.mean([(a >= s.T[k][f][:, i]).mean() for f in FS])) for i, p in enumerate(s.places)}
    def ok(s, Ls):
        if validate([tuple(s.names[L]) for L in Ls], s.pool, max_shared=s.shared): return False
        return not any(s.pos[i] == "DST" for a, b in itertools.combinations(Ls, 2) for i in set(a) & set(b))
    def search(s, Ls, locks=None, iters=60, k="A"):
        Ls = [list(L) for L in Ls]; locks = locks or [set() for _ in Ls]; cur = s.obj(k, Ls); S = s.S[k]
        for _ in range(iters):
            best = (cur + 1e-6, None)
            for q in range(len(Ls)):
                Ho = [s.contrib(k, Ls[j]) for j in range(len(Ls)) if j != q]
                o = {f: (np.max([h[f] for h in Ho], 0) if Ho else np.zeros((len(S), len(s.places)))) for f in FS}
                base = S[:, Ls[q]].sum(1)
                for i, old in enumerate(Ls[q]):
                    if old in locks[q]: continue
                    cand = np.where(s.sal <= 50000 - (s.sal[Ls[q]].sum() - s.sal[old]))[0]; cand = cand[~np.isin(cand, Ls[q])]
                    cand = cand[s.pos[cand] == s.pos[old]] if s.pos[old] in ("QB", "DST") else cand[np.isin(s.pos[cand], ["RB", "WR", "TE"])]
                    if not len(cand): continue
                    new = base[:, None] - S[:, [old]] + S[:, cand]; v = np.zeros(len(cand))
                    for f in FS:
                        dw = np.array([s.dw([x for x in Ls[q] if x != old] + [c])[f] for c in cand])
                        for pi in range(len(s.places)):
                            hit = (new >= s.T[k][f][:, [pi]]) * dw[None, :]
                            v += s.w[pi] * np.maximum(hit, o[f][:, [pi]]).mean(0)
                    v = v / len(FS) * 1e3
                    for j in np.argsort(-v)[:15]:
                        if v[j] <= best[0]: break
                        tr = list(Ls[q]); tr[i] = cand[j]
                        if not slots_ok(list(s.pos[tr])): continue
                        trial = [tr if r == q else Ls[r] for r in range(len(Ls))]
                        if s.ok(trial): best = (v[j], (q, i, cand[j])); break
            if best[1] is None: break
            q, i, j = best[1]; Ls[q][i] = j; cur = best[0]
        return Ls, cur
    def ils(s, Ls, locks=None, kicks=4, seed=0):
        rng = np.random.default_rng(seed); Ls, cur = s.search(Ls, locks)
        for _ in range(kicks):
            q = int(rng.integers(len(Ls))); pc = [c for c in s.C[:250] if not (locks and locks[q]) or locks[q] <= set(c)]
            if not pc: continue
            trial = [list(pc[int(rng.integers(len(pc)))]) if r == q else Ls[r] for r in range(len(Ls))]
            if not s.ok(trial): continue
            t2, v2 = s.search(trial, locks)
            if v2 > cur: Ls, cur = t2, v2
        return Ls, cur
    def grade(s, Ls): return {k: s.obj(k, Ls) for k in "ABC"}
    def greedy(s, first=None, order=None):
        pk = [first] if first else []
        for j in (order if order is not None else range(len(s.C))):
            c = s.C[j]
            if not pk or s.ok(pk + [c]): pk.append(c)
            if len(pk) == s.n: return pk
        return None
    def slot_order(s, L):
        """DK order QB,RB,RB,WR,WR,WR,TE,FLEX,DST with the LATEST-kicking flex-eligible player in FLEX (late-swap flexibility)."""
        d = s.pool.iloc[L].copy(); kt = d.Kick.astype(str).map(lambda k: int(k.split(":")[0]) % 12 * 60 + int(k.split(":")[1][:2]))
        d["kt"] = kt.values; need = {"RB": 2, "WR": 3, "TE": 1}; flex = d[d.Pos.isin(need)]
        for _, r in flex.sort_values("kt", ascending=False).iterrows():
            rest = flex.drop(r.name)
            if all((rest.Pos == p).sum() >= n for p, n in need.items()): fx = r.name; break
        out = [d[d.Pos == "QB"].index[0]]
        for p, n in need.items(): out += [i for i in d[d.Pos == p].sort_values("kt").index if i != fx][:n]
        return out + [fx, d[d.Pos == "DST"].index[0]]

def main():
    a = argparse.ArgumentParser(); a.add_argument("week"); a.add_argument("npz"); a.add_argument("--n", type=int, default=3)
    a.add_argument("--tag", default="v4"); a.add_argument("--starts", type=int, default=10); a.add_argument("--shared", type=int, default=4)
    a.add_argument("--seed0", type=int, default=0); a.add_argument("--hunch", action="append", default=[]); a.add_argument("--force", action="append", default=[])
    a = a.parse_args(); P = Port(a.week, a.npz, a.shared); P.n = a.n; log = []
    say = lambda *x: (print(*x, flush=True), log.append(" ".join(map(str, x))))
    so = lambda L: sum(WP[p] * v for p, v in P.single("A", L).items()); P.C.sort(key=so, reverse=True)
    say(f"[{a.tag}] {len(P.pool)} players · {len(P.C)} candidates · places {P.places} weights {list(P.w)} · dup-aware")
    res = []
    for st in range(a.seed0, a.seed0 + a.starts):
        rng = np.random.default_rng(st); order = list(range(len(P.C))) if st == 0 else list(rng.permutation(min(200, len(P.C)))) + list(range(len(P.C)))
        g = P.greedy(order=order)
        if not g: continue
        Ls, v = P.ils(g, seed=st); gr = P.grade(Ls); res.append((gr, Ls))
        say(f"start {st}: A {gr['A']:.1f} · B {gr['B']:.1f} · C {gr['C']:.1f} · mean(B,C) {(gr['B']+gr['C'])/2:.1f}")
    res.sort(key=lambda r: -(r[0]["B"] + r[0]["C"])); g0, best = res[0]
    say(f"\nPICK (best mean B,C): A {g0['A']:.1f} B {g0['B']:.1f} C {g0['C']:.1f}")
    tests = []
    for h in a.hunch + a.force:
        lk = {P.ix[n.strip()] for n in h.split("+") if n.strip() in P.ix}
        if not lk: continue
        first = next((c for c in P.C if lk <= set(c)), None)
        if first is None: continue
        alts = []
        for q in range(a.n):
            others = [best[r] for r in range(a.n) if r != q]; trial = None
            for c in [c for c in P.C if lk <= set(c)][:80]:
                if P.ok(others + [c]): trial = others + [c]; break
            if trial is None: continue
            Ls, _ = P.ils(trial, locks=[set()] * (a.n - 1) + [lk], kicks=3, seed=q); gr = P.grade(Ls); alts.append((gr, Ls))
        if not alts: continue
        alts.sort(key=lambda r: -(r[0]["B"] + r[0]["C"])); gr, Ls = alts[0]; tests.append((h, gr, Ls))
        say(f"TEST {h}: A {gr['A']:.1f} B {gr['B']:.1f} C {gr['C']:.1f} · mean(B,C) {(gr['B']+gr['C'])/2:.1f} vs pick {(g0['B']+g0['C'])/2:.1f}")
    own = pd.read_csv(os.path.join(a.week, "own_est.csv")).set_index("Name").Own; rows = []
    sc = [P.single("C", L) for L in best]; order = np.argsort([-sum(WP[p] * v for p, v in x.items()) for x in sc])
    slots = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "DST"]
    for r, q in enumerate(order, 1):
        L = best[q]; x = sc[q]; d = P.pool.iloc[P.slot_order(L)].copy(); d["Slot"] = slots; d["Own"] = d.Name.map(own); d["Lineup"] = r
        dups = [P.dup[f].get(tuple(sorted(L)), 0) for f in FS]
        say(f"\nL{r} ${int(d.Salary.sum()):,} proj {d.Proj.sum():.1f} own {d.Own.sum():.0f}% · top-3 {x[3]*1e4:.2f}/10k · top-15 {x[15]*1e3:.2f}/1k · top-150 {x[150]*100:.2f}% · field dups {dups}")
        for t in d.itertuples(): say(f"   {t.Slot:4s} {t.Name:22s} {t.Team} ${t.Salary:,} {t.Proj:5.1f} own {t.Own:4.1f}% {t.Kick}")
        rows.append(d)
    ex = collections.Counter(n for L in best for n in P.names[L]); say("exposure: " + ", ".join(f"{n} {v}/{a.n}" for n, v in ex.most_common() if v > 1))
    say("VALIDATOR: " + str(validate([tuple(P.names[L]) for L in best], P.pool, max_shared=a.shared) or "PASS"))
    pd.concat(rows).to_csv(os.path.join(a.week, f"lineups_{a.tag}.csv"), index=False)
    pd.to_pickle({"res": res, "tests": tests}, os.path.join(a.week, f"port_{a.tag}.pkl"))
    open(os.path.join(a.week, f"port_{a.tag}.txt"), "w").write("\n".join(log))

if __name__ == "__main__": main()
