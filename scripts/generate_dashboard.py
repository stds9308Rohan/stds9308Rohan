import json, os, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

USER = os.getenv("GITHUB_USERNAME", "stds9308Rohan")
TOKEN = os.environ["GH_TOKEN"]
query = """query($login:String!){user(login:$login){followers{totalCount} following{totalCount} repositories(first:100,privacy:PUBLIC,orderBy:{field:UPDATED_AT,direction:DESC}){totalCount nodes{primaryLanguage{name}}} contributionsCollection{totalCommitContributions totalIssueContributions totalPullRequestContributions totalPullRequestReviewContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
payload = json.dumps({"query": query, "variables": {"login": USER}}).encode()
req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json", "User-Agent": "Rohan-GitHub-Intelligence"})
with urllib.request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read())
if result.get("errors"):
    raise RuntimeError(result["errors"])
u = result["data"]["user"]
if not u:
    raise RuntimeError("GitHub user not found: " + USER)
cc, cal = u["contributionsCollection"], u["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]][-371:]
langs = Counter((r.get("primaryLanguage") or {}).get("name") for r in u["repositories"]["nodes"])
langs.pop(None, None)
top = langs.most_common(5)
denom = sum(langs.values()) or 1
svg = []
def add(s): svg.append(s)
add('<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="760" viewBox="0 0 1500 760">')
add('<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#080f1c"/><stop offset="1" stop-color="#14283b"/></linearGradient><linearGradient id="glow" x2="1" y2="1"><stop stop-color="#bef264"/><stop offset="1" stop-color="#10b981"/></linearGradient></defs>')
add('<rect width="1500" height="760" rx="28" fill="url(#bg)"/>')
add('<circle cx="1280" cy="100" r="230" fill="#10b981" opacity=".05"/>')
add('<text x="65" y="70" fill="#f8fafc" font-size="34" font-family="Arial" font-weight="bold">ROHAN.NAIK</text>')
add('<text x="67" y="103" fill="#8ca3b8" font-size="14" font-family="Arial" letter-spacing="3">GITHUB INTELLIGENCE · CONTRIBUTION LANDSCAPE</text>')
add('<text x="1430" y="70" text-anchor="end" fill="#71869c" font-size="13" font-family="Arial">'+datetime.now(timezone.utc).strftime("%d %b %Y").upper()+' UTC</text>')
add('<path d="M65 130H1435" stroke="#2b4056"/>')
add('<text x="70" y="170" fill="#e2e8f0" font-size="19" font-family="Arial">365-DAY CONTRIBUTION TERRAIN</text>')
maxc=max([d["contributionCount"] for d in days] or [1])
ox, oy, sx, sy = 170, 350, 15, 4.5
for i,d in enumerate(days):
    week, dow = divmod(i, 7)
    x, y, n = ox+(week-dow)*sx, oy+(week+dow)*sy, d["contributionCount"]
    base=f"{x},{y} {x+sx},{y+sy} {x},{y+2*sy} {x-sx},{y+sy}"
    add(f'<polygon points="{base}" fill="#172b3e" stroke="#2a4055" stroke-width=".7"/>')
    if n:
        h=min(90, n/maxc*90)
        color="#14532d" if n/maxc>.65 else "#15803d" if n/maxc>.3 else "#65a30d" if n/maxc>.1 else "#a3e635"
        top=f"{x},{y-h} {x+sx},{y+sy-h} {x},{y+2*sy-h} {x-sx},{y+sy-h}"
        left=f"{x-sx},{y+sy-h} {x},{y+2*sy-h} {x},{y+2*sy} {x-sx},{y+sy}"
        right=f"{x+sx},{y+sy-h} {x},{y+2*sy-h} {x},{y+2*sy} {x+sx},{y+sy}"
        add(f'<polygon points="{left}" fill="#166534"/><polygon points="{right}" fill="#0f5132"/><polygon points="{top}" fill="{color}" stroke="#d9f99d" stroke-opacity=".25"/>')
metrics=[("CONTRIBUTIONS",cal["totalContributions"]),("COMMITS",cc["totalCommitContributions"]),("PULL REQUESTS",cc["totalPullRequestContributions]),("ISSUES",cc["totalIssueContributions"]),("REVIEWS",cc["totalPullRequestReviewContributions"]),("PUBLIC REPOS",u["repositories"]["totalCount"])]
for i,(label,value) in enumerate(metrics):
    x, y = 1040+(i%2)*190, 185+(i//2)*105
    add(f'<rect x="{x}" y="{y}" width="170" height="78" rx="13" fill="#14263a" stroke="#2b4056"/>')
    add(f'<text x="{x+14}" y="{y+25}" fill="#8ca3b8" font-size="10" font-family="Arial">{label}</text>')
    add(f'<text x="{x+14}" y="{y+59}" fill="#f8fafc" font-size="27" font-weight="bold" font-family="Arial">{value:,}</text>')
add('<text x="1040" y="525" fill="#e2e8f0" font-size="17" font-family="Arial">LANGUAGE MIX · TOP PUBLIC REPOS</text>')
palette=["#34d399","#60a5fa","#fbbf24","#c084fc","#fb7185"]
for i,(name,count) in enumerate(top):
    y=560+i*30
    pct=count/denom
    add(f'<text x="1040" y="{y}" fill="#cbd5e1" font-size="12" font-family="Arial">{name}</text>')
    add(f'<rect x="1140" y="{y-10}" width="210" height="9" rx="4" fill="#2b4056"/>')
    add(f'<rect x="1140" y="{y-10}" width="{210*pct:.1f}" height="9" rx="4" fill="{palette[i]}"/>')
    add(f'<text x="1360" y="{y}" fill="#94a3b8" font-size="11" font-family="Arial">{pct*100:.0f}%</text>')
add('<path d="M65 690H1435" stroke="#2b4056"/>')
add(f'<text x="67" y="724" fill="#8ca3b8" font-size="12" font-family="Arial">github.com/{USER} · {u["followers"]["totalCount"]} followers · {u["following"]["totalCount"]} following</text>')
add('<text x="1430" y="724" text-anchor="end" fill="#71869c" font-size="11" font-family="Arial">GitHub GraphQL API · public data · auto-updated</text>')
add('</svg>')
Path("assets/github-dashboard.svg").write_text("\\n".join(svg), encoding="utf-8")
print("Dashboard SVG generated.")
