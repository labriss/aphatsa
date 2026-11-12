# Pub 7 · « Le Soir du plombier », film muet (piste n° 1 du carnet)

Format 9:16, environ 24 s. Une salle de cinéma dans le noir : rideaux rouges sombres en haut et en bas de l'écran
vertical, l'image projetée au centre (4:3 couché dans le 9:16, ou 3:4 debout), gravure à l'encre noire et lavis argent,
scintillement, poussière, rayures, vignette qui respire. Aucune voix. Un vrai piano de cinéma (ragtime léger, pas de
synthé), le cliquetis du projecteur en fond. Des cartons de texte (intertitres) entre les plans : **une seule chose à
lire à la fois**, cadre art nouveau, lettres crème sur noir.

Le héros : un artisan ordinaire, visage impassible à la Buster Keaton (grammaire seulement), habit de travail sobre.
Aucun trait caricatural ; l'humour vient des objets et de la paperasse, jamais de la personne.

| t (s) | Plan (un seul plan large et fixe, comme dans les films muets) | Ce qu'on lit | Piano |
|---|---|---|---|
| 0-2 | Le rideau s'ouvre sur l'écran ; amorce de film « 3, 2, 1 » qui clignote. | — | accord d'ouverture |
| 2-4 | Carton. | « 21 heures. » | note suspendue |
| 4-8 | Cuisine, nuit. L'artisan à table devant une pile de papiers. Il tape un devis à un doigt sur une vieille machine ; la pile monte, monte… et s'écroule sur lui. Il ressort, impassible, une feuille collée sur le front. | — | ragtime qui accélère, chute sur « crash » |
| 8-10 | Carton. | « Il y avait une autre façon. » | silence d'un temps |
| 10-15 | Même cuisine. Il sort son téléphone, le porte à la bouche comme un cornet de téléphone 1920. Ses mots sortent en volutes d'encre qui entrent dans le téléphone ; une feuille de devis propre s'imprime au bout comme un télégramme, ligne après ligne. Il la regarde, lève un sourcil (seul mouvement de son visage du film). | — | thème léger, une note par ligne |
| 15-17 | Carton. | « Devis envoyé. 21 h 04. » | accord joyeux |
| 17-21 | Il souffle sur la pile de papiers qui part dans la corbeille ; il met son chapeau, ouvre la porte : la famille l'attend à table, la lampe allumée. Iris qui se ferme sur la table. | — | final du thème |
| 21-24 | Carton final, même cadre : logo Diktéo, « Le devis dicté, envoyé du chantier. », diktéo.fr. | une chose | dernier accord, le projecteur s'arrête |

## Fabrication
- Le skill **lemo-opuscar** (style `silent-film`) : setup.sh installe la bibliothèque ; lire son STYLE.md et DIRECTOR.md.
- Dessins en gravure faits en code (SVG/canvas, hachures), mêmes pixels partout ; pas d'images générées qui « font IA ».
- Musique : piano de cinéma réel, sous licence libre (Mixkit, Pixabay ou domaine public, ex. ragtime de Scott Joplin
  enregistré sous licence libre) ; bruitages réels : projecteur, papier, machine à écrire, porte.
- Vérifier chaque plan sur une planche d'images avant le rendu ; 60 i/s.
