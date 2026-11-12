"""Musiques originales des pubs Diktéo (composées ici, libres de droits : elles appartiennent à Diktéo).
Écrit un MIDI calé sur la grille de chaque pub, le joue avec FluidSynth + FluidR3_GM (licence MIT),
puis le masterise (EQ douce, compression, -14 LUFS). Le fichier sort là où son.py l'attend :
pubN/musique/mixkit-<PISTE>.mp3 (nom historique gardé pour ne pas toucher aux son.py).
python son/libre/composer.py [pub ...]   (défaut : toutes)
"""
import os
import subprocess
import sys

import mido
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
PUBS = os.path.abspath(os.path.join(ICI, "..", ".."))
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
PPQ = 480

# grille de chaque pub, relevée dans son son.py : tempo du fichier (BPM_P), instant du temps 0 de la pub dans le fichier
# (DEBUT_MUSIQUE), rapport tempo pub / tempo musique (2 = la musique en demi-tempo), durée en temps de pub, temps du carton.
#        piste  bpm     debut                     pub/mus  durée  carton  style         tonalité  graine  progression
CONF = {
    "pub4":  ("130", 123.0, 30.581 - 4 * 60 / 123, 1, 50, 41.5, "pop", 62, 4, "I V vi IV"),
    "pub8":  ("474", 121.0, .112 + 16 * 60 / 121, 1, 38, 27.4, "pop", 65, 8, "vi IV I V"),
    "pub10": ("134", 125.0, .204 + 16 * 60 / 125, 1, 34, 26.4, "pop", 67, 10, "I vi IV V"),
    "pub11": ("801", 143.55, .0697 + 8 * 60 / 143.55, 1, 36, 28, "pop", 64, 11, "I V vi IV"),
    "pub12": ("529", 85.0, .399 + 32 * 60 / 85, 1, 28, 22.7, "lofi", 65, 12, "ii7 V7 Imaj7 vi7"),
    "pub13": ("847", 83.0, .398 + 16 * 60 / 83, 1, 27, 21.5, "lofi", 63, 13, "Imaj7 vi7 ii7 V7"),
    "pub14": ("617", 129.2, .0464 + 8 * 60 / 129.2, 1, 31, 24.4, "pop", 69, 14, "vi IV I V"),
    "pub15": ("5", 80.75, .6037 + 8 * 60 / 80.75, 2, 41, 33, "lofi", 60, 15, "IVmaj7 iii7 vi7 Imaj7"),
    "pub16": ("963", 95.7, .0232 + 8 * 60 / 95.7, 1, 24, 19.5, "lofi", 62, 16, "Imaj7 IVmaj7 iii7 vi7"),
    "pub17": ("52", 76.0, .1625 + 8 * 60 / 76, 1, 20, 16.2, "acoustique", 67, 17, "I V vi IV"),
    "pub18": ("493", 140.0, .114 + 16 * 60 / 140, 1, 47, 38.7, "pop", 70, 18, "I iii IV V"),
    "pub19": ("91", 75.0, .467 + 8 * 60 / 75, 1, 25, 22.5, "acoustique", 64, 19, "I IV vi V"),
}

MAJ = [0, 2, 4, 5, 7, 9, 11]
DEG = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5}


