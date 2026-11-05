"""Monte une pub Diktéo de bout en bout : plans, écran incrusté, titres, voix, musique, bruitages.

Usage : python monter.py <nom de la pub> [--brouillon]   (les pubs sont décrites dans pubs.py)

Étapes :
1. les plans « incrust » passent par incruster.py (écran de Diktéo posé dans le téléphone à écran vert) ;
2. chaque plan est lu, recadré au format (zoom doux d'un point à un autre), étalonné chaud et légèrement granuleux ;
3. les titres (titres.html) sont rendus en PNG transparents et posés par-dessus ;
4. le son : musique coupée sur les mesures, voix off, bruitages, musique baissée sous la voix, -16 LUFS.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import wave

import cv2
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(ICI)
TMP = os.path.join(ICI, "tmp")
OUT = os.path.join(VIDEO, "out", "pub2")
ECRAN = os.path.join(ICI, "ecran", "sombre")
CLIPS = os.path.join(ICI, "clips")
SFX = os.path.join(VIDEO, "son", "sfx")
MUSIQUE = os.path.join(VIDEO, "assets", "musique", "promo-drop.mp3")
IPS = 30


def sh(*cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"échec : {' '.join(map(str, cmd))[:300]}\n{r.stderr[-2000:]}")
    return r


# ——— Étalonnage : chaud, noirs relevés, contraste doux, un peu désaturé ———
def luts():
    x = np.arange(256) / 255.0
    s = x + 0.10 * np.sin(np.pi * x) * (x - 0.5) * 2  # courbe en S douce
    base = 0.035 + 0.94 * np.clip(s, 0, 1)            # noirs relevés, blancs adoucis
    r = np.clip(base * 1.045 + 0.008, 0, 1)
    g = np.clip(base * 1.0, 0, 1)
    b = np.clip(base * 0.92 + 0.012, 0, 1)
    return [(c * 255).astype(np.uint8) for c in (b, g, r)]


LUT = luts()


def etalonner(img, sat=0.9):
    out = np.dstack([cv2.LUT(img[..., k], LUT[k]) for k in range(3)])
    if sat != 1:
        hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] *= sat
        out = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    return out


def adoucir(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cadrer(img, W, H, cx, cy, z):
    """Recadre l'image source au format W×H, centrée sur (cx, cy) en proportion, zoom z (1 = remplit juste)."""
    h, w = img.shape[:2]
    s = max(W / w, H / h) * z
    # Le centre demandé, borné pour ne jamais montrer de bord noir.
    vx = min(max(cx * w * s, W / 2), w * s - W / 2)
    vy = min(max(cy * h * s, H / 2), h * s - H / 2)
    M = np.float32([[s, 0, W / 2 - vx], [0, s, H / 2 - vy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)


def ajuster(img, W, H, z, cache={}):
    """Toute l'image source au centre (sans recadrage), sur un fond flouté tiré d'elle-même : pour une vidéo
    verticale dans un format carré ou horizontal."""
    h, w = img.shape[:2]
    s = min(W / w, H / h) * z
    fw, fh = int(w * s), int(h * s)
    fg = cv2.resize(img, (fw, fh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    fond = cadrer(cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA), W, H, 0.5, 0.5, 1.15)
    fond = cv2.GaussianBlur(fond, (0, 0), 28)
    out = (fond.astype(np.float32) * 0.45).astype(np.uint8)
    x0, y0 = (W - fw) // 2, (H - fh) // 2
    ax0, ay0, ax1, ay1 = max(0, x0), max(0, y0), min(W, x0 + fw), min(H, y0 + fh)
    out[ay0:ay1, ax0:ax1] = fg[ay0 - y0: ay1 - y0, ax0 - x0: ax1 - x0]
    return out


class Lecteur:
    """Lit une vidéo à une cadence quelconque, sans revenir en arrière."""

    def __init__(self, chemin):
        self.cap = cv2.VideoCapture(chemin)
        self.ips = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos, self.img = -1, None

    def image(self, t):
        k = min(int(round(t * self.ips)), self.n - 1)
        if k < self.pos:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, k)
            self.pos = k - 1
        while self.pos < k:
            ok = self.cap.grab()
            if not ok:
                break
            self.pos += 1
        ok, img = self.cap.retrieve()
        if ok:
            self.img = img
        return self.img


def plan_incruste(p):
    """Pré-rend le plan avec l'écran incrusté (mis en cache selon ses réglages)."""
    cle = hashlib.md5(json.dumps({**{k: p.get(k) for k in ("src", "debut", "duree", "ecran_debut", "ecran_vitesse", "plein", "reflet")},
                                  "ecran": p.get("ecran", ECRAN)}, sort_keys=True).encode()).hexdigest()[:10]
    sortie = os.path.join(TMP, f"incr_{p['src']}_{cle}.mp4")
    if not os.path.exists(sortie):
        cmd = [sys.executable, os.path.join(ICI, "incruster.py"), os.path.join(CLIPS, p["src"] + ".mp4"), p.get("ecran", ECRAN), sortie,
               "--debut", str(p["debut"]), "--duree", str(p["duree"] * p.get("vitesse", 1) + 0.1), "--ips", str(IPS),
               "--ecran-debut", str(p["ecran_debut"]), "--ecran-vitesse", str(p.get("ecran_vitesse", 1) / p.get("vitesse", 1)),
               "--reflet", str(p.get("reflet", 0.18))]
        if p.get("plein"):
            cmd.append("--plein")
        sh(*cmd)
    return sortie


def images_ecran():
    return sorted(f for f in os.listdir(ECRAN) if f.endswith(".png"))


def fond_ecran(W, H, cache={}):
    if (W, H) not in cache:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.55) / H) ** 2)
        lueur = np.clip(1 - d / 0.62, 0, 1) ** 2
        fond = np.zeros((H, W, 3), np.float32)
        fond[:] = (18, 20, 14)  # BGR du fond sombre du thème
        fond += lueur[..., None] * np.array([15, 101, 232], np.float32) * 0.42
        cache[(W, H)] = np.clip(fond, 0, 255).astype(np.uint8)
    return cache[(W, H)]


