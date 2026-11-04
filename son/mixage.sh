#!/usr/bin/env bash
# Le mixage final : musique + bruitages, puis le volume aux normes des réseaux (−14 LUFS intégré, crête réelle −1 dBTP).
# Normalisation en deux passes (mesure, puis correction linéaire) : on ne comprime pas la musique, on la règle.
# Usage : bash son/mixage.sh   (lit out/musique_30s.wav et out/bruitages_30s.wav, écrit out/mix_30s.wav)
set -euo pipefail
cd "$(dirname "$0")/.."
bash son/musique.sh out/musique_30s.wav > /dev/null
python son/bruitages.py out/bruitages_30s.wav > /dev/null
ffmpeg -v error -y -i out/musique_30s.wav -i out/bruitages_30s.wav \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0:duration=first" -c:a pcm_s24le out/mix_brut.wav
mesure=$(ffmpeg -hide_banner -nostats -i out/mix_brut.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
val() { echo "$mesure" | grep "\"$1\"" | sed -E 's/.*: "([^"]+)".*/\1/'; }
ffmpeg -v error -y -i out/mix_brut.wav -af "loudnorm=I=-14:TP=-1:LRA=11:linear=true:measured_I=$(val input_i):measured_TP=$(val input_tp):measured_LRA=$(val input_lra):measured_thresh=$(val input_thresh):offset=$(val target_offset),aresample=48000" \
  -c:a pcm_s24le out/mix_30s.wav
ffmpeg -hide_banner -nostats -i out/mix_30s.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
