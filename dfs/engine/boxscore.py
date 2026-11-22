"""ESPN box score -> DraftKings points (players + DST).  python3 -I boxscore.py <box.html> [...]  -> CSV to stdout.
DK: pass yd .04, pass TD 4, INT -1, 300+ pass yds +3; rush/rec yd .1, TD 6, rec 1, 100+ rush or rec yds +3; fum lost -1;
return TD 6. DST: sack 1, INT 2, fum rec 2, def/ret TD 6, safety 2 (n/a), PA 0:10,1-6:7,7-13:4,14-20:1,21-27:0,28-34:-1,35+:-4."""
import re, sys, json, collections
def walk(o):
    if isinstance(o, dict):
        if "athlts" in o and "keys" in o and "type" in o: yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
def num(x):
    try: return float(str(x).split("/")[0])
    except: return 0.0
def pa_pts(pa): return 10 if pa == 0 else 7 if pa <= 6 else 4 if pa <= 13 else 1 if pa <= 20 else 0 if pa <= 27 else -1 if pa <= 34 else -4
def parse(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    d = json.loads(re.search(r"__espnfitt__'\]=(\{.*?\});</script>", t, re.S).group(1))
    P = collections.defaultdict(float); team_of = {}; D = collections.defaultdict(lambda: collections.defaultdict(float)); teams = []
    for sec in walk(d):
        tm = re.sub(r" (Passing|Rushing|Receiving|Fumbles|Defense|Defensive|Interceptions|Kick Returns|Punt Returns|Kicking|Punting)$", "", sec.get("text", ""))
        if tm not in teams: teams.append(tm)
        K = sec["keys"]; typ = sec["type"]
        for a in sec["athlts"]:
            nm = a["athlt"]["dspNm"]; st = dict(zip(K, a["stats"])); team_of[nm] = tm
            if typ == "passing":
                y = num(st.get("passingYards")); P[nm] += .04 * y + 4 * num(st.get("passingTouchdowns")) - num(st.get("interceptions")) + (3 if y >= 300 else 0)
            elif typ == "rushing":
                y = num(st.get("rushingYards")); P[nm] += .1 * y + 6 * num(st.get("rushingTouchdowns")) + (3 if y >= 100 else 0)
            elif typ == "receiving":
                y = num(st.get("receivingYards")); P[nm] += num(st.get("receptions")) + .1 * y + 6 * num(st.get("receivingTouchdowns")) + (3 if y >= 100 else 0)
            elif typ == "fumbles":
                P[nm] -= num(st.get("fumblesLost")); D[tm]["fumrec_given"] += num(st.get("fumblesLost"))
            elif typ in ("kickReturns", "puntReturns"):
                td = num(st.get("kickReturnTouchdowns", st.get("puntReturnTouchdowns", 0))); P[nm] += 6 * td; D[tm]["rettd"] += td
        if typ == "defensive":
            tt = dict(zip(K, sec.get("ttls", []))); D[tm]["sacks"] += num(tt.get("sacks")); D[tm]["deftd"] += num(tt.get("defensiveTouchdowns"))
        if typ == "interceptions":
            tt = dict(zip(K, sec.get("ttls", []))); D[tm]["ints"] += num(tt.get("interceptions"))
    g = d["page"]["content"]["gamepackage"]["gmStrp"] if "page" in d else next(x for x in walk_any(d, "gmStrp"))
    tms = g["tms"]; state = g["status"]["state"]
    loc2ab = {}
    for tm in teams:
        m = [x for x in tms if x["displayName"].startswith(tm)]
        if len(m) == 1: loc2ab[tm] = m[0]["abbrev"]
    if len(loc2ab) < len(teams):                                   # same-location matchup: fall back to order
        for tm, x in zip(teams, tms): loc2ab.setdefault(tm, x["abbrev"])
    score = {x["abbrev"]: int(x.get("score") or 0) for x in tms}
    ab = [x["abbrev"] for x in tms]; opp = {ab[0]: ab[1], ab[1]: ab[0]}
    out = {n: (loc2ab.get(team_of[n], "?"), v) for n, v in P.items()}
    DD = {loc2ab.get(k, "?"): v for k, v in D.items()}
    dst = {}
    for a in ab:
        v = DD.get(a, {}); o = DD.get(opp[a], {})
        dst[a] = v.get("sacks", 0) + 2 * v.get("ints", 0) + 2 * o.get("fumrec_given", 0) + 6 * (v.get("deftd", 0) + v.get("rettd", 0)) + pa_pts(score[opp[a]])
    return out, dst, state, score

def walk_any(o, key):
    if isinstance(o, dict):
        if key in o: yield o[key]
        for v in o.values(): yield from walk_any(v, key)
    elif isinstance(o, list):
        for v in o: yield from walk_any(v, key)
if __name__ == "__main__":
    print("Name,Team,DK,State")
    for f in sys.argv[1:]:
        out, dst, state, score = parse(f)
        for n, (tm, v) in sorted(out.items(), key=lambda z: -z[1][1]): print(f"{n},{tm},{v:.2f},{state}")
        for a, v in dst.items(): print(f"DST {a},{a},{v:.2f},{state}")
