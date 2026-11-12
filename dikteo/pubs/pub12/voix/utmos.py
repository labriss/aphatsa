"""Note de naturel (UTMOS22, prédicteur de MOS) de chaque prise : ~/outils/venv-voix2/bin/python (Windows : Scripts/python) utmos.py → prises/utmos.json"""
import glob, json, os
import torch, torchaudio
ICI = os.path.dirname(os.path.abspath(__file__))
juge = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
notes = {}
for f in sorted(glob.glob(os.path.join(ICI, "prises", "*.wav"))):
    w, sr = torchaudio.load(f)
    w = torchaudio.functional.resample(w.mean(0, keepdim=True), sr, 16000)
    with torch.no_grad():
        notes[os.path.basename(f)] = round(float(juge(w, 16000)), 3)
    print(os.path.basename(f), notes[os.path.basename(f)], flush=True)
json.dump(notes, open(os.path.join(ICI, "prises", "utmos.json"), "w"), indent=1)
