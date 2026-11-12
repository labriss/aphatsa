"""Les pubs Diktéo, décrites plan par plan (lues par monter.py). Scripts : scripts.md.

Données fictives uniquement (Mme Fontaine, 872,30 €, D-2026-0042 : l'exemple de la page d'accueil).
Écran : film de la page d'accueil capturé par capture-ecran.mjs dans ecran/sombre (30 i/s) :
micro 1,2 s · fin de dictée 6,2 · « Le devis se remplit » 6,2-7,2 · lignes 7,2 / 7,62 / 8,04 / 8,46 ·
« Valider et envoyer » touché 9,6 · « Envoyé à Mme Fontaine » 10,4.
Musique « Promo Drop » : drop à 5,71 s du morceau, mesure 1,579 s, dernier coup 106,77 s.
"""
import os

ICI = os.path.dirname(os.path.abspath(__file__))
VOIX = os.path.join(ICI, "voix")

PLIC = "fs-447910-plop.ogg"
DING = "fs-571513-soft-notifications-bell-ding-d.ogg"
WOOSH = "fs-683096-woosh.ogg"
SWOOSH = "fs-786514-swoosh-v2.ogg"
RISER = "fs-685256-riser-sound-effect-short-wav.ogg"
AMBIANCE = "fs-426767-apartment-room-tone-wav.ogg"
CLIC, POP, IMPACT = "click.ogg", "pop.ogg", "impact.ogg"

DROP, MESURE, DERNIER_COUP = 5.71, 1.579, 106.77


def sous_titre(pub, nom, texte, at, t1, accents=(), y=1180, taille=96, **kw):
    """Voix off + sous-titre mot par mot calé sur la parole."""
    from monter import mots_cales

    f = os.path.join(VOIX, pub, nom + ".wav")
    return f, at, {"type": "mots", "t0": at, "t1": t1, "y": y, "taille": taille,
                   "mots": mots_cales(texte, f, at, accents), **kw}


def ecran_t(plan_t0, ecran_debut, t_ecran):
    """Instant dans la pub où l'écran atteint t_ecran."""
    return plan_t0 + (t_ecran - ecran_debut)


# Ce qui change d'un métier à l'autre : l'accroche (pub A), le plan de fin (A, B, C), le film de l'écran, la notification
# (client et total TTC de l'exemple du métier, src/lib/trades.ts) et le défi de la pub D.
def _m(accroche, voix, texte, accent, fin, ecran, client, total, defi, bruit=None):
    return dict(accroche=accroche, voix=voix, texte=texte, accent=accent, bruit=bruit or [(IMPACT, 0.3, -14)], fin=fin,
                ecran=os.path.join(ICI, "ecran", ecran), client=client, total=total, defi=defi)


