"""Choisit la meilleure prise de chaque phrase : prononciation exacte puis netteté (confiance moyenne de Whisper).
python noter.py → prises/choix.json et le classement à l'écran"""
import numpy as np
import difflib, glob, json, os, re, subprocess, unicodedata
from faster_whisper import WhisperModel
ICI = os.path.dirname(os.path.abspath(__file__))
ATTENDU = ["rebouchage des fissures forfait cent quatre-vingts euros", "sous-couche trente-deux mètres carrés à sept euros le mètre",
           "deux couches de peinture mat velours dix-huit euros le mètre", "protection nettoyage quatre-vingt-dix euros"]
NOMBRES = {"180": "cent quatre-vingts", "32": "trente-deux", "7": "sept", "18": "dix-huit", "90": "quatre-vingt-dix", "2": "deux", "m2": "mètres carrés", "m²": "mètres carrés"}
def norm(s):
    s = s.lower().replace("€", " euros ")
    for k, v in NOMBRES.items(): s = re.sub(rf"\b{re.escape(k)}\b", v, s)
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s.replace("-", " ")).split())
w = WhisperModel("small", device="cpu", compute_type="int8")
res = {}
for f in sorted(glob.glob(os.path.join(ICI, "prises", os.environ.get("PREFIXE", "") + "*.wav"))):
    b = os.path.basename(f); i = int(re.search(r"_p(\d)_", b).group(1))
    segs = list(w.transcribe(np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.float32), language="fr", beam_size=5)[0]); txt = " ".join(s.text for s in segs)
    nett = sum(s.avg_logprob for s in segs) / max(1, len(segs))
    exact = difflib.SequenceMatcher(None, norm(txt), norm(ATTENDU[i])).ratio()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    res[b] = dict(phrase=i, exact=round(exact, 3), nettete=round(nett, 3), duree=round(dur, 2), entendu=txt.strip())
    print(f"{b:28s} exact {exact:.2f} nette {nett:.2f} {dur:4.1f}s  {txt.strip()}", flush=True)
choix = {}
for i in range(4):
    c = [(r["exact"] >= .9, r["nettete"], b) for b, r in res.items() if r["phrase"] == i]
    if c: choix[i] = max(c)[2]
json.dump(dict(prises=res, choix=choix), open(os.path.join(ICI, "prises", "choix.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("CHOIX", choix)
