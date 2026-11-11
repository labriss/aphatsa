"""Son de la pub 19, la tournée (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
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
B = 60 / 75
D = 25 * B
# « Summer's Here », Mixkit #91 (acoustique) : 75,0 BPM mesurés (contraste du peigne 19,3), phase 0,467 s ; on part du temps 8.
PISTE, BPM_P, PHASE_P, SAUT_P = "91", 75.0, 0.467, 8
TITRE_P = "« Summer's Here » (Mixkit)"
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


m = lire(os.path.join(ICI, "musique", f"mixkit-{PISTE}.mp3"), DEBUT_MUSIQUE, (D + 0.5) * 75 / BPM_P, af=f"atempo={75 / BPM_P:.5f}")[:N]
m = m / max(1e-6, np.abs(m).max())
k = int(0.03 * SR)
m[:k] *= np.linspace(0, 1, k)[:, None]
k = int(1.6 * SR)
m[-k:] *= np.linspace(1, 0.0, k)[:, None]
musique[: len(m)] = m

# Pub 18 : le crayon, un clic de micro par phrase ; le rabot (souffle filtré aigu qui suit la passe) ; le fer qui grave
# le prix (grésillement + crépitements) ; le chiffon d'huile ; le total gravé ; l'envoi ; le carton.
SOUFFLE = "ambience/fs-329569-roomtone-bedroom-yew.ogg"


def bruit(beat, duree_b, db, desc, k, filtre, pulse=0.0, attaque=.04, chute=.12):
    d = duree_b * B
    s = lire(os.path.join(SKILL, SOUFFLE), (1 + k * .61) % 17, d, af=filtre)
    t = np.arange(len(s)) / SR
    env = np.minimum(1, t / attaque) * np.minimum(1, np.maximum(0, (d - t) / chute))
    if pulse:
        env *= 1 - .3 * (.5 + .5 * np.sin(2 * np.pi * pulse * t + k))
    s = s * env[:, None]
    s = s / max(1e-6, np.abs(s).max()) * 10 ** (db / 20)
    a = int(beat * B * SR)
    s = s[: N - a]
    bruits[a:a + len(s)] += s
    journal.append((beat * B, desc, SOUFFLE, INFO.get(SOUFFLE, {}).get("credit", SOUFFLE), INFO.get(SOUFFLE, {}).get("license", "?")))


def fer(beat, db, desc, k, gros=False):
    bruit(beat, 2.4 if gros else 1.6, db, desc, k, "highpass=f=2500,lowpass=f=9000", attaque=.01, chute=.6)
    for j in range(9 if gros else 5):
        sfx("tick/fs384187.ogg", beat + .08 + rnd(k * 17 + j) * (1.6 if gros else 1.0), db - 8 - 6 * rnd(k * 5 + j), "crépitement du fer")


def rnd(n):
    return (np.sin(n * 127.1 + 311.7) * 43758.5453) % 1


sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 0, -8, "« MULTISERVICE ? »")
ARR = (3, 6, 9, 12, 15)
departs = [2.2] + [a + 1.7 for a in ARR]
arrivees = list(ARR) + [17.4]
for k, (d0, d1) in enumerate(zip(departs, arrivees)):
    bruit(d0, d1 - d0, -17, "l'utilitaire roule", 50 + k, "highpass=f=60,lowpass=f=420", pulse=6, attaque=.25, chute=.35)
for k, a in enumerate(ARR):
    sfx("kit/click.ogg", a, -13, "une phrase dictée")
    sfx("pop/fs-447910-plop.ogg", a + 1.35, -12, "l'épingle s'allume")
    sfx("ding/kenney-interface-confirmation-001.ogg" if k % 2 else "ding/fs-634690-lil-pip.ogg", a + 1.25, -16, "envoyé")
sfx("whoosh/fs-169867-swoosh.ogg", 17.6, -10, "la caméra recule", 2 / 60)
sfx("riser/fs-685256-riser-sound-effect-short-wav.ogg", 18.0, -16, "la tournée se révèle")
sfx("ding/fs-349504-triangle-open-04.ogg", 19.2, -10, "la bulle Diktéo apparaît")
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 20.2, -12, "5 devis envoyés")
sfx("ding/kenney-interface-confirmation-002.ogg", 22.5, -11, "le carton Diktéo")

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
    f.write(f"# Son de la pub 19 (la tournée)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