METIERS = {
    "plombier": _m(dict(src="9890450", debut=3.0, cx=0.50, cy=0.45), ("A", "v1"), "Une fuite.", "fuite",
                   dict(src="7584762", debut=2.0, cx=0.55, cy=0.45), "sombre", "Mme Fontaine", "872,30 €",
                   (("D", "d1"), "Défi : un devis de plombier, dicté en 5 secondes."), bruit=[(PLIC, 0.95, -4), (PLIC, 1.42, -9)]),
    "electricien": _m(dict(src="10664445", debut=2.0, cx=0.5, cy=0.42), ("E", "e2"), "Un tableau à refaire.", "refaire",
                      dict(src="34572318", debut=1.0, cx=0.6, cy=0.45), "electricien", "M. Lebrun", "905,30 €",
                      (("F", "d_electricien"), "Défi : un devis d'électricien, dicté en 5 secondes.")),
    "chauffagiste": _m(dict(src="35999366", debut=0.3, cx=0.62, cy=0.5), ("F", "a_chauffagiste"), "Des radiateurs tout froids.",
                       "froids", dict(src="7647713", debut=1.0, cx=0.62, cy=0.4), "chauffagiste", "Mme Garnier", "886,60 €",
                       (("F", "d_chauffagiste"), "Défi : un devis de chauffagiste, dicté en 5 secondes.")),
    "carreleur": _m(dict(src="24906850", debut=1.0, cx=0.45, cy=0.5), ("F", "a_carreleur"), "Une salle de bain à refaire.",
                    "refaire", dict(src="4729560", debut=2.0, cx=0.55, cy=0.5), "carreleur", "M. Petit", "1 734,70 €",
                    (("F", "d_carreleur"), "Défi : un devis de carreleur, dicté en 5 secondes.")),
    "peintre": _m(dict(src="6474155", debut=1.0, cx=0.45, cy=0.55), ("F", "a_peintre"), "Un séjour à repeindre.", "repeindre",
                  dict(src="9823147", debut=1.0, cx=0.6, cy=0.45), "peintre", "Mme Laurent", "1 958,00 €",
                  (("F", "d_peintre"), "Défi : un devis de peintre, dicté en 5 secondes.")),
    "menuisier": _m(dict(src="27876429", debut=3.0, cx=0.6, cy=0.55), ("F", "a_menuisier"), "Une porte d'entrée à changer.",
                    "changer", dict(src="7492603", debut=3.0, cx=0.5, cy=0.5), "menuisier", "M. Fabre", "2 073,50 €",
                    (("F", "d_menuisier"), "Défi : un devis de menuisier, dicté en 5 secondes.")),
    "macon": _m(dict(src="7830320", debut=1.0, cx=0.5, cy=0.5), ("F", "a_macon"), "Un mur à ouvrir.", "ouvrir",
                dict(src="39664848", debut=2.0, cx=0.5, cy=0.5), "macon", "M. Robin", "2 402,40 €",
                (("F", "d_macon"), "Défi : un devis de maçon, dicté en 5 secondes.")),
    "couvreur": _m(dict(src="5018919", debut=0.3, cx=0.5, cy=0.5), ("F", "a_couvreur"), "Une toiture à refaire.", "toiture",
                   dict(src="13361432", debut=2.0, cx=0.55, cy=0.5), "couvreur", "Mme Perrin", "3 064,60 €",
                   (("F", "d_couvreur"), "Défi : un devis de couvreur, dicté en 5 secondes.")),
    "serrurier": _m(dict(src="8292925", debut=2.0, cx=0.62, cy=0.5), ("F", "a_serrurier"), "Une serrure à changer.", "serrure",
                    dict(src="6182060", debut=2.0, cx=0.5, cy=0.45), "serrurier", "M. Mercier", "599,50 €",
                    (("F", "d_serrurier"), "Défi : un devis de serrurier, dicté en 5 secondes.")),
    "multiservice": _m(dict(src="8320780", debut=1.0, cx=0.62, cy=0.45), ("F", "a_multiservice"), "Plein de petits travaux.",
                       "petits", dict(src="7817161", debut=2.0, cx=0.5, cy=0.45), "multiservice", "Mme Chevalier", "259,60 €",
                       (("F", "d_multiservice"), "Défi : un devis de petits travaux, dicté en 5 secondes.")),
}


def notif(m, court=False):
    return f"{m['client']} a accepté le devis" + ("" if court else " D-2026-0042") + f" · {m['total']}"


def fin_plan(m, W, H, **k):
    """Plan de fin du métier ; une vidéo verticale dans un format plus large passe en mode « ajusté »."""
    import cv2
    c = cv2.VideoCapture(os.path.join(ICI, "clips", m["fin"]["src"] + ".mp4"))
    vertical = c.get(cv2.CAP_PROP_FRAME_HEIGHT) > c.get(cv2.CAP_PROP_FRAME_WIDTH)
    p = dict(type="clip", **{**m["fin"], **k})
    if vertical and W >= H:
        p["ajuste"] = True
    return p


def fin_parole(pub, nom):
    from monter import parole
    return parole(os.path.join(VOIX, pub, nom + ".wav"))[1]


