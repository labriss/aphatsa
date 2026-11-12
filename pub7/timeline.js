// Le Soir du plombier — grille de tempo : source unique pour l'image, la partition, le mixage et la vérification.
// Sections de la « cue sheet » du cinéma muet ; chaque section commence à la fin de la précédente.
export const FPS = 24;

// [nom, bpm, temps, humeur]
const SECS = [
  ['PRE',    96, 2,   'le projecteur démarre (pas de musique)'],
  ['CARD1',  96, 5.5, 'Misterioso : « Plombier ? Encore un devis à taper à 21 heures ? »'],
  ['GAG',   112, 12,  'Agitato : la pile monte, vacille et s’écroule'],
  ['CARD2',  96, 5.5, 'SILENCE : « Une autre façon : il dicte son devis. »'],
  ['VOIX',   84, 8,   'Tenderly : la voix devient télégramme'],
  ['CARD3',  96, 5,   'accord joyeux : « Devis envoyé. 21 h 04. »'],
  ['MAISON', 84, 6,   'le thème, chaud : il rentre dîner'],
  ['FIN',    84, 7,   'carton Diktéo, accord tenu, la bobine claque'],
];

export const SEC = {};
let t = 0;
for (const [name, bpm, beats, mood] of SECS) {
  const beat = 60 / bpm, dur = beat * beats;
  SEC[name] = { name, bpm, beats, beat, t0: t, t1: t + dur, dur, mood };
  t += dur;
}
export const DUR = +t.toFixed(4);
export const at = (name, b = 0) => SEC[name].t0 + b * SEC[name].beat;
export const secAt = tt => { for (const k in SEC) if (tt < SEC[k].t1) return SEC[k]; return SEC.FIN; };

// Les coups : l'image tombe dessus, la partition les joue.
export const HIT = {
  lampe:     at('PRE', .5),
  carte1:    at('CARD1', 0),
  gag:       at('GAG', 0),
  feuille1:  at('GAG', 2),      // il pose une feuille de plus sur la pile
  feuille2:  at('GAG', 4),
  feuille3:  at('GAG', 6),
  vacille:   at('GAG', 7),      // la pile vacille (trille)
  chute:     at('GAG', 8.5),    // elle s'écroule sur lui (cluster)
  emerge:    at('GAG', 10),     // il ressort, une feuille collée au front
  plonk:     at('GAG', 11),
  carte2:    at('CARD2', 0),
  voix:      at('VOIX', 0),
  telephone: at('VOIX', .5),    // il porte le téléphone à sa bouche (premier son après le silence)
  ligne1:    at('VOIX', 2.5),
  ligne2:    at('VOIX', 3.5),
  ligne3:    at('VOIX', 4.5),
  ligne4:    at('VOIX', 5.5),
  sourcil:   at('VOIX', 6.8),   // il lève un sourcil vers nous (note de grâce)
  carte3:    at('CARD3', 0),
  maison:    at('MAISON', 0),
  souffle:   at('MAISON', .5),  // il souffle la pile vers la corbeille
  porte:     at('MAISON', 3),   // la porte s'ouvre sur la table
  iris:      at('MAISON', 4.2),
  fin:       at('FIN', 0),
  claque:    at('FIN', 6),
};
