# Pubs qui marchent : étude (novembre 2026)

But : apprendre des pubs vidéo **encore diffusées après des semaines ou des mois**, donc rentables pour leur annonceur,
pour s'en inspirer ensuite pour Fuitéo (TikTok, YouTube, Google Ads). On reprend leurs méthodes (accroche, structure,
rythme, preuve, appel à l'action), jamais leurs textes, images ou marques.

## Méthode

- **Source** : bibliothèque publicitaire Meta (pubs actives, avec leur date de début ; la même vidéo tourne en général
  aussi sur TikTok et YouTube), centre de transparence Google (YouTube, Google Ads), Creative Center TikTok.
- **Critère « ça marche »** : la vidéo est diffusée depuis au moins 30 jours (âge de la vidéo lu dans la bibliothèque),
  on prend d'abord les plus anciennes. Une pub non rentable est coupée en quelques jours.
- **Analyse de chaque pub** (`analyser.py`) : planche d'images (accroche à la demi-seconde, puis toutes les 2 s),
  texte dit (Whisper, en local), rythme des coupes. Les vidéos sont supprimées après l'étude ; seules ces notes restent.
- **Annonceurs** : concurrents directs (logiciels de devis et factures pour artisans) et voisins (banque, compta,
  facturation des indépendants), en France et aux États-Unis.

## Les pubs étudiées

| # | Annonceur | Domaine | Diffusée depuis | Durée |
|---|---|---|---|---|
| 1 | Tolteck | Devis et factures pour artisans du bâtiment (FR, concurrent direct) | août 2021 (5 ans) | 24 s |
| 2 | Tolteck | idem | août 2021 (5 ans) | 17 s |
| 3 | Tolteck | idem | août 2021 (5 ans) | 15 s |
| 4 | Tolteck | idem | mai 2026 (161 j) | 50 s |
| 5 | Obat | Devis et factures pour artisans du bâtiment (FR, concurrent direct) | sept. 2026 | 78 s |
| 6 | Obat | idem | sept. 2026 (vidéo de 3 ans) | 109 s |
| 7 | Housecall Pro | Gestion pour artisans (US) | 811 j | 23 s |
| 8 | Housecall Pro | idem | 473 j | 60 s |
| 9 | Housecall Pro | idem | 470 j | 23 s |
| 10 | Jobber | Gestion pour artisans (US) | 249 j | 38 s |
| 11 | Jobber | idem | 154 j | 26 s |
| 12 | Jobber | idem | 152 j | 30 s |
| 13 | Jobber | idem | 84 j | 30 s |
| 14 | Pennylane | Comptabilité des entreprises (FR) | 285 j | 31 s |
| 15 | Pennylane | idem | 278 j | 21 s |
| 16 | Pennylane | idem | 145 j | 27 s |
| 17 | Qonto | Banque pro, ici pour les artisans du bâtiment (FR) | 169 j | 23 s |
| 18 | Qonto | Banque pro (FR) | 110 j | 18 s |
| 19 | Qonto | Banque pro et facturation (FR) | 106 j | 27 s |
| 20 | Indy | Compta et facturation des indépendants (FR) | 182 j | 31 s |
| 21 | Indy | idem | 151 j | 39 s |

Google Ads (centre de transparence) : Obat y diffuse surtout des **annonces texte sur la recherche** (actives depuis
le 25 août 2026, encore diffusées le 4 nov.), pas de vidéo YouTube : les artisans y sont captés quand ils cherchent.
TikTok Creative Center : sans compte, seules 4 pubs visibles, hors sujet ; à refaire avec un compte TikTok Ads.

## Fiches

**1. Tolteck, 24 s, 5 ans.** Enregistrement d'écran brut du logiciel : un devis réel, on clique « Facturer », la facture
sort. Aucun visage, aucun effet. *À retenir* : montrer le produit faire le travail, en vrai, suffit quand la cible cherche
déjà un outil.

**2. Tolteck, 17 s, 5 ans.** Carton noir « Créez des devis-factures clairs et professionnels », deux artisanes à table,
écran du devis avec une étiquette orange « Proposer une offre claire et compréhensible », fin : note 4,8 étoiles.
*À retenir* : une promesse, une preuve (de vraies artisanes), une note client.

**3. Tolteck, 15 s, 5 ans.** Carton « Simplifiez votre gestion comptable », gros plan d'écran, tableau de bord, note 4,8.
*À retenir* : 15 s suffisent pour une seule idée.

**4. Tolteck, 50 s.** Un artisan (vrai client) parle à son bureau, cadré serré dans un cadre de couleur ; chaque argument
s'affiche entouré de rouge : « Simple à utiliser », « Devis en moins de 5 min », « Disponible sur PC, Mac et téléphone »,
« Multi-utilisateur gratuit », « Le meilleur rapport qualité/prix ». Ouverture : « ARTISAN : un logiciel conforme, simple
et au meilleur prix ? ». Fin : « +30 000 utilisateurs, essayez gratuitement ». *À retenir* : interpeller le métier dès
la première image, puis un témoin qui coche les objections une à une.

