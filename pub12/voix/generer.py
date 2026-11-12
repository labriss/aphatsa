"""Voix de la pub 12 : le peintre dicte ses 4 lignes de devis.
Chatterbox multilingue (Resemble AI, licence MIT), en local sur le processeur, cloné sur une vraie voix française
enregistrée pour la synthèse (base SIWIS, CC BY 4.0). Plusieurs références × plusieurs prises par phrase ;
noter.py choisit ensuite la meilleure prise.
~/outils/venv-voix2/Scripts/python generer.py <ref.wav> <etiquette> [prises=3] [phrases=0,1,2,3]"""
import os
import sys
import time

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ICI = os.path.dirname(os.path.abspath(__file__))
# Écrit comme on le dit : les nombres en toutes lettres, la ponctuation pour les respirations.
PHRASES = [
    "Rebouchage des fissures... forfait, cent quatre-vingts euros.",
    "Sous-couche, trente-deux mètres carrés... à sept euros le mètre.",
    "Deux couches de peinture mat velours... dix-huit euros le mètre.",
    "Protection, nettoyage... quatre-vingt-dix euros.",
]
REF, ETI = sys.argv[1], sys.argv[2]
PRISES = int(sys.argv[3]) if len(sys.argv) > 3 else 3
QUELLES = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else range(len(PHRASES))
SORTIE = os.path.join(ICI, "prises")
os.makedirs(SORTIE, exist_ok=True)
torch.set_num_threads(4)
t0 = time.time()
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print("modèle chargé", round(time.time() - t0), "s", flush=True)
# réglages d'une dictée : posée, peu théâtrale (exagération basse), débit naturel
REGLAGES = [(.5, .3, .8), (.45, .35, .75), (.55, .3, .85)]
for i in QUELLES:
    for k in range(PRISES):
        ex, cfg, temp = REGLAGES[k % len(REGLAGES)]
        torch.manual_seed(1000 * i + k)
        t0 = time.time()
        w = m.generate(PHRASES[i], language_id="fr", audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg, temperature=temp)
        nom = os.path.join(SORTIE, f"{ETI}_p{i}_k{k}.wav")
        torchaudio.save(nom, w, m.sr)
        print("ok", os.path.basename(nom), round(time.time() - t0), "s", flush=True)
