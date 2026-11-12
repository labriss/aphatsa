#!/usr/bin/env bash
# Rend les plans 3D de la pub en séquences d'images (renders/final/<plan>/).
# Usage : bash blender/rendre.sh [plan ...]   (par défaut : goutte cuisine_nuit cuisine_soir telephone)
set -euo pipefail
cd "$(dirname "$0")"
B="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
# BROUILLON=1 : petite image, peu d'échantillons, dans renders/brouillon (pour monter tout de suite).
if [ -n "${BROUILLON:-}" ]; then export APERCU=1; R=$(cd .. && pwd)/renders/brouillon; else R=$(cd .. && pwd)/renders/final; fi
for plan in "${@:-goutte cuisine_nuit cuisine_soir telephone}"; do
  for p in $plan; do
    ecran=-
    [ "$p" = telephone ] && ecran="$(cd .. && pwd)/renders/final/ecran"
    mkdir -p "$R/$p"
    start=$(date +%s)
    "$B" -b -P scenes.py -- "$p" anim "$R/$p/f" "$ecran" > "$R/$p.log" 2>&1
    echo "$p : $(( $(date +%s) - start )) s"
  done
done
