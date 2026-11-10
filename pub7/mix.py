"""Mixage : la partition de piano + le projecteur dans la cabine (le seul « son de salle » d'un film muet) → out/mix.wav
Aucun bruitage, volontairement : le piano joue chaque gag. Le projecteur démarre au début, ronronne sous tout le film,
reste seul pendant le SILENCE du carton « Il y avait une autre façon. », puis la queue de la pellicule claque à la fin."""
import sys, os, json
import numpy as np, soundfile as sf
D = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB', os.path.expanduser('~/lemo-opuscar'))
sys.path.insert(0, LIB)
from core.audio.sfx import SR, bp, t_, limit, compress
rng = np.random.default_rng(7)
TL = json.load(open(os.path.join(D, 'timeline.json'), encoding='utf-8')); SEC, HIT, DUR = TL['SEC'], TL['HIT'], TL['DUR']
N = int(round(DUR * SR))
score, sr = sf.read(os.path.join(D, 'music/score.wav')); assert sr == SR
score = np.pad(score, ((0, max(0, N - len(score))), (0, 0)))[:N]

def griffe(v=1.0):
    """une avance de la griffe : un petit tic métallique et un coup sourd"""
    tt = t_(.05)
    x = bp(rng.standard_normal(len(tt)), 1200, 5200) * np.exp(-tt / .004) * .9 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / .012) * .5
    return x * v
fin0 = HIT['claque'] - .3
def vitesse(t):
    if t < .1: return 0
    if t < 1.1: return 18 * min(1, (t - .1) / .9) ** .7
    if t < fin0: return 18
    return max(0, 18 * (1 - (t - fin0) / 1.2))
proj = np.zeros(N); t = .1
while t < DUR - .05:
    f = vitesse(t)
    if f < 1: t += .02; continue
    c = griffe(.8 + .2 * rng.random()); s = int(t * SR); e = min(N, s + len(c)); proj[s:e] += c[:e - s]
    t += 1 / f * (1 + (rng.random() - .5) * .04)
tt = np.arange(N) / SR; sp = np.interp(tt, tt[::480], np.array([vitesse(x) for x in tt[::480]])) / 18
hum = (np.sin(2 * np.pi * 60 * tt) * .5 + np.sin(2 * np.pi * 120 * tt) * .3 + np.sin(2 * np.pi * 180 * tt) * .12) * sp
fan = bp(rng.standard_normal(N), 300, 1800) * .25 * sp
proj = proj * .5 + hum * .05 + fan * .35
t = fin0 + .1                                    # la queue de la pellicule qui claque sur la bobine
while t < DUR - .1:
    f = max(4, 14 - (t - fin0) * 5); x = bp(rng.standard_normal(int(.03 * SR)), 600, 4000) * np.exp(-t_(.03) / .006) * 1.2
    s = int(t * SR); e = min(N, s + len(x)); proj[s:e] += x[:e - s]; t += 1 / f
k = int(.05 * SR); proj[k:k + int(.03 * SR)] += bp(rng.standard_normal(int(.03 * SR)), 900, 6000) * np.exp(-t_(.03) / .004) * 2   # la lampe s'allume
c2, v0 = SEC['CARD2']['t0'], SEC['VOIX']['t0']
niv = [(0, 1.0), (SEC['CARD1']['t0'], 1.0), (SEC['CARD1']['t0'] + .4, .35), (c2 - .15, .35), (c2 + .15, 1.0), (v0, 1.0), (v0 + .6, .32), (fin0, .32), (fin0 + .6, 1.0), (DUR + 1, 1.0)]
proj = proj * np.interp(tt, [p[0] for p in niv], [p[1] for p in niv]) * .13
pr = np.stack([proj * .9, proj * 1.0], 1)
sc = score * .9; lk = np.abs(sc).max(1); gk = compress(lk, thr=.18, ratio=3, att=.002, rel=.12) / np.maximum(lk, 1e-9)
mix = sc * gk[:, None] * 1.5 + pr
for c in (0, 1): mix[:, c] = limit(mix[:, c], .95)
os.makedirs(os.path.join(D, 'out'), exist_ok=True)
sf.write(os.path.join(D, 'out/mix.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
print('mix.wav', round(len(mix) / SR, 2), 's  crête', round(float(np.abs(mix).max()), 3))
