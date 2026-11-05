"""Incruste les polices en base64 dans la page : python build.py → demo.html"""
import base64
import os

ICI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ICI, "demo.src.html"), encoding="utf-8").read()
faces = ""
for nom, fichier, poids in (("Archivo", "Archivo.ttf", "100 900"), ("PublicSans", "PublicSans.ttf", "100 900"), ("JBMono", "JetBrainsMono.ttf", "100 800")):
    b = base64.b64encode(open(os.path.join(ICI, "polices", fichier), "rb").read()).decode()
    faces += f"@font-face{{font-family:'{nom}';src:url(data:font/ttf;base64,{b}) format('truetype');font-weight:{poids};}}\n"
open(os.path.join(ICI, "demo.html"), "w", encoding="utf-8").write(src.replace("/*FONTS*/", faces))
print("ok")
