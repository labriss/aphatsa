// Le Soir du plombier — montage. Écran vertical 1080×1920 : une salle de cinéma dans le noir, l'image projetée
// au centre en 3:4 debout (1000×1333), un lambrequin de velours en haut, la rampe et les têtes des spectateurs en bas.
// Chaîne d'une image : plan tonal → Redraw (encre, lavis, hachures) → iris → FilmPost (tirage, grain, rayures) → poussières.
// Le mouvement est échantillonné à 16 i/s (« manivelle ») ; le scintillement et le flottement changent à chaque image.
import { Redraw } from './engine/redraw.js';
import { FilmPost, damage } from './engine/film.js';
import { intertitle, iris } from './engine/cards.js';
import { setFrame, S as IS } from './engine/ink.js';
import { SEC, DUR as D, HIT, secAt } from './timeline.js';
import { CARDS, LOGO } from './cardspecs.js';
import * as SH from './shots.js';

export const DUR = D;
const W = 1080, H = 1920, FW = SH.FW, FH = SH.FH, GATE = { x: 40, y: 250, w: FW, h: FH };
const mk = () => { const c = document.createElement('canvas'); c.width = FW; c.height = FH; return c; };
const fc = mk(), fg = fc.getContext('2d'), mask = mk(), mg = mask.getContext('2d');
let RD = null, FP = null;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = x => { x = clamp(x); return x * x * (3 - 2 * x); };

// l'aspect de la copie par section : str = abîmé, sepia (plus chaud quand le film devient tendre), fps = manivelle
const LOOK = {
  PRE: { str: .7, sepia: .12, fps: 16 }, CARD1: { str: .6, sepia: .12, fps: 16 },
  GAG: { str: .85, sepia: .1, fps: 18, crank: 1.3 }, CARD2: { str: .5, sepia: .16, fps: 16 },
  VOIX: { str: .45, sepia: .22, fps: 16 }, CARD3: { str: .4, sepia: .26, fps: 16 },
  MAISON: { str: .32, sepia: .34, fps: 16 }, FIN: { str: .35, sepia: .32, fps: 16 },
};
const SHOTS = { GAG: SH.gag, VOIX: SH.voix, MAISON: SH.maison };

export function renderFilm(g, t) {
  RD = RD || new Redraw(FW, FH); FP = FP || new FilmPost(FW, FH);
  const sec = secAt(t), look = LOOK[sec.name], frame = Math.floor(t * 24 + 1e-6);
  const ta = Math.floor(t * look.fps + 1e-6) / look.fps, lt = Math.max(0, ta - sec.t0);
  fg.setTransform(1, 0, 0, 1, 0, 0); fg.globalAlpha = 1; fg.globalCompositeOperation = 'source-over'; fg.filter = 'none';
  let src = fc, exposure = 1, colour = null;
  const card = CARDS[sec.name];
  if (sec.name === 'PRE') {
    // la lampe du projecteur s'allume : l'amorce « 3 · 2 · 1 » sur fond gris
    const u = (t - HIT.lampe) / (SEC.PRE.t1 - HIT.lampe);
    fg.fillStyle = '#bdb7ab'; fg.fillRect(0, 0, FW, FH);
    if (u > 0) {
      const n = 3 - Math.min(2, Math.floor(u * 3)), a = (u * 3 % 1) * Math.PI * 2;
      fg.strokeStyle = '#2a2622'; fg.lineWidth = 6; fg.beginPath(); fg.arc(FW / 2, FH / 2, 300, 0, 7); fg.stroke(); fg.beginPath(); fg.arc(FW / 2, FH / 2, 250, 0, 7); fg.stroke();
      fg.fillStyle = 'rgba(40,36,32,.35)'; fg.beginPath(); fg.moveTo(FW / 2, FH / 2); fg.arc(FW / 2, FH / 2, 250, -Math.PI / 2, -Math.PI / 2 + a); fg.fill();
      fg.beginPath(); fg.moveTo(0, FH / 2); fg.lineTo(FW, FH / 2); fg.moveTo(FW / 2, 0); fg.lineTo(FW / 2, FH); fg.lineWidth = 3; fg.stroke();
      fg.fillStyle = '#1c1915'; fg.font = '900 300px "Playfair Display SC"'; fg.textAlign = 'center'; fg.textBaseline = 'middle'; fg.fillText(String(n), FW / 2, FH / 2 + 10);
    }
    exposure = .25 + .75 * ss((t - HIT.lampe) / .5);
  } else if (card) {
    intertitle(fg, FW, FH, card, t - sec.t0);
    if (sec.name === 'FIN') {           // le logo Diktéo : la seule couleur du film
      mg.clearRect(0, 0, FW, FH); logo(mg, LOGO.cx, LOGO.cy, LOGO.size, true); logo(fg, LOGO.cx, LOGO.cy, LOGO.size, false); colour = mask;
    }
  } else {
    setFrame(ta, { boil: 1 }); IS.sepLine = .5;
    fg.fillStyle = '#fff'; fg.fillRect(0, 0, FW, FH);
    fg.save(); SHOTS[sec.name](fg, lt); fg.restore();
    src = RD.render(fc, { frame });
  }
  const ir = irisAt(t);
  if (ir) { if (src !== fc) { fg.setTransform(1, 0, 0, 1, 0, 0); fg.drawImage(src, 0, 0); src = fc; } iris(fg, FW, FH, ir.x, ir.y, ir.r, 4); }
  const fp = { frame, strength: look.str, sepia: look.sepia, crank: look.crank ?? 1, exposure };
  if (card) fp.halation = 1.4;
  const dev = FP.render(src, fp, colour);
  salle(g, Math.max(.3, FP.mean * exposure), t);
  g.save(); g.beginPath(); g.roundRect(GATE.x, GATE.y, GATE.w, GATE.h, 20); g.clip();
  g.drawImage(dev, GATE.x, GATE.y); damage(g, GATE.x, GATE.y, FW, FH, frame, look.str);
  g.restore();
  public_(g, t);
}

