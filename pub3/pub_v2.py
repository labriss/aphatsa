"""Pub 3, version complète (~47 s, 9:16) : la journée en pixel (patience 20 → 0), la découverte de Diktéo,
la réalité qui se propage depuis l'écran, l'homme réel heureux, le téléphone 3D, le carton de fin.
python pub_v2.py → out/dikteo_pub3_plombier.mp4"""
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "pixel"))
import hd  # noqa: E402
import journee_hd as JH  # noqa: E402
from bascule import etalonner, grain, lire_clip, zoom  # noqa: E402

OW, OH, FPS = 1080, 1920, 30
X = 4
OUT = os.path.join(ICI, "out")
TMP = os.path.join(ICI, "tmp", "v2")
SFX = os.path.join(ICI, "..", "son", "sfx")
ECRAN = os.path.join(ICI, "..", "pub2", "ecran", "sombre")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ——— le découpage ———
T_PIX = sum(s[1] for s in JH.SCENES)           # 31.4 s de pixel
T_POV = T_PIX + 3.6                              # découverte de l'appli
T_PIXA = T_POV + 1.0                             # le vrai homme, mais encore en pixel
T_TRANS = T_PIXA + 1.8                           # la réalité part de son téléphone
REEL = [(0.2, 3.8), (11.6, 2.4), (8.4, 1.8)]    # (début dans le plan, durée)
T_REEL = T_POV + sum(d for _, d in REEL)
T_3D = T_REEL + 4.0
T_FIN = T_3D + 2.6
N = int(round(T_FIN * FPS))

VOIX_T = {"r1": 0.4, "r2": 4.9, "r3": 9.1, "r4": 13.6, "r5": 17.8, "r6": 22.05, "r7": 29.3, "r8": 31.8, "r9": 35.6,
          "r10": 41.6, "r11": 45.9}

ARCHIVO = os.path.join(ICI, "polices", "Archivo.ttf")


def police(taille, poids=800, largeur=100):
    f = ImageFont.truetype(ARCHIVO, taille)
    f.set_variation_by_axes([poids, largeur])
    return f


F_SOUS = police(70, 800)


def sous_titre(img, texte_, u, y=1180):
    """Sous-titre façon TikTok : blanc, contour noir, apparition sèche (pas de fondu « motion design »)."""
    if u <= 0:
        return img
    d = ImageDraw.Draw(img)
    yy = y
    for l in texte_.split("\n"):
        w = d.textlength(l, font=F_SOUS)
        d.text(((OW - w) / 2, yy), l, font=F_SOUS, fill=(255, 255, 255), stroke_width=7, stroke_fill=(10, 10, 10))
        yy += 86
    return img


