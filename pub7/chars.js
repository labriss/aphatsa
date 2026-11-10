// Cast of The Runaway Loaf (all original). Values are print densities (0 = black, 1 = white).
import { form, stroke, ink, catmull, grey, pathOf, ellipsePts, INK, hatch } from './engine/ink.js';
import { torsoPoint } from './engine/figure.js';
import { PROFILE_ADULT, PROFILE_CHILD, FRONT_ADULT, FRONT_CHILD } from './engine/heads.js';

const lerp = (a, b, t) => a + (b - a) * t;
const ss = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
// blend a head-local shape between front / profile / back sets (same point count). pts in head units.
export function headShape(H, frontPts, profPts, backPts) {
  const w = ss(.35, .95, H.p);
  const base = H.front >= 0 ? frontPts : (backPts || frontPts);
  const fm = H.front >= 0 ? H.f : -H.f;          // asymmetric front shapes follow the facing side
  return base.map((q, i) => { const r = profPts[i]; return [lerp(q[0] * fm, r[0] * H.f, w) * H.sc, lerp(q[1], r[1], w) * H.sc]; });
}
const loop = (pts, n = 5) => catmull(pts, true, n);

// casquette plate : calotte bombée et visière
const flatF = [[-.42, -.24], [-.46, -.38], [-.36, -.52], [-.12, -.6], [.14, -.6], [.38, -.53], [.48, -.4], [.44, -.25], [0, -.3]];
const flatP = [[-.42, -.16], [-.48, -.32], [-.38, -.5], [-.14, -.6], [.14, -.6], [.36, -.52], [.5, -.38], [.48, -.24], [0, -.28]];
const peakF = [[-.36, -.26], [0, -.3], [.36, -.26], [.34, -.2], [0, -.22], [-.34, -.2]];
const peakP = [[.18, -.26], [.46, -.26], [.66, -.2], [.64, -.16], [.44, -.18], [.18, -.2]];
// ---------------- L'ARTISAN : plombier, casquette plate, salopette sombre sur chemise claire ----------------
const ottoHairF = [[-.36, -.08], [-.37, -.3], [-.25, -.46], [0, -.52], [.25, -.46], [.37, -.3], [.36, -.08], [.3, -.2], [.18, -.27], [.05, -.24], [-.1, -.28], [-.25, -.24]];
const ottoHairP = [[-.38, .18], [-.44, -.1], [-.32, -.42], [-.05, -.52], [.2, -.47], [.33, -.33], [.3, -.26], [.2, -.3], [.12, -.22], [.02, -.14], [-.02, .02], [-.2, .2]];
const ottoHairB = [[-.36, .1], [-.4, -.2], [-.28, -.44], [0, -.52], [.28, -.44], [.4, -.2], [.36, .1], [.25, .22], [.12, .25], [0, .26], [-.12, .25], [-.25, .22]];
// soft pleated baker's cap, flopped to the character's right
const capF = [[-.38, -.33], [-.41, -.41], [-.34, -.5], [-.14, -.55], [.1, -.55], [.3, -.52], [.44, -.46], [.45, -.4], [.4, -.34], [0, -.36]];
const capP = [[-.44, -.24], [-.5, -.34], [-.45, -.46], [-.24, -.55], [0, -.57], [.22, -.54], [.36, -.46], [.4, -.39], [.37, -.31], [0, -.35]];
const capBandF = [[-.37, -.22], [0, -.25], [.37, -.22], [.4, -.28], [.39, -.35], [0, -.37], [-.39, -.35], [-.4, -.28]];
const capBandP = [[-.44, -.14], [0, -.24], [.37, -.21], [.39, -.27], [.38, -.33], [0, -.36], [-.45, -.26], [-.46, -.19]];
export const ARTISAN = {
  name: 'Artisan', body: 'adult', line: .028,
  skin: { v: .8 }, handW: .3, neckW: .4,
  leg: { v: .22, w: [.58, .46, .4], folds: true, patch: false, gap: 5.5 },
  shoe: { v: .12 },
  arm: { v: .9, w: [.36, .31, .27], sleeve: .5, foreW: [.26, .19] },
  torso: { v: .9, grad: .2 },
  vest: { v: .2, shoulder: .55, bottom: -.1 },
  torsoW: 1.0, torsoD: 1.0,
  torsoDetail(g, J, pr, s, lw, face) {
    if (s < 14) return;
    const T = (xf, y, xs) => torsoPoint(J, pr, xf, y, xs);
    const fv = pr.cy > -.25, ps = Math.abs(pr.sy);
    if (fv) {
      // shirt showing in the waistcoat's V + the waistcoat's front edges, buttons and a watch chain
      const v = [T(-.3, 2.3, .14), T(0, 1.62, .42), T(.3, 2.3, .3), T(.12, 2.36, .24), T(-.12, 2.36, .1)];
      form(g, loop(v, 3), { v: .9, line: lw * .8, grad: .1, seed: 236 });
      stroke(g, [T(0, 1.62, .42), T(ps > .85 ? .02 : .02, .8, .4)], lw * .8, { seed: 237 });
      for (let i = 0; i < 4; i++) { const q = T(.06, 1.5 - i * .2, .43); g.fillStyle = grey(.62); g.beginPath(); g.arc(q[0], q[1], s * .02, 0, 7); g.fill(); }
      const w0 = T(.06, 1.3, .43), w1 = T(-.35, 1.18, .3), w2 = T(-.45, 1.32, .12);
      stroke(g, catmull([w0, [lerp(w0[0], w1[0], .5), lerp(w0[1], w1[1], .5) + s * .06], w1, w2], false, 5), lw * .55, { color: grey(.82), seed: 238, alpha: .9 });
      // pocket welts
      if (ps < .8) { stroke(g, [T(-.52, 1.28), T(-.26, 1.3)], lw * .6, { color: grey(.5), seed: 239 }); stroke(g, [T(.26, 1.3), T(.52, 1.28)], lw * .6, { color: grey(.5), seed: 240 }); }
    } else {
      stroke(g, [T(-.3, 1.9, 0), T(.3, 1.9, 0)], lw * .6, { seed: 244, alpha: .6 });   // back strap
      stroke(g, [T(0, 1.4, 0), T(0, .8, 0)], lw * .5, { seed: 245, alpha: .6 });
    }
  },
  collar(g, J, pr, s, lw, face) {
    const T = (xf, y, xs) => torsoPoint(J, pr, xf, y, xs);
    // neckerchief (dark) tucked into a white stand collar
    if (pr.cy > -.3) {
      const k = T(0, 2.3, .2);
      const knot = loop([[k[0] - s * .09, k[1] - s * .06], [k[0] + s * .09, k[1] - s * .06], [k[0] + s * .07, k[1] + s * .07], [k[0] - s * .07, k[1] + s * .07]], 4);
      const tails = loop([[k[0] - s * .05, k[1] + s * .04], [k[0] + s * .06, k[1] + s * .04], [k[0] + s * .11 * face, k[1] + s * .3], [k[0] - s * .02, k[1] + s * .26]], 4);
      form(g, tails, { v: .2, line: lw * .8, hatch: .3, seed: 241 }); form(g, knot, { v: .17, line: lw * .8, hatch: .3, seed: 242 });
    }
    // stand collar: hugs the neck, open in a small V at the front
    const c = pr.cy > -.3 ? loop([T(-.26, 2.33, -.22), T(-.05, 2.28, .16), T(0, 2.4, .22), T(.05, 2.28, .2), T(.26, 2.33, .24), T(.24, 2.5, .2), T(0, 2.47, -.03), T(-.24, 2.5, -.24)], 4)
      : loop([T(-.26, 2.33, -.22), T(.26, 2.33, .24), T(.24, 2.5, .2), T(-.24, 2.5, -.24)], 4);
    form(g, c, { v: .92, line: lw * .85, grad: .18, hatch: 0, seed: 243 });
  },
  head: {
    skin: .82, jaw: 1, chinW: .44, brow: 2.1, lip: .36, profile: PROFILE_ADULT,
    hairMass: { v: .13, top: -.2, nape: .22, temple: .2, fringe: true },
    _oldHair(g, H) {
      const pts = loop(headShape(H, ottoHairF, ottoHairP, ottoHairB));
      form(g, pts, { v: .13, line: H.lw * .8, grad: .1, hatch: .2, seed: 211 });
      // hair texture: lighter combed strokes
      for (let i = 0; i < 7; i++) {
        const u = i / 6, a = headShape(H, [[lerp(-.3, .3, u), -.34]], [[lerp(-.3, .25, u), -.36]])[0], b = headShape(H, [[lerp(-.34, .34, u) + .04, -.12 - Math.abs(u - .5) * .1]], [[lerp(-.38, .1, u), -.08 + u * .06]])[0];
        stroke(g, [a, b], H.lw * .45, { color: grey(.42), seed: 212 + i, alpha: .8 });
      }
    },
    hat(g, H) {
      const crown = loop(headShape(H, flatF, flatP, flatF), 5);
      form(g, crown, { v: .32, line: H.lw, grad: .24, hatch: .35, seed: 221, shade: { off: H.sc * .06, a: .16, hatch: .3, seed: 229 } });
      const peak = loop(headShape(H, peakF, peakP, peakF), 4);
      form(g, peak, { v: .2, line: H.lw, grad: .2, hatch: .3, seed: 222 });
      const sh = headShape(H, [[-.35, -.2], [0, -.23], [.35, -.2], [.32, -.13], [0, -.16], [-.32, -.13]], [[-.3, -.12], [0, -.22], [.4, -.18], [.36, -.12], [0, -.16], [-.3, -.08]]);
      g.fillStyle = 'rgba(30,24,20,.24)'; pathOf(g, loop(sh, 3)); g.fill();
    },
  },
};