def accord(sym, ton):
    """symbole de degré -> notes MIDI (fondamentale autour de ton-12)"""
    q = "maj7" if sym.endswith("maj7") else "7" if sym.endswith("7") else ""
    d = DEG[sym.replace("maj7", "").replace("7", "")]
    nb = 4 if q else 3
    notes = [ton + MAJ[(d + 2 * i) % 7] + 12 * ((d + 2 * i) // 7) for i in range(nb)]
    return notes, ton + MAJ[d]


class Piste:
    def __init__(self, ch, prog, vol=100, pan=64, reverb=40, chorus=0):
        self.ch, self.ev = ch, []
        self.ev += [(0, mido.Message("program_change", channel=ch, program=prog)),
                    (0, mido.Message("control_change", channel=ch, control=7, value=vol)),
                    (0, mido.Message("control_change", channel=ch, control=10, value=pan)),
                    (0, mido.Message("control_change", channel=ch, control=91, value=reverb)),
                    (0, mido.Message("control_change", channel=ch, control=93, value=chorus))]

    def note(self, temps, hauteur, duree, vel):
        a = int(round(temps * PPQ))
        b = a + max(1, int(round(duree * PPQ)))
        v = int(np.clip(vel, 1, 127))
        self.ev += [(a, mido.Message("note_on", channel=self.ch, note=int(hauteur), velocity=v)),
                    (b, mido.Message("note_off", channel=self.ch, note=int(hauteur), velocity=0))]


def composer(pub):
    piste, bpm, debut, rapport, duree, carton, style, ton, graine, prog = CONF[pub]
    rng = np.random.default_rng(graine)
    off = debut * bpm / 60  # le temps 0 de la pub, en temps du fichier
    L = duree / rapport + 2  # durée en temps de musique (avec la traîne)
    E = round(carton / rapport * 2) / 2  # la frappe finale, sur le carton (au demi-temps)
    E = float(np.floor(E)) if E - np.floor(E) < .75 else float(np.ceil(E))
    syms = prog.split()
    hum = lambda s=0.012: rng.normal(0, s)  # léger jeu humain (en temps)

    P = {}
    if style == "pop":
        P["kick"] = P["drum"] = Piste(9, 0, 110, 64, 10)
        P["keys"] = Piste(0, 0, 92, 50, 45)          # piano
        P["pad"] = Piste(1, 89, 70, 64, 70, 60)      # nappe chaude
        P["bass"] = Piste(2, 38, 100, 64, 5)         # basse synthé
        P["lead"] = Piste(3, 12, 96, 78, 50)         # marimba
        P["gloss"] = Piste(4, 9, 60, 90, 60)         # glockenspiel, doublure à l'octave
    elif style == "lofi":
        P["drum"] = Piste(9, 0, 105, 64, 15)
        P["keys"] = Piste(0, 4, 100, 54, 55, 30)     # piano électrique
        P["pad"] = Piste(1, 48, 58, 64, 75)          # cordes
        P["bass"] = Piste(2, 33, 105, 64, 5)         # basse aux doigts
        P["lead"] = Piste(3, 11, 92, 76, 60)         # vibraphone
    else:
        P["drum"] = Piste(9, 0, 100, 64, 25)
        P["keys"] = Piste(0, 25, 100, 52, 45, 20)    # guitare folk
        P["pad"] = Piste(1, 49, 55, 64, 80)          # cordes lentes
        P["bass"] = Piste(2, 32, 100, 64, 10)        # contrebasse
        P["lead"] = Piste(3, 9, 82, 80, 60)          # glockenspiel
        P["keys2"] = Piste(4, 24, 70, 84, 50)        # guitare nylon, contrechant

    D = P["drum"] if "drum" in P else P["kick"]
    swing = 0.06 if style == "lofi" else 0.0

    def sw(b):  # swing des doubles-croches paires
        return b + (swing if abs((b * 4) % 2 - 1) < 1e-6 else 0)

    # ——— motif mélodique (2 mesures), repris et varié : A A' B A'' ———
    rythmes = {"pop": [[0, .75, 1.5, 2.5, 3, 4.5, 5.5, 6], [0, .5, 1.5, 2, 3, 4, 4.75, 5.5, 6.5]],
               "lofi": [[0, 1.5, 2, 3.5, 4.5, 6], [.5, 1, 2.5, 4, 5, 5.5, 6.5]],
               "acoustique": [[0, 1, 1.5, 2.5, 4, 5, 6], [0, .5, 1.5, 3, 4, 4.5, 5.5, 6.5]]}[style]
    motif = rythmes[graine % 2]
    pas = rng.choice([-2, -1, 1, 2, 0, 1, -1], size=len(motif))

    def gamme(i):
        return ton + 12 + MAJ[i % 7] + 12 * (i // 7)

    nb_mes = int(np.ceil(L / 4))
    for m in range(nb_mes):
        b0 = 4 * m
        if b0 > E + 4:
            break
        sym = syms[m % len(syms)]
        notes, fond = accord(sym, ton - 12)
        fin = b0 >= E - 1e-6 or (b0 < E < b0 + 4)
        plein = m >= 1
        avant_fin = b0 + 4 <= E < b0 + 8

        for k in range(4):  # chaque temps de la mesure
            b = b0 + k
            if b >= E:
                break
            # ——— batterie ———
            if style == "pop":
                D.note(off + b, 36, .25, 118 if k in (0, 2) else 108)
                if plein:
                    if k in (1, 3):
                        D.note(off + b + hum(.004), 39, .25, 100)
                    D.note(off + b + .5 + hum(.006), 46, .2, 70)
                    for s in (0, .25, .75):
                        D.note(off + b + s + hum(.006), 42, .1, 62 + (12 if s == 0 else 0) + rng.integers(-6, 6))
                else:
                    D.note(off + b + .5, 42, .1, 55)
            elif style == "lofi":
                if k == 0 or (k == 2 and plein):
                    D.note(off + b, 36, .25, 112)
                if k == 1 and plein:
                    D.note(off + b + .75, 36, .2, 80)
                if k in (1, 3):
                    D.note(off + b + .02, 38 if plein else 37, .25, 92 if plein else 70)
                for s in (0, .5):
                    D.note(off + sw(b + s) + hum(.008), 42, .1, 58 + (10 if s == 0 else 0) + rng.integers(-8, 8))
            else:
                if k in (0, 2):
                    D.note(off + b, 36, .25, 96 if k == 0 else 80)
                if k in (1, 3):
                    D.note(off + b + .01, 37, .2, 78)
                    if plein:
                        D.note(off + b + .01, 54, .2, 60)
                for s in (0, .25, .5, .75):
                    D.note(off + b + s + hum(.006), 70, .1, 40 + (18 if s in (0, .5) else 0) + rng.integers(-5, 5))
            # ——— basse ———
            if style == "pop":
                for s, o in ((0, 0), (.5, 12)):
                    P["bass"].note(off + b + s, fond - 12 + o, .4, 104 if s == 0 else 88)
            elif style == "lofi":
                if k == 0:
                    P["bass"].note(off + b, fond - 12, 1.4, 108)
                elif k == 2:
                    P["bass"].note(off + b, fond - 12 + (7 if rng.random() < .5 else 0), .9, 96)
                elif k == 3:
                    P["bass"].note(off + sw(b + .5), fond - 12 + 12, .4, 80)
            else:
                if k in (0, 2):
                    P["bass"].note(off + b, fond - 12 + (0 if k == 0 else 7), .95, 100 if k == 0 else 88)
            # ——— accords ———
            if style == "pop":
                for s in (.5,) if k % 2 == 0 else (.5, .75):
                    for n in notes:
                        P["keys"].note(off + b + s + hum(.005), n + 12, .22, 78 + rng.integers(-6, 6))
            elif style == "lofi":
                if k in (0, 2) or (k == 3 and rng.random() < .4):
                    st = off + (b if k != 3 else sw(b + .5))
                    for i, n in enumerate(sorted(notes)):
                        P["keys"].note(st + i * .02 + hum(.006), n + 12, 1.8 if k == 0 else .9, 74 + rng.integers(-6, 6))
            else:
                ordre = [0, 2, 1, 3, 2, 1, 3, 2] if len(notes) > 3 else [0, 2, 1, 2, 0, 2, 1, 2]
                for s in range(2):
                    i = ordre[(k * 2 + s) % 8]
                    n = sorted(notes)[i % len(notes)] + 12
                    P["keys"].note(off + b + s * .5 + hum(.008), n, 1.4, 70 + (14 if s == 0 else 0) + rng.integers(-6, 6))
        # nappe : l'accord tenu toute la mesure
        if not fin:
            for n in notes:
                P["pad"].note(off + b0, n, min(4, E - b0) - .05, 64 if plein else 48)
        # ——— mélodie (dès la 2e mesure) ———
        if plein and not fin:
            phrase = (m - 1) // 2 % 4
            moitie = (m - 1) % 2
            deg0 = {0: 4, 1: 4, 2: 6, 3: 4}[phrase]
            pos = deg0
            for i, r in enumerate(motif):
                if not (moitie * 4 <= r < moitie * 4 + 4):
                    continue
                b = b0 + r - moitie * 4
                if b >= E - .5:
                    continue
                pos += int(pas[i]) + (1 if phrase == 2 and i == 0 else 0)
                h = gamme(pos)
                # temps forts : on se pose sur une note de l'accord
                if r % 1 == 0:
                    cands = [n + 24 + 12 * o for n in notes for o in (-1, 0, 1)]
                    h = min(cands, key=lambda c: abs(c - h))
                h = int(np.clip(h, ton + 12, ton + 26))
                du = min(.45 if style == "pop" else .9, E - b - .05)
                v = (96 if r % 2 == 0 else 84) + rng.integers(-6, 6)
                P["lead"].note(off + sw(b) + hum(.006), h, du, v)
                if "gloss" in P and r % 1 == 0:
                    P["gloss"].note(off + b, h + 12, .3, 50)
                if "keys2" in P and r % 2 == 0:
                    P["keys2"].note(off + b + .02, h - 12, .9, 62)
        # roulement de caisse claire avant la frappe finale
        if avant_fin and E - b0 >= 2:
            r0 = max(b0, E - 2)
            n = int((E - r0) * 4)
            for i in range(n):
                D.note(off + r0 + i / 4, 38 if style != "acoustique" else 37, .1, 50 + int(70 * i / max(1, n - 1)))
            if style != "acoustique":
                for i in range(n // 2):
                    D.note(off + r0 + i / 2, 36, .1, 80 + 4 * i)

    # ——— la frappe finale sur le carton : cymbale, accord de tonique tenu, note finale de la mélodie ———
    notes, fond = accord(("Imaj7" if style == "lofi" else "I"), ton - 12)
    tenue = L - E + 1
    D.note(off + E, 49, 2.5, 108)
    D.note(off + E, 36, .3, 120)
    if style != "acoustique":
        D.note(off + E, 57, 2.5, 70)
    P["bass"].note(off + E, fond - 12, tenue, 110)
    for n in notes + [notes[0] + 14]:
        P["pad"].note(off + E, n, tenue, 82)
        P["keys"].note(off + E + .015 * (n % 3), n + 12, tenue, 88)
    P["lead"].note(off + E, ton + 24, tenue, 100)
    if "gloss" in P:
        P["gloss"].note(off + E, ton + 36, 2, 70)
    if "keys2" in P:
        P["keys2"].note(off + E, ton + 12, tenue, 70)

    # ——— écriture MIDI ———
    mid = mido.MidiFile(ticks_per_beat=PPQ)
    t0 = mido.MidiTrack()
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    mid.tracks.append(t0)
    for p in {id(p): p for p in P.values()}.values():
        tr = mido.MidiTrack()
        ev = sorted(p.ev, key=lambda e: (e[0], 0 if e[1].type == "note_off" else 1))
        last = 0
        for tk, msg in ev:
            tk = max(0, tk)
            tr.append(msg.copy(time=tk - last))
            last = tk
        mid.tracks.append(tr)
    dos = os.path.join(PUBS, pub, "musique")
    os.makedirs(dos, exist_ok=True)
    tmp = os.path.join(dos, "composition")
    mid.save(tmp + ".mid")
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.45", "-r", "48000", "-R", "1", "-C", "1", "-F", tmp + ".wav", SF2, tmp + ".mid"],
                   check=True, capture_output=True)
    fin_s = debut + L * 60 / bpm + 3
    sortie = os.path.join(dos, f"mixkit-{piste}.mp3")
    # mastering : coupe des infra-graves, un peu d'air, compression de bus, -14 LUFS, plafond -1 dBTP
    af = ("highpass=f=30,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=9000:t=h:w=0.7:g=2,"
          "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=180:makeup=2,"
          f"apad,atrim=0:{fin_s:.3f},loudnorm=I=-14:TP=-1:LRA=9")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp + ".wav", "-af", af, "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "320k", sortie], check=True)
    os.remove(tmp + ".wav")
    print(f"{pub}: {style}, {bpm} BPM, frappe finale au temps {E} → {os.path.relpath(sortie, PUBS)}")


for p in sys.argv[1:] or CONF:
    composer(p)
