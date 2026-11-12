"""Transcrit chaque prise avec Whisper et garde, pour chaque réplique, celle qui colle le mieux au texte attendu.
python choisir.py → v2/choix.txt (et le détail à l'écran)."""
import difflib
import os
import re
import subprocess
import unicodedata

import numpy as np
from faster_whisper import WhisperModel

ICI = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(ICI, "v2")
# ce qu'on doit entendre (Diktéo s'écrit « Dictéo » pour Whisper aussi)
ATTENDU = {
    "r1": "six heures cinquante-huit le client a juste une petite question",
    "r2": "huit heures quinze bouchon",
    "r3": "neuf heures quarante ta pièce rupture",
    "r4": "quatre minutes pour décharger trente-cinq euros",
    "r5": "dix-sept heures trente en fait ils préfèrent le blanc",
    "r6": "vingt et une heures et un message",
    "r7": "et puis dictéo",
    "r8": "tu parles le devis se fait tout seul",
    "r9": "trente secondes plus tard c'est envoyé fini la vie en pixels",
    "r10": "dictéo le devis du soir fait en trente secondes à la voix",
    "r11": "gratuit pour commencer",
}
CHIFFRES = {"6h58": "six heures cinquante-huit", "8h15": "huit heures quinze", "9h40": "neuf heures quarante",
            "17h30": "dix-sept heures trente", "21h": "vingt et une heures", "35": "trente-cinq", "30": "trente", "3": "trois", "4": "quatre"}


def norm(t):
    t = t.lower().replace("’", "'")
    t = re.sub(r"(\d+)\s*h\s*(\d*)", lambda m: m.group(1) + "h" + m.group(2), t)
    for k, v in sorted(CHIFFRES.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"\b{k}\b", v, t)
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = re.sub(r"(dikteo|dicteo|dicte o|dik teo|dictaio|diktaio)", "dicteo", t)
    return re.sub(r"[^a-z ]+", " ", t).split()


def main():
    m = WhisperModel("small", device="cpu", compute_type="int8")
    choix = []
    for nom, att in ATTENDU.items():
        prises = sorted(f for f in os.listdir(V2) if re.fullmatch(rf"{nom}_\d+\.wav", f))
        meilleur = None
        for f in prises:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(V2, f), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                                 capture_output=True).stdout
            a = np.frombuffer(raw, np.float32)
            segs, _ = m.transcribe(a, language="fr", vad_filter=False, initial_prompt="Diktéo, devis, plombier.")
            dit = " ".join(s.text for s in segs)
            score = difflib.SequenceMatcher(None, norm(att), norm(dit)).ratio()
            duree = len(a) / 16000
            print(f"{f:10s} {score:.2f} {duree:4.1f}s  {dit.strip()}")
            if meilleur is None or score > meilleur[0] + 0.01:
                meilleur = (score, f)
        if meilleur:
            choix.append(f"{nom} {meilleur[1]}")
            print("  →", meilleur[1], f"{meilleur[0]:.2f}")
    open(os.path.join(V2, "choix.txt"), "w", encoding="utf-8").write("\n".join(choix) + "\n")


if __name__ == "__main__":
    main()
