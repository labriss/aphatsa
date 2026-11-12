"""Test de la bascule de la pub 3 : la vie en pixel → le vrai mec → le téléphone 3D → le carton de fin.
python bascule.py → out/bascule_test.mp4 (1080×1920, 30 i/s, avec le son)."""
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "pixel"))
import journee as J  # noqa: E402
from rpg import W, H, cadre, h, sprite, texte  # noqa: E402

OW, OH, FPS = 1080, 1920, 30
TMP = os.path.join(ICI, "tmp", "bascule")
OUT = os.path.join(ICI, "out")
SFX = os.path.join(ICI, "..", "son", "sfx")
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# découpage (en images)
A, B, C, D, E, F, G, FIN = 0, 60, 84, 108, 183, 195, 315, 369


def grand(im):
    return im.resize((OW, OH), Image.NEAREST)


# ——— le plan pixel où il prend son téléphone (cadré comme le vrai plan) ———
def pixel_telephone(lueur):
    im = Image.new("RGB", (W, H), h("#1B1430"))
    d = ImageDraw.Draw(im)
    J.carrelage(d, 0, H, "#231B36", "#1E1730", 12)
    e = 9
    x0, y0 = (W - 12 * e) // 2, 66
    fond = {im.getpixel((0, y)) for y in range(H)} | {im.getpixel((12, y)) for y in range(H)}
    J.perso(im, x0, y0, "enerve", e)
    # l'écran (qu'on ne voit pas) éclaire son visage en orange
    px = im.load()
    k = 0.3 * lueur
    for y in range(y0, y0 + 8 * e):
        for x in range(x0, x0 + 12 * e):
            r, g, b = px[x, y]
            if (r, g, b) in fond or r + g + b < 120:
                continue
            px[x, y] = (min(255, int(r + (240 - r) * k)), min(255, int(g + (122 - g) * k * 0.7)), int(b * (1 - k * 0.5)))
    # le téléphone tenu face à nous, deux mains sur les côtés
    d.rectangle([64, 170, 116, 266], fill=h("#0A0B0D"), outline=h("#3A3F44"))
    d.rectangle([69, 175, 85, 191], fill=h("#1A1C20"))
    for (x, y) in ((54, 210), (110, 206)):
        d.rectangle([x, y, x + 14, y + 22], fill=h("peau"), outline=h("peau2"))
    for r in range(8, 8 + int(34 * lueur), 7):
        d.arc([90 - r - 30, 164 - r, 90 + r + 30, 168 + r], 200, 340, fill=h("orange"))
    J.patience(im, 0)
    cadre(d, [6, 26, 174, 52], 2)
    texte(d, (14, 35), "* Tu prends ton tel.", "orange")
    return im


# ——— le vrai plan (Pexels 4010137), recadré en 1080×1920 ———
def lire_clip(chemin, debut, duree):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(debut), "-t", str(duree), "-i", chemin, "-vf",
           f"fps={FPS},scale={OW}:-2,crop={OW}:{OH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (OW * OH * 3)
    return [Image.frombuffer("RGB", (OW, OH), raw[i * OW * OH * 3:(i + 1) * OW * OH * 3]) for i in range(n)]


def etalonner(im):
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.08)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04 + 4)))
    b = b.point(lambda v: int(v * 0.94))
    return Image.merge("RGB", (r, g, b))


def zoom(im, z, cx=0.5, cy=0.5):
    if z <= 1.0001:
        return im
    w, hh = OW / z, OH / z
    x0 = min(max(cx * OW - w / 2, 0), OW - w)
    y0 = min(max(cy * OH - hh / 2, 0), OH - hh)
    return im.resize((OW, OH), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + hh))


