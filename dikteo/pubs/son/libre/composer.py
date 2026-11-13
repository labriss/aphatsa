"""Musiques originales des pubs Diktéo, style chill / lo-fi : « ouf, avec Diktéo on souffle ».
Tout est synthétisé ici (numpy), donc libre de droits : Rhodes en FM, nappe de scies désaccordées filtrée, sub-basse,
batterie feutrée (grosse caisse ronde, caisse claire balai, charleston discret), grain de vinyle, saturation de bande,
réverbération à convolution, compression « sidechain » douce. Dramaturgie : groove posé et détendu ; juste avant le carton,
la musique retient son souffle (accord suspendu, filtre qui se ferme, batterie qui s'arrête) ; sur le carton, l'accord
de tonique s'ouvre (maj9) avec un long soupir de soulagement.
Le fichier sort là où son.py l'attend : pubN/musique/mixkit-<PISTE>.mp3 (nom historique gardé).
python son/libre/composer.py [pub ...]   (défaut : toutes)
"""
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ICI = os.path.dirname(os.path.abspath(__file__))
PUBS = os.path.abspath(os.path.join(ICI, "..", ".."))
SR = 48000

# grille de chaque pub, relevée dans son son.py : tempo du fichier (BPM_P), instant du temps 0 de la pub dans le fichier
# (DEBUT_MUSIQUE), rapport tempo pub / tempo musique, durée et temps du carton (en temps de pub), tonalité, graine.
CONF = {
    "pub4":  ("130", 123.0, 30.581 - 4 * 60 / 123, 1, 50, 41.5, 62, 4),
    "pub8":  ("474", 121.0, .112 + 16 * 60 / 121, 1, 38, 27.4, 65, 8),
    "pub10": ("134", 125.0, .204 + 16 * 60 / 125, 1, 34, 26.4, 67, 10),
    "pub11": ("801", 143.55, .0697 + 8 * 60 / 143.55, 1, 36, 28, 64, 11),
    "pub12": ("529", 85.0, .399 + 32 * 60 / 85, 1, 28, 22.7, 65, 12),
    "pub13": ("847", 83.0, .398 + 16 * 60 / 83, 1, 27, 21.5, 63, 13),
    "pub14": ("617", 129.2, .0464 + 8 * 60 / 129.2, 1, 31, 24.4, 69, 14),
    "pub15": ("5", 80.75, .6037 + 8 * 60 / 80.75, 2, 41, 33, 60, 15),
    "pub16": ("963", 95.7, .0232 + 8 * 60 / 95.7, 1, 24, 19.5, 62, 16),
    "pub17": ("52", 76.0, .1625 + 8 * 60 / 76, 1, 20, 16.2, 67, 17),
    "pub18": ("493", 140.0, .114 + 16 * 60 / 140, 1, 47, 38.7, 70, 18),
    "pub19": ("91", 75.0, .467 + 8 * 60 / 75, 1, 25, 22.5, 64, 19),
}

# progressions jazz-pop détendues (degrés de la gamme majeure, qualité) ; la dernière mesure avant le carton est
# toujours un V9sus4 (la retenue), le carton un Imaj9 (le soulagement).
PROGS = [[("IV", "maj9"), ("iii", "m7"), ("ii", "m9"), ("I", "maj9")],
         [("I", "maj9"), ("vi", "m9"), ("ii", "m9"), ("IV", "maj9")],
         [("ii", "m9"), ("iii", "m7"), ("IV", "maj9"), ("I", "maj9")],
         [("vi", "m9"), ("IV", "maj9"), ("I", "maj9"), ("iii", "m7")]]