// ---------------- THE GIRL ----------------
const beretF = [[-.42, -.2], [-.5, -.34], [-.44, -.5], [-.2, -.62], [.12, -.64], [.4, -.56], [.55, -.42], [.5, -.28], [.36, -.22], [0, -.3]];
const beretP = [[-.4, -.14], [-.5, -.3], [-.44, -.48], [-.2, -.62], [.1, -.64], [.35, -.56], [.48, -.42], [.44, -.28], [.34, -.24], [0, -.3]];
const gHairF = [[-.42, .3], [-.4, -.1], [-.3, -.32], [0, -.38], [.3, -.32], [.4, -.1], [.42, .3], [.34, .1], [.3, -.12], [.1, -.2], [-.1, -.2], [-.3, -.12], [-.34, .1]];
const gHairP = [[-.3, .36], [-.44, .05], [-.38, -.3], [-.05, -.4], [.25, -.34], [.34, -.2], [.3, -.14], [.18, -.18], [.08, -.1], [0, 0], [-.05, .12], [-.12, .3], [-.2, .38]];
export const ENFANT = {
  name: 'Enfant', body: 'child', line: .034,
  skin: { v: .82 }, handW: .36, neckW: .3,
  leg: { v: .8, w: [.34, .27, .24], folds: false },          // bare knees / pale stockings
  shoe: { v: .16 },
  arm: { v: .3, w: [.36, .33, .3], sleeve: 1 },
  torso: { v: .3, grad: .18 },
  torsoW: 1.08,
  skirt: { front: true, v: .3, top: .95, len: 1.55, wz: .72, fx: .48, topW: 1, hemW: 1.35, hatch: .35 },
  collar(g, J, pr, s, lw) {       // scarf
    const n = pr.P(J.neck);
    const pts = loop([[n[0] - s * .36, n[1] - s * .12], [n[0] + s * .36, n[1] - s * .12], [n[0] + s * .38, n[1] + s * .08], [n[0], n[1] + s * .14], [n[0] - s * .38, n[1] + s * .08]], 4);
    form(g, pts, { v: .6, line: lw * .8, hatch: .1, seed: 301 });
    for (let i = -1; i <= 1; i++) stroke(g, [[n[0] + i * s * .2 - s * .05, n[1] - s * .1], [n[0] + i * s * .2 + s * .03, n[1] + s * .1]], lw * 1.1, { seed: 302 + i, alpha: .6 });
  },
  head: {
    skin: .82, jaw: .92, chinW: .5, brow: 1.2, lip: .45, profile: PROFILE_CHILD, front: FRONT_CHILD, eyeH: 1.35, eyeY: .0, makeup: .7, nose: .85,
    hairBack(g, H) { const pts = loop(headShape(H, gHairF, gHairP)); form(g, pts, { v: .22, line: H.lw * .8, grad: .12, hatch: .3, seed: 311 }); },
    hat(g, H) {
      const pts = loop(headShape(H, beretF, beretP), 5);
      form(g, pts, { v: .2, line: H.lw, grad: .2, hatch: .45, seed: 321 });
      const c = headShape(H, [[.08, -.64]], [[.05, -.64]])[0];
      stroke(g, [c, [c[0] + .02 * H.sc, c[1] - .07 * H.sc]], H.lw * 1.4, { seed: 322 });
    },
  },
};

