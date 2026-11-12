"""Pub Diktéo, pixel art façon RPG indé en couleur : la journée pourrie d'un plombier qui finit par péter un câble.
Pas de combat : une jauge PATIENCE qui descend à chaque galère. Rien n'est repris d'un jeu existant.
python journee.py → journee_1..8.png (×6) et planche_journee.png."""
import math
import os
import random

from PIL import Image, ImageDraw

from rpg import C, F8, H, W, X, cadre, h, sprite, texte

PERSO = [
    "...HHHHHH...", "..HHHHHHHH..", "..HHHHHHHH..", "..HPPPPPPH..", "..PPPPPPPP..", "..HPPPPPPH..",
    "..HHPPPPHH..", "....HHHH....", ".VVVVVVVVVV.", "VVVVVVVVVVVV", "VVVVVVVVVVVV", "PVVVVVVVVVVP",
    "PVVVVVVVVVVP", "..JJJJJJJJ..", "..JJJ..JJJ..", "..JJJ..JJJ..", ".KKKK..KKKK.",
]
CLIENT = [
    "...CCCCCC...", "..CCCCCCCC..", "..CPPPPPPC..", "..PPPPPPPP..", "..PPPPPPPP..", "...PPPPPP...",
    "....PPPP....", ".RRRRRRRRRR.", "RRRRRRRRRRRR", "RRRRRRRRRRRR", "PRRRRRRRRRRP", "PRRRRRRRRRRP",
    "..GGGGGGGG..", "..GGG..GGG..", "..GGG..GGG..", ".KKKK..KKKK.",
]


def perso(im, x, y, humeur="calme", e=3):
    """Le plombier de face : cheveux bruns, barbe, t-shirt beige (comme le vrai, plan Pexels 4010137). humeur : calme, agace, enerve, furieux, soulage."""
    peau = {"furieux": "#E2614F", "enerve": "#E08A6A"}.get(humeur, "peau")
    sprite(im, PERSO, x, y, {"H": "#2A1E18", "P": peau, "V": "#CDBA98", "J": "jean", "K": "encre"}, e)
    d = ImageDraw.Draw(im)
    p = lambda cx, cy, c="encre": d.rectangle([x + cx * e, y + cy * e, x + cx * e + e - 1, y + cy * e + e - 1], fill=h(c))
    if humeur in ("calme", "soulage"):
        p(4, 4), p(7, 4)
    else:
        p(4, 4), p(7, 4)
        p(3, 3), p(8, 3)  # sourcils froncés
        if humeur != "agace":
            p(4, 3), p(7, 3)
    if humeur == "calme":
        p(5, 6), p(6, 6)
    elif humeur == "soulage":
        p(4, 5), p(7, 5), p(5, 6), p(6, 6)
    elif humeur == "agace":
        p(4, 6), p(5, 6), p(6, 6), p(7, 6)
    else:
        for cx in range(4, 8):
            p(cx, 6, "rouge2")
        p(4, 5, "encre"), p(7, 5, "encre")
    if humeur == "furieux":  # fumée qui sort des oreilles
        for k, (dx, dy) in enumerate(((-4, 2), (-7, -2), (13, 2), (16, -2))):
            d.ellipse([x + dx * e, y + dy * e, x + dx * e + 2 * e, y + dy * e + 2 * e], fill=h("blanc" if k % 2 else "gris"))


def client(im, x, y, e=3):
    sprite(im, CLIENT, x, y, {"C": "#8A5A3C", "P": "#D9A07A", "R": "#7A5CFF", "G": "#5A5F66", "K": "encre"}, e)
    d = ImageDraw.Draw(im)
    for cx in (4, 7):
        d.rectangle([x + cx * e, y + 4 * e, x + cx * e + e - 1, y + 4 * e + e - 1], fill=h("encre"))
    for cx in range(4, 8):  # grand sourire
        d.rectangle([x + cx * e, y + 6 * e, x + cx * e + e - 1, y + 6 * e + e - 1], fill=h("encre"))


def patience(im, v):
    """Jauge en haut : PATIENCE v/20, verte, puis jaune, puis rouge."""
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 16], fill=h("noir"))
    texte(d, (4, 5), "PATIENCE", "blanc")
    d.rectangle([72, 5, 132, 12], fill=h("rouge2"))
    col = "vert" if v > 12 else "jaune" if v > 5 else "rouge"
    if v:
        d.rectangle([72, 5, 72 + int(60 * v / 20), 12], fill=h(col))
    texte(d, (138, 5), f"{v:>2}/20", col)


