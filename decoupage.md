# Pub Fuitéo — découpage (30 s, vertical 1080 × 1920, 30 images/s)

Fil rouge : le plombier. Avant gris et froid, fait d'objets ; après orange et chaud.
Musique : silence sur l'accroche, montée électro, drop quand le devis se remplit tout seul.
Données fictives uniquement (cliente « Mme Fontaine », montants d'exemple).

| Plan | Temps | Outil | Image | Texte à l'écran | Son |
|---|---|---|---|---|---|
| 1 | 0,0 – 2,5 s | Blender | Gros plan : une goutte se forme sous l'écrou d'un siphon en cuivre, fond noir, contre-jour. Elle tombe au ralenti. | « Vous réparez la fuite en 20 minutes. » | Silence, puis « plic ». |
| 2 | 2,5 – 5,0 s | Blender | La table de cuisine la nuit, bleu-gris : ordinateur portable et son tableur, carnet raturé, café froid, horloge 22:47. | « Le devis, lui, vous prend la soirée. » | Un bourdon grave, le tic-tac. |
| 3 | 5,0 – 7,0 s | Blender | Lente avancée vers l'horloge, les aiguilles filent de 22:47 à 23:38. Le curseur clignote. | — | Le tic-tac accélère, la tension monte. |
| 4 | 7,0 – 8,0 s | Blender | La lueur de l'écran vire à l'orange, la caméra plonge dedans. | « Et si vous le dictiez ? » | Souffle (whoosh), la musique démarre. |
| 5 | 8,0 – 13,0 s | Blender + interface | Le téléphone 3D monte dans une lueur orange et se tourne vers nous. À l'écran, la vraie appli : on touche le micro, l'onde vocale, la phrase dictée s'écrit. | — | Montée électro, clic du micro. |
| 6 | 13,0 – 16,16 s | Interface | DROP : les lignes du devis tombent en cartes sur le rythme, le total s'affiche en chiffres mono. | « Chiffré tout seul. » | Drop. |
| 7 | 16,16 – 19,32 s | Blender + interface | On touche « Envoyer » ; l'écran passe à « Devis accepté ✓ — Mme Fontaine ». Le téléphone pivote. | — | « Ding » d'acceptation. |
| 8 | 19,32 – 24,05 s | Animations du site | Les 9 autres métiers défilent, un par temps (0,395 s), le dernier tient 3 temps : la réparation finie, le nom du métier en grand. | « Pour tous les métiers du bâtiment. » | Coupes sur chaque temps. |
| 9 | 24,05 – 26,56 s | Blender | Retour à la cuisine, maintenant chaude : l'ordinateur est fermé, l'horloge indique 18:30. | — | La musique respire. |
| 10 | 26,56 – 30,0 s | Interface | Logo Fuitéo, lueur orange. | « Le devis dicté, envoyé du chantier. » — « Gratuit pour commencer » — fuiteo.vercel.app | Note finale. |

Version 15 s : plans 1, 4 (raccourci), 6, 7, 10.
Version 16:9 : même montage, le téléphone au centre et le texte à côté.

## Musique : « Promo Drop » (JoyInSound, Pixabay)

Fichier : `assets/musique/promo-drop.mp3` (hors de git), licence dans `assets/musique/LICENCE.txt`.
Mesuré dans le fichier : 152 BPM, un temps = 0,3947 s, une mesure = 1,579 s.
Roulement de caisse claire 5,0 – 5,7 s, drop à 5,71 s, phrases de 8 mesures, dernier coup à 106,77 s
puis queue de réverb jusqu'à 111 s.

Montage du son (deux morceaux du fichier, coupés sur des barres de mesure, fondu de 30 ms) :
- 0 – 7,29 s : pas de musique. Seulement les bruitages (« plic », bourdon, tic-tac qui accélère).
- 7,29 s : le morceau démarre au début ; son intro monte pendant la dictée.
- 13,00 s : le drop du morceau (5,71 s) tombe sur les lignes du devis.
- 25,63 s (8 mesures après le drop) : on enchaîne sur la dernière mesure du morceau (105,19 s).
- 27,21 s : le dernier coup tombe quand la goutte du logo se pose ; la réverb s'éteint, léger fondu sur les 0,5 dernières secondes.

Repères sur la musique (barres de mesure après le drop) : 14,58 · 16,16 · 17,74 · 19,32 · 20,89 · 22,47 · 24,05 · 25,63.
Les coupes et les titres tombent sur ces barres ou sur les temps.

Bruitages : uniquement aux endroits écrits dans le tableau, mixés sous la musique (−12 dB environ),
jamais deux en même temps. Volume final normalisé à −14 LUFS (réseaux sociaux), crête à −1 dBTP.

## Effets de titres (inspirés de 21st.dev, recodés)
- Plan 1 : révélation lettre par lettre, chaque lettre monte de sous son cache.
- Plan 2 : « la soirée » sort d'un flou froid.
- Plan 6 : « tout seul. » arrive sur le drop, un reflet balaie le mot.
- Plan 8 : le nom du métier roule (l'ancien monte, le nouveau arrive) à chaque temps.
- Plan 10 : la goutte se dessine au trait puis se remplit, posée sur le dernier coup.
