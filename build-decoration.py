#!/usr/bin/env python3
"""Generate the DaedricMorrowind Aurorae window decoration.

    python3 decoration/build-decoration.py [out-dir] [theme-name]

Geometry is authored 1:1 in pixels. Each frame element is as big as the area
Aurorae gives it (shadow padding + border), so nothing is squeezed or tiled:
the whole title bar is the "top" element and the soft shadow lives in the
padding. Edges only use gradients that run across them, so they stretch clean.
No SVG filters: glows are layered translucent strokes and radial gradients.
"""
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".local/share/aurorae/themes/DaedricMorrowind"
NAME = sys.argv[2] if len(sys.argv) > 2 else OUT.name

P = 18          # shadow padding on every side
B = 5           # side and bottom border
ET, TH, EB = 5, 30, 9   # title edge top, title height, title edge bottom
T = ET + TH + EB        # title bar height
C = 40          # stretchable centre in the template
BTN = 24

W = P + B + C + B + P
H = P + T + C + B + P
X0, X1 = P, W - P            # window left / right edge
Y0, Y1 = P, H - P            # window top / bottom edge
XL, XR = P + B, W - P - B    # centre left / right
YT, YB = P + T, H - P - B    # centre top / bottom

VOID, BASALT = "#060505", "#150c0b"
# Ashlander: weathered bronze, ash-bone, dried blood (the brass/gold version is build-decoration.v2-brass.py)
BRASS, BRASS_HI, BRASS_LO = "#5e3d30", "#6f4a3a", "#2e1d18"
BONE, PEACH, EMBER, FLAME, BLOOD = "#a89a84", "#c2633c", "#963724", "#6e1a13", "#330b0a"
ASH, ASH_LO = "#383533", "#1d1c1b"


def stops(*s):
    return "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in s)


def defs():
    sh = lambda tint: ((0, "#000", 0.50), (0.18, tint, 0.34), (0.45, "#000", 0.13), (0.75, "#000", 0.04), (1, "#000", 0))
    out = ["<defs>"]
    for key, tint in (("a", "#120505"), ("i", "#000")):
        s = stops(*sh(tint))
        out += [
            f'<linearGradient id="sh{key}L" x1="1" y1="0" x2="0" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}R" x1="0" y1="0" x2="1" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}T" x1="0" y1="1" x2="0" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}B" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient>',
        ]
        for corner, cx, cy in (("TL", X0, Y0), ("TR", X1, Y0), ("BL", X0, Y1), ("BR", X1, Y1)):
            out.append(f'<radialGradient id="sh{key}{corner}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{P}">{s}</radialGradient>')
    out += [
        # title bar stone, top to bottom
        f'<linearGradient id="barA" x1="0" y1="0" x2="0" y2="1">{stops((0, "#2b1412", 1), (0.5, "#190d0c", 1), (1, "#0c0707", 1))}</linearGradient>',
        f'<linearGradient id="barI" x1="0" y1="0" x2="0" y2="1">{stops((0, "#1a1919", 1), (1, "#0d0d0d", 1))}</linearGradient>',
        # ember seam under the title: a soft bloom with a thin hot core
        f'<linearGradient id="seam" x1="0" y1="0" x2="0" y2="1">{stops((0, BLOOD, 0), (0.45, BLOOD, 0.22), (0.78, FLAME, 0.38), (0.88, FLAME, 0.5), (1, "#0a0505", 1))}</linearGradient>',
        f'<linearGradient id="seamI" x1="0" y1="0" x2="0" y2="1">{stops((0, "#000", 0), (0.75, "#000", 0.35), (0.85, ASH, 0.8), (1, "#060504", 1))}</linearGradient>',
        f'<linearGradient id="stud" x1="0" y1="0" x2="1" y2="1">{stops((0, BONE, 1), (0.5, BRASS, 1), (1, BRASS_LO, 1))}</linearGradient>',
        "</defs>",
    ]
    return "\n".join(out)


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def title_strip(x, w, active, left_edge=False, right_edge=False):
    """A slice of the title bar from window top to the centre."""
    bar, seam, hair = ("barA", "seam", BRASS_HI) if active else ("barI", "seamI", ASH)
    o = [rect(x, Y0, w, T, f"url(#{bar})"),
         rect(x, Y0, w, 1, hair),
         rect(x, Y0 + 1, w, 1, BONE if active else "#fff", 'opacity="0.05"'),
         rect(x, YT - 9, w, 9, f"url(#{seam})")]
    if left_edge:
        o.append(rect(x, Y0, 1, T, hair))
    if right_edge:
        o.append(rect(x + w - 1, Y0, 1, T, hair))
    return o


