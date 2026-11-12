#!/bin/bash
# Reprises des phrases faibles (pub 13 : grès cérame, plinthes ; pub 19 : fuite) : 4 nouvelles prises, puis nouvelle notation et nouvel essai.
V=$(cd "$(dirname "$0")/../.." && pwd)  # le dossier video/ (sous Windows : /c/Users/Brisset/Desktop/plomberie-durand/video)
VENV2=~/outils/venv-voix2; VPY=$VENV2/bin/python; [ -x "$VPY" ] || VPY=$VENV2/Scripts/python  # macOS : bin/, Windows : Scripts/
if [ -z "${PY:-}" ]; then PY=python; [ "$(uname -s)" = Darwin ] && { PY=python3; [ -x ~/outils/venv-video/bin/python ] && PY=~/outils/venv-video/bin/python; }; fi  # macOS : venv-video ; Windows : python
command -v timeout >/dev/null || timeout(){ if command -v gtimeout >/dev/null; then gtimeout "$@"; else shift; "$@"; fi; }  # macOS : pas de timeout sans coreutils
until grep -q "motion fini" "$1" 2>/dev/null; do sleep 60; done
until ( set -C; echo "voix reprises" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 50; done; echo "verrou $(date +%T)"
timeout 5400 $VPY $V/pub12/voix/generer_pub.py $V/pub12/voix/ref_H.wav $V/pub13/voix 4 2,3 2 > $V/pub13/voix/gen2.log 2>&1; echo "pub13 $(date +%T)"
timeout 3600 $VPY $V/pub12/voix/generer_pub.py $V/pub12/voix/ref_H.wav $V/pub19/voix 4 1 2 > $V/pub19/voix/gen2.log 2>&1; echo "pub19 $(date +%T)"
[ "$(cat $V/RENDU_EN_COURS.lock)" = "voix reprises" ] && rm -f $V/RENDU_EN_COURS.lock
CH="highpass=f=110,lowpass=f=9000,equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,aecho=0.8:0.4:19:0.10"
for p in pub13 pub19; do
  rm -f $V/$p/voix/prises/*_serre.wav
  $PY $V/pub12/voix/noter_pub.py $V/$p/voix 2>&1 | grep -a "exact\|CHOIX"
  args=(); fc=""; n=0; for f in $(ls $V/$p/voix/prises/*_serre.wav | sort -V); do args+=(-i "$f"); fc+="[$n]aresample=44100,apad=pad_dur=0.6[a$n];"; n=$((n+1)); done
  cat=""; for i in $(seq 0 $((n-1))); do cat+="[a$i]"; done
  ffmpeg -v error -y "${args[@]}" -filter_complex "${fc}${cat}concat=n=$n:v=0:a=1,$CH,loudnorm=I=-16:TP=-2" -b:a 160k $V/$p/voix_essai_homme.mp3; echo "$p essai prêt"
done
echo "reprises finies $(date +%T)"
