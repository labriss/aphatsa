#!/usr/bin/env bash
# Le mixage final d'une version : musique + bruitages, puis le volume aux normes des réseaux
# (−16 LUFS intégré, crête réelle sous −4 dBTP : marge pour la recompression AAC des réseaux et les haut-parleurs de téléphone). Normalisation en deux passes (mesure, puis correction linéaire) :
# on ne comprime pas la musique, on la règle.
# Usage : bash son/mixage.sh [30|15|6]   (écrit out/mix_<version>s.wav)
set -euo pipefail
cd "$(dirname "$0")/.."
V=${1:-30}
python son/musique.py "$V" "out/musique_${V}s.wav" > /dev/null
python son/bruitages.py "$V" "out/bruitages_${V}s.wav" > /dev/null
ffmpeg -v error -y -i "out/musique_${V}s.wav" -i "out/bruitages_${V}s.wav" \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0:duration=first" -c:a pcm_s24le "out/mix_brut_${V}s.wav"
mesure=$(ffmpeg -hide_banner -nostats -i "out/mix_brut_${V}s.wav" -af loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
val() { echo "$mesure" | grep "\"$1\"" | sed -E 's/.*: "([^"]+)".*/\1/'; }
ffmpeg -v error -y -i "out/mix_brut_${V}s.wav" -af "loudnorm=I=-16:TP=-4.5:LRA=11:linear=true:measured_I=$(val input_i):measured_TP=$(val input_tp):measured_LRA=$(val input_lra):measured_thresh=$(val input_thresh):offset=$(val target_offset),aresample=48000" \
  -c:a pcm_s24le "out/mix_${V}s.wav"
echo "version $V s :"
ffmpeg -hide_banner -nostats -i "out/mix_${V}s.wav" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