def side_strip(x, y, h, active, outer_left):
    hair = BRASS if active else ASH
    o = [rect(x, y, B, h, BASALT if active else "#121111")]
    o.append(rect(x if outer_left else x + B - 1, y, 1, h, hair))
    o.append(rect(x + B - 1 if outer_left else x, y, 1, h, "#060504"))
    return o


def bottom_strip(x, w, active):
    hair = BRASS if active else ASH
    return [rect(x, YB, w, B, BASALT if active else "#121111"),
            rect(x, YB, w, 1, "#060504"),
            rect(x, Y1 - 1, w, 1, hair)]


def stud(cx, cy, active):
    r = 4
    d = f"M{cx},{cy - r} L{cx + r},{cy} L{cx},{cy + r} L{cx - r},{cy} Z"
    if not active:
        return [f'<path d="{d}" fill="{ASH_LO}" stroke="{ASH}" stroke-width="1"/>']
    # stays inside the corner element's box: anything wider would rescale the corner
    return [f'<path d="{d}" fill="url(#stud)" stroke="#060504" stroke-width="0.8"/>',
            f'<circle cx="{cx}" cy="{cy}" r="1.3" fill="{EMBER}"/>']


def frame(prefix, active):
    k = "a" if active else "i"
    g = {}
    g["center"] = [rect(XL, YT, C, C, "#080707")]
    g["top"] = [rect(XL, 0, C, P, f"url(#sh{k}T)")] + title_strip(XL, C, active)
    g["bottom"] = [rect(XL, Y1, C, P, f"url(#sh{k}B)")] + bottom_strip(XL, C, active)
    g["left"] = [rect(0, YT, P, C, f"url(#sh{k}L)")] + side_strip(X0, YT, C, active, True)
    g["right"] = [rect(X1, YT, P, C, f"url(#sh{k}R)")] + side_strip(XL + C, YT, C, active, False)
    g["topleft"] = ([rect(0, 0, P, P, f"url(#sh{k}TL)"), rect(P, 0, B, P, f"url(#sh{k}T)"), rect(0, P, P, T, f"url(#sh{k}L)")]
                    + title_strip(X0, B, active, left_edge=True) + stud(X0 + 0.5, Y0 + 0.5, active))
    g["topright"] = ([rect(X1, 0, P, P, f"url(#sh{k}TR)"), rect(XR, 0, B, P, f"url(#sh{k}T)"), rect(X1, P, P, T, f"url(#sh{k}R)")]
                     + title_strip(XR, B, active, right_edge=True) + stud(X1 - 0.5, Y0 + 0.5, active))
    g["bottomleft"] = ([rect(0, Y1, P, P, f"url(#sh{k}BL)"), rect(P, Y1, B, P, f"url(#sh{k}B)"), rect(0, YB, P, B, f"url(#sh{k}L)")]
                       + side_strip(X0, YB, B, active, True) + [rect(X0, Y1 - 1, B, 1, BRASS if active else ASH)]
                       + stud(X0 + 0.5, Y1 - 0.5, active))
    g["bottomright"] = ([rect(X1, Y1, P, P, f"url(#sh{k}BR)"), rect(XR, Y1, B, P, f"url(#sh{k}B)"), rect(X1, YB, P, B, f"url(#sh{k}R)")]
                        + side_strip(XR, YB, B, active, False) + [rect(XR, Y1 - 1, B, 1, BRASS if active else ASH)]
                        + stud(X1 - 0.5, Y1 - 0.5, active))
    return "\n".join(f'<g id="{prefix}-{n}">\n' + "\n".join(v) + "\n</g>" for n, v in g.items())


def masks():
    boxes = {"center": (XL, YT, C, C), "top": (XL, Y0, C, T), "bottom": (XL, YB, C, B), "left": (X0, YT, B, C),
             "right": (XR, YT, B, C), "topleft": (X0, Y0, B, T), "topright": (XR, Y0, B, T),
             "bottomleft": (X0, YB, B, B), "bottomright": (XR, YB, B, B)}
    # each mask element keeps the full element size; only the window part is opaque
    full = {"center": (XL, YT, C, C), "top": (XL, 0, C, P + T), "bottom": (XL, YB, C, B + P), "left": (0, YT, P + B, C),
            "right": (XR, YT, B + P, C), "topleft": (0, 0, P + B, P + T), "topright": (XR, 0, B + P, P + T),
            "bottomleft": (0, YB, P + B, B + P), "bottomright": (XR, YB, B + P, B + P)}
    out = []
    for n in boxes:
        hidden = 'opacity="0"'
        out.append(f'<g id="mask-{n}">{rect(*full[n], "#000", hidden)}{rect(*boxes[n], "#fff")}</g>')
    return "\n".join(out)