def dialogue(d, lignes, y0=226):
    cadre(d, [6, y0, 174, 312], 3)
    y = y0 + 12
    for l, c in lignes:
        texte(d, (14, y), l, c)
        y += 12


def carrelage(d, y0, y1, c1, c2, pas=10):
    for y in range(y0, y1, pas):
        for x in range(0, W, pas):
            d.rectangle([x, y, x + pas - 1, y + pas - 1], fill=h(c1 if ((x + y) // pas) % 2 else c2))


def heure(d, t, couleur="jaune"):
    cadre(d, [108, 22, 174, 38], 2, "noir", couleur)
    texte(d, (113, 27), t, couleur)


# ——— 1. 6 h 58 : le téléphone sonne au lit (l'accroche) ———
def s1():
    im = Image.new("RGB", (W, H), h("#141A33"))
    d = ImageDraw.Draw(im)
    carrelage(d, 40, 226, "#1C2444", "#19203D", 12)
    d.rectangle([30, 90, 130, 190], fill=h("#6B4A8E"), outline=h("encre"))  # lit
    d.rectangle([30, 90, 130, 112], fill=h("papier2"), outline=h("encre"))
    d.rectangle([30, 130, 130, 190], fill=h("#4E7BC0"), outline=h("encre"))
    sprite(im, ["..HHHH..", ".HPPPPH.", ".PKPPKP.", ".PPPPPP.", "..PPPP.."], 64, 104, {"H": "cheveux", "P": "peau", "K": "encre"}, 3)
    d.rectangle([136, 120, 160, 150], fill=h("bois"), outline=h("bois2"))  # table de nuit
    d.rectangle([142, 112, 154, 126], fill=h("encre"), outline=h("blanc"))  # téléphone
    d.rectangle([144, 114, 152, 122], fill=h("bleu"))
    for r in (10, 16):
        d.arc([148 - r, 119 - r, 148 + r, 119 + r], 200, 340, fill=h("jaune"))
    texte(d, (130, 84), "BZZZ", "jaune")
    heure(d, "6 H 58")
    patience(im, 20)
    dialogue(d, [("* Un client.", "blanc"), ("* « Juste une", "jaune"), ("  petite question »", "jaune"),
                 ("* Il est 6 h 58.", "gris")])
    return im


# ——— 2. 9 h 40 : le fournisseur ———
def s2():
    im = Image.new("RGB", (W, H), h("#2A2A2A"))
    d = ImageDraw.Draw(im)
    for y in (48, 78, 108):  # rayonnages
        d.rectangle([0, y, W, y + 4], fill=h("bois2"))
        for x in range(4, W, 14):
            d.rectangle([x, y - 12, x + 10, y - 1], fill=h(random.Random(x + y).choice(["#C0C0C0", "orange2", "bleu", "vert2"])))
    d.rectangle([0, 150, W, 170], fill=h("bois"), outline=h("bois2"))  # comptoir
    client(im, 72, 100)  # le vendeur, derrière le comptoir
    perso(im, 74, 176, "agace")
    cadre(d, [104, 64, 176, 92], 2, "blanc", "blanc")
    d.text((108, 68), "RUPTURE.", font=F8, fill=h("encre"))
    d.text((108, 80), "MARDI.", font=F8, fill=h("rouge"))
    heure(d, "9 H 40")
    patience(im, 14)
    dialogue(d, [("* Ta pièce ?", "blanc"), ("* Plus en stock.", "blanc"), ("* Ton chantier", "jaune"), ("  attend.", "jaune"),
                 ("* Toi aussi.", "gris")])
    return im


# ——— 3. 13 h 10 : le camion ———
def s3():
    im = Image.new("RGB", (W, H), h("#6FA8C9"))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 150, W, 226], fill=h("#4A4F55"))
    for x in range(0, W, 30):
        d.rectangle([x, 186, x + 16, 189], fill=h("blanc"))
    d.rectangle([0, 140, W, 150], fill=h("#9AA0A6"))
    d.rectangle([20, 96, 120, 150], fill=h("blanc"), outline=h("encre"))  # camion
    d.rectangle([120, 112, 158, 150], fill=h("papier2"), outline=h("encre"))
    d.rectangle([126, 116, 152, 130], fill=h("#2F4A66"))
    d.rectangle([20, 132, 158, 136], fill=h("#2F5D9E"))
    for cx in (46, 136):
        d.ellipse([cx - 10, 140, cx + 10, 160], fill=h("encre"))
        d.ellipse([cx - 4, 146, cx + 4, 154], fill=h("gris"))
    d.polygon([(128, 117), (146, 115), (147, 127), (129, 129)], fill=h("jaune"), outline=h("encre"))  # l'amende
    d.line([132, 121, 142, 120], fill=h("encre"))
    perso(im, 60, 160, "enerve")
    cadre(d, [70, 56, 174, 84], 2, "blanc", "blanc")
    d.text((74, 60), "35 EUROS.", font=F8, fill=h("rouge"))
    d.text((74, 72), "BON APPETIT.", font=F8, fill=h("encre"))
    heure(d, "13 H 10")
    patience(im, 9)
    dialogue(d, [("* 4 minutes de", "blanc"), ("  livraison.", "blanc"), ("* Un papier jaune", "jaune"),
                 ("  sur le pare-brise.", "jaune")])
    return im


# ——— 4. 17 h 30 : chez le client ———
def s4():
    im = Image.new("RGB", (W, H), h("#E9DCC2"))
    d = ImageDraw.Draw(im)
    carrelage(d, 40, 226, "#CFE3E8", "#B9D3DA", 10)
    d.rectangle([120, 60, 168, 130], fill=h("#F4F4F4"), outline=h("encre"))  # le meuble posé
    d.rectangle([126, 70, 162, 90], fill=h("#2F7A9E"), outline=h("encre"))
    texte(d, (128, 136), "NEUF", "vert2")
    client(im, 20, 120)
    perso(im, 74, 128, "enerve")
    cadre(d, [10, 52, 112, 92], 2, "blanc", "blanc")
    d.text((14, 56), "EN FAIT...", font=F8, fill=h("encre"))
    d.text((14, 68), "ON PREFERE", font=F8, fill=h("encre"))
    d.text((14, 80), "LE BLANC.", font=F8, fill=h("violet"))
    heure(d, "17 H 30")
    patience(im, 4)
    dialogue(d, [("* Meuble posé.", "blanc"), ("* Raccordé.", "blanc"), ("* Joint fait.", "blanc"),
                 ("* Il est bleu.", "jaune"), ("", "blanc")])
    return im


# ——— 5. 21 h : le SMS de trop, il pète un câble ———
def s5():
    im = Image.new("RGB", (W, H), h("#3A0E12"))
    d = ImageDraw.Draw(im)
    for k in range(18):  # rayons rouges
        a = k / 18 * math.tau
        d.polygon([(90, 130), (90 + math.cos(a) * 260, 130 + math.sin(a) * 260),
                   (90 + math.cos(a + 0.12) * 260, 130 + math.sin(a + 0.12) * 260)], fill=h("#5A1418"))
    random.seed(4)
    for k in range(16):  # les devis s'envolent
        x, y, r = random.randint(4, 166), random.randint(40, 214), random.random()
        d.polygon([(x, y), (x + 10, y + 2 * r), (x + 9, y + 13), (x - 1, y + 11)], fill=h("papier"), outline=h("encre"))
        d.line([x + 2, y + 5, x + 7, y + 5], fill=h("gris"))
    d.polygon([(40, 196), (140, 196), (150, 210), (30, 210)], fill=h("bois"), outline=h("bois2"))  # table renversée
    d.rectangle([36, 210, 42, 222], fill=h("bois2")), d.rectangle([138, 210, 144, 222], fill=h("bois2"))
    d.rectangle([124, 88, 138, 102], fill=h("#BBBBBB"), outline=h("encre"))  # la calculatrice qui vole
    d.rectangle([126, 90, 136, 94], fill=h("vert2"))
    perso(im, 72, 134, "furieux")
    sprite(im, ["K..K", ".KK.", "K..K"], 20, 120, {"K": "jaune"}, 3)
    sprite(im, ["K..K", ".KK.", "K..K"], 150, 150, {"K": "jaune"}, 3)
    cadre(d, [8, 44, 128, 80], 2, "blanc", "blanc")  # le SMS
    d.text((12, 48), "Mme FONTAINE", font=F8, fill=h("gris"))
    d.text((12, 60), "ALORS CE DEVIS", font=F8, fill=h("encre"))
    d.text((12, 69), "? :)", font=F8, fill=h("encre"))
    heure(d, "21 H", "rouge")
    patience(im, 0)
    dialogue(d, [("* Trois devis", "blanc"), ("  à faire.", "blanc"), ("* Patience : 0.", "rouge"),
                 ("* Tu pètes", "rouge"), ("  un câble.", "rouge")])
    return im


# ——— 6. 21 h 01 : il dicte ———
def s6():
    im = Image.new("RGB", (W, H), h("#1B1430"))
    d = ImageDraw.Draw(im)
    carrelage(d, 40, 226, "#2A2140", "#231B36", 10)
    random.seed(4)
    for k in range(10):
        x, y = random.randint(4, 166), random.randint(150, 214)
        d.rectangle([x, y, x + 10, y + 6], fill=h("papier2"), outline=h("encre"))
    perso(im, 28, 120, "agace")
    cadre(d, [90, 46, 172, 214], 3, "#F6F2EA", "encre")  # le téléphone
    d.rectangle([96, 52, 166, 63], fill=h("orange"))
    d.text((100, 54), "DIKTEO", font=F8, fill=h("blanc"))
    for i, (t, p) in enumerate((("BALLON", "520"), ("POSE", "180"), ("RACCORDS", "64"))):
        d.text((98, 70 + i * 20), t, font=F8, fill=h("encre"))
        d.text((164 - 8 * len(p), 79 + i * 20), p, font=F8, fill=h("orange2"))
    d.line([98, 132, 164, 132], fill=h("encre"))
    d.text((98, 138), "TOTAL", font=F8, fill=h("encre"))
    d.text((124, 150), "764 E", font=F8, fill=h("vert2"))
    d.ellipse([117, 176, 145, 204], fill=h("orange"), outline=h("encre"))  # le micro
    sprite(im, [".KK.", "KKKK", "KKKK", ".KK.", "K..K", ".KK."], 127, 180, {"K": "blanc"}, 2)
    heure(d, "21 H 01", "orange")
    patience(im, 2)
    dialogue(d, [("* Tu prends le", "blanc"), ("  téléphone.", "blanc"), ("* Tu DICTES.", "orange"),
                 ("* 30 secondes.", "jaune"), ("", "blanc")])
    return im


# ——— 7. 21 h 03 : accepté, soirée sauvée ———
def s7():
    im = Image.new("RGB", (W, H), h("#1E2A24"))
    d = ImageDraw.Draw(im)
    carrelage(d, 40, 226, "#26382F", "#213129", 10)
    d.rectangle([20, 140, 160, 190], fill=h("#8E5A3C"), outline=h("encre"))  # canapé
    d.rectangle([20, 124, 160, 144], fill=h("#A86C48"), outline=h("encre"))
    perso(im, 72, 114, "soulage")
    d.ellipse([110, 170, 134, 180], fill=h("blanc"), outline=h("encre"))  # assiette de pâtes
    d.ellipse([114, 168, 130, 176], fill=h("jaune"))
    cadre(d, [8, 46, 172, 80], 2, "blanc", "vert")  # notification
    d.rectangle([14, 54, 26, 66], fill=h("orange"))
    d.text((32, 52), "DIKTEO", font=F8, fill=h("gris"))
    d.text((32, 64), "DEVIS ACCEPTE", font=F8, fill=h("vert2"))
    heure(d, "21 H 03", "vert")
    patience(im, 20)
    dialogue(d, [("* Mme Fontaine a", "blanc"), ("  ACCEPTÉ.", "vert"), ("* Les pâtes sont", "blanc"),
                 ("  encore chaudes.", "blanc"), ("* Soirée sauvée.", "jaune")])
    return im


# ——— 8. Carton de fin ———
def s8():
    im = Image.new("RGB", (W, H), h("noir"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([62, 70, 118, 126], 10, fill=h("orange"))
    d.text((80, 86), "D", font=F8.font_variant(size=24), fill=h("blanc"))
    texte(d, (54, 140), "DIKTEO", "blanc")
    texte(d, (18, 176), "Le devis du soir,", "orange")
    texte(d, (18, 190), "dicté en 30 s.", "orange")
    cadre(d, [14, 226, 166, 262], 2, "noir", "jaune")
    texte(d, (24, 234), "GRATUIT", "jaune")
    texte(d, (24, 248), "3 devis par mois", "blanc")
    texte(d, (28, 290), "diktéo.fr", "gris")
    return im


if __name__ == "__main__":
    ims = [s1(), s2(), s3(), s4(), s5(), s6(), s7(), s8()]
    for i, im in enumerate(ims, 1):
        im.resize((W * X, H * X), Image.NEAREST).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"journee_{i}.png"))
    planche = Image.new("RGB", (W * 4 + 18, H * 2 + 6), h("#1A1A1A"))
    for i, im in enumerate(ims):
        planche.paste(im, ((i % 4) * (W + 6), (i // 4) * (H + 6)))
    planche.resize((planche.width * 2, planche.height * 2), Image.NEAREST).save(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "planche_journee.png"))
    print("ok")
