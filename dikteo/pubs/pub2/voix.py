"""Voix off française avec Piper (voix « siwis », licence CC-BY 4.0 : créditer « SIWIS French Speech Synthesis Database »).

Usage (avec l'environnement .venv-voix, où onnxruntime fonctionne) :
  .venv-voix/bin/python (Windows : Scripts/python) voix.py <fichier de répliques> <dossier de sortie> [--vitesse 0.92]

Fichier de répliques : une ligne par réplique, « nom|texte ». Le texte est écrit pour l'oreille (« Dikté-o »,
« té-vé-a ») : le sous-titre, lui, garde l'orthographe normale.
"""
import argparse
import io
import os
import wave

from piper import PiperVoice
from piper.config import SynthesisConfig

ICI = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repliques")
    ap.add_argument("sortie")
    ap.add_argument("--vitesse", type=float, default=0.92, help="length_scale : plus petit = plus rapide")
    ap.add_argument("--voix", default=os.path.join(ICI, "voix", "fr_FR-siwis-medium.onnx"))
    a = ap.parse_args()
    v = PiperVoice.load(a.voix)
    os.makedirs(a.sortie, exist_ok=True)
    cfg = SynthesisConfig(length_scale=a.vitesse)
    with open(a.repliques, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            nom, texte = ligne.split("|", 1)
            chemin = os.path.join(a.sortie, nom + ".wav")
            with wave.open(chemin, "wb") as w:
                v.synthesize_wav(texte, w, syn_config=cfg)
            with wave.open(chemin) as w:
                print(f"{nom}\t{w.getnframes() / w.getframerate():.2f}\t{texte}")


if __name__ == "__main__":
    main()
