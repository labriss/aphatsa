// Les cartons. level : 1 = narration (double filet), 2 = tendre (vignes). Format portrait 1000×1333.
export const CARDS = {
  CARD1: { level: 1, lines: [{ text: 'Plombier ?', font: 'Playfair Display SC', weight: 900, size: 116 }, { text: ' ', size: 30 }, { text: 'Encore un devis', italic: true, size: 80 }, { text: 'à taper à 21 heures ?', italic: true, size: 80 }], gap: 1.3, stagger: .45 },
  CARD2: { level: 1, lines: [{ text: 'Une autre façon :', italic: true, size: 86 }, { text: ' ', size: 26 }, { text: 'il dicte', font: 'Playfair Display SC', weight: 900, size: 104 }, { text: 'son devis.', font: 'Playfair Display SC', weight: 900, size: 104 }], gap: 1.3, stagger: .5 },
  CARD3: { level: 2, lines: [{ text: 'Devis envoyé.', font: 'Playfair Display SC', weight: 900, size: 96 }, { text: '21 h 04.', italic: true, size: 84 }], gap: 1.4, stagger: .45 },
  FIN: { level: 2, dy: 40, lines: [
    { text: ' ', size: 150 },
    { text: 'Diktéo', font: 'Playfair Display SC', weight: 900, size: 120 },
    { text: 'Tu dictes ton devis,', italic: true, size: 62 },
    { text: 'Diktéo l’écrit.', italic: true, size: 62 },
    { text: ' ', size: 30 },
    { text: 'diktéo.fr', font: 'Playfair Display SC', weight: 700, size: 44, spacing: 2 },
  ], gap: 1.3, stagger: .35, at: .3 },
};
// Le seul élément en couleur du film : le logo orange du carton final (masque couleur).
export const LOGO = { cx: 500, cy: 360, size: 150 };
