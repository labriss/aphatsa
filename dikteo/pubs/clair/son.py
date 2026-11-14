"""Son des pubs claires : musique originale (composer.py clair) + bruitages libres posés sur chaque action, sans voix.
python son.py <video_muette.mp4> <sortie.mp4>   (volume final -14 LUFS, crête -1 dBTP, comme sonoriser.sh)"""
import json, os, subprocess, sys
ICI = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.expanduser("~/.claude/skills/sound-effects/sfx")
VIDEO, SORTIE = sys.argv[1], sys.argv[2]
B = 60 / 96
A, PB, C, IA, ENV, F, FIN = 0, 4 * B, 8 * B, 15 * B, 21 * B, 26 * B, 31 * B   # mêmes repères que clair.src.html
MICRO, TAPE0, TAPE1 = C + .5 * B, C + 1.0, IA - .55
LIGNES = [IA + .5 * B + i * B for i in range(4)]
TOT, TAP = IA + 4.5 * B, ENV + B
SIGNE = TAP + .5 * B
# (instant, fichier, gain dB[, durée max])
POSE = [(.05, "impact/kenney-impact-impactsoft-heavy-000.ogg", -8)]
POSE += [(.3 + i * .32, "tick/fs384187.ogg", -20) for i in range(6)]
POSE += [(PB - .15, "transition/fs-816262-broomstick-whoosh-3-quiet-okm1.ogg", -10)]
POSE += [(PB + i * B, "pop/kenney-interface-pluck-001.ogg" if i < 2 else "pop/kenney-interface-pluck-002.ogg", -9) for i in range(3)]
POSE += [(PB + 3 * B, "whoosh/fs-683101-quick-woosh.ogg", -14)]
POSE += [(C - .1, "transition/fs-786514-swoosh-v2.ogg", -10), (MICRO - .05, "click/kenney-interface-click-001.ogg", -6)]
POSE += [(TAPE0, "typing/fs-416777-digital-typing-wav.ogg", -16, TAPE1 - TAPE0)]
POSE += [(IA, "ui-blip/kenney-ui-rollover2.ogg", -10)]
POSE += [(t, f"pop/kenney-interface-drop-00{1 + i % 3}.ogg", -7) for i, t in enumerate(LIGNES)]
POSE += [(TOT, "riser/fs-685256-riser-sound-effect-short-wav.ogg", -18, .7), (TOT + .7, "kit/pop.ogg", -8)]
POSE += [(ENV - .1, "whoosh/fs-683101-quick-woosh.ogg", -12), (TAP - .05, "click/kenney-interface-select-001.ogg", -5)]
POSE += [(SIGNE + .1, "ding/kenney-interface-confirmation-001.ogg", -5), (SIGNE + .5, "ding/fs-571513-soft-notifications-bell-ding-d.ogg", -11)]
POSE += [(F - .2, "transition/fs-683096-woosh.ogg", -10), (F, "impact/kenney-impact-impactsoft-heavy-001.ogg", -9), (F + 1.0, "ding/kenney-interface-glass-001.ogg", -9)]

# MUSIQUE=<fichier> et DEBUT_M=<secondes> choisissent un morceau (ex. Mixkit) et le passage ; défaut : la composition maison
MUS = os.environ.get("MUSIQUE", os.path.join(ICI, "musique", "mixkit-clair.mp3")); DM = float(os.environ.get("DEBUT_M", "0"))
entrees, chaines = ["-i", VIDEO, "-ss", f"{DM:.3f}", "-i", MUS], []
chaines.append(f"[1:a]atrim=0:{FIN:.3f},afade=t=in:d=0.04,afade=t=out:st={FIN - 1.2:.3f}:d=1.2,volume={os.environ.get('MUSIQUE_DB', '-4')}dB[m]")
for k, (t, f, g, *d) in enumerate(POSE):
    entrees += ["-i", os.path.join(SFX, f)]
    tr = f"atrim=0:{d[0]:.3f},afade=t=out:st={max(0, d[0] - .15):.3f}:d=0.15," if d else ""
    chaines.append(f"[{k + 2}:a]{tr}aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t * 1000)}|{int(t * 1000)}[s{k}]")
mix = "[m]" + "".join(f"[s{k}]" for k in range(len(POSE))) + f"amix=inputs={len(POSE) + 1}:normalize=0:duration=first,alimiter=limit=0.89[a]"
tmp = SORTIE + ".tmp.mov"
subprocess.run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex", ";".join(chaines + [mix]), "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "pcm_s16le", "-t", str(FIN), tmp], check=True)
out = subprocess.run(["ffmpeg", "-nostats", "-i", tmp, "-af", f"loudnorm=I={os.environ.get('CIBLE_LUFS', '-14')}:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
J = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
CIBLE = os.environ.get("CIBLE_LUFS", "-14")
af = (f"loudnorm=I={CIBLE}:TP=-1:LRA=11:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}"
      f":measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", SORTIE], check=True)
os.remove(tmp)
print(SORTIE)
