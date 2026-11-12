#!/bin/bash
# Rend les pubs livrées (pub 4 boucle, 8, 10 à 19) dans out/livraison/, une à la fois sous le verrou partagé.
# Usage : bash rendre_livraison.sh [pub ...]   (ex. pub13 pub19 ; par défaut toutes)
V=$(cd "$(dirname "$0")" && pwd); L=$V/out/livraison; mkdir -p $L
PY=${PY:-python3}; [ -x ~/outils/venv-video/bin/python ] && PY=~/outils/venv-video/bin/python
W=${WORKERS:-6}
nom(){ case $1 in pub4) echo boucle:dikteo_pub4_boucle;; pub8) echo pile:dikteo_pub8_pile;; pub10) echo plan:dikteo_pub10_plan;; pub11) echo tableau:dikteo_pub11_tableau;;
  pub12) echo plan:dikteo_pub12_rouleau;; pub13) echo plan:dikteo_pub13_carreaux;; pub14) echo chauffage:dikteo_pub14_froid;; pub15) echo toit:dikteo_pub15_toit;;
  pub16) echo mur:dikteo_pub16_mur;; pub17) echo porte:dikteo_pub17_porte;; pub18) echo plan:dikteo_pub18_copeau;; pub19) echo plan:dikteo_pub19_tournee;; esac; }  # bash 3 du Mac : pas de tableau associatif
prendre(){ until ( set -C; echo "$1" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 30; done; }
rendre(){ [ "$(cat $V/RENDU_EN_COURS.lock 2>/dev/null)" = "$1" ] && rm -f $V/RENDU_EN_COURS.lock; }
for p in ${@:-pub8 pub19 pub13 pub12 pub18 pub10 pub11 pub14 pub15 pub16 pub17 pub4}; do
  n=$(nom $p); page=${n%%:*}; sortie=${n##*:}; cd $V/$p; mkdir -p tmp
  $PY build.py $page > /dev/null || { echo "ECHEC build $p"; continue; }
  prendre "livraison $p"; t0=$(date +%s)
  rm -f muet*.mp4; node ../pub4/render.mjs $page.html muet.mp4 60 8 $W > tmp/rendu.log 2>&1; ok=$?
  rendre "livraison $p"
  [ -f muet_silent.mp4 ] && mv -f muet_silent.mp4 muet.mp4
  [ $ok = 0 ] && [ -f muet.mp4 ] || { echo "ECHEC rendu $p (voir $p/tmp/rendu.log)"; continue; }
  if [ $p = pub4 ]; then $PY son_boucle.py muet.mp4 $sortie.mp4 > tmp/son.log 2>&1; else $PY son.py muet.mp4 $sortie.mp4 > tmp/son.log 2>&1; fi || { echo "ECHEC son $p"; tail -3 tmp/son.log; continue; }
  cp -f $sortie.mp4 $L/
  ffmpeg -v error -y -i $sortie.mp4 -vf "fps=2,scale=150:-1,tile=10x4" -frames:v 1 tmp/planche.jpg
  echo "$p fini en $(( $(date +%s) - t0 )) s : $(ffmpeg -nostats -i $sortie.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E ' I:' | tail -1 | xargs)"
done
echo "LIVRAISON FINIE"
