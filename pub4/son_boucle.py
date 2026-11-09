"""Son de la boucle (pub 4 v4) (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
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
INTRO = 4  # temps d'accroche avant l'histoire
D = 46 * B
DEBUT_MUSIQUE = 30.581 - INTRO * B  # un temps du morceau (grille vérifiée sur les grosses caisses, écart médian 4 ms)

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


m = lire(os.path.join(ICI, "musique", "mixkit-130.mp3"), DEBUT_MUSIQUE, D + 0.5)[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(0.7 * SR)
m[-k:] *= np.linspace(1, 0.15, k)[:, None]
musique[: len(m)] = m

deux = 2 / 60  # les « whoosh » partent 2 images en avance
sfx("kit/impact.ogg", 0, -9, "la bille se pose sur « Encore » (raccord de boucle)")
POPS = ("pop/fs-447910-plop.ogg", "kit/pop.ogg", "pop/fs-824189-pop-in-sfx.ogg", "pop/kenney-interface-drop-001.ogg")
for i, bt in enumerate((1, 2, 6, 11, 12, 13, 20, 21, 26, 27)):
    sfx(POPS[i % 4], bt, -9, "un mot s'allume")
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 3, -12, "le document du soir")
sfx("whoosh/fs-683101-quick-woosh.ogg", 4, -15, "chute vers « Dites-le. »", deux)
sfx("kit/click.ogg", 7, -4, "le micro s'allume")
sfx("whoosh/fs-683101-quick-woosh.ogg", 9, -15, "chute vers le devis", deux)
sfx("kit/impact.ogg", 14, -11, "la bille sur le devis")
for i, bt in enumerate((14, 14.5, 15)):
    sfx(f"ui-blip/kenney-ui-rollover{i + 1}.ogg", bt, -10, f"ligne {i + 1}")
for j in range(14):
    u = (j / 13) ** 0.7
    sfx("kit/tick.ogg", 16 + 2 * u, -17 + 6 * u, "le total monte")
sfx("whoosh/fs-264777-swoosh.ogg", 18, -14, "chute vers le client", deux)
for j in range(4):
    sfx("tick/fs721514.ogg", 22 + j * 0.25, -18, "la signature")
sfx("ding/kenney-interface-confirmation-002.ogg", 24, -6, "devis accepté")
sfx("whoosh/fs-683101-quick-woosh.ogg", 24, -15, "chute vers la facture", deux)
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 28, -7, "facture prête")
sfx("transition/fs-683096-woosh.ogg", 29, -5, "la bille s'envole, la caméra recule", deux)
sfx("kit/pop.ogg", 30.5, -12, "« Ce soir, vous êtes libre. »")
sfx("riser/fs-464250-echo-chromatic-riser-wav.ogg", 35.6, -16, "monte jusqu'au carton", finit=True)
sfx("kit/pop.ogg", 35.6, -8, "le carton Diktéo")
sfx("whoosh/fs-830856.ogg" if not os.path.exists(os.path.join(SKILL, "whoosh/fs830856.ogg")) else "whoosh/fs830856.ogg", 41.8, -9, "la caméra replonge", deux)

mix = musique * 10 ** (-9 / 20) + bruits
mix /= max(1e-6, np.abs(mix).max()) / 0.9
wav = os.path.join(ICI, "tmp", "son.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-16:TP=-5:LRA=11,alimiter=limit=0.52:level=false", "-shortest", "-movflags", "+faststart", SORTIE], check=True)
os.makedirs(os.path.join(ICI, "son"), exist_ok=True)
with open(os.path.join(ICI, "son", "CREDITS_boucle.txt"), "w", encoding="utf-8") as f:
    f.write("Musique : « Tech House vibes » par Alejandro Magaña (A. M.), Mixkit #130, Mixkit Stock Music Free License\n\nBruitages :\n")
    for cr in sorted({j[3] for j in journal}):
        f.write(f"- {cr}\n")
with open(os.path.join(ICI, "son", "SOUND_boucle.md"), "w", encoding="utf-8") as f:
    f.write("# Son de la pub 4\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #130 (licence vérifiée le 5 nov. 2026).\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
