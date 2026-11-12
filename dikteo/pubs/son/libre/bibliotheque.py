"""Bibliothèque de bruitages libre de droits pour les pubs Diktéo (remplace celle du skill sound-effects).
Part des 12 enregistrements CC0 de son/sfx (freesound) et fabrique le reste par synthèse ou par dérivation
(hauteur, vitesse, couches). Tout est CC0 : les sons dérivés gardent le crédit de leur enregistrement d'origine.
python son/libre/bibliotheque.py [dossier]   (défaut : ~/.claude/skills/sound-effects/sfx, chemin lu par les son.py)
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "..", "sfx")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/skills/sound-effects/sfx")
RNG = np.random.default_rng(7)
CRED = {}
for ligne in open(os.path.join(SRC, "CREDITS.txt"), encoding="utf-8"):
    if " — " in ligne and ligne.split(" — ")[0].endswith(".ogg"):
        CRED[ligne.split(" — ")[0]] = " — ".join(ligne.strip().split(" — ")[1:])
MAISON = "synthèse maison Diktéo (numpy), CC0 1.0"
manifest = []


def lire(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, f), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def ecrire(nom, x, credit):
    x = np.asarray(x, np.float32)
    x = x / max(1e-6, np.abs(x).max()) * 0.89
    k = min(len(x) // 4, int(0.004 * SR))
    x[-k:] *= np.linspace(1, 0, k)
    chemin = os.path.join(OUT, nom)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    st = np.stack([x, x], 1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "libvorbis", "-q:a", "7", chemin],
                   input=st.tobytes(), check=True)
    manifest.append(dict(file=nom, credit=credit, license="CC0 1.0"))


def t(d):
    return np.arange(int(d * SR)) / SR


def filtre(x, typ, f, ordre=2):
    return sosfilt(butter(ordre, f, typ, fs=SR, output="sos"), x)


def env(d, a=0.002, decay=0.2, courbe=1.0):
    tt = t(d)
    return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / decay) ** courbe


def hauteur(x, demi_tons):
    """change hauteur et vitesse ensemble (bande accélérée), interpolation linéaire"""
    r = 2 ** (demi_tons / 12)
    i = np.arange(0, len(x) - 1, r)
    return np.interp(i, np.arange(len(x)), x)


def plus(*xs):
    """additionne des sons de longueurs différentes (le plus long fixe la durée)"""
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[: len(x)] += x
    return out


def place(dst, src, t0, g=1.0):
    a = int(t0 * SR)
    n = min(len(src), len(dst) - a)
    dst[a:a + n] += src[:n] * g
    return dst


def reverb(x, d=1.2, mix=0.25, couleur=6000):
    ir = RNG.standard_normal(int(d * SR)) * np.exp(-t(d) / (d / 6.9) * 1.0)
    ir = filtre(ir, "low", couleur)
    w = fftconvolve(x, ir)
    w = w / max(1e-6, np.abs(w).max()) * np.abs(x).max()
    y = np.zeros(len(w))
    y[: len(x)] += x
    return y * (1 - mix) + w * mix


def boom(f0, f1, d, bruit=0.3, coupe=3000, decay=None):
    tt = t(d)
    f = f1 + (f0 - f1) * np.exp(-tt * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    n = filtre(RNG.standard_normal(len(tt)), "low", coupe) * np.exp(-tt * 40)
    return (s + bruit * n) * env(d, 0.001, decay or d / 4)


def cloche(f, d, partiels=((1, 1), (2.0, .5), (3.0, .25)), decay=0.3):
    tt = t(d)
    s = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt / (decay / m ** .5)) for m, a in partiels)
    return s * np.minimum(1, tt / 0.002)


def karplus(f, d, clair=0.5):
    n = int(SR / f)
    buf = RNG.uniform(-1, 1, n)
    out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * (0.994 + 0.005 * clair)
    return out


def souffle(d, f0, f1, q=1.0, montee=0.5):
    """whoosh synthétique : bruit rose filtré passe-bande qui glisse de f0 à f1"""
    n = RNG.standard_normal(int(d * SR))
    tt = t(d)
    out = np.zeros_like(n)
    blocs = 64
    for b in range(blocs):
        a, z = len(n) * b // blocs, len(n) * (b + 1) // blocs
        fc = f0 * (f1 / f0) ** (b / blocs)
        lo, hi = fc / (1 + q), min(fc * (1 + q), SR / 2 - 100)
        out[a:z] = sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), n[max(0, a - 2000):z])[-(z - a):]
    e = np.sin(np.pi * np.minimum(1, (tt / d) / montee * 0.5) ) * np.minimum(1, (d - tt) / (d * (1 - montee) + 1e-3))
    return out * np.clip(e, 0, 1)


# ——— 1. les 12 enregistrements CC0, à leur place dans l'arborescence attendue ———
for nom, f in [("kit/click.ogg", "click.ogg"), ("kit/pop.ogg", "pop.ogg"), ("kit/impact.ogg", "impact.ogg"),
               ("pop/fs-447910-plop.ogg", "fs-447910-plop.ogg"), ("ding/fs-571513-soft-notifications-bell-ding-d.ogg", "fs-571513-soft-notifications-bell-ding-d.ogg"),
               ("transition/fs-816262-broomstick-whoosh-3-quiet-okm1.ogg", "fs-816262-broomstick-whoosh-3-quiet-okm1.ogg"),
               ("transition/fs-683096-woosh.ogg", "fs-683096-woosh.ogg"), ("transition/fs-786514-swoosh-v2.ogg", "fs-786514-swoosh-v2.ogg"),
               ("riser/fs-685256-riser-sound-effect-short-wav.ogg", "fs-685256-riser-sound-effect-short-wav.ogg"),
               ("tick/fs384187.ogg", "fs384187.ogg"), ("tick/fs528561.ogg", "fs528561.ogg")]:
    ecrire(nom, lire(f), CRED[f])

# ——— 2. dérivés d'enregistrements réels (meilleur grain qu'une synthèse pure) ———
W = lire("fs-683096-woosh.ogg")
SW = lire("fs-786514-swoosh-v2.ogg")
BR = lire("fs-816262-broomstick-whoosh-3-quiet-okm1.ogg")
CL = lire("click.ogg")
PO = lire("pop.ogg")
PL = lire("fs-447910-plop.ogg")
IM = lire("impact.ogg")
TK = lire("fs384187.ogg")
DG = lire("fs-571513-soft-notifications-bell-ding-d.ogg")
RT = lire("fs-426767-apartment-room-tone-wav.ogg")
c = lambda f: CRED[f] + " (dérivé : hauteur/vitesse/couches)"

ecrire("whoosh/fs-169867-swoosh.ogg", plus(hauteur(SW, -2), 0.5 * souffle(0.34, 500, 3000, 1.2)), c("fs-786514-swoosh-v2.ogg"))
ecrire("whoosh/fs-683101-quick-woosh.ogg", hauteur(BR, 2), c("fs-816262-broomstick-whoosh-3-quiet-okm1.ogg"))
ecrire("whoosh/fs830856.ogg", hauteur(W, 5), c("fs-683096-woosh.ogg"))
ecrire("whoosh/fs-830856.ogg", hauteur(W, 5), c("fs-683096-woosh.ogg"))
ecrire("whoosh/fs-264777-swoosh.ogg", hauteur(SW, 3), c("fs-786514-swoosh-v2.ogg"))
ecrire("whoosh/fs-127197-fast-simple-chop-5-aif.ogg", plus(hauteur(BR, 5), 0.6 * place(np.zeros(int(.3 * SR)), boom(400, 120, .12, .8, 5000), .05)), c("fs-816262-broomstick-whoosh-3-quiet-okm1.ogg"))
ecrire("transition/fs-850347-swipe-various.ogg", np.concatenate([hauteur(SW, 4), hauteur(SW, 6)[: int(.2 * SR)]]), c("fs-786514-swoosh-v2.ogg"))
ecrire("riser/fs-174363-rewind.ogg", hauteur(W[::-1], 3) * np.linspace(0.3, 1, len(hauteur(W[::-1], 3))), c("fs-683096-woosh.ogg"))
ecrire("pop/fs-824189-pop-in-sfx.ogg", place(hauteur(PL, 3).copy(), hauteur(PO, -2), 0, 0.5), c("fs-447910-plop.ogg"))
ecrire("pop/kenney-interface-drop-001.ogg", place(place(np.zeros(int(.35 * SR)), hauteur(PO, -5), 0), boom(220, 90, .25, .1), 0, .6), c("pop.ogg"))
ecrire("pop/kenney-interface-drop-002.ogg", place(place(np.zeros(int(.35 * SR)), hauteur(PO, -3), 0), boom(260, 110, .22, .1), 0, .5), c("pop.ogg"))
ecrire("pop/kenney-interface-drop-003.ogg", place(place(np.zeros(int(.35 * SR)), hauteur(PO, -7), 0), boom(180, 70, .3, .1), 0, .6), c("pop.ogg"))
ecrire("click/kenney-interface-toggle-001.ogg", place(place(np.zeros(int(.12 * SR)), hauteur(CL, 2), 0), hauteur(CL, 7), .045, .6), c("click.ogg"))
ecrire("click/kenney-interface-click-001.ogg", hauteur(CL, 4), c("click.ogg"))
ecrire("click/kenney-interface-select-001.ogg", place(hauteur(CL, 1).copy(), cloche(1760, .08, ((1, 1),), .03), 0, .4), c("click.ogg"))
ecrire("tick/fs721514.ogg", hauteur(lire("fs528561.ogg"), 3), c("fs528561.ogg"))
ecrire("kit/tick.ogg", hauteur(TK, 2), c("fs384187.ogg"))
ecrire("impact/kenney-impact-impactsoft-heavy-000.ogg", place(plus(boom(130, 48, .6, .25, 1800), np.zeros(int(.7 * SR))), hauteur(IM, -5), 0, .7), c("impact.ogg"))
ecrire("impact/kenney-impact-impactsoft-heavy-001.ogg", place(plus(boom(120, 44, .6, .25, 1600), np.zeros(int(.7 * SR))), hauteur(IM, -7), 0, .7), c("impact.ogg"))
ecrire("impact/kenney-impact-impactpunch-heavy-000.ogg", place(plus(boom(180, 55, .35, .6, 4000), np.zeros(int(.7 * SR))), hauteur(IM, -2), 0, .9), c("impact.ogg"))
ecrire("impact/kenney-impact-impactpunch-heavy-001.ogg", place(plus(boom(170, 50, .35, .6, 3500), np.zeros(int(.7 * SR))), hauteur(IM, -3), 0, .9), c("impact.ogg"))
ecrire("ding/fs-634690-lil-pip.ogg", place(cloche(2093, .25, ((1, 1), (2.01, .15)), .07), hauteur(TK, 5), 0, .2), MAISON)

# ambiances longues (40 s) pour que les son.py puissent y piocher n'importe où : bouclage en fondu croisé du room tone CC0
def long(x, d=40.0, xf=2.0):
    k = int(xf * SR)
    out = x.copy()
    while len(out) < d * SR:
        f = np.linspace(0, 1, k)
        out = np.concatenate([out[:-k], out[-k:] * (1 - f) + x[:k] * f, x[k:]])
    return out[: int(d * SR)]


ecrire("ambience/fs-426767-apartment-room-tone-wav.ogg", long(RT), CRED["fs-426767-apartment-room-tone-wav.ogg"])
ecrire("ambience/fs-329569-roomtone-bedroom-yew.ogg", long(filtre(RT, "low", 6000) + 0.15 * filtre(RNG.standard_normal(len(RT)), "band", [200, 4000])),
       c("fs-426767-apartment-room-tone-wav.ogg"))
ecrire("ambience/fs-329533-room-tone-in-an-apartment-livi.ogg", long(filtre(RT, "high", 80)), c("fs-426767-apartment-room-tone-wav.ogg"))

# ——— 3. synthèse pure ———
ecrire("ding/kenney-interface-confirmation-001.ogg", place(place(np.zeros(int(.6 * SR)), cloche(1046.5, .4, decay=.15), 0), cloche(1568, .5, decay=.2), .07), MAISON)
ecrire("ding/kenney-interface-confirmation-002.ogg",
       reverb(place(place(place(np.zeros(int(.9 * SR)), cloche(784, .5, decay=.18), 0, .8), cloche(1046.5, .5, decay=.2), .08, .8), cloche(1568, .7, decay=.3), .16), .8, .2), MAISON)
ecrire("ding/fs-349504-triangle-open-04.ogg", reverb(cloche(1320, 3.0, ((1, 1), (2.76, .6), (5.4, .35), (8.9, .2), (13.3, .1)), 1.4), 1.5, .2), MAISON)
ecrire("ding/kenney-interface-glass-001.ogg", cloche(2637, .6, ((1, 1), (2.32, .5), (4.25, .3)), .12), MAISON)
ecrire("pop/kenney-interface-pluck-001.ogg", karplus(659, .5) * env(.5, .001, .15), MAISON)
ecrire("pop/kenney-interface-pluck-002.ogg", karplus(784, .5) * env(.5, .001, .15), MAISON)
up = lambda f0, f1, d: np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t(d) / d)) / SR) * env(d, .003, d / 2.5)
ecrire("pop/kenney-interface-maximize-001.ogg", up(500, 1400, .18), MAISON)
ecrire("transition/kenney-interface-maximize-005.ogg", plus(up(300, 1800, .3), 0.4 * souffle(.3, 800, 6000, 1.0, .8)), MAISON)
ecrire("pop/fs-514833-user-interface-menu-sounds-wav.ogg", place(hauteur(CL, 3).copy(), cloche(1318, .12, ((1, 1),), .04), .01, .5), c("click.ogg"))
ecrire("impact/fs-177242-cinematic-impact.ogg", reverb(boom(90, 32, 2.2, .5, 2500, .6), 2.5, .35, 4000), MAISON)
ecrire("impact/fs-222517-dramatic-hit.ogg", reverb(boom(110, 38, 1.8, .7, 3500, .45) + 0.3 * cloche(146.8, 1.8, ((1, 1), (2.4, .4)), .5), 2.2, .35), MAISON)
ecrire("impact/fs-347561-micheal-bay-hit.ogg", reverb(boom(80, 28, 2.8, .9, 5000, .7), 3.0, .4, 3000), MAISON)
ecrire("impact/fs745291.ogg", reverb(boom(150, 45, 1.0, .5, 3000, .25), 1.2, .25), MAISON)
# montée chromatique en écho : 12 notes qui accélèrent et montent
rs = np.zeros(int(2.8 * SR))
pos = 0.0
for i in range(12):
    rs = place(rs, cloche(392 * 2 ** (i / 12), .3, ((1, 1), (2, .3)), .08), pos, 0.4 + 0.6 * i / 11)
    pos += 0.2 * 0.9 ** i
rs = place(rs, souffle(2.2, 300, 6000, 1.0, .95), 0, 0.5)
ecrire("riser/fs-464250-echo-chromatic-riser-wav.ogg", reverb(rs, 1.0, .3), MAISON)
# glitchs : bruit échantillonné grossièrement (bit-crush) en rafales
g = np.zeros(int(.5 * SR))
for i in range(7):
    b = np.round(RNG.standard_normal(int(.04 * SR)) * 3) / 3
    b = np.repeat(b[::12], 12)[: int(.04 * SR)] * (0.4 + 0.6 * RNG.random())
    g = place(g, b * np.sin(2 * np.pi * RNG.uniform(200, 1500) * t(.04)), i * .06)
ecrire("glitch/kenney-sci-computernoise-000.ogg", g, MAISON)
ecrire("glitch/kenney-interface-glitch-002.ogg", g[: int(.25 * SR)] * filtre(np.ones(int(.25 * SR)), "low", 50), MAISON)
# frappe au clavier : 14 touches irrégulières
ty = np.zeros(int(1.6 * SR))
p = 0.0
for i in range(14):
    ty = place(ty, hauteur(TK, RNG.uniform(-3, 4)), p, RNG.uniform(.5, 1))
    p += RNG.uniform(.07, .13)
ecrire("typing/fs-416777-digital-typing-wav.ogg", ty, c("fs384187.ogg"))
# crayon qui gratte : bruit filtré, modulé par des traits rapides
sc = filtre(RNG.standard_normal(int(1.4 * SR)), "band", [1800, 7000]) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 5.5 * t(1.4)))) ** 2
ecrire("typing/fs-pencil-scribble.ogg", sc * env(1.4, .02, 2), MAISON)

json.dump(dict(bundled=manifest, default_kit=[]), open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(manifest)} sons dans {OUT}")
