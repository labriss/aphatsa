"""Pixel art « HD » de la pub 3 : écran natif 270×480 (agrandi ×4 en 1080×1920), perso ombré, décors détaillés.
Le perso ressemble au vrai plombier de la fin (Pexels 6194923) : cheveux courts bruns, lunettes dorées, barbe courte, pull vert."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
W, H, X = 270, 480, 4
F8 = ImageFont.truetype(os.path.join(ICI, "PressStart2P-Regular.ttf"), 8)
F16 = ImageFont.truetype(os.path.join(ICI, "PressStart2P-Regular.ttf"), 16)

P = {
    "o": "#1A1420", "h": "#2B1E1A", "H": "#4A3328", "s": "#C98E6A", "S": "#A06A4D", "l": "#DDA47E", "g": "#C9A85A",
    "e": "#1A1420", "b": "#3A2A22", "m": "#7A3A30", "v": "#35553D", "V": "#243A2B", "L": "#4A7254", "j": "#3A5878",
    "J": "#2A4058", "k": "#201A1E", "w": "#F2F4F0",
    # décor
    "noir": "#0B0910", "blanc": "#F4EFE6", "gris": "#8A8F98", "gris2": "#5A5F6A", "jaune": "#FFD84D", "orange": "#F07A1E",
    "orange2": "#B5530C", "rouge": "#E5484D", "rouge2": "#8E1E22", "vert": "#3BD47A", "vert2": "#1E7A4C", "bleu": "#4FB3FF",
    "bleu2": "#2B5F9E", "violet": "#7A5CFF", "rose": "#FF7AA8", "papier": "#FFF7E6", "papier2": "#E2D3B5", "bois": "#8A5632",
    "bois2": "#5A3420", "bois3": "#A8703F",
}


def c(k):
    v = P.get(k, k)
    return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))


# ——— le perso, de face, 24×37 cases ———
PERSO = [
    "........oooooooo........",
    ".......oHHHhhhhho.......",
    "......ohhHhhhhhhho......",
    "......ohhhhhhhhhho......",
    "......ohsslllllsho......",
    "......osllllllllso......",
    "......osggglsgggso......",
    "......osgeglsgegso......",
    "......osggglsgggso......",
    "......oSlllsslllSo......",
    "......obSllllllSbo......",
    "......obbbmmmmbbbo......",
    "......obbbbbbbbbbo......",
    ".......obbbbbbbbo.......",
    "........oSSSSSSo........",
    ".....oovvvvvvvvvvoo.....",
    "....oVvvvvvvvvvvvvVo....",
    "...oVvvLvvvvvvvvLvvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVvvvvvvvvvvVvVo...",
    "...oVvVVVVVVVVVVVVvVo...",
    "...osSojjjjjjjjjjosSo...",
    "...osSojjjjjjjjjjosSo...",
    "....oo.ojjjJjjjjo.oo....",
    ".......ojjjjoojjjjo......",
    ".......ojJjjoojJjjo......",
    ".......ojJjjoojJjjo......",
    ".......ojJjjoojJjjo......",
    ".......ojJjjoojJjjo......",
    ".......ojJjjoojJjjo......",
    "......okkkkkookkkkko.....",
    "......oooooooooooooo.....",
]
PERSO = [r.ljust(24, ".")[:24] for r in PERSO]


def grille(im, rows, x0, y0, pal=None, e=1, teinte=None):
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            col = c((pal or {}).get(ch, ch))
            if teinte:
                col = tuple(int(a + (b - a) * teinte[1]) for a, b in zip(col, c(teinte[0])))
            for a in range(e):
                for b in range(e):
                    xx, yy = x0 + x * e + a, y0 + y * e + b
                    if 0 <= xx < im.width and 0 <= yy < im.height:
                        px[xx, yy] = col


POSES = {
    "calme": {}, "fatigue": dict(yeux="fermes", sourcils="triste"), "agace": dict(sourcils="colere"),
    "enerve": dict(sourcils="colere", bouche="grimace"), "furieux": dict(sourcils="colere", bouche="cri", bras="ciel"),
    "cri": dict(sourcils="colere", bouche="cri", bras="ciel"), "content": dict(bouche="sourire"),
    "surpris": dict(sourcils="haut", yeux="grands", bouche="o"), "telephone": dict(bras="telephone", sourcils="haut", yeux="grands", bouche="sourire"),
}
_cache = {}


def perso(im, x, y, humeur="calme", e=2, t=0.0, jambes=True, rouge=0.0):
    """Le plombier (personnage.py, même taille de pixel que le décor). x, y : coin haut-gauche de l'ancien gabarit 24e×37e."""
    import personnage
    k = {1: 0.55, 2: 1.0, 3: 1.5}.get(e, e / 2)
    pose = dict(POSES.get(humeur, {}), buste=not jambes, rouge=round(rouge, 1))
    if humeur in ("calme", "content"):
        pose["jambes"] = 0.0
    cle = (k, tuple(sorted(pose.items())))
    if cle not in _cache:
        _cache[cle] = personnage.rendre(pose, k)
    spr = _cache[cle]
    bob = int(round(math.sin(t * 6) * 0.6)) if humeur in ("calme", "content") else 0
    x0 = int(x + 12 * e - spr.width / 2)
    y0 = int(y + bob)
    im.paste(spr, (x0, y0), spr)
    if humeur in ("furieux", "cri"):  # fumée par les oreilles
        d = ImageDraw.Draw(im)
        for kk in range(3):
            ph = (t * 3 + kk / 3) % 1
            for sx in (-1, 1):
                cx = x0 + spr.width / 2 + sx * (11 * k + ph * 10)
                cy = y0 + 18 * k - ph * 22
                r = 2 + int(ph * 4)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c("blanc" if ph < 0.5 else "gris"))


