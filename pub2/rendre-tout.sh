#!/usr/bin/env bash
# Rend toutes les pubs (6 formats x 10 métiers) et les range par métier dans video/out/pub2/livraison/<métier>/.
# Usage : bash rendre-tout.sh [filtre]   (filtre : motif grep sur le nom, ex. « _peintre$ »)
# Plusieurs rendus peuvent tourner en même temps : une pub déjà rendue ou en cours (verrou) est sautée.
cd "$(dirname "$0")"
L=../out/pub2/livraison
for nom in $(python -c "import pubs; print('\n'.join(pubs.PUBS))" | grep -E "${1:-.}"); do
  metier=plombier
  for m in $(python -c "import pubs; print(' '.join(pubs.METIERS))"); do [[ $nom == *_$m ]] && metier=$m; done
  mkdir -p "$L/$metier"
  [ -f "$L/$metier/Dikteo_$nom.mp4" ] && [ -z "$FORCER" ] && continue
  mkdir "tmp/verrou_$nom" 2>/dev/null || continue
  if python monter.py "$nom" > "tmp/log_$nom.txt" 2>&1; then
    cp "../out/pub2/$nom.mp4" "$L/$metier/Dikteo_$nom.mp4"; echo "ok $nom"
  else
    echo "ECHEC $nom"
  fi
  rmdir "tmp/verrou_$nom"
done