# ——— A. TikTok / Reels / Shorts, 9:16, 23 s : « En parlant » ———
def pub_a(metier="plombier"):
    W, H = 1080, 1920
    m = METIERS[metier]
    plans = [
        dict(type="clip", duree=round(max(1.70, 0.3 + fin_parole(*m["voix"]) + 0.12), 2), z0=1.06, z1=1.18, **m["accroche"]),
        dict(type="incrust", src="32084122", debut=1.0, duree=2.60, ecran_debut=0.4, cx=0.62, cy=0.36, cy1=0.28, z0=1.05, z1=1.22),
        dict(type="incrust", src="12280180", debut=0.0, duree=4.00, ecran_debut=3.0, cx=0.48, cy=0.34, z0=1.10, z1=1.20),
        dict(type="ecran", duree=2.80, ecran_debut=7.0, z0=0.80, z1=0.86, punch=0.10),
        dict(type="incrust", src="27380944", debut=1.0, duree=2.90, ecran_debut=9.8, cx=0.48, cy=0.34, z0=1.10, z1=1.18),
        fin_plan(m, W, H, duree=3.98, z0=1.05, z1=1.14),
        dict(type="noir", duree=5.02),
    ]
    t = [0]
    for p in plans:
        t.append(t[-1] + p["duree"])
    # t = débuts des plans : 0 · 1,70 · 4,30 · 8,30 · 11,10 · 14,00 · 17,98 · fin 23,00
    vo, titres = [], []

    def st(*a, **k):
        f, at, calque = sous_titre("A", *a, **k)
        vo.append((f, at))
        titres.append(calque)

    f, at, calque = sous_titre(m["voix"][0], m["voix"][1], m["texte"], 0.3, t[1] - 0.05, accents=(m["accent"],), y=820, taille=120)
    vo.append((f, at))
    titres.append(calque)
    st("v2", "Et le devis, tu le fais quand ?", t[1] + 0.15, t[2] - 0.05, accents=("quand",), y=170, taille=88)
    st("v3", "Maintenant. En parlant.", t[2] + 0.15, t[2] + 2.6, accents=("parlant",), y=170, taille=88)
    st("v4", "Tout se range tout seul.", t[3] + 0.25, t[4] - 0.1, accents=("seul",), y=150, taille=80)
    st("v5", "Tu l'envoies.", t[4] + 0.15, t[5] - 0.1, accents=("l'envoies",), y=170, taille=88)
    st("v6", "Ton client accepte en ligne.", t[5] + 0.85, t[6] - 0.08, accents=("accepte",))
    for nom, at in (("v7", t[6] + 0.3), ("v8", t[6] + 1.2), ("v9", t[6] + 3.25)):
        vo.append((os.path.join(VOIX, "A", nom + ".wav"), at))

    titres += [
        {"type": "cta", "t0": t[5] + 0.2, "t1": t[6] - 0.06, "y": 1395, "texte": "Essayer gratuitement"},
        {"type": "flash", "t0": t[3], "t1": t[3] + 0.28, "force": 0.8},
        {"type": "notif", "t0": t[5] + 0.5, "t1": t[6] - 0.15, "y": 250, "titre": "Diktéo",
         "texte": notif(m)},
        {"type": "flash", "t0": t[6], "t1": t[6] + 0.35, "force": 0.55},
        {"type": "fin", "t0": t[6], "t1": t[7], "slogan": "Le devis dicté,<br><em>envoyé du chantier.</em>",
         "offre": "Gratuit pour 3 devis par mois<br>Sans carte bancaire", "offre_t": 1.2, "bouton": "Essayer gratuitement",
         "bouton_t": 2.6, "url": "diktéo.fr"},
    ]

    debut_musique = ecran_t(t[3], 7.0, 7.2) - DROP  # le drop tombe sur la 1re ligne du devis
    coupe = DROP + 5 * MESURE                          # 5 mesures après le drop, sur une barre
    reprise = DERNIER_COUP - MESURE                    # la dernière mesure du morceau
    a_reprise = t[6] - MESURE                          # le dernier coup tombe sur la carte de fin
    musique = [(0.0, min(coupe, a_reprise - debut_musique), debut_musique),
               (reprise, 111.0, a_reprise)]

    lignes = [ecran_t(t[3], 7.0, x) for x in (7.2, 7.62, 8.04, 8.46)]
    sfx = [(AMBIANCE, 0.0, -26), *m["bruit"], (WOOSH, t[1] - 0.35, -12),
           (CLIC, ecran_t(t[1], 0.4, 1.2), -6), (RISER, t[3] - 2.46, -14), (IMPACT, t[3], -5)]
    sfx += [(POP, x, -13) for x in lignes]
    sfx += [(CLIC, ecran_t(t[3], 7.0, 9.6), -5), (SWOOSH, t[4] - 0.12, -10), (SWOOSH, ecran_t(t[4], 9.8, 10.4), -9),
            (DING, t[5] + 0.5, -4), (WOOSH, t[6] - 0.4, -13), (POP, t[6] + 0.05, -8)]
    return {"format": (W, H), "plans": plans, "titres": titres, "vo": vo, "musique": musique, "sfx": sfx,
            "musique_db": -6, "vo_db": 4, "fondu": 0.9, "ecran": m["ecran"]}


