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
# Morceau choisi par variables d'environnement (défaut : « Hazy After Hours », Mixkit #132) : numéro, tempo mesuré, phase, temps sautés.
PISTE = os.environ.get("PISTE", "132")
BPM_P = float(os.environ.get("BPM_P", "121"))
PHASE_P = float(os.environ.get("PHASE_P", "0.124"))
SAUT_P = int(os.environ.get("SAUT_P", "16"))
TITRE_P = os.environ.get("TITRE_P", "« Hazy After Hours » par Alejandro Magaña (A. M.)")
DEBUT_MUSIQUE = PHASE_P + SAUT_P * 60 / BPM_P  # étiré de 123/BPM_P pour tomber sur la grille de la pub

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


m = lire(os.path.join(ICI, "musique", f"mixkit-{PISTE}.mp3"), DEBUT_MUSIQUE, (D + 0.5) * 123 / BPM_P, af=f"atempo={123 / BPM_P:.5f}")[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(1.6 * SR)
m[-k:] *= np.linspace(1, 0.0, k)[:, None]
musique[: len(m)] = m

deux = 2 / 60
sfx("pop/kenney-interface-pluck-001.ogg", 0, -9, "« Un devis, chrono en main. »")
sfx("ding/fs-634690-lil-pip.ogg", 2.5, -10, "le chrono apparaît")
sfx("transition/fs-816262-broomstick-whoosh-3-quiet-okm1.ogg", 4, -8, "le téléphone arrive", deux)
sfx("click/kenney-interface-select-001.ogg", 4, -10, "le chrono part")
sfx("click/kenney-interface-toggle-001.ogg", 5.5, -6, "le doigt touche le micro")
sfx("pop/kenney-interface-maximize-001.ogg", 14, -14, "« Le devis se remplit… »")
for f, bt in (("pop/kenney-interface-drop-001.ogg", 15), ("pop/kenney-interface-drop-002.ogg", 15.5),
              ("pop/kenney-interface-drop-003.ogg", 16), ("pop/kenney-interface-pluck-002.ogg", 16.5)):
    sfx(f, bt, -10, "une ligne du devis")
for j in range(6):
    sfx("tick/fs528561.ogg", 16.6 + 0.3 * j, -21 + j, "le total monte")
sfx("click/kenney-interface-click-001.ogg", 20, -6, "« Valider et envoyer »")
sfx("whoosh/fs-169867-swoosh.ogg", 20.4, -10, "l'avion part vers le client", deux)
sfx("ding/kenney-interface-glass-001.ogg", 20.4, -9, "envoyé à Mme Fontaine")
sfx("ding/fs-349504-triangle-open-04.ogg", 20.6, -9, "le chrono s'arrête")
sfx("transition/kenney-interface-maximize-005.ogg", 21, -12, "le chrono vient au centre")
sfx("pop/fs-514833-user-interface-menu-sounds-wav.ogg", 21.3, -14, "éclat")
sfx("pop/kenney-interface-pluck-002.ogg", 24.5, -10, "« Ce soir, vous êtes libre. »")
sfx("ding/kenney-interface-confirmation-001.ogg", 28.5, -9, "le carton Diktéo")

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
    f.write(f"Musique : {TITRE_P}, Mixkit #{PISTE}, Mixkit Stock Music Free License\n\nBruitages :\n")
    for cr in sorted({j[3] for j in journal}):
        f.write(f"- {cr}\n")
with open(os.path.join(ICI, "son", "SOUND.md"), "w", encoding="utf-8") as f:
    f.write(f"# Son de la pub 5 (le défi chrono)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
