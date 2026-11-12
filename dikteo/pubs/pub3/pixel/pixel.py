"""Pixel art rétro de la pub Diktéo : sprites dessinés pixel par pixel, scène en 180×320, agrandie ×6 (1080×1920).
Usage : python pixel.py  → planche_pixel.png (deux écrans : le boss « devis » de 21 h, puis le bonus Diktéo)."""
import os

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
W, H, X = 180, 320, 6
POLICE = os.path.join(ICI, "PressStart2P-Regular.ttf")

PAL = {
    "K": "#14100E", "W": "#F6F2EA", "S": "#E7A97F", "s": "#C27E55", "R": "#E2553F", "r": "#A93421",
    "H": "#3B2A22", "h": "#22160F", "G": "#2E7A5C", "g": "#1F5641", "O": "#F07A1E", "o": "#B5530C",
    "B": "#34506A", "b": "#22364A", "N": "#2B211C", "M": "#7A2C1F", "Y": "#FFD84D", "P": "#0E1412",
}


def hexa(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def sprite(im, rows, x0, y0, remplace=None, e=1):
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if remplace and ch in remplace:
                ch = remplace[ch]
            for a in range(e):
                for b in range(e):
                    if 0 <= x0 + x * e + a < im.width and 0 <= y0 + y * e + b < im.height:
                        px[x0 + x * e + a, y0 + y * e + b] = hexa(PAL[ch])


# ——— L'artisan (24 × 44). Tête : sourcils en V (colère) ou détendus ; bouche ouverte ou sourire ———
TETE_COLERE = [
    "......KKKKKKKKKKKK......",
    ".....KHHHHHHHHHHHHK.....",
    "....KHHHHHHHHhHHHHHK....",
    "....KHHHhHHHHHHHHHHK....",
    "...KHHSSSSSSSSSSSSHHK...",
    "..KSKSSSSSSSSSSSSSSKSK..",
    "..KSKKKSSSSSSSSSSKKKSK..",
    "..KSSSKKKSSSSSSKKKSSSK..",
    "..KSSWWWKSSSSSSKWWWSSK..",
    "..KSSWKWSSSSSSSSWKWSSK..",
    "...KSSSSSSSssSSSSSSSK...",
    "...KSSSSSSSssSSSSSSSK...",
    "...KSSSKKKKKKKKKKSSSK...",
    "...KSSSKWWWWWWWWKSSSK...",
    "...KsSSKMMMMMMMMKSSsK...",
    "....KsSKMMRRRRMMKSsK....",
    ".....KsSKKKKKKKKSsK.....",
    "......KKsssssssKK.......",
    "........KssssK..........",
]
TETE_SOURIRE = TETE_COLERE[:5] + [
    "..KSKSSSSSSSSSSSSSSKSK..",
    "..KSSKKKSSSSSSSSKKKSSK..",
    "..KSSSSSSSSSSSSSSSSSSK..",
    "..KSSWWWSSSSSSSSWWWSSK..",
    "..KSSWKWSSSSSSSSWKWSSK..",
    "...KSSSSSSSssSSSSSSSK...",
    "...KSSSSSSSssSSSSSSSK...",
    "...KSSKSSSSSSSSSSKSSK...",
    "...KSSSKWWWWWWWWKSSSK...",
    "...KsSSSKMMMMMMKSSSsK...",
    "....KsSSSKKKKKKSSSsK....",
    ".....KsSSSSSSSSSSsK.....",
    "......KKsssssssKK.......",
    "........KssssK..........",
]
CORPS = [
    "....KKKKGGWWWWGGKKKK....",
    "...KGGGGGGKWWKGGGGGGK...",
    "..KGGGGGGGGKKGGGGGGggK..",
    "..KGGKKKKGGKKGGGGGGggK..",
    "..KGGKggKGGKKGGGGGGggK..",
    "..KGGKKKKGGKKGGGGGGggK..",
    "..KOOOOOOOOOOOOOOOOOOK..",
    "..KYYYYYYYYYYYYYYYYYYK..",
    "..KGGGGGGGGKKGGGGGGggK..",
    "..KGGGGGGGGKKGGGGGGggK..",
    "...KKKKKKKKKKKKKKKKKK...",
    "....KBBBBBK..KBBBBBK....",
    "....KBBBbBK..KBBBbBK....",
    "....KBBBbBK..KBBBbBK....",
    "....KBBBbBK..KBBBbBK....",
    "...KNNNNNNK..KNNNNNNK...",
    "...KKKKKKKK..KKKKKKKK...",
]
BRAS_CIEL = ["KKKK", "KSSK", "KSSK", "KKKK", "KGGK", "KGGK", "KGGK", "KGGK", "KOOK", "KYYK", "KGGK", "KGGK", "KGGK", "KGGK", "KGGK", "KGGK"]
COLERE = {"S": "R", "s": "r"}


def artisan(im, x, y, humeur="colere", bras_ciel=False, telephone=False, e=2):
    tete = TETE_COLERE if humeur == "colere" else TETE_SOURIRE
    rem = COLERE if humeur == "colere" else None
    if bras_ciel:
        for c in (-1, 1):
            sprite(im, BRAS_CIEL, x + (-2 if c < 0 else 22) * e, y + (len(tete) - 14) * e, rem, e)
    sprite(im, tete, x, y, rem, e)
    sprite(im, CORPS, x, y + len(tete) * e, None, e)
    if telephone:
        sprite(im, ["KSSK", "KSSK", "KGGK", "KGGK", "KGGK", "KGGK", "KGGK"], x - 3 * e, y + 13 * e, None, e)
        sprite(im, ["KKKKKK", "KPPPPK", "KPOPOK", "KPOOOK", "KPPPPK", "KPOYPK", "KKKKKK"], x - 5 * e, y + 6 * e, None, e)


# ——— Le boss : une pile de devis avec des yeux méchants (32 × 40) ———
def boss(im, x, y, e=2):
    d = ImageDraw.Draw(im)
    for k in range(11):
        dx = ((k * 7) % 5) - 2
        d.rectangle([x + dx * 2, y + 66 - k * 6, x + 58 + dx * 2, y + 71 - k * 6], fill=hexa(PAL["W"]), outline=hexa(PAL["K"]))
        d.line([x + 6 + dx * 2, y + 68 - k * 6, x + 40 + dx * 2, y + 68 - k * 6], fill=hexa("#B9B1A3"))
    d.rectangle([x + 4, y - 8, x + 54, y + 2], fill=hexa(PAL["R"]), outline=hexa(PAL["K"]))
    texte(d, (x + 9, y - 7), "DEVIS", "W", ombre=False)
    sprite(im, ["KKK......KKK", ".KKK....KKK.", "..KWWK.KWWK.", "..KWKK.KKWK.", "...KK...KK.."], x + 6, y + 10, None, e)
    sprite(im, ["K.K.K.K.K.K.K", "KWKWKWKWKWKWK", "KRRRRRRRRRRRK", "KKKKKKKKKKKKK"], x + 3, y + 30, None, e)
    for (bx, by) in ((x - 8, y + 4), (x + 64, y + 12), (x - 6, y + 40), (x + 66, y + 46)):
        sprite(im, ["..Y", ".Y.", "YYY", ".Y.", "Y.."], bx, by, None, 2)


def barre_boss(im, x, y, frac):
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + 70, y + 7], fill=hexa(PAL["P"]), outline=hexa(PAL["W"]))
    d.rectangle([x + 2, y + 2, x + 2 + int(66 * frac), y + 5], fill=hexa(PAL["R"]))


