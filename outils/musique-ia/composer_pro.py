"""Composition « pro » : ACE-Step 1.5 + LM 1.7B en mode réflexion (structure plus aboutie), plusieurs prises.
python composer_pro.py <dossier> <bpm> <durée> <tonalité> "<description>" graine1 graine2 ..."""
import os, sys, time, json, shutil
os.environ.setdefault("ACESTEP_CHECKPOINTS_DIR", "/home/user/outils/ace-modeles"); os.environ.setdefault("ACESTEP_CPU_BF16", "1"); os.environ.setdefault("ACESTEP_VAE_ON_CPU", "1")
sys.path.insert(0, "/home/user/outils/ACE-Step-1.5")
import torch; torch.set_num_threads(os.cpu_count())
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
out, bpm, dur, key, cap = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]; seeds = [int(s) for s in sys.argv[6:]]
os.makedirs(out, exist_ok=True)
dit = AceStepHandler(); dit.initialize_service(project_root="/home/user/outils/ACE-Step-1.5", config_path="acestep-v15-turbo", device="cpu")
lm = LLMHandler(); print("LM", lm.initialize(checkpoint_dir="/home/user/outils/ace-modeles", lm_model_path="acestep-5Hz-lm-1.7B", backend="pt", device="cpu", dtype=torch.bfloat16), flush=True)
for s in seeds:
    t = time.time()
    p = GenerationParams(caption=cap, lyrics="[Instrumental]", instrumental=True, bpm=bpm, keyscale=key, timesignature="4", duration=dur,
                         inference_steps=8, shift=3.0, seed=s, thinking=True, use_cot_metas=False, use_cot_caption=False, use_cot_language=False,
                         lm_temperature=float(os.environ.get("LM_TEMP", "0.85")))
    r = generate_music(dit, lm, p, GenerationConfig(batch_size=1, use_random_seed=False, seeds=[s], audio_format="wav"), save_dir=out)
    if r.success:
        shutil.move(r.audios[0]["path"], os.path.join(out, f"pro_{s}.wav")); json.dump({"caption": cap, "key": key, "seed": s, "bpm": bpm, "thinking": True}, open(os.path.join(out, f"pro_{s}.json"), "w"))
    print(s, "OK" if r.success else "ECHEC " + str(r.error)[:300], round(time.time() - t), "s", flush=True)
