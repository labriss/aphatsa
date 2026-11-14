"""Arrange et masterise une musique sur la pub claire (96 BPM, temps = 0,625 s).
Pistes séparées par Demucs (batterie, basse, autres) → accroche filtrée sans batterie, la batterie entre sur la promesse,
arrêt d'un demi-temps avant le carton, fin propre ; mastering Matchering sur une référence commerciale, puis -14 LUFS.
python arranger.py <musique.wav> <sortie.wav> [reference.mp3]"""
import os, sys, subprocess, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
src, sortie = sys.argv[1], sys.argv[2]; ref = sys.argv[3] if len(sys.argv) > 3 else None
B = 60 / 96; PROMESSE, CARTON, FIN = 4 * B, 26 * B, 31 * B
tmp = sortie + "_stems"; os.makedirs(tmp, exist_ok=True)
subprocess.run([sys.executable, "-m", "demucs", "-n", "htdemucs", "-o", tmp, "--device", "cpu", src], check=True, capture_output=True)
d = os.path.join(tmp, "htdemucs", os.path.splitext(os.path.basename(src))[0])
st = {k: sf.read(os.path.join(d, k + ".wav"))[0] for k in ("drums", "bass", "other", "vocals")}
sr = sf.info(os.path.join(d, "drums.wav")).samplerate; n = int(FIN * sr) + int(.05 * sr)
for k in st: st[k] = np.pad(st[k], ((0, max(0, n - len(st[k]))), (0, 0)))[:n]
t = np.arange(n) / sr
def rampe(a, b, d):  # 0 avant a, 1 après a+d
    return np.clip((t - a) / d, 0, 1) if b is None else None
# batterie : absente sur l'accroche, petit roulement qui monte le dernier temps, pleine sur la promesse
g_dr = np.where(t < PROMESSE - B, 0.0, np.where(t < PROMESSE, .35 * (t - (PROMESSE - B)) / B, 1.0))
# arrêt : tout se coupe un demi-temps avant le carton (sauf la queue des autres instruments), reprise pleine sur le carton
stop = (t >= CARTON - .5 * B) & (t < CARTON)
g_dr[stop] = 0; g_bass = np.ones(n); g_bass[stop] = 0; g_oth = np.ones(n); g_oth[stop] = .25
# accroche : basse et harmonie filtrées (comme derrière une porte), le filtre s'ouvre sur la promesse
def lp(x, f): return sosfilt(butter(2, f, "low", fs=sr, output="sos"), x, axis=0)
ouv = np.clip((t - (PROMESSE - .3)) / .3, 0, 1)[:, None]
harm = st["other"] + st["vocals"]
harm = harm * ouv + lp(harm, 900) * (1 - ouv)
bass = st["bass"] * ouv + lp(st["bass"], 300) * (1 - ouv)
mix = st["drums"] * g_dr[:, None] + bass * g_bass[:, None] * 1.05 + harm * g_oth[:, None]
# accroche un peu plus basse, fin : decrescendo sur la dernière mesure
mix *= (0.7 + 0.3 * ouv)
mix *= np.clip((FIN - t) / 1.4, 0, 1)[:, None] ** .7
# fondus d'entrée et anti-clic aux coupures
mix[: int(.01 * sr)] *= np.linspace(0, 1, int(.01 * sr))[:, None]
brut = sortie.replace(".wav", "_brut.wav"); sf.write(brut, mix / max(1e-6, np.abs(mix).max()) * .8, sr)
if ref:
    import matchering as mg
    mg.process(target=brut, reference=ref, results=[mg.pcm24(sortie)])
else:
    os.replace(brut, sortie)
print("ok", sortie)
