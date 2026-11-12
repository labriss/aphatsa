#!/bin/bash
# Met le son libre de droits sur les pubs livrées : bruitages CC0 (bibliotheque.py), musique originale (composer.py),
# puis le mixage de chaque son.py (inchangé). Entrée : out/livraison/<nom>_muet.mp4 → sortie : out/livraison/<nom>.mp4
# Usage : bash son/libre/sonoriser.sh [pub ...]   (défaut : toutes celles dont la vidéo muette existe)
V=$(cd "$(dirname "$0")/../.." && pwd); L=$V/out/livraison; cd $V
[ -f ~/.claude/skills/sound-effects/sfx/manifest.json ] || python3 son/libre/bibliotheque.py
nom(){ case $1 in pub4) echo dikteo_pub4_boucle;; pub8) echo dikteo_pub8_pile;; pub10) echo dikteo_pub10_plan;; pub11) echo dikteo_pub11_tableau;;
  pub12) echo dikteo_pub12_rouleau;; pub13) echo dikteo_pub13_carreaux;; pub14) echo dikteo_pub14_froid;; pub15) echo dikteo_pub15_toit;;
  pub16) echo dikteo_pub16_mur;; pub17) echo dikteo_pub17_porte;; pub18) echo dikteo_pub18_copeau;; pub19) echo dikteo_pub19_tournee;; esac; }
for p in ${@:-pub4 pub8 pub10 pub11 pub12 pub13 pub14 pub15 pub16 pub17 pub18 pub19}; do
  n=$(nom $p); [ -f $L/${n}_muet.mp4 ] || { echo "pas de vidéo muette pour $p"; continue; }
  python3 son/libre/composer.py $p > /dev/null || { echo "ECHEC musique $p"; continue; }
  s=$p/son.py; [ $p = pub4 ] && s=$p/son_boucle.py
  mkdir -p $p/tmp; python3 $s $L/${n}_muet.mp4 $L/$n.mp4 > $p/tmp/son.log 2>&1 || { echo "ECHEC son $p"; tail -3 $p/tmp/son.log; continue; }
  # volume réseaux sociaux : -14 LUFS intégrés, crête vraie -1 dBTP (loudnorm en 2 passes, linéaire)
  J=$(ffmpeg -nostats -i $L/$n.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -v error -y -i $L/$n.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" \
    -ar 48000 -c:a aac -b:a 192k -movflags +faststart $L/$n.tmp.mp4 && mv $L/$n.tmp.mp4 $L/$n.mp4
  # crédits : la musique est une composition originale, pas Mixkit
  m="musique originale composée pour Diktéo (son/libre/composer.py, synthèse maison) — libre de droits"
  sed -i -E "s|^Musique : .*|Musique : $m|; s|Musique : Mixkit #[0-9]+, Mixkit Stock Music Free License\.|Musique : $m.|" $p/son/CREDITS.txt $p/son/SOUND.md 2>/dev/null
  echo "$p : $(ffmpeg -nostats -i $L/$n.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E ' I:' | tail -1 | xargs)"
done