def coeurs(im, x, y, plein, total=5):
    C = [".KK.KK.", "KRRKRRK", "KRRRRRK", ".KRRRK.", "..KRK..", "...K..."]
    V = [".KK.KK.", "KbbKbbK", "KbbbbbK", ".KbbbK.", "..KbK..", "...K..."]
    for i in range(total):
        sprite(im, C if i < plein else V, x + i * 16, y, None, 2)


def texte(d, xy, t, couleur="W", ombre=True):
    """Texte en police pixel ; les majuscules accentuées absentes de la police sont dessinées (E + accent)."""
    f = ImageFont.truetype(POLICE, 8)
    accents = [i for i, c in enumerate(t) if c in "ÉÈ"]
    t = t.replace("É", "E").replace("È", "E")
    for dx, dy, c in ((1, 1, "K"), (0, 0, couleur)) if ombre else ((0, 0, couleur),):
        d.text((xy[0] + dx, xy[1] + dy), t, font=f, fill=hexa(PAL[c]))
        for i in accents:
            x, y = xy[0] + dx + i * 8, xy[1] + dy
            d.point([(x + 4, y - 3), (x + 5, y - 3), (x + 3, y - 2), (x + 4, y - 2)], fill=hexa(PAL[c]))


def fond_cuisine(im, chaud=False):
    d = ImageDraw.Draw(im)
    mur = ("#3A1A12", "#2C130D") if chaud else ("#1E2E28", "#18251F")
    for y in range(0, 230):
        d.line([0, y, W, y], fill=hexa(mur[(y // 8) % 2]))
    # fenêtre de nuit et sa lune
    d.rectangle([118, 46, 160, 86], fill=hexa("#0B1230"), outline=hexa(PAL["K"]))
    d.line([139, 46, 139, 86], fill=hexa(PAL["K"]))
    d.line([118, 66, 160, 66], fill=hexa(PAL["K"]))
    d.ellipse([146, 50, 154, 58], fill=hexa("#F3E9B5"))
    # sol en damier
    for y in range(230, H):
        for x in range(0, W, 8):
            on = ((x // 8) + (y // 8)) % 2
            d.line([x, y, x + 7, y], fill=hexa("#4A3426" if on else "#3B2A1F"))


def hud(im, plein, heure, niveau):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 30], fill=hexa(PAL["P"]))
    d.line([0, 30, W, 30], fill=hexa(PAL["O"]))
    d.line([0, 31, W, 31], fill=hexa(PAL["o"]))
    texte(d, (5, 4), "PATIENCE", "Y")
    coeurs(im, 5, 15, plein)
    texte(d, (118, 4), heure, "W")
    texte(d, (110, 16), niveau, "O")


def dialogue(im, lignes, y=248):
    d = ImageDraw.Draw(im)
    d.rectangle([6, y, W - 7, y + 14 + 11 * len(lignes)], fill=hexa(PAL["P"]), outline=hexa(PAL["W"]), width=2)
    for i, (t, c) in enumerate(lignes):
        texte(d, (13, y + 8 + i * 11), t, c, ombre=False)


def ecran_boss():
    im = Image.new("RGB", (W, H))
    fond_cuisine(im, chaud=True)
    d = ImageDraw.Draw(im)
    d.rectangle([96, 214, 176, 236], fill=hexa("#6B3D22"), outline=hexa(PAL["K"]))  # table
    d.rectangle([100, 236, 106, 250], fill=hexa("#4A2A16"), outline=hexa(PAL["K"]))
    d.rectangle([166, 236, 172, 250], fill=hexa("#4A2A16"), outline=hexa(PAL["K"]))
    boss(im, 108, 142)
    barre_boss(im, 104, 126, 1.0)
    artisan(im, 18, 134, "colere", bras_ciel=True)
    for (x, y) in ((6, 150), (0, 140), (70, 150), (76, 139)):
        d.rectangle([x, y, x + 6, y + 6], fill=hexa("#DADADA"), outline=hexa(PAL["K"]))
    hud(im, 0, "21:07", "BOSS")
    texte(d, (50, 50), "BOSS FINAL", "Y")
    texte(d, (34, 64), "LE DEVIS DE 21H", "R")
    dialogue(im, [("Le devis attaque !", "W"), ("Ta patience : 0", "R"), ("> Fuir    > Dicter", "Y")], y=262)
    return im


def ecran_bonus():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(0, 262):
        d.line([0, y, W, y], fill=hexa("#1E2E28" if (y // 8) % 2 else "#18251F"))
    for y in range(36, 262, 10):
        for x in range(-14, W, 14):
            o = 7 if (y // 10) % 2 else 0
            d.rectangle([x + o, y, x + 12 + o, y + 8], outline=hexa("#2A4038"))
    for y in range(262, H):
        for x in range(0, W, 8):
            d.line([x, y, x + 7, y], fill=hexa("#4A3426" if ((x // 8) + (y // 8)) % 2 else "#3B2A1F"))
    artisan(im, 30, 136, "sourire", telephone=True)
    # le bonus Diktéo : la bulle-micro orange, avec son halo
    for r, c in ((26, "#3A2A14"), (20, "#6B3D12")):
        d.ellipse([128 - r, 116 - r, 128 + r, 116 + r], fill=hexa(c))
    sprite(im, [
        "...KKKKKKKK...",
        "..KOOOOOOOOK..",
        ".KOOWWWWWWOOK.",
        ".KOWWOOOOWWOK.",
        ".KOWOOYOOOWOK.",
        ".KOWOOYYOOWOK.",
        ".KOWOOYOOOWOK.",
        ".KOWWOOOOWWOK.",
        ".KOOWWWWWOOOK.",
        "..KOOOOOOOOK..",
        "...KKKOOKK....",
        "......KK......",
    ], 114, 104, None, 2)
    for (x, y) in ((100, 90), (156, 96), (152, 138), (98, 136)):
        sprite(im, [".Y.", "YYY", ".Y."], x, y, None, 2)
    texte(d, (110, 74), "+100", "Y")
    hud(im, 5, "08:12", "NIV. 6")
    texte(d, (26, 44), "DEVIS ACCEPTÉ !", "Y")
    texte(d, (30, 58), "NIVEAU TERMINÉ", "W")
    dialogue(im, [("BONUS : DIKTÉO", "O"), ("Tu parles.", "W"), ("C'est fait.", "Y")], y=262)
    return im


if __name__ == "__main__":
    a, b = ecran_boss(), ecran_bonus()
    for nom, im in (("pixel_boss", a), ("pixel_bonus", b)):
        im.resize((W * X, H * X), Image.NEAREST).save(os.path.join(ICI, nom + ".png"))
    duo = Image.new("RGB", (W * 2 + 6, H), hexa(PAL["K"]))
    duo.paste(a, (0, 0))
    duo.paste(b, (W + 6, 0))
    duo.resize((duo.width * 4, duo.height * 4), Image.NEAREST).save(os.path.join(ICI, "planche_pixel.png"))
    print("ok")
