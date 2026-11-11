"""Son de la pub 11, le tableau (électriciens) (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
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
B = 60 / 144
D = 34 * B
# Morceau choisi par variables d'environnement (défaut : « Smile », Mixkit #1076, choisie par l'utilisateur le 10 nov. 2026) : numéro, tempo mesuré, phase, temps sautés.
PISTE = os.environ.get("PISTE", "801")
BPM_P = float(os.environ.get("BPM_P", "143.55"))
PHASE_P = float(os.environ.get("PHASE_P", "0.0697"))
SAUT_P = int(os.environ.get("SAUT_P", "8"))
TITRE_P = os.environ.get("TITRE_P", "« Happy Home » (Mixkit)")
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


m = lire(os.path.join(ICI, "musique", f"mixkit-{PISTE}.mp3"), DEBUT_MUSIQUE, (D + 0.5) * 144 / BPM_P, af=f"atempo={144 / BPM_P:.5f}")[:N]
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
sfx("riser/fs-685256-riser-sound-effect-short-wav.ogg", 0, -16, "le néon grésille")
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 0.4, -8, "« ÉLECTRICIEN ? » s'allume")
sfx("whoosh/fs-169867-swoosh.ogg", 3.0, -12, "le tableau sort de l'ombre", 2 / 60)
for bt in (5, 7, 9, 11):
    sfx("kit/click.ogg", bt, -11, "une phrase dictée")
    sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", bt + .3, -7, "le disjoncteur claque")
sfx("impact/fs-177242-cinematic-impact.ogg", 14.2, -4, "l'interrupteur général")
sfx("riser/fs-685256-riser-sound-effect-short-wav.ogg", 14.5, -14, "le compteur déroule le total")
sfx("whoosh/fs-683101-quick-woosh.ogg", 16.6, -10, "la caméra recule", 2 / 60)
for i in range(5):
    sfx("pop/fs-447910-plop.ogg", 18.0 + i * .6, -14, "une fenêtre s'allume")
sfx("whoosh/fs-169867-swoosh.ogg", 21.8, -6, "le devis part du toit", 2 / 60)
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 23.4, -8, "envoyé")
sfx("ding/kenney-interface-confirmation-002.ogg", 26.2, -11, "le carton Diktéo")

# la musique un peu plus basse pendant la pile, pour laisser la place aux chocs
tb = np.arange(N) / SR / B
env = np.where(tb < 0, 1.0, 1.0).astype(np.float32)
env = np.convolve(env, np.ones(int(.2 * SR)) / int(.2 * SR), mode="same").astype(np.float32)
mix = musique * env[:, None] * 10 ** (-7 / 20) + bruits
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
    f.write(f"# Son de la pub 11 (le tableau)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