def rendu_ecran(W, H, t_ecran, z, noms, cache={}):
    """L'écran de l'appli en grand, coins arrondis, ombre et lueur orange sur fond sombre."""
    k = max(0, min(int(round(t_ecran * 30)), len(noms) - 1))
    if k not in cache:
        cache.clear()
        cache[k] = cv2.imread(os.path.join(ECRAN, noms[k]), cv2.IMREAD_COLOR)
    scr = cache[k]
    h0 = H * 0.86 * z if H >= W else H * 0.92 * z
    s = h0 / scr.shape[0]
    sw, shh = int(scr.shape[1] * s), int(h0)
    scr = cv2.resize(scr, (sw, shh), interpolation=cv2.INTER_AREA)
    out = fond_ecran(W, H).copy()
    x0, y0 = (W - sw) // 2, int((H - shh) * 0.5)
    r = int(sw * 0.085)
    masque = np.zeros((shh, sw), np.uint8)
    cv2.rectangle(masque, (r, 0), (sw - r, shh), 255, -1)
    cv2.rectangle(masque, (0, r), (sw, shh - r), 255, -1)
    for cx, cy in ((r, r), (sw - r, r), (r, shh - r), (sw - r, shh - r)):
        cv2.circle(masque, (cx, cy), r, 255, -1, cv2.LINE_AA)
    # Ombre portée douce.
    ombre = np.zeros((H, W), np.float32)
    xs, ys = max(0, x0), max(0, y0 + 30)
    sub = masque[: H - ys, : W - xs] if ys < H and xs < W else masque[:0, :0]
    ombre[ys: ys + sub.shape[0], xs: xs + sub.shape[1]] = sub / 255.0
    ombre = cv2.GaussianBlur(ombre, (0, 0), 40) * 0.7
    out = (out.astype(np.float32) * (1 - ombre[..., None])).astype(np.uint8)
    # Pose de l'écran (rogné si plus grand que l'image).
    ax0, ay0 = max(0, x0), max(0, y0)
    ax1, ay1 = min(W, x0 + sw), min(H, y0 + shh)
    a = masque[ay0 - y0: ay1 - y0, ax0 - x0: ax1 - x0].astype(np.float32)[..., None] / 255
    zone = out[ay0:ay1, ax0:ax1].astype(np.float32)
    src = scr[ay0 - y0: ay1 - y0, ax0 - x0: ax1 - x0].astype(np.float32)
    out[ay0:ay1, ax0:ax1] = (src * a + zone * (1 - a)).astype(np.uint8)
    return out


def vignette(W, H, force=0.32, cache={}):
    if (W, H, force) not in cache:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.414
        cache[(W, H, force)] = (1 - force * np.clip(d, 0, 1) ** 2.2)[..., None].astype(np.float32)
    return cache[(W, H, force)]


# ——— Voix : instants de chaque mot (parole répartie selon la longueur des mots) ———
def duree_wav(f):
    with wave.open(f) as w:
        return w.getnframes() / w.getframerate()