def maximized(prefix, active):
    # centre-only frame stretched over the title bar; authored at title-bar height
    return (f'<g id="{prefix}-center">' + "".join(
        s.replace(f'y="{Y0}"', 'y="0"').replace(f'y="{Y0 + 1}"', 'y="1"').replace(f'y="{YT - 9}"', f'y="{T - 9}"')
        for s in title_strip(0, C, active)) + "</g>")


def decoration_svg():
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        defs(), frame("decoration", True), frame("decoration-inactive", False), masks(),
        f'<rect id="hint-stretch-borders" x="0" y="0" width="1" height="1" fill="none"/>',
        # Aurorae stretches the maximized centre over the whole window height; tiling it
        # at its natural size instead keeps the title bar art 1:1 in the visible strip
        '<rect id="decoration-maximized-hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>',
        '<rect id="decoration-maximized-inactive-hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>',
        "</svg>"])


def maximized_svg_groups():
    # kept in the same file but outside the frame's coordinate system
    return maximized("decoration-maximized", True) + "\n" + maximized("decoration-maximized-inactive", False)


# ---- buttons -----------------------------------------------------------------
M = BTN / 2
GLYPHS = {
    "close":       f"M{M-4},{M-4} L{M+4},{M+4} M{M+4},{M-4} L{M-4},{M+4}",
    "minimize":    f"M{M-4.5},{M+2.5} L{M+4.5},{M+2.5}",
    "maximize":    f"M{M},{M-4.5} L{M+4.5},{M} L{M},{M+4.5} L{M-4.5},{M} Z",
    "restore":     f"M{M-1.5},{M-3.5} L{M+2},{M} L{M-1.5},{M+3.5} L{M-5},{M} Z M{M+1.5},{M-3.5} L{M+5},{M} L{M+1.5},{M+3.5}",
    "keepabove":   f"M{M-4},{M+1.5} L{M},{M-3} L{M+4},{M+1.5} M{M-2.5},{M+4.5} L{M+2.5},{M+4.5}",
    "keepbelow":   f"M{M-4},{M-1.5} L{M},{M+3} L{M+4},{M-1.5} M{M-2.5},{M-4.5} L{M+2.5},{M-4.5}",
    "shade":       f"M{M-4.5},{M-3.5} L{M+4.5},{M-3.5} M{M-3},{M+3.5} L{M},{M} L{M+3},{M+3.5}",
    "alldesktops": f"M{M},{M-1.8} L{M+1.8},{M} L{M},{M+1.8} L{M-1.8},{M} Z",
    # the ALMSIVI triangle
    "menu":        f"M{M},{M-4.5} L{M+4.5},{M+3.5} L{M-4.5},{M+3.5} Z",
}
DIAMOND = f"M{M},1.5 L{BTN-1.5},{M} L{M},{BTN-1.5} L1.5,{M} Z"


def button_state(ident, glyph, rim, fill, ink, glow=None, halo=0.0, core=None):
    o = [f'<g id="{ident}">', rect(0, 0, BTN, BTN, "#000", 'opacity="0"')]
    if halo:
        o.append(f'<circle cx="{M}" cy="{M}" r="{M}" fill="url(#halo)" opacity="{halo}"/>')
    o.append(f'<path d="{DIAMOND}" fill="{fill}" stroke="{rim}" stroke-width="1.1" stroke-linejoin="round"/>')
    common = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if glow:
        o.append(f'<path d="{glyph}" {common} stroke="{glow}" stroke-width="4.2" opacity="0.22"/>')
        o.append(f'<path d="{glyph}" {common} stroke="{glow}" stroke-width="2.8" opacity="0.38"/>')
    o.append(f'<path d="{glyph}" {common} stroke="{ink}" stroke-width="1.5"/>')
    if core:
        o.append(f'<circle cx="{M}" cy="{M + (1.2 if "L" in glyph and glyph is GLYPHS["menu"] else 0)}" r="1.1" fill="{core}"/>')
    o.append("</g>")
    return "\n".join(o)


