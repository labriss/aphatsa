"""Voix off de la pub 3 avec Chatterbox Multilingual (MIT), timbre guidé par une voix de synthèse (Piper « tom »).
~/outils/venv-voix2/bin/python (Windows : Scripts/python) voix_off.py [nom ...] → v2/<nom>_<k>.wav (plusieurs prises par réplique)."""
import os
import sys

import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ICI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(ICI, "v2", "ref_tom.wav")

# nom : (texte écrit pour être bien prononcé, expressivité, nombre de prises)
REPLIQUES = {
    "r1": ("Six heures cinquante-huit. Le client a juste une petite question.", 0.55, 2),
    "r2": ("Huit heures quinze. Bouchon.", 0.5, 2),
    "r3": ("Neuf heures quarante. Ta pièce ? Rupture.", 0.55, 2),
    "r4": ("Quatre minutes pour décharger. Trente-cinq euros.", 0.55, 2),
    "r5": ("Dix-sept heures trente. En fait... ils préfèrent le blanc.", 0.6, 2),
    "r6": ("Vingt et une heures. Et un message.", 0.6, 3),
    "r7": ("Et puis... Dictéo.", 0.5, 3),
    "r8": ("Tu parles. Le devis se fait tout seul.", 0.55, 2),
    "r9": ("Trente secondes plus tard, c'est envoyé. Fini la vie en pixels.", 0.6, 2),
    "r10": ("Dictéo. Le devis du soir, fait en trente secondes, à la voix.", 0.5, 3),
    "r11": ("Gratuit pour commencer.", 0.5, 3),
}

if __name__ == "__main__":
    noms = sys.argv[1:] or list(REPLIQUES)
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    for nom in noms:
        txt, ex, n = REPLIQUES[nom]
        for k in range(n):
            w = m.generate(txt, language_id="fr", audio_prompt_path=REF, exaggeration=ex, cfg_weight=0.45, temperature=0.75)
            torchaudio.save(os.path.join(ICI, "v2", f"{nom}_{k}.wav"), w, m.sr)
            print("ok", nom, k, flush=True)
