// Le Soir du plombier — les plans. Chaque plan peint une image TONALE portrait 1000×1333 (valeurs de gris = densité d'impression) ;
// film.js la passe dans Redraw (encre + hachures) puis FilmPost (tirage argentique, vieillissement). lt = secondes depuis le début de la section.
import { drawFigure, P0, mixPose, solve, projector, BODY, walkPose } from './engine/figure.js';
import { form, stroke, grey, rectPts, ellipsePts, mottle, catmull, pathOf } from './engine/ink.js';
import { ARTISAN, ENFANT } from './chars.js';
import { SEC } from './timeline.js';

export const FW = 1000, FH = 1333;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const ss = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const seg = (x, a, b) => clamp((x - a) / (b - a));
const lin = x => clamp(x);
const rnd = n => { n = Math.sin(n * 127.1 + 311.7) * 43758.5453; return n - Math.floor(n); };
const clonePose = p => mixPose(p, p, 0);

export function poseAt(b, keys, ease = ss) {
  const val = v => typeof v === 'function' ? v(b) : v;
  if (b <= keys[0][0]) return clonePose(val(keys[0][1]));
  for (let i = 1; i < keys.length; i++) if (b < keys[i][0]) {
    const [b0, A] = keys[i - 1], [b1, Bv] = keys[i];
    return mixPose(val(A), val(Bv), ease((b - b0) / (b1 - b0)));
  }
  return clonePose(val(keys[keys.length - 1][1]));
}
export function numAt(b, keys, ease = ss) {
  if (b <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (b < keys[i][0]) { const [b0, a] = keys[i - 1], [b1, c] = keys[i]; return lerp(a, c, ease((b - b0) / (b1 - b0))); }
  return keys[keys.length - 1][1];
}
// où sont les mains et la tête d'un personnage (même placement que drawFigure)
export function bodyAt(ch, opt) {
  const B = BODY[ch.body || 'adult'], J = solve(opt.pose, B), s = opt.scale;
  const low = Math.min(J.legs.L.sole[1], J.legs.R.sole[1], J.legs.L.toe[1], J.legs.R.toe[1], J.legs.L.heel[1], J.legs.R.heel[1]);
  const pr = projector(opt.x, opt.ground + low * s, s, opt.yaw);
  return { L: pr.P(J.arms.L.hand), R: pr.P(J.arms.R.hand), head: pr.P(J.head), s };
}

// ---------------- les expressions et les poses ----------------
const DEADPAN = { open: .78, brow: 0, look: [0, 0] };
const LOOKDOWN = { open: .6, brow: .1, look: [0, .6] };
const SOURCIL = { open: 1.0, brow: 1.5, browA: -.3, look: [0, -.1] };
const DOUX = { open: .6, brow: .35, browA: .5, smile: .6, look: [0, .1] };
const ecrit = ph => {          // il tape un devis à un doigt sur la table
  const p = P0(); p.lean = .32; p.nod = .32; p.expr = LOOKDOWN;
  const k = Math.abs(Math.sin(ph * Math.PI * 3));
  p.aR = { fl: .95, abd: .12, el: 1.15 - .25 * k, wr: .2, hand: 'fist' };
  p.aL = { fl: .7, abd: .2, el: 1.35, wr: .1, hand: 'relax' };
  return p;
};
const pose1 = () => { const p = ecrit(0); p.aR = { fl: 1.1, abd: .1, el: .45, wr: .1, hand: 'open' }; p.lean = .26; return p; };   // pose une feuille sur la pile
const regarde = () => { const p = P0(); p.headTurn = -.55; p.nod = -.12; p.expr = DEADPAN; p.lean = .05; return p; };
const ecrase = () => { const p = P0(); p.lean = .55; p.nod = .5; p.aL = { fl: 1.6, abd: .4, el: 1.9, wr: 0, hand: 'open' }; p.aR = { fl: 1.6, abd: .4, el: 1.9, wr: 0, hand: 'open' }; p.expr = DEADPAN; return p; };
const debout = () => { const p = P0(); p.expr = DEADPAN; p.nod = 0; return p; };
const telephone = () => {     // le téléphone tenu comme un cornet, contre la bouche
  const p = P0(); p.nod = .02; p.headTurn = .1; p.expr = DEADPAN;
  p.aL = { fl: 1.45, abd: .08, el: 2.55, wr: .35, hand: 'fist' };
  p.aR = { fl: .1, abd: .05, el: .3, wr: .1, hand: 'relax' };
  return p;
};
const souffle = () => { const p = P0(); p.lean = .2; p.nod = .2; p.headTurn = -.35; p.expr = { open: .5, mouthOpen: .5, mouthW: .35, brow: .2 }; return p; };
const chapeau = () => { const p = P0(); p.aR = { fl: 2.7, abd: .25, el: 1.4, wr: .1, hand: 'fist' }; p.expr = DOUX; return p; };

// ---------------- la cuisine, la nuit ----------------
const TABLE_Y = 930, SOL = 1180;
function cuisine(g, o = {}) {
  // mur clair, lambris sombre en bas
  form(g, rectPts(-20, -20, FW + 40, 1000), { v: .78, line: 0, seed: 1 }); mottle(g, 0, 0, FW, 980, .1, 3);
  form(g, rectPts(-20, 760, FW + 40, 240), { v: .52, line: 2.2, seed: 2 });
  for (let x = 20; x < FW; x += 90) stroke(g, [[x, 770], [x, 990]], 1.2, { seed: 30 + x, alpha: .5 });
  // la fenêtre de nuit (un rond de lune), en haut à gauche
  form(g, rectPts(60, 120, 300, 380), { v: .6, line: 2.6, seed: 3, shade: 8 });
  form(g, rectPts(80, 140, 260, 340), { v: .12, line: 2, grad: .2, seed: 4 });
  form(g, ellipsePts(270, 220, 38, 38), { v: .92, line: 1.6, seed: 5 });
  stroke(g, [[210, 140], [210, 480]], 3, { color: grey(.6), seed: 6 }); stroke(g, [[80, 310], [340, 310]], 3, { color: grey(.6), seed: 7 });
  // l'horloge : 21 h
  form(g, ellipsePts(800, 230, 70, 70), { v: .9, line: 2.6, seed: 8, shade: 6 });
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; stroke(g, [[800 + Math.cos(a) * 56, 230 + Math.sin(a) * 56], [800 + Math.cos(a) * 64, 230 + Math.sin(a) * 64]], 2, { seed: 9 + i }); }
  const m = o.minute ?? 0, ah = (9 + m / 60) / 12 * Math.PI * 2 - Math.PI / 2, am = m / 60 * Math.PI * 2 - Math.PI / 2;
  stroke(g, [[800, 230], [800 + Math.cos(ah) * 34, 230 + Math.sin(ah) * 34]], 5, { seed: 22 });
  stroke(g, [[800, 230], [800 + Math.cos(am) * 52, 230 + Math.sin(am) * 52]], 3, { seed: 23 });
  // la lampe suspendue et son cône de lumière
  stroke(g, [[500, -20], [500, 250]], 2, { seed: 24 });
  form(g, [[430, 300], [570, 300], [535, 250], [465, 250]], { v: .25, line: 2.2, grad: .2, seed: 25 });
  g.save(); g.globalCompositeOperation = 'lighter'; const lg = g.createRadialGradient(500, 330, 10, 500, 700, 620);
  lg.addColorStop(0, 'rgba(255,255,255,.22)'); lg.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = lg; g.fillRect(0, 280, FW, 900); g.restore();
  // le sol
  form(g, rectPts(-20, 990, FW + 40, 400), { v: .4, line: 2, seed: 26 });
  for (let y = 1010; y < FH; y += 40) stroke(g, [[0, y], [FW, y + 6]], 1, { seed: 40 + y, alpha: .35 });
}
function table(g) {        // la table vue de face, devant le personnage : elle cache ses jambes
  form(g, [[90, TABLE_Y], [910, TABLE_Y], [940, TABLE_Y + 36], [60, TABLE_Y + 36]], { v: .58, line: 2.6, grad: .15, seed: 50, shade: 6 });
  form(g, rectPts(70, TABLE_Y + 36, 860, SOL - TABLE_Y - 20), { v: .42, line: 2.4, grad: .12, seed: 51, shade: 6 });
  for (const x of [110, 520]) { form(g, rectPts(x, TABLE_Y + 80, 370, 150), { v: .48, line: 1.8, seed: 52 + x }); form(g, ellipsePts(x + 185, TABLE_Y + 150, 10, 10), { v: .2, line: 1.2, seed: 53 + x }); }
  for (const x of [110, 520]) form(g, rectPts(x, TABLE_Y + 250, 370, 150), { v: .48, line: 1.8, seed: 56 + x });
}
// une feuille de papier (vue un peu de dessus), avec ses lignes d'écriture
function feuille(g, x, y, w, rot = 0, v = .93, seed = 1, lignes = true) {
  const h = w * 1.35, c = Math.cos(rot), s = Math.sin(rot), P = (u, q) => [x + u * c - q * s, y + u * s + q * c];
  form(g, [P(-w / 2, -h / 2), P(w / 2, -h / 2), P(w / 2, h / 2), P(-w / 2, h / 2)], { v, line: Math.max(1, w * .02), seed });
  if (lignes && w > 30) for (let i = 0; i < 6; i++) { const yy = -h / 2 + h * (.2 + i * .12), l = w * (.3 + rnd(seed + i) * .35); stroke(g, [P(-w * .38, yy), P(-w * .38 + l, yy)], Math.max(.8, w * .012), { seed: seed * 7 + i, alpha: .6 }); }
}
// la pile de papiers, vue de face : n feuilles empilées (une tranche par feuille)
function pile(g, x, base, n, tilt = 0, seed = 1) {
  g.save(); g.translate(x, base); g.rotate(tilt);
  for (let i = 0; i < n; i++) {
    const y = -i * 9, dx = (rnd(seed + i) - .5) * 22, w = 230 + (rnd(seed + i * 3) - .5) * 20;
    form(g, rectPts(-w / 2 + dx, y - 9, w, 9), { v: i % 2 ? .9 : .84, line: 1.3, seed: seed + i });
  }
  // la feuille du dessus, vue un peu de dessus
  form(g, [[-118, -n * 9 - 6], [118, -n * 9 - 6], [124, -n * 9 + 2], [-124, -n * 9 + 2]], { v: .95, line: 1.4, seed: seed + 999 });
  g.restore();
}

