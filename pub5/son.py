"""Son de la pub 5, le défi chrono (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
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
B = 60 / 123
D = 36 * B
DEBUT_MUSIQUE = 0.402 + 32 * B  # grosse caisse, début d'une section de 8 mesures (tempo mesuré : 123 BPM, phase 0,402 s)

MAN = json.load(open(os.path.join(SKILL, "manifest.json"), encoding="utf-8"))
INFO = {e["file"]: e for e in MAN["bundled"] + MAN["default_kit"] if e.get("file")}


def lire(chemin, debut=0.0, duree=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(debut), "-i", chemin] + (["-t", str(duree)] if duree else [])
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


m = lire(os.path.join(ICI, "musique", "mixkit-171.mp3"), DEBUT_MUSIQUE, D + 0.5)[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(1.6 * SR)
m[-k:] *= np.linspace(1, 0.0, k)[:, None]
musique[: len(m)] = m

deux = 2 / 60
sfx("kit/pop.ogg", 0, -9, "« Un devis, chrono en main. »")
sfx("kit/tick.ogg", 2.5, -6, "le chrono apparaît")
sfx("transition/fs-683096-woosh.ogg", 4, -9, "le téléphone arrive", deux)
sfx("kit/click.ogg", 4, -7, "le chrono part")
for j in range(5, 20):
    sfx("tick/fs721514.ogg", j, -24, "tic du chrono")
sfx("kit/click.ogg", 5.5, -4, "le doigt touche le micro")
sfx("pop/fs-824189-pop-in-sfx.ogg", 14, -16, "« Le devis se remplit… »")
for i, bt in enumerate((15, 15.5, 16, 16.5)):
    sfx(f"ui-blip/kenney-ui-rollover{i % 3 + 1}.ogg", bt, -9, f"ligne {i + 1}")
for j in range(12):
    u = (j / 11) ** 0.7
    sfx("kit/tick.ogg", 16.5 + 1.7 * u, -18 + 6 * u, "le total monte")
sfx("kit/click.ogg", 20, -4, "« Valider et envoyer »")
sfx("transition/fs-683096-woosh.ogg", 20.4, -8, "l'avion part vers le client", deux)
sfx("ding/kenney-interface-confirmation-002.ogg", 20.4, -7, "envoyé à Mme Fontaine")
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 20.5, -6, "le chrono s'arrête")
sfx("whoosh/fs-683101-quick-woosh.ogg", 21, -12, "le chrono vient au centre", deux)
sfx("pop/fs-447910-plop.ogg", 21.3, -10, "éclat")
sfx("kit/pop.ogg", 24.5, -10, "« Ce soir, vous êtes libre. »")
sfx("riser/fs-464250-echo-chromatic-riser-wav.ogg", 28.5, -16, "monte jusqu'au carton", finit=True)
sfx("kit/pop.ogg", 28.5, -8, "le carton Diktéo")

mix = musique * 10 ** (-9 / 20) + bruits
mix /= max(1e-6, np.abs(mix).max()) / 0.9
wav = os.path.join(ICI, "tmp", "son.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-16:TP=-5:LRA=11,alimiter=limit=0.52:level=false", "-shortest", "-movflags", "+faststart", SORTIE], check=True)
os.makedirs(os.path.join(ICI, "son"), exist_ok=True)
with open(os.path.join(ICI, "son", "CREDITS.txt"), "w", encoding="utf-8") as f:
    f.write("Musique : « Techno Fights » par Alejandro Magaña (A. M.), Mixkit #171, Mixkit Stock Music Free License\n\nBruitages :\n")
    for cr in sorted({j[3] for j in journal}):
        f.write(f"- {cr}\n")
with open(os.path.join(ICI, "son", "SOUND.md"), "w", encoding="utf-8") as f:
    f.write("# Son de la pub 5 (le défi chrono)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #171, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
