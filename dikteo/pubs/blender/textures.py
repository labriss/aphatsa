# Textures dessinées pour les scènes Blender : l'écran du tableur (l'« avant ») et le carnet raturé.
# Usage : python textures.py <dossier de sortie>
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
random.seed(7)


def font(size, bold=False):
    for name in (["arialbd.ttf"] if bold else []) + ["arial.ttf", "segoeui.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


# Le tableur : une grille froide, des cellules à moitié remplies, une case active qui clignote.
W, H = 1600, 1000
img = Image.new("RGB", (W, H), (226, 232, 238))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 70], fill=(58, 96, 140))
d.text((24, 18), "devis_FONTAINE_v3_final(2).xlsx", font=font(30, True), fill=(235, 240, 246))
d.rectangle([0, 70, W, 120], fill=(205, 212, 220))
for i, label in enumerate(["Fichier", "Accueil", "Insertion", "Formules", "Données"]):
    d.text((24 + i * 170, 82), label, font=font(24), fill=(60, 70, 82))
col = [0, 90, 640, 820, 1000, 1200, 1400, W]
top, row_h = 160, 46
d.rectangle([0, 120, W, top], fill=(214, 220, 228))
for c, label in enumerate(["", "Désignation", "Qté", "Unité", "PU HT", "TVA", "Total HT"]):
    d.text((col[c] + 12, 128), label, font=font(22, True), fill=(52, 60, 70))
lines = ["Remplacement siphon", "Joint fibre", "Main-d'oeuvre", "Déplacement", "Raccord laiton ??", "", "", "", "", "", "", "", "", "", "", ""]
for r in range(17):
    y = top + r * row_h
    d.line([0, y, W, y], fill=(186, 194, 204), width=2)
    d.text((col[0] + 30, y + 10), str(r + 1), font=font(22), fill=(120, 130, 142))
    if r < len(lines) and lines[r]:
        d.text((col[1] + 12, y + 10), lines[r], font=font(24), fill=(36, 42, 50))
        if r < 4:
            for c, v in ((2, "1"), (3, "u"), (4, "#VALEUR!" if r == 2 else f"{random.randint(5, 90)},00"), (5, "10 %")):
                d.text((col[c] + 12, y + 10), v, font=font(24), fill=(176, 40, 40) if "#" in v else (36, 42, 50))
for x in col:
    d.line([x, 120, x, H], fill=(186, 194, 204), width=2)
# La case active.
y = top + 4 * row_h
d.rectangle([col[4], y, col[5], y + row_h], outline=(30, 110, 60), width=5)
img.save(out / "tableur.png")

# Le carnet : papier quadrillé, des montants raturés à la main.
W, H = 1000, 1400
paper = Image.new("RGB", (W, H), (236, 232, 220))
d = ImageDraw.Draw(paper)
for x in range(0, W, 40):
    d.line([x, 0, x, H], fill=(205, 214, 222), width=2)
for y in range(0, H, 40):
    d.line([0, y, W, y], fill=(205, 214, 222), width=2)
d.line([110, 0, 110, H], fill=(214, 140, 140), width=3)
ink = (38, 52, 96)
hand = font(46)
entries = [("Siphon", "45"), ("Joint", "6"), ("MO 1h", "55"), ("Depl.", "30"), ("TVA ??", ""), ("Total", "136 → 149 ?")]
for i, (label, amount) in enumerate(entries):
    y = 120 + i * 150
    d.text((150 + random.randint(-6, 6), y), label, font=hand, fill=ink)
    d.text((560 + random.randint(-6, 6), y), amount, font=hand, fill=ink)
    if i in (1, 3, 5):
        # Rature : un gribouillis sur le montant.
        x0 = 540
        pts = [(x0 + k * 22, y + 24 + (12 if k % 2 else -12)) for k in range(14)]
        d.line(pts, fill=ink, width=6)
d.line([150, 1080, 860, 1060], fill=ink, width=5)
paper = paper.filter(ImageFilter.GaussianBlur(0.8))
paper.save(out / "carnet.png")
print("ok", out)
