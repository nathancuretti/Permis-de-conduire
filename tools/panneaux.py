#!/usr/bin/env python3
"""Génère les panneaux et schémas SVG de l'appli (img/panneaux, img/schemas).

Dessins simplifiés d'après la nomenclature officielle française (IISR).
Usage : python3 tools/panneaux.py
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_P = os.path.join(ROOT, "img", "panneaux")
OUT_S = os.path.join(ROOT, "img", "schemas")

RED = "#d0101b"
BLUE = "#1a56b0"
YEL = "#f7c600"
BLK = "#1a1a1a"
WHT = "#ffffff"
GRY = "#8a8a8a"


def svg(body, vb="0 0 100 100"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>\n'


# ---------- formes de base ----------
def tri(inner="", bg=WHT):
    """Triangle de danger, pointe en haut, liseré rouge."""
    return (f'<polygon points="50,9 93,85 7,85" fill="{bg}" stroke="{RED}" stroke-width="9" '
            f'stroke-linejoin="round"/>' + inner)


def tri_inv(inner=""):
    return (f'<polygon points="7,14 93,14 50,90" fill="{WHT}" stroke="{RED}" stroke-width="9" '
            f'stroke-linejoin="round"/>' + inner)


def rond_rouge(inner="", bg=WHT):
    return f'<circle cx="50" cy="50" r="43" fill="{bg}" stroke="{RED}" stroke-width="10"/>' + inner


def rond_bleu(inner=""):
    return (f'<circle cx="50" cy="50" r="47" fill="{WHT}"/>'
            f'<circle cx="50" cy="50" r="44" fill="{BLUE}"/>' + inner)


def rond_fin(inner=""):
    return (f'<circle cx="50" cy="50" r="46" fill="{WHT}" stroke="{BLK}" stroke-width="1.5"/>' + inner)


def carre_bleu(inner=""):
    return (f'<rect x="4" y="4" width="92" height="92" rx="8" fill="{WHT}"/>'
            f'<rect x="7" y="7" width="86" height="86" rx="6" fill="{BLUE}"/>' + inner)


def text(t, x=50, y=50, size=30, fill=BLK, weight="bold", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{t}</text>')


def barre_fin(color=BLK, w=6):
    """Barre oblique des panneaux de fin."""
    return f'<line x1="22" y1="82" x2="78" y2="18" stroke="{color}" stroke-width="{w}"/>'


def barre_interdit(w=8):
    return f'<line x1="21" y1="21" x2="79" y2="79" stroke="{RED}" stroke-width="{w}"/>'


# ---------- pictogrammes ----------
def personne(x, y, s=1.0, c=BLK, pas=True):
    """Silhouette de piéton (x, y = pieds), hauteur ~ 34*s."""
    h = 34 * s
    head = f'<circle cx="{x}" cy="{y - h + 4*s}" r="{4.2*s}" fill="{c}"/>'
    body = f'<line x1="{x}" y1="{y - h + 9*s}" x2="{x}" y2="{y - 13*s}" stroke="{c}" stroke-width="{5*s}" stroke-linecap="round"/>'
    if pas:
        legs = (f'<line x1="{x}" y1="{y - 13*s}" x2="{x - 7*s}" y2="{y}" stroke="{c}" stroke-width="{4*s}" stroke-linecap="round"/>'
                f'<line x1="{x}" y1="{y - 13*s}" x2="{x + 6*s}" y2="{y}" stroke="{c}" stroke-width="{4*s}" stroke-linecap="round"/>')
        arms = (f'<line x1="{x}" y1="{y - h + 11*s}" x2="{x - 7*s}" y2="{y - 17*s}" stroke="{c}" stroke-width="{3.2*s}" stroke-linecap="round"/>'
                f'<line x1="{x}" y1="{y - h + 11*s}" x2="{x + 7*s}" y2="{y - 18*s}" stroke="{c}" stroke-width="{3.2*s}" stroke-linecap="round"/>')
    else:
        legs = (f'<line x1="{x}" y1="{y - 13*s}" x2="{x - 3*s}" y2="{y}" stroke="{c}" stroke-width="{4*s}" stroke-linecap="round"/>'
                f'<line x1="{x}" y1="{y - 13*s}" x2="{x + 3*s}" y2="{y}" stroke="{c}" stroke-width="{4*s}" stroke-linecap="round"/>')
        arms = ""
    return head + body + legs + arms


def velo(x, y, s=1.0, c=BLK, cycliste=True):
    """Bicyclette de profil, (x, y) = centre bas."""
    r = 7 * s
    lw = 2.6 * s
    w1x, w2x, wy = x - 11*s, x + 11*s, y - r
    g = (f'<circle cx="{w1x}" cy="{wy}" r="{r}" fill="none" stroke="{c}" stroke-width="{lw}"/>'
         f'<circle cx="{w2x}" cy="{wy}" r="{r}" fill="none" stroke="{c}" stroke-width="{lw}"/>'
         f'<polyline points="{w1x},{wy} {x - 2*s},{wy} {x + 6*s},{wy - 10*s} {w2x},{wy}" fill="none" stroke="{c}" stroke-width="{lw}" stroke-linejoin="round"/>'
         f'<line x1="{x - 2*s}" y1="{wy}" x2="{x - 5*s}" y2="{wy - 11*s}" stroke="{c}" stroke-width="{lw}"/>'
         f'<line x1="{x + 6*s}" y1="{wy - 10*s}" x2="{x + 7*s}" y2="{wy - 14*s}" stroke="{c}" stroke-width="{lw}"/>')
    if cycliste:
        g += (f'<circle cx="{x}" cy="{wy - 25*s}" r="{3.6*s}" fill="{c}"/>'
              f'<polyline points="{x - 5*s},{wy - 12*s} {x - 2*s},{wy - 21*s} {x + 7*s},{wy - 14*s}" fill="none" stroke="{c}" stroke-width="{4*s}" stroke-linejoin="round" stroke-linecap="round"/>'
              f'<line x1="{x - 5*s}" y1="{wy - 12*s}" x2="{x - 1*s}" y2="{wy - 2*s}" stroke="{c}" stroke-width="{3*s}" stroke-linecap="round"/>')
    return g


def voiture_face(x, y, s=1.0, c=BLK):
    """Voiture vue de face/arrière, (x, y) = centre bas."""
    w, h = 26 * s, 18 * s
    return (f'<path d="M{x - w/2},{y - 4*s} v{-h*0.45} l{4*s},{-h*0.45} h{w - 8*s} l{4*s},{h*0.45} v{h*0.45} z" fill="{c}"/>'
            f'<rect x="{x - w/2 + 1*s}" y="{y - 5*s}" width="{5*s}" height="{5*s}" fill="{c}"/>'
            f'<rect x="{x + w/2 - 6*s}" y="{y - 5*s}" width="{5*s}" height="{5*s}" fill="{c}"/>'
            f'<rect x="{x - w/2 + 6*s}" y="{y - h*0.85}" width="{w - 12*s}" height="{h*0.32}" fill="{WHT}"/>')


def fleche(d, c=WHT, w=9, head=12):
    """Trait épais + pointe : d = liste de points, la pointe est au dernier."""
    import math
    (x1, y1), (x2, y2) = d[-2], d[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * 0.9 * math.cos(a), y2 - head * 0.9 * math.sin(a)
    pts = " ".join(f"{x},{y}" for x, y in d[:-1]) + f" {bx},{by}"
    lx, ly = bx + head * math.cos(a + math.pi / 2), by + head * math.sin(a + math.pi / 2)
    rx, ry = bx + head * math.cos(a - math.pi / 2), by + head * math.sin(a - math.pi / 2)
    return (f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"/>'
            f'<polygon points="{x2},{y2} {lx},{ly} {rx},{ry}" fill="{c}"/>')


# ---------- catalogue des panneaux ----------
P = {}

# Danger (A)
P["A1a"] = tri(f'<path d="M42,77 V60 Q42,46 58,44" fill="none" stroke="{BLK}" stroke-width="8"/>')
P["A1b"] = tri(f'<path d="M58,77 V60 Q58,46 42,44" fill="none" stroke="{BLK}" stroke-width="8"/>')
P["A1c"] = tri(f'<path d="M40,77 V66 Q40,58 50,56 Q60,54 60,46 V36" fill="none" stroke="{BLK}" stroke-width="7"/>')
P["A2b"] = tri(f'<path d="M22,74 H34 Q50,52 66,74 H78" fill="{BLK}" stroke="{BLK}" stroke-width="3"/>')
P["A3"] = tri(f'<path d="M36,78 Q36,62 44,56 V38 M64,78 Q64,62 56,56 V38" fill="none" stroke="{BLK}" stroke-width="6"/>')
P["A3a"] = tri(f'<path d="M40,78 V38 M64,78 Q64,62 54,56 V38" fill="none" stroke="{BLK}" stroke-width="6"/>')
P["A4"] = tri(voiture_face(50, 58, 0.95) +
              f'<path d="M36,78 q4,-6 0,-12 M64,78 q-4,-6 0,-12" fill="none" stroke="{BLK}" stroke-width="3.5"/>')
P["A7"] = tri(f'<rect x="24" y="56" width="52" height="9" fill="{BLK}"/>'
              f'<rect x="28" y="65" width="4" height="13" fill="{BLK}"/><rect x="68" y="65" width="4" height="13" fill="{BLK}"/>'
              + "".join(f'<rect x="{30 + i*8}" y="57" width="4" height="7" fill="{WHT}"/>' for i in range(5)))
P["A8"] = tri(f'<rect x="28" y="58" width="30" height="14" fill="{BLK}"/><rect x="54" y="48" width="14" height="24" fill="{BLK}"/>'
              f'<rect x="32" y="50" width="6" height="8" fill="{BLK}"/><rect x="24" y="68" width="48" height="4" fill="{BLK}"/>'
              f'<circle cx="35" cy="76" r="4" fill="{BLK}"/><circle cx="48" cy="76" r="4" fill="{BLK}"/><circle cx="62" cy="76" r="4" fill="{BLK}"/>')
P["A13a"] = tri(personne(42, 79, 0.95) + personne(58, 79, 0.75))
P["A13b"] = tri(personne(50, 74, 0.9) +
                "".join(f'<rect x="{25 + i*10}" y="76" width="6" height="5" fill="{BLK}"/>' for i in range(6)))
P["A14"] = tri(f'<rect x="45" y="38" width="10" height="28" rx="2" fill="{BLK}"/><circle cx="50" cy="74" r="5.5" fill="{BLK}"/>')
P["A15b"] = tri(f'<path d="M26,78 L30,62 Q32,56 40,56 H58 L64,48 L62,42 L67,40 L70,46 L76,50 L74,54 L68,54 L66,62 L70,78 H66 L62,66 H44 L38,78 H34 L36,66 L32,68 L30,78 Z" fill="{BLK}"/>'
                f'<path d="M64,48 L60,36 M62,40 L56,34 M68,42 L72,32 M70,38 L76,34" stroke="{BLK}" stroke-width="2.5" fill="none"/>')
P["A17"] = tri(f'<rect x="40" y="35" width="20" height="46" rx="4" fill="{BLK}"/>'
               f'<circle cx="50" cy="44" r="5.5" fill="{RED}"/><circle cx="50" cy="58" r="5.5" fill="#f2a900"/><circle cx="50" cy="72" r="5.5" fill="#1a9c3c"/>')
P["A18"] = tri(fleche([(40, 80), (40, 40)], BLK, 6, 9) + fleche([(60, 40), (60, 80)], BLK, 6, 9))
P["A20"] = tri(f'<polygon points="22,48 78,78 22,78" fill="{BLK}"/>' + text("10%", 58, 56, 13))
P["A21"] = tri(velo(50, 80, 1.0))
P["A24"] = tri(f'<rect x="28" y="40" width="4" height="40" fill="{BLK}"/>'
               f'<polygon points="32,42 72,50 72,58 32,62" fill="{RED}" stroke="{BLK}" stroke-width="1.5"/>'
               f'<polygon points="45,44.6 55,46.6 55,59.6 45,60.6" fill="{WHT}"/><polygon points="63,48.2 72,50 72,58 63,58.8" fill="{WHT}"/>')
P["AK5"] = tri(personne(44, 78, 0.9, pas=False) +
               f'<line x1="50" y1="56" x2="66" y2="76" stroke="{BLK}" stroke-width="3"/>'
               f'<path d="M58,80 Q66,66 78,80 Z" fill="{BLK}"/>', bg=YEL)

# Intersection et priorité (AB)
P["AB1"] = tri(f'<path d="M34,46 L66,78 M66,46 L34,78" stroke="{BLK}" stroke-width="8"/>')
P["AB2"] = tri(f'<rect x="44" y="34" width="12" height="48" fill="{BLK}"/><rect x="28" y="56" width="44" height="6" fill="{BLK}"/>')
P["AB3a"] = tri_inv()
P["AB4"] = (f'<polygon points="30,3 70,3 97,30 97,70 70,97 30,97 3,70 3,30" fill="{WHT}"/>'
            f'<polygon points="31.5,7 68.5,7 93,31.5 93,68.5 68.5,93 31.5,93 7,68.5 7,31.5" fill="{RED}"/>'
            + text("STOP", 50, 51, 27, WHT))
P["AB6"] = (f'<polygon points="50,3 97,50 50,97 3,50" fill="{WHT}" stroke="{BLK}" stroke-width="1.5"/>'
            f'<polygon points="50,18 82,50 50,82 18,50" fill="{YEL}"/>')
P["AB7"] = P["AB6"] + '<line x1="27" y1="73" x2="73" y2="27" stroke="#222" stroke-width="7"/>'
def giratoire(cx=50, cy=62, r=13, c=BLK, w=4.5):
    """Trois flèches tournant dans le sens inverse des aiguilles d'une montre (vu sur l'écran)."""
    import math
    out = ""
    for k in range(3):
        a0 = math.radians(90 + k * 120 + 15)
        a1 = a0 - math.radians(75)          # sens antihoraire à l'écran (y vers le bas)
        pts = [(cx + r * math.cos(a0 - t * (a0 - a1) / 6), cy + r * math.sin(a0 - t * (a0 - a1) / 6)) for t in range(7)]
        out += fleche([(round(x, 1), round(y, 1)) for x, y in pts], c, w, 6)
    return out


P["AB25"] = tri(giratoire())

# Interdiction (B)
P["B0"] = rond_rouge()
P["B1"] = (f'<circle cx="50" cy="50" r="47" fill="{WHT}"/><circle cx="50" cy="50" r="44" fill="{RED}"/>'
           f'<rect x="18" y="42" width="64" height="16" fill="{WHT}"/>')
P["B2a"] = rond_rouge(fleche([(56, 74), (56, 48), (34, 48)], BLK, 8, 11) + barre_interdit())
P["B2b"] = rond_rouge(fleche([(44, 74), (44, 48), (66, 48)], BLK, 8, 11) + barre_interdit())
P["B2c"] = rond_rouge(f'<path d="M58,76 V44 A10,10 0 0 0 38,44 V54" fill="none" stroke="{BLK}" stroke-width="7"/>'
                      f'<polygon points="30,52 46,52 38,66" fill="{BLK}"/>' + barre_interdit())
P["B3"] = rond_rouge(voiture_face(36, 68, 0.9, RED) + voiture_face(64, 68, 0.9, BLK))
P["B6a1"] = (f'<circle cx="50" cy="50" r="43" fill="{BLUE}" stroke="{RED}" stroke-width="10"/>'
             f'<line x1="21" y1="21" x2="79" y2="79" stroke="{RED}" stroke-width="10"/>')
P["B6d"] = P["B6a1"] + f'<line x1="79" y1="21" x2="21" y2="79" stroke="{RED}" stroke-width="10"/>'
for v in (30, 50, 70, 80, 90, 110, 130):
    P[f"B14-{v}"] = rond_rouge(text(str(v), 50, 52, 38 if v < 100 else 31))
P["B16"] = rond_rouge(f'<path d="M30,44 h10 l14,-10 v32 l-14,-10 h-10 z" fill="{BLK}"/>'
                      f'<path d="M60,40 q6,10 0,20 M66,36 q9,14 0,28" fill="none" stroke="{BLK}" stroke-width="3"/>' + barre_interdit())
P["B9b"] = rond_rouge(velo(50, 72, 1.1))

# Fin d'interdiction
P["B31"] = rond_fin('<defs><clipPath id="c"><circle cx="50" cy="50" r="45"/></clipPath></defs><g clip-path="url(#c)">'
                    + "".join(f'<line x1="{8 + i*6}" y1="92" x2="{56 + i*6}" y2="8" stroke="{GRY}" stroke-width="2.6"/>' for i in range(-3, 4))
                    + '</g>')
for v in (30, 50, 70, 90, 110):
    P[f"B33-{v}"] = rond_fin(text(str(v), 50, 52, 36 if v < 100 else 30, GRY) +
                             f'<line x1="18" y1="84" x2="84" y2="18" stroke="{BLK}" stroke-width="5"/>')
P["B34"] = rond_fin(voiture_face(36, 68, 0.9, GRY) + voiture_face(64, 68, 0.9, GRY) + barre_fin(BLK, 5))

# Obligation
P["B21-1"] = rond_bleu(fleche([(42, 76), (42, 46), (74, 46)], WHT, 9, 13))
P["B21-2"] = rond_bleu(fleche([(58, 76), (58, 46), (26, 46)], WHT, 9, 13))
P["B21a1"] = rond_bleu(fleche([(30, 30), (68, 68)], WHT, 9, 13))
P["B21b"] = rond_bleu(fleche([(50, 80), (50, 22)], WHT, 9, 13))
P["B22a"] = rond_bleu(velo(50, 70, 1.15, WHT))
P["B25-30"] = rond_bleu(text("30", 50, 52, 40, WHT))
P["B40"] = rond_bleu(velo(50, 70, 1.15, WHT) + f'<line x1="18" y1="82" x2="82" y2="18" stroke="{RED}" stroke-width="7"/>')

# Indication (C) et zones
P["C1a"] = carre_bleu(text("P", 50, 53, 62, WHT))
P["C12"] = carre_bleu(fleche([(50, 84), (50, 18)], WHT, 12, 16))
P["C13a"] = carre_bleu(f'<rect x="43" y="34" width="14" height="52" fill="{WHT}"/><rect x="26" y="18" width="48" height="14" fill="{RED}"/>')
P["C20a"] = carre_bleu(f'<polygon points="50,14 88,84 12,84" fill="{WHT}"/>' + personne(50, 72, 0.9) +
                       "".join(f'<rect x="{30 + i*9}" y="74" width="5" height="5" fill="{BLK}"/>' for i in range(5)))
P["C24a"] = carre_bleu(f'<rect x="22" y="14" width="56" height="72" fill="{WHT}"/>' +
                       fleche([(40, 80), (40, 22)], BLK, 7, 10) + fleche([(60, 22), (60, 80)], BLK, 7, 10))


def rect_zone(inner, w=100, h=140, end=False):
    b = (f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="6" fill="{WHT}" stroke="{BLK}" stroke-width="2"/>' + inner)
    if end:
        b += f'<line x1="10" y1="{h - 10}" x2="{w - 10}" y2="10" stroke="{BLK}" stroke-width="6"/>'
    return b


P["B30"] = ("0 0 100 140", rect_zone(
    f'<circle cx="50" cy="52" r="34" fill="{WHT}" stroke="{RED}" stroke-width="8"/>' + text("30", 50, 54, 32) +
    text("ZONE", 50, 115, 24)))
P["B51"] = ("0 0 100 140", rect_zone(
    f'<circle cx="50" cy="52" r="34" fill="{WHT}" stroke="{GRY}" stroke-width="8"/>' + text("30", 50, 54, 32, GRY) +
    text("ZONE", 50, 115, 24, GRY), end=True))
P["B52"] = ("0 0 140 100", f'<rect x="2" y="2" width="136" height="96" rx="6" fill="{WHT}" stroke="{BLK}" stroke-width="2"/>'
            + personne(28, 52, 0.95) + f'<circle cx="68" cy="36" r="17" fill="{WHT}" stroke="{RED}" stroke-width="5"/>' + text("20", 68, 37, 17)
            + voiture_face(110, 52, 1.0) + text("ZONE DE", 70, 70, 13) + text("RENCONTRE", 70, 86, 13))
P["B54"] = ("0 0 140 100", f'<rect x="2" y="2" width="136" height="96" rx="6" fill="{WHT}" stroke="{BLK}" stroke-width="2"/>'
            + personne(58, 56, 1.15) + personne(82, 56, 0.8) + text("AIRE", 70, 72, 13) + text("PIÉTONNE", 70, 88, 13))
P["EB10"] = ("0 0 200 80", f'<rect x="2" y="2" width="196" height="76" rx="5" fill="{WHT}" stroke="{RED}" stroke-width="5"/>'
             + text("VILLENEUVE", 100, 41, 24))
P["EB20"] = ("0 0 200 80", f'<rect x="2" y="2" width="196" height="76" rx="5" fill="{WHT}" stroke="{RED}" stroke-width="5"/>'
             + text("VILLENEUVE", 100, 41, 24) + f'<line x1="14" y1="70" x2="186" y2="10" stroke="{RED}" stroke-width="7"/>')


def direction(bg, fg, label, sub=""):
    b = f'<rect x="2" y="2" width="196" height="76" rx="6" fill="{bg}" stroke="{fg}" stroke-width="3"/>'
    b += fleche([(26, 40), (60, 40)], fg, 8, 12) if True else ""
    b += text(label, 128, 30 if sub else 41, 22, fg)
    if sub:
        b += text(sub, 128, 56, 18, fg, "normal")
    return ("0 0 200 80", b)


P["D-bleu"] = direction(BLUE, WHT, "A 6", "Lyon")
P["D-vert"] = direction("#0b7a3b", WHT, "N 7", "Valence")
P["D-blanc"] = direction(WHT, BLK, "Centre-ville")
P["D-jaune"] = direction(YEL, BLK, "Déviation")
P["D-marron"] = direction("#7a4a22", WHT, "Château")

P["M1-150"] = ("0 0 100 40", f'<rect x="2" y="2" width="96" height="36" rx="4" fill="{WHT}" stroke="{BLK}" stroke-width="2"/>' + text("150 m", 50, 21, 20))
P["M12"] = ("0 0 100 70", f'<rect x="2" y="2" width="96" height="66" rx="4" fill="{WHT}" stroke="{BLK}" stroke-width="2"/>'
            f'<polygon points="12,14 40,14 26,40" fill="{WHT}" stroke="{RED}" stroke-width="4" stroke-linejoin="round"/>'
            + velo(62, 40, 0.8) + fleche([(62, 60), (84, 60)], BLK, 3.5, 6))

# ---------- feux ----------
ORANGE = "#f29a00"
OFF = "#3a3a3a"


def feu(rouge=False, orange=False, vert=False, clign=False):
    def lamp(cy, on, col):
        if not on:
            return f'<circle cx="50" cy="{cy}" r="14" fill="{OFF}"/>'
        anim = (f'<animate attributeName="fill" values="{col};{OFF};{col}" dur="1.2s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/>'
                if clign else "")
        return f'<circle cx="50" cy="{cy}" r="14" fill="{col}">{anim}</circle>'
    return ("0 0 100 140", f'<rect x="28" y="6" width="44" height="128" rx="10" fill="{BLK}"/>'
            + lamp(30, rouge, RED) + lamp(70, orange, ORANGE) + lamp(110, vert, "#19b34a"))


P["feu-rouge"] = feu(rouge=True)
P["feu-orange"] = feu(orange=True)
P["feu-vert"] = feu(vert=True)
P["feu-orange-cli"] = feu(orange=True, clign=True)
P["feu-rouge-cli"] = ("0 0 140 80", f'<rect x="6" y="18" width="128" height="44" rx="22" fill="{BLK}"/>'
                      f'<circle cx="40" cy="40" r="15" fill="{RED}"><animate attributeName="fill" values="{RED};{OFF};{RED}" dur="1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/></circle>'
                      f'<circle cx="100" cy="40" r="15" fill="{OFF}"><animate attributeName="fill" values="{OFF};{RED};{OFF}" dur="1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/></circle>')
P["feu-rouge-fleche-cli"] = ("0 0 150 140", feu(rouge=True)[1] +
                             f'<rect x="84" y="94" width="40" height="40" rx="8" fill="{BLK}"/>'
                             f'<g>{fleche([(92, 114), (116, 114)], ORANGE, 5, 8)}<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/></g>')
P["voie-croix"] = (f'<rect x="4" y="4" width="92" height="92" rx="8" fill="{BLK}"/>'
                   f'<path d="M28,28 L72,72 M72,28 L28,72" stroke="{RED}" stroke-width="11" stroke-linecap="round"/>')
P["voie-fleche-verte"] = (f'<rect x="4" y="4" width="92" height="92" rx="8" fill="{BLK}"/>'
                          + fleche([(50, 20), (50, 80)], "#19b34a", 11, 16))
P["voie-fleche-orange"] = (f'<rect x="4" y="4" width="92" height="92" rx="8" fill="{BLK}"/>'
                           + fleche([(32, 72), (70, 30)], ORANGE, 10, 15))

# ---------- schémas de marquage (vue de dessus) ----------
ROUTE = "#555b61"


def auto(x, y, c="#e63946", rot=0):
    return (f'<g transform="translate({x},{y}) rotate({rot})">'
            f'<rect x="-9" y="-16" width="18" height="32" rx="5" fill="{c}"/>'
            f'<rect x="-7" y="-9" width="14" height="7" rx="2" fill="#bfe3ff"/>'
            f'<rect x="-7" y="6" width="14" height="5" rx="2" fill="#bfe3ff"/></g>')


def route(inner, h=200, w=120):
    return (f"0 0 {w} {h}", f'<rect width="{w}" height="{h}" fill="#8fbf6a"/>'
            f'<rect x="10" width="{w - 20}" height="{h}" fill="{ROUTE}"/>'
            f'<rect x="13" width="2" height="{h}" fill="{WHT}"/><rect x="{w - 15}" width="2" height="{h}" fill="{WHT}"/>' + inner)


def discontinue(x, y0, y1, trait=10, vide=14, w=3):
    out, y = "", y0
    while y < y1:
        out += f'<rect x="{x - w/2}" y="{y}" width="{w}" height="{min(trait, y1 - y)}" fill="{WHT}"/>'
        y += trait + vide
    return out


S = {}
S["ligne-continue"] = route(f'<rect x="58.5" width="3" height="200" fill="{WHT}"/>' + auto(85, 150))
S["ligne-discontinue"] = route(discontinue(60, 0, 200) + auto(85, 150))
S["ligne-annonce"] = route(f'<rect x="58.5" width="3" height="50" fill="{WHT}"/>' + discontinue(60, 56, 130, 20, 5) +
                          discontinue(60, 140, 200) + auto(85, 165))
S["ligne-mixte-discontinue-cote"] = route(f'<rect x="56" width="3" height="200" fill="{WHT}"/>' + discontinue(62.5, 0, 200) + auto(85, 150))
S["ligne-mixte-continue-cote"] = route(f'<rect x="61" width="3" height="200" fill="{WHT}"/>' + discontinue(57.5, 0, 200) + auto(85, 150))
S["fleche-rabattement"] = route(f'<rect x="58.5" width="3" height="70" fill="{WHT}"/>' + discontinue(60, 70, 200, 18, 6) +
                                f'<path d="M36,128 Q36,108 52,98" fill="none" stroke="{WHT}" stroke-width="5"/>'
                                f'<polygon points="46,92 60,93 53,104" fill="{WHT}"/>' + auto(35, 165) + auto(85, 120, "#2a9d8f"))
S["ligne-stop"] = route(f'<rect x="60" y="80" width="48" height="6" fill="{WHT}"/>' + text("STOP", 84, 104, 13, WHT) +
                        f'<rect x="58.5" y="86" width="3" height="114" fill="{WHT}"/>' + auto(84, 160), h=200)
S["ligne-cedez"] = route("".join(f'<rect x="{62 + i*9}" y="80" width="6" height="5" fill="{WHT}"/>' for i in range(5)) +
                         f'<polygon points="74,98 94,98 84,118" fill="none" stroke="{WHT}" stroke-width="2.5"/>' +
                         discontinue(60, 86, 200) + auto(84, 160))
S["jaune-continue"] = route(f'<rect x="105" width="5" height="200" fill="{YEL}"/>' + auto(85, 150, "#2a9d8f"))
S["jaune-discontinue"] = route("".join(f'<rect x="105" y="{i*24}" width="5" height="12" fill="{YEL}"/>' for i in range(9)) + auto(85, 150, "#2a9d8f"))
S["zebra"] = route(f'<polygon points="60,20 70,90 60,180 50,90" fill="none" stroke="{WHT}" stroke-width="2.5"/>' +
                   "".join(f'<line x1="{52 + (i % 2)}" y1="{40 + i*12}" x2="{68}" y2="{30 + i*12}" stroke="{WHT}" stroke-width="2.5"/>' for i in range(11)) +
                   auto(85, 170) + auto(35, 30, "#2a9d8f", 180))
S["sas-velo"] = route(f'<rect x="60" y="60" width="48" height="4" fill="{WHT}"/><rect x="60" y="100" width="48" height="4" fill="{WHT}"/>'
                      + velo(84, 92, 0.6, WHT, False) + discontinue(60, 0, 200) + auto(84, 140), h=200)
S["bau"] = route(f'<rect x="70" width="3" height="200" fill="{WHT}"/>' + discontinue(40, 0, 200, 20, 10) +
                 f'<rect x="73" width="35" height="200" fill="#62686e"/>' + auto(25, 150) + auto(55, 60, "#2a9d8f"), w=120)
S["passage-pieton"] = route("".join(f'<rect x="{16 + i*11}" y="80" width="6" height="40" fill="{WHT}"/>' for i in range(9)) + auto(85, 165))


def discontinue_h(y, x0, x1, trait=10, vide=14, w=3):
    out, x = "", x0
    while x < x1:
        out += f'<rect x="{x}" y="{y - w/2}" width="{min(trait, x1 - x)}" height="{w}" fill="{WHT}"/>'
        x += trait + vide
    return out


# ---------- panneaux complémentaires ----------
P["B12"] = rond_rouge(text("3,5 m", 50, 52, 20) +
                      f'<polygon points="44,22 56,22 50,30" fill="{BLK}"/><polygon points="44,80 56,80 50,72" fill="{BLK}"/>')
P["B13"] = rond_rouge(text("5,5 t", 50, 52, 24))
P["B11"] = rond_rouge(text("2 m", 50, 52, 22) +
                      f'<polygon points="20,44 20,56 28,50" fill="{BLK}"/><polygon points="80,44 80,56 72,50" fill="{BLK}"/>')
P["C107"] = carre_bleu(f'<rect x="20" y="20" width="60" height="60" rx="4" fill="{WHT}"/>' + voiture_face(50, 66, 1.2, BLK))
P["C207"] = carre_bleu(f'<path d="M36,86 L44,30 M64,86 L56,30" stroke="{WHT}" stroke-width="7"/>'
                       f'<path d="M20,46 Q50,20 80,46" fill="none" stroke="{WHT}" stroke-width="6"/>')


# ---------- carrefours (vue de dessus) ----------
GRASS = "#8fbf6a"


def carrefour(inner, rond=False):
    """Croisement de deux routes à double sens, 200x200. Voies : x=85/115, y=85/115."""
    b = f'<rect width="200" height="200" fill="{GRASS}"/>'
    if rond:
        b += (f'<rect x="70" width="60" height="200" fill="{ROUTE}"/><rect y="70" width="200" height="60" fill="{ROUTE}"/>'
              f'<circle cx="100" cy="100" r="62" fill="{ROUTE}"/><circle cx="100" cy="100" r="30" fill="{GRASS}" stroke="{WHT}" stroke-width="2"/>')
    else:
        b += f'<rect x="70" width="60" height="200" fill="{ROUTE}"/><rect y="70" width="200" height="60" fill="{ROUTE}"/>'
        b += discontinue(100, 0, 66, 8, 8) + discontinue(100, 134, 200, 8, 8)
        b += "".join(f'<rect x="{x}" y="98.5" width="8" height="3" fill="{WHT}"/>' for x in (2, 18, 34, 50, 142, 158, 174, 190))
    return ("0 0 200 200", b + inner)


def chemin(d, c):
    return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round" opacity=".9"/>')


def mini(code, x, y, s=0.2):
    v = P[code]
    body = v[1] if isinstance(v, tuple) else v
    return f'<g transform="translate({x},{y}) scale({s})">{body}</g>'


RED_C, BLUE_C, GREEN_C = "#e63946", "#2f6fdf", "#2a9d8f"
SUD = (115, 160, 0)      # vient du sud, roule vers le nord
EST = (160, 85, -90)     # vient de l'est, roule vers l'ouest
NORD = (85, 40, 180)     # vient du nord, roule vers le sud
OUEST = (40, 115, 90)    # vient de l'ouest, roule vers l'est


def car(pos, c):
    x, y, r = pos
    return auto(x, y, c, r)


TOUT_DROIT_S = "M115,140 L115,10"
GAUCHE_S = "M115,140 C115,100 100,85 15,85"
DROITE_S = "M115,140 C115,125 125,115 190,115"
TOUT_DROIT_E = "M140,85 L10,85"
TOUT_DROIT_N = "M85,60 L85,190"
GAUCHE_N = "M85,60 C85,100 100,115 190,115"
TOUT_DROIT_O = "M60,115 L190,115"

S["prio-droite"] = carrefour(chemin(TOUT_DROIT_S, RED_C) + chemin(TOUT_DROIT_E, BLUE_C) + car(SUD, RED_C) + car(EST, BLUE_C))
S["prio-gauche"] = carrefour(chemin(TOUT_DROIT_S, RED_C) + chemin(TOUT_DROIT_O, BLUE_C) + car(SUD, RED_C) + car(OUEST, BLUE_C))
S["tourne-gauche-face"] = carrefour(chemin(GAUCHE_S, RED_C) + chemin(TOUT_DROIT_N, BLUE_C) + car(SUD, RED_C) + car(NORD, BLUE_C))
S["trois-voitures"] = carrefour(chemin(TOUT_DROIT_S, RED_C) + chemin(TOUT_DROIT_E, BLUE_C) + chemin(TOUT_DROIT_O, GREEN_C)
                                + car(SUD, RED_C) + car(EST, BLUE_C) + car(OUEST, GREEN_C))
S["stop-droite"] = carrefour(f'<rect x="100" y="134" width="30" height="4" fill="{WHT}"/>' + mini("AB4", 134, 140)
                             + chemin(TOUT_DROIT_S, RED_C) + chemin(TOUT_DROIT_O, BLUE_C) + car(SUD, RED_C) + car(OUEST, BLUE_C))
S["prioritaire-droite"] = carrefour(mini("AB6", 134, 140) + f'<rect x="134" y="66" width="4" height="30" fill="{WHT}"/>'
                                    + chemin(TOUT_DROIT_S, RED_C) + chemin(TOUT_DROIT_E, BLUE_C) + car(SUD, RED_C) + car(EST, BLUE_C))
S["giratoire"] = carrefour("".join(f'<rect x="{100 + i*6}" y="140" width="4" height="3" fill="{WHT}"/>' for i in range(5))
                           + mini("AB3a", 134, 146) + chemin("M50,100 A50,50 0 0 0 100,150", BLUE_C)
                           + auto(115, 172, RED_C, 0) + auto(54, 110, BLUE_C, 160), rond=True)
S["giratoire-sans-panneau"] = carrefour(chemin("M50,100 A50,50 0 0 0 100,150", BLUE_C)
                                        + auto(115, 172, RED_C, 0) + auto(54, 110, BLUE_C, 160), rond=True)
S["parking-sortie"] = ("0 0 200 200", f'<rect width="200" height="200" fill="{GRASS}"/><rect y="70" width="200" height="60" fill="{ROUTE}"/>'
                       + discontinue_h(100, 0, 200) + f'<rect x="100" y="130" width="40" height="70" fill="#9b9b9b"/>'
                       + "".join(f'<rect x="{102 + i*0}" y="{150 + i*14}" width="36" height="2" fill="{WHT}"/>' for i in range(3))
                       + chemin("M120,150 C120,125 130,115 190,115", RED_C) + chemin("M190,115 L10,115", BLUE_C).replace("190,115 L10", "10,115 L190")
                       + auto(120, 165, RED_C, 0) + auto(40, 115, BLUE_C, 90))
S["voie-insertion"] = ("0 0 200 200", f'<rect width="200" height="200" fill="{GRASS}"/>'
                       f'<rect x="60" width="70" height="200" fill="{ROUTE}"/><polygon points="130,200 160,200 160,120 130,40" fill="{ROUTE}"/>'
                       + discontinue(95, 0, 200, 14, 10) + discontinue(130, 40, 200, 4, 4)
                       + auto(145, 160, RED_C, 0) + auto(112, 120, BLUE_C, 0))


# ---------- pictogrammes médicaments ----------
def medoc(col, niveau, l1, l2):
    return ("0 0 120 104",
            f'<rect width="120" height="104" rx="8" fill="{WHT}"/>'
            f'<polygon points="60,8 112,96 8,96" fill="{col}" stroke="{BLK}" stroke-width="3" stroke-linejoin="round"/>'
            + voiture_face(60, 84, 1.25, BLK))


P["med-1"] = medoc("#ffd400", 1, "Soyez prudent", "")
P["med-2"] = medoc("#f28c00", 2, "Soyez très prudent", "")
P["med-3"] = medoc("#e3001b", 3, "Attention, danger : ne pas conduire", "")

# ---------- schémas conducteur / secours ----------
S["angle-mort"] = ("0 0 160 220", f'<rect width="160" height="220" fill="{GRASS}"/><rect x="20" width="120" height="220" fill="{ROUTE}"/>'
                   + discontinue(80, 0, 220, 14, 10)
                   + '<polygon points="101,138 60,175 60,215 101,160" fill="#ffb703" opacity=".55"/>'
                   + '<polygon points="119,138 140,175 140,215 119,160" fill="#ffb703" opacity=".55"/>'
                   + auto(110, 130, "#e63946")
                   + '<g transform="translate(68,182)"><rect x="-3" y="-11" width="6" height="22" rx="3" fill="#2f6fdf"/><circle cx="0" cy="-2" r="4" fill="#1a1a1a"/></g>')
S["balisage"] = ("0 0 320 120", f'<rect width="320" height="120" fill="{GRASS}"/><rect y="25" width="320" height="70" fill="{ROUTE}"/>'
                 + discontinue_h(60, 0, 320)
                 + '<g transform="translate(250,77) rotate(90)">' + auto(0, 0, "#e63946")[len('<g transform="translate(0,0) rotate(0)">'):]
                 + '<polygon points="120,66 132,86 108,86" fill="#ff3b30" stroke="#fff" stroke-width="1.5"/>'
                 + f'<line x1="126" y1="100" x2="244" y2="100" stroke="{WHT}" stroke-width="1.5"/>'
                 + '<polygon points="126,96 126,104 120,100" fill="#fff"/><polygon points="244,96 244,104 250,100" fill="#fff"/>'
                 + text("au moins 30 m", 185, 110, 10, WHT))

# croix de Saint-André (passage à niveau sans barrière)
def croix_st_andre():
    rouge = "".join(f'<rect x="4" y="38" width="92" height="24" rx="4" fill="{RED}" transform="rotate({g} 50 50)"/>' for g in (35, -35))
    blanc = "".join(f'<rect x="8" y="42" width="84" height="16" rx="2" fill="{WHT}" transform="rotate({g} 50 50)"/>' for g in (35, -35))
    return rouge + blanc


P["G1"] = croix_st_andre()
P["plaque-orange"] = ("0 0 160 110", f'<rect x="4" y="4" width="152" height="102" rx="6" fill="#ff8c00" stroke="{BLK}" stroke-width="6"/>'
                      f'<line x1="4" y1="55" x2="156" y2="55" stroke="{BLK}" stroke-width="5"/>'
                      + text("33", 80, 31, 34) + text("1203", 80, 81, 34))

def main():
    os.makedirs(OUT_P, exist_ok=True)
    os.makedirs(OUT_S, exist_ok=True)
    for name, v in P.items():
        vb, body = v if isinstance(v, tuple) else ("0 0 100 100", v)
        with open(os.path.join(OUT_P, f"{name}.svg"), "w") as f:
            f.write(svg(body, vb))
    for name, (vb, body) in S.items():
        with open(os.path.join(OUT_S, f"{name}.svg"), "w") as f:
            f.write(svg(body, vb))
    print(f"{len(P)} panneaux, {len(S)} schémas")


if __name__ == "__main__":
    main()
