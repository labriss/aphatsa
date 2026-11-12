# Le montage de la pub : assemble les plans (rendus 3D, appli filmée, métiers), pose les titres,
# ajoute la patine « film » (halo des lumières, vignettage, grain léger), puis encode avec le son.
# Usage : python montage.py <30|15|6|16x9> [première image dernière image]
#   Sans intervalle : encode out/pub_<version>s.mp4 avec out/mix_<version>s.wav (bash son/mixage.sh <version>).
#   Avec un intervalle : sort seulement ces images en PNG dans out/controle/, pour vérifier.
# Les versions courtes sont des extraits du 30 s : chaque image vient d'une image du 30 s (« maître »),
# choisie pour que le drop et le dernier coup de leur musique (son/musique.py) tombent au même endroit de l'image.
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ICI = Path(__file__).resolve().parent
R = ICI / "renders" / "final"
W, H, FPS, N = 1080, 1920, 30, 900
NUIT = np.array([14, 20, 18], dtype=np.float32)  # --background du mode sombre
TEMPS = 60 / 152

VERSION = sys.argv[1] if len(sys.argv) > 1 else "30"
# (première image de la version, première image du maître, nombre d'images)
EXTRAITS = {
    "30": [(0, 0, 900)],
    # Goutte 0–2 s, cuisine 2–4 s (« la soirée »), plongée 4–5 s, téléphone (drop à 6,00 s, ding à 9,2 s), fin (coup à 12,32 s).
    "15": [(0, 0, 60), (60, 82, 60), (120, 210, 30), (150, 360, 200), (350, 797, 100)],
    # Goutte 0–1,2 s, téléphone (drop à 1,60 s), fin (coup à 4,76 s).
    "6": [(0, 24, 36), (36, 378, 92), (128, 801, 52)],
    # Le 30 s en horizontal : même montage, même son, autre mise en page (voir image_paysage).
    "16x9": [(0, 0, 900)],
}[VERSION]
PAYSAGE = VERSION == "16x9"
SW, SH = (1920, 1080) if PAYSAGE else (W, H)  # taille de la vidéo de sortie
NV = sum(n for _, _, n in EXTRAITS)
OUT = ICI / "out" / (f"pub_{VERSION}.mp4" if PAYSAGE else f"pub_{VERSION}s.mp4")
CONTROLE = len(sys.argv) > 3
A = int(sys.argv[2]) if CONTROLE else 0
B = int(sys.argv[3]) if CONTROLE else NV - 1


def maitre(f):
    """L'image du 30 s qui donne l'image f de la version."""
    for debut, source, n in EXTRAITS:
        if debut <= f < debut + n:
            return source + f - debut
    raise ValueError(f)


