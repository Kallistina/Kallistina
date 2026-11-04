"""Draw the theme-switching header for the GitHub profile README.

Light mode: a GitHub-style round cat icon next to empty contribution squares.
Dark mode:  the same cat turned into a Pac-Man ("Pac-cat") about to eat green squares.
GitHub shows one or the other depending on the viewer's theme, so switching theme "transforms" it.
Run:  python3 make_paccat.py  ->  writes assets/paccat-light.svg and assets/paccat-dark.svg
"""
import math
import os

W, H = 600, 200
CX, CY, R = 110, 104, 70   # Pac-cat body
MOUTH = 34                 # half-angle of the open mouth, degrees

THEMES = {
    # Greens are GitHub's own contribution-graph colours for each theme.
    "light": dict(body="#ffcc2f", line="#e0a800", ear="#f2a7b5", eye="#1f2328", shine="#ffffff",
                  greens=("#9be9a8", "#40c463", "#30a14e", "#216e39")),
    "dark": dict(body="#ffcc2f", line="#e0a800", ear="#f2a7b5", eye="#0d1117", shine="#ffffff",
                 greens=("#0e4429", "#006d32", "#26a641", "#39d353")),
}


def point(angle_deg, radius=R):
    a = math.radians(angle_deg)
    return CX + radius * math.cos(a), CY - radius * math.sin(a)


def ear(a0, a1, c):
    """A pointy cat ear rising from the body between angles a0 and a1."""
    (x0, y0), (x1, y1) = point(a0, R - 4), point(a1, R - 4)
    mid = (a0 + a1) / 2
    tx, ty = point(mid, R + 34)
    ix, iy = point(mid, R + 22)
    (jx0, jy0), (jx1, jy1) = point(a0 + 6, R + 4), point(a1 - 6, R + 4)
    return (f'<path d="M{x0:.1f},{y0:.1f} L{tx:.1f},{ty:.1f} L{x1:.1f},{y1:.1f} Z" fill="{c["body"]}" stroke="{c["line"]}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M{jx0:.1f},{jy0:.1f} L{ix:.1f},{iy:.1f} L{jx1:.1f},{jy1:.1f} Z" fill="{c["ear"]}"/>')


def squares(colors):
    """Contribution squares in front of the cat, getting greener towards the far end."""
    out = ""
    for i, shade in enumerate((0, 1, 2, 3, 2, 3, 3)):
        out += f'<rect x="{200 + i * 52}" y="{CY - 18}" width="36" height="36" rx="7" fill="{colors[shade]}"/>'
    return out


def svg(body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
{body}
</svg>
'''


def build_icon():
    """GitHub-style round icon: a white cat silhouette with a curly tail inside a dark circle."""
    ink, white = "#1f2328", "#ffffff"
    cat = (f'<circle cx="{CX}" cy="{CY - 14}" r="27" fill="{white}"/>'
           f'<path d="M{CX - 25},{CY - 22} L{CX - 26},{CY - 56} L{CX - 6},{CY - 38} Z" fill="{white}"/>'
           f'<path d="M{CX + 25},{CY - 22} L{CX + 26},{CY - 56} L{CX + 6},{CY - 38} Z" fill="{white}"/>'
           f'<ellipse cx="{CX}" cy="{CY + 48}" rx="36" ry="42" fill="{white}"/>'
           f'<path d="M{CX - 28},{CY + 62} C{CX - 54},{CY + 62} {CX - 58},{CY + 26} {CX - 40},{CY + 16}" '
           f'fill="none" stroke="{white}" stroke-width="9" stroke-linecap="round"/>')
    body = (f'<defs><clipPath id="disc"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath></defs>'
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{ink}"/>'
            f'<g clip-path="url(#disc)">{cat}</g>'
            + squares(("#ebedf0",) * 4))
    return svg(body, "A round GitHub-style cat icon next to a row of empty contribution squares.")


def build(c):
    top_x, top_y = point(MOUTH)
    bot_x, bot_y = point(-MOUTH)
    body = (f'<path d="M{CX},{CY} L{top_x:.1f},{top_y:.1f} A{R},{R} 0 1 0 {bot_x:.1f},{bot_y:.1f} Z" '
            f'fill="{c["body"]}" stroke="{c["line"]}" stroke-width="3" stroke-linejoin="round"/>')
    tail = (f'<path d="M{CX - R + 10},{CY + 34} C{CX - R - 40},{CY + 40} {CX - R - 44},{CY - 10} {CX - R - 18},{CY - 20}" '
            f'fill="none" stroke="{c["line"]}" stroke-width="15" stroke-linecap="round"/>'
            f'<path d="M{CX - R + 10},{CY + 34} C{CX - R - 40},{CY + 40} {CX - R - 44},{CY - 10} {CX - R - 18},{CY - 20}" '
            f'fill="none" stroke="{c["body"]}" stroke-width="9" stroke-linecap="round"/>')
    ears = ear(118, 146, c) + ear(66, 94, c)
    face = (f'<circle cx="{CX + 6}" cy="{CY - 36}" r="10" fill="{c["eye"]}"/>'
            f'<circle cx="{CX + 9}" cy="{CY - 39}" r="3.4" fill="{c["shine"]}"/>')
    return svg(tail + ears + body + face + squares(c["greens"]),
               "A yellow Pac-Man with cat ears about to eat a row of green contribution squares.")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "paccat-light.svg"), "w") as f:
        f.write(build_icon())
    with open(os.path.join(out, "paccat-dark.svg"), "w") as f:
        f.write(build(THEMES["dark"]))
    print("wrote", out)
