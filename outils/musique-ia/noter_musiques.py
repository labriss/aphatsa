"""Note des musiques par rapport à une référence aimée. python noter_musiques.py <ref.wav> <fichiers...>"""
import sys, numpy as np, librosa
def feats(f):
    y, sr = librosa.load(f, sr=22050, mono=True); y = y[: 20 * sr]
    rms = librosa.feature.rms(y=y)[0]; cen = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    flat = librosa.feature.spectral_flatness(y=y)[0]; chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mf = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20); onset = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr)
    ibi = np.diff(librosa.frames_to_time(beats, sr=sr)); reg = 1 - min(1, np.std(ibi) / max(1e-6, np.mean(ibi))) if len(ibi) > 3 else 0
    vec = np.concatenate([mf.mean(1) / 50, mf.std(1) / 50, chroma.mean(1), [cen.mean() / 4000, flat.mean() * 10, rms.mean() * 5]])
    return dict(vec=vec, regul=reg, lisse=1 - min(1, rms.std() / max(1e-6, rms.mean())), chaud=1 - abs(cen.mean() - 2200) / 2200,
                tonal=float(np.mean(chroma.max(0) - chroma.mean(0))), bruit=float(flat.mean()), crete=float(np.abs(y).max()))
ref = feats(sys.argv[1]); res = []
for f in sys.argv[2:]:
    d = feats(f); sim = float(np.dot(d["vec"], ref["vec"]) / np.linalg.norm(d["vec"]) / np.linalg.norm(ref["vec"]))
    score = 40 * sim + 15 * d["regul"] + 15 * d["lisse"] + 10 * d["chaud"] + 15 * min(1, d["tonal"] / .5) - 50 * max(0, d["bruit"] - .05)
    res.append((score, f, sim, d))
for s, f, sim, d in sorted(res, reverse=True):
    print(f"{s:5.1f}  {f.split('/')[-1]:28s} ressemblance={sim:.3f} régularité={d['regul']:.2f} lissé={d['lisse']:.2f} chaleur={d['chaud']:.2f} tonal={d['tonal']:.2f} bruit={d['bruit']:.3f}")