def pixeliser(img):
    """Le vrai plan transformé en pixel art à la même taille de pixel que le jeu (palette réduite, contours)."""
    from PIL import ImageEnhance
    p = ImageEnhance.Color(img).enhance(1.25).resize((108, 192), Image.BOX)
    p = p.quantize(18, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return p.resize((OW, OH), Image.NEAREST)


def camera_main(img, t):
    """Léger mouvement de caméra à la main (au lieu d'un zoom lisse)."""
    dx = 7 * math.sin(t * 1.7) + 4 * math.sin(t * 3.1 + 1)
    dy = 6 * math.sin(t * 1.3 + 2) + 3 * math.sin(t * 2.7)
    z = 1.06
    w, h = OW / z, OH / z
    x0, y0 = (OW - w) / 2 + dx, (OH - h) / 2 + dy
    return img.resize((OW, OH), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def ui(k):
    k = max(1, min(375, k))
    return Image.open(os.path.join(ECRAN, f"ecran_{k:04d}.png")).convert("RGB")


def coller_ecran(img, rect, k):
    x0, y0, x1, y1 = [v * X for v in rect]
    u = ui(k).resize((x1 - x0, y1 - y0), Image.LANCZOS)
    m = Image.new("L", u.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, u.width - 1, u.height - 1], 40, fill=255)
    img.paste(u, (x0, y0), m)
    return img


# ——— enregistrement des lettres écrites (pour les « bips ») ———
_lettres = {"n": 0}
_dialogue = JH.dialogue


def dialogue_compte(d, lignes, t, *a, **k):
    n = _dialogue(d, lignes, t, *a, **k)
    _lettres["n"] = n
    return n


JH.dialogue = dialogue_compte


def scene_a(t):
    acc = 0.0
    for nom, du, *_ in JH.SCENES:
        if t < acc + du:
            return nom, t - acc, acc
        acc += du
    nom, du = JH.SCENES[-1][0], JH.SCENES[-1][1]
    return nom, du, acc - du


# ——— rendu « HD-2D » léger : profondeur de champ, halo des lumières, vignette ———
_ys = np.arange(OH)[:, None].astype(np.float32)
_net = np.clip(np.minimum((_ys - 360) / 300, (1500 - _ys) / 260), 0, 1)       # 1 = net (milieu), 0 = flou (haut, bas)
_MASQUE_FLOU = Image.fromarray((np.repeat(255 * (1 - _net), OW, axis=1)).astype(np.uint8))
_xs = np.arange(OW)[None, :].astype(np.float32)
_v = 1 - 0.28 * np.clip(np.hypot((_xs - OW / 2) / (OW * 0.62), (_ys - OH * 0.5) / (OH * 0.62)) - 0.35, 0, 1) ** 1.5
_VIGNETTE = _v[..., None].astype(np.float32)
ZONES_NETTES = [(0, hd.HUD_Y * X, OW, (hd.HUD_Y + 78) * X), (0, 356 * X, OW, 432 * X)]


def hd2d(img):
    net = img
    flou = img.filter(ImageFilter.GaussianBlur(4))
    img = Image.composite(flou, img, _MASQUE_FLOU)
    a = np.asarray(img).astype(np.float32)
    mx, mn = a.max(axis=2, keepdims=True), a.min(axis=2, keepdims=True)
    lumiere = (mx > 200) & (mx - mn > 90)  # seulement les lumières colorées (lampe, aube, téléphone), pas les blancs
    brillant = Image.fromarray(np.clip(a * lumiere, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30))
    a = a + np.asarray(brillant).astype(np.float32) * 0.5
    a = a * _VIGNETTE
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    for z in ZONES_NETTES:  # la jauge et les dialogues restent parfaitement nets
        img.paste(net.crop(z), z[:2])
    return img


def pixel_frame(t):
    nom, tl, debut = scene_a(t)
    _lettres["n"] = 0
    im = JH.scene(nom, tl)
    # petit fondu « en carreaux » au début de chaque scène
    if tl < 0.22 and debut > 0:
        prev_nom, prev_t, _ = scene_a(debut - 0.01)
        prev = JH.scene(prev_nom, prev_t)
        u = tl / 0.22
        rng = random.Random(int(debut * 10))
        m = Image.new("L", (hd.W, hd.H), 0)
        dm = ImageDraw.Draw(m)
        for gy in range(0, hd.H, 10):
            for gx in range(0, hd.W, 10):
                if rng.random() < u:
                    dm.rectangle([gx, gy, gx + 9, gy + 9], fill=255)
        prev.paste(im, (0, 0), m)
        im = prev
    return hd2d(im.resize((OW, OH), Image.NEAREST)), nom, tl


def pov_frame(t, patience):
    im, rect = JH.pov(t)
    d = ImageDraw.Draw(im)
    hd.hud(im, "21 H 05", patience, None, t, "vert" if patience > 12 else "orange")
    if patience >= 1 and int(t * 10) % 3 == 0:
        hd.texte(d, (124, hd.HUD_Y + 62), "+1", "vert", hd.F16)
    _lettres["n"] = 0
    JH.dialogue(d, [("* Tu parles.", "blanc"), ("* Le devis se fait", "orange"), ("  tout seul.", "orange")], t - 0.3)
    img = hd2d(im.resize((OW, OH), Image.NEAREST))
    k = 1 + int(t / 3.6 * 372)  # le film de l'écran, accéléré : dictée → lignes → total → envoyé
    img = coller_ecran(img, rect, k)
    # halo orange de l'écran sur le monde pixel
    return img, im, rect


def mosaique(img, b):
    if b <= 1:
        return img
    return img.resize((OW // b, OH // b), Image.BOX).resize((OW, OH), Image.NEAREST)


YY, XX = np.mgrid[0:OH, 0:OW]


def propagation(pix, reel, u, centre):
    """La réalité part de l'écran et gagne tout le cadre ; une bande de pixels de plus en plus fins sur le bord."""
    dist = np.hypot(XX - centre[0], YY - centre[1])
    rmax = 2300
    r = 250 + (rmax - 250) * u ** 1.8
    bande = 380
    a_pix = np.asarray(pix).astype(np.float32)
    out = a_pix.copy()
    niveaux = [(np.asarray(mosaique(reel, b)).astype(np.float32), b) for b in (24, 12, 6, 3, 1)]
    pos = np.clip((r - dist) / bande, 0, 1)  # 0 au bord, 1 à l'intérieur
    for k, (arr, b) in enumerate(niveaux):
        lo, hi = k / len(niveaux), (k + 1) / len(niveaux)
        m = (pos > lo) & (pos <= hi) if k < len(niveaux) - 1 else pos > lo
        out[m] = arr[m]
    anneau = np.exp(-((dist - r) / 26) ** 2)[..., None]
    out = out + anneau * np.array([255, 170, 110], np.float32) * 0.45
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def hud_tombe(img, hud_natif, u):
    """La jauge du jeu tombe en morceaux dans le monde réel."""
    if u >= 1:
        return img
    rng = random.Random(11)
    for gy in range(hd.HUD_Y, hd.HUD_Y + 78, 6):
        for gx in range(0, hd.W, 6):
            delai = rng.uniform(0, 0.4)
            v = max(0.0, u - delai)
            y = gy * X + int(2200 * v * v)
            if y > OH:
                continue
            tuile = hud_natif.crop((gx, gy, gx + 6, gy + 6)).resize((6 * X, 6 * X), Image.NEAREST)
            tuile = tuile.rotate(rng.uniform(-90, 90) * v, Image.NEAREST)
            img.paste(tuile, (gx * X + int(rng.uniform(-200, 200) * v), y))
    return img


def main():
    reel = []
    for debut, du in REEL:
        reel += [etalonner(f) for f in lire_clip(os.path.join(ICI, "clips", "6194923.mp4"), debut, du + 0.1)][: int(round(du * FPS))]
    tel = sorted(f for f in os.listdir(os.path.join(ICI, "tmp", "tel")) if f.endswith(".png"))
    fin = sorted(os.listdir(os.path.join(ICI, "tmp", "fin", "img")))
    sortie_brute = os.path.join(TMP, "image.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", sortie_brute],
                          stdin=subprocess.PIPE)
    evenements = {"bips": [], "lettres_prec": 0}
    dernier_pov = None
    centre = None
    for i in range(N):
        t = i / FPS
        if t < T_PIX:
            img, nom, tl = pixel_frame(t)
        elif t < T_POV:
            tp = t - T_PIX
            pat = min(20, int(tp / 3.0 * 20))
            img, nat, rect = pov_frame(tp, pat)
            dernier_pov = (img.copy(), nat)
            centre = ((rect[0] + rect[2]) / 2 * X, (rect[1] + rect[3]) / 2 * X)
        elif t < T_REEL:
            k = i - int(round(T_POV * FPS))
            r = camera_main(reel[min(k, len(reel) - 1)], t)
            if t < T_TRANS:
                # le vrai homme, encore en pixel, avec la jauge du jeu ; puis la réalité part de son téléphone
                pr = pixeliser(r)
                pr.paste(dernier_pov[0].crop((0, hd.HUD_Y * X, OW, (hd.HUD_Y + 78) * X)), (0, hd.HUD_Y * X))
                if t < T_POV + 0.25:
                    pr = Image.blend(dernier_pov[0], pr, (t - T_POV) / 0.25)
                if t < T_PIXA:
                    img = pr
                else:
                    u = (t - T_PIXA) / (T_TRANS - T_PIXA)
                    img = propagation(pr, r, u, (0.66 * OW, 0.76 * OH))
                    img = hud_tombe(img, dernier_pov[1], max(0.0, u - 0.3) / 0.7 * 1.3)
            else:
                img = hud_tombe(r, dernier_pov[1], 1.3 + (t - T_TRANS))
            # sous-titres
            a = T_POV + REEL[0][1]
            b = a + REEL[1][1]
            if t < a:
                img = sous_titre(img, "Le devis est parti.\nEn 30 secondes.", t - T_TRANS - 0.2)
            elif t < b:
                img = sous_titre(img, "Fini la vie\nen pixels.", t - a)
            else:
                img = sous_titre(img, "Retour à la\nvraie vie.", t - b)
            img = grain(img, 4, i)
        elif t < T_3D:
            k = i - int(round(T_REEL * FPS))
            img = Image.open(os.path.join(ICI, "tmp", "tel", tel[min(k, len(tel) - 1)])).convert("RGB").resize((OW, OH), Image.LANCZOS)
            if k < 5:
                img = Image.blend(img, Image.new("RGB", img.size, (255, 200, 150)), 1 - k / 5)
            img = sous_titre(img, "Tu dictes.\nDiktéo fait le devis.", (t - T_REEL) - 0.6, 230)
        else:
            k = i - int(round(T_3D * FPS))
            img = Image.open(os.path.join(ICI, "tmp", "fin", "img", fin[min(k, len(fin) - 1)])).convert("RGB")
        n = _lettres["n"] if t < T_POV else 0
        if n > evenements["lettres_prec"] and n % 2 == 0:
            evenements["bips"].append(t)
        evenements["lettres_prec"] = n
        ff.stdin.write(img.tobytes())
        if i % 60 == 0:
            print(f"{i}/{N}", flush=True)
    ff.stdin.close()
    ff.wait()
    return sortie_brute, evenements["bips"]


# ——— le son ———
SR = 48000


def sfx(nom):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SFX, nom), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def son(bips):
    n = int(T_FIN * SR) + SR
    piste = np.zeros(n, np.float32)

    def pose(sig, t, db=0.0):
        a = int(t * SR)
        if a >= n:
            return
        sig = sig[: n - a] * (10 ** (db / 20))
        piste[a:a + len(sig)] += sig

    tt = lambda d: np.arange(int(d * SR)) / SR

    def carre(f, d, dec=8, vol=0.12, duty=0.5):
        x = tt(d)
        ph = (f * x) % 1
        return (np.where(ph < duty, 1.0, -1.0) * np.exp(-x * dec) * vol).astype(np.float32)

    def note(m):
        return 440 * 2 ** ((m - 69) / 12)

    # musique 8-bits : progression qui se tend scène après scène
    progs = [[57, 60, 64, 67], [57, 60, 64, 69], [55, 59, 62, 65], [53, 57, 60, 64], [52, 55, 59, 62], [52, 55, 58, 61]]
    acc = 0.0
    for s_idx, (nom, du, *_r) in enumerate(JH.SCENES):
        if nom == "telephone":
            break
        tempo = 0.125 - s_idx * 0.012
        prog = progs[min(s_idx, len(progs) - 1)]
        t = acc
        k = 0
        fin_s = acc + du if nom != "soir" else acc + 1.9
        while t < fin_s - 0.01:
            m = prog[k % 4] + (12 if (k // 4) % 2 else 0)
            pose(carre(note(m), tempo * 1.6, 7, 0.07, 0.25), t)
            if k % 2 == 0:
                pose(carre(note(prog[0] - 24), tempo * 2, 3, 0.09), t)
            if k % 4 == 0:
                pose((np.random.default_rng(k).uniform(-1, 1, int(0.05 * SR)) * np.exp(-tt(0.05) * 50) * 0.18).astype(np.float32), t)
            t += tempo
            k += 1
        acc += du
    # les coups sur la patience
    acc = 0.0
    for nom, du, h, pv, coup in JH.SCENES:
        if coup:
            tc = acc + coup[0]
            pose(sfx("impact.ogg"), tc, -8)
            for j, m in enumerate((64, 60, 55)):
                pose(carre(note(m), 0.09, 10, 0.12), tc + j * 0.07)
        acc += du
    # la crise de 21 h : grondement, bruit, cri en carré qui descend
    t_soir = sum(s[1] for s in JH.SCENES[:5])
    tc = t_soir + 1.9
    x = tt(4.2)
    gr = (np.sin(2 * np.pi * (60 - 20 * x / 4.2) * x) * 0.4 + np.random.default_rng(1).uniform(-1, 1, len(x)) * 0.12) * np.exp(-x * 0.5)
    pose(gr.astype(np.float32), tc)
    pose(sfx("impact.ogg"), tc, -2)
    for j in range(16):
        pose(carre(note(76 - j * 2), 0.06, 6, 0.1), tc + j * 0.06)
    # le téléphone s'allume : petite mélodie douce
    t_tel = T_PIX - JH.SCENES[-1][1]
    for j, m in enumerate((72, 76, 79, 84)):
        pose(carre(note(m), 0.25, 5, 0.08), t_tel + 0.6 + j * 0.12)
    # la découverte : arpège majeur qui monte, un « bip » par point de patience regagné
    for j in range(20):
        pose(carre(note(60 + [0, 4, 7, 12][j % 4] + 12 * (j // 8)), 0.12, 9, 0.07), T_PIX + 0.15 * j)
    # bips de texte
    for b in bips:
        pose(carre(note(84), 0.025, 30, 0.05), b)
    # la propagation : montée, souffle, grave
    pose(sfx("fs-685256-riser-sound-effect-short-wav.ogg"), T_POV - 1.0, -6)
    pose(sfx("fs-786514-swoosh-v2.ogg"), T_POV, -3)
    x = tt(3.0)
    pose((np.sin(2 * np.pi * (48 - 10 * x) * x) * np.exp(-x * 1.2) * 0.5).astype(np.float32), T_POV + 0.2)
    # le monde réel : ambiance + nappe chaude (accords majeurs)
    amb = sfx("fs-426767-apartment-room-tone-wav.ogg")
    pose(amb[: int((T_FIN - T_POV) * SR)], T_POV, -10)
    x = tt(T_FIN - T_POV)
    env = np.minimum(1, x / 1.0) * np.minimum(1, (x[-1] - x) / 1.0)
    accords = [(130.8, 164.8, 196.0, 261.6), (174.6, 220.0, 261.6, 349.2), (196.0, 246.9, 293.7, 392.0), (130.8, 164.8, 196.0, 261.6)]
    nappe = np.zeros(len(x), np.float32)
    seg = len(x) // 4
    for k, acc_ in enumerate(accords):
        xs = x[k * seg:(k + 1) * seg]
        e = np.minimum(1, (xs - xs[0]) / 0.4) * np.minimum(1, (xs[-1] - xs) / 0.4)
        nappe[k * seg:(k + 1) * seg] = sum(np.sin(2 * np.pi * f * xs) + 0.3 * np.sin(2 * np.pi * 2 * f * xs) for f in acc_) * 0.03 * e
    pose(nappe * env, T_POV)
    # le téléphone 3D, la fin
    pose(sfx("fs-786514-swoosh-v2.ogg"), T_REEL - 0.1, -6)
    pose(sfx("click.ogg"), T_REEL + 1.5, -6)
    pose(sfx("fs-571513-soft-notifications-bell-ding-d.ogg"), T_3D + 0.1, -3)
    # la voix off, et la musique qui s'efface sous la voix
    choix = os.path.join(ICI, "voix", "v2", "choix.txt")
    if os.path.exists(choix) and "--voix" in sys.argv:
        voix = np.zeros(n, np.float32)
        for ligne in open(choix, encoding="utf-8"):
            nom, fichier = ligne.split()
            a = int(VOIX_T[nom] * SR)
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ICI, "voix", "v2", fichier), "-af",
                                  "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,silenceremove=start_periods=1:start_threshold=-45dB",
                                  "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
            v = np.frombuffer(raw, np.float32)
            v = v / max(1e-6, np.abs(v).max()) * 0.9
            voix[a:a + len(v)] += v[: n - a]
        env = np.convolve(np.abs(voix), np.ones(4800) / 4800, mode="same")
        duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1)
        piste = piste / max(1e-6, np.abs(piste).max()) * 0.6 * duck + voix
    piste /= max(1e-6, np.abs(piste).max()) / 0.89
    chemin = os.path.join(TMP, "son.wav")
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((piste[: int(T_FIN * SR)] * 32767).astype(np.int16).tobytes())
    return chemin


if __name__ == "__main__":
    if "--son" in sys.argv:  # ne refait que le son, sur l'image déjà rendue
        import json
        video, bips = os.path.join(TMP, "image.mp4"), json.load(open(os.path.join(TMP, "bips.json")))
    else:
        video, bips = main()
        import json
        json.dump(bips, open(os.path.join(TMP, "bips.json"), "w"))
    wav = son(bips)
    sortie = os.path.join(OUT, "dikteo_pub3_plombier.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-shortest", "-movflags", "+faststart", sortie], check=True)
    print("OK", sortie, f"{T_FIN:.1f} s")