MAJ = [0, 2, 4, 5, 7, 9, 11]
DEG = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5}
INTER = {"maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14], "m7": [0, 3, 7, 10], "9sus4": [0, 5, 7, 10, 14]}
hz = lambda n: 440 * 2 ** ((n - 69) / 12)


def lp(x, f, o=2):
    return sosfilt(butter(o, min(f, SR / 2 - 200), "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x, axis=0)


class Mix:
    def __init__(self, duree, rng):
        self.n = int(duree * SR)
        self.rng = rng
        self.bus = {k: np.zeros((self.n, 2)) for k in ("keys", "pad", "bass", "drums", "lead", "fx")}

    def add(self, bus, t, x, g=1.0, pan=0.0):
        if x.ndim == 1:
            x = np.stack([x * np.sqrt((1 - pan) / 2), x * np.sqrt((1 + pan) / 2)], 1)
        a = int(round(t * SR))
        if a < 0:
            x, a = x[-a:], 0
        k = min(len(x), self.n - a)
        if k > 0:
            self.bus[bus][a:a + k] += x[:k] * g


def env_adsr(d, a, rel, total=None, decay=None):
    total = total or d + rel
    t = np.arange(int(total * SR)) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if decay:
        e = e * np.exp(-t / decay)
    e = e * np.clip(1 - (t - d) / rel, 0, 1)
    return e, t


def rhodes(n, d, vel, rng):
    """piano électrique FM (rapport 1:1 + dent à 14:1), brillance selon la vélocité, trémolo stéréo"""
    f = hz(n)
    dec = 2.6 * (440 / f) ** .35
    e, t = env_adsr(d, .004, .35, d + .6, dec)
    i1 = (0.9 + 1.6 * vel) * np.exp(-t / .5)
    i2 = 0.5 * vel * np.exp(-t / .03)
    m = np.sin(2 * np.pi * f * t) * i1 + np.sin(2 * np.pi * f * 14 * t) * i2
    x = np.sin(2 * np.pi * f * t + m) * e * (0.25 + 0.75 * vel)
    trem = 0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * t + rng.uniform(0, 6))
    return np.stack([x * (0.8 + 0.2 * trem), x * (1.0 - 0.2 * trem)], 1)


def nappe(n, d, rng, coupe=1400):
    """3 scies désaccordées (additives, sans repliement), filtrées, attaque et relâche lentes"""
    f = hz(n)
    a, rel = .9, 1.6
    e, t = env_adsr(d, a, rel)
    out = np.zeros((len(t), 2))
    for j, det in enumerate((-.09, 0, .1)):
        ph = rng.uniform(0, 6)
        s = sum(np.sin(2 * np.pi * f * 2 ** (det / 12) * k * t + ph * k) / k for k in range(1, int(4000 / f) + 1))
        out[:, 0 if j == 0 else 1 if j == 2 else 0] += s * (1 if j != 1 else .5)
        if j == 1:
            out[:, 1] += s * .5
    return lp(out * e[:, None], coupe, 2) * .25


def sub(n, d):
    f = hz(n)
    e, t = env_adsr(d, .012, .12)
    x = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t)
    return lp(np.tanh(1.3 * x) * e, 600)


def kick(v):
    t = np.arange(int(.45 * SR)) / SR
    f = 48 + 70 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .2)
    x += 0.15 * lp(np.random.default_rng(1).standard_normal(len(t)), 3000) * np.exp(-t / .006)
    return np.tanh(1.5 * x) * v


def balai(v, rng):
    t = np.arange(int(.3 * SR)) / SR
    nz = bp(rng.standard_normal(len(t)), 900, 5500) * np.exp(-t / .09)
    corps = np.sin(2 * np.pi * 185 * t) * np.exp(-t / .05) * .5
    return lp(nz + corps, 6500) * v


def rim(v):
    t = np.arange(int(.12 * SR)) / SR
    return (bp(np.random.default_rng(3).standard_normal(len(t)), 1500, 4000) * np.exp(-t / .012) + np.sin(2 * np.pi * 820 * t) * np.exp(-t / .02)) * v


def charley(v, rng, ouvert=False):
    t = np.arange(int((.25 if ouvert else .06) * SR)) / SR
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / (.08 if ouvert else .018)) * v


def soupir(d):
    """le « ouf » : une longue expiration (bruit filtré par des formants de souffle), douce"""
    rng = np.random.default_rng(99)
    t = np.arange(int(d * SR)) / SR
    nz = rng.standard_normal(len(t))
    x = bp(nz, 500, 1800) * .6 + bp(nz, 2000, 4200) * .35 + lp(nz, 400) * .2
    e = np.minimum(1, t / .25) * np.exp(-np.maximum(0, t - .3) / (d / 3))
    return lp(x * e, 5000)


def reverb(x, d=2.8, pre=.025, couleur=5500, graine=5):
    rng = np.random.default_rng(graine)
    t = np.arange(int(d * SR)) / SR
    ir = np.zeros((len(t) + int(pre * SR), 2))
    for c in range(2):
        ir[int(pre * SR):, c] = lp(rng.standard_normal(len(t)), couleur) * np.exp(-t / (d / 6.9))
    ir /= np.sqrt((ir ** 2).sum(0))
    return np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)


