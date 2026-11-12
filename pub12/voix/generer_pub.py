"""Voix d'une pub : Chatterbox multilingue (MIT) cloné sur la référence donnée (ref_H.wav : lecteur LibriVox
« Bernard », domaine public). Une ligne de phrases.txt = « texte dit|texte attendu par Whisper ».
~/outils/venv-voix2/Scripts/python generer_pub.py <ref.wav> <dossier voix de la pub> [prises=2]"""
import os, sys, time
import torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
REF, DOS = sys.argv[1], sys.argv[2]
PRISES = int(sys.argv[3]) if len(sys.argv) > 3 else 2
PHRASES = [l.split("|")[0].strip() for l in open(os.path.join(DOS, "phrases.txt"), encoding="utf-8") if l.strip()]
SORTIE = os.path.join(DOS, "prises"); os.makedirs(SORTIE, exist_ok=True)
torch.set_num_threads(4)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); print("modèle chargé", flush=True)
REGLAGES = [(.5, .3, .8), (.45, .35, .75), (.55, .3, .85)]   # dictée posée, peu théâtrale
for i, p in enumerate(PHRASES):
    for k in range(PRISES):
        ex, cfg, temp = REGLAGES[k % len(REGLAGES)]
        torch.manual_seed(1000 * i + k); t0 = time.time()
        w = m.generate(p, language_id="fr", audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg, temperature=temp)
        nom = os.path.join(SORTIE, f"H_p{i}_k{k}.wav"); torchaudio.save(nom, w, m.sr)
        print("ok", os.path.basename(nom), round(time.time() - t0), "s", flush=True)