# ——— éléments communs ———
def texte(d, xy, t, col="blanc", f=F8):
    acc = [i for i, ch in enumerate(t) if ch in "ÉÈÊ"]
    d.text(xy, t.replace("É", "E").replace("È", "E").replace("Ê", "E"), font=f, fill=c(col))
    k = 8 if f is F8 else 16
    for i in acc:
        x, y = xy[0] + i * k, xy[1]
        d.rectangle([x + k // 2, y - k // 4, x + k // 2 + k // 8, y - k // 8], fill=c(col))


def cadre(d, box, ep=3, fond="noir", bord="blanc"):
    d.rectangle(box, fill=c(fond))
    for k in range(ep):
        d.rectangle([box[0] + k, box[1] + k, box[2] - k, box[3] - k], outline=c(bord))


def degrade(d, box, c1, c2, bandes=8):
    """Dégradé en bandes avec tramage, façon jeu 16 bits."""
    x0, y0, x1, y1 = box
    a, b = c(c1), c(c2)
    hh = y1 - y0
    for y in range(y0, y1):
        u = (y - y0) / max(1, hh)
        k = int(u * bandes)
        frac = u * bandes - k
        for x in range(x0, x1):
            kk = k + (1 if ((x + y) % 2 == 0 and frac > 0.5) else 0)
            v = min(1.0, kk / bandes)
            d.point((x, y), fill=tuple(int(p + (q - p) * v) for p, q in zip(a, b)))


def dialogue(d, lignes, t, vitesse=26, y0=356):
    """Boîte de dialogue ; le texte s'écrit lettre par lettre. Renvoie le nombre de lettres affichées."""
    cadre(d, [8, y0, W - 9, y0 + 74], 3)
    reste = int(t * vitesse)
    total = 0
    y = y0 + 14
    for l, col in lignes:
        n = max(0, min(len(l), reste))
        texte(d, (18, y), l[:n], col)
        reste -= len(l)
        total += n
        y += 14
    if reste > 0 and int(t * 3) % 2:
        d.polygon([(W - 26, y0 + 60), (W - 18, y0 + 60), (W - 22, y0 + 65)], fill=c("blanc"))
    return total


HUD_Y = 40  # sous la zone cachée par l'interface de TikTok / Reels


def hud(im, heure, pv, t_coup=None, t=0.0, couleur_h="jaune"):
    """Jauge PATIENCE en 20 gros segments + heure ; secousse et « -n » qui monte après un coup."""
    d = ImageDraw.Draw(im)
    y0 = HUD_Y
    dx = 0
    if t_coup is not None and 0 <= t - t_coup[0] < 0.35:
        dx = int(math.sin((t - t_coup[0]) * 90) * 3)
    col = "vert" if pv > 12 else "jaune" if pv > 6 else "rouge"
    if pv <= 4 and int(t * 6) % 2:
        col = "rouge2"
    cadre(d, [6 + dx, y0, 264 + dx, y0 + 56], 2, "noir", col if pv <= 4 else "blanc")
    grille(im, [".rr.rr.", "rrrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."], 14 + dx, y0 + 11, {"r": "rouge"}, 2)
    texte(d, (34 + dx, y0 + 9), "PATIENCE", "blanc", F16)
    texte(d, (176 + dx, y0 + 13), f"{pv:>2}/20", col)
    for k in range(20):
        x = 14 + dx + k * 12
        d.rectangle([x, y0 + 32, x + 10, y0 + 47], fill=c(col if k < pv else "#2A2230"))
        if k < pv:
            d.rectangle([x, y0 + 32, x + 10, y0 + 34], fill=tuple(min(255, v + 60) for v in c(col)))
    cadre(d, [196, y0 + 62, 264, y0 + 76], 1, "noir", couleur_h)
    texte(d, (200, y0 + 65), heure, couleur_h)
    if t_coup is not None and 0 <= t - t_coup[0] < 1.1:
        u = (t - t_coup[0]) / 1.1
        texte(d, (120, y0 + 64 - int(u * 10)), f"-{t_coup[1]}", "rouge", F16)
        if u < 0.25:
            d.rectangle([0, 0, W - 1, H - 1], outline=c("rouge"), width=3)


def papier(d, x, y, r=0.0, s=1.0):
    pts = [(-6, -8), (6, -8), (6, 8), (-6, 8)]
    ca, sa = math.cos(r), math.sin(r)
    poly = [(x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s) for px, py in pts]
    d.polygon(poly, fill=c("papier"), outline=c("o"))
    for k in (-3, 0, 3):
        a = (x + (-3 * ca - k * sa) * s, y + (-3 * sa + k * ca) * s)
        b = (x + (3 * ca - k * sa) * s, y + (3 * sa + k * ca) * s)
        d.line([a, b], fill=c("gris"))


def telephone_pixel(d, x, y, allume=0.0, vibre=0.0, t=0.0):
    ox = int(math.sin(t * 70) * 2 * vibre)
    d.rectangle([x + ox, y, x + ox + 14, y + 24], fill=c("o"))
    d.rectangle([x + ox + 2, y + 2, x + ox + 12, y + 22], fill=tuple(int(a + (b - a) * allume) for a, b in zip(c("#22252C"), c("orange"))))
    if vibre:
        for k in (1, 2):
            d.arc([x - 4 * k, y - 4 * k + 6, x + 18 + 4 * k, y + 18 + 4 * k], 200, 340, fill=c("jaune"))