// ============ 1 · LE GAG (plan d'ensemble fixe) ============
const ART_X = 600, ART_S = 112;
export function gag(g, lt) {
  const B = SEC.GAG.beat, b = lt / B;
  cuisine(g);
  // la pile : 22 feuilles, puis une de plus à chaque feuille posée ; elle vacille, puis s'écroule sur lui
  const n = 24 + (b >= 2.4 ? 5 : 0) + (b >= 4.4 ? 6 : 0) + (b >= 6.4 ? 7 : 0);
  const tilt = b < 7 ? 0 : b < 8.5 ? Math.sin((b - 7) * Math.PI * 4) * .05 * (b - 7) : 0;
  const P = poseAt(b, [[0, ecrit], [1.5, ecrit], [2, pose1()], [2.4, ecrit], [3.6, ecrit], [4, pose1()], [4.4, ecrit], [5.6, ecrit], [6, pose1()], [6.4, ecrit],
    [7, regarde()], [8.4, regarde()], [8.7, ecrase()], [9.8, ecrase()], [10.3, debout()]]);
  const yawG = numAt(b, [[1.4, 20], [1.8, -55], [2.3, -55], [2.6, 20], [3.4, 20], [3.8, -55], [4.3, -55], [4.6, 20], [5.4, 20], [5.8, -55], [6.3, -55], [6.6, 20], [7, -30], [8.4, -30], [8.7, 20]]);
  const fig = { x: ART_X, ground: SOL, scale: ART_S, yaw: yawG, pose: P, t: lt };
  drawFigure(g, ARTISAN, fig);
  const corps = bodyAt(ARTISAN, fig);
  // feuille posée : elle part de sa main droite vers le haut de la pile
  if (b < 8.5) {
    pile(g, 300, TABLE_Y, n, tilt, 7);
    for (const k of [2, 4, 6]) if (b >= k - .5 && b < k + .4) {
      const u = seg(b, k - .5, k + .4), top = TABLE_Y - n * 9;
      feuille(g, lerp(corps.R[0], 300, ss(u)), lerp(corps.R[1], top - 10, ss(u)) - Math.sin(u * Math.PI) * 60, 90, lerp(.6, 0, u), .95, 80 + k);
    }
  } else {
    // l'avalanche : les feuilles volent de la pile vers lui, puis le recouvrent
    const u = seg(b, 8.5, 9.4);
    pile(g, 300, TABLE_Y, 6, 0, 7);
    for (let i = 0; i < 38; i++) {
      const d = rnd(i * 13) * .35, uu = clamp((u - d) / (1 - d));
      const x0 = 300 + (rnd(i) - .5) * 120, y0 = TABLE_Y - 60 - rnd(i * 5) * 300;
      const x1 = corps.head[0] + (rnd(i * 7) - .5) * 260, y1 = corps.head[1] + 40 + rnd(i * 11) * 380;
      const x = lerp(x0, x1, uu), y = lerp(y0, y1, uu) - Math.sin(uu * Math.PI) * (140 + rnd(i * 3) * 120);
      if (b > 9.8 && i % 3 !== 0) continue;          // il se dégage : une partie retombe
      feuille(g, x, b > 9.8 ? lerp(y, TABLE_Y - 10, seg(b, 9.8, 10.3)) : y, 70 + rnd(i * 17) * 30, (rnd(i * 19) - .5) * 2.4 * uu, .9 + rnd(i) * .07, 200 + i);
    }
  }
  table(g);
  if (b >= 8.5) pile(g, 300, TABLE_Y, 6, 0, 7);
  // la feuille collée au front, après la chute
  if (b >= 10) feuille(g, corps.head[0] + 6, corps.head[1] - ART_S * .18, 64, -.12, .95, 300);
}

