"""La voix de l'artisan dans le mixage d'une pub (importé par les son.py) : il dicte ses lignes de devis.
Les prises viennent de son/voix/dicter.py, le choix de son/voix/noter.py (<pub>/voix/prises/choix.json, clé « choix »).
Sans choix.json (ou avec SANS_VOIX=1), rien ne change : voix muette, musique non baissée.

Traitée comme une vraie dictée au téléphone (même chaîne que la pub 12) : coupe des graves, présence, petite pièce,
compression douce ; l'air de la pièce dessous ; la musique s'efface sous la voix (ducking).
Chaque phrase commence avec son bandeau « TU DICTES » ; plus longue que sa place, elle est resserrée (au plus ×1,15) ;
elle ne commence jamais avant la fin de la précédente."""
import json
import os

import numpy as np
from scipy.ndimage import uniform_filter1d

CHAINE = ("highpass=f=110,lowpass=f=9000,equalizer=f=3000:t=q:w=1:g=3,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=90,aecho=0.8:0.4:19:0.10")
COUPE = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
AIR = "ambience/fs-329533-room-tone-in-an-apartment-livi.ogg"
CREDITS = {
    "tom": ("voix de synthèse Piper fr_FR-tom-medium, générée en local (poids AGPL-3.0, usage de la voix autorisé ; "
            "voix de synthèse, ne représente personne)", "AGPL-3.0 (modèle)"),
    "pierre": ("voix de synthèse Piper fr_FR-upmc-medium, locuteur « pierre » (données UPMC, CC BY-SA 4.0), générée en local", "CC BY-SA 4.0"),
    "siwis": ("voix de synthèse Kokoro-82M (Apache 2.0), voix ff_siwis (données SIWIS, CC BY 4.0), générée en local", "CC BY 4.0"),
}
RMS_VOIX = -17.0   # dBFS : la voix devant, la musique (déjà à -7 dB) dessous
BAISSE = .5        # la musique perd ~6 dB pendant que l'artisan parle


def poser_voix(ici, lire, n, sr, b, debuts, fin, journal, info, skill, avance=.08, tempo_max=1.15):
    """debuts : début de chaque phrase en temps de musique ; fin : le temps de l'événement qui suit la dernière.
    Renvoie (voix stéréo n×2, enveloppe de la musique n). Écrit <pub>/voix/calage.json."""
    voix, duck = np.zeros((n, 2), np.float32), np.ones(n, np.float32)
    f_choix = os.environ.get("VOIX_CHOIX", os.path.join(ici, "voix", "prises", "choix.json"))
    if os.environ.get("SANS_VOIX") == "1" or not os.path.exists(f_choix):
        return voix, duck
    tout = json.load(open(f_choix, encoding="utf-8"))
    ch = tout["choix"]
    credit, licence = CREDITS.get(tout.get("voix"), ("voix de synthèse générée en local", "?"))
    calage, fin_prec = [], 0.0
    for i, bt in enumerate(debuts):
        f = os.path.join(ici, "voix", "prises", ch.get(str(i), "-"))
        if not os.path.exists(f):
            continue
        t0 = max((bt + avance) * b, fin_prec + .12)
        place = (debuts[i + 1] * b - .1 if i + 1 < len(debuts) else fin * b + .2) - t0
        duree = len(lire(f, af=COUPE)) / sr
        tempo = min(tempo_max, max(1.0, duree / max(.1, place)))
        v = lire(f, af=f"{COUPE},atempo={tempo:.4f},{CHAINE}")
        v = v * (10 ** (RMS_VOIX / 20) / max(1e-6, np.sqrt((v ** 2).mean())))
        v = v / max(1.0, np.abs(v).max() / .95)
        a0 = int(t0 * sr)
        v = v[: n - a0]
        voix[a0:a0 + len(v)] += v
        fin_prec = t0 + len(v) / sr
        calage.append(dict(phrase=i, prise=ch[str(i)], debut_s=round(t0, 3), duree_s=round(len(v) / sr, 3), tempo=round(tempo, 3),
                           retard_s=round(t0 - (bt + avance) * b, 3), depasse_s=round(max(0.0, len(v) / sr - place), 3)))
        journal.append((t0, f"voix, phrase {i + 1}", ch[str(i)], credit, licence))
    if not calage:
        return voix, duck
    json.dump(dict(voix=tout.get("voix"), calage=calage), open(os.path.join(ici, "voix", "calage.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    # l'air de la pièce sous la voix : une dictée réelle n'est jamais posée sur un silence parfait
    if os.path.exists(os.path.join(skill, AIR)):
        for c in calage:
            d = c["duree_s"] + .5
            a = lire(os.path.join(skill, AIR), 2 + c["phrase"] * 3.1, d)
            t = np.arange(len(a)) / sr
            a = a * (np.minimum(1, t / .2) * np.minimum(1, np.maximum(0, (d - t) / .3)))[:, None]
            a = a / max(1e-6, np.abs(a).max()) * 10 ** (-30 / 20)
            a0 = max(0, int((c["debut_s"] - .2) * sr))
            a = a[: n - a0]
            voix[a0:a0 + len(a)] += a
            journal.append((c["debut_s"] - .2, "l'air de la pièce sous la dictée", AIR, info.get(AIR, {}).get("credit", AIR),
                            info.get(AIR, {}).get("license", "?")))
    # la musique s'efface sous la voix, avec une rampe douce (0,35 s)
    parle = np.zeros(n, np.float32)
    for c in calage:
        parle[int(c["debut_s"] * sr):int((c["debut_s"] + c["duree_s"]) * sr)] = 1
    parle = uniform_filter1d(parle, int(.35 * sr), mode="constant")
    duck = (1 - BAISSE * np.clip(parle * 1.5, 0, 1)).astype(np.float32)
    print("voix :", tout.get("voix"), json.dumps(calage, ensure_ascii=False))
    return voix, duck
