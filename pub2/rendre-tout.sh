#!/usr/bin/env bash
# Rend toutes les pubs (6 formats x 10 métiers) et les range par métier dans video/out/pub2/livraison/<métier>/.
# Usage : bash rendre-tout.sh [filtre]   (filtre : motif grep sur le nom, ex. « _peintre$ »)
cd "$(dirname "$0")"
L=../out/pub2/livraison
for nom in $(python -c "import pubs; print('\n'.join(pubs.PUBS))" | grep -E "${1:-.}"); do
  metier=plombier
  for m in $(python -c "import pubs; print(' '.join(pubs.METIERS))"); do [[ $nom == *_$m ]] && metier=$m; done
  mkdir -p "$L/$metier"
  if python monter.py "$nom" > "tmp/log_$nom.txt" 2>&1; then
    cp "../out/pub2/$nom.mp4" "$L/$metier/Dikteo_$nom.mp4"; echo "ok $nom"
  else
    echo "ECHEC $nom"
  fi
done
