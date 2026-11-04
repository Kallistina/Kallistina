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
LEFT, BASE = 44, 112  # screen position of the front-left corner of the grid
W, H = 860, 172

LEVELS = ("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")

THEMES = {
    "light": dict(levels=("#ebe8f2", "#d6c9f0", "#b39ce6", "#8a66d6", "#5b3fa0"),
                  text="#57534f", strong="#5b3fa0", grid="#d6d0e3"),
    "dark": dict(levels=("#1f1b2e", "#4a3a7d", "#6b52b8", "#9478e6", "#c4b2f5"),
                 text="#8b949e", strong="#b9a5ec", grid="#332d4a"),
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


def stats(weeks):
    """Busiest day and longest streak of days with at least one contribution."""
    days = sorted((d for w in weeks for d in w), key=lambda d: d["date"])
    busiest = max(days, key=lambda d: d["contributionCount"], default=None)
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    return busiest, longest


def floor(n_weeks, t):
    """The flat board the blocks stand on, with a grid line between every day."""
    dx, dy = DEPTH
    x0, y0, x1 = LEFT, BASE, LEFT + n_weeks * CELL
    board = (f'<path d="M{x0},{y0} H{x1} l{7 * dx},{7 * dy} H{x0 + 7 * dx} Z" fill="{t["levels"][0]}"/>'
             f'<path d="M{x0},{y0} H{x1} v3 H{x0} Z" fill="{shade(t["levels"][0], 0.86)}"/>'
             f'<path d="M{x1},{y0} l{7 * dx},{7 * dy} v3 l{-7 * dx},{-7 * dy} Z" fill="{shade(t["levels"][0], 0.72)}"/>')
    lines = "".join(f'<path d="M{x0 + i * CELL},{y0} l{7 * dx},{7 * dy}"/>' for i in range(n_weeks + 1))
    lines += "".join(f'<path d="M{x0 + k * dx},{y0 + k * dy} H{x1 + k * dx}"/>' for k in range(8))
    return board + f'<g stroke="{t["grid"]}" stroke-width="1" fill="none">{lines}</g>'


def legend(x, y, t):
    """'Less ▢▢▢▢▢ More', right-aligned to x."""
    out = f'<text x="{x}" y="{y}" font-size="11" text-anchor="end" fill="{t["text"]}">More</text>'
    for i, color in enumerate(reversed(t["levels"])):
        out += f'<rect x="{x - 40 - i * 14}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>'
    return out + f'<text x="{x - 40 - 5 * 14 - 4}" y="{y}" font-size="11" text-anchor="end" fill="{t["text"]}">Less</text>'


def build(total, weeks, t):
    peak = max((d["contributionCount"] for w in weeks for d in w), default=1) or 1
    dx, dy = DEPTH
    blocks = []
    for back in range(6, -1, -1):  # draw the back row (Sunday) first, the front row (Saturday) last
        for wi, week in enumerate(weeks):
            day = next((d for d in week if d["weekday"] == 6 - back), None)
            if day is None or day["contributionCount"] == 0:
                continue  # empty days are just the board
            level = LEVELS.index(day["contributionLevel"]) if day["contributionLevel"] in LEVELS else 0
            h = 6 + (MAX_H - 6) * math.sqrt(day["contributionCount"] / peak)
            x, y = LEFT + wi * CELL + back * dx, BASE + back * dy
            blocks.append(block(x, y, round(h, 1), t["levels"][level], 0.15 + wi * 0.018))
    months, seen = [], set()
    for wi, week in enumerate(weeks):
        first = dt.date.fromisoformat(week[0]["date"])
        if first.day <= 7 and first.month not in seen and 0 < wi < len(weeks) - 2:
            seen.add(first.month)
            months.append(f'<text x="{LEFT + wi * CELL}" y="{BASE + 20}" font-size="11" fill="{t["text"]}">{first:%b}</text>')
    weekdays = "".join(  # GitHub labels Mon, Wed and Fri; weekday 0 (Sunday) is the back row
        f'<text x="{LEFT - 6 + (6 - wd) * dx}" y="{BASE + (6 - wd) * dy + dy / 2 + 4}" font-size="10" '
        f'text-anchor="end" fill="{t["text"]}">{name}</text>'
        for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    busiest, longest = stats(weeks)
    details = f'<tspan font-weight="600" fill="{t["strong"]}">{total}</tspan> contributions in the last year'
    if busiest and busiest["contributionCount"]:
        when = dt.date.fromisoformat(busiest["date"])
        details += (f'  ·  busiest day <tspan font-weight="600" fill="{t["strong"]}">{when:%b} {when.day}</tspan>'
                    f' ({busiest["contributionCount"]})')
    if longest:
        details += f'  ·  longest streak <tspan font-weight="600" fill="{t["strong"]}">{longest}</tspan> days'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="3D contribution graph: {total} contributions in the last year.">
<style>
  text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  .b {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow .7s ease-out both; }}
  @keyframes grow {{ from {{ transform: scaleY(0.05); opacity: .3; }} to {{ transform: scaleY(1); opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .b {{ animation: none; }} }}
</style>
{floor(len(weeks), t)}
{"".join(blocks)}
{"".join(months)}
{weekdays}
<text x="{LEFT}" y="{BASE + 46}" font-size="12" fill="{t["text"]}" xml:space="preserve">{details}</text>
{legend(W - 24, BASE + 46, t)}
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
