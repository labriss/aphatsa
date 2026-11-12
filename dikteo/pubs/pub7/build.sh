#!/bin/sh
# Le Soir du plombier : reconstruit le film d'une commande (sh video/pub7/build.sh).
set -e
LIB=${LIB:-$HOME/lemo-opuscar}; export LIB
HERE=$(cd "$(dirname "$0")" && pwd)
PY="$LIB/.venv/Scripts/python"; [ -x "$PY.exe" ] || [ -x "$PY" ] || PY="$LIB/.venv/bin/python"; export PYTHONIOENCODING=utf-8
sh "$HERE/tools/fonts.sh"
node "$HERE/tools/dump_timeline.mjs"
"$PY" "$HERE/music/score.py"
"$PY" "$HERE/mix.py"
cd "$LIB"
node core/render/video.mjs "$HERE" --fps 24 --workers 3 --size 1080x1920 --out "$HERE/out/video.mp4"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/out/master.mp4" 24 1
ffmpeg -loglevel error -i "$HERE/out/master.mp4" -c:v libx264 -preset slow -crf 23 -tune grain -c:a copy -movflags +faststart -y "$HERE/dikteo_pub7_film_muet.mp4"
node core/render/still.mjs "$HERE" 9.5 --size 1080x1920 --out "$HERE/out/still" --prefix p_ && cp "$HERE/out/still/p_9.5.jpg" "$HERE/poster.jpg"
echo "$HERE/dikteo_pub7_film_muet.mp4"
