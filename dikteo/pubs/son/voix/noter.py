"""Choisit la voix d'une pub puis la meilleure prise de chaque phrase.
Pour chaque prise : ce que Whisper (small, sherpa-onnx, en local) entend, comparé au texte dit (exactitude),
la note de naturel UTMOS si prises/utmos.json existe (utmos.py), la durée utile (silences coupés) et le resserrement
qu'il faudrait pour tenir dans la place de la phrase (au plus ×1,15).
Une seule voix par pub (c'est le même artisan qui dicte) : celle dont les meilleures prises notent le mieux, ou VOIX=<nom>.
~/outils/venv-tts/bin/python noter.py <dossier voix de la pub> → prises/choix.json"""
import difflib
import glob
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np

DOS = sys.argv[1]
LIGNES = [[c.strip() for c in l.split("|")] for l in open(os.path.join(DOS, "phrases.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")]
DIT = [l[0] for l in LIGNES]
PLACE = [float(l[2]) if len(l) > 2 and l[2] else 9.0 for l in LIGNES]
TEMPO_MAX = 1.15
W = os.path.expanduser(os.environ.get("WHISPER", "~/outils/tts/sherpa-onnx-whisper-small"))


def norm(s):
    from num2words import num2words
    s = s.lower().replace("€", " euros ").replace("m²", " mètres carrés ").replace("×", " par ")
    s = re.sub(r"(\d)[\s  .](\d{3})\b", r"\1\2", s)
    s = re.sub(r"\d+", lambda m: " " + num2words(int(m.group()), lang="fr") + " ", s)
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z ]", " ", s.replace("-", " ")).split())


CHIFFRES = set("deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize vingt vingts trente quarante cinquante soixante cent cents mille".split())


def nombres(s):
    """les mots-nombres dans l'ordre : un prix mal entendu (« quatre-vingt-cinq » pour « quatre-vingt-quinze ») est rédhibitoire"""
    return [m for m in norm(s).split() if m in CHIFFRES]


def lire(f, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", f] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", "1", "-ar", "16000", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)


COUPE = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
import sherpa_onnx  # noqa: E402

rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{W}/small-encoder.int8.onnx", decoder=f"{W}/small-decoder.int8.onnx",
                                                 tokens=f"{W}/small-tokens.txt", language="fr", task="transcribe", num_threads=4)
mos = {}
if os.path.exists(os.path.join(DOS, "prises", "utmos.json")):
    mos = json.load(open(os.path.join(DOS, "prises", "utmos.json")))
res = {}
for f in sorted(glob.glob(os.path.join(DOS, "prises", "*_p*_d*_k*.wav"))):
    b = os.path.basename(f)
    voix, i = b.split("_p")[0], int(re.search(r"_p(\d+)_", b).group(1))
    if i >= len(DIT):
        continue
    x = lire(f, COUPE)
    st = rec.create_stream()
    st.accept_waveform(16000, x / max(1e-6, np.abs(x).max()) * .8)
    rec.decode_stream(st)
    txt = st.result.text.strip()
    ex = difflib.SequenceMatcher(None, norm(txt), norm(DIT[i])).ratio()
    nb = nombres(txt) == nombres(DIT[i])
    dur = len(x) / 16000
    tempo = max(1.0, dur / PLACE[i])
    m = mos.get(b, 3.0)
    # le naturel (si noté) et la netteté d'abord ; un prix mal entendu ou une prise qui ne tient pas dans sa place est écartée ;
    # resserrer coûte un peu ; une prise qui remplit sa place (débit posé) est préférée à une prise pressée
    score = m + .5 * min(1, dur / PLACE[i]) + 1.5 * ex - 2 * (ex < .85) - 2 * (not nb) - 3 * (tempo > TEMPO_MAX) - 2.5 * (tempo - 1)
    res[b] = dict(voix=voix, phrase=i, exact=round(ex, 3), prix_ok=nb, utmos=m, duree=round(dur, 2), tempo=round(tempo, 3), score=round(score, 3), entendu=txt)
    print(f"{b:24s} exact {ex:.2f} prix {'ok' if nb else 'FAUX'} mos {m:.2f} {dur:4.2f}s (place {PLACE[i]:.2f}) tempo {tempo:.2f} score {score:5.2f}  {txt}", flush=True)

familles = {}
for v in sorted({r["voix"] for r in res.values()}):
    meilleurs = [max([r["score"] for r in res.values() if r["voix"] == v and r["phrase"] == i] or [-9]) for i in range(len(DIT))]
    # + la régularité de la voix : part de toutes ses prises comprises mot pour mot, prix compris
    regulier = np.mean([r["exact"] * r["prix_ok"] for r in res.values() if r["voix"] == v])
    familles[v] = round(float(np.mean(meilleurs) + regulier), 3)
voix = os.environ.get("VOIX") or max(familles, key=familles.get)
choix = {}
for i in range(len(DIT)):
    c = [(r["score"], b) for b, r in res.items() if r["voix"] == voix and r["phrase"] == i]
    if c:
        choix[str(i)] = max(c)[1]
manque = [i for i in range(len(DIT)) if str(i) not in choix or res[choix[str(i)]]["score"] < 0]
json.dump(dict(voix=voix, familles=familles, choix=choix, a_revoir=manque, prises=res),
          open(os.path.join(DOS, "prises", "choix.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("FAMILLES", familles)
print("VOIX", voix, "CHOIX", json.dumps({k: (v, res[v]["entendu"], res[v]["tempo"]) for k, v in choix.items()}, ensure_ascii=False), "À REVOIR", manque)