def button_svg(name):
    g = GLYPHS[name]
    hot = name == "close"
    core = FLAME if name in ("menu", "close") else None
    d = ("<defs>"
         f'<linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">{stops((0, BONE, 1), (0.5, BRASS, 1), (1, BRASS_LO, 1))}</linearGradient>'
         f'<radialGradient id="well" cx="0.5" cy="0.4" r="0.6">{stops((0, "#1f100e", 1), (1, "#080505", 1))}</radialGradient>'
         f'<radialGradient id="wellHot" cx="0.5" cy="0.5" r="0.6">{stops((0, "#4e120d", 1), (1, "#170807", 1))}</radialGradient>'
         f'<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">{stops((0, FLAME, 0.9), (0.55, FLAME, 0.35), (1, FLAME, 0))}</radialGradient>'
         "</defs>")
    states = [
        button_state("active-center", g, "url(#rim)", "url(#well)", "#9c8f7c", glow=FLAME, core=core),
        button_state("hover-center", g, BONE, "url(#wellHot)" if hot else "url(#well)", "#d2c3a8", glow=EMBER, halo=0.75 if hot else 0.5, core=PEACH if core else None),
        button_state("pressed-center", g, FLAME, "url(#wellHot)", PEACH, glow=FLAME, halo=0.9),
        button_state("inactive-center", g, ASH, "#141210", "#4e4944"),
        button_state("hover-inactive-center", g, BRASS, "url(#well)", "#c9bca6", glow=EMBER, halo=0.3),
        button_state("pressed-inactive-center", g, EMBER, "url(#wellHot)", PEACH, halo=0.6),
        button_state("deactivated-center", g, ASH_LO, "#12100e", ASH),
        button_state("deactivated-inactive-center", g, ASH_LO, "#12100e", "#352e26"),
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{BTN}" height="{BTN}" viewBox="0 0 {BTN} {BTN}">\n'
            + d + "\n" + "\n".join(states) + "\n</svg>\n")


RC = f"""[General]
ActiveTextColor=168,154,132,255
InactiveTextColor=92,86,80,255
TitleAlignment=Left
TitleVerticalAlignment=Center
Animation=160
Shadow=true
TitleShadow=false
UseTextShadow=false

[Layout]
TitleHeight={TH}
TitleEdgeTop={ET}
TitleEdgeBottom={EB}
TitleEdgeLeft=9
TitleEdgeRight=9
TitleEdgeTopMaximized={ET}
TitleEdgeBottomMaximized={EB}
TitleEdgeLeftMaximized=9
TitleEdgeRightMaximized=9
TitleBorderLeft=8
TitleBorderRight=8
ButtonWidth={BTN}
ButtonHeight={BTN}
ButtonSpacing=4
ButtonMarginTop={(TH - BTN) // 2}
ButtonMarginTopMaximized={(TH - BTN) // 2}
ExplicitButtonSpacer=8
PaddingLeft={P}
PaddingRight={P}
PaddingTop={P}
PaddingBottom={P}
BorderLeft={B}
BorderRight={B}
BorderBottom={B}
CornerRadius=0
BorderRadius=0
"""

META = f"""[Desktop Entry]
Name={NAME}
Comment=Near-black oxblood shrine frame: dim bronze hairlines, a faint red seam under the title, diamond corner studs, soft shadow, softly glowing diamond buttons.
Type=Service
X-KDE-ServiceTypes=AuroraeTheme
X-KDE-Library=aurorae
X-KDE-Aurorae-Corner-Radius=0
X-KDE-PluginInfo-Author=splicer scorn (voidrane)
X-KDE-PluginInfo-Version=2.0
X-KDE-PluginInfo-License=GPL-3.0-or-later
X-KDE-PluginInfo-Website=https://github.com/numbpill3d/daedric-morrowind-aurorae
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    svg = decoration_svg().replace("</svg>", maximized_svg_groups() + "\n</svg>")
    (OUT / "decoration.svg").write_text(svg)
    for name in GLYPHS:
        (OUT / f"{name}.svg").write_text(button_svg(name))
    (OUT / f"{NAME}rc").write_text(RC)
    (OUT / "metadata.desktop").write_text(META)
    stale = OUT / "masks.svg"
    if stale.exists():
        stale.unlink()   # masks now live in decoration.svg, where Aurorae reads them
    print("wrote", OUT)