def debuts(plans):
    t = [0.0]
    for p in plans:
        t.append(round(t[-1] + p["duree"], 3))
    return t


# ——— B. YouTube (in-stream), 16:9, 30 s : « Le soir / le chantier » (sans / avec, 1-2-3) ———
def pub_b(metier="plombier"):
    W, H = 1920, 1080
    m = METIERS[metier]
    debut_mus = 4.6                       # la musique part avec le jour (la camionnette)
    drop = debut_mus + DROP                # 10,31 : le téléphone apparaît
    fin = drop + 9 * MESURE                # 24,52 : la carte de fin, sur une barre
    plans = [
        dict(type="clip", src="6964002", debut=2.0, duree=3.2, cx=0.5, cy=0.40, z0=1.0, z1=1.08, sat=0.75),
        dict(type="clip", src="6614775", debut=4.0, duree=1.4, cx=0.5, cy=0.55, z0=1.0, z1=1.05, sat=0.75),
        dict(type="clip", src="9507651", debut=1.0, duree=2.4, cx=0.5, cy=0.5, z0=1.0, z1=1.08),
        dict(type="clip", src="9353913", debut=1.0, duree=round(drop - 7.0, 3), cx=0.45, cy=0.5, z0=1.0, z1=1.1),
        dict(type="incrust", src="32084122", debut=0.5, duree=3.59, ecran_debut=0.9, cx=0.62, cy=0.42, cx1=0.6, cy1=0.36, z0=1.0, z1=1.45),
        dict(type="ecran", duree=4.4, ecran_debut=6.6, z0=0.94, z1=1.0, punch=0.08),
        dict(type="incrust", src="32084122", debut=5.5, duree=3.3, ecran_debut=11.0, cx=0.40, cy=0.4, z0=1.15, z1=1.3),
        dict(type="clip", src="7584762", debut=6.0, duree=round(fin - 21.6, 3), cx=0.5, cy=0.5, z0=1.0, z1=1.08)
        if metier == "plombier" else fin_plan(m, W, H, duree=round(fin - 21.6, 3), z0=1.0, z1=1.08),
        dict(type="noir", duree=round(30.0 - fin, 3)),
    ]
    t = debuts(plans)
    vo, titres = [], []

    def st(*a, **k):
        f, at, calque = sous_titre("B", *a, **k)
        vo.append((f, at))
        titres.append(calque)

    bas = dict(y=850, taille=78)
    cote = dict(y=330, taille=80, gauche=80, droite=1100)
    st("b1", "21 h. Il te reste trois devis à faire.", 0.2, t[1] - 0.05, accents=("trois", "devis"), **bas)
    st("b2", "Comme hier soir.", t[1] + 0.15, t[2] - 0.05, accents=("hier",), **bas)
    st("b3", "Et si tu les faisais avant de repartir ?", t[2] + 0.15, t[3] - 0.05, accents=("avant",), **bas)
    st("b4", "Avec Diktéo, tu dictes ton chantier.", t[3] + 0.3, t[4] - 0.05, accents=("dictes",), **bas)
    st("b5", "Tu parles.", t[4] + 0.3, t[5] - 0.05, accents=("parles",), numero="1", **cote)
    st("b6", "Le devis se remplit tout seul.", t[5] + 0.3, t[6] - 0.05, accents=("seul",), numero="2", **cote)
    st("b7", "Ton client l'accepte en ligne.", t[6] + 0.4, t[7] - 0.05, accents=("l'accepte",), numero="3", **cote)
    st("b8", "Et toi, tu es déjà sur le chantier suivant.", t[7] + 0.15, t[8] - 0.05, accents=("suivant",), **bas)
    vo.append((os.path.join(VOIX, "B", "b9.wav"), t[8] + 0.45))
    titres += [
        {"type": "flash", "t0": t[4], "t1": t[4] + 0.3, "force": 0.7},
        {"type": "notif", "t0": t[6] + 0.3, "t1": t[7] - 0.15, "y": 60, "titre": "Diktéo", "texte": notif(m)},
        {"type": "flash", "t0": t[8], "t1": t[8] + 0.35, "force": 0.5},
        {"type": "fin", "t0": t[8], "t1": t[9], "slogan": "Le devis dicté, <em>envoyé du chantier.</em>",
         "offre": "Gratuit pour 3 devis par mois · Sans carte bancaire", "offre_t": 1.0, "bouton": "Essayer gratuitement",
         "bouton_t": 1.8, "url": "diktéo.fr"},
    ]
    musique = [(0.0, fin - MESURE - debut_mus, debut_mus), (DERNIER_COUP - MESURE, 111.0, fin - MESURE)]
    lignes = [ecran_t(t[5], 6.6, x) for x in (7.2, 7.62, 8.04, 8.46)]
    sfx = [(AMBIANCE, 0.0, -20), (WOOSH, t[2] - 0.35, -12), (IMPACT, t[4], -6), (CLIC, ecran_t(t[4], 0.9, 1.2), -6)]
    sfx += [(POP, x, -13) for x in lignes]
    sfx += [(CLIC, ecran_t(t[5], 6.6, 9.6), -5), (SWOOSH, ecran_t(t[5], 6.6, 10.4), -9), (DING, t[6] + 0.3, -4),
            (WOOSH, t[8] - 0.4, -13), (POP, t[8] + 0.05, -8)]
    return {"format": (W, H), "plans": plans, "titres": titres, "vo": vo, "musique": musique, "sfx": sfx,
            "musique_db": -7, "vo_db": 4, "fondu": 1.0, "vignette": 0.36, "ecran": m["ecran"]}