def mosaique(im, bloc, couleurs=None):
    if bloc <= 1:
        return im
    p = im.resize((max(1, OW // bloc), max(1, OH // bloc)), Image.BOX)
    if couleurs:
        p = p.quantize(couleurs, dither=Image.Dither.NONE).convert("RGB")
    return p.resize((OW, OH), Image.NEAREST)


def aberration(im, dx):
    if dx < 1:
        return im
    r, g, b = im.split()
    return Image.merge("RGB", (ImageChops.offset(r, int(dx), 0), g, ImageChops.offset(b, -int(dx), 0)))


def grain(im, force=7, graine=0):
    rng = np.random.default_rng(graine)
    a = np.asarray(im).astype(np.int16) + rng.normal(0, force, (OH, OW, 1)).astype(np.int16)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def flash(im, k, couleur=(255, 214, 170)):
    if k <= 0:
        return im
    return Image.blend(im, Image.new("RGB", im.size, couleur), min(1.0, k))


def eclats(fond, pix, t):
    """Les carreaux du monde pixel s'envolent vers la caméra et laissent voir le vrai monde."""
    out = fond.copy()
    rng = random.Random(9)
    taille = 10  # en pixels natifs
    for gy in range(0, H, taille):
        for gx in range(0, W, taille):
            delai = rng.uniform(0, 0.45) + 0.25 * math.hypot(gx / W - 0.5, gy / H - 0.45)
            u = (t - delai) / 0.5
            if u >= 1:
                continue
            u = max(0.0, u)
            tuile = pix.crop((gx, gy, gx + taille, gy + taille))
            ech = 1 + 2.4 * u * u
            s = int(taille * 6 * ech)
            dx = (gx + taille / 2 - W / 2) * 6 * (1 + 3 * u * u)
            dy = (gy + taille / 2 - H * 0.45) * 6 * (1 + 3 * u * u)
            x = int(OW / 2 + dx - s / 2)
            y = int(OH * 0.45 + dy - s / 2)
            tu = tuile.resize((s, s), Image.NEAREST).rotate(rng.uniform(-40, 40) * u, Image.NEAREST, expand=False)
            masque = Image.new("L", (s, s), int(255 * (1 - u) ** 0.6))
            out.paste(tu, (x, y), masque)
    return out


def main():
    s5 = J.s5()
    reel = [etalonner(f) for f in lire_clip(os.path.join(ICI, "clips", "4010137.mp4"), 0.3, (E - C) / FPS + 0.5)]
    tel_dir = os.path.join(ICI, "tmp", "tel")
    tel = sorted(f for f in os.listdir(tel_dir) if f.startswith("tel_") and f.endswith(".png"))
    fin = sorted(os.listdir(os.path.join(ICI, "tmp", "fin", "img")))
    rng = random.Random(3)
    cx_tel, cy_tel = 0.5, 0.86  # le téléphone dans le vrai plan

    for i in range(FIN):
        if i < B:  # la colère, l'image tremble
            amp = 2 + 2 * (i / B)
            im = Image.new("RGB", (W, H), h("noir"))
            im.paste(s5, (rng.randint(-int(amp), int(amp)), rng.randint(-int(amp), int(amp))))
            if (i // 6) % 2:
                ImageDraw.Draw(im).rectangle([0, 0, W - 1, H - 1], outline=h("rouge"), width=2)
            img = grand(im)
        elif i < C:
            img = grand(pixel_telephone((i - B) / (C - B)))
        elif i < D:  # la bascule
            t = (i - C) / (D - C)
            r = reel[i - C]
            bloc = [24, 24, 18, 14, 11, 9, 7, 6, 5, 4, 4, 3, 3, 2, 2, 2, 1][min(16, int(t * 17))]
            base = mosaique(r, bloc, 24 if bloc >= 6 else None)
            base = aberration(base, 18 * (1 - t) ** 2)
            img = eclats(base, pixel_telephone(1.0), t * 1.15)
            img = flash(img, 0.9 * (1 - t / 0.18) if t < 0.18 else 0)
        elif i < E:  # le vrai mec, poussée lente vers le téléphone
            t = (i - D) / (E - D)
            img = zoom(reel[i - C], 1.0 + 0.22 * t, 0.5, 0.5 + 0.2 * t)
        elif i < F:  # plongée dans le téléphone
            t = (i - E) / (F - E)
            z = 1.22 + 3.5 * t ** 2.2
            img = zoom(reel[min(len(reel) - 1, i - C)], z, cx_tel, 0.7 + 0.16 * min(1, t * 1.6))
            img = img.filter(ImageFilter.GaussianBlur(6 * t))
            img = flash(img, max(0, (t - 0.6) / 0.4), (255, 150, 80))
        elif i < G:  # le téléphone 3D
            k = i - F
            img = Image.open(os.path.join(tel_dir, tel[min(k, len(tel) - 1)])).convert("RGB").resize((OW, OH), Image.LANCZOS)
            img = flash(img, 1 - k / 6 if k < 6 else 0, (255, 150, 80))
        else:
            img = Image.open(os.path.join(ICI, "tmp", "fin", "img", fin[min(i - G, len(fin) - 1)])).convert("RGB")
        if i >= C:
            img = grain(img, 5, i)
        img.save(os.path.join(TMP, f"i_{i:04d}.png"))
        if i % 30 == 0:
            print(i, flush=True)


# ——— le son ———
SR = 48000


def sfx(nom):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SFX, nom), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def son():
    n = int(FIN / FPS * SR) + SR
    piste = np.zeros(n, np.float32)

    def pose(sig, t, db=0.0):
        a = int(t * SR)
        sig = sig[: max(0, n - a)] * (10 ** (db / 20))
        piste[a:a + len(sig)] += sig

    tt = lambda d: np.arange(int(d * SR)) / SR
    # 8-bits tendu : arpège en carré, de plus en plus rapide, jusqu'à la bascule
    notes = [57, 60, 64, 60, 57, 60, 65, 60, 56, 59, 64, 59, 56, 59, 62, 59]
    t, k = 0.0, 0
    while t < C / FPS - 0.02:
        du = 0.11 if t < 1.6 else 0.075
        f = 440 * 2 ** ((notes[k % len(notes)] - 69) / 12)
        x = tt(du)
        sq = np.sign(np.sin(2 * np.pi * f * x)) * np.exp(-x * 9) * 0.16
        basse = np.sign(np.sin(2 * np.pi * f / 4 * x)) * 0.07
        pose((sq + basse).astype(np.float32), t)
        if k % 4 == 0:
            pose((np.random.default_rng(k).uniform(-1, 1, int(0.04 * SR)) * np.exp(-tt(0.04) * 60) * 0.25).astype(np.float32), t)
        t += du
        k += 1
    # la bascule : coupure, impact, grave
    pose(sfx("fs-685256-riser-sound-effect-short-wav.ogg"), C / FPS - 1.2, -10)
    pose(sfx("impact.ogg"), C / FPS, -2)
    x = tt(2.5)
    pose((np.sin(2 * np.pi * (52 - 14 * x) * x) * np.exp(-x * 1.6) * 0.55).astype(np.float32), C / FPS)
    # le vrai monde : ambiance de pièce + nappe douce
    amb = sfx("fs-426767-apartment-room-tone-wav.ogg")[: int((F - C) / FPS * SR)]
    pose(amb, C / FPS + 0.1, -8)
    x = tt((FIN - C) / FPS)
    env = np.minimum(1, x / 1.2) * np.minimum(1, (x[-1] - x) / 0.8)
    nappe = sum(np.sin(2 * np.pi * f * x + p) for f, p in ((110, 0), (164.8, 1), (220.5, 2), (277.2, 0.5), (329.6, 1.5))) * 0.035
    pose((nappe * env).astype(np.float32), C / FPS)
    # la plongée dans le téléphone, puis le téléphone 3D
    pose(sfx("fs-786514-swoosh-v2.ogg"), E / FPS - 0.05, -4)
    pose(sfx("impact.ogg"), F / FPS, -9)
    x = tt((G - F) / FPS)
    pouls = (np.sin(2 * np.pi * 55 * x) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 2 * x))) * 0.12 * np.minimum(1, x / 0.5))
    pose(pouls.astype(np.float32), F / FPS)
    pose(sfx("click.ogg"), F / FPS + 1.4, -6)
    pose(sfx("fs-571513-soft-notifications-bell-ding-d.ogg"), G / FPS + 0.1, -4)
    piste /= max(1e-6, np.abs(piste).max()) / 0.85
    chemin = os.path.join(TMP, "son.wav")
    import wave
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((piste[: int(FIN / FPS * SR)] * 32767).astype(np.int16).tobytes())
    return chemin


if __name__ == "__main__":
    main()
    wav = son()
    sortie = os.path.join(OUT, "bascule_test.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "i_%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", sortie], check=True)
    print("OK", sortie)
