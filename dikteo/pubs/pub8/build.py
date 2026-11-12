"""Incruste les polices en base64 : python build.py [nom] → <nom>.html (défaut : pile)"""
import base64
import os

ICI = os.path.dirname(os.path.abspath(__file__))
import sys
NOM = sys.argv[1] if len(sys.argv) > 1 else "pile"
src = open(os.path.join(ICI, NOM + ".src.html"), encoding="utf-8").read()
faces = ""
for nom, fichier, poids in (("Archivo", "Archivo.ttf", "100 900"), ("PublicSans", "PublicSans.ttf", "100 900"), ("JBMono", "JetBrainsMono.ttf", "100 800")):
    b = base64.b64encode(open(os.path.join(ICI, "..", "pub4", "polices", fichier), "rb").read()).decode()
    faces += f"@font-face{{font-family:'{nom}';src:url(data:font/ttf;base64,{b}) format('truetype');font-weight:{poids};}}\n"
open(os.path.join(ICI, NOM + ".html"), "w", encoding="utf-8").write(src.replace("/*FONTS*/", faces))
print("ok")
