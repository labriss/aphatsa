# Musique IA exclusive : ACE-Step 1.5

Modèle : ACE-Step 1.5 turbo (licence MIT, entraîné sur des morceaux sous licence, usage commercial autorisé).
Sur le CPU de la session cloud (Xeon avec AMX bf16) : environ 1 minute pour 20 s de musique.

## Installation (environ 10 min)
1. Réseau : autoriser huggingface.co, us.aws.cdn.hf.co, us.gcp.cdn.hf.co, cas-bridge.xethub.hf.co.
2. `git clone --depth 1 https://github.com/ace-step/ACE-Step-1.5 ~/outils/ACE-Step-1.5`
3. `python3 -m venv ~/outils/ace && . ~/outils/ace/bin/activate`
   `pip install torch==2.10.0 torchaudio==2.10.0 "transformers>=4.51,<4.58" "diffusers>=0.37" scipy soundfile loguru einops "accelerate>=1.12" diskcache matplotlib peft modelscope numba vector-quantize-pytorch pytorch_wavelets PyWavelets`
4. Poids (6 Go, sans le LM 1.7B) dans `~/outils/ace-modeles` depuis `ACE-Step/Ace-Step1.5` sur Hugging Face.
5. Correctif CPU (bf16, moitié moins de mémoire) dans `acestep/core/generation/handler/init_service_orchestrator.py` :
   remplacer `torch.bfloat16 if resolved_device == "xpu" else torch.float32`
   par `torch.bfloat16 if (resolved_device == "xpu" or os.environ.get("ACESTEP_CPU_BF16") == "1") else torch.float32`.

## Utilisation
`python -I composer_lot.py <dossier> 96 21 [style ...]` → `<style>.wav` + `<style>.json` (description, tonalité, graine).
Styles prêts : trap, phonk, afro, reggaeton, boombap, electropop, funk, epique (96 BPM = tempo des pubs claires).
Monter sur une pub : `MUSIQUE=<wav> DEBUT_M=0 MUSIQUE_DB=-3 python3 dikteo/pubs/clair/son.py <muet.mp4> <sortie.mp4>`.

## Choix
`noter_musiques.py <ref.wav> <wav...>` note chaque morceau (ressemblance avec une musique aimée, régularité, douceur, chaleur, mélodie, bruit).
Musique des pubs claires (14 nov.) : `musiques/lofi_reggaeton_202.mp3` — lo-fi reggaeton posé, choisi daprès