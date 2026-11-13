"""Pubs « claires » : un modèle (clair.src.html) × les démos de chaque métier (metiers.json, tiré de src/lib/trades.ts de fuiteo).
python build.py [metier ...] → <metier>.html (défaut : tous)"""
import base64, json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ICI, "clair.src.html"), encoding="utf-8").read()
faces = ""
for nom, fichier, poids in (("Archivo", "Archivo.ttf", "100 900"), ("PublicSans", "PublicSans.ttf", "100 900"), ("JBMono", "JetBrainsMono.ttf", "100 800")):
    b = base64.b64encode(open(os.path.join(ICI, "..", "pub4", "polices", fichier), "rb").read()).decode()
    faces += f"@font-face{{font-family:'{nom}';src:url(data:font/ttf;base64,{b}) format('truetype');font-weight:{poids};}}\n"
metiers = {m["id"]: m for m in json.load(open(os.path.join(ICI, "metiers.json"), encoding="utf-8"))}
for mid in sys.argv[1:] or metiers:
    html = src.replace("/*FONTS*/", faces).replace("/*DONNEES*/null", json.dumps(metiers[mid], ensure_ascii=False))
    open(os.path.join(ICI, mid + ".html"), "w", encoding="utf-8").write(html)
    print(mid)
