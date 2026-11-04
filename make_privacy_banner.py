"""Draw the static privacy banner for the GitHub profile README.

Run:  python3 make_privacy_banner.py  ->  writes assets/privacy-light.svg and assets/privacy-dark.svg
"""
import math
import os

W, H = 1050, 380

THEMES = {
    "light": dict(card="#ffffff", card_line="#e3dfeb", ink="#1c1b22", muted="#8a8796", accent="#5b3fa0",
                  soft="#efeafa", robot="#ece7f8", screen="#ffffff", env="#ffffff", path="#c9c2dc",
                  cheek="#f2a7b5", ring_b="#b4b0bf"),
    "dark": dict(card="#161b22", card_line="#30363d", ink="#e6edf3", muted="#8b949e", accent="#b9a5ec",
                 soft="#241f38", robot="#2a2342", screen="#0d1117", env="#0d1117", path="#3d3a52",
                 cheek="#d98b9b", ring_b="#6e7681"),
}

CLIENT_X, CLIENT_W, CLIENT_H = 60, 190, 84
CLIENT_YS = (48, 148, 248)
ROBOT_CX = 880


def database(x, y, c):
    """A small database cylinder with a padlock on it, top-left at (x, y)."""
    w, h, e = 44, 50, 8
    return f'''
  <path d="M{x},{y + e} v{h - 2 * e} a{w / 2},{e} 0 0 0 {w},0 v{-(h - 2 * e)}" fill="{c["soft"]}" stroke="{c["accent"]}" stroke-width="2.5"/>
  <ellipse cx="{x + w / 2}" cy="{y + e}" rx="{w / 2}" ry="{e}" fill="{c["soft"]}" stroke="{c["accent"]}" stroke-width="2.5"/>
  <path d="M{x},{y + h / 2} a{w / 2},{e} 0 0 0 {w},0" fill="none" stroke="{c["accent"]}" stroke-width="2" opacity=".6"/>
  <g transform="translate({x + w - 6},{y + h - 14})">
    <path d="M-7,-2 v-6 a7,7 0 0 1 14,0 v6" fill="none" stroke="{c["ink"]}" stroke-width="2.6"/>
    <rect x="-10" y="-3" width="20" height="16" rx="3.5" fill="{c["accent"]}"/>
    <circle cx="0" cy="4" r="2.2" fill="{c["card"]}"/>
  </g>'''


def client(y, c):
    x = CLIENT_X
    bars = "".join(
        f'<rect x="{x + 84}" y="{y + 24 + i * 14}" width="{w}" height="6" rx="3" fill="{c["card_line"]}"/>'
        for i, w in enumerate((76, 56, 66))
    )
    return (f'<rect x="{x}" y="{y}" width="{CLIENT_W}" height="{CLIENT_H}" rx="16" fill="{c["card"]}" stroke="{c["card_line"]}" stroke-width="2"/>'
            + database(x + 22, y + 17, c) + bars)


def envelope(cx, cy, angle, c):
    """A sealed envelope centred at (cx, cy), with a few noise sparkles around it."""
    sparkles = ""
    for dx, dy, s in ((-30, -20, 5), (28, -22, 4), (-24, 22, 3.5), (32, 16, 4.5)):
        sparkles += (f'<path d="M{dx},{dy - s} L{dx + s * .3},{dy - s * .3} L{dx + s},{dy} L{dx + s * .3},{dy + s * .3} '
                     f'L{dx},{dy + s} L{dx - s * .3},{dy + s * .3} L{dx - s},{dy} L{dx - s * .3},{dy - s * .3} Z" fill="{c["accent"]}" opacity=".55"/>')
    return f'''
  <g transform="translate({cx:.1f},{cy:.1f}) rotate({angle:.1f})">
    {sparkles}
    <rect x="-19" y="-13" width="38" height="26" rx="4" fill="{c["env"]}" stroke="{c["accent"]}" stroke-width="2.5"/>
    <path d="M-17,-11 L0,2 L17,-11" fill="none" stroke="{c["accent"]}" stroke-width="2.5" stroke-linejoin="round"/>
    <circle cx="0" cy="3" r="4.5" fill="{c["accent"]}"/>
  </g>'''


def flight(y, t, c):
    """Dashed path from a client to the robot, with an envelope travelling on it."""
    x0, y0 = CLIENT_X + CLIENT_W + 8, y + CLIENT_H / 2
    x1, y1 = ROBOT_CX - 105, 200
    cx1, cy1, cx2, cy2 = x0 + 160, y0, x1 - 170, y1
    path = f'<path d="M{x0},{y0} C{cx1},{cy1} {cx2},{cy2} {x1},{y1}" fill="none" stroke="{c["path"]}" stroke-width="2.5" stroke-dasharray="2 9" stroke-linecap="round"/>'
    bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * cx1 + 3 * (1 - t) * t ** 2 * cx2 + t ** 3 * x1
    by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * cy1 + 3 * (1 - t) * t ** 2 * cy2 + t ** 3 * y1
    dx = 3 * (1 - t) ** 2 * (cx1 - x0) + 6 * (1 - t) * t * (cx2 - cx1) + 3 * t ** 2 * (x1 - cx2)
    dy = 3 * (1 - t) ** 2 * (cy1 - y0) + 6 * (1 - t) * t * (cy2 - cy1) + 3 * t ** 2 * (y1 - cy2)
    return path + envelope(bx, by, math.degrees(math.atan2(dy, dx)) * 0.6, c)


