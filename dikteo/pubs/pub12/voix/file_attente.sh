#!/bin/bash
# File d'attente des rendus de la session pub 12/13 : chaque travail prend le verrou partagé seulement s'il est libre.
V=$(cd "$(dirname "$0")/../.." && pwd)  # le dossier video/ (sous Windows : /c/Users/Brisset/Desktop/plomberie-durand/video)
VENV2=~/outils/venv-voix2; VPY=$VENV2/bin/python; [ -x "$VPY" ] || VPY=$VENV2/Scripts/python  # macOS : bin/, Windows : Scripts/
if [ -z "${PY:-}" ]; then PY=python; [ "$(uname -s)" = Darwin ] && { PY=python3; [ -x ~/outils/venv-video/bin/python ] && PY=~/outils/venv-video/bin/python; }; fi  # macOS : venv-video ; Windows : python
command -v timeout >/dev/null || timeout(){ if command -v gtimeout >/dev/null; then gtimeout "$@"; else shift; "$@"; fi; }  # macOS : pas de timeout sans coreutils
prendre(){ until ( set -C; echo "$1" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 50; done; echo "verrou $1 $(date +%T)"; }
rendre(){ rm -f $V/RENDU_EN_COURS.lock; }
pub(){ # $1 dossier, $2 sortie
  prendre $1; cd $V/$1 && $PY build.py >/dev/null && rm -f final_silent*.mp4 && node ../pub4/render.mjs plan.html final_silent.mp4 60 8 4 > tmp/rendu.log 2>&1
  [ -f final_silent_silent.mp4 ] && mv -f final_silent_silent.mp4 final_silent.mp4; rendre
  $PY son.py final_silent.mp4 $2.mp4 2>&1 | tail -1
  ffmpeg -v error -y -i $2.mp4 -vf scale=720:-2 -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k -movflags +faststart ${2}_telephone.mp4
  ffmpeg -v error -y -i $2.mp4 -vf "fps=2,scale=150:-1,tile=10x4" -frames:v 1 tmp/planche.jpg; echo "$1 fini $(date +%T)"; }
# Chatterbox seul sur le PC ; abandon au bout de 90 min
prendre "pub12 voix"; cd $V/pub12/voix && timeout 5400 $VPY generer.py ref_A.wav A 2 > gen_A.log 2>&1; rendre; echo "voix chatterbox fini $(date +%T)"; grep "^ok\|charg" gen_A.log; PREFIXE=A_ $PY noter.py 2>&1 | grep -a "CHOIX"
pub pub13 dikteo_pub13_carreaux
pub pub12 dikteo_pub12_rouleau
