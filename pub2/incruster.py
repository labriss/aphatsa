"""Incruste l'écran de Diktéo dans un téléphone à écran vert filmé (vidéo Pexels).

Pour chaque image : on repère le vert, on trouve les 4 coins de l'écran (lissés dans le temps pour ne pas trembler),
on déforme la capture d'écran en perspective et on la pose seulement là où il y avait du vert : les doigts qui passent
devant restent devant. Les reflets du vrai écran (la luminosité du vert) sont remis par-dessus, discrètement, et le
liseré vert des bords est neutralisé.

Usage :
  python incruster.py <vidéo écran vert> <écran : image .png ou dossier d'images> <sortie.mp4>
         [--debut s] [--duree s] [--reflet 0.18] [--ips 30] [--controle dossier]

Le dossier d'images de l'écran est lu à sa cadence (--ecran-ips) à partir de --ecran-debut ; s'il est plus court,
la dernière image reste affichée.
"""
import argparse
import glob
import os
import subprocess

import cv2
import numpy as np


def masque_vert(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Vert de chroma : teinte 35-90 (sur 180), assez saturé et lumineux.
    m = cv2.inRange(hsv, (35, 70, 60), (90, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m, hsv[..., 1]


def coins_ecran(m, sat):
    """4 coins de la plus grande zone verte (haut-gauche, haut-droit, bas-droit, bas-gauche), ou None."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n < 2:
        return None
    # L'écran est la zone verte la plus « écran » : grande, pleine (pas éparpillée comme un feuillage) et saturée.
    meilleur, k = 0, 0
    for j in range(1, n):
        aire = st[j, cv2.CC_STAT_AREA]
        if aire < 0.005 * m.size:
            continue
        z = (lab == j).astype(np.uint8)
        cnts, _ = cv2.findContours(z, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        plein = aire / max(1.0, cv2.contourArea(cv2.convexHull(max(cnts, key=cv2.contourArea))))
        score = aire * plein ** 3 * (sat[z > 0].mean() / 255) ** 2
        if score > meilleur:
            meilleur, k = score, j
    if not k:
        return None
    zone = (lab == k).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(zone, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.convexHull(max(cnts, key=cv2.contourArea))
    peri = cv2.arcLength(hull, True)
    quad = None
    for eps in np.linspace(0.01, 0.08, 15):
        a = cv2.approxPolyDP(hull, eps * peri, True)
        if len(a) == 4:
            quad = a.reshape(4, 2).astype(np.float32)
            break
    if quad is None:  # écran aux coins très arrondis : on prend le rectangle tourné qui l'enveloppe
        quad = cv2.boxPoints(cv2.minAreaRect(hull)).astype(np.float32)
    # Ordre : haut-gauche, haut-droit, bas-droit, bas-gauche.
    s, d = quad.sum(1), np.diff(quad, axis=1).ravel()
    return np.array([quad[np.argmin(s)], quad[np.argmin(d)], quad[np.argmax(s)], quad[np.argmax(d)]], np.float32), zone


def zone_ecran(zone):
    """Zone de l'écran avec les petits trous bouchés (repères de suivi), sans boucher les doigts."""
    inv = cv2.bitwise_not(zone)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    out = zone.copy()
    for k in range(1, n):
        x, y, w, h, a = st[k]
        touche_bord = x == 0 or y == 0 or x + w >= zone.shape[1] or y + h >= zone.shape[0]
        if not touche_bord and a < 0.03 * cv2.countNonZero(zone):
            out[lab == k] = 255
    return out


def lire_ecrans(src):
    if os.path.isdir(src):
        fs = sorted(glob.glob(os.path.join(src, "*.png")) + glob.glob(os.path.join(src, "*.jpg")))
    else:
        fs = [src]
    return fs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("ecran")
    ap.add_argument("sortie")
    ap.add_argument("--debut", type=float, default=0)
    ap.add_argument("--duree", type=float, default=0)
    ap.add_argument("--reflet", type=float, default=0.18)
    ap.add_argument("--ips", type=float, default=30)
    ap.add_argument("--lissage", type=float, default=0.35, help="0 = suit chaque image, 1 = figé")
    ap.add_argument("--controle", default="")
    ap.add_argument("--ecran-debut", type=float, default=0, help="instant (s) de la séquence d'écran au début du plan")
    ap.add_argument("--ecran-ips", type=float, default=30, help="cadence des images d'écran")
    ap.add_argument("--ecran-vitesse", type=float, default=1, help="vitesse de lecture de l'écran")
    ap.add_argument("--plein", action="store_true", help="remplace tout l'écran (rien ne passe devant)")
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.video)
    ips_src = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_src = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duree = a.duree or (n_src / ips_src - a.debut)
    n_out = int(round(duree * a.ips))
    ecrans = lire_ecrans(a.ecran)
    cache = {}

    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(a.ips),
         "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", a.sortie],
        stdin=subprocess.PIPE)
    if a.controle:
        os.makedirs(a.controle, exist_ok=True)

    prec, perdu = None, 0
    for i in range(n_out):
        t = a.debut + i / a.ips
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * ips_src)))
        ok, img = cap.read()
        if not ok:
            break
        m, sat = masque_vert(img)
        r = coins_ecran(m, sat)
        if r is None:
            perdu += 1
            ff.stdin.write(img.tobytes())
            continue
        coins, zone = r
        coins = coins if prec is None else (a.lissage * prec + (1 - a.lissage) * coins)
        prec = coins

        k = int(round((a.ecran_debut + i / a.ips * a.ecran_vitesse) * a.ecran_ips))
        f = ecrans[max(0, min(k, len(ecrans) - 1))]
        if f not in cache:
            cache.clear()
            cache[f] = cv2.imread(f, cv2.IMREAD_COLOR)
        scr = cache[f]
        h, w = scr.shape[:2]
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), coins)
        warp = cv2.warpPerspective(scr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Alpha : le vert seulement (les doigts restent devant), trous des repères bouchés, bord adouci.
        if a.plein:  # écran sans rien devant (repères de suivi) : tout le quadrilatère, un peu rentré
            alpha = np.zeros((H, W), np.uint8)
            cv2.fillConvexPoly(alpha, coins.astype(np.int32), 255)
            alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8))
        else:
            alpha = zone_ecran(zone)
        alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2).astype(np.float32)[..., None] / 255

        # Reflets : la luminosité du vert d'origine, centrée, ajoutée légèrement.
        lum = img[..., 1].astype(np.float32)
        moy = lum[zone > 0].mean() if cv2.countNonZero(zone) else 128
        refl = np.clip((lum - moy) * a.reflet, -40, 60)[..., None]
        comp = np.clip(warp.astype(np.float32) + refl, 0, 255)

        # Neutralise le liseré vert autour de l'écran (despill) : vert ramené au max(rouge, bleu).
        bord = cv2.dilate(zone, np.ones((9, 9), np.uint8)) & ~cv2.erode(zone, np.ones((5, 5), np.uint8))
        res = img.astype(np.float32)
        g = res[..., 1]
        lim = np.maximum(res[..., 0], res[..., 2])
        res[..., 1] = np.where(bord > 0, np.minimum(g, lim + 8), g)

        out = (comp * alpha + res * (1 - alpha)).astype(np.uint8)
        ff.stdin.write(out.tobytes())
        if a.controle and i % int(a.ips) == 0:
            cv2.imwrite(os.path.join(a.controle, f"{i:05d}.jpg"), out)
    ff.stdin.close()
    ff.wait()
    print(f"{a.sortie} : {n_out} images, écran perdu sur {perdu}")


if __name__ == "__main__":
    main()
