"""Conditional late swap: lock actual DK points for started games (ESPN box scores), re-simulate only games not yet
started, rebuild the field, and re-optimize our late slots for P(top-15/top-150) of the PAIR.
  python3 lateswap.py            (live)      python3 lateswap.py --test   (dry run: 1:00 games 'final' at projection)"""
import sys, re, subprocess, unicodedata, numpy as np, pandas as pd; sys.path.insert(0, "../engine")
from sim import simulate; from field_classic import sample_field, field_thresholds; from pipeline import estimate_own; from validate import validate, slots_ok
TEST = "--test" in sys.argv
DL = "/tmp/claude-0/-home-user-kendalleddy8-github-io/e52ada3d-e7c1-5e4c-a107-74cef7dd16c9/scratchpad/dl_live"; subprocess.run(["mkdir", "-p", DL])
pool = pd.read_pickle("cands_run.pkl")[0].reset_index(drop=True)
names = pool.Name.to_numpy(object); sal = pool.Salary.to_numpy(float); pos = pool.Pos.to_numpy(object); team = pool.Team.to_numpy(object)
norm = lambda s: re.sub(r"[^a-z]", "", re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", unicodedata.normalize("NFKD", s).lower()))
FIX = {"JAX": "JAC", "WSH": "WAS"}
state, actual = {}, {}
if TEST:
    for i in range(len(pool)):
        if pool.Kick[i] == "1:00": state[team[i]] = "post"; actual[i] = float(pool.Proj[i]) * (1.6 if names[i] in ("Tony Pollard", "Garrett Wilson") else 1.0)
else:
    g = DL + "/sb.html"
    subprocess.run(["curl", "-sS", "--max-time", "30", "-A", "Mozilla/5.0", "-o", g, "https://www.espn.com/nfl/scoreboard/_/week/11/year/2026/seasontype/2"], check=True)
    ids = sorted(set(re.findall(r"gameId/(\d+)", open(g, errors="ignore").read())))
    act_name, act_dst = {}, {}
    for gid in ids:
        f = f"{DL}/box_{gid}.html"
        subprocess.run(["curl", "-sS", "--max-time", "30", "-A", "Mozilla/5.0", "-o", f, f"https://www.espn.com/nfl/boxscore/_/gameId/{gid}"])
        out = subprocess.run(["python3", "-I", "../engine/boxscore.py", f], capture_output=True, text=True).stdout.splitlines()[1:]
        for line in out:
            n, tm, v, st = line.rsplit(",", 3); tm = FIX.get(tm, tm); state[tm] = st
            if n.startswith("DST "): act_dst[tm] = float(v)
            else: act_name[(norm(n), tm)] = float(v)
    for i in range(len(pool)):
        if state.get(team[i], "pre") == "post" or (state.get(team[i]) == "in" and pool.Kick[i] == "1:00"):
            actual[i] = act_dst.get(team[i], 0.0) if pos[i] == "DST" else act_name.get((norm(names[i]), team[i]), 0.0)
        # 4:05 game in progress: keep simulating (not frozen at partial stats) but locked for swapping via `started`
started = {t for t, s in state.items() if s != "pre"}
print(f"games started/final: {sorted(started)}  ·  players locked: {len(actual)}")
ov = pd.read_csv("overrides.csv"); ex = {n: float(o) for n, o in zip(ov.Name, ov.Own) if pd.notna(o)}; ex["Jalon Daniels"] = 0.0
S = simulate(pool, 8000, seed=777).astype(np.float32)
for i, v in actual.items(): S[:, i] = v
SC = {"flat": 0.7, "cal": 1.0, "chalky": 1.35}; T = {}
for k, ts in SC.items():
    F = sample_field(estimate_own(pool, ex, temp_scale=ts), 150000, seed=int(ts * 100)); T[k] = field_thresholds(S, F)
ix = {n: i for i, n in enumerate(names)}
L1 = [ix[n] for n in ["Dak Prescott","Tony Pollard","Omarion Hampton","CeeDee Lamb","George Pickens","Garrett Wilson","Darren Waller","Tommy Tremble","Steelers"]]
L2 = [ix[n] for n in ["Bo Nix","Tony Pollard","Breece Hall","Ashton Jeanty","CeeDee Lamb","George Pickens","Elic Ayomanor","Evan Engram","Chiefs"]]
PIVOT = {"Darren Waller": "Mason Taylor", "Tommy Tremble": "Dawson Knox"}   # planned 11:30 inactive swaps
if not TEST:
    for L in (L1, L2):
        for n, rep in PIVOT.items():
            i = ix.get(n)
            if i in L and team[i] in started and (norm(n), team[i]) not in act_name and rep in ix:
                L[L.index(i)] = ix[rep]; print(f"{n} had no stats (inactive) -> assuming planned swap to {rep}")
W15 = 10.0
def val(Ls):
    H = [S[:, L].sum(1) for L in Ls]
    return np.mean([np.any([h >= T[s][:, 1] for h in H], 0).mean() + W15 * np.any([h >= T[s][:, 0] for h in H], 0).mean() for s in SC])
def single(L):
    h = S[:, L].sum(1); return np.mean([(h >= T[s][:, 0]).mean() for s in SC]) * 1e3, np.mean([(h >= T[s][:, 1]).mean() for s in SC]) * 100
locked = lambda i: team[i] in started
before = (single(L1), single(L2), val([L1, L2]))
Ls = [list(L1), list(L2)]; cur = val(Ls); late_pool = [i for i in range(len(pool)) if not locked(i) and names[i] not in ("Jalon Daniels", "Omar Cooper Jr.")]
improved = True
while improved:
    improved = False
    for k in (0, 1):
        for s_i, old in enumerate(Ls[k]):
            if locked(old): continue
            for c in late_pool:
                if c in Ls[k]: continue
                if (pos[old] in ("QB", "DST") and pos[c] != pos[old]) or (pos[old] not in ("QB", "DST") and pos[c] not in ("RB", "WR", "TE")): continue
                t = list(Ls[k]); t[s_i] = c
                if sal[t].sum() > 50000 or not slots_ok(list(pos[t])) or validate([tuple(names[t])], pool): continue
                trial = [t, Ls[1]] if k == 0 else [Ls[0], t]; v = val(trial)
                if v > cur + 1e-6: Ls, cur, improved = trial, v, True
print("\nCurrent standing given actual early scores (P top-15 per 1k · P top-150 %):")
print(f"  L1 {before[0][0]:.2f} · {before[0][1]:.2f}%   L2 {before[1][0]:.2f} · {before[1][1]:.2f}%")
for k, (old, new) in enumerate(zip([L1, L2], Ls), 1):
    sw = [f"{names[a]} -> {names[b]}" for a, b in zip(old, new) if a != b]
    s = single(new); print(f"L{k} swaps: {'; '.join(sw) if sw else 'NONE — keep as is'}   => {s[0]:.2f} · {s[1]:.2f}%  (${int(sal[new].sum()):,})")
print(f"Pair value {before[2]*1e3:.1f} -> {cur*1e3:.1f}")
