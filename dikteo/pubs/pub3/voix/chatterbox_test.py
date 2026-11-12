import sys, time, torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
t0 = time.time()
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print("charge", round(time.time() - t0), "s", flush=True)
for i, (txt, ex) in enumerate([("Six heures cinquante-huit. Le client a juste une petite question.", 0.5),
                               ("Et puis... Diktéo. Tu dictes ton devis, il se fait tout seul.", 0.6)]):
    t0 = time.time()
    w = m.generate(txt, language_id="fr", exaggeration=ex, cfg_weight=0.5)
    torchaudio.save(f"v2/test_{i}.wav", w, m.sr)
    print("ok", i, round(time.time() - t0), "s", flush=True)