def charge(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


BROUILLON = ICI / "renders" / "brouillon"
LONGUEUR = {"goutte": 75, "cuisine_nuit": 165, "telephone": 340, "cuisine_soir": 75}


def seq(dossier, i):
    """Image i (à partir de 0) d'un plan 3D : le rendu définitif s'il existe, sinon le brouillon agrandi.
    Un fichier vide est une image réservée par un rendu en cours : elle n'est pas encore là."""
    nom = f"f_{min(i, LONGUEUR[dossier] - 1) + 1:04d}.png"
    final = R / dossier / nom
    # BROUILLON=1 : tout en brouillon, pour ne pas mélanger deux qualités dans un même plan.
    if not __import__("os").environ.get("BROUILLON") and final.exists() and final.stat().st_size > 0:
        return charge(final)
    img = Image.open(BROUILLON / dossier / nom).convert("RGB").resize((W, H), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32)


METIERS = ["electricien", "chauffagiste", "carreleur", "peintre", "menuisier", "macon", "couvreur", "serrurier", "multiservice"]
M0 = round(19.32 * FPS)  # 580
BORNES = [round(k * TEMPS * FPS) for k in range(9)] + [round(24.05 * FPS) - M0]


def metier(i):
    """Plan 8 : la scène du métier au centre, sur le fond de nuit, avec un petit coup de zoom à chaque temps."""
    k = max(j for j in range(9) if BORNES[j] <= i)
    local = i - BORNES[k]
    fichiers = sorted((R / "metiers" / METIERS[k]).glob("*.png"))
    art = Image.open(fichiers[min(local, len(fichiers) - 1)]).convert("RGB")
    zoom = 1 + 0.05 * np.exp(-local / 3.0)
    taille = int(900 * zoom)
    art = art.resize((taille, taille), Image.LANCZOS)
    img = Image.new("RGB", (W, H), tuple(int(v) for v in NUIT))
    img.paste(art, ((W - taille) // 2, 880 - taille // 2))
    return np.asarray(img, dtype=np.float32)


def plan(f):
    """L'image de fond (sans titres) de l'image f de la pub."""
    if f < 75:
        return seq("goutte", f)
    if f < 240:
        return seq("cuisine_nuit", f - 75)
    if f < M0:
        return seq("telephone", f - 240)
    if f < round(24.05 * FPS):
        return metier(f - M0)
    return seq("cuisine_soir", f - round(24.05 * FPS))


# ——— Patine ———

yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
_d = np.sqrt(((xx - SW / 2) / (SW * 0.62)) ** 2 + ((yy - SH / 2) / (SH * 0.62)) ** 2)
VIGNETTE = (1 - 0.32 * np.clip(_d - 0.45, 0, 1) ** 1.6)[..., None]
rng = np.random.default_rng(2026)


def halo(img, force=0.22):
    """Les lumières débordent un peu, comme sur une vraie optique : seules les zones très claires bavent."""
    clair = np.clip(img - 200, 0, None) * (255 / 55)
    petit = Image.fromarray(clair.clip(0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    flou = np.asarray(petit.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR), dtype=np.float32)
    return img + flou * force


FLASH = {"30": 240, "15": 150, "6": None, "16x9": 240}[VERSION]


def flash_orange(img, f):
    """Raccord ordinateur → téléphone : la lueur orange envahit l'image, puis se retire sur le téléphone.
    f est l'image de la version : le raccord y tombe à un autre instant que dans le 30 s."""
    centre = FLASH
    if centre is None:
        return img
    x = np.exp(-(((f - centre) / 4.0) ** 2))
    if x < 0.01:
        return img
    orange = np.array([255, 122, 51], dtype=np.float32)
    return img * (1 - 0.85 * x) + orange * 0.85 * x + 60 * x


def grain(img):
    g = rng.normal(0, 3.2, (SH // 2, SW // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((SW, SH), Image.BILINEAR))
    return img + g[..., None]


def image_paysage(vertical):
    """16:9 : l'image verticale à droite, sur un fond fait d'elle-même (agrandie, floutée, assombrie) ;
    la place à gauche est pour les titres (film/titres.html?format=paysage)."""
    v = Image.fromarray(vertical.clip(0, 255).astype(np.uint8))
    fond = v.resize((SW // 8, SW * H // W // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
    fond = fond.resize((SW, SW * H // W), Image.BILINEAR)
    haut = (fond.height - SH) // 2
    toile = np.asarray(fond.crop((0, haut, SW, haut + SH)), dtype=np.float32) * 0.38
    largeur = round(SH * W / H)
    x0 = 1240 - largeur // 2
    cadre = np.asarray(v.resize((largeur, SH), Image.LANCZOS), dtype=np.float32)
    # Une ombre douce de chaque côté de l'image verticale.
    for k in range(40):
        toile[:, max(0, x0 - 40 + k)] *= 0.6 + 0.4 * (1 - k / 40)
        toile[:, min(SW - 1, x0 + largeur + 39 - k)] *= 0.6 + 0.4 * (1 - k / 40)
    toile[:, x0 : x0 + largeur] = cadre
    return toile


def image(fv):
    f = maitre(fv)
    img = plan(f)
    img = flash_orange(img, fv)
    img = halo(img)
    if PAYSAGE:
        img = image_paysage(img)
    titres = Image.open(R / ("titres_paysage" if PAYSAGE else "titres") / f"titres_{f + 1:04d}.png").convert("RGBA")
    t = np.asarray(titres, dtype=np.float32)
    a = t[..., 3:4] / 255
    img = img * (1 - a) + t[..., :3] * a
    img = img * VIGNETTE
    img = grain(img)
    return img.clip(0, 255).astype(np.uint8)


if CONTROLE:
    d = ICI / "out" / "controle"
    d.mkdir(parents=True, exist_ok=True)
    for f in range(A, B + 1):
        Image.fromarray(image(f)).save(d / f"{VERSION}_{f:04d}.png")
    print(f"{B - A + 1} images dans {d}")
    sys.exit()

# Encodage : H.264 haute qualité (les réseaux recompressent, on leur donne une source propre), son AAC 320 k.
son = ICI / "out" / ("mix_30s.wav" if PAYSAGE else f"mix_{VERSION}s.wav")
OUT.parent.mkdir(parents=True, exist_ok=True)
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}", "-r", str(FPS), "-i", "-",
       "-i", str(son), "-map", "0:v", "-map", "1:a",
       "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "320k", "-shortest", str(OUT)]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(NV):
    p.stdin.write(image(f).tobytes())
    if f % 90 == 0:
        print(f"{f / FPS:.0f} s", flush=True)
p.stdin.close()
p.wait()
print(OUT)
