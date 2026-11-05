"""La journée en pixel HD, animée : chaque fonction renvoie l'image native 270×480 à l'instant t (secondes dans la scène)."""
import math
import random

from PIL import Image, ImageDraw

import hd
from hd import H, W, F16, c, cadre, degrade, dialogue, grille, hud, papier, perso, telephone_pixel, texte

# Durées et coups : (durée, heure, patience au début, coup (instant, points))
SCENES = [
    ("reveil", 4.6, "6 H 58", 20, (3.4, 3)),
    ("bouchon", 4.2, "8 H 15", 17, (3.0, 2)),
    ("fournisseur", 4.4, "9 H 40", 15, (3.2, 4)),
    ("amende", 4.2, "13 H 10", 11, (3.0, 3)),
    ("client", 4.6, "17 H 30", 8, (3.4, 4)),
    ("soir", 6.4, "21 H 00", 4, (1.9, 4)),
    ("telephone", 3.0, "21 H 04", 0, None),
]

import personnage

VENDEUR2 = dict(lunettes=False, barbe=False, cols=(("cheveux", "#8C8C90"), ("cheveux_c", "#A8A8AC"), ("pull", "#3A6EA8"),
                ("pull_c", "#5A8EC8"), ("pull_o", "#2A5280"), ("peau", "#E0AC8C"), ("peau_c", "#F0C4A4"), ("peau_o", "#B8846A")))
CLIENT2 = dict(lunettes=False, barbe=False, bouche="sourire", cols=(("cheveux", "#7A4A2A"), ("cheveux_c", "#9A6440"), ("pull", "#8A5CC8"),
               ("pull_c", "#A87CE0"), ("pull_o", "#6A40A0"), ("jean", "#4A4A55"), ("jean_c", "#5E5E6A"), ("jean_o", "#3A3A44"),
               ("peau", "#8E5E44"), ("peau_c", "#A87458"), ("peau_o", "#6E4632")))
_c2 = {}


def autre(im, pose, x, y, k=1.0):
    cle = (tuple(sorted((a, b) for a, b in pose.items())), k)
    if cle not in _c2:
        _c2[cle] = personnage.rendre(pose, k)
    s_ = _c2[cle]
    im.paste(s_, (int(x), int(y)), s_)


def tete(im, x, y, k=1.0, **pose):
    s_ = personnage.rendre(pose, k)
    s_ = s_.crop((0, 0, s_.width, int(31 * k)))
    im.paste(s_, (int(x), int(y)), s_)


VENDEUR = {"h": "#8A8A8A", "H": "#A8A8A8", "g": "l", "v": "#3A6EA8", "V": "#2A5280", "L": "#5A8EC8", "b": "S"}
CLIENTE = {"h": "#6A3A2A", "H": "#8A5236", "g": "l", "b": "l", "v": "#8A5CC8", "V": "#6A40A0", "L": "#A87CE0", "j": "#4A4A55", "J": "#3A3A44"}


def perso_pal(im, pal, x, y, e=2):
    grille(im, hd.PERSO, x, y, pal, e)
    d = ImageDraw.Draw(im)
    for cx in (9, 14):
        d.rectangle([x + cx * e, y + 7 * e, x + cx * e + e - 1, y + 7 * e + e - 1], fill=c("o"))
    for cx in range(10, 14):
        d.rectangle([x + cx * e, y + 11 * e, x + cx * e + e - 1, y + 11 * e + e - 1], fill=c("m"))


def bulle(d, box, lignes, queue=None):
    cadre(d, box, 2, "blanc", "o")
    if queue:
        d.polygon(queue, fill=c("blanc"), outline=c("o"))
    y = box[1] + 7
    for l, col in lignes:
        texte(d, (box[0] + 7, y), l, col)
        y += 12


import numpy as np

_YY, _XX = np.mgrid[0:H, 0:W]
_DAMIER = ((_XX + _YY) % 2 == 0)


def _maj(im, a):
    im.paste(Image.fromarray(a.astype(np.uint8)))


