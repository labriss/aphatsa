// Filme l'écran du vrai téléphone de la page d'accueil (le film du devis dicté), image par image.
// L'horloge du navigateur est simulée : chaque image tombe exactement à son instant, sans à-coup.
// Usage : node capture-ecran.mjs <sortie> <instants en s, séparés par des virgules | début:fin:ips> [clair|sombre] [métier]
import { mkdirSync } from "node:fs";
import { chromium } from "playwright-core";

const [out, when, theme = "sombre", metier = ""] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
let times;
if (when.includes(":")) {
  const [a, b, fps] = when.split(":").map(Number);
  times = Array.from({ length: Math.round((b - a) * fps) }, (_, i) => a + i / fps);
} else {
  times = when.split(",").map(Number);
}

const browser = await chromium.launch({ channel: "chrome", headless: true });
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 3,
  colorScheme: theme === "clair" ? "light" : "dark",
  reducedMotion: "no-preference",
});
await ctx.addInitScript((t) => localStorage.setItem("theme", t), theme === "clair" ? "light" : "dark");
// Le métier choisi (src/lib/trades.ts) : la dictée et les lignes du film changent avec lui.
if (metier) await ctx.addInitScript((m) => localStorage.setItem("fuiteo:metier", m), metier);
// Sans Element.animate, Motion calcule ses animations lui-même, sur l'horloge simulée : elles tombent juste à chaque image.
await ctx.addInitScript(() => {
  delete Element.prototype.animate;
});
const page = await ctx.newPage();
// L'horloge simulée est arrêtée : le temps du film n'avance que quand on le décide, image par image.
await page.clock.install({ time: new Date("2026-11-03T09:41:00") });
await page.clock.pauseAt(new Date("2026-11-03T09:41:01"));
await page.goto("http://localhost:3000/", { timeout: 180000, waitUntil: "load" });
// Écran aux coins droits : c'est le téléphone 3D qui l'arrondit.
await page.addStyleTag({ content: "nextjs-portal{display:none!important} [data-ui] > div.overflow-hidden{border-radius:0!important}" });
// L'appli s'hydrate en temps réel pendant que le film, lui, reste à zéro.
await page.waitForTimeout(3000);
await page.evaluate(() => document.fonts.ready);
const screen = page.locator("[data-ui] > div.overflow-hidden");
let now = 0;
for (const [i, t] of times.entries()) {
  const ms = Math.round(t * 1000) - now;
  if (ms > 0) {
    // Les animations CSS (l'onde du micro, les pulsations) suivent le temps réel :
    // on les avance du même pas que l'horloge simulée, pour que chaque image soit exacte.
    const step = 1000 / 60;
    for (let done = 0; done < ms; done += step) {
      const d = Math.min(step, ms - done);
      await page.clock.runFor(d);
      await page.evaluate((d) => {
        for (const a of document.getAnimations()) {
          // Les apparitions au défilement (animation-timeline: view()) suivent la page, pas le temps : on les laisse.
          if (a.timeline !== document.timeline || !(a instanceof CSSAnimation || a instanceof CSSTransition)) continue;
          const c = typeof a.currentTime === "number" && Number.isFinite(a.currentTime) ? a.currentTime : 0;
          a.pause();
          a.currentTime = c + d;
        }
      }, d);
    }
  }
  now += Math.max(ms, 0);
  await screen.screenshot({ path: `${out}/ecran_${String(i + 1).padStart(4, "0")}.png`, animations: "allow" });
}
await browser.close();
console.log(`${times.length} images dans ${out}`);
