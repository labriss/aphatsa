#!/bin/bash
# Refait les voix des pubs : prises (dicter.py), notation Whisper et choix (noter.py) → <pub>/voix/prises/choix.json.
# Voix retenue : Kokoro ff_siwis (VOIX=siwis). Variante voix d'homme : VOIX=pierre (ou tom) SORTIE=choix_homme.json,
# à essayer au mixage avec VOIX_CHOIX=$PWD/<pub>/voix/prises/choix_homme.json.
# Usage : bash son/voix/toutes.sh [pub ...]   (prérequis : bash son/voix/installer.sh)
V=$(cd "$(dirname "$0")/../.." && pwd); cd $V; PY=~/outils/venv-tts/bin/python
for p in ${@:-pub4 pub11 pub12 pub13 pub14 pub15 pub16 pub17 pub18 pub19}; do
  $PY son/voix/dicter.py $p/voix ${MOTEURS:-tom,pierre,siwis} 3 > $p/voix/gen.log 2>&1 || { echo "ECHEC voix $p"; continue; }
  VOIX=${VOIX:-siwis} $PY son/voix/noter.py $p/voix > $p/voix/note.log 2>&1 && tail -1 $p/voix/note.log
done