# ——— C. Bumper 6 s (YouTube / Google), 16:9 ou 9:16 : « Dicté. Envoyé. Accepté. » ———
def pub_c(vertical=False, metier="plombier"):
    W, H = (1080, 1920) if vertical else (1920, 1080)
    m = METIERS[metier]
    plans = [
        dict(type="incrust", src="12280180", debut=1.0, duree=1.6, ecran_debut=2.0, cx=0.48, cy=0.36, z0=1.12, z1=1.25)
        if vertical else
        dict(type="incrust", src="32084122", debut=1.0, duree=1.6, ecran_debut=2.0, cx=0.62, cy=0.4, z0=1.2, z1=1.4),
        dict(type="ecran", duree=1.7, ecran_debut=8.2, ecran_vitesse=2.0, z0=0.78 if vertical else 0.96,
             z1=0.82 if vertical else 1.02, punch=0.1),
        dict(type="clip", src="7584762", debut=8.0, duree=1.2, cx=0.55, cy=0.45, z0=1.05, z1=1.12) if metier == "plombier"
        else fin_plan(m, W, H, debut=m["fin"]["debut"] + 1.5, duree=1.2, z0=1.05, z1=1.12),
        dict(type="noir", duree=1.5),
    ]
    t = debuts(plans)
    taille, y = (150, 300) if vertical else (130, 760)

    def mot(w, t0, t1, **k):
        return {"type": "mots", "t0": t0, "t1": t1, "y": y, "taille": taille, "mots": [{"w": w, "t": t0, "accent": True}], **k}

    envoye = t[1] + (10.4 - 8.2) / 2.0  # l'écran est lu à vitesse 2 : « Envoyé » à 10,4 s du film
    vo = [(os.path.join(VOIX, "C", f"c{k}.wav"), at) for k, at in ((1, 0.25), (2, envoye), (3, t[2] + 0.2), (4, t[3] + 0.15))]
    titres = [
        mot("Dicté.", 0.2, t[1] - 0.05, **({"y": 130} if vertical else {"y": 470, "gauche": 60, "droite": 1240})),
        mot("Envoyé.", envoye, t[2] - 0.05, **({"y": 110} if vertical else {"y": 470, "gauche": 60, "droite": 1240})),
        {"type": "notif", "t0": t[2] + 0.02, "t1": t[3] - 0.05, "y": 250 if vertical else 60, "titre": "Diktéo",
         "texte": notif(m, court=True), "din": 0.2},
        {"type": "tampon", "t0": t[2] + 0.15, "t1": t[3] - 0.05, "y": 1150 if vertical else 640, "texte": "Accepté ✓"},
        {"type": "fin", "t0": t[3], "t1": t[4], "slogan": "Le devis dicté.", "offre": "Gratuit pour commencer",
         "offre_t": 0.4, "bouton": "Essayer gratuitement", "bouton_t": 0.6, "url": "diktéo.fr"},
    ]
    debut = DROP - t[1]  # le drop tombe sur l'écran du devis
    musique = [(debut, debut + t[3] - 1.0, 0.0), (DERNIER_COUP - 1.0, DERNIER_COUP + 1.6, t[3] - 1.0)]
    sfx = [(CLIC, 0.15, -6), (IMPACT, t[1], -6), (SWOOSH, envoye - 0.05, -9), (DING, t[2] + 0.02, -4), (POP, t[3] + 0.05, -8)]
    return {"format": (W, H), "plans": plans, "titres": titres, "vo": vo, "musique": musique, "sfx": sfx,
            "musique_db": -6, "vo_db": 5, "fondu": 0.25, "ecran": m["ecran"]}


