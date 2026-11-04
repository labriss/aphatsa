# Le montage de la pub : assemble les plans (rendus 3D, appli filmée, métiers), pose les titres,
# ajoute la patine « film » (halo des lumières, vignettage, grain léger), puis encode avec le son.
# Usage : python montage.py <sortie.mp4> [première image] [dernière image]   (images de 0 à 899, 30 i/s)
#         Avec seulement un intervalle, sort aussi les images PNG dans out/controle/ pour vérifier.
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

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ICI / "out" / "pub_30s.mp4")
A = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else N - 1
CONTROLE = len(sys.argv) > 2


def charge(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def seq(dossier, i, prefixe="f_"):
    """Image i (à partir de 0) d'une séquence ; on garde la dernière si la séquence est plus courte."""
    fichiers = sorted((R / dossier).glob(f"{prefixe}*.png"))
    return charge(fichiers[min(i, len(fichiers) - 1)])


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

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIGNETTE = (1 - 0.32 * np.clip(_d - 0.45, 0, 1) ** 1.6)[..., None]
rng = np.random.default_rng(2026)


def halo(img, force=0.22):
    """Les lumières débordent un peu, comme sur une vraie optique : seules les zones très claires bavent."""
    clair = np.clip(img - 200, 0, None) * (255 / 55)
    petit = Image.fromarray(clair.clip(0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    flou = np.asarray(petit.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR), dtype=np.float32)
    return img + flou * force


def flash_orange(img, f):
    """Raccord ordinateur → téléphone (8,0 s) : la lueur orange envahit l'image, puis se retire sur le téléphone."""
    centre = 240
    x = np.exp(-(((f - centre) / 4.0) ** 2))
    if x < 0.01:
        return img
    orange = np.array([255, 122, 51], dtype=np.float32)
    return img * (1 - 0.85 * x) + orange * 0.85 * x + 60 * x


def grain(img):
    g = rng.normal(0, 3.2, (H // 2, W // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((W, H), Image.BILINEAR))
    return img + g[..., None]


def image(f):
    img = plan(f)
    img = flash_orange(img, f)
    img = halo(img)
    titres = Image.open(R / "titres" / f"titres_{f + 1:04d}.png").convert("RGBA")
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
        Image.fromarray(image(f)).save(d / f"img_{f:04d}.png")
    print(f"{B - A + 1} images dans {d}")
    sys.exit()

# Encodage : H.264 haute qualité (les réseaux recompressent, on leur donne une source propre), son AAC 320 k.
son = ICI / "out" / "mix_30s.wav"
OUT.parent.mkdir(parents=True, exist_ok=True)
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(son), "-map", "0:v", "-map", "1:a",
       "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "320k", "-shortest", str(OUT)]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(N):
    p.stdin.write(image(f).tobytes())
    if f % 90 == 0:
        print(f"{f / FPS:.0f} s", flush=True)
p.stdin.close()
p.wait()
print(OUT)
