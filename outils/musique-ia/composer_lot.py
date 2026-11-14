"""Compose un lot de musiques ACE-Step 1.5 (modèle chargé une fois). python composer_lot.py <dossier> <bpm> <durée>"""
import os, sys, time, json, shutil
os.environ.setdefault("ACESTEP_CHECKPOINTS_DIR", "/home/user/outils/ace-modeles"); os.environ.setdefault("ACESTEP_CPU_BF16", "1"); os.environ.setdefault("ACESTEP_VAE_ON_CPU", "1")
sys.path.insert(0, "/home/user/outils/ACE-Step-1.5")
import torch; torch.set_num_threads(os.cpu_count())
from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
out, bpm, dur = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]); os.makedirs(out, exist_ok=True)
STYLES = {
 "trap":      ("modern French rap trap beat, hard 808 bass slides, crisp rolling hi-hats, snappy claps, catchy bright bell melody, confident and motivating, polished, instrumental", "C minor", 7),
 "phonk":     ("drift phonk, aggressive distorted 808 cowbell melody, punchy kick, fast hi-hats, dark energetic TikTok trend, instrumental", "F minor", 11),
 "afro":      ("afrobeats, warm groovy log drum and shaker percussion, bouncy bass, bright marimba and guitar riff, happy sunny dance vibe, instrumental", "A minor", 23),
 "reggaeton": ("modern reggaeton, dembow rhythm, deep bass, catchy synth pluck lead, summer party energy, clean mix, instrumental", "D minor", 5),
 "boombap":   ("confident boom bap hip hop, dusty punchy drums, deep bass, funky electric piano chops, head-nodding groove, instrumental", "E minor", 31),
 "electropop":("upbeat electro pop, punchy four on the floor kick, groovy synth bass, bright catchy synth hook, claps, feel-good commercial energy, instrumental", "G major", 17),
 "funk":      ("modern funk groove, slap bass, tight drums, wah guitar, brass stabs, energetic and fun, instrumental", "E minor", 13),
 "epique":    ("hybrid trap cinematic, big punchy drums, deep 808, bold synth brass hits, rising energy, powerful advertising, instrumental", "D minor", 3),

 "chill_reggaeton": ("laid-back chill reggaeton, soft dembow groove, warm deep bass, mellow nylon guitar and soft plucked synth, relaxed confident summer evening vibe, smooth and clean, feeling of relief, instrumental", "A minor", 101),
 "lofi_reggaeton":  ("lo-fi reggaeton, relaxed dembow beat, warm sub bass, dreamy electric piano chords, soft vinyl texture, calm and reassuring, instrumental", "F major", 102),
 "afro_chill":      ("chill afrobeats, smooth groovy percussion, warm bass, soft guitar licks, mellow and positive, relaxed and confident, instrumental", "D minor", 103),
 "tropical":        ("tropical house slow groove, soft kick, marimba and steel drum melody, warm bass, sunny relaxed, feel-good solution vibe, instrumental", "C major", 104),
 "rnb_chill":       ("smooth chill R&B groove, laid-back drums, warm bass, silky electric piano, soft guitar, calm confident and modern, instrumental", "E minor", 105),
 "moombah_chill":   ("chill moombahton, relaxed latin groove, warm deep bass, soft brass and plucks, easygoing and positive, instrumental", "G minor", 106),
}
which = sys.argv[4:] or list(STYLES)
dit = AceStepHandler(); dit.initialize_service(project_root="/home/user/outils/ACE-Step-1.5", config_path="acestep-v15-turbo", device="cpu")
for spec in which:
    nom, _, sd = spec.partition(":"); cap, key, seed = STYLES[nom]; seed = int(sd) if sd else seed; nom = f"{nom}_{seed}" if sd else nom; t = time.time()
    p = GenerationParams(caption=cap, lyrics="[Instrumental]", instrumental=True, bpm=bpm, keyscale=key, timesignature="4", duration=dur,
                         inference_steps=8, shift=3.0, seed=seed, thinking=False, use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
    r = generate_music(dit, None, p, GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="wav"), save_dir=out)
    if r.success:
        shutil.move(r.audios[0]["path"], os.path.join(out, f"{nom}.wav")); json.dump({"caption": cap, "key": key, "seed": seed, "bpm": bpm}, open(os.path.join(out, f"{nom}.json"), "w"))
    print(nom, "OK" if r.success else "ECHEC " + str(r.error), round(time.time() - t), "s", flush=True)