def ombre(im, cx, y, w):
    """Ombre douce au sol sous un personnage ou un objet (tramée, pour rester pixel)."""
    a = np.asarray(im).astype(np.int16)
    m = (((_XX - cx) / (w / 2)) ** 2 + ((_YY - y) / 3.5) ** 2 <= 1) & _DAMIER
    a[m] = a[m] * 6 // 10
    _maj(im, a)


def voile(im, poly, col, force=0.35):
    """Rayon de lumière tramé (un pixel sur deux) : lumière douce sans flou."""
    mk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mk).polygon(poly, fill=255)
    m = (np.asarray(mk) > 0) & _DAMIER
    a = np.asarray(im).astype(np.float32)
    a[m] = a[m] + (np.array(c(col), np.float32) - a[m]) * force
    _maj(im, a)


_TEX = {}


def texture(im, box, force=10, graine=0):
    """Grain léger sur un mur ou un sol, pour casser les aplats."""
    if graine not in _TEX:
        rng = np.random.default_rng(graine)
        _TEX[graine] = ((rng.random((H, W)) < 0.18) * rng.choice((-1, 1), (H, W))).astype(np.int16)
    x0, y0, x1, y1 = box
    a = np.asarray(im).astype(np.int16)
    a[y0:y1, x0:x1] += (_TEX[graine][y0:y1, x0:x1] * force)[..., None]
    _maj(im, np.clip(a, 0, 255))


def cuisine(im, d, colere=False):
    """La cuisine, le soir : placards, frigo, fenêtre avec la lune, horloge."""
    if colere:
        return
    d.rectangle([0, 120, 70, 150], fill=c("#3A2E4A"), outline=c("o"))
    d.rectangle([200, 120, 270, 150], fill=c("#3A2E4A"), outline=c("o"))
    for x in (35, 235):
        d.line([x, 120, x, 150], fill=c("o"))
        d.rectangle([x - 6, 133, x - 4, 137], fill=c("gris2"))
        d.rectangle([x + 4, 133, x + 6, 137], fill=c("gris2"))
    d.rectangle([214, 156, 262, 258], fill=c("#5A5A6E"), outline=c("o"))
    d.line([214, 190, 262, 190], fill=c("o"))
    d.rectangle([254, 166, 256, 182], fill=c("gris"))
    d.rectangle([254, 198, 256, 216], fill=c("gris"))
    d.rectangle([10, 160, 64, 220], fill=c("#0E1430"), outline=c("o"))
    d.ellipse([40, 168, 54, 182], fill=c("#E8E2C8"))
    d.ellipse([44, 166, 58, 180], fill=c("#0E1430"))
    for (x, y) in ((18, 172), (28, 196), (52, 206)):
        d.point((x, y), fill=c("blanc"))
    d.line([37, 160, 37, 220], fill=c("o"))
    d.line([10, 190, 64, 190], fill=c("o"))
    d.ellipse([170, 122, 192, 144], fill=c("papier"), outline=c("o"))
    d.line([181, 133, 181, 125], fill=c("o"))
    d.line([181, 133, 175, 135], fill=c("o"))