// ============ 2 · LA VOIX (plan moyen, poussée lente, iris à demi) ============
export function voix(g, lt) {
  const B = SEC.VOIX.beat, b = lt / B;
  const z = lerp(1.35, 1.6, ss(b / 8)), cx = 560, cy = 640;           // la caméra s'approche doucement
  g.save(); g.translate(FW / 2, FH / 2); g.scale(z, z); g.translate(-cx, -cy);
  cuisine(g, { minute: Math.round(numAt(b, [[0, 0], [7, 4]], lin)) });
  const P = poseAt(b, [[0, debout()], [.5, telephone()], [6.6, telephone()], [6.8, (() => { const p = telephone(); p.expr = SOURCIL; p.headTurn = .35; return p; })()]]);
  const fig = { x: ART_X, ground: SOL, scale: ART_S, yaw: 20, pose: P, t: lt };
  drawFigure(g, ARTISAN, fig);
  const corps = bodyAt(ARTISAN, fig);
  // le téléphone dans sa main droite
  const ph = [corps.L[0] - 8, corps.L[1] - 10];
  form(g, rectPts(ph[0] - 22, ph[1] - 40, 44, 84), { v: .12, line: 2, grad: .2, seed: 60 });
  form(g, rectPts(ph[0] - 17, ph[1] - 34, 34, 70), { v: .55, line: 1, seed: 61 });
  // les mots sortent en volutes d'encre de sa bouche et entrent dans le téléphone
  const bouche = [corps.head[0] + ART_S * .12, corps.head[1] + ART_S * .12];
  // trois arcs de son partent de la bouche vers le téléphone, en rythme avec la parole
  if (b > .8 && b < 6.4) for (let k = 0; k < 3; k++) {
    const u = ((b - .8) * 1.6 + k / 3) % 1, rr = 10 + u * 34, c = [bouche[0] + ART_S * .08, bouche[1]];
    const pts = []; for (let i = 0; i <= 10; i++) { const aa = -.7 + i * .14; pts.push([c[0] + Math.cos(aa) * rr, c[1] + Math.sin(aa) * rr]); }
    stroke(g, pts, 3.2, { seed: 70 + k, alpha: Math.sin(u * Math.PI) });
  }
  // la bande de télégramme sort du bas du téléphone et descend ; une ligne s'imprime sur chaque coup
  const len = numAt(b, [[1.8, 0], [6, 520]], lin);
  if (len > 2) {
    const x0 = ph[0] - 30, y0 = ph[1] + 44;
    const ondule = y => Math.sin((y - y0) * .02) * 10;
    const bord = []; for (let y = y0; y <= y0 + len; y += 16) bord.push([x0 + ondule(y), y]);
    const pts = [...bord, ...bord.slice().reverse().map(([x, y]) => [x + 60, y])];
    form(g, pts, { v: .93, line: 1.6, seed: 62 });
    for (let i = 0; i < 4; i++) {
      const yy = y0 + 70 + i * 110; if (yy > y0 + len - 20) continue;
      stroke(g, [[x0 + 10 + ondule(yy), yy], [x0 + 46 + ondule(yy), yy]], 3, { seed: 80 + i });
      stroke(g, [[x0 + 10 + ondule(yy + 18), yy + 18], [x0 + 32 + ondule(yy + 18), yy + 18]], 2, { seed: 90 + i, alpha: .7 });
    }
  }
  g.restore();
}
// le visage, en coordonnées du film, pour l'iris à demi
export function visageVoix(t) {
  const lt = t - SEC.VOIX.t0, b = lt / SEC.VOIX.beat;
  const z = lerp(1.35, 1.6, ss(b / 8)), P = telephone();
  const c = bodyAt(ARTISAN, { x: ART_X, ground: SOL, scale: ART_S, yaw: 20, pose: P }).head;
  return [(c[0] - 560) * z + FW / 2, (c[1] - 640) * z + FH / 2];
}

