#!/bin/bash
# Variante serrée de la voix Chatterbox, lancée après les rendus 18 et 19 (Chatterbox doit être seul sur le PC).
V=/c/Users/Brisset/Desktop/plomberie-durand/video
ATT="$1"  # fichier de sortie à attendre (« pub19 fini »)
until grep -q "pub19 fini" "$ATT" 2>/dev/null; do sleep 60; done
until ( set -C; echo "pub12 voix" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 50; done; echo "verrou pub12 voix $(date +%T)"
cd $V/pub12/voix && timeout 5400 ~/outils/venv-voix2/Scripts/python generer.py ref_A.wav S 2 > gen_S.log 2>&1
[ "$(cat $V/RENDU_EN_COURS.lock)" = "pub12 voix" ] && rm -f $V/RENDU_EN_COURS.lock
echo "voix serrée finie $(date +%T)"; grep -a "^ok" gen_S.log
PREFIXE=S_ SORTIE=choix_serre.json python noter.py 2>&1 | grep -a "S_\|CHOIX"
