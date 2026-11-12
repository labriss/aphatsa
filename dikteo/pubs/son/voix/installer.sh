#!/bin/bash
# Installe les moteurs de voix (sans Hugging Face : tout vient de PyPI et des releases GitHub).
#  - piper-tts + voix françaises Piper re-publiées par sherpa-onnx (release « tts-models ») : tom, tjiho, upmc (pierre)
#  - kokoro-onnx + kokoro-v1.0.onnx / voices-v1.0.bin (release « model-files-v1.0 » de thewh1teagle/kokoro-onnx) : ff_siwis
#  - Whisper small (release « asr-models » de sherpa-onnx) pour noter.py
# Usage : bash son/voix/installer.sh   → ~/outils/venv-tts et ~/outils/tts (≈ 1,3 Go)
set -e
T=~/outils/tts; mkdir -p $T/kokoro; cd $T
[ -x ~/outils/venv-tts/bin/python ] || python3 -m venv ~/outils/venv-tts
~/outils/venv-tts/bin/pip install -q piper-tts kokoro-onnx sherpa-onnx soundfile numpy num2words
S=https://github.com/k2-fsa/sherpa-onnx/releases/download
for n in tom-medium upmc-medium tjiho-model1 tjiho-model2 tjiho-model3; do
  [ -d vits-piper-fr_FR-$n ] || curl -sSL $S/tts-models/vits-piper-fr_FR-$n.tar.bz2 | tar xj
done
[ -d sherpa-onnx-whisper-small ] || curl -sSL $S/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar xj
K=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do [ -f kokoro/$f ] || curl -sSL -o kokoro/$f $K/$f; done
echo "voix installées dans $T"
