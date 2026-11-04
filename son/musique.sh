#!/usr/bin/env bash
# La piste musicale de la pub (30 s), calée sur le découpage (voir decoupage.md, « Musique »).
# Deux morceaux de « Promo Drop », coupés sur des barres de mesure (152 BPM, mesure = 1,579 s) :
#   - le début du morceau (0 → 18,34 s) posé à 7,29 s : son drop (5,71 s) tombe à 13,00 s ;
#   - la dernière mesure (105,19 s → fin) posée à 25,63 s : le dernier coup tombe à 27,21 s.
# Fondus de 30 ms aux raccords, fondu final sur les 0,5 dernières secondes.
# Le MP3 est masterisé très fort (crêtes réelles à +3,2 dB une fois décodé) : on baisse de 5 dB en virgule flottante,
# avant d'écrire le fichier, pour ne jamais écrêter. Le volume final se règle au mixage (−14 LUFS).
# Usage : bash son/musique.sh <sortie.wav>
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=assets/musique/promo-drop.mp3
OUT=${1:-out/musique_30s.wav}
mkdir -p "$(dirname "$OUT")"

ffmpeg -v error -y -i "$SRC" -filter_complex "
  [0:a]atrim=0:18.37,asetpts=PTS-STARTPTS,afade=t=out:st=18.34:d=0.03,adelay=7290:all=1[a];
  [0:a]atrim=105.16,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.03,adelay=25600:all=1[b];
  [a][b]amix=inputs=2:normalize=0:duration=longest,apad,atrim=0:30,afade=t=out:st=29.5:d=0.5,volume=-5dB[m]
" -map "[m]" -ar 48000 -ac 2 -c:a pcm_s24le "$OUT"
echo "$OUT"
