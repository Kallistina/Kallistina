"""Draw the animated pixel-art banner for the GitHub profile README.

Run:  python3 make_runner.py   ->  writes assets/runner-light.svg and assets/runner-dark.svg
"""
import os

W, H = 900, 220
P = 4  # size of one "pixel"
GROUND = 176  # y of the road

# Sprites: one character per pixel, "." is transparent.
RUNNER_A = """
....HHHH....
...HHHHHH...
..HHSSSSH...
.HHHSSSS....
.HH.SSSS....
.H...SS.....
....TTTT....
...TTTTTT...
..S.TTTT.S..
.S..TTTT..S.
....PPPP....
....P..P....
...P....P...
..S......S..
.S........S.
KK........KK
"""
RUNNER_B = """
....HHHH....
...HHHHHH...
..HHSSSSH...
.HHHSSSS....
HH..SSSS....
H....SS.....
....TTTT....
...TTTTTT...
...STTTTS...
...STTTTS...
....PPPP....
.....PP.....
.....PS.....
....SS......
....S.......
....KK......
"""
CAT_A = """
..........O...O.
..........OWOOWO
O.........OWWWWO
OW........OWEWEO
.OW.......OWWNWO
..OWOOOOOOOWWWO.
..OWWWWWWWWWWWO.
...OWWWWWWWWWWO.
...OWO.....OWO..
..OO.......OO...
"""
CAT_B = """
..........O...O.
..........OWOOWO
O.........OWWWWO
OW........OWEWEO
.OW.......OWWNWO
..OWOOOOOOOWWWO.
..OWWWWWWWWWWWO.
...OWWWWWWWWWWO.
....OWO..OWO....
....OO....OO....
"""

BUG = """
...KK.
.RRKRR
RKRRKR
RRRRRR
.K.K.K
"""

# The bug crawls from the right edge to off-screen left once per loop;
# the cat and the runner jump while it passes under them.
LOOP = 5.0          # seconds per bug
BUG_FROM, BUG_TO = W + 10, -40
BUG_W = 6 * P


def jump_keyframes(name, x_left, x_right, height):
    """Keyframes that lift a sprite spanning [x_left, x_right] while the bug passes under it."""
    dist = BUG_FROM - BUG_TO
    enter = (BUG_FROM - x_right) / dist   # bug's left edge reaches the sprite's right edge
    leave = (BUG_FROM - (x_left - BUG_W)) / dist  # bug's right edge clears the sprite's left edge
    start, end = enter - 0.05, leave + 0.03
    frames = [f"0% {{ transform: translateY(0); }}", f"{start * 100:.2f}% {{ transform: translateY(0); }}"]
    for i in range(1, 8):
        u = i / 8
        y = -height * (1 - (2 * u - 1) ** 2)
        frames.append(f"{(start + u * (end - start)) * 100:.2f}% {{ transform: translateY({y:.1f}px); }}")
    frames.append(f"{end * 100:.2f}% {{ transform: translateY(0); }}")
    frames.append("100% { transform: translateY(0); }")
    return f"@keyframes {name} {{ " + " ".join(frames) + " }"


THEMES = {
    "light": dict(ink="#1c1b22", muted="#6b6875", accent="#5b3fa0", road="#c9c4d6",
                  hill="#ece7f6", temple="#d8cfee", cloud="#f1eff6",
                  H="#4a3426", S="#f0c6a4", T="#5b3fa0", P="#2b2833", K="#1c1b22",
                  R="#e5484d",
                  O="#a9a5b4", W="#eeedf3", E="#3f8f4f", N="#f2a7b5"),
    "dark": dict(ink="#e6edf3", muted="#9198a1", accent="#b9a5ec", road="#30363d",
                 hill="#1b1730", temple="#2c2549", cloud="#1a1f27",
                 H="#6b4a36", S="#f0c6a4", T="#9b82e0", P="#c9d1d9", K="#e6edf3",
                 R="#e5484d",
                 O="#d9dbe0", W="#f5f6f8", E="#3f8f4f", N="#f2a7b5"),
}


def sprite(art, x0, y0, colors):
    rects = []
    for r, row in enumerate(art.strip("\n").splitlines()):
        for c, ch in enumerate(row):
            if ch != ".":
                rects.append(f'<rect x="{x0 + c * P}" y="{y0 + r * P}" width="{P}" height="{P}" fill="{colors[ch]}"/>')
    return "".join(rects)


