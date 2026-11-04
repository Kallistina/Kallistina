"""Draw a horizontal 3D contribution graph in purple for the GitHub profile README.

Weeks run left to right (like GitHub's own calendar) and the seven weekdays recede into depth,
so the graph stays horizontal while every day becomes a block whose height shows activity.

Usage:
  GITHUB_TOKEN=... python3 scripts/contrib3d.py Kallistina   # real data (used by the workflow)
  python3 scripts/contrib3d.py --public Kallistina            # real public data, no token needed
  python3 scripts/contrib3d.py --sample                       # made-up data, for previewing locally
Writes assets/contrib3d-light.svg and assets/contrib3d-dark.svg.
"""
import datetime as dt
import json
import math
import os
import random
import re
import sys
import urllib.request

CELL = 14            # block width along the week axis
DEPTH = (6.0, -8.0)  # screen offset per weekday going back (up and to the right)
MAX_H = 34           # height of the busiest day
LEFT, BASE = 20, 112  # screen position of the front-left corner of the grid
W, H = 830, 168

LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")

THEMES = {
    "light": dict(levels=("#ebe8f2", "#d6c9f0", "#b39ce6", "#8a66d6", "#5b3fa0"),
                  text="#57534f", strong="#5b3fa0"),
    "dark": dict(levels=("#1f1b2e", "#4a3a7d", "#6b52b8", "#9478e6", "#c4b2f5"),
                 text="#8b949e", strong="#b9a5ec"),
}

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } } } } }"""


def fetch(login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        cal = json.load(resp)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], [w["contributionDays"] for w in cal["weeks"]]


def fetch_public(login):
    """Read the public contribution calendar page (no token needed; public contributions only)."""
    with urllib.request.urlopen(f"https://github.com/users/{login}/contributions") as resp:
        html = resp.read().decode()
    counts = {}
    for cell_id, text in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', html):
        found = re.match(r"([\d,]+) contribution", text)
        counts[cell_id] = int(found.group(1).replace(",", "")) if found else 0
    weeks = {}
    for td in re.findall(r"<td[^>]*data-date[^>]*>", html):
        cell_id = re.search(r'id="(contribution-day-component-(\d+)-(\d+))"', td)
        weekday, week = int(cell_id.group(2)), int(cell_id.group(3))
        weeks.setdefault(week, []).append({
            "date": re.search(r'data-date="([^"]+)"', td).group(1), "weekday": weekday,
            "contributionCount": counts.get(cell_id.group(1), 0),
            "contributionLevel": LEVELS[int(re.search(r'data-level="(\d)"', td).group(1))],
        })
    ordered = [sorted(weeks[w], key=lambda d: d["weekday"]) for w in sorted(weeks)]
    return sum(d["contributionCount"] for w in ordered for d in w), ordered


def sample():
    rand = random.Random(4)
    start = dt.date.today() - dt.timedelta(days=dt.date.today().weekday() + 1 + 52 * 7)
    weeks, total = [], 0
    for w in range(53):
        days = []
        for d in range(7):
            busy = 0.15 + 0.35 * math.sin(w / 8) ** 2
            count = int(rand.random() < busy) * rand.choice((1, 2, 3, 5, 8, 13))
            total += count
            level = LEVELS[min(4, (count > 0) + (count > 2) + (count > 5) + (count > 10))]
            days.append({"date": str(start + dt.timedelta(days=w * 7 + d)), "weekday": d,
                         "contributionCount": count, "contributionLevel": level})
        weeks.append(days)
    return total, weeks


def shade(hex_color, factor):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * factor))) for v in (r, g, b))


def block(x, y, h, color, delay):
    """A box whose front-bottom-left corner is at (x, y), seen from the front and slightly above."""
    dx, dy = DEPTH
    top = f"M{x},{y - h} h{CELL} l{dx},{dy} h{-CELL} Z"
    front = f"M{x},{y} h{CELL} v{-h} h{-CELL} Z"
    side = f"M{x + CELL},{y} l{dx},{dy} v{-h} l{-dx},{-dy} Z"
    return (f'<g class="b" style="animation-delay:{delay:.2f}s">'
            f'<path d="{side}" fill="{shade(color, 0.72)}"/><path d="{front}" fill="{shade(color, 0.86)}"/>'
            f'<path d="{top}" fill="{color}"/></g>')


def build(total, weeks, t):
    peak = max((d["contributionCount"] for w in weeks for d in w), default=1) or 1
    dx, dy = DEPTH
    blocks = []
    for back in range(6, -1, -1):  # draw the back row (Sunday) first, the front row (Saturday) last
        for wi, week in enumerate(weeks):
            day = next((d for d in week if d["weekday"] == 6 - back), None)
            if day is None:
                continue
            level = LEVELS.index(day["contributionLevel"]) if day["contributionLevel"] in LEVELS else 0
            h = 2 if day["contributionCount"] == 0 else 6 + (MAX_H - 6) * math.sqrt(day["contributionCount"] / peak)
            x, y = LEFT + wi * CELL + back * dx, BASE + back * dy
            blocks.append(block(x, y, round(h, 1), t["levels"][level], 0.15 + wi * 0.018))
    months, seen = [], set()
    for wi, week in enumerate(weeks):
        first = dt.date.fromisoformat(week[0]["date"])
        if first.day <= 7 and first.month not in seen and 0 < wi < len(weeks) - 2:
            seen.add(first.month)
            months.append(f'<text x="{LEFT + wi * CELL}" y="{BASE + 20}" font-size="11" fill="{t["text"]}">{first:%b}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="3D contribution graph: {total} contributions in the last year.">
<style>
  text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow .7s ease-out both; }}
  @keyframes grow {{ from {{ transform: scaleY(0.05); opacity: .3; }} to {{ transform: scaleY(1); opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .b {{ animation: none; }} }}
</style>
{"".join(blocks)}
{"".join(months)}
<text x="{LEFT}" y="{BASE + 44}" font-size="12" fill="{t["text"]}"><tspan font-weight="600" fill="{t["strong"]}">{total}</tspan> contributions in the last year</text>
</svg>
'''


if __name__ == "__main__":
    if "--sample" in sys.argv:
        total, weeks = sample()
    elif "--public" in sys.argv:
        total, weeks = fetch_public(sys.argv[-1])
    else:
        total, weeks = fetch(sys.argv[1])
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out, exist_ok=True)
    for name, theme in THEMES.items():
        with open(os.path.join(out, f"contrib3d-{name}.svg"), "w") as f:
            f.write(build(total, weeks, theme))
    print(f"wrote {out} ({total} contributions)")