**5. Obat, 78 s.** Un artisan filmé comme un selfie, une seule prise, coupes sèches, énormes sous-titres mot à mot au centre
(« OBAT, MOI ÇA FAIT QUATRE, CINQ ANS QUE JE L'UTILISE »). Il raconte son usage : « tu rentres, son téléphone, hop, le devis ».
Texte de la pub : « La facturation électronique arrive en 2026. Excel n'est pas compatible. Obat, si. » *À retenir* :
le témoignage brut, sans production, tient même long.

**6. Obat, 109 s.** Mini-reportage chez une vraie carreleuse (son entreprise, son camion, son numéro) : interview,
gestes de chantier (colle, carrelage, découpe), l'appli sur tablette à la maison. Horizontal. *À retenir* : le métier
filmé pour de vrai, le logiciel en second.

**7. Housecall Pro, 23 s, 811 j.** Uniquement du texte animé, format carré, couleurs de marque : « Do you want to grow
your Electrical business? », « Unlock the full potential », « For free! », guide gratuit à télécharger, logo.
**Décliné par métier** (électricien, nettoyage de moquette…). *À retenir* : la même pub, le nom du métier changé, et un
cadeau gratuit (guide) plutôt qu'un abonnement.

**8. Housecall Pro, 60 s, 473 j.** L'avant en **noir et blanc** (tiroirs en vrac, post-its « HELP! », « Some guys don't
mind doing things the hard way »), puis la couleur avec un vrai plombier (son camion), l'appli sur téléphone, des mots
qui claquent « USABLE / IN YOUR PHONE / SIMPLIFY / SCALE », fin « Built for the trades, no trade-offs » et bouton.
*À retenir* : le contraste avant/après par la couleur marche, à condition d'avoir de **vraies personnes**.

**9. Housecall Pro, 23 s, 470 j.** Accroche question : « Have you considered Housecall Pro, but aren't sure it's the right
move? » Une patronne face caméra (style selfie) : dans les 24 premières heures, trois avis 5 étoiles.
Fin : « Book a demo ». *À retenir* : un résultat concret et daté, raconté par une cliente.

**10. Jobber, 38 s, 249 j.** Un créateur de contenu (micro de podcast, néons) : « Nobody talks about this but every blue
collar worker… », sous-titres mot à mot avec des mots en couleur, images d'un frigoriste au travail, l'appli (planning,
devis, facture, paiement), fin « Quote, Schedule, Invoice, Get paid, free 14-day trial », « link down below ». Publiée
sous le nom d'un client (« Reliable HVACR avec Jobber »). *À retenir* : format TikTok natif, la voix d'un pair, pas
d'une marque.

**11. Jobber, 26 s, 154 j.** Un patron assis en studio, puis sur ses chantiers (camion, téléphone, ville) : « Sometimes as a
small business it's difficult… », la standardiste IA rappelle les clients. Fin : « Start your free trial ».

**12. Jobber, 30 s, 152 j.** « Before Jobber, it was paper. » Un électricien seul devenu équipe de 7 ; téléphone, camion,
équipe. Même fin. *À retenir* : l'accroche « Avant, c'était… » et une transformation chiffrée.

**13. Jobber, 30 s, 84 j.** S'ouvre **en pleine action** : vue de drone d'un toit en chantier, nacelle. Le couvreur raconte
le projet, fait « le devis sur place » (écran) ; fin : la liste des métiers qui défile « Built for HVAC, Electrical,
Plumbing… ».