def acropolis(x, c):
    """A pixel Parthenon on a hill, with its left edge at x."""
    parts = [
        f'<path d="M{x},{GROUND} Q{x + 130},{GROUND - 70} {x + 260},{GROUND} Z" fill="{c["hill"]}"/>',
        f'<rect x="{x + 70}" y="{GROUND - 58}" width="120" height="6" fill="{c["temple"]}"/>',  # steps
        f'<rect x="{x + 76}" y="{GROUND - 64}" width="108" height="6" fill="{c["temple"]}"/>',
    ]
    for i in range(8):  # columns
        parts.append(f'<rect x="{x + 82 + i * 13}" y="{GROUND - 100}" width="6" height="36" fill="{c["temple"]}"/>')
    parts.append(f'<rect x="{x + 76}" y="{GROUND - 108}" width="108" height="8" fill="{c["temple"]}"/>')  # entablature
    parts.append(f'<path d="M{x + 72},{GROUND - 108} L{x + 130},{GROUND - 128} L{x + 188},{GROUND - 108} Z" fill="{c["temple"]}"/>')
    return "".join(parts)


def cloud(x, y, c):
    return (f'<rect x="{x}" y="{y}" width="48" height="8" fill="{c["cloud"]}"/>'
            f'<rect x="{x + 8}" y="{y - 8}" width="28" height="8" fill="{c["cloud"]}"/>')


def build(c):
    # Background layer is drawn twice side by side and slid left by one width, so it loops seamlessly.
    bg = acropolis(380, c) + cloud(120, 40, c) + cloud(560, 28, c) + cloud(780, 56, c)
    dashes = "".join(f'<rect x="{x}" y="{GROUND + 14}" width="16" height="3" fill="{c["road"]}"/>' for x in range(0, W, 48))
    rx, ry = 300, GROUND - 16 * P
    dx, dy = 372, GROUND - 10 * P
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Pixel-art Kalliopi and her white cat running past the Acropolis, jumping over bugs">
<style>
  .bg {{ animation: slide 24s linear infinite; }}
  .road {{ animation: road 0.9s linear infinite; }}
  .fa {{ animation: fa .36s steps(1) infinite; }}
  .fb {{ animation: fb .36s steps(1) infinite; }}
  .bob {{ animation: bob .36s steps(1) infinite; }}
  .bug {{ animation: crawl {LOOP}s linear infinite; }}
  .jr {{ animation: jr {LOOP}s linear infinite; }}
  .jc {{ animation: jc {LOOP}s linear infinite; }}
  @keyframes crawl {{ from {{ transform: translateX(0); }} to {{ transform: translateX({BUG_TO - BUG_FROM}px); }} }}
  {jump_keyframes("jr", rx, rx + 12 * P, 44)}
  {jump_keyframes("jc", dx, dx + 16 * P, 34)}
  @keyframes slide {{ to {{ transform: translateX(-{W}px); }} }}
  @keyframes road {{ to {{ transform: translateX(-48px); }} }}
  @keyframes fa {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
  @keyframes fb {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
  @keyframes bob {{ 0% {{ transform: translateY(0); }} 50% {{ transform: translateY(-{P}px); }} }}
  @media (prefers-reduced-motion: reduce) {{
    .bg, .road, .bob, .bug, .jr, .jc {{ animation: none; }}
    .fa {{ animation: none; opacity: 1; }}
    .fb {{ animation: none; opacity: 0; }}
  }}
</style>
<g class="bg">{bg}<g transform="translate({W},0)">{bg}</g></g>
<rect x="0" y="{GROUND}" width="{W}" height="3" fill="{c["road"]}"/>
<g class="road">{dashes}<g transform="translate({W},0)">{dashes}</g></g>
<g class="bug">{sprite(BUG, BUG_FROM, GROUND - 5 * P, c)}</g>
<g class="jr"><g class="bob">
  <g class="fa">{sprite(RUNNER_A, rx, ry, c)}</g>
  <g class="fb">{sprite(RUNNER_B, rx, ry, c)}</g>
</g></g>
<g class="jc">
  <g class="fb">{sprite(CAT_A, dx, dy, c)}</g>
  <g class="fa">{sprite(CAT_B, dx, dy, c)}</g>
</g>
<text x="12" y="{H - 6}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15" fill="{c["muted"]}">running marathons, fuzzers &amp; federated models</text>
</svg>
'''


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(out, exist_ok=True)
    for name, colors in THEMES.items():
        with open(os.path.join(out, f"runner-{name}.svg"), "w") as f:
            f.write(build(colors))
    print("wrote", out)