// ============ 3 · LA MAISON (plan d'ensemble, iris qui se ferme) ============
export function maison(g, lt) {
  const B = SEC.MAISON.beat, b = lt / B;
  cuisine(g, { minute: 5 });
  // la porte à droite : elle s'ouvre sur la pièce chaude où l'attend sa famille
  const ouvre = ss(seg(b, 2.4, 3.2));
  form(g, rectPts(690, 470, 260, 520), { v: .45, line: 2.6, seed: 100, shade: 6 });
  form(g, rectPts(706, 486, 228, 504), { v: lerp(.3, .86, ouvre), line: 2, seed: 101 });
  if (ouvre > .05) {
    // la pièce derrière : la lampe, la table, la mère et l'enfant attablés
    g.save(); g.beginPath(); g.rect(706, 486, 228, 504); g.clip();
    form(g, [[730, 560], [910, 560], [880, 520], [760, 520]], { v: .3, line: 1.6, seed: 102 });
    form(g, ellipsePts(820, 860, 100, 22), { v: .62, line: 2, seed: 103 });
    form(g, ellipsePts(765, 720, 32, 38), { v: .25, line: 1.8, seed: 104 }); form(g, [[722, 860], [808, 860], [818, 770], [712, 770]], { v: .22, line: 1.8, seed: 105 });
    form(g, ellipsePts(880, 770, 24, 28), { v: .25, line: 1.8, seed: 106 }); form(g, [[852, 860], [910, 860], [914, 800], [848, 800]], { v: .22, line: 1.8, seed: 107 });
    for (const [x, y] of [[795, 838], [850, 840]]) form(g, ellipsePts(x, y, 16, 6), { v: .9, line: 1.2, seed: 109 + x });
    g.restore();
    // le battant ouvert
    form(g, [[706, 486], [706 + 228 * (1 - ouvre), 500], [706 + 228 * (1 - ouvre), 980], [706, 990]], { v: .4, line: 2.2, seed: 108, shade: 4 });
  }
  // il souffle la pile vers la corbeille, met sa casquette, part vers la porte
  const P = poseAt(b, [[0, debout()], [.5, souffle()], [1.6, souffle()], [2.1, chapeau()], [2.6, debout()],
    [2.9, b2 => { const p = walkPose((b2 - 2.9) * .9, .8); p.expr = DOUX; return p; }], [4.4, b2 => { const p = walkPose((b2 - 2.9) * .9, .8); p.expr = DOUX; return p; }], [4.8, (() => { const p = P0(); p.expr = DOUX; p.headTurn = .3; return p; })()]]);
  const x = numAt(b, [[2.9, ART_X], [4.6, 640]], lin);
  const yaw = numAt(b, [[0, 20], [.4, -40], [1.8, -40], [2.4, 20], [2.9, 80]]);
  drawFigure(g, ARTISAN, { x, ground: SOL, scale: ART_S, yaw, pose: P, t: lt });
  table(g);
  // la corbeille, devant le buffet
  form(g, [[30, 1120], [150, 1120], [138, 1250], [42, 1250]], { v: .35, line: 2.2, seed: 110, shade: 4 });
  // les feuilles s'envolent dans la corbeille
  const u = seg(b, .6, 2.2);
  for (let i = 0; i < 14; i++) {
    const d = rnd(i * 3) * .4, uu = clamp((u - d) / (1 - d));
    if (uu >= 1) continue;
    const x0 = 300 + (rnd(i) - .5) * 160, y0 = TABLE_Y - 20, x1 = 90 + (rnd(i * 7) - .5) * 40, y1 = 1130;
    feuille(g, lerp(x0, x1, uu), lerp(y0, y1, uu) - Math.sin(uu * Math.PI) * 220, 60, uu * 5 * (rnd(i) - .5), .93, 400 + i);
  }
  if (u < .5) pile(g, 300, TABLE_Y, Math.round(lerp(6, 0, u * 2)), 0, 7);
}
export const IRIS_MAISON = [790, 760];
