"""Compose des musiques exclusives avec ACE-Step 1.5 (MIT, usage commercial autorisé), sur CPU.
python composer_ace.py <sortie_dossier> <bpm> <durée> <graine> "<description>" [tonalité]"""
import os, sys, time
os.environ.setdefault("ACESTEP_CHECKPOINTS_DIR", "/home/user/outils/ace-modeles")
sys.path.insert(0, "/home/user/outils/ACE-Step-1.5")
import torch
torch.set_num_threads(os.cpu_count())
from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
out, bpm, dur, seed, caption = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
key = sys.argv[6] if len(sys.argv) > 6 else ""
os.makedirs(out, exist_ok=True)
t0 = time.time()
dit = AceStepHandler()
msg = dit.initialize_service(project_root="/home/user/outils/ACE-Step-1.5", config_path="acestep-v15-turbo", device="cpu")
print("init", round(time.time() - t0), "s", msg if isinstance(msg, str) else msg[0][:200], flush=True)
p = GenerationParams(caption=caption, lyrics="[Instrumental]", instrumental=True, bpm=bpm, keyscale=key, timesignature="4",
                     duration=dur, inference_steps=8, shift=3.0, seed=seed, thinking=False,
                     use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
c = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="wav")
t1 = time.time()
r = generate_music(dit, None, p, c, save_dir=out)
print("gen", round(time.time() - t1), "s", r.success, r.error if not r.success else [a["path"] for a in r.audios], flush=True)
