"""Draw the theme-switching Octocat-style header for the GitHub profile README.

Light mode: "Pac-Octocat", a yellow cat-octopus next to Pac-Man pellets.
Dark mode:  the same cat turned into a Pac-Man ghost.
GitHub shows one or the other depending on the viewer's theme (like the Octodex example).
Run:  python3 make_octo.py  ->  writes assets/octo-light.svg and assets/octo-dark.svg
"""
import os

W, H = 400, 400

# Cat head with two pointy ears, shared by both characters so the switch reads as a transformation.
HEAD = ("M80,175 C70,120 85,80 100,40 L155,85 Q200,72 245,85 L300,40 "
        "C315,80 330,120 320,175")


def svg(body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
{body}
</svg>
'''


def pellets(color):
    return "".join(f'<circle cx="{x}" cy="362" r="{r}" fill="{color}"/>' for x, r in ((318, 7), (350, 7), (382, 12)))


def pac_octocat():
    yellow, edge, face, iris, ink = "#ffcc2f", "#e0a800", "#f6d2b4", "#7a4434", "#3a2a22"
    head = f'<path d="{HEAD} C315,250 260,280 200,280 C140,280 85,250 80,175 Z" fill="{yellow}" stroke="{edge}" stroke-width="4"/>'
    inner_ears = (f'<path d="M108,62 L146,92 L118,112 Z" fill="#f2a7b5"/>'
                  f'<path d="M292,62 L254,92 L282,112 Z" fill="#f2a7b5"/>')
    face_patch = (f'<path d="M120,178 C120,132 160,116 200,116 C240,116 280,132 280,178 '
                  f'C280,232 245,256 200,256 C155,256 120,232 120,178 Z" fill="{face}"/>')
    eyes = ""
    for x in (160, 240):
        eyes += (f'<ellipse cx="{x}" cy="182" rx="22" ry="28" fill="#ffffff"/>'
                 f'<circle cx="{x + 3}" cy="188" r="13" fill="{iris}"/>'
                 f'<circle cx="{x + 8}" cy="182" r="4" fill="#ffffff"/>')
    nose_mouth = (f'<circle cx="200" cy="214" r="5" fill="{iris}"/>'
                  f'<path d="M186,230 Q200,240 214,230" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
    torso = f'<path d="M152,262 C146,296 150,316 162,326 L238,326 C250,316 254,296 248,262 Z" fill="{yellow}" stroke="{edge}" stroke-width="4"/>'
    tentacles = ""
    for d in ("M165,318 C150,345 120,350 110,330", "M184,322 C180,350 170,360 158,357",
              "M216,322 C220,350 230,360 242,357", "M235,318 C250,345 280,350 290,330",
              "M126,250 C100,262 82,246 78,226", "M274,250 C300,262 318,246 322,226"):
        tentacles += (f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="24" stroke-linecap="round"/>'
                      f'<path d="{d}" fill="none" stroke="{yellow}" stroke-width="17" stroke-linecap="round"/>')
    shadow = '<ellipse cx="200" cy="364" rx="120" ry="18" fill="#e9e3cf"/>'
    # Little Pac-Man badge on the chest.
    badge = '<path d="M200,298 L213,291 A15,15 0 1 0 213,305 Z" fill="#ffffff" stroke="#e0a800" stroke-width="2.5" stroke-linejoin="round"/>'
    body = shadow + pellets("#e0a800") + tentacles + torso + badge + head + inner_ears + face_patch + eyes + nose_mouth
    return svg(body, "Pac-Octocat: a yellow cat-octopus character next to Pac-Man pellets.")


def ghost_octocat():
    red, edge = "#ff4d4d", "#d62f3a"
    # Same head, but the body drops straight down into the ghost's wavy edge.
    skirt = " ".join(f"L{x},{y}" for x, y in ((320, 336), (294, 312), (267, 336), (240, 312), (214, 336),
                                               (187, 312), (160, 336), (133, 312), (107, 336), (80, 312)))
    ghost = f'<path d="{HEAD} L320,336 {skirt} Z" fill="{red}" stroke="{edge}" stroke-width="4" stroke-linejoin="round"/>'
    inner_ears = (f'<path d="M108,62 L146,92 L118,112 Z" fill="#ff8a8a"/>'
                  f'<path d="M292,62 L254,92 L282,112 Z" fill="#ff8a8a"/>')
    eyes = ""
    for x in (152, 248):  # classic ghost eyes, glancing to the side
        eyes += (f'<ellipse cx="{x}" cy="176" rx="32" ry="40" fill="#ffffff"/>'
                 f'<circle cx="{x + 13}" cy="186" r="16" fill="#2a3cff"/>')
    shadow = '<ellipse cx="200" cy="364" rx="120" ry="18" fill="#30363d"/>'
    body = shadow + pellets("#ffcc2f") + ghost + inner_ears + eyes
    return svg(body, "The same cat turned into a red Pac-Man ghost.")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "octo-light.svg"), "w") as f:
        f.write(pac_octocat())
    with open(os.path.join(out, "octo-dark.svg"), "w") as f:
        f.write(ghost_octocat())
    print("wrote", out)
