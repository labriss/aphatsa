"""Son de la pub 8, la pile de galères (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
python son.py <video_muette.mp4> <sortie.mp4>"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser("~/.claude/skills/sound-effects/sfx")
VIDEO, SORTIE = sys.argv[1], sys.argv[2]
SR = 48000
B = 60 / 121
D = 48 * B
# Morceau choisi par variables d'environnement (défaut : « Smile », Mixkit #1076, choisie par l'utilisateur le 10 nov. 2026) : numéro, tempo mesuré, phase, temps sautés.
PISTE = os.environ.get("PISTE", "474")
BPM_P = float(os.environ.get("BPM_P", "121"))
PHASE_P = float(os.environ.get("PHASE_P", "0.112"))
SAUT_P = int(os.environ.get("SAUT_P", "16"))
TITRE_P = os.environ.get("TITRE_P", "« Motivating Mornings » (Mixkit)")
DEBUT_MUSIQUE = PHASE_P + SAUT_P * 60 / BPM_P  # étiré de 121/BPM_P pour tomber sur la grille de la pub

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


m = lire(os.path.join(ICI, "musique", f"mixkit-{PISTE}.mp3"), DEBUT_MUSIQUE, (D + 0.5) * 121 / BPM_P, af=f"atempo={121 / BPM_P:.5f}")[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(1.6 * SR)
m[-k:] *= np.linspace(1, 0.0, k)[:, None]
musique[: len(m)] = m

deux = 2 / 60
SOBRE = False
# Pub 8 : chaque galère tombe avec un coup sourd, « LES DEVIS » s'écrase lourdement, la voix balaie la pile,
# le vrai écran se remplit, l'envoi, le carton.
sfx("kit/pop.ogg", 0, -10, "« Artisan ? »")
for i in range(6):
    sfx("impact/kenney-impact-impactsoft-heavy-00%d.ogg" % (i % 2), 2 + i * 2 + .72, -9 + i * .6, "une galère tombe sur la pile")
sfx("kit/tick.ogg", 13, -10, "22 h 07 s'allume")
sfx("riser/fs-464250-echo-chromatic-riser-wav.ogg", 16 + .72, -15, "la pile monte en tension", finit=True)
sfx("impact/fs-222517-dramatic-hit.ogg", 16 + .72, -4, "« LES DEVIS. » s'écrase")
sfx("whoosh/fs-169867-swoosh.ogg", 19.5, -7, "l'onde de voix balaie la pile", deux)
sfx("transition/fs-683096-woosh.ogg", 20.6, -12, "le téléphone monte", deux)
sfx("kit/click.ogg", 22, -10, "le micro")
for j in range(4):
    sfx("pop/kenney-interface-drop-00%d.ogg" % (j % 3 + 1), 29.5 + j * .5, -15, "une ligne du devis")
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 33.6, -9, "envoyé")
sfx("ding/kenney-interface-confirmation-001.ogg", 38.8, -13, "le carton Diktéo")

mix = musique * 10 ** (-7 / 20) + bruits
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
    f.write(f"# Son de la pub 8 (la pile)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