// le logo Diktéo (tuile orange, bulle « D » qui parle) ; en niveaux de gris pour l'image, en couleur pour le masque
function logo(g, cx, cy, s, couleur) {
  g.save(); g.translate(cx - s / 2, cy - s / 2);
  const r = s * .28;
  g.beginPath(); g.roundRect(0, 0, s, s, r);
  g.fillStyle = couleur ? '#D9580D' : '#7a7a7a'; g.fill();
  g.scale(s / 24, s / 24); g.translate(2.4, 1.6);
  const p = new Path2D('M6.5 2.5H12a9 9 0 0 1 0 18H9.2L4.5 23V4.5a2 2 0 0 1 2-2ZM9.2 9.5a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-1-1Zm3.1-2.5a1 1 0 0 0-1 1v7a1 1 0 0 0 2 0V8a1 1 0 0 0-1-1Zm3.1 2a1 1 0 0 0-1 1v3a1 1 0 0 0 2 0v-3a1 1 0 0 0-1-1Z');
  g.scale(.8, .8); g.fillStyle = couleur ? '#FFF4EA' : '#f0f0f0'; g.fill(p, 'evenodd');
  g.restore();
}

// la salle : le noir, le velours du lambrequin et des côtés éclairé par l'écran, la rampe chaude en bas
function salle(g, spill, t) {
  g.fillStyle = '#050404'; g.fillRect(0, 0, W, H);
  const velours = (x, y, w, h, vertical) => {
    const n = vertical ? 4 : 12, step = (vertical ? w : w) / n;
    for (let i = 0; i < n; i++) {
      const xa = x + i * step, gr = g.createLinearGradient(xa, 0, xa + step, 0), L = .04 + spill * .14;
      gr.addColorStop(0, `rgb(${L * 300 | 0},${L * 150 | 0},${L * 130 | 0})`); gr.addColorStop(.5, `rgb(${L * 120 | 0},${L * 55 | 0},${L * 50 | 0})`); gr.addColorStop(1, `rgb(${L * 280 | 0},${L * 140 | 0},${L * 120 | 0})`);
      g.fillStyle = gr; g.fillRect(xa, y, step + 1, h);
    }
  };
  velours(0, 0, W, 210, false);
  // franges du lambrequin
  g.fillStyle = `rgba(150,110,60,${.25 + spill * .3})`; for (let x = 0; x < W; x += 14) g.fillRect(x, 200, 6, 26);
  const lg = g.createLinearGradient(0, 0, 0, 230); lg.addColorStop(0, 'rgba(0,0,0,.7)'); lg.addColorStop(1, 'rgba(0,0,0,.1)'); g.fillStyle = lg; g.fillRect(0, 0, W, 230);
  // la lueur de l'écran autour de la toile
  g.save(); g.shadowColor = `rgba(230,215,190,${.18 * spill})`; g.shadowBlur = 80; g.fillStyle = '#0b0a09'; g.fillRect(GATE.x, GATE.y, GATE.w, GATE.h); g.restore();
  // la rampe : lumière chaude qui monte du bord de la scène
  const fl = g.createRadialGradient(W / 2, H + 60, 40, W / 2, H + 60, 700);
  fl.addColorStop(0, 'rgba(255,170,110,.35)'); fl.addColorStop(.6, 'rgba(160,70,40,.1)'); fl.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = fl; g.fillRect(0, GATE.y + GATE.h, W, H);
}
// les têtes des spectateurs, en ombres chinoises, devant l'écran
function public_(g, t) {
  g.fillStyle = '#020202';
  const tetes = [[90, 1860, 70], [250, 1880, 78], [420, 1850, 72], [600, 1875, 80], [770, 1855, 70], [950, 1880, 76]];
  for (const [x, y, r] of tetes) {
    const dx = Math.sin(t * .7 + x) * 3;
    g.beginPath(); g.ellipse(x + dx, y - r * .9, r * .62, r * .78, 0, 0, 7); g.fill();
    g.beginPath(); g.ellipse(x + dx, y + r * .6, r * 1.25, r * .9, 0, 0, 7); g.fill();
  }
}

// iris : à demi tenu sur son visage quand il lève le sourcil ; il se ferme sur la table de famille à la fin
function irisAt(t) {
  const full = 1800;
  if (t >= HIT.sourcil - .4 && t < SEC.VOIX.t1) {
    const c = SH.visageVoix(t), k = ss((t - (HIT.sourcil - .4)) / .5);
    return { x: c[0], y: c[1], r: full - (full - 300) * k };
  }
  if (t >= HIT.iris && t < SEC.MAISON.t1) {
    const k = ss((t - HIT.iris) / (SEC.MAISON.t1 - HIT.iris));
    return { x: SH.IRIS_MAISON[0], y: SH.IRIS_MAISON[1], r: Math.max(.5, full * (1 - k)) };
  }
  return null;
}

export function events() {
  const ev = [];
  for (const k in SEC) ev.push({ t: SEC[k].t0, type: 'section', name: k });
  for (const k in HIT) ev.push({ t: HIT[k], type: 'hit', name: k });
  return ev.sort((a, b) => a.t - b.t);
}
