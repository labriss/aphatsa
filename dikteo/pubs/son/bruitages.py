# Les bruitages de la pub : de vrais sons enregistrés (CC0, son/sfx/, crédits dans son/sfx/CREDITS.txt),
# posés aux instants du découpage (decoupage.md), un son par moment, jamais deux en même temps.
# Méthode du skill sound-effects (Barty-Bart/motion-graphics, d'après Vox) : un mouvement ou une coupe prend son souffle
# 2 images avant, une montée finit sur le coup suivant, le dévoilement est le bruitage le plus fort.
# Usage : python son/bruitages.py <30|15|6> <sortie.wav>
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
ICI = Path(__file__).resolve().parent
VERSION = sys.argv[1] if len(sys.argv) > 1 else "30"
DUREE = {"30": 30.0, "15": 15.0, "6": 6.0}[VERSION]
IMG = 2 / 30  # deux images d'avance pour les souffles


def son(nom):
    """Charge un son de son/sfx/ en stéréo 48 kHz, crête ramenée à 1."""
    brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ICI / "sfx" / nom), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                          capture_output=True, check=True).stdout
    x = np.frombuffer(brut, dtype=np.float32).reshape(-1, 2).copy()
    return x / (np.abs(x).max() + 1e-9)


piste = np.zeros((int(DUREE * SR), 2), dtype=np.float32)


def poser(nom, instant, gain_db, fin=None, fondu=0.0):
    """Pose un son à l'instant donné (s), au niveau voulu (dB sous la pleine échelle).
    fin : coupe le son à cet instant de la vidéo (avec un fondu de sortie, en s)."""
    x = son(nom) * 10 ** (gain_db / 20)
    i = int(instant * SR)
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(piste) - i)
    if fin is not None:
        n = min(n, int(fin * SR) - i)
    x = x[:n].copy()
    if fondu:
        k = min(n, int(fondu * SR))
        x[n - k :] *= np.linspace(1, 0, k)[:, None]
    piste[i : i + n] += x


def finir_sur(nom, instant):
    """Instant de départ pour qu'un son (une montée) se termine exactement à « instant »."""
    return instant - len(son(nom)) / SR


def tic_tac(debut, fin_lent, fin, gain):
    """Le tic-tac : une seconde par tic jusqu'à « fin_lent », puis il accélère jusqu'à « fin ». Deux tics qui alternent."""
    s, pas, k = debut, 1.0, 0
    while s < fin:
        poser("fs528561.ogg" if k % 2 == 0 else "fs384187.ogg", s, gain + min(4, k * 0.3))
        if s >= fin_lent:
            pas = max(0.075, pas * 0.72)
        s += pas
        k += 1


AMBIANCE = "fs-426767-apartment-room-tone-wav.ogg"
MONTEE = "fs-685256-riser-sound-effect-short-wav.ogg"

if VERSION == "30":
    # Plan 1 : la pièce silencieuse dès la première image, puis la goutte touche sur la coupe vers la cuisine.
    poser(AMBIANCE, 0.0, -14, fin=7.6, fondu=0.5)
    poser("fs-447910-plop.ogg", 2.47, -6)
    # Plans 2-3 : le tic-tac, une seconde par tic, puis il accélère avec les aiguilles (5,0 → 6,63 s).
    tic_tac(2.62, 5.0, 6.6, -12)
    # La montée finit pile au départ de la musique (7,29 s) ; le souffle accompagne la plongée dans l'écran.
    poser(MONTEE, finir_sur(MONTEE, 7.29), -14)
    poser("fs-683096-woosh.ogg", 6.63 - IMG, -12)
    # Plan 6 : le dévoilement, sur le drop (13,00 s) : un impact doux, le bruitage le plus fort.
    poser("impact.ogg", 13.0, -7)
    # Plan 7 : le doigt sur « Valider et envoyer » (15,4 s), puis le « ding » de l'envoi (16,2 s).
    poser("click.ogg", 15.4, -14)
    poser("fs-571513-soft-notifications-bell-ding-d.ogg", 16.2, -10)
    # Coupes : téléphone → métiers (19,32 s), métiers → cuisine du soir (24,05 s).
    poser("fs-786514-swoosh-v2.ogg", 19.32 - IMG, -15)
    poser("fs-816262-broomstick-whoosh-3-quiet-okm1.ogg", 24.05 - IMG, -15)
    # Plan 10 : le bouton apparaît (28,11 s).
    poser("pop.ogg", 28.11, -16)
elif VERSION == "15":
    # Les plans du 30 s, raccourcis (montage.py) : goutte 0–2 s, cuisine 2–4 s, plongée 4–5 s, téléphone, fin.
    poser(AMBIANCE, 0.0, -14, fin=4.6, fondu=0.4)
    poser("fs-447910-plop.ogg", 1.97, -6)
    tic_tac(2.12, 3.2, 4.0, -12)
    poser(MONTEE, finir_sur(MONTEE, 4.3), -14)
    poser("fs-683096-woosh.ogg", 4.0 - IMG, -12)
    poser("impact.ogg", 6.0, -7)
    poser("click.ogg", 8.4, -14)
    poser("fs-571513-soft-notifications-bell-ding-d.ogg", 9.2, -10)
    poser("fs-786514-swoosh-v2.ogg", 11.67 - IMG, -15)
    poser("pop.ogg", 13.22, -16)
else:
    # 6 s : la goutte se forme, elle tombe sur la coupe vers le téléphone, juste avant le drop.
    poser(AMBIANCE, 0.0, -14, fin=1.4, fondu=0.3)
    poser("fs-447910-plop.ogg", 1.15, -6)
    poser("impact.ogg", 1.6, -7)

out = Path(sys.argv[2] if len(sys.argv) > 2 else f"out/bruitages_{VERSION}s.wav")
out.parent.mkdir(parents=True, exist_ok=True)
crete = np.abs(piste).max()
assert crete < 0.9, f"bruitages trop forts : crête {crete:.2f}"
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(3)
    w.setframerate(SR)
    pcm = np.clip(piste * (2**23 - 1), -(2**23), 2**23 - 1).astype("<i4")
    w.writeframes(pcm.reshape(-1, 1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
print(out, f"crête {20 * np.log10(crete):.1f} dBFS")
