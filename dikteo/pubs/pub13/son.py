"""Son de la pub 13, mot après mot (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
python son.py <video_muette.mp4> <sortie.mp4>"""
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.ndimage import uniform_filter1d

ICI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser("~/.claude/skills/sound-effects/sfx")
VIDEO, SORTIE = sys.argv[1], sys.argv[2]
SR = 48000
B = 60 / 83
D = 27 * B
# « It's April », Mixkit #847 (acoustique) : 83,0 BPM mesurés (contraste du peigne 12,3), phase 0,398 s.
# On part du temps 16, là où tout l'orchestre entre.
PISTE, BPM_P, PHASE_P, SAUT_P = "847", 83.0, 0.398, 16
TITRE_P = "« It's April » (Mixkit)"
DEBUT_MUSIQUE = PHASE_P + SAUT_P * 60 / BPM_P

MAN = json.load(open(os.path.join(SKILL, "manifest.json"), encoding="utf-8"))
INFO = {e["file"]: e for e in MAN["bundled"] + MAN["default_kit"] if e.get("file")}


def lire(chemin, debut=0.0, duree=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(debut), "-i", chemin] + (["-t", str(duree)] if duree else []) + (["-af", af] if af else [])
    raw = subprocess.run(cmd + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(D * SR) + 1
musique, bruits, journal = np.zeros((N, 2), np.float32), np.zeros((N, 2), np.float32), []


def sfx(f, beat, db=-6.0, desc="", avance=0.0, finit=False):
    s = lire(os.path.join(SKILL, f))
    t = beat * B - avance - (len(s) / SR if finit else 0)
    s = s / max(1e-6, np.abs(s).max()) * 10 ** (db / 20)
    a = max(0, int(t * SR))
    s = s[: N - a]
    bruits[a:a + len(s)] += s
    journal.append((t, desc, f, INFO.get(f, {}).get("credit", f), INFO.get(f, {}).get("license", "?")))


m = lire(os.path.join(ICI, "musique", f"mixkit-{PISTE}.mp3"), DEBUT_MUSIQUE, D + 0.5)[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(1.6 * SR)
m[-k:] *= np.linspace(1, 0.0, k)[:, None]
musique[: len(m)] = m

# Pub 13 : le cordeau claque ; chaque mot dicté tombe en carreau (clac céramique), le prix tombe plus lourd ;
# la vague de pose en cascade de petits clacs ; le maillet ; l'envoi ; le carton.
CLAC = "impact/fs745291.ogg"
sfx("tick/fs384187.ogg", .05, -7, "le cordeau claque")
sfx("whoosh/fs-127197-fast-simple-chop-5-aif.ogg", .05, -14, "la poudre de craie")
sfx("kit/click.ogg", 2.5, -14, "« TU DICTES » s'allume")
PHRASES = [3, 6, 9, 12]
for p in PHRASES:
    for j in range(4):
        sfx(CLAC, p + j * .42 + .16 / B * 60 / 60, -13 - (j % 2), "un mot se pose en carreau")
    sfx(CLAC, p + 2.0 + .16, -9, "le carreau du prix")
    sfx("impact/kenney-impact-impactpunch-heavy-001.ogg", p + 2.0 + .16, -17, "le poids du carreau du prix")
import random
random.seed(13)
for c in range(-1, 6):
    for r in range(-4, 7):
        if 0 <= c <= 4 and 0 <= r <= 3:
            continue
        if random.random() < .45:
            sfx(CLAC, 15 + (c + (r + 4) * .55) * .17 + .16, -27 + random.random() * 5, "la vague de pose")
sfx("ding/fs-349504-triangle-open-04.ogg", 16.8, -14, "le coup de lumière sur le carrelage")
sfx(CLAC, 17.4 + .16, -10, "le dernier carreau tombe")
sfx("impact/kenney-impact-impactpunch-heavy-000.ogg", 17.95, -6, "le coup de maillet")
sfx("whoosh/fs-169867-swoosh.ogg", 19.4, -12, "le carreau se retourne", 2 / 60)
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 19.8, -9, "envoyé à M. Bernard")
sfx("ding/kenney-interface-confirmation-002.ogg", 21.5, -11, "le carton Diktéo")

# la musique un peu plus basse pendant la pile, pour laisser la place aux chocs
tb = np.arange(N) / SR / B
env = np.where(tb < 0, 1.0, 1.0).astype(np.float32)
env = uniform_filter1d(env, int(.2 * SR), mode="constant").astype(np.float32)
# ——— la voix : l'artisan dicte ses lignes (son/voix : dicter.py → noter.py → prises/choix.json) ; absente sans choix.json ———
# une phrase par bandeau « TU DICTES » (temps de musique) ; FIN : la vague de pose, la dernière phrase doit être dite avant
DEBUTS, FIN = [3, 6, 9, 12], 15
sys.path.insert(0, os.path.join(ICI, "..", "son", "voix"))
from poser import poser_voix  # noqa: E402
voix, sous_voix = poser_voix(ICI, lire, N, SR, B, DEBUTS, FIN, journal, INFO, SKILL)
mix = musique * (env * sous_voix)[:, None] * 10 ** (float(os.environ.get("MUSIQUE_DB", "-4")) / 20) + bruits * 10 ** (float(os.environ.get("BRUITS_DB", "-5")) / 20) + voix
mix /= max(1e-6, np.abs(mix).max()) / 0.9
wav = os.path.join(ICI, "tmp", "son.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-16:TP=-5:LRA=11,alimiter=limit=0.52:level=false", "-shortest", "-movflags", "+faststart", SORTIE], check=True)
os.makedirs(os.path.join(ICI, "son"), exist_ok=True)
with open(os.path.join(ICI, "son", "CREDITS.txt"), "w", encoding="utf-8") as f:
    f.write(f"Musique : {TITRE_P}, Mixkit #{PISTE}, Mixkit Stock Music Free License\n\nBruitages :\n")
    for cr in sorted({j[3] for j in journal}):
        f.write(f"- {cr}\n")
with open(os.path.join(ICI, "son", "SOUND.md"), "w", encoding="utf-8") as f:
    f.write(f"# Son de la pub 13 (mot après mot)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
