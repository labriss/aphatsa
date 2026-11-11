"""Les 4 phrases de la pub 12 avec Kokoro (Apache 2.0), voix française ff_siwis, 3 débits.
~/outils/venv-kokoro/Scripts/python kokoro_gen.py → prises/K_p<i>_k<j>.wav"""
import os, soundfile as sf
from kokoro_onnx import Kokoro
ICI = os.path.dirname(os.path.abspath(__file__)); D = os.path.expanduser("~/outils/kokoro")
PHRASES = ["Rebouchage des fissures, forfait cent quatre-vingts euros.", "Sous-couche, trente-deux mètres carrés, sept euros le mètre.",
           "Deux couches de peinture mat velours, dix-huit euros le mètre.", "Protection et nettoyage, quatre-vingt-dix euros."]
k = Kokoro(os.path.join(D, "kokoro-v1.0.onnx"), os.path.join(D, "voices-v1.0.bin"))
os.makedirs(os.path.join(ICI, "prises"), exist_ok=True)
for i, p in enumerate(PHRASES):
    for j, v in enumerate((.95, 1.02, 1.1)):
        a, sr = k.create(p, voice="ff_siwis", speed=v, lang="fr-fr")
        sf.write(os.path.join(ICI, "prises", f"K_p{i}_k{j}.wav"), a, sr); print("ok", i, j, round(len(a) / sr, 2), "s", flush=True)
