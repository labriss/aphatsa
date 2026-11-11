#!/bin/bash
# File d'attente des rendus de la session pub 12/13 : chaque travail prend le verrou partagé seulement s'il est libre.
V=/c/Users/Brisset/Desktop/plomberie-durand/video
prendre(){ until ( set -C; echo "$1" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 50; done; echo "verrou $1 $(date +%T)"; }
rendre(){ rm -f $V/RENDU_EN_COURS.lock; }
pub(){ # $1 dossier, $2 sortie
  prendre $1; cd $V/$1 && python build.py >/dev/null && rm -f final_silent*.mp4 && node ../pub4/render.mjs plan.html final_silent.mp4 60 8 4 > tmp/rendu.log 2>&1
  [ -f final_silent_silent.mp4 ] && mv -f final_silent_silent.mp4 final_silent.mp4; rendre
  python son.py final_silent.mp4 $2.mp4 2>&1 | tail -1
  ffmpeg -v error -y -i $2.mp4 -vf scale=720:-2 -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k -movflags +faststart ${2}_telephone.mp4
  ffmpeg -v error -y -i $2.mp4 -vf "fps=2,scale=150:-1,tile=10x4" -frames:v 1 tmp/planche.jpg; echo "$1 fini $(date +%T)"; }
pub pub13 dikteo_pub13_carreaux
pub pub12 dikteo_pub12_rouleau
# Chatterbox seul sur le PC ; abandon s'il dépasse 15 min pour la première prise
prendre "pub12 voix"; cd $V/pub12/voix && timeout 5400 ~/outils/venv-voix2/Scripts/python generer.py ref_A.wav A 2 > gen_A.log 2>&1; rendre; echo "voix chatterbox fini $(date +%T)"; grep "^ok\|charg" gen_A.log