def composer(pub):
    piste, bpm, debut, rapport, duree, carton, ton, graine = CONF[pub]
    # la musique de la pub 4 (tonalité, progression, tirages) sert de référence pour toutes (choix de l'utilisateur, 12 nov.)
    modele = os.environ.get("MUSIQUE_COMME", "pub4")
    if modele in CONF:
        ton, graine = CONF[modele][6], CONF[modele][7]
    rng = np.random.default_rng(graine)
    tempo_pub = bpm * rapport  # tempo ressenti (pub15 : 161,5 → on joue sur 80,75 comme le fichier)
    demi = bpm > 108  # au-dessus de 108 BPM : groove en demi-tempo, pulsation = 2 temps
    P = 2 if demi else 1
    L = duree / rapport + 1  # temps de musique utiles
    E = carton / rapport  # le carton, en temps de musique (fichier)
    E = round(E * 2) / 2 if not demi else round(E)
    tb = 60 / bpm
    fin_s = debut + (L + 8) * tb + 3
    M = Mix(fin_s, rng)
    T = lambda b: debut + b * tb  # temps de musique -> secondes dans le fichier

    prog = PROGS[graine % len(PROGS)]
    mesure = 4 * P  # une mesure = 4 pulsations
    racine = ton - 12  # accords autour de la 3e octave
    voix_prec = None

    def voicing(deg, q):
        r = racine + MAJ[DEG[deg]] if deg in DEG else racine
        notes = [r + i for i in INTER[q]]
        # conduite des voix : on rapproche chaque voicing du précédent (renversements à l'octave)
        nonlocal voix_prec
        if voix_prec is not None:
            c = np.mean(voix_prec)
            notes = [n - 12 if n - c > 7 else n + 12 if c - n > 8 else n for n in notes]
        notes = sorted(notes)
        voix_prec = notes
        return r, notes

    nb = int(np.ceil(E / mesure))
    mesures = []
    for m in range(nb):
        b0 = m * mesure
        b1 = min(E, b0 + mesure)
        derniere = b1 >= E - 1e-6
        if derniere and b1 - b0 >= P:  # la retenue : V9sus4 sur la dernière mesure
            mesures.append((b0, b1, "V", "9sus4"))
        else:
            d, q = prog[m % len(prog)]
            mesures.append((b0, b1, d, q))

    swing = 0.16 * P  # swing des croches (en temps)
    gamme_penta = [0, 2, 4, 7, 9]

    for idx, (b0, b1, deg, q) in enumerate(mesures):
        r, notes = voicing(deg, q)
        retenue = q == "9sus4"
        # ——— Rhodes : accord plaqué légèrement égrené, + une relance sur le « et » du 2e temps (ou de la 3e pulsation) ———
        for k, (b, v, du) in enumerate([(b0, .72, b1 - b0), (b0 + 2.5 * P, .5, (1.5 * P))] if b1 - b0 > 2.5 * P else [(b0, .72, b1 - b0)]):
            if retenue and k:
                continue
            for i, n in enumerate(notes):
                M.add("keys", T(b + (swing if b % P else 0)) + i * .012 + rng.normal(0, .004),
                      rhodes(n + 12, du * tb, v - .04 * i + rng.uniform(-.04, .04), rng), .32)
        # ——— nappe : fondamentale + tierce + septième, tenue ———
        for n in [notes[0] + 12, notes[1] + 12, notes[-2] + 12]:
            M.add("pad", T(b0), nappe(n, (b1 - b0) * tb, rng, 900 if retenue else 1500), .5)
        # ——— sub-basse : fondamentale, petite relance ———
        M.add("bass", T(b0), sub(r - 12, (min(b1 - b0, 2.5 * P) - .1) * tb), .9)
        if b1 - b0 > 3 * P and not retenue:
            M.add("bass", T(b0 + 3 * P + swing), sub(r - 12 + (7 if rng.random() < .5 else 12), (P - .1) * tb), .6)
        # ——— batterie feutrée (pas pendant la retenue : on retient son souffle) ———
        if not retenue:
            for p in range(int((b1 - b0) / P)):
                b = b0 + p * P
                pos = p % 4
                if pos == 0 or (pos == 2 and rng.random() < .3):
                    M.add("drums", T(b), kick(.9), 1)
                if pos == 2:
                    M.add("drums", T(b + .5 * P + swing * .5), kick(.6), 1)
                if pos in (1, 3):
                    M.add("drums", T(b) + .012, balai(.55, rng), 1, .1)
                    M.add("drums", T(b) + .012, rim(.12), 1, .1)
                for s in (0, .5):
                    M.add("drums", T(b + s * P + (swing if s else 0)) + rng.normal(0, .004),
                          charley(.16 if s == 0 else .1, rng), 1, .35)
        else:
            # un charleston ouvert qui s'éteint + un Rhodes inversé qui aspire vers le carton
            M.add("drums", T(b0), charley(.12, rng, True), 1, .35)
            for n in (notes[0] + 24, notes[2] + 24):
                rv = rhodes(n, (b1 - b0) * tb, .6, rng)[::-1]
                M.add("fx", T(b1) - len(rv) / SR, rv * np.linspace(0, 1, len(rv))[:, None] ** 2, .35)
        # ——— mélodie : peu de notes, beaucoup d'espace (phrases de 2 mesures, la 2e répond à la 1re) ———
        if idx >= 1 and not retenue:
            rythme = [0, 1.5, 2.5] if idx % 2 else [.5, 2, 3]
            for j, rb in enumerate(rythme):
                b = b0 + rb * P
                if b >= b1 - .5 * P:
                    continue
                cible = notes[(j + idx) % len(notes)] + 24
                penta = [ton + 12 + i + 12 * o for i in gamme_penta for o in (0, 1)]
                h = min(penta, key=lambda c: abs(c - cible))
                M.add("lead", T(b + (swing if (rb * 2) % 2 else 0)), rhodes(h, 1.4 * P * tb, .55, rng), .34, .25)

    # ——— le carton : Imaj9 qui s'ouvre, sub, glockenspiel doux, et le soupir de soulagement ———
    r, notes = voicing("I", "maj9")
    tenue = (L - E + 6) * tb
    for i, n in enumerate(notes):
        M.add("keys", T(E) + i * .03, rhodes(n + 12, tenue, .8, rng), .34)
    for n in (notes[0] + 12, notes[1] + 12, notes[3] + 12, notes[4] + 12):
        M.add("pad", T(E) - .15, nappe(n, tenue, rng, 2600), .55)
    M.add("bass", T(E), sub(r - 12, tenue * .8), 1.0)
    M.add("drums", T(E), kick(.8), 1)
    M.add("lead", T(E) + .06, rhodes(ton + 24 + 4, tenue, .6, rng), .3, -.2)
    M.add("fx", T(E) - .05, soupir(2.8), .22)

    # ——— bus : sidechain doux de la grosse caisse sur nappe et Rhodes, réverbérations, texture vinyle ———
    kick_env = np.abs(M.bus["drums"][:, 0])
    kick_env = lp(kick_env, 8)
    kick_env = kick_env / max(1e-6, kick_env.max())
    duck = (1 - .35 * kick_env)[:, None]
    keys = M.bus["keys"] * duck
    pad = M.bus["pad"] * duck
    lead = M.bus["lead"]
    wet = reverb(keys * .5 + pad * .4 + lead * .9 + M.bus["fx"] * .6, 3.2, .03, 5000)
    drums = M.bus["drums"]
    mix = keys + pad + lead * .9 + M.bus["bass"] + drums * .85 + M.bus["fx"] + wet * .55 + reverb(drums, .8, .01, 7000, 8) * .12
    # vinyle : craquements épars + souffle de bande très bas
    n = len(mix)
    craq = np.zeros(n)
    pos = rng.integers(0, n, size=int(n / SR * 9))
    craq[pos] = rng.uniform(-1, 1, len(pos)) * rng.uniform(.2, 1, len(pos)) ** 3
    craq = bp(craq, 1200, 7000) * 1.4
    souffle = lp(hp(rng.standard_normal(n), 2000), 9000) * .004
    mix += np.stack([craq + souffle, np.roll(craq, 37) + souffle], 1) * .9
    # couleur « bande » : léger filtre passe-bas, saturation douce, coupe des infra-graves
    mix = hp(lp(mix, 11500), 28)
    mix = np.tanh(mix / max(1e-6, np.abs(mix).max()) * 1.6) / np.tanh(1.6)
    # silence avant le temps 0 et petite montée en entrée
    a = int(debut * SR)
    mix[: max(0, a - int(.02 * SR))] = 0

    dos = os.path.join(PUBS, pub, "musique")
    os.makedirs(dos, exist_ok=True)
    wav = os.path.join(dos, "composition.wav")
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32000).astype(np.int16).tobytes())
    sortie = os.path.join(dos, f"mixkit-{piste}.mp3")
    af = "acompressor=threshold=-20dB:ratio=2:attack=25:release=250:makeup=1.5,loudnorm=I=-15:TP=-1.5:LRA=8"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", af, "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "320k", sortie], check=True)
    os.remove(wav)
    print(f"{pub}: {bpm} BPM{' (demi-tempo)' if demi else ''}, carton au temps {E} → {os.path.relpath(sortie, PUBS)}")


for p in sys.argv[1:] or CONF:
    composer(p)
