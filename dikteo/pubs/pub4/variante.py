"""Déclinaison par métier de la pub 4 : python variante.py electricien → demo_electricien.html (polices incrustées).
Les contenus du devis sont des exemples (données fictives), comme sur le site."""
import base64
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
METIERS = {
    "electricien": [
        ("Villeurbanne · chauffe-eau", "Villeurbanne · tableau électrique"),
        (">Chauffe-eau</div>", ">Tableau neuf</div>"), (">200 litres,</div>", ">3 rangées,</div>"), (">520 euros,</div>", ">340 euros,</div>"),
        ('<div class="d">Chauffe-eau 200 L</div><div class="q">1 u</div><div class="p">520,00 €</div>',
         '<div class="d">Tableau 3 rangées</div><div class="q">1 u</div><div class="p">340,00 €</div>'),
        ('<div class="d">Groupe de sécurité</div><div class="q">1 u</div><div class="p">48,00 €</div>',
         '<div class="d">Disjoncteurs</div><div class="q">8 u × 12,00 €</div><div class="p">96,00 €</div>'),
        ('<div class="d">Dépose ancien ballon</div><div class="q">1 forfait</div><div class="p">60,00 €</div>',
         '<div class="d">Mise à la terre</div><div class="q">1 forfait</div><div class="p">90,00 €</div>'),
        ('<div class="q">3 h × 55,00 €</div><div class="p">165,00 €</div>', '<div class="q">4 h × 55,00 €</div><div class="p">220,00 €</div>'),
        ("HT 793,00 € · TVA 79,30 €", "HT 746,00 € · TVA 74,60 €"),
        ("const tot=872.30*ease(u);", "const tot=820.60*ease(u);"),
        ("872,30 €", "820,60 €"),
        ("Durand Plomberie", "Durand Électricité"),
        ("Remplacement du chauffe-eau", "Remplacement du tableau"),
    ],
}

if __name__ == "__main__":
    nom = sys.argv[1]
    s = open(os.path.join(ICI, "demo.src.html"), encoding="utf-8").read()
    for a, b in METIERS[nom]:
        assert a in s, a
        s = s.replace(a, b)
    faces = ""
    for fam, fichier, poids in (("Archivo", "Archivo.ttf", "100 900"), ("PublicSans", "PublicSans.ttf", "100 900"), ("JBMono", "JetBrainsMono.ttf", "100 800")):
        b64 = base64.b64encode(open(os.path.join(ICI, "polices", fichier), "rb").read()).decode()
        faces += f"@font-face{{font-family:'{fam}';src:url(data:font/ttf;base64,{b64}) format('truetype');font-weight:{poids};}}\n"
    open(os.path.join(ICI, f"demo_{nom}.html"), "w", encoding="utf-8").write(s.replace("/*FONTS*/", faces))
    print("ok", nom)
