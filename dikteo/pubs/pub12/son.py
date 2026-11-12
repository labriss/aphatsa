"""Son de la pub 12, le rouleau (méthode du skill sound-effects) : vraie musique calée sur la grille, vrais bruitages sur chaque contact.
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
B = 60 / 85
D = 28 * B
# « Walking in the Park », Mixkit #529 : 85,0 BPM mesurés (contraste du peigne 12,7), phase 0,399 s, temps fort tous les 8 temps.
# On part du temps 32 (début de section, 22,99 s) : la pub est déjà à 85 BPM, aucun étirement.
PISTE, BPM_P, PHASE_P, SAUT_P = "529", 85.0, 0.399, 32
TITRE_P = "« Walking in the Park » (Mixkit)"
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

# Pub 12 : le tag bombé ; un clic de micro par phrase ; chaque geste a son bruit doux (couteau, coups de rouleau,
# ruban arraché, bâche) ; la lumière s'allume, le cadre se pose ; le total ; l'envoi ; le carton.
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 0, -6, "« PEINTRE ? » bombé")
sfx("whoosh/fs-264777-swoosh.ogg", 0, -13, "le jet de la bombe", 1 / 60)
sfx("whoosh/fs-264777-swoosh.ogg", .75, -16, "la question bombée", 1 / 60)
for bt in (3, 6, 10, 14):
    sfx("kit/click.ogg", bt - (.3 if bt == 3 else 0), -12, "une phrase dictée")
for k in range(4):
    sfx("transition/fs-850347-swipe-various.ogg", 3.6 + .5 * k, -17, "le couteau lisse l'enduit")
# Le rouleau : pas de « swipe » (trop aigu, il glisse en hauteur : on dirait un laser). Un vrai souffle enregistré,
# filtré bas-médium et pulsé au rythme du manchon qui tourne : le frottement mat d'un rouleau chargé de peinture.
SOUFFLE = "ambience/fs-329569-roomtone-bedroom-yew.ogg"


def frottement(beat, duree_b, db, desc, k):
    d = duree_b * B + .12
    s = lire(os.path.join(SKILL, SOUFFLE), (1 + k * .61) % 17, d, af="highpass=f=220,lowpass=f=1500,lowpass=f=1500")
    t = np.arange(len(s)) / SR
    env = np.minimum(1, t / .05) * np.minimum(1, np.maximum(0, (d - t) / .14))
    env *= 1 - .22 * (.5 + .5 * np.sin(2 * np.pi * 7.5 * t + k))
    s = s * env[:, None]
    s = s / max(1e-6, np.abs(s).max()) * 10 ** (db / 20)
    a = int(beat * B * SR)
    s = s[: N - a]
    bruits[a:a + len(s)] += s
    journal.append((beat * B, desc, SOUFFLE, INFO.get(SOUFFLE, {}).get("credit", SOUFFLE), INFO.get(SOUFFLE, {}).get("license", "?")))


for j in range(6):
    frottement(6.6 + .5 * j, .5, -13, "coup de rouleau, sous-couche", j)
for j in range(6):
    frottement(10.6 + .33 * j, .33, -14, "coup de rouleau, 1re couche", 10 + j)
for j in range(6):
    frottement(12.7 + .2 * j, .2, -16, "2e couche", 20 + j)
sfx("transition/fs-786514-swoosh-v2.ogg", 14.6, -11, "le ruban de masquage s'arrache")
sfx("whoosh/fs-169867-swoosh.ogg", 15.6, -9, "la bâche glisse")
sfx("click/kenney-interface-toggle-001.ogg", 17.1, -10, "les appliques s'allument")
sfx("impact/kenney-impact-impactsoft-heavy-001.ogg", 17.95, -11, "le cadre se pose")
sfx("pop/fs-447910-plop.ogg", 18.25, -15, "la plante")
sfx("impact/kenney-impact-impactsoft-heavy-000.ogg", 18.6, -8, "le total")
sfx("ding/fs-349504-triangle-open-04.ogg", 19.25, -11, "le coup de lumière sur le total")
sfx("whoosh/fs-683101-quick-woosh.ogg", 20.6, -10, "le devis part", 2 / 60)
sfx("ding/fs-571513-soft-notifications-bell-ding-d.ogg", 20.9, -9, "envoyé à Mme Garnier")
sfx("ding/kenney-interface-confirmation-002.ogg", 22.7, -11, "le carton Diktéo")

# ——— la voix : le peintre dicte ses 4 lignes (son/voix : dicter.py → noter.py → voix/prises/choix.json) ; absente sans choix.json ———
# une phrase par bandeau (temps de musique) ; FIN : les appliques s'allument
DEBUTS, FIN = [2.7, 6, 10, 14], 17.1
sys.path.insert(0, os.path.join(ICI, "..", "son", "voix"))
from poser import poser_voix  # noqa: E402
voix, sous_voix = poser_voix(ICI, lire, N, SR, B, DEBUTS, FIN, journal, INFO, SKILL)
mix = musique * sous_voix[:, None] * 10 ** (float(os.environ.get("MUSIQUE_DB", "-4")) / 20) + bruits * 10 ** (float(os.environ.get("BRUITS_DB", "-5")) / 20) + voix
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
    f.write(f"# Son de la pub 12 (le rouleau)\n\nUsage : TikTok, Reels, Shorts, pubs en ligne. Musique : Mixkit #{PISTE}, Mixkit Stock Music Free License.\n\n")
    f.write("| t (s) | moment | son | licence |\n|---|---|---|---|\n")
    for t, desc, fi, cr, li in sorted(journal):
        f.write(f"| {t:.3f} | {desc} | {fi} | {li} |\n")
print("OK", SORTIE, "licences inconnues :", [j[2] for j in journal if j[4] == "?"])
