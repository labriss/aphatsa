#!/bin/bash
# Variante serrée de la voix Chatterbox, lancée après les rendus 18 et 19 (Chatterbox doit être seul sur le PC).
V=$(cd "$(dirname "$0")/../.." && pwd)  # le dossier video/ (sous Windows : /c/Users/Brisset/Desktop/plomberie-durand/video)
VENV2=~/outils/venv-voix2; VPY=$VENV2/bin/python; [ -x "$VPY" ] || VPY=$VENV2/Scripts/python  # macOS : bin/, Windows : Scripts/
if [ -z "${PY:-}" ]; then PY=python; [ "$(uname -s)" = Darwin ] && { PY=python3; [ -x ~/outils/venv-video/bin/python ] && PY=~/outils/venv-video/bin/python; }; fi  # macOS : venv-video ; Windows : python
command -v timeout >/dev/null || timeout(){ if command -v gtimeout >/dev/null; then gtimeout "$@"; else shift; "$@"; fi; }  # macOS : pas de timeout sans coreutils
ATT="$1"  # fichier de sortie à attendre (« pub19 fini »)
until grep -q "pub19 fini" "$ATT" 2>/dev/null; do sleep 60; done
until ( set -C; echo "pub12 voix" > $V/RENDU_EN_COURS.lock ) 2>/dev/null; do sleep 50; done; echo "verrou pub12 voix $(date +%T)"
cd $V/pub12/voix && timeout 5400 $VPY generer.py ref_A.wav S 2 > gen_S.log 2>&1
[ "$(cat $V/RENDU_EN_COURS.lock)" = "pub12 voix" ] && rm -f $V/RENDU_EN_COURS.lock
echo "voix serrée finie $(date +%T)"; grep -a "^ok" gen_S.log
PREFIXE=S_ SORTIE=choix_serre.json $PY noter.py 2>&1 | grep -a "S_\|CHOIX"
