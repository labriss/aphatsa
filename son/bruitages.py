# Les bruitages de la pub, fabriqués à partir de sons purs (aucun fichier téléchargé, aucun droit à gérer),
# puis posés sur une piste de 30 s aux instants du découpage (decoupage.md).
# Usage : python son/bruitages.py <sortie.wav>
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUREE = 30.0
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(d * SR)) / SR


def env(t, attaque, chute):
    """Enveloppe : montée linéaire puis décroissance exponentielle (constante de temps « chute »)."""
    a = np.clip(t / max(attaque, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attaque, 0) / chute)


def passe_bas(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def passe_bande(x, f0, q):
    """Filtre résonant simple (biquad passe-bande), f0 peut varier dans le temps."""
    f0 = np.broadcast_to(f0, x.shape)
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        w = 2 * np.pi * f0[i] / SR
        alpha = np.sin(w) / (2 * q)
        b0, a0, a1, a2 = alpha, 1 + alpha, -2 * np.cos(w), 1 - alpha
        v = (b0 * x[i] - b0 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x[i], y1, v
        y[i] = v
    return y


# ——— Les sons ———

def ambiance(d):
    """Le silence d'une pièce : un souffle d'air grave, à peine audible. Sans lui, le début semble muet."""
    t = t_(d)
    x = passe_bas(passe_bas(rng.standard_normal(len(t)), 700), 700)
    x = x / np.abs(x).max() + 0.25 * np.sin(2 * np.pi * 50 * t)
    return x / np.abs(x).max() * np.clip(t / 0.4, 0, 1) * np.clip((d - t) / 0.4, 0, 1)


def plic():
    """La goutte qui touche : une bulle dont la hauteur remonte très vite, avec un petit claquement."""
    t = t_(0.35)
    f = 700 + 1300 * (1 - np.exp(-t / 0.012))
    phase = 2 * np.pi * np.cumsum(f) / SR
    bulle = np.sin(phase) * env(t, 0.001, 0.045)
    claque = passe_bande(rng.standard_normal(len(t)) * env(t, 0.0005, 0.004), 3200, 2.0)
    return 0.8 * bulle + 0.5 * claque


def tic(aigu=True):
    """Un tic d'horloge : un clic sec et une petite résonance de boîtier."""
    t = t_(0.08)
    bruit = rng.standard_normal(len(t)) * env(t, 0.0003, 0.002)
    corps = passe_bande(bruit, 2600 if aigu else 1900, 8.0)
    return 0.9 * corps / (np.abs(corps).max() + 1e-9)


def bourdon(d):
    """Une nappe grave et froide, qui monte doucement : la soirée qui s'étire."""
    t = t_(d)
    x = sum(a * np.sin(2 * np.pi * f * t + p) for a, f, p in ((1.0, 55.0, 0), (0.6, 55.4, 1.0), (0.35, 82.5, 2.0), (0.15, 110.3, 0.5)))
    x = passe_bas(x, 400)
    montee = np.clip(t / (d * 0.85), 0, 1) ** 1.5
    fin = np.clip((d - t) / 0.25, 0, 1)
    return x / np.abs(x).max() * montee * fin


def souffle(d):
    """La plongée dans l'écran : un souffle dont le filtre s'ouvre, qui gonfle jusqu'au départ de la musique."""
    t = t_(d)
    n = rng.standard_normal(len(t))
    f0 = 250 * (14 ** (t / d))
    x = passe_bande(n, f0, 1.2)
    forme = (t / d) ** 2.2 * np.clip((d - t) / 0.06, 0, 1)
    return x / np.abs(x).max() * forme


def tape():
    """Le doigt sur « Valider et envoyer » : un tapotement doux d'interface."""
    t = t_(0.09)
    return 0.7 * np.sin(2 * np.pi * 1150 * t) * env(t, 0.001, 0.012) + 0.3 * passe_bande(rng.standard_normal(len(t)) * env(t, 0.0003, 0.003), 4000, 3.0)


def ding():
    """Devis envoyé : deux notes de clochette (mi puis si), claires, qui s'éteignent lentement."""
    out = np.zeros(int(1.6 * SR))
    for debut, f in ((0.0, 1318.5), (0.09, 1975.5)):
        t = t_(1.6 - debut)
        note = sum(a * np.sin(2 * np.pi * f * r * t) * env(t, 0.002, 0.5 / r ** 0.7) for a, r in ((1.0, 1.0), (0.35, 2.76), (0.12, 5.4)))
        out[int(debut * SR) :] += note
    return out / np.abs(out).max()


# ——— La piste ———

piste = np.zeros((int(DUREE * SR), 2))


def poser(x, instant, gain_db, pan=0.0):
    """Pose un son à l'instant donné (en s), au niveau voulu (dB sous la pleine échelle), panoramique -1..1."""
    g = 10 ** (gain_db / 20)
    i = int(instant * SR)
    x = x[: max(0, len(piste) - i)]
    piste[i : i + len(x), 0] += x * g * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    piste[i : i + len(x), 1] += x * g * np.sqrt((1 + pan) / 2) * np.sqrt(2)


# Plan 1 : l'ambiance de la pièce dès la première image, puis la goutte touche au moment de la coupe vers la cuisine.
poser(ambiance(7.6), 0.0, -24)
poser(plic(), 2.47, -6)
# Plans 2-3 : le bourdon monte sous la cuisine, jusqu'au départ de la musique.
poser(bourdon(4.85), 2.45, -11)
# Le tic-tac : une seconde par tic, puis il accélère avec les aiguilles (5,0 → 6,63 s), et s'arrête dans la plongée.
instants, s = [], 2.62
while s < 5.0:
    instants.append(s)
    s += 1.0
pas = 1.0
while s < 6.75:
    instants.append(s)
    pas = max(0.075, pas * 0.72)
    s += pas
for k, s in enumerate(instants):
    poser(tic(k % 2 == 0), s, -9 + min(4, k * 0.3), 0.15 if k % 2 == 0 else -0.15)
# Plan 4 : la plongée dans l'écran, le souffle culmine quand la musique démarre (7,29 s).
poser(souffle(0.75), 6.56, -9)
# Plan 6-7 : le doigt sur « Valider et envoyer » (15,4 s), puis le « ding » de l'envoi (16,2 s), sous la musique.
poser(tape(), 15.4, -18)
poser(ding(), 16.2, -15)

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/bruitages_30s.wav")
out.parent.mkdir(parents=True, exist_ok=True)
crete = np.abs(piste).max()
assert crete < 0.9, f"bruitages trop forts : crête {crete:.2f}"
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(3)
    w.setframerate(SR)
    pcm = np.clip(piste * (2**23 - 1), -(2**23), 2**23 - 1).astype(np.int32)
    w.writeframes(b"".join(int(v).to_bytes(3, "little", signed=True) for v in pcm.reshape(-1)))
print(out, f"crête {20 * np.log10(crete):.1f} dBFS")