**14. Pennylane, 31 s, 285 j.** Animation du produit seule (cartes d'interface, « 3 en 1 », « Gagnez du temps, de
l'argent, en sérénité », curseur qui clique « Activez le Compte Pro »). Cible : clients déjà inscrits.

**15. Pennylane, 21 s, 278 j.** Un client en interview, assis, sous-titré (« Je me souviens encore de la première
démonstration »), logo du client à la fin.

**16. Pennylane, 27 s, 145 j.** Deux cofondateurs clients en interview, plans de leur bureau et de l'écran, logo commun.

**17. Qonto, 23 s, 169 j.** Bandeau d'accroche en haut : « Artisan, marre d'être bloqué dans tes achats ? » Un artisan en
magasin de bricolage, paiement refusé en caisse, puis l'explication ; fin : logo et Trustpilot. *À retenir* : la scène du
problème, dans le monde du métier, en ouverture.

**18. Qonto, 18 s, 110 j.** Un dirigeant nommé à l'écran : « Qonto m'a permis d'économiser 5 000 € », « je passais 10-15 h
par mois, maintenant 2 h ». *À retenir* : des chiffres dits par un client.

**19. Qonto, 27 s, 106 j.** Écran partagé **« Sans Qonto / Avec Qonto »** : deux personnes sur un canapé, sous chacune une
liste qui grandit (en rouge : factures Excel, réforme, relances ; en vert : conforme, en un clic, payé plus vite). Fin :
la page du produit. *À retenir* : comparaison côte à côte, lisible sans le son.

**20. Indy, 31 s, 182 j.** Une créatrice face caméra : « On va voir ensemble comment créer une facture en moins de
30 secondes », étapes numérotées avec les écrans incrustés, « vous serez conforme ». *À retenir* : le tutoriel express.

**21. Indy, 39 s, 151 j.** Un jeune créateur au tableau blanc explique la réforme (« Facturation électronique… hors
conforme ? »), puis la solution gratuite. Fin rose avec la note de l'appli. *À retenir* : éduquer sur une contrainte
réelle et datée.

## Les premières phrases dites (transcription Whisper, à quelques mots près)

- Obat (6) : « Je suis Carlos, plaquiste. J'ai démarré mon entreprise le 3 janvier 2023, suite à une reconversion. »
  → se présenter par son prénom et son métier, puis raconter.
- Obat (5) : « Ça fait 4-5 ans que je l'utilise… tu peux mettre ton logo, tes couleurs, tes lignes… »
- Qonto (19) : « Moi, je fais mes factures sur Excel. [La réforme] arrive, je ne sais même pas par où commencer. »
  / « Moi, avec Qonto, mes factures sont électroniques et 100 % conformes. » → le dialogue Sans / Avec.
- Qonto (17) : « Quand on a un gros achat, on peut augmenter notre plafond… contrairement à une banque traditionnelle. »
- Qonto (18) : « Qonto m'a permis d'économiser, sur une année, environ 5 000 €. »
- Indy (21) : « La facturation électronique, combien ça va me coûter ? Le problème, c'est que personne ne vous explique
  vraiment ce que vous avez à faire. Est-ce que vous êtes concerné ? » → trois questions que la cible se pose.
- Indy (20) : « On va voir ensemble comment créer une facture en moins de 30 secondes. »
- Pennylane (15) : « Je me souviens encore de la première démonstration… »
- Jobber (10) : « Well, nobody talks about this, but every blue collar worker 100 % agrees with this. »
- Jobber (12) : « Before Jobber, it was paper. And as soon as you hire an employee, that all goes out the window. »
- Jobber (13) : « We started this project. Our scope of work was just replacing the roof… huge structural issues. »
- Housecall Pro (8) : « Some guys don't mind doing things the hard way. »
- Housecall Pro (9) : « Have you considered Housecall Pro, but aren't sure it's the right move? »
- Tolteck (1), Housecall Pro (7), Pennylane (14) : pas de voix, seulement musique et texte à l'écran.

Point commun : la première phrase est **dite par une personne, au « je » ou au « tu »**, et parle du quotidien du métier
(Excel, le papier, un gros achat, la réforme), jamais du logiciel en premier.

## Ce qui revient : les méthodes à reprendre

1. **De vraies personnes du métier, pas des objets ni de la 3D.** 17 pubs sur 21 montrent un artisan ou un client qui
   parle. Les seules sans visage sont des démos d'écran (Tolteck) ou du texte animé (Housecall Pro), jamais de la 3D.
2. **Une accroche dès la première seconde, écrite à l'écran** : le métier interpellé (« ARTISAN », « Artisan, marre
   de… », « your Electrical business »), une question, ou « Avant, c'était le papier ».
3. **Des sous-titres incrustés** partout, souvent mot à mot et gros au centre (la vidéo est vue sans le son).
4. **Un montage lent** : 0,06 à 0,73 coupe par seconde. Le témoin a le temps de parler ; ce n'est pas un clip.
5. **Le produit montré en vrai** : un vrai écran (devis, facture, paiement), quelques secondes, souvent tenu en main.
6. **Une preuve** : nombre d'utilisateurs (21 000, 30 000, 300 000), note (4,8, Trustpilot), chiffres de clients
   (5 000 €, 10 h ramenées à 2 h, 3 avis en 24 h).
7. **Une fin simple** : essai gratuit, sans carte, un bouton ; parfois un cadeau (guide).
8. **Des déclinaisons par métier** (Housecall Pro, Jobber « Built for… ») : la même pub, le métier changé.
9. **Les formats** : vertical 9:16 pour TikTok, Reels et Shorts (Jobber, Obat, Indy, Qonto), carré pour le fil,
   horizontal pour les reportages ; 15 à 40 s le plus souvent, jusqu'à 110 s pour un témoignage.
10. **Une actualité qui oblige** : la facture électronique de 2026 (Obat, Indy, Qonto, Tolteck).

## Ce que la pub Fuitéo de novembre 2026 faisait à l'opposé

Des objets en 3D au lieu de personnes, un montage rythmé façon clip, aucune preuve (ni client, ni chiffre), la musique
au premier plan, une accroche poétique au lieu d'interpeller le métier. Belle, mais contraire à tout ce qui tient dans
la durée ici.
