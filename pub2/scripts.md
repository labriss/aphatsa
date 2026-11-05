# Pubs Diktéo v2 : une pub par format

Base : l'étude des 100 pubs (`video/recherche/pubs-qui-marchent.md`). Aucun tournage : vidéos Pexels, vrai écran de
Diktéo capturé (`capture-ecran.mjs`) et incrusté dans les téléphones à écran vert (`incruster.py`), voix de synthèse
française (`voix.py`, Piper « siwis »), titres animés (`titres.html`), montage et mixage (`monter.py`).
Le détail exact de chaque plan est dans `pubs.py` ; les crédits dans `CREDITS.md`.

Règles tenues : aucun faux client, aucun témoignage, aucun chiffre inventé. Les personnes des vidéos Pexels ne parlent
jamais et ne sont pas présentées comme des clients. Le chrono du défi ne mesure que la dictée (les 5 s qu'il faut pour
dire la phrase de l'exemple). Offre réelle : 3 devis et 3 factures par mois gratuits, sans carte bancaire.

Fabriquer une pub : `python monter.py A` (ou B, C, C_vertical, D, D_vertical ; `--brouillon` pour une version rapide).
Sortie : `video/out/pub2/`.

## Style commun
- Étalonnage chaud et doux, grain léger, vignette : les vidéos de sources différentes ont l'air d'un même tournage.
- Typo Archivo très grasse, mot par mot avec un léger rebond ; le mot fort en orange.
- Écran incrusté avec les reflets et les doigts du vrai téléphone ; coupe franche sur les temps forts de la musique.
- Voix devant, musique baissée automatiquement sous la voix, -16 LUFS, crêtes sous -4,5 dBTP.

## A. TikTok / Reels / Shorts — 9:16, 23 s — « En parlant »
Recettes : démo au téléphone tenu en main, le « satisfaisant », appel à l'action.

| t | Image | Voix (sous-titres) |
|---|---|---|
| 0–1,7 | Robinet qui goutte, « plic » | « Une fuite. » |
| 1,7–4,3 | Téléphone sur le tableau de bord, Diktéo ouvert, le micro s'allume | « Et le devis, tu le fais quand ? » |
| 4,3–8,3 | Téléphone en main : la dictée s'écrit | « Maintenant. En parlant. » |
| 8,3–11,1 | Écran en grand, drop de la musique : les lignes tombent, total 872,30 € | « Tout se range tout seul. » |
| 11,1–14,0 | Autre main : « Envoyé à Mme Fontaine » | « Tu l'envoies. » |
| 14,0–18,0 | Plomberie ; notification « Mme Fontaine a accepté le devis », ding | « Ton client accepte en ligne. » |
| 18,0–23,0 | Carte de fin : logo, « Le devis dicté, envoyé du chantier », offre, bouton, dikteo.vercel.app | « Diktéo. Gratuit pour tes trois devis du mois. Sans carte bancaire. » |

### Déclinaisons par métier (les 6 formats × 10 métiers)
Chaque pub existe pour chaque métier du site : `A_<métier>`, `B_<métier>`, `C_<métier>`, `C_vertical_<métier>`,
`D_<métier>`, `D_vertical_<métier>` (sans suffixe : plombier). Ce qui change (`METIERS` dans pubs.py) : l'écran capturé
avec l'exemple du métier, le client et le total de la notification, l'accroche de A, le plan de fin, le défi de D.

| Métier | Accroche (A) | Client · total TTC |
|---|---|---|
| plombier | « Une fuite. » | Mme Fontaine · 872,30 € |
| electricien | « Un tableau à refaire. » | M. Lebrun · 905,30 € |
| chauffagiste | « Des radiateurs tout froids. » | Mme Garnier · 886,60 € |
| carreleur | « Une salle de bain à carreler. » | M. Petit · 1 734,70 € |
| peintre | « Un séjour à repeindre. » | Mme Laurent · 1 958,00 € |
| menuisier | « Une porte d'entrée à changer. » | M. Fabre · 2 073,50 € |
| macon | « Un mur à ouvrir. » | M. Robin · 2 402,40 € |
| couvreur | « Une toiture à refaire. » | Mme Perrin · 3 064,60 € |
| serrurier | « Une serrure à changer. » | M. Mercier · 599,50 € |
| multiservice | « Plein de petits travaux. » | Mme Chevalier · 259,60 € |

Nouveau métier : une entrée dans `METIERS`, les voix dans `voix/F.txt`, puis
`node capture-ecran.mjs pub2/ecran/<métier> 0:12.5:30 sombre <métier>`.

## B. YouTube in-stream — 16:9, 30 s — « Le soir / le chantier »
Recettes : sans / avec, liste numérotée.

| t | Image | Voix |
|---|---|---|
| 0–3,2 | Homme soucieux devant ses papiers, le soir (désaturé) | « 21 h. Il te reste trois devis à faire. » |
| 3,2–4,6 | Homme épuisé au bureau | « Comme hier soir. » |
| 4,6–7,0 | Le jour : camionnette (la musique démarre) | « Et si tu les faisais avant de repartir ? » |
| 7,0–10,3 | Artisan au volant | « Avec Diktéo, tu dictes ton chantier. » |
| 10,3–13,9 | Drop : téléphone sur le tableau de bord, la caméra s'approche | 1 « Tu parles. » |
| 13,9–18,3 | Écran en grand : lignes, total, envoi | 2 « Le devis se remplit tout seul. » |
| 18,3–21,6 | Main, notification d'acceptation | 3 « Ton client l'accepte en ligne. » |
| 21,6–24,5 | Plomberie | « Et toi, tu es déjà sur le chantier suivant. » |
| 24,5–30 | Carte de fin | « Diktéo. Gratuit pour commencer. » |

## C. Bumper — 6 s, 16:9 et 9:16 — « Dicté. Envoyé. Accepté. »
Recette : une idée, une offre. Main + dictée → écran (lignes, envoi, en accéléré) → notification + tampon
« Accepté ✓ » → logo, « Gratuit pour commencer ».

## D. Défi chrono — 15 s, 1:1 (Google Ads Demand Gen) et 9:16 — « Pari tenu »
Recettes : le défi, le satisfaisant. « Défi : un devis de plombier, dicté en 5 secondes. » → « Top chrono ! » → la dictée
pendant que le chrono tourne → 5,0 s, tampon « Pari tenu ✓ » → « Et le devis se remplit tout seul. » → « À toi de jouer »,
« Gratuit pour commencer ».

## Pour aller plus loin (non fait)
- Une vraie voix humaine (fondateur face caméra, recette n° 2) : la plus forte selon l'étude, mais demande un tournage.
