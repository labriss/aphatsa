# Analyse d'une pub vidéo pour l'étude des pubs qui marchent (video/recherche/pubs-qui-marchent.md).
# Pour chaque vidéo : une planche d'images (l'accroche détaillée, puis le reste), le texte dit (Whisper, en local)
# et le rythme du montage (instants des coupes).
# Usage : python analyser.py <dossier des vidéos> [nom ...]   → <nom>_planche.jpg et <nom>.json à côté de chaque vidéo
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DOSSIER = Path(sys.argv[1])
NOMS = sys.argv[2:] or [p.stem for p in sorted(DOSSIER.glob("*.mp4"))]
_whisper = None


def duree(v):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                                capture_output=True, text=True).stdout.strip() or 0)


def image(v, t, h=360):
    brut = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", "-vf", f"scale=-2:{h}",
                           "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(brut)).convert("RGB") if brut else None


def coupes(v):
    """Instants des changements de plan (détection de scène de ffmpeg)."""
    err = subprocess.run(["ffmpeg", "-i", str(v), "-vf", "select='gt(scene,0.3)',showinfo", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [round(float(l.split("pts_time:")[1].split()[0]), 2) for l in err.splitlines() if "pts_time:" in l]


def transcrire(v):
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("base", device="cpu", compute_type="int8")
    # Le son est extrait par ffmpeg (16 kHz mono) : la lecture audio intégrée à faster-whisper plante avec PyAV récent.
    import numpy as np
    brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(v), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                          capture_output=True).stdout
    audio = np.frombuffer(brut, dtype=np.float32)
    if len(audio) < 16000:
        return None, []
    # Sans le filtre de silence (VAD) : son moteur ONNX plante sur cette machine.
    # Sans reprise du texte précédent ni recherche en faisceau : plus rapide, et pas de boucle sur la musique.
    segs, info = _whisper.transcribe(audio, vad_filter=False, beam_size=1, condition_on_previous_text=False)
    return info.language, [(round(s.start, 1), round(s.end, 1), s.text.strip()) for s in segs]


def planche(v, d, sortie):
    instants = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0] + [t for t in range(4, int(d) + 1, 2)]
    instants = [t for t in instants if t < d - 0.05][:40]
    vignettes = [(t, image(v, t)) for t in instants]
    vignettes = [(t, im) for t, im in vignettes if im]
    if not vignettes:
        return
    w, h = vignettes[0][1].size
    cols = 8
    lignes = (len(vignettes) + cols - 1) // cols
    p = Image.new("RGB", (cols * w, lignes * (h + 22)), (20, 20, 20))
    dr = ImageDraw.Draw(p)
    try:
        f = ImageFont.truetype("arialbd.ttf", 16)
    except OSError:
        f = ImageFont.load_default()
    for i, (t, im) in enumerate(vignettes):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        p.paste(im.resize((w, h)), (x, y + 22))
        dr.text((x + 4, y + 2), f"{t:.1f} s", fill=(255, 200, 120), font=f)
    p.save(sortie, quality=85)


# Premier passage, rapide : planches et coupes de toutes les vidéos. Second passage : ce qui est dit.
for nom in NOMS:
    v, j = DOSSIER / f"{nom}.mp4", DOSSIER / f"{nom}.json"
    if j.exists():
        continue
    d = duree(v)
    planche(v, d, DOSSIER / f"{nom}_planche.jpg")
    c = coupes(v)
    res = {"nom": nom, "duree": round(d, 1), "coupes": c, "coupes_par_s": round(len(c) / d, 2) if d else 0}
    j.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(nom, round(d, 1), "s", len(c), "coupes", flush=True)
for nom in NOMS:
    j = DOSSIER / f"{nom}.json"
    res = json.loads(j.read_text(encoding="utf-8"))
    if "texte" in res:
        continue
    res["langue"], res["texte"] = transcrire(DOSSIER / f"{nom}.mp4")
    j.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(nom, res["langue"], len(res["texte"]), "phrases", flush=True)
