"""Partition originale de « Le Soir du plombier » : un piano droit de cinéma qui joue la « cue sheet » (VSCO 2 CE, CC0).
Misterioso (Plombier ? 21 heures) → Agitato (la pile monte, vacille, s'écroule : trille, glissando, cluster) → plink… plonk →
SILENCE (carton) → Tenderly (la voix : une note par ligne du télégramme, note de grâce sur le sourcil) →
accord joyeux (devis envoyé) → le thème, chaud (il rentre dîner) → accord final tenu.
Toutes les durées viennent de ../timeline.json. Sortie : music/score.wav"""
import sys, os, json
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB', os.path.expanduser('~/lemo-opuscar'))
sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR

S.seed(1926)
TL = json.load(open(os.path.join(HERE, '../timeline.json'), encoding='utf-8'))
SEC, HIT, DUR = TL['SEC'], TL['HIT'], TL['DUR']
def at(s, b=0.0): return SEC[s]['t0'] + b * SEC[s]['beat']
def bt(s): return SEC[s]['beat']
EV = []
P = 'upright'
def n(t, p, d, v=.6, pan=0.): EV.append((t, P, p, d, v, pan))
def chord(t, ps, d, v=.6, pan=0., roll=0.):
    for i, p in enumerate(ps): n(t + i * roll, p, d, v * (1 - .04 * i), pan)
