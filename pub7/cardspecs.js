// Les cartons. level : 1 = narration (double filet), 2 = tendre (vignes). Format portrait 1000×1333.
export const CARDS = {
  CARD1: { level: 1, lines: [{ text: '21 heures.', font: 'Playfair Display SC', weight: 900, size: 120 }], gap: 1.3 },
  CARD2: { level: 1, lines: [{ text: 'Il y avait', italic: true, size: 92 }, { text: 'une autre façon.', italic: true, size: 92 }], gap: 1.35 },
  CARD3: { level: 2, lines: [{ text: 'Devis envoyé.', font: 'Playfair Display SC', weight: 900, size: 96 }, { text: '21 h 04.', italic: true, size: 84 }], gap: 1.4 },
  FIN: { level: 2, dy: 40, lines: [
    { text: ' ', size: 150 },
    { text: 'Diktéo', font: 'Playfair Display SC', weight: 900, size: 120 },
    { text: 'Le devis dicté,', italic: true, size: 62 },
    { text: 'envoyé du chantier.', italic: true, size: 62 },
    { text: ' ', size: 30 },
    { text: 'dikteo.vercel.app', font: 'Playfair Display SC', weight: 700, size: 44, spacing: 2 },
  ], gap: 1.3 },
};
// Le seul élément en couleur du film : le logo orange du carton final (masque couleur).
export const LOGO = { cx: 500, cy: 360, size: 150 };