# ——— 1. 6 h 58, le réveil ———
def reveil(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    degrade(d, (0, 44, W, 260), "#141A3A", "#2A2550", 6)
    d.rectangle([0, 260, W, H], fill=c("#231E3C"))
    for x in range(0, W, 18):
        d.line([x, 260, x - 30, H], fill=c("#1C1832"))
    # fenêtre, l'aube
    d.rectangle([150, 70, 240, 160], fill=c("#3A3A6A"), outline=c("o"))
    degrade(d, (154, 74, 236, 156), "#2A3A7A", "#E87A4A", 6)
    d.line([195, 70, 195, 160], fill=c("o"), width=2)
    d.line([150, 115, 240, 115], fill=c("o"), width=2)
    texture(im, (0, 44, W, 260), 6, 1)
    d.rectangle([30, 120, 84, 166], fill=c("bois2"), outline=c("o"))
    d.rectangle([34, 124, 80, 162], fill=c("#6FA8C9"))
    d.polygon([(34, 162), (50, 140), (62, 152), (70, 144), (80, 162)], fill=c("#3E6A4A"))
    d.ellipse([196, 350, 266, 382], fill=c("#5A3A5A"), outline=c("#3A2440"))
    voile(im, [(154, 156), (236, 156), (270, 330), (120, 330)], "#F0A060", 0.22)
    # lit
    d.rectangle([20, 250, 190, 340], fill=c("#4A3A6A"), outline=c("o"))
    d.rectangle([24, 254, 92, 284], fill=c("papier2"), outline=c("o"))
    d.rectangle([20, 290, 190, 360], fill=c("#3E68B0"), outline=c("o"))
    for y in range(298, 360, 12):
        d.line([22, y, 188, y], fill=c("#335A9C"))
    eveille = t > 0.9
    tete(im, 36, 226, 1.0, **({"yeux": "fermes"} if not eveille else {"sourcils": "haut", "yeux": "grands"}))
    d.rectangle([20, 254, 190, 258], fill=c("#3E68B0"))
    if eveille:
        texte(d, (96, 230), "!", "jaune", F16)
    # table de nuit + téléphone
    ombre(im, 105, 362, 170)
    d.rectangle([200, 300, 250, 360], fill=c("bois"), outline=c("o"))
    d.rectangle([204, 310, 246, 314], fill=c("bois2"))
    telephone_pixel(d, 218, 276, allume=0.6, vibre=1.0 if t < 3.0 else 0, t=t)
    if t < 3.0 and int(t * 6) % 2:
        texte(d, (196, 252), "BZZZ", "jaune")
    hud(im, "6 H 58", 20 - (3 if t >= 3.4 else 0), (3.4, 3), t)
    dialogue(d, [("* 6 h 58. Un client.", "blanc"), ("* « Juste une petite", "jaune"), ("  question... »", "jaune")], t - 0.3)
    return im


# ——— 2. 8 h 15, le bouchon ———
def bouchon(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    degrade(d, (0, 44, W, 230), "#7EC2E8", "#F2D9A8", 6)
    for k, (x, hh) in enumerate(((0, 90), (40, 130), (90, 70), (130, 150), (190, 100), (230, 120))):
        d.rectangle([x, 230 - hh, x + 44, 230], fill=c("#8A9AB0" if k % 2 else "#7A889E"), outline=c("#5E6A80"))
        for wy in range(230 - hh + 8, 224, 14):
            for wx in range(x + 6, x + 40, 12):
                d.rectangle([wx, wy, wx + 5, wy + 7], fill=c("#C8DCEC"))
    for k, (x, y) in enumerate(((30, 70), (150, 60), (230, 90))):
        xx = (x + t * 6 + k * 40) % (W + 60) - 40
        for dx, r in ((0, 9), (10, 12), (22, 8)):
            d.ellipse([xx + dx - r, y - r // 2, xx + dx + r, y + r // 2], fill=c("#F4F4F0"))
    d.rectangle([0, 230, W, H], fill=c("#4A4F58"))
    texture(im, (0, 230, W, H), 7, 2)
    d.rectangle([0, 226, W, 232], fill=c("#9AA0A6"))
    d.rectangle([256, 150, 260, 230], fill=c("#2A2A30"))
    d.rectangle([250, 140, 266, 176], fill=c("#2A2A30"), outline=c("o"))
    d.ellipse([254, 144, 262, 152], fill=c("rouge"))
    d.ellipse([254, 154, 262, 162], fill=c("#3A3A30"))
    d.ellipse([254, 164, 262, 172], fill=c("#2A3A2A"))
    for x in range(-40, W, 40):
        xx = x + int(t * 3) % 40
        d.rectangle([xx, 300, xx + 20, 303], fill=c("blanc"))
    # voitures à l'arrêt
    for x, col in ((-30, "rouge"), (180, "bleu"), (240, "jaune")):
        d.rounded_rectangle([x, 250, x + 60, 282], 6, fill=c(col), outline=c("o"))
        d.rectangle([x + 12, 254, x + 44, 266], fill=c("#C8DCEC"), outline=c("o"))
        for wx in (x + 12, x + 48):
            d.ellipse([wx - 7, 276, wx + 7, 290], fill=c("o"))
    # le camion du plombier
    x0 = 52
    ombre(im, x0 + 64, 306, 140)
    for k in range(3):
        ph = (t * 1.5 + k / 3) % 1
        r = 3 + int(ph * 6)
        cx, cy = x0 - 6 - ph * 18, 292 - ph * 14
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c("#8A8F98" if ph < 0.6 else "#B0B4BA"))
    d.rectangle([x0, 230, x0 + 96, 296], fill=c("blanc"), outline=c("o"))
    d.rectangle([x0 + 96, 248, x0 + 126, 296], fill=c("papier2"), outline=c("o"))
    d.rectangle([x0 + 100, 252, x0 + 122, 272], fill=c("#C8DCEC"), outline=c("o"))
    tete(im, x0 + 100, 250, 0.62, sourcils="colere")
    d.rectangle([x0, 276, x0 + 126, 282], fill=c("orange"))
    texte(d, (x0 + 8, 254), "PLOMBERIE", "bleu2")
    for wx in (x0 + 24, x0 + 104):
        d.ellipse([wx - 10, 286, wx + 10, 306], fill=c("o"))
        d.ellipse([wx - 4, 292, wx + 4, 300], fill=c("gris"))
    if int(t * 4) % 2:
        texte(d, (190, 214), "TUUUT", "rouge")
        texte(d, (6, 214), "TUT !", "jaune")
    hud(im, "8 H 15", 17 - (2 if t >= 3.0 else 0), (3.0, 2), t)
    dialogue(d, [("* Bouchon.", "blanc"), ("* Le chantier de 8 h", "blanc"), ("  t'attend depuis 8 h.", "jaune")], t - 0.2)
    return im


# ——— 3. 9 h 40, le fournisseur ———
def fournisseur(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 44, W, H], fill=c("#3A3A44"))
    rng = random.Random(4)
    for y in (90, 140, 190):
        d.rectangle([0, y, W, y + 5], fill=c("bois2"))
        for x in range(4, W, 22):
            col = rng.choice(["#C0C4CC", "orange2", "bleu2", "vert2", "#B8A070"])
            d.rectangle([x, y - 26, x + 18, y - 1], fill=c(col), outline=c("o"))
            d.rectangle([x + 4, y - 18, x + 14, y - 12], fill=c("papier"))
    autre(im, VENDEUR2, 114, 168)
    d.rectangle([0, 238, W, 268], fill=c("bois3"), outline=c("o"))
    d.rectangle([0, 268, W, H], fill=c("bois2"))
    for x in (40, 135, 230):
        d.rectangle([x - 22, 46, x + 22, 49], fill=c("#E8F4FF"))
        voile(im, [(x - 22, 50), (x + 22, 50), (x + 40, 236), (x - 40, 236)], "#E8F4FF", 0.10)
    for y in range(282, H, 16):
        d.line([0, y, W, y], fill=c("#4A2C1A"))
    texture(im, (0, 268, W, H), 6, 3)
    perso(im, 112, 290, "agace" if t > 1.4 else "calme", 2, t, jambes=False)
    if t > 0.6:
        bulle(d, [150, 140, 262, 176], [("RUPTURE.", "o"), ("MARDI.", "rouge")], [(156, 176), (166, 176), (150, 186)])
    hud(im, "9 H 40", 15 - (4 if t >= 3.2 else 0), (3.2, 4), t)
    dialogue(d, [("* Ta pièce ? Plus", "blanc"), ("  en stock.", "blanc"), ("* Ton chantier attend.", "jaune")], t - 0.3)
    return im


# ——— 4. 13 h 10, l'amende ———
def amende(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    degrade(d, (0, 44, W, 220), "#5AB0E8", "#BFE4F6", 5)
    d.rectangle([0, 200, W, 230], fill=c("#C9B89A"), outline=c("#9A8A6E"))
    d.rectangle([0, 230, W, H], fill=c("#4A4F58"))
    for x in range(0, W, 18):
        d.line([x, 200, x - 6, 230], fill=c("#A89878"))
    texture(im, (0, 230, W, H), 7, 4)
    d.rectangle([246, 110, 250, 226], fill=c("#3A3F48"))
    d.rectangle([236, 104, 258, 112], fill=c("#3A3F48"), outline=c("o"))
    d.rectangle([12, 150, 15, 226], fill=c("#5A5F6A"))
    d.rectangle([2, 128, 26, 152], fill=c("bleu2"), outline=c("o"))
    texte(d, (7, 133), "P", "blanc", F16)
    x0 = 30
    ombre(im, x0 + 95, 266, 200)
    d.rectangle([x0, 160, x0 + 140, 250], fill=c("blanc"), outline=c("o"))
    d.rectangle([x0 + 140, 186, x0 + 190, 250], fill=c("papier2"), outline=c("o"))
    d.rectangle([x0 + 146, 192, x0 + 184, 214], fill=c("#2F4A66"), outline=c("o"))
    d.rectangle([x0, 226, x0 + 190, 232], fill=c("orange"))
    texte(d, (x0 + 26, 190), "PLOMBERIE", "bleu2")
    for wx in (x0 + 34, x0 + 160):
        d.ellipse([wx - 13, 238, wx + 13, 264], fill=c("o"))
        d.ellipse([wx - 5, 246, wx + 5, 256], fill=c("gris"))
    if t > 0.5:
        k = min(1, (t - 0.5) * 3)
        d.polygon([(x0 + 150, 196), (x0 + 170, 194), (x0 + 171, 194 + 16 * k), (x0 + 151, 196 + 16 * k)], fill=c("jaune"), outline=c("o"))
    ombre(im, 208, 344, 34)
    perso(im, 196, 264, "enerve" if t > 1.4 else "calme", 2, t)
    if t > 1.0:
        bulle(d, [116, 128, 262, 164], [("35 EUROS.", "rouge"), ("BON APPETIT.", "o")], [(220, 164), (230, 164), (226, 176)])
    hud(im, "13 H 10", 11 - (3 if t >= 3.0 else 0), (3.0, 3), t)
    dialogue(d, [("* 4 minutes pour", "blanc"), ("  décharger.", "blanc"), ("* Un papier jaune.", "jaune")], t - 0.2)
    return im


# ——— 5. 17 h 30, « on préfère le blanc » ———
def client(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(44, H, 12):
        for x in range(0, W, 12):
            d.rectangle([x, y, x + 11, y + 11], fill=c("#CFE3E8" if ((x + y) // 12) % 2 else "#B9D3DA"), outline=c("#A8C4CC"))
    d.rectangle([60, 96, 120, 150], fill=c("#DDEEF4"), outline=c("o"))
    d.line([70, 104, 86, 120], fill=c("blanc"))
    d.line([74, 104, 96, 126], fill=c("blanc"))
    d.rectangle([128, 160, 150, 206], fill=c("#3E8A5A"), outline=c("o"))
    d.rectangle([132, 206, 146, 226], fill=c("#B86A3A"), outline=c("o"))
    ombre(im, 210, 254, 90)
    d.rectangle([170, 120, 250, 250], fill=c("bleu2"), outline=c("o"))
    d.rectangle([176, 130, 244, 180], fill=c("#C8E4F4"), outline=c("o"))
    d.rectangle([176, 190, 244, 244], fill=c("#244E86"), outline=c("o"))
    d.rectangle([205, 210, 215, 214], fill=c("blanc"))
    texte(d, (182, 256), "NEUF !", "vert2")
    ombre(im, 39, 312, 34)
    ombre(im, 116, 312, 34)
    autre(im, CLIENT2, 18, 230)
    perso(im, 92, 236, "enerve" if t > 1.6 else "content", 2, t)
    if t > 0.8:
        bulle(d, [8, 140, 150, 188], [("EN FAIT...", "o"), ("ON PRÉFÈRE", "o"), ("LE BLANC.", "violet")], [(30, 188), (40, 188), (34, 200)])
    hud(im, "17 H 30", 8 - (4 if t >= 3.4 else 0), (3.4, 4), t)
    dialogue(d, [("* Meuble posé. Raccordé.", "blanc"), ("* Joint fait.", "blanc"), ("* Il est bleu.", "jaune")], t - 0.4)
    return im


# ——— 6. 21 h, le SMS de trop : il pète un câble ———
def soir(t):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    colere = t >= 1.9
    degrade(d, (0, 44, W, 260), "#2A1E3A" if not colere else "#4A0E14", "#3E2E50" if not colere else "#7A1A1E", 5)
    d.rectangle([0, 260, W, H], fill=c("#2A2140" if not colere else "#3A0A10"))
    if colere:
        for k in range(16):
            a = k / 16 * math.tau + t * 0.6
            d.polygon([(135, 230), (135 + math.cos(a) * 400, 230 + math.sin(a) * 400),
                       (135 + math.cos(a + 0.14) * 400, 230 + math.sin(a + 0.14) * 400)], fill=c("#5A1218"))
    cuisine(im, d, colere=colere)
    if not colere:
        voile(im, [(118, 92), (152, 92), (210, 252), (60, 252)], "#FFD84D", 0.16)
    # lampe
    d.line([135, 44, 135, 90], fill=c("o"), width=2)
    d.polygon([(115, 90), (155, 90), (145, 78), (125, 78)], fill=c("jaune" if not colere else "orange"), outline=c("o"))
    sh = (int(math.sin(t * 80) * 3), int(math.cos(t * 70) * 3)) if colere else (0, 0)
    perso(im, 87 + sh[0], 144 + sh[1], "cri" if colere and t < 4.2 else "furieux" if colere else "fatigue", 4, t,
          jambes=False, rouge=0.35 if colere else 0)
    # table et piles de devis
    d.rectangle([20, 250, 250, 268], fill=c("bois3"), outline=c("o"))
    d.rectangle([30, 268, 40, 360], fill=c("bois2")), d.rectangle([230, 268, 240, 360], fill=c("bois2"))
    if not colere:
        for k in range(9):
            d.rectangle([40 + k * 3, 238 - k * 3, 76 + k * 3, 250 - k * 3], fill=c("papier"), outline=c("o"))
        for k in range(6):
            d.rectangle([180 - k * 2, 240 - k * 3, 214 - k * 2, 250 - k * 3], fill=c("papier"), outline=c("o"))
    else:
        rng = random.Random(7)
        u = t - 1.9
        for k in range(26):
            a = rng.uniform(-math.pi, 0)
            v = rng.uniform(60, 160)
            x = 135 + math.cos(a) * v * u
            y = 240 + math.sin(a) * v * u + 60 * u * u
            papier(d, x, y, rng.uniform(0, 6) + u * rng.uniform(-6, 6), 1.2)
        if int(t * 4) % 2:
            texte(d, (150, 170), "RAAAH !", "jaune", F16)
    # le SMS
    if 0.8 < t < 2.6:
        bulle(d, [14, 122, 200, 160], [("Mme FONTAINE", "gris2"), ("Alors ce devis ? :)", "o")])
    hud(im, "21 H 00", 4 if t < 1.9 else 0, (1.9, 4), t, "rouge" if colere else "jaune")
    if colere and t > 2.5:
        cadre(d, [30, 360, 240, 400], 3, "noir", "rouge")
        if int(t * 5) % 2:
            texte(d, (44, 374), "PATIENCE : 0", "rouge", F16)
    else:
        dialogue(d, [("* Trois devis à faire.", "blanc"), ("* Et un SMS.", "jaune")], t - 0.1)
    return im


# ——— 7. 21 h 04, il découvre l'appli ———
def telephone(t):
    """Il s'effondre sur la table ; le téléphone s'allume en orange : Diktéo."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    degrade(d, (0, 44, W, 260), "#120E1C", "#1E1830", 5)
    d.rectangle([0, 260, W, H], fill=c("#16121F"))
    rng = random.Random(3)
    for k in range(18):
        papier(d, rng.randint(10, 260), rng.randint(276, 372), rng.uniform(0, 6), 1.2)
    cuisine(im, d)
    a_ = np.asarray(im).astype(np.float32)
    a_[44:260] *= np.array([0.55, 0.55, 0.6], np.float32)
    _maj(im, a_)
    perso(im, 87, 144, "fatigue" if t < 1.6 else "surpris", 4, t, jambes=False)
    d.rectangle([20, 250, 250, 268], fill=c("bois3"), outline=c("o"))
    allume = min(1.0, max(0.0, (t - 0.5) * 2))
    telephone_pixel(d, 170, 224, allume=allume, vibre=0.6 if 0.5 < t < 1.4 else 0, t=t)
    if allume > 0:
        for r in (16, 26, 36):
            d.arc([177 - r, 236 - r, 177 + r, 236 + r], 0, 360, fill=tuple(int(v * allume * 0.6) for v in c("orange")))
    if t > 0.9:
        bulle(d, [120, 120, 262, 158], [("DIKTÉO", "orange2"), ("Dicte ton devis.", "o")], [(176, 158), (186, 158), (178, 212)])
    hud(im, "21 H 04", 0, None, t, "orange")
    dialogue(d, [("* Une notif.", "blanc"), ("* « Dicte ton devis. »", "orange")], t - 0.2)
    return im


def pov(t, kitchen_flou=True):
    """Vue subjective : ses mains de pixel tiennent le téléphone. Renvoie (image native, rectangle de l'écran natif)."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    degrade(d, (0, 0, W, H), "#1A1428", "#2A1A20", 5)
    rng = random.Random(5)
    for k in range(10):
        papier(d, rng.randint(0, 270), rng.randint(300, 480), rng.uniform(0, 6), 2.0)
    ecran = (78, 112, 192, 342)
    d.rounded_rectangle([ecran[0] - 8, ecran[1] - 10, ecran[2] + 8, ecran[3] + 12], 14, fill=c("o"))
    d.rounded_rectangle([ecran[0] - 6, ecran[1] - 8, ecran[2] + 6, ecran[3] + 10], 12, outline=c("#3A3F48"))
    # ses mains : paumes sur les bords, pouces sur l'écran, manches du pull vert qui sortent du cadre
    for sx in (-1, 1):
        bord = ecran[0] - 6 if sx < 0 else ecran[2] + 6
        d.polygon([(bord - sx * 34, 330), (bord + sx * 6, 300), (bord + sx * 30, 480), (bord - sx * 70, 480)], fill=c("v"), outline=c("o"))
        d.polygon([(bord - sx * 22, 380), (bord - sx * 60, 480), (bord - sx * 40, 480)], fill=c("V"))
        d.ellipse(sorted([bord - sx * 30, bord + sx * 12]) and [min(bord - sx * 30, bord + sx * 12), 262, max(bord - sx * 30, bord + sx * 12), 344],
                  fill=c("s"), outline=c("o"))
        d.ellipse([min(bord - sx * 26, bord + sx * 2), 300, max(bord - sx * 26, bord + sx * 2), 344], fill=c("S"))
        d.rounded_rectangle([min(bord, bord + sx * 18), 246, max(bord, bord + sx * 18), 292], 7, fill=c("l"), outline=c("o"))
    return im, ecran


def scene(nom, t):
    return {"reveil": reveil, "bouchon": bouchon, "fournisseur": fournisseur, "amende": amende, "client": client,
            "soir": soir, "telephone": telephone}[nom](t)


if __name__ == "__main__":
    import os
    ims = []
    for nom, du, *_ in SCENES:
        ims.append(scene(nom, du * 0.8))
    ims.append(pov(1)[0])
    pl = Image.new("RGB", (W * 4 + 18, H * 2 + 6), (26, 26, 26))
    for i, im in enumerate(ims):
        pl.paste(im, ((i % 4) * (W + 6), (i // 4) * (H + 6)))
    pl.save(os.path.join(hd.ICI, "..", "tmp", "ap", "journee_hd.png"))