def robot(c):
    cx = ROBOT_CX
    hx, hy, hw, hh = cx - 82, 64, 164, 122   # head
    bx, by, bw, bh = cx - 70, 196, 140, 112  # body
    # Chest screen: hollow points split by the boundary the model learned without seeing them.
    sx, sy, sw, sh = bx + 18, by + 18, bw - 36, bh - 40
    pts = [(.12, .2, 1), (.3, .12, 1), (.5, .25, 1), (.75, .14, 1), (.88, .3, 1), (.2, .45, 1),
           (.15, .82, 0), (.35, .7, 0), (.55, .86, 0), (.72, .66, 0), (.9, .8, 0), (.62, .5, 1)]
    rings = "".join(
        f'<circle cx="{sx + u * sw:.1f}" cy="{sy + v * sh:.1f}" r="4.2" fill="none" '
        f'stroke="{c["accent"] if up else c["ring_b"]}" stroke-width="2"/>'
        for u, v, up in pts
    )
    curve = (f'<path d="M{sx + 2},{sy + sh * .62} C{sx + sw * .35},{sy + sh * .4} {sx + sw * .6},{sy + sh * .78} {sx + sw - 2},{sy + sh * .48}" '
             f'fill="none" stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round"/>')
    return f'''
  <line x1="{cx}" y1="{hy}" x2="{cx}" y2="{hy - 26}" stroke="{c["accent"]}" stroke-width="4" stroke-linecap="round"/>
  <circle cx="{cx}" cy="{hy - 32}" r="9" fill="{c["accent"]}"/>
  <rect x="{bx - 26}" y="{by + 16}" width="26" height="14" rx="7" fill="{c["robot"]}" stroke="{c["accent"]}" stroke-width="3"/>
  <rect x="{bx + bw}" y="{by + 16}" width="26" height="14" rx="7" fill="{c["robot"]}" stroke="{c["accent"]}" stroke-width="3"/>
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="22" fill="{c["robot"]}" stroke="{c["accent"]}" stroke-width="3"/>
  <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{c["screen"]}" stroke="{c["accent"]}" stroke-width="2"/>
  {rings}{curve}
  <rect x="{bx + 26}" y="{by + bh}" width="22" height="16" rx="6" fill="{c["accent"]}"/>
  <rect x="{bx + bw - 48}" y="{by + bh}" width="22" height="16" rx="6" fill="{c["accent"]}"/>
  <rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="34" fill="{c["robot"]}" stroke="{c["accent"]}" stroke-width="3"/>
  <rect x="{hx - 4}" y="{hy + 38}" width="{hw + 8}" height="30" rx="8" fill="{c["accent"]}"/>
  <path d="M{hx + hw + 2},{hy + 46} l22,-12 l-4,16 Z M{hx + hw + 2},{hy + 58} l24,10 l-14,6 Z" fill="{c["accent"]}"/>
  <path d="M{cx - 36},{hy + 53} q10,-7 20,0 M{cx + 16},{hy + 53} q10,-7 20,0" fill="none" stroke="{c["robot"]}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="{cx - 50}" cy="{hy + 88}" r="9" fill="{c["cheek"]}" opacity=".7"/>
  <circle cx="{cx + 50}" cy="{hy + 88}" r="9" fill="{c["cheek"]}" opacity=".7"/>
  <path d="M{cx - 18},{hy + 86} q18,16 36,0" fill="none" stroke="{c["ink"]}" stroke-width="3.5" stroke-linecap="round"/>'''


def build(c):
    clients = "".join(client(y, c) for y in CLIENT_YS)
    # Envelopes at different points along their paths, so they read as "in flight".
    flights = "".join(flight(y, t, c) for y, t in zip(CLIENT_YS, (0.36, 0.6, 0.45)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Three clients keep their data locked; only sealed, noisy updates travel to a blindfolded robot that still learns a decision boundary.">
{flights}
{clients}
{robot(c)}
<text x="{W / 2}" y="{H - 14}" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="17" fill="{c["muted"]}">learning from data it's not allowed to see</text>
</svg>
'''


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(out, exist_ok=True)
    for name, colors in THEMES.items():
        with open(os.path.join(out, f"privacy-{name}.svg"), "w") as f:
            f.write(build(colors))
    print("wrote", out)
