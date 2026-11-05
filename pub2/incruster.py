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
    return bords_ecran(hull, zone.shape), zone


def ordonner(q):
    """Haut-gauche, haut-droit, bas-droit, bas-gauche."""
    c = q.mean(0)
    ang = np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0])
    q = q[np.argsort(ang)]  # sens horaire à l'écran (y vers le bas), en partant d'en haut à gauche
    k = np.argmin(q.sum(1))
    return np.roll(q, -k, axis=0).astype(np.float32)


def bords_ecran(hull, forme):
    """Les 4 coins « vifs » de l'écran : chaque bord est mesuré (droite ajustée sur sa partie rectiligne, loin des coins
    arrondis et de l'encoche), puis les 4 droites sont prolongées et croisées. Une approximation polygonale du contour,
    elle, coupe les coins arrondis en biais et pose l'image de travers."""
    remp = np.zeros(forme, np.uint8)
    cv2.fillConvexPoly(remp, hull, 255)
    cnts, _ = cv2.findContours(remp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pts = max(cnts, key=cv2.contourArea).reshape(-1, 2).astype(np.float32)
    boite = ordonner(cv2.boxPoints(cv2.minAreaRect(hull)))
    lignes = []
    for j in range(4):
        a, b = boite[j], boite[(j + 1) % 4]
        L = np.linalg.norm(b - a)
        u = (b - a) / L
        n = np.array([-u[1], u[0]])
        rel = pts - a
        s, d = rel @ u, rel @ n
        # Partie centrale du bord (les coins arrondis sont exclus), points proches du côté de la boîte.
        garde = (s > 0.18 * L) & (s < 0.82 * L) & (np.abs(d) < 0.06 * L + 6)
        sel = pts[garde]
        if len(sel) < 10:
            lignes.append((a, u))
            continue
        vx, vy, x0, y0 = cv2.fitLine(sel, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lignes.append((np.array([x0, y0]), np.array([vx, vy])))
    coins = []
    for j in range(4):  # coin j = croisement du bord j-1 et du bord j
        (p1, d1), (p2, d2) = lignes[j - 1], lignes[j]
        A = np.array([d1, -d2]).T
        if abs(np.linalg.det(A)) < 1e-6:
            coins.append(boite[j])
            continue
        t = np.linalg.solve(A, p2 - p1)
        coins.append(p1 + t[0] * d1)
    return ordonner(np.array(coins, np.float32))


def lisser(traj, sigma):
    """Lissage centré (sans retard) d'une suite de coins (n, 4, 2) ; les images sans écran sont interpolées."""
    traj = np.array(traj, np.float64)
    ok = ~np.isnan(traj[:, 0, 0])
    if ok.sum() == 0:
        return traj
    idx = np.arange(len(traj))
    for c in range(4):
        for x in range(2):
            traj[:, c, x] = np.interp(idx, idx[ok], traj[ok, c, x])
    if sigma <= 0:
        return traj
    r = int(3 * sigma) + 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(traj, ((r, r), (0, 0), (0, 0)), mode="edge")
    return np.stack([np.convolve(pad[:, c, x], k, "valid") for c in range(4) for x in range(2)], 1).reshape(traj.shape)


def sans_ilot(scr):
    """Efface l'îlot noir dessiné en haut de la capture : le téléphone filmé a déjà le sien (ou son encoche)."""
    h, w = scr.shape[:2]
    out = scr.copy()
    fond = np.median(scr[int(h * 0.005): int(h * 0.012), int(w * 0.3): int(w * 0.7)].reshape(-1, 3), 0)
    out[int(h * 0.008): int(h * 0.072), int(w * 0.31): int(w * 0.69)] = fond  # l'îlot : (0,33-0,67) × (0,017-0,064)
    return out


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


class Lecteur:
    """Lit les images d'une vidéo dans l'ordre (grab), sans chercher chaque image : bien plus rapide en 4K."""

    def __init__(self, chemin):
        self.cap = cv2.VideoCapture(chemin)
        self.pos, self.der = 0, (-1, None)

    def image(self, k):
        if k == self.der[0]:  # source moins rapide que la sortie : la même image sert deux fois
            return True, self.der[1].copy()
        if k < self.pos or k > self.pos + 120:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, k)
            self.pos = k
        while self.pos < k:
            self.cap.grab()
            self.pos += 1
        ok, img = self.cap.read()
        self.pos += 1
        if ok:
            self.der = (k, img)
        return ok, img


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
    ap.add_argument("--lissage", type=float, default=0.35, help="lissage centré des coins (0 = aucun ; écart = 3 × valeur, en images)")
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
         "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", a.sortie],
        stdin=subprocess.PIPE)
    if a.controle:
        os.makedirs(a.controle, exist_ok=True)

    # La détection se fait sur une image réduite (rapide en 4K) ; le détourage, lui, reste en pleine résolution.
    ech = min(1.0, 1280 / max(W, H))

    def analyser(img):
        petit = cv2.resize(img, None, fx=ech, fy=ech, interpolation=cv2.INTER_AREA) if ech < 1 else img
        r = coins_ecran(*masque_vert(petit))
        return None if r is None else (r[0] / ech, r[1])

    # 1er passage : les coins de chaque image ; puis lissage centré (le cadre ne traîne jamais derrière le téléphone).
    traj = []
    lec = Lecteur(a.video)
    for i in range(n_out):
        ok, img = lec.image(int(round((a.debut + i / a.ips) * ips_src)))
        if not ok:
            break
        r = analyser(img)
        traj.append(np.full((4, 2), np.nan) if r is None else r[0])
    n_out = len(traj)
    trouve = [not np.isnan(c[0, 0]) for c in traj]
    traj = lisser(traj, a.lissage * 3)

    perdu = 0
    lec = Lecteur(a.video)
    for i in range(n_out):
        t = a.debut + i / a.ips
        ok, img = lec.image(int(round(t * ips_src)))
        if not ok:
            break
        r = analyser(img) if trouve[i] else None
        if r is None:
            perdu += 1
            ff.stdin.write(img.tobytes())
            continue
        coins = traj[i].astype(np.float32)

        # Tout se passe dans le rectangle qui entoure l'écran (avec une marge).
        x0, y0 = np.floor(coins.min(0)).astype(int) - 24
        x1, y1 = np.ceil(coins.max(0)).astype(int) + 24
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        roi = img[y0:y1, x0:x1]
        c_roi = coins - np.float32([x0, y0])
        rh, rw = roi.shape[:2]

        # Zone de l'écran : le vert en pleine résolution, limité au quadrilatère ; les trous des repères (bouchés sur
        # l'image réduite) sont rajoutés ; les doigts, eux, restent devant.
        quad = np.zeros((rh, rw), np.uint8)
        cv2.fillConvexPoly(quad, np.round(c_roi).astype(np.int32), 255)
        quad = cv2.dilate(quad, np.ones((7, 7), np.uint8))
        zone = masque_vert(roi)[0] & quad
        petite = r[1]
        trous = cv2.bitwise_and(zone_ecran(petite), cv2.bitwise_not(petite))
        if cv2.countNonZero(trous):
            grand = cv2.resize(trous, (W, H), interpolation=cv2.INTER_NEAREST) if ech < 1 else trous
            zone = zone | (grand[y0:y1, x0:x1] & quad)

        k = int(round((a.ecran_debut + i / a.ips * a.ecran_vitesse) * a.ecran_ips))
        f = ecrans[max(0, min(k, len(ecrans) - 1))]
        if f not in cache:
            cache.clear()
            cache[f] = sans_ilot(cv2.imread(f, cv2.IMREAD_COLOR))
        scr = cache[f]
        h, w = scr.shape[:2]
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), c_roi)
        warp = cv2.warpPerspective(scr, M, (rw, rh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Alpha : le vert seulement, bord adouci.
        if a.plein:  # écran sans rien devant (repères de suivi) : tout le quadrilatère, un peu rentré
            alpha = np.zeros((rh, rw), np.uint8)
            cv2.fillConvexPoly(alpha, np.round(c_roi).astype(np.int32), 255)
            alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8))
        else:
            alpha = zone
        alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2).astype(np.float32)[..., None] / 255

        # Reflets : la luminosité du vert d'origine, centrée, ajoutée légèrement.
        lum = roi[..., 1].astype(np.float32)
        moy = lum[zone > 0].mean() if cv2.countNonZero(zone) else 128
        refl = np.clip((lum - moy) * a.reflet, -40, 60)[..., None]
        comp = np.clip(warp.astype(np.float32) + refl, 0, 255)

        # Neutralise le liseré vert autour de l'écran (despill) : vert ramené au max(rouge, bleu).
        bord = cv2.dilate(zone, np.ones((9, 9), np.uint8)) & ~cv2.erode(zone, np.ones((5, 5), np.uint8))
        res = roi.astype(np.float32)
        g = res[..., 1]
        lim = np.maximum(res[..., 0], res[..., 2])
        res[..., 1] = np.where(bord > 0, np.minimum(g, lim + 8), g)

        out = img.copy()
        out[y0:y1, x0:x1] = (comp * alpha + res * (1 - alpha)).astype(np.uint8)
        ff.stdin.write(out.tobytes())
        if a.controle and i % int(a.ips) == 0:
            cv2.imwrite(os.path.join(a.controle, f"{i:05d}.jpg"), out)
    ff.stdin.close()
    ff.wait()
    print(f"{a.sortie} : {n_out} images, écran perdu sur {perdu}")


if __name__ == "__main__":
    main()
