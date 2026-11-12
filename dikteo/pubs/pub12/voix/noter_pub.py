"""Choisit la meilleure prise de chaque phrase d'une pub (prononciation exacte, puis netteté Whisper),
coupe les silences et resserre les pauses (prises/*_serre.wav). python noter_pub.py <dossier voix de la pub>"""
import difflib, glob, json, os, re, subprocess, sys, unicodedata
import numpy as np
from faster_whisper import WhisperModel
DOS = sys.argv[1]
ATT = [l.split("|")[1].strip() for l in open(os.path.join(DOS, "phrases.txt"), encoding="utf-8") if l.strip()]
def norm(s):
    s = s.lower().replace("€", " euros ").replace("×", " ").replace("m²", " mètres carrés ")
    s = re.sub(r"(\d)[\s  ](\d)", r"\1\2", s)
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.replace("-", " ")).split())
def lire(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.float32)
w = WhisperModel("small", device="cpu", compute_type="int8"); res = {}
for f in sorted(glob.glob(os.path.join(DOS, "prises", "H_p*_k?.wav"))):
    b = os.path.basename(f); i = int(re.search(r"_p(\d+)_", b).group(1))
    segs = list(w.transcribe(lire(f), language="fr", beam_size=5)[0]); txt = " ".join(s.text for s in segs).strip()
    nett = sum(s.avg_logprob for s in segs) / max(1, len(segs))
    ex = difflib.SequenceMatcher(None, norm(txt), norm(ATT[i])).ratio()
    res[b] = dict(phrase=i, exact=round(ex, 3), nettete=round(nett, 3), entendu=txt)
    print(f"{b:14s} exact {ex:.2f} nette {nett:.2f}  {txt}", flush=True)
choix = {}
for i in range(len(ATT)):
    c = [(r["exact"] >= .9, r["nettete"], b) for b, r in res.items() if r["phrase"] == i]
    if not c: continue
    b = max(c)[2]; src = os.path.join(DOS, "prises", b); dst = src.replace(".wav", "_serre.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=stop_periods=-1:stop_duration=0.22:stop_threshold=-42dB", dst])
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst], capture_output=True, text=True).stdout)
    choix[i] = dict(prise=b, duree=round(d, 2), exact=res[b]["exact"])
json.dump(dict(prises=res, choix=choix), open(os.path.join(DOS, "prises", "choix.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("CHOIX", json.dumps(choix, ensure_ascii=False))
