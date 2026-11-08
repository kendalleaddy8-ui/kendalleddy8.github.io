"""Data ingestion. Downloads go to a separate data dir; parse them with `python3 -I`.
  python3 -I fetch.py get <url> <out.html>            # curl through the session proxy (WebFetch can't reach DK/ESPN)
  python3 -I fetch.py espn <espn.html> <out.csv>      # ESPN 'DraftKings DFS values' table -> salary/proj/team pool
  python3 -I fetch.py injuries <dk_injury.html> <out.csv>   # DK Network injury report -> Name,Status
  python3 -I fetch.py text <article.html> <out.txt>   # readable article text (picks, DvP, stacks)
"""
import re, sys, html, subprocess, pandas as pd

def get(url, out):
    subprocess.run(["curl", "-sS", "--max-time", "30", "-A", "Mozilla/5.0", "-o", out, url], check=True)

def _txt(s): return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def espn(src):
    t = open(src, encoding="utf-8", errors="ignore").read(); rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [_txt(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 7 and c[0] != "Player":            # Player | Rating | Team | Opp | Pos | Proj | $
            rows.append(dict(Name=c[0].replace(" D/ST", ""), Rating=c[1], Team=c[2], Opponent=c[3].lstrip("@"),
                             Pos=c[4], Base=float(c[5]), Salary=int(re.sub(r"[^\d]", "", c[6]))))
    return pd.DataFrame(rows).drop_duplicates("Name").reset_index(drop=True)

def text(src):
    t = open(src, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<article.*?</article>", t, re.S); body = m.group(0) if m else t
    body = re.sub(r"<(script|style|aside|nav|figure)[^>]*>.*?</\1>", " ", body, flags=re.S)
    lines = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", body)).splitlines()]
    return "\n".join(l for l in lines if len(l) > 2)

POS = r"(?:QB|RB|WR|TE|FB|K)"
def injuries(src):
    tx = text(src); out = {}
    for m in re.finditer(rf"^([A-Z][\w.'’\- ]+?), {POS} — (Out|Doubtful|Questionable)", tx, re.M):
        out[m.group(1).strip()] = m.group(2).upper()
    for blk in re.findall(r"On IR/Reserve:\n(.+)", tx):                  # "Name, POS (injury...) · Name, POS ..."
        for m in re.finditer(rf"([A-Z][\w.'’\- ]+?), {POS} \(", blk): out.setdefault(m.group(1).strip(), "IR")
    return pd.DataFrame(sorted(out.items()), columns=["Name", "Status"])

if __name__ == "__main__":
    cmd, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
    if cmd == "get": get(a, b)
    elif cmd == "espn": d = espn(a); d.to_csv(b, index=False); print(len(d), "players")
    elif cmd == "injuries": d = injuries(a); d.to_csv(b, index=False); print(d.Status.value_counts().to_string())
    elif cmd == "text": open(b, "w").write(text(a)); print("ok")
