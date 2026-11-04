#!/usr/bin/env bash
# Rend les plans 3D de la pub en séquences d'images (renders/final/<plan>/).
# Usage : bash blender/rendre.sh [plan ...]   (par défaut : goutte cuisine_nuit cuisine_soir telephone)
set -euo pipefail
cd "$(dirname "$0")"
B="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
R=$(cd .. && pwd)/renders/final
for plan in "${@:-goutte cuisine_nuit cuisine_soir telephone}"; do
  for p in $plan; do
    ecran=-
    [ "$p" = telephone ] && ecran="$R/ecran"
    mkdir -p "$R/$p"
    start=$(date +%s)
    "$B" -b -P scenes.py -- "$p" anim "$R/$p/f" "$ecran" > "$R/$p.log" 2>&1
    echo "$p : $(( $(date +%s) - start )) s"
  done
done
