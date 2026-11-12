#!/usr/bin/env bash
# Filme les 9 métiers du plan 8, un par temps de musique (0,3947 s) ; le dernier tient jusqu'à 24,05 s.
# Nombre d'images par métier : les bornes des temps arrondies à l'image (30 i/s).
set -euo pipefail
cd "$(dirname "$0")"
OUT=renders/final/metiers
for spec in electricien:12 chauffagiste:12 carreleur:12 peintre:11 menuisier:12 macon:12 couvreur:12 serrurier:12 multiservice:47; do
  m=${spec%%:*}; n=${spec##*:}
  if [ "$m" = multiservice ]; then from=0.35; else from=0.5; fi
  node capture-metier.mjs "$m" "$OUT/$m" "$n" "$from" 0.97
done
