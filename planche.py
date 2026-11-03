# La planche du storyboard : les 10 plans de la pub, image clé + minutage + texte + son.
# Usage : python planche.py <sortie.png>
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

R = Path(__file__).resolve().parent / "renders"
T = R / "sb_titres"
NIGHT = (14, 20, 18)


def font(size, bold=False):
    for name in (["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def over(base, titres):
    img = base.convert("RGBA")
    img.alpha_composite(Image.open(titres).convert("RGBA"))
    return img.convert("RGB")


def scene_metier():
    bg = Image.new("RGB", (1080, 1920), NIGHT)
    s = Image.open(R / "sb_metier" / "electricien_0001.png").convert("RGB").resize((1000, 1000), Image.LANCZOS)
    bg.paste(s, (40, 440))
    return over(bg, T / "titres_0005.png")


def bascule():
    # Plan 4 : la lueur de l'écran vire à l'orange, la caméra plonge dedans (flou d'élan).
    k = Image.open(R / "sb_cuisine_nuit.png").convert("RGB")
    k = k.crop((80, 900, 680, 1966)).resize((1080, 1920), Image.LANCZOS)
    r, g, b = k.split()
    k = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.9 + 20))), g.point(lambda v: int(v * 0.75)), b.point(lambda v: int(v * 0.35))))
    k = k.filter(ImageFilter.GaussianBlur(10))
    k = ImageEnhance.Brightness(k).enhance(0.75)
    return over(k, T / "titres_0003.png")


PLANS = [
    ("1", "0,0 – 2,5 s", "Blender", lambda: over(Image.open(R / "sb_goutte.png"), T / "titres_0001.png"),
     "Gros plan : la goutte se forme sous l'écrou et tombe au ralenti.", "Silence, puis « plic »."),
    ("2", "2,5 – 5,0 s", "Blender", lambda: over(Image.open(R / "sb_cuisine_nuit.png"), T / "titres_0002.png"),
     "La table de la cuisine à 22:47 : tableur, carnet raturé, café froid.", "Bourdon grave, tic-tac."),
    ("3", "5,0 – 7,0 s", "Blender", lambda: Image.open(R / "sb_horloge.png"),
     "On avance vers l'horloge, les aiguilles filent jusqu'à 23:38.", "Le tic-tac accélère."),
    ("4", "7,0 – 8,0 s", "Blender", bascule,
     "La lueur de l'écran vire à l'orange, la caméra plonge dedans.", "Souffle, la musique part."),
    ("5", "8,0 – 13,0 s", "Blender + appli", lambda: Image.open(R / "sb_tel_monte.png"),
     "Le téléphone monte dans la lueur ; la vraie appli : on dicte.", "Montée électro, clic du micro."),
    ("6", "13,0 – 16,5 s", "Blender + appli", lambda: over(Image.open(R / "sb_tel_face.png"), T / "titres_0004.png"),
     "DROP : les lignes du devis tombent sur le rythme, le total monte.", "Drop."),
    ("7", "16,5 – 19,5 s", "Blender + appli", lambda: Image.open(R / "sb_tel_envoye.png"),
     "On valide : « Envoyé à Mme Fontaine ». Le téléphone pivote.", "« Ding »."),
    ("8", "19,5 – 24,0 s", "Animations du site", scene_metier,
     "Les 9 autres métiers, 0,5 s chacun : la réparation, le nom en grand.", "Une coupe par temps."),
    ("9", "24,0 – 26,5 s", "Blender", lambda: Image.open(R / "sb_cuisine_soir.png"),
     "La même table à 18:30 : ordinateur fermé, plus de paperasse, le soleil.", "La musique respire."),
    ("10", "26,5 – 30,0 s", "Titres", lambda: Image.open(T / "titres_0006.png"),
     "Logo, promesse, « Gratuit pour commencer », l'adresse.", "Note finale."),
]

TW, TH = 360, 640
COLS, GAP, PAD = 5, 36, 60
CAP = 250
W = PAD * 2 + COLS * TW + (COLS - 1) * GAP
H = 230 + 2 * (TH + CAP) + GAP + PAD
sheet = Image.new("RGB", (W, H), (242, 245, 243))
d = ImageDraw.Draw(sheet)
d.text((PAD, 50), "Fuitéo — pub 30 s, storyboard", font=font(64, True), fill=(21, 32, 27))
d.text((PAD, 135), "Vertical 1080 × 1920 · avant gris et froid, après orange et chaud · images réelles des rendus (qualité brouillon)", font=font(30), fill=(86, 100, 94))


def wrap(text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


for i, (num, temps, outil, make, image, son) in enumerate(PLANS):
    x = PAD + (i % COLS) * (TW + GAP)
    y = 230 + (i // COLS) * (TH + CAP + GAP)
    img = make().convert("RGB").resize((TW, TH), Image.LANCZOS)
    sheet.paste(img, (x, y))
    d.rounded_rectangle([x + 14, y + 14, x + 74, y + 64], 12, fill=(201, 72, 10))
    d.text((x + 44, y + 39), num, font=font(30, True), fill="white", anchor="mm")
    cy = y + TH + 16
    d.text((x, cy), temps, font=font(28, True), fill=(21, 32, 27))
    d.text((x + TW, cy + 4), outil, font=font(22), fill=(86, 100, 94), anchor="ra")
    cy += 44
    for line in wrap(image, font(24), TW):
        d.text((x, cy), line, font=font(24), fill=(21, 32, 27))
        cy += 31
    d.text((x, cy + 6), "Son : " + son, font=font(23, True), fill=(201, 72, 10))

out = Path(sys.argv[1] if len(sys.argv) > 1 else "storyboard.png")
sheet.save(out, quality=92)
print(out, sheet.size)
