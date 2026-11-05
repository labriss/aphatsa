"""Pub Diktéo en pixel art façon RPG indé en couleur (ambiance, sans rien reprendre d'un jeu existant).
Écran natif 180×320, agrandi ×6. python rpg.py → rpg_1.png, rpg_2.png, rpg_3.png et planche_rpg.png."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
W, H, X = 180, 320, 6
F8 = ImageFont.truetype(os.path.join(ICI, "PressStart2P-Regular.ttf"), 8)

C = {
    "noir": "#07090A", "blanc": "#F6F2EA", "gris": "#7E8784", "encre": "#14100E",
    "orange": "#F07A1E", "orange2": "#B5530C", "jaune": "#FFD84D", "rouge": "#E5484D", "rouge2": "#8E1E22",
    "vert": "#3BD47A", "vert2": "#1E7A4C", "violet": "#7A5CFF", "bleu": "#4FB3FF", "rose": "#FF7AA8",
    "papier": "#FFF7E6", "papier2": "#E9DCC2", "peau": "#E7A97F", "peau2": "#C27E55", "cheveux": "#3B2A22",
    "veste": "#2E7A5C", "veste2": "#1F5641", "jean": "#34506A", "bois": "#7A4A2A", "bois2": "#4E2E19",
}


def h(c):
    c = C.get(c, c)
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def texte(d, xy, t, couleur="blanc"):
    """Texte pixel ; É/È dessinés (absents de la police)."""
    acc = [i for i, ch in enumerate(t) if ch in "ÉÈ"]
    t = t.replace("É", "E").replace("È", "E")
    d.text(xy, t, font=F8, fill=h(couleur))
    for i in acc:
        x, y = xy[0] + i * 8, xy[1]
        d.point([(x + 4, y - 3), (x + 5, y - 3), (x + 3, y - 2), (x + 4, y - 2)], fill=h(couleur))


def cadre(d, box, epais=3, fond="noir", bord="blanc"):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=h(fond))
    for k in range(epais):
        d.rectangle([x0 + k, y0 + k, x1 - k, y1 - k], outline=h(bord))


def sprite(im, rows, x0, y0, pal, e=1):
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "." or ch not in pal:
                continue
            for a in range(e):
                for b in range(e):
                    xx, yy = x0 + x * e + a, y0 + y * e + b
                    if 0 <= xx < im.width and 0 <= yy < im.height:
                        px[xx, yy] = h(pal[ch])


# ——— Le monstre « Devis » : une feuille de devis vivante, colorée, plutôt attachante ———
def devis(im, cx, cy, humeur="fache", t=0):
    d = ImageDraw.Draw(im)
    # piles de feuilles derrière (comme une cape)
    for k, (dx, dy, c) in enumerate(((-16, 8, "papier2"), (14, 6, "papier2"), (-8, 3, "papier"), (8, 2, "papier"))):
        d.polygon([(cx - 22 + dx, cy - 30 + dy), (cx + 22 + dx, cy - 30 + dy), (cx + 24 + dx, cy + 34 + dy), (cx - 24 + dx, cy + 34 + dy)],
                  fill=h(c), outline=h("encre"))
    # la feuille principale, avec un coin corné
    d.polygon([(cx - 26, cy - 36), (cx + 18, cy - 36), (cx + 28, cy - 26), (cx + 28, cy + 38), (cx - 26, cy + 38)], fill=h("papier"), outline=h("encre"))
    d.polygon([(cx + 18, cy - 36), (cx + 18, cy - 26), (cx + 28, cy - 26)], fill=h("papier2"), outline=h("encre"))
    # en-tête « DEVIS » et lignes du tableau
    d.rectangle([cx - 22, cy - 32, cx + 20, cy - 22], fill=h("rouge" if humeur == "fache" else "vert"))
    texte(d, (cx - 20, cy - 31), "DEVIS", "blanc")
    for k in range(4):
        y = cy + 14 + k * 5
        d.line([cx - 20, y, cx + 10, y], fill=h("gris"))
        d.line([cx + 14, y, cx + 22, y], fill=h("orange"))
    # visage
    if humeur == "fache":
        sprite(im, ["KK....KK", ".KK..KK.", "WWK..KWW", "WKW..WKW", ".W....W."], cx - 12, cy - 18, {"K": "encre", "W": "blanc"}, 3)
        sprite(im, ["KKKKKKKKKK", "KWKWKWKWKK", "KRRRRRRRRK", "KKKKKKKKKK"], cx - 10, cy + 2, {"K": "encre", "W": "blanc", "R": "rouge"}, 2)
    else:
        sprite(im, ["........", ".KK..KK.", "K..KK..K", "........"], cx - 12, cy - 14, {"K": "encre"}, 3)
        sprite(im, ["K........K", ".K......K.", "..KKKKKK.."], cx - 10, cy + 2, {"K": "encre"}, 2)
        for (px, py) in ((cx - 22, cy - 6), (cx + 16, cy - 6)):
            d.rectangle([px, py, px + 5, py + 3], fill=h("rose"))
    # petits bras ; il brandit un stylo comme une épée
    d.line([cx - 26, cy + 6, cx - 38, cy - 6 + math.sin(t) * 2], fill=h("encre"), width=3)
    d.line([cx + 28, cy + 6, cx + 40, cy - 4], fill=h("encre"), width=3)
    d.polygon([(cx + 40, cy - 4), (cx + 46, cy - 28), (cx + 49, cy - 27), (cx + 43, cy - 3)], fill=h("bleu"), outline=h("encre"))
    # pieds
    d.rectangle([cx - 16, cy + 38, cx - 8, cy + 42], fill=h("encre"))
    d.rectangle([cx + 8, cy + 38, cx + 16, cy + 42], fill=h("encre"))


# ——— Boutons de combat (les nôtres) : icône + mot, cadre orange, celui choisi en jaune ———
ICONES = {
    "DICTER": ["..KK..", ".KOOK.", ".KOOK.", ".KOOK.", "K.KK.K", ".KKKK.", "..KK..", ".KKKK."],
    "ENVOYER": ["K.....", "KKK...", "KOKKK.", "KOOOKK", "KOKKK.", "KKK...", "K....."],
    "BONUS": ["..K...", ".KYK..", "KYYYK.", ".KYK..", "..K...", "......"],
    "FUIR": ["..KK..", "..KK..", ".KKKK.", "K.KK.K", "..KK..", ".K..K.", "K....K"],
}


def boutons(im, choix=0):
    d = ImageDraw.Draw(im)
    for i, nom in enumerate(("DICTER", "ENVOYER", "BONUS", "FUIR")):
        x = 4 + (i % 2) * 88
        y = 268 + (i // 2) * 24
        col = "jaune" if i == choix else "orange"
        cadre(d, [x, y, x + 84, y + 20], 2, "noir", col)
        sprite(im, ICONES[nom], x + 5, y + 4, {"K": col, "O": col, "Y": col}, 2)
        texte(d, (x + 22, y + 7), nom, col)


def stats(im, pv, pvmax=20):
    d = ImageDraw.Draw(im)
    texte(d, (6, 252), "ARTISAN", "blanc")
    texte(d, (66, 252), "PV", "blanc")
    d.rectangle([84, 252, 84 + 40, 259], fill=h("rouge2"))
    d.rectangle([84, 252, 84 + int(40 * pv / pvmax), 259], fill=h("jaune" if pv > 6 else "rouge"))
    texte(d, (130, 252), f"{pv}/{pvmax}", "blanc")


# ——— Écran 1 : la cuisine à 21 h (exploration, vue de dessus) ———
ARTISAN_DOS = [
    "....HHHHHH....", "...HHHHHHHH...", "...HHHHHHHH...", "...HPPPPPPH...", "....PPPPPP....",
    "..VVVVVVVVVV..", ".VVVVVVVVVVVV.", ".VVVOOOOOOVVV.", ".PVVVVVVVVVVP.", "..VVVVVVVVVV..",
    "...JJJ..JJJ...", "...JJJ..JJJ...", "..KKKK..KKKK..",
]


def ecran1():
    im = Image.new("RGB", (W, H), h("noir"))
    d = ImageDraw.Draw(im)
    # pièce : carrelage violet sombre, murs, table, lampe
    for y in range(40, 230, 10):
        for x in range(10, 170, 10):
            d.rectangle([x, y, x + 9, y + 9], fill=h("#2A2140" if ((x + y) // 10) % 2 else "#231B36"))
    d.rectangle([10, 20, 170, 40], fill=h("#3A2E5A"))
    d.rectangle([10, 40, 170, 42], fill=h("#5A4A8A"))
    d.rectangle([118, 24, 140, 36], fill=h("#0B1230"), outline=h("blanc"))
    d.point([(134, 27), (135, 27), (134, 28), (135, 28)], fill=h("jaune"))
    d.rectangle([60, 120, 120, 150], fill=h("bois"), outline=h("bois2"))
    for k in range(5):
        d.rectangle([70 + k * 8 - k % 2 * 2, 116 - k * 3, 86 + k * 8, 128 - k * 3], fill=h("papier"), outline=h("encre"))
    # halo de la lampe
    for r, c in ((36, "#2E2448"), (24, "#3A2E52")):
        d.ellipse([90 - r, 135 - r // 2, 90 + r, 135 + r // 2], outline=h(c))
    sprite(im, ARTISAN_DOS, 82, 168, {"H": "cheveux", "P": "peau", "V": "veste", "O": "orange", "J": "jean", "K": "encre"}, 2)
    cadre(d, [6, 236, 174, 312], 3)
    texte(d, (14, 248), "* Il est 21 h.", "blanc")
    texte(d, (14, 262), "* Trois devis", "blanc")
    texte(d, (14, 274), "  t'attendent", "blanc")
    texte(d, (14, 286), "  sur la table.", "jaune")
    texte(d, (14, 300), "* Encore.", "gris")
    return im


# ——— Écran 2 : le combat (esquive des papiers) ———
def ecran2():
    im = Image.new("RGB", (W, H), h("noir"))
    d = ImageDraw.Draw(im)
    devis(im, 70, 72, "fache", 1)
    # bulle du monstre
    cadre(d, [96, 6, 176, 38], 2, "blanc", "blanc")
    for i, l in enumerate(("TVA ?", "ACOMPTE ?", "21 H !")):
        d.text((100, 9 + i * 9), l, font=F8, fill=h("encre"))
    d.polygon([(104, 38), (112, 38), (100, 46)], fill=h("blanc"))
    texte(d, (8, 120), "LE DEVIS attaque !", "rouge")
    # arène : papiers et horloges qui volent, le micro orange esquive
    cadre(d, [20, 134, 160, 244], 3)
    random.seed(7)
    for k in range(9):
        x, y = random.randint(28, 140), random.randint(142, 230)
        d.rectangle([x, y, x + 8, y + 10], fill=h("papier"), outline=h("encre"))
        d.line([x + 2, y + 3, x + 6, y + 3], fill=h("gris"))
        d.line([x + 2, y + 6, x + 6, y + 6], fill=h("gris"))
    for (x, y) in ((40, 150), (128, 200)):
        d.ellipse([x, y, x + 10, y + 10], fill=h("violet"), outline=h("blanc"))
        d.line([x + 5, y + 5, x + 5, y + 2], fill=h("blanc"))
    for (x, y, t) in ((60, 220, "€"), (110, 160, "%"), (135, 228, "€")):
        texte(d, (x, y), t, "jaune")
    sprite(im, ["..OO..", ".OOOO.", ".OYYO.", ".OOOO.", "O.OO.O", ".OOOO.", "..OO..", ".OOOO."], 84, 186,
           {"O": "orange", "Y": "jaune"}, 2)
    stats(im, 3)
    boutons(im, 0)
    return im


# ——— Écran 3 : la victoire ———
def ecran3():
    im = Image.new("RGB", (W, H), h("noir"))
    d = ImageDraw.Draw(im)
    random.seed(2)
    for k in range(40):
        x, y = random.randint(0, W - 1), random.randint(0, 130)
        d.point((x, y), fill=h(random.choice(("jaune", "orange", "rose", "bleu", "vert"))))
    devis(im, 90, 70, "content")
    cadre(d, [6, 130, 174, 246], 3)
    texte(d, (14, 142), "* Tu as DICTÉ", "orange")
    texte(d, (14, 154), "  le devis.", "orange")
    texte(d, (14, 170), "* Le DEVIS se", "blanc")
    texte(d, (14, 182), "  range tout seul.", "blanc")
    texte(d, (14, 198), "* Mme Fontaine", "vert")
    texte(d, (14, 210), "  l'a ACCEPTÉ.", "vert")
    texte(d, (14, 228), "* Soirée sauvée.", "jaune")
    stats(im, 20)
    boutons(im, 1)
    return im


if __name__ == "__main__":
    ims = [ecran1(), ecran2(), ecran3()]
    for i, im in enumerate(ims, 1):
        im.resize((W * X, H * X), Image.NEAREST).save(os.path.join(ICI, f"rpg_{i}.png"))
    planche = Image.new("RGB", (W * 3 + 12, H), h("#1A1A1A"))
    for i, im in enumerate(ims):
        planche.paste(im, (i * (W + 6), 0))
    planche.resize((planche.width * 3, planche.height * 3), Image.NEAREST).save(os.path.join(ICI, "planche_rpg.png"))
    print("ok")