NOMS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def m2n(m): return NOMS[m % 12] + str(m // 12 - 1)
def midi(p): return int(round(S.midi(p)))
BLANCHES = [0, 2, 4, 5, 7, 9, 11]
def gliss(t, p0, p1, d, v0=.5, v1=.75):
    a, b = midi(p0), midi(p1); st = 1 if b > a else -1
    ns = [m for m in range(a, b + st, st) if m % 12 in BLANCHES]
    for i, m in enumerate(ns):
        u = i / max(1, len(ns) - 1); n(t + u * d, m2n(m), .22, v0 + (v1 - v0) * u, (u - .5) * .4)
def trille(t, a, b, d, rate=16, v0=.35, v1=.7):
    k, tt = 0, t
    while tt < t + d - 1e-6:
        u = (tt - t) / d; n(tt, a if k % 2 == 0 else b, 1 / rate * 1.3, v0 + (v1 - v0) * u, .25); tt += 1 / rate; k += 1

# ---------- CARD1 · Misterioso : la nuit tombe, une basse qui rampe ----------
B = bt('CARD1')
chord(at('CARD1'), ['A1', 'E2', 'A2'], B * 4, .55, -.3)
for i, p in enumerate(['A2', 'G#2', 'G2', 'F#2']): n(at('CARD1', i), p, B * .9, .45, -.2)
n(at('CARD1', .5), 'E5', B * 1.5, .3, .3); n(at('CARD1', 2.5), 'C5', B * 1.5, .28, .3)
chord(at('CARD1', 4), ['E1', 'E2', 'B2'], B * 1.5, .45, -.3); n(at('CARD1', 4.5), 'B4', B * 1, .26, .3)  # carton allongé : la basse tient jusqu'à la pile

# ---------- GAG · Agitato (ré mineur) : main gauche « stride », la pile monte ----------
B = bt('GAG')
basses = ['D2', 'A1', 'D2', 'A1', 'Bb1', 'F2', 'A1', 'E2']
accords = [['F3', 'A3', 'D4'], ['E3', 'G3', 'C#4'], ['F3', 'A3', 'D4'], ['E3', 'G3', 'C#4']]
for i in range(7):
    n(at('GAG', i), basses[i % 8], B * .45, .5, -.25); chord(at('GAG', i + .5), accords[i % 4], B * .35, .38, -.1)
# un motif nerveux qui monte d'un cran à chaque feuille posée
for k, (b0, base) in enumerate([(2, 'D5'), (4, 'F5'), (6, 'A5')]):
    m = midi(base)
    for j, dm in enumerate([0, 2, 3]): n(at('GAG', b0 - .5 + j * .17), m2n(m + dm), .2, .55 + .05 * k, .3)
# la pile vacille : trille qui enfle
trille(at('GAG', 7), 'E5', 'F5', B * 1.45, 16, .35, .75)
# l'écroulement : glissando qui descend, puis un « cluster » d'avant-bras dans le grave
gliss(at('GAG', 8.5), 'C7', 'C3', B * .55, .8, .6)
chord(at('GAG', 9.05), ['C2', 'D2', 'E2', 'F2', 'G2', 'A2'], B * 1.6, .9, -.2)
# il ressort : plink… plonk
n(at('GAG', 10.4), 'G6', .5, .45, .4); n(at('GAG', 11), 'C2', 1.2, .5, -.3)

# ---------- CARD2 : SILENCE (seul le projecteur) ----------

# ---------- VOIX · Tenderly (do majeur) : la première note après le silence, puis une note par ligne ----------
B = bt('VOIX')
n(HIT['telephone'], 'E5', B * 1.5, .32, .2)
chord(at('VOIX', 1.5), ['C3', 'G3'], B * 1.2, .3, -.2)
for b0, p, lh in [(2.5, 'G4', ['C3', 'G3', 'E4']), (3.5, 'A4', ['F2', 'C3', 'A3']), (4.5, 'C5', ['G2', 'D3', 'B3']), (5.5, 'E5', ['C3', 'G3', 'E4'])]:
    n(at('VOIX', b0), p, B * .95, .5, .25); chord(at('VOIX', b0), lh, B * .9, .3, -.2, roll=.03)
n(HIT['sourcil'] - .05, 'D#6', .06, .35, .4); n(HIT['sourcil'], 'E6', B * .8, .42, .4)       # le clin d'œil

# ---------- CARD3 : l'accord joyeux, une petite course ----------
B = bt('CARD3')
chord(at('CARD3'), ['C2', 'C3', 'G3'], B * 2.5, .75, -.3); chord(at('CARD3'), ['E4', 'G4', 'C5', 'E5'], B * 2, .7, .2, roll=.015)
for i, p in enumerate(['G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'G5']): n(at('CARD3', 2.5 + i * .14), p, .25, .45 + .03 * i, .25)
chord(at('CARD3', 3.6), ['C3', 'G3', 'E4', 'C5'], B * 1.4, .55, 0, roll=.02)

# ---------- MAISON : le thème, chaud ----------
B = bt('MAISON')
theme = [(0, 'E5', 1), (1, 'D5', .5), (1.5, 'C5', .5), (2, 'G4', 1), (3, 'A4', .5), (3.5, 'C5', .5), (4, 'E5', 1.2), (5.2, 'D5', .8)]
for b0, p, d in theme: n(at('MAISON', b0), p, B * d * .95, .5, .25)
for b0, lh in [(0, ['C3', 'G3', 'E4']), (2, ['F2', 'C3', 'A3']), (4, ['G2', 'D3', 'F3', 'B3'])]: chord(at('MAISON', b0), lh, B * 1.9, .33, -.2, roll=.04)

# ---------- FIN : accord tenu, puis une dernière note douce ----------
B = bt('FIN')
chord(at('FIN'), ['C2', 'C3', 'G3'], B * 5, .7, -.3); chord(at('FIN'), ['E4', 'G4', 'C5', 'E5', 'G5'], B * 4.5, .62, .2, roll=.03)
n(at('FIN', 4.5), 'C6', B * 2, .3, .3)

mix = S.render(EV, dur=DUR + 1.5)
mix = S.room(mix, size=.35, mix=.16)
sf.write(os.path.join(HERE, 'score.wav'), mix.astype(np.float32), SR)
print('score.wav', round(len(mix) / SR, 2), 's', len(EV), 'notes')
