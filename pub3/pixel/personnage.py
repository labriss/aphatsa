"""Le plombier en pixel art, à l'image du vrai (Pexels 6194923) : cheveux noirs courts dégradés, gros sourcils,
barbe courte et moustache, lunettes fines dorées octogonales, pull vert olive, jean.
Dessiné en formes lisses ×8 puis réduit à la taille native et ramené sur une palette fixe : même taille de pixel
que les décors, ombres propres, contour sombre. rendre(pose, k) → image RGBA (k = pixels natifs par unité)."""
import math

from PIL import Image, ImageDraw

S = 8  # suréchantillonnage
PAL = {
    "peau_c": "#DDAC8A", "peau": "#BE8F73", "peau_o": "#966652", "cheveux": "#231B17", "cheveux_c": "#3A2E27",
    "barbe": "#54423A", "pull_c": "#52654A", "pull": "#3A4A35", "pull_o": "#252F22", "jean_c": "#4C6C8C", "jean": "#35506B",
    "jean_o": "#26394D", "chaus": "#1E1A1C", "chaus_c": "#3A3438", "or": "#C9AE78", "blanc": "#F4F1EA", "bouche": "#7A3E36",
    "contour": "#18121A", "rouge": "#E5484D",
}


def hexa(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


COUL = {k: hexa(v) for k, v in PAL.items()}
LISTE = list(COUL.values())


def proche(c):
    return min(LISTE, key=lambda p: (p[0] - c[0]) ** 2 * 0.3 + (p[1] - c[1]) ** 2 * 0.59 + (p[2] - c[2]) ** 2 * 0.11)


POSE = dict(bras="bas", bouche="neutre", sourcils="neutre", yeux="ouverts", jambes=0.0, rouge=0.0, buste=False, lunettes=True, barbe=True, cols=())


def rendre(pose=None, k=1.0):
    p = dict(POSE, **(pose or {}))
    W, H = 40, 78
    s = S * k
    im = Image.new("RGBA", (int(W * s), int(H * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = dict(p["cols"])
    C = lambda n: (hexa(cols[n]) if n in cols else COUL[n]) + (255,)
    liste = [C(n)[:3] for n in COUL]

    def el(cx, cy, rx, ry, col):
        d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=C(col))

    def rr(x0, y0, x1, y1, r, col):
        d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s], r * s, fill=C(col))

    def poly(pts, col):
        d.polygon([(x * s, y * s) for x, y in pts], fill=C(col))

    def membre(a, b, r, col):
        (x0, y0), (x1, y1) = a, b
        n = 12
        for i in range(n + 1):
            u = i / n
            el(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, r, r, col)

    # jambes (marche : décalage alterné)
    if not p["buste"]:
        j = p["jambes"]
        for sx, off in ((-1, j), (1, -j)):
            x = 20 + sx * 4.2
            rr(x - 3.4, 50, x + 3.4, 71 + off * 0.6, 1.5, "jean")
            rr(x - 3.4 + (1.6 if sx < 0 else 0), 50, x - 1.4 + (1.6 if sx < 0 else 3.4), 71 + off * 0.6, 1, "jean_o" if sx > 0 else "jean_c")
            rr(x - 4.0 + off * 0.4, 70 + off * 0.6, x + 4.4 + off * 0.4, 74.5 + off * 0.6, 1.6, "chaus")
            rr(x - 3.0 + off * 0.4, 70.4 + off * 0.6, x + 1.0 + off * 0.4, 71.6 + off * 0.6, 0.6, "chaus_c")
    # bras derrière le corps quand ils sont en l'air
    epaules = ((11.5, 33.5), (28.5, 33.5))
    mains = {
        "bas": ((9.5, 50), (30.5, 50)),
        "ciel": ((5, 14), (35, 14)),
        "table": ((14, 46), (26, 46)),
        "telephone": ((16.5, 41), (23.5, 41)),
        "tete": ((12.5, 22), (27.5, 22)),
        "pouce": ((9.5, 50), (31, 30)),
    }[p["bras"]]
    if p["bras"] == "ciel":
        for (a, b) in zip(epaules, mains):
            membre(a, b, 2.6, "pull")
            el(b[0], b[1], 2.4, 2.4, "peau")
    # torse : pull avec ombre à droite et lumière à gauche
    rr(10, 30, 30, 53, 5, "pull")
    rr(10, 30, 16, 53, 4, "pull_c")
    rr(25, 31, 30, 53, 4, "pull_o")
    rr(13, 30, 27, 34, 2, "pull_o")      # col roulé
    rr(14, 30, 26, 32.5, 1.5, "pull")
    for x in range(12, 30, 3):           # côtes du bas du pull
        rr(x, 50.5, x + 1.2, 53, 0.4, "pull_o")
    if p["bras"] != "ciel":
        for (a, b), lado in zip(zip(epaules, mains), (-1, 1)):
            membre(a, b, 2.5, "pull_c" if lado < 0 else "pull_o")
            el(b[0], b[1], 2.2, 2.2, "peau")
    if p["bras"] == "telephone":
        rr(15.5, 34.5, 24.5, 45, 1.2, "contour")
    if p["bras"] == "pouce":
        rr(30.2, 25.5, 32.0, 29.5, 0.8, "peau")
    # tête
    el(11.6, 19.5, 1.8, 2.6, "peau_o")
    el(28.4, 19.5, 1.8, 2.6, "peau_o")
    el(20, 18.5, 8.6, 10.2, "peau")
    el(17.5, 16, 5, 6.5, "peau_c")
    poly([(25, 12), (28.6, 16), (28, 23), (24, 27)], "peau_o")
    # barbe courte, moustache
    if p["barbe"]:
      poly([(12.0, 20.5), (13.4, 25.0), (16.6, 28.2), (23.4, 28.2), (26.6, 25.0), (28.0, 20.5), (26.8, 22.4), (24.2, 22.8),
          (20, 22.6), (15.8, 22.8), (13.2, 22.4)], "barbe")
      poly([(15.4, 23.6), (24.6, 23.6), (23.6, 26.2), (16.4, 26.2)], "peau")       # autour de la bouche, la peau ressort
      poly([(17.0, 23.0), (23.0, 23.0), (22.6, 24.0), (17.4, 24.0)], "barbe")      # moustache
    # cheveux : dessus en volume, côtés courts (dégradé)
    el(20, 8.4, 8.2, 4.8, "cheveux")
    el(18.4, 7.2, 5.0, 2.4, "cheveux_c")
    poly([(11.4, 9.5), (11.9, 15.5), (12.9, 15.5), (13.2, 10.5)], "barbe")      # côtés courts (dégradé)
    poly([(28.6, 9.5), (28.1, 15.5), (27.1, 15.5), (26.8, 10.5)], "barbe")
    poly([(11.6, 10.6), (28.4, 10.6), (27.6, 12.2), (20, 11.4), (12.4, 12.2)], "cheveux")
    im = im.resize((int(W * k), int(H * k)), Image.BOX)
    # palette fixe + suppression des demi-transparences
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 110:
                px[x, y] = (0, 0, 0, 0)
            else:
                px[x, y] = min(liste, key=lambda q: (q[0] - r) ** 2 * 0.3 + (q[1] - g) ** 2 * 0.59 + (q[2] - b) ** 2 * 0.11) + (255,)
    d = ImageDraw.Draw(im)

    def pt(x, y, col):
        X, Y = int(round(x * k)), int(round(y * k))
        d.point((X, Y), fill=C(col))

    def ligne(x0, y0, x1, y1, col):
        d.line([(round(x0 * k), round(y0 * k)), (round(x1 * k), round(y1 * k))], fill=C(col), width=max(1, int(k)))

    # sourcils épais
    if p["sourcils"] == "colere":
        ligne(14, 13.4, 18, 15.0, "cheveux"), ligne(22, 15.0, 26, 13.4, "cheveux")
    elif p["sourcils"] == "triste":
        ligne(14, 15.2, 18, 14.0, "cheveux"), ligne(22, 14.0, 26, 15.2, "cheveux")
    elif p["sourcils"] == "haut":
        ligne(14, 13.2, 18, 12.8, "cheveux"), ligne(22, 12.8, 26, 13.2, "cheveux")
    else:
        ligne(14, 14.4, 18, 14.0, "cheveux"), ligne(22, 14.0, 26, 14.4, "cheveux")
    # yeux
    for ex in (16, 24):
        if p["yeux"] == "fermes":
            ligne(ex - 1, 17.4, ex + 1, 17.4, "contour")
        elif p["yeux"] == "grands":
            pt(ex, 17, "blanc"), pt(ex, 17.9, "contour")
        else:
            pt(ex, 17.4, "contour")
    # lunettes fines dorées, octogonales, et le pont
    for ex in ((16, 24) if p["lunettes"] else ()):
        x0, x1, y0, y1 = ex - 2.6, ex + 2.6, 15.4, 19.6
        for a, b in (((x0 + 0.8, y0), (x1 - 0.8, y0)), ((x1, y0 + 0.8), (x1, y1 - 0.8)), ((x1 - 0.8, y1), (x0 + 0.8, y1)),
                     ((x0, y1 - 0.8), (x0, y0 + 0.8))):
            ligne(a[0], a[1], b[0], b[1], "or")
    if p["lunettes"]:
        ligne(18.6, 16.6, 21.4, 16.6, "or")
        ligne(13.4, 16.6, 11.8, 17.2, "or"), ligne(26.6, 16.6, 28.2, 17.2, "or")
    # bouche
    b = p["bouche"]
    if b == "sourire":
        ligne(17, 25, 23, 25, "blanc"), pt(16.4, 24.4, "bouche"), pt(23.6, 24.4, "bouche")
    elif b == "rire":
        for y in (24.6, 25.6):
            ligne(17, y, 23, y, "bouche")
        ligne(17.4, 24.6, 22.6, 24.6, "blanc")
    elif b == "cri":
        for y in (24.4, 25.4, 26.4):
            ligne(17.2, y, 22.8, y, "bouche")
        ligne(17.6, 24.4, 22.4, 24.4, "blanc")
    elif b == "o":
        pt(19.6, 25, "bouche"), pt(20.4, 25, "bouche"), pt(19.6, 25.8, "bouche"), pt(20.4, 25.8, "bouche")
    elif b == "grimace":
        ligne(17, 25.2, 23, 25.2, "bouche"), pt(16.6, 25.8, "bouche"), pt(23.4, 25.8, "bouche")
    else:
        ligne(18, 25, 22, 25, "bouche")
    # contour sombre extérieur
    a = im.split()[3]
    out = Image.new("RGBA", (im.width + 2, im.height + 2), (0, 0, 0, 0))
    m = Image.new("L", out.size, 0)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        m.paste(a, (dx, dy), a)
    out.paste(Image.new("RGBA", out.size, C("contour")), (0, 0), m)
    out.paste(im, (1, 1), im)
    if p["rouge"]:  # seul le visage rougit
        px = out.load()
        peaux = {C("peau")[:3], C("peau_c")[:3], C("peau_o")[:3]}
        for y in range(out.height):
            for x in range(out.width):
                r_, g_, b_, a_ = px[x, y]
                if (r_, g_, b_) in peaux:
                    u = p["rouge"]
                    px[x, y] = (min(255, int(r_ + (235 - r_) * u * 0.6)), int(g_ * (1 - 0.45 * u)), int(b_ * (1 - 0.45 * u)), a_)
    if p["buste"]:
        out = out.crop((0, 0, out.width, int(54 * k)))
    return out


if __name__ == "__main__":
    import os
    poses = [dict(), dict(bouche="sourire"), dict(sourcils="colere", bouche="grimace"), dict(sourcils="colere", bouche="cri", bras="ciel", rouge=0.4),
             dict(yeux="fermes", sourcils="triste", bras="table"), dict(bras="telephone", sourcils="haut", yeux="grands", bouche="o"),
             dict(bras="pouce", bouche="rire", sourcils="haut"), dict(jambes=2)]
    ims = [rendre(p) for p in poses]
    grand = [rendre(p, 2) for p in poses[2:6]]
    pl = Image.new("RGB", (270, 300), (42, 33, 64))
    for i, im in enumerate(ims):
        pl.paste(im, (4 + i * 33, 6), im)
    for i, im in enumerate(grand):
        pl.paste(im, (4 + i * 66, 100), im)
    pl.resize((270 * 4, 300 * 4), Image.NEAREST).save(os.path.join(os.path.dirname(__file__), "..", "tmp", "ap", "perso2.png"))
