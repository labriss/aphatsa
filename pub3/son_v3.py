"""Passe son de la pub 3 (méthode du skill sound-effects) : vraies musiques + vrais bruitages, aucun son synthétisé.
python son_v3.py → out/dikteo_pub3_plombier.mp4 (son remplacé), SOUND.md et CREDITS.txt dans out/son/."""
import json
import os
import subprocess
import wave

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser("~/.claude/skills/sound-effects/sfx")
VIDEO = os.path.join(ICI, "tmp", "v2", "image.mp4")
OUT = os.path.join(ICI, "out")
SR = 48000

MAN = json.load(open(os.path.join(SKILL, "manifest.json"), encoding="utf-8"))
INFO = {e["file"]: e for e in MAN["bundled"] if e.get("file")}
INFO.update({e["file"]: e for e in MAN["default_kit"] if e.get("file")})


def lire(chemin, debut=0.0, duree=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(debut), "-i", chemin]
    if duree:
        cmd += ["-t", str(duree)]
    raw = subprocess.run(cmd + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def duree_video():
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VIDEO],
                                capture_output=True, text=True).stdout)


T = duree_video()
N = int(T * SR)
musique = np.zeros((N, 2), np.float32)
bruits = np.zeros((N, 2), np.float32)
utilises = []


def poser(piste, sig, t, db=0.0, fondu_in=0.0, fondu_out=0.0):
    a = int(t * SR)
    if a >= N:
        return
    sig = sig[: N - a] * (10 ** (db / 20))
    if fondu_in:
        k = min(len(sig), int(fondu_in * SR))
        sig[:k] *= np.linspace(0, 1, k)[:, None]
    if fondu_out:
        k = min(len(sig), int(fondu_out * SR))
        sig[-k:] *= np.linspace(1, 0, k)[:, None]
    piste[a:a + len(sig)] += sig


def sfx(fichier, t, db=-6.0, desc=""):
    sig = lire(os.path.join(SKILL, fichier))
    sig = sig / max(1e-6, np.abs(sig).max())
    poser(bruits, sig, t, db)
    e = INFO.get(fichier, {})
    utilises.append((t, desc, fichier, e.get("credit", fichier), e.get("license", "?")))


# ——— musiques ———
# journée pixel : « 8-Bit Battle Loop », jusqu'au SMS de trop (23,9 s), coupée net
m1 = lire(os.path.join(ICI, "musique", "8BitBattleLoop.ogg"), 0, 23.9)
poser(musique, m1 / max(1e-6, np.abs(m1).max()), 0.0, -3, 0.05, 0.03)
# vraie vie : « It's Love » ; son temps fort (39,3 s du morceau) tombe quand la réalité a tout envahi (37,8 s)
T_REEL = 36.0
m2 = lire(os.path.join(ICI, "musique", "mixkit-834.mp3"), 39.3 - (37.8 - T_REEL), T - T_REEL)
poser(musique, m2 / max(1e-6, np.abs(m2).max()), T_REEL, -4, 0.4, 1.4)

# ——— bruitages (un son par moment, prises variées) ———
for t in (4.6, 8.8, 13.2, 17.4, 22.0):
    sfx("ui-blip/kenney-ui-rollover2.ogg", t, -16, "changement de scène")
coups = ["impact/kenney-impact-impactpunch-heavy-000.ogg", "impact/kenney-impact-impactpunch-heavy-001.ogg"]
for k, t in enumerate((3.4, 7.8, 12.0, 16.2, 20.8)):
    sfx(coups[k % 2], t, -8, "la patience baisse")
    sfx("glitch/kenney-interface-glitch-002.ogg", t + 0.02, -18, "la jauge tremble")
sfx("riser/fs-174363-rewind.ogg", 23.75, -8, "la musique s'arrête net")
sfx("impact/fs-347561-micheal-bay-hit.ogg", 23.9, -2, "il pète un câble")
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 24.7, -6, "coup sur la table")
sfx("impact/kenney-impact-impactpunch-heavy-001.ogg", 25.6, -7, "coup sur la table")
sfx("ambience/fs-329533-room-tone-in-an-apartment-livi.ogg", 26.0, -18, "le calme après la crise")
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 28.9, -6, "la notification Diktéo")
sfx("typing/fs-416777-digital-typing-wav.ogg", 31.9, -16, "le devis se remplit")
for k in range(6):
    sfx("ui-blip/kenney-ui-rollover%d.ogg" % (1 + k % 4), 31.6 + k * 0.5, -18, "la patience remonte")
sfx("pop/fs-824189-pop-in-sfx.ogg", 34.6, -8, "le devis est prêt")
sfx("riser/fs-464250-echo-chromatic-riser-wav.ogg", 34.9, -9, "la réalité arrive")
sfx("transition/fs-786514-swoosh-v2.ogg", 36.0 - 2 / 30, -6, "la réalité part du téléphone")
sfx("glitch/kenney-sci-computernoise-000.ogg", 36.6, -16, "la jauge du jeu tombe")
sfx("impact/fs-177242-cinematic-impact.ogg", 37.8, -6, "le monde est réel")
sfx("ambience/fs-426767-apartment-room-tone-wav.ogg", 36.0, -20, "pièce réelle")
sfx("whoosh/fs-683101-quick-woosh.ogg", 43.4 - 2 / 30, -8, "le téléphone 3D")
sfx("click/kenney-interface-click-001.ogg", 45.0, -10, "on touche le micro")
sfx("ding/kenney-interface-confirmation-001.ogg", 47.45, -6, "le logo")

# ——— mixage : bruitages au-dessus, musique dessous, puis niveau réseaux (-16 LUFS, crête < -4 dBTP) ———
mix = musique * 0.55 + bruits * 0.9
mix /= max(1e-6, np.abs(mix).max()) / 0.9
os.makedirs(os.path.join(OUT, "son"), exist_ok=True)
wav = os.path.join(ICI, "tmp", "v2", "son_v3.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
sortie = os.path.join(OUT, "dikteo_pub3_plombier.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-16:TP=-5:LRA=11,alimiter=limit=0.56:level=false", "-shortest", "-movflags", "+faststart", sortie],
               check=True)

with open(os.path.join(OUT, "son", "CREDITS.txt"), "w", encoding="utf-8") as f:
    f.write("Musique :\n- « 8-Bit Battle Loop » par Theodore Kerr (Wolfgang_), https://opengameart.org/content/8-bit-battle-loop, CC0\n")
    f.write("- « It's Love » par Michael Ramir C., Mixkit #834, Mixkit Stock Music Free License\n\nBruitages :\n")
    for cr in sorted({u[3] for u in utilises}):
        f.write(f"- {cr}\n")
with open(os.path.join(OUT, "son", "SOUND.md"), "w", encoding="utf-8") as f:
    f.write("# Son de la pub 3\n\nUsage : TikTok, Instagram Reels, YouTube Shorts, pubs en ligne.\n\n| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(utilises):
        f.write(f"| {t:.2f} | {desc} | {fi} | {li} |\n")
print("OK", sortie, len(utilises), "bruitages")
print("licences inconnues :", [u[2] for u in utilises if u[4] == "?"])
