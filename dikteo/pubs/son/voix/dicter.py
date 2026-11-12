"""Voix d'une pub : l'artisan dicte ses lignes de devis. Synthèse vocale locale, sur le processeur, sans Hugging Face.
Une ligne de <pub>/voix/phrases.txt = « texte dit | texte affiché | place en secondes » (la place : du début de la phrase
au début de la suivante, ce que la voix peut occuper ; facultative).
Moteurs (modèles téléchargés depuis les releases GitHub, voir son/voix/installer.sh) :
  piper (piper-tts) : tom (fr_FR-tom-medium, homme, 44,1 kHz ; poids AGPL-3.0, voix d'une personne réelle autorisée
                      gratuitement si on ne la présente pas comme celle d'une personne réelle ou identifiée et qu'on ne nomme pas
                      son auteur), tj1..tj3 (fr_FR-tjiho, même voix, plus anciens), pierre (fr_FR-upmc, locuteur pierre, CC BY-SA 4.0)
  kokoro (kokoro-onnx, Apache 2.0) : siwis (ff_siwis, femme, données SIWIS CC BY 4.0 ; la plus naturelle, mais une femme)
  Écartée : miro (fr_FR-miro-high) — licence CC BY-NC-ND (TigreGotico), interdite en publicité.
Trois débits par voix (posé, normal, serré) × PRISES tirages : noter.py choisit ensuite.
~/outils/venv-tts/bin/python dicter.py <dossier voix de la pub> [voix=tom,siwis] [prises=2]
→ <pub>/voix/prises/<voix>_p<i>_d<debit>_k<prise>.wav"""
import os
import sys

import numpy as np
import soundfile as sf

T = os.path.expanduser(os.environ.get("MODELES_TTS", "~/outils/tts"))
DOS = sys.argv[1]
VOIX = (sys.argv[2] if len(sys.argv) > 2 else "tom,siwis").split(",")
PRISES = int(sys.argv[3]) if len(sys.argv) > 3 else 2
PHRASES = [l.split("|")[0].strip() for l in open(os.path.join(DOS, "phrases.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")]
SORTIE = os.path.join(DOS, "prises")
os.makedirs(SORTIE, exist_ok=True)

PIPER = {"tom": ("tom-medium", None), "tj1": ("tjiho-model1", None), "tj2": ("tjiho-model2", None), "tj3": ("tjiho-model3", None),
         "pierre": ("upmc-medium", 1)}
# débits : length_scale de Piper (plus petit = plus rapide) ; tom est naturellement lent. DEBITS=serre : pour les pubs
# dont les phrases n'ont qu'environ 1,4 s.
SERRE = os.environ.get("DEBITS") == "serre"
DEBITS_PIPER = {"tom": (.8, .72, .66) if SERRE else (.95, .87, .8)}
DEBITS_K = (1.12, 1.22, 1.32) if SERRE else (.92, 1.0, 1.08)


def piper(nom):
    from piper import PiperVoice, SynthesisConfig
    m, sid = PIPER[nom]
    d = f"{T}/vits-piper-fr_FR-{m}"
    v = PiperVoice.load(f"{d}/fr_FR-{m}.onnx", config_path=f"{d}/fr_FR-{m}.onnx.json")

    def dire(txt, j, k):
        ls = DEBITS_PIPER.get(nom, (.88, .8, .74) if SERRE else (1.0, .92, .85))[j]
        # un peu moins de bruit que par défaut : moins de grain, prosodie plus posée ; varié d'une prise à l'autre
        cfg = SynthesisConfig(speaker_id=sid, length_scale=ls, noise_scale=(.55, .667, .45)[k % 3], noise_w_scale=(.7, .8, .6)[k % 3])
        morceaux = list(v.synthesize(txt, syn_config=cfg))
        return np.concatenate([c.audio_float_array for c in morceaux]), morceaux[0].sample_rate
    return dire


def kokoro(voix):
    from kokoro_onnx import Kokoro
    k = Kokoro(f"{T}/kokoro/kokoro-v1.0.onnx", f"{T}/kokoro/voices-v1.0.bin")

    def dire(txt, j, _k):
        return k.create(txt, voice=voix, speed=DEBITS_K[j], lang="fr-fr")
    return dire


for nom in VOIX:
    dire = kokoro("ff_siwis") if nom == "siwis" else piper(nom)
    # Kokoro est déterministe : une seule prise par débit
    n = 1 if nom == "siwis" else PRISES
    for i, p in enumerate(PHRASES):
        for j in range(3):
            for k in range(n):
                a, sr = dire(p, j, k)
                f = os.path.join(SORTIE, f"{nom}_p{i}_d{j}_k{k}.wav")
                sf.write(f, np.asarray(a, np.float32), sr)
                print("ok", os.path.basename(f), round(len(a) / sr, 2), "s", flush=True)