def parole(f):
    """Début et fin de la parole dans le fichier (seuil d'énergie)."""
    with wave.open(f) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    fen = int(sr * 0.02)
    e = np.array([np.sqrt(np.mean(a[i:i + fen] ** 2)) for i in range(0, len(a) - fen, fen)])
    seuil = e.max() * 0.08
    ix = np.where(e > seuil)[0]
    return (ix[0] * fen / sr, (ix[-1] + 1) * fen / sr) if len(ix) else (0, len(a) / sr)


def mots_cales(texte, wavf, t0, accents=()):
    d, f = parole(wavf)
    mots = texte.split()
    poids = [len(m.strip(".,!?:;")) + 2 for m in mots]
    tot, acc, res = sum(poids), 0, []
    for m, p in zip(mots, poids):
        res.append({"w": m, "t": round(t0 + d + (f - d) * acc / tot - 0.04, 3), "accent": m.strip(".,!?:;").lower() in accents})
        acc += p
    return res


# ——— Son ———
def mixer(pub, duree, sortie):
    entrees, filtres, voies, n = [], [], [], 0
    # Musique : segments [début dans le morceau, fin, instant dans la pub], fondus de 30 ms.
    for (a, b, at) in pub.get("musique", []):
        entrees += ["-i", MUSIQUE]
        filtres.append(f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.03}:d=0.03,"
                       f"adelay={int(at * 1000)}:all=1,volume={pub.get('musique_db', -5)}dB[m{n}]")
        voies.append(f"[m{n}]"); n += 1
    nm = len(voies)
    if nm:
        filtres.append("".join(voies) + f"amix=inputs={nm}:normalize=0,afade=t=out:st={duree - pub.get('fondu', 0.8)}:d={pub.get('fondu', 0.8)}[mus]")
    vo = []
    for (f, at) in pub.get("vo", []):
        entrees += ["-i", f]
        filtres.append(f"[{n}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                       f"equalizer=f=3500:t=q:w=1:g=2.5,adelay={int(at * 1000)}:all=1,volume={pub.get('vo_db', 3)}dB[v{n}]")
        vo.append(f"[v{n}]"); n += 1
    if vo:
        filtres.append("".join(vo) + f"amix=inputs={len(vo)}:normalize=0,asplit=2[voix][cle]")
    fx = []
    for (nom, at, db) in pub.get("sfx", []):
        entrees += ["-i", os.path.join(SFX, nom)]
        filtres.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(at * 1000)}:all=1,volume={db}dB[s{n}]")
        fx.append(f"[s{n}]"); n += 1
    pistes = []
    if nm and vo:
        filtres.append("[mus][cle]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[musb]")
        pistes.append("[musb]")
    elif nm:
        pistes.append("[mus]")
    if vo:
        pistes.append("[voix]")
    pistes += fx
    filtres.append("".join(pistes) + f"amix=inputs={len(pistes)}:normalize=0,atrim=0:{duree},apad=whole_dur={duree}[pre]")
    graphe = ";".join(filtres)
    brut = sortie + ".brut.wav"
    sh("ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex", graphe, "-map", "[pre]", "-ar", "48000", brut)
    # Normalisation en deux passes : -16 LUFS, crêtes sous -4,5 dBTP (mesurées).
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", brut, "-af", "loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    sh("ffmpeg", "-v", "error", "-y", "-i", brut, "-af",
       f"loudnorm=I=-16:TP=-4.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
       f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,alimiter=limit=0.59:level=false", "-ar", "48000", sortie)
    os.remove(brut)


def main():
    sys.path.insert(0, ICI)
    from pubs import PUBS

    ap = argparse.ArgumentParser()
    ap.add_argument("nom")
    ap.add_argument("--brouillon", action="store_true", help="demi-résolution, plus rapide")
    ap.add_argument("--sans-titres", action="store_true")
    a = ap.parse_args()
    global ECRAN
    pub = PUBS[a.nom]()
    ECRAN = pub.get("ecran", ECRAN)  # film de l'écran du métier de la pub
    W, H = pub["format"]
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    # Durées et instants des plans.
    t, plans = 0.0, []
    for p in pub["plans"]:
        p = dict(p, t0=t)
        t += p["duree"]
        plans.append(p)
    duree = round(t, 3)

    # Titres.
    dossier_titres = os.path.join(TMP, f"titres_{a.nom}")
    if not a.sans_titres:
        spec = {"l": W, "h": H, "duree": duree, "calques": pub["titres"]}
        sf = os.path.join(TMP, f"titres_{a.nom}.json")
        ancien = open(sf, encoding="utf-8").read() if os.path.exists(sf) else ""
        neuf = json.dumps(spec, ensure_ascii=False, indent=1)
        if neuf != ancien or not os.path.isdir(dossier_titres):
            open(sf, "w", encoding="utf-8").write(neuf)
            for f in os.listdir(dossier_titres) if os.path.isdir(dossier_titres) else []:
                os.remove(os.path.join(dossier_titres, f))
            print("titres…", flush=True)
            sh("node", os.path.join(ICI, "rendre-titres.mjs"), sf, dossier_titres, str(IPS), cwd=ICI)

    # Son.
    son = os.path.join(TMP, f"son_{a.nom}.wav")
    print("son…", flush=True)
    mixer(pub, duree, son)

    # Image.
    fw, fh = (W // 2, H // 2) if a.brouillon else (W, H)
    sortie = os.path.join(OUT, f"{a.nom}{'_brouillon' if a.brouillon else ''}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{fw}x{fh}", "-r", str(IPS), "-i", "-",
                           "-i", son, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow" if not a.brouillon else "veryfast",
                           "-crf", "17" if not a.brouillon else "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", "-shortest", sortie], stdin=subprocess.PIPE)
    noms = images_ecran()
    vig = vignette(W, H, pub.get("vignette", 0.32))
    rng = np.random.default_rng(7)
    lecteurs = {}
    n_tot = int(round(duree * IPS))
    print(f"images : {n_tot}", flush=True)
    for i in range(n_tot):
        ti = i / IPS
        p = next((q for q in plans if q["t0"] <= ti + 1e-6 < q["t0"] + q["duree"]), plans[-1])
        u = (ti - p["t0"]) / p["duree"]
        z = p.get("z0", 1.0) + (p.get("z1", p.get("z0", 1.0)) - p.get("z0", 1.0)) * adoucir(u) if p.get("lisse", True) else \
            p.get("z0", 1.0) + (p.get("z1", p.get("z0", 1.0)) - p.get("z0", 1.0)) * u
        # Coup de zoom à l'entrée du plan (« punch »).
        if p.get("punch"):
            z *= 1 + p["punch"] * (1 - adoucir((ti - p["t0"]) / 0.3))
        cx = p.get("cx", 0.5) + (p.get("cx1", p.get("cx", 0.5)) - p.get("cx", 0.5)) * adoucir(u)
        cy = p.get("cy", 0.5) + (p.get("cy1", p.get("cy", 0.5)) - p.get("cy", 0.5)) * adoucir(u)
        typ = p["type"]
        if typ in ("clip", "incrust"):
            src = plan_incruste(p) if typ == "incrust" else os.path.join(CLIPS, p["src"] + ".mp4")
            if src not in lecteurs:
                lecteurs[src] = Lecteur(src)
            local = (ti - p["t0"]) * p.get("vitesse", 1)
            img = lecteurs[src].image(local if typ == "incrust" else p["debut"] + local)
            img = ajuster(img, W, H, z) if p.get("ajuste") else cadrer(img, W, H, cx, cy, z)
            img = etalonner(img, p.get("sat", 0.9))
        elif typ == "ecran":
            img = rendu_ecran(W, H, p["ecran_debut"] + (ti - p["t0"]) * p.get("ecran_vitesse", 1), z, noms)
        else:  # noir : la carte de fin est dessinée par les titres
            img = fond_ecran(W, H).copy()
        f = img.astype(np.float32) * vig
        if not a.sans_titres:
            tp = os.path.join(dossier_titres, f"t_{i:05d}.png")
            ov = cv2.imread(tp, cv2.IMREAD_UNCHANGED)
            if ov is not None:
                if ov.ndim == 2:
                    ov = cv2.cvtColor(ov, cv2.COLOR_GRAY2BGRA)
                al = ov[..., 3:4].astype(np.float32) / 255 if ov.shape[2] == 4 else np.ones((H, W, 1), np.float32)
                f = ov[..., :3].astype(np.float32) * al + f * (1 - al)
        f += rng.normal(0, pub.get("grain", 3.2), (H, W, 1)).astype(np.float32)
        img = np.clip(f, 0, 255).astype(np.uint8)
        if a.brouillon:
            img = cv2.resize(img, (fw, fh), interpolation=cv2.INTER_AREA)
        ff.stdin.write(img.tobytes())
        if i % 60 == 0:
            print(f"  {i}/{n_tot}", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"OK : {sortie} ({duree:.2f} s)")


if __name__ == "__main__":
    main()
