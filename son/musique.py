# La piste musicale de chaque version de la pub, calée sur le découpage (voir decoupage.md, « Musique »).
# « Promo Drop » : 152 BPM, mesure = 1,579 s, drop à 5,71 s, dernière mesure à 105,19 s (dernier coup à 106,77 s).
# Chaque version est une suite de morceaux du fichier coupés sur des barres de mesure, avec des fondus de 30 ms
# aux raccords : le drop tombe sur les lignes du devis, le dernier coup sur la goutte du logo.
# Le MP3 est masterisé très fort (crêtes réelles à +3,2 dB une fois décodé) : on baisse de 5 dB en virgule flottante,
# avant d'écrire le fichier, pour ne jamais écrêter. Le volume final se règle au mixage (−14 LUFS).
# Usage : python son/musique.py <30|15|6> <sortie.wav>
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SRC = ICI / "assets" / "musique" / "promo-drop.mp3"
FIN = 111.5

# (instant dans la vidéo, début dans le morceau, fin dans le morceau, fondu d'entrée) ; durée de la version.
VERSIONS = {
    # Drop à 13,00 s ; on enchaîne sur la dernière mesure à 25,63 s, dernier coup à 27,21 s.
    "30": ([(7.29, 0.0, 18.34, 0.03), (25.63, 105.19, FIN, 0.03)], 30.0),
    # La musique entre pendant la plongée (4,3 s), drop à 6,00 s, dernier coup à 12,32 s.
    "15": ([(4.3, 4.01, 10.45, 0.25), (10.74, 105.19, FIN, 0.03)], 15.0),
    # Fin du roulement à 1,2 s, drop à 1,60 s, dernier coup à 4,76 s.
    "6": ([(1.2, 5.31, 7.29, 0.05), (3.18, 105.19, FIN, 0.03)], 6.0),
}

version, out = sys.argv[1], Path(sys.argv[2])
morceaux, duree = VERSIONS[version]
filtres, noms = [], []
for i, (instant, debut, fin, fondu) in enumerate(morceaux):
    longueur = fin - debut
    filtres.append(
        f"[0:a]atrim={debut}:{fin + 0.03},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={fondu},"
        f"afade=t=out:st={longueur}:d=0.03,adelay={round(instant * 1000)}:all=1[m{i}]"
    )
    noms.append(f"[m{i}]")
filtres.append(
    f"{''.join(noms)}amix=inputs={len(noms)}:normalize=0:duration=longest,apad,atrim=0:{duree},"
    f"afade=t=out:st={duree - 0.5}:d=0.5,volume=-5dB[m]"
)
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", ";".join(filtres),
                "-map", "[m]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(out)], check=True)
print(out)