# ——— D. Le défi chrono, 15 s, 1:1 (Google Ads, Demand Gen) ou 9:16 (Reels) ———
# Le chrono ne mesure que la dictée : les 5 secondes qu'il faut pour dire la phrase de l'exemple.
def pub_d(vertical=False, metier="plombier"):
    W, H = (1080, 1920) if vertical else (1080, 1080)
    m = METIERS[metier]
    (dpub, dnom), dtexte = m["defi"]
    d1 = round(max(3.0, 0.15 + fin_parole(dpub, dnom) + 0.12), 2)  # le défi est annoncé en entier avant « Top chrono »
    plans = [
        dict(type="incrust", src="27380944", debut=0.0, duree=d1, ecran_debut=0.0, ecran_vitesse=0.3, cx=0.48, cy=0.42,
             z0=1.0 if vertical else 1.0, z1=1.08 if vertical else 1.06, ajuste=not vertical),
        dict(type="incrust", src="12280180", debut=0.0, duree=5.0, ecran_debut=1.2, cx=0.48, cy=0.36,
             z0=1.08 if vertical else 1.0, z1=1.2 if vertical else 1.1, ajuste=not vertical),
        dict(type="ecran", duree=1.8, ecran_debut=6.2, z0=0.8 if vertical else 0.78, z1=0.84 if vertical else 0.8, punch=0.1),
        dict(type="ecran", duree=2.5, ecran_debut=8.0, z0=0.84 if vertical else 0.8, z1=0.88 if vertical else 0.84),
        dict(type="noir", duree=round(2.7 - (d1 - 3.0), 2)),  # toujours 15 s en tout
    ]
    t = debuts(plans)
    vo, titres = [], []
    haut = dict(y=120, taille=78) if vertical else dict(y=36, taille=60, marge=50)

    def st(*a, **k):
        f, at, calque = sous_titre("D", *a, **k)
        vo.append((f, at))
        titres.append(calque)

    f, at, calque = sous_titre(dpub, dnom, dtexte, 0.15, t[1] - 0.15, accents=("5", "secondes"), **haut)
    vo.append((f, at))
    titres.append(calque)
    st("d2", "Top chrono !", t[1] - 0.05, t[1] + 1.4, accents=("chrono",), **haut)
    st("d4", "Et le devis se remplit tout seul.", t[3] + 0.1, t[4] - 0.05, accents=("seul",), **haut)
    vo.append((os.path.join(VOIX, "D", "d3.wav"), t[2] + 0.12))
    vo.append((os.path.join(VOIX, "D", "d5.wav"), t[4] + 0.2))
    cx, cy = (700, 1500) if vertical else (790, 900)
    titres += [
        {"type": "chrono", "t0": 0.5, "t1": t[3] - 0.05, "x": cx, "y": cy, "depart": t[1], "arret": t[2]},
        {"type": "tampon", "t0": t[2] + 0.05, "t1": t[3] - 0.05, "y": 820 if vertical else 430, "texte": "Pari tenu ✓"},
        {"type": "flash", "t0": t[2], "t1": t[2] + 0.3, "force": 0.6},
        {"type": "fin", "t0": t[4], "t1": t[5], "slogan": "À toi de jouer.", "offre": "Gratuit pour commencer · Sans carte bancaire",
         "offre_t": 0.6, "bouton": "Essayer gratuitement", "bouton_t": 1.0, "url": "diktéo.fr"},
    ]
    debut_mus = t[1]                                 # la musique part au « Top chrono »
    a_reprise = t[4] - MESURE
    musique = [(0.0, a_reprise - debut_mus, debut_mus), (DERNIER_COUP - MESURE, DERNIER_COUP + 2.5, a_reprise)]
    lignes = [ecran_t(t[2], 6.2, x) for x in (7.2, 7.62)] + [ecran_t(t[3], 8.0, x) for x in (8.04, 8.46)]
    sfx = [(CLIC, t[1] + 0.02, -5), (IMPACT, t[2], -5), (DING, t[2] + 0.02, -6)]
    sfx += [(POP, x, -13) for x in lignes]
    sfx += [(CLIC, ecran_t(t[3], 8.0, 9.6), -5), (SWOOSH, ecran_t(t[3], 8.0, 10.4), -9), (POP, t[4] + 0.05, -8)]
    return {"format": (W, H), "plans": plans, "titres": titres, "vo": vo, "musique": musique, "sfx": sfx,
            "musique_db": -6, "vo_db": 4, "fondu": 0.6, "ecran": m["ecran"]}


PUBS = {"A": pub_a, "B": pub_b, "C": pub_c, "C_vertical": lambda: pub_c(True), "D": pub_d, "D_vertical": lambda: pub_d(True)}
for _mt in METIERS:  # A_electricien, B_electricien, C_vertical_electricien… pour chaque métier
    if _mt != "plombier":
        PUBS.update({f"A_{_mt}": (lambda x: lambda: pub_a(x))(_mt), f"B_{_mt}": (lambda x: lambda: pub_b(x))(_mt),
                     f"C_{_mt}": (lambda x: lambda: pub_c(False, x))(_mt), f"C_vertical_{_mt}": (lambda x: lambda: pub_c(True, x))(_mt),
                     f"D_{_mt}": (lambda x: lambda: pub_d(False, x))(_mt), f"D_vertical_{_mt}": (lambda x: lambda: pub_d(True, x))(_mt)})
