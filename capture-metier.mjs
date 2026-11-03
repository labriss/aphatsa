// Filme la scène de réparation d'un métier (page /metiers/<métier>), du début à la fin du travail.
// Le travail avance avec le défilement : on fait défiler la section par petits pas, horloge simulée.
// Usage : node capture-metier.mjs <métier> <sortie> <nombre d'images> [avancement de départ 0–1] [avancement de fin 0–1]
import { mkdirSync } from "node:fs";
import { chromium } from "playwright-core";

const [trade, out, count = "1", from = "0.98", to = from] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const n = Number(count);

const browser = await chromium.launch({ channel: "chrome", headless: true });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, colorScheme: "dark" });
await ctx.addInitScript(() => {
  localStorage.setItem("theme", "dark");
  delete Element.prototype.animate;
});
const page = await ctx.newPage();
await page.clock.install({ time: new Date("2026-11-03T09:41:00") });
await page.clock.pauseAt(new Date("2026-11-03T09:41:01"));
await page.goto(`http://localhost:3000/metiers/${trade}`, { timeout: 180000, waitUntil: "load" });
await page.addStyleTag({ content: "nextjs-portal{display:none!important} html{scroll-behavior:auto!important}" });
await page.waitForTimeout(2500);
const { top, height } = await page.evaluate(() => {
  const s = document.querySelector('svg[viewBox="0 0 400 400"]').closest("section");
  const r = s.getBoundingClientRect();
  return { top: r.top + scrollY, height: r.height };
});
const svg = page.locator('section svg[viewBox="0 0 400 400"]').first();
for (let i = 0; i < n; i++) {
  const f = n === 1 ? Number(from) : Number(from) + ((Number(to) - Number(from)) * i) / (n - 1);
  await page.evaluate((y) => window.scrollTo(0, y), top + (height - 844) * f);
  // Le défilement est amorti par un ressort : on lui laisse le temps (simulé) de se poser.
  await page.clock.runFor(n === 1 ? 2000 : 34);
  await svg.screenshot({ path: `${out}/${trade}_${String(i + 1).padStart(4, "0")}.png` });
}
await browser.close();
console.log(`${n} images dans ${out}`);
