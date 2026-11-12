// Rend les titres d'une pub en images PNG transparentes, une par image du film.
// Usage : node rendre-titres.mjs <spec.json> <dossier de sortie> [ips=30]
import { mkdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const [specFile, out, ipsArg] = process.argv.slice(2);
const ips = Number(ipsArg || 30);
const spec = JSON.parse(readFileSync(specFile, "utf8"));
mkdirSync(out, { recursive: true });
const ici = dirname(fileURLToPath(import.meta.url));

const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({ viewport: { width: spec.l, height: spec.h }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(resolve(ici, "titres.html")).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.evaluate((s) => window.charger(s), spec);
const n = Math.round(spec.duree * ips);
const scene = page.locator("#scene");
for (let i = 0; i < n; i++) {
  await page.evaluate((t) => window.rendre(t), i / ips);
  await scene.screenshot({ path: `${out}/t_${String(i).padStart(5, "0")}.png`, omitBackground: true });
}
await browser.close();
console.log(`${n} images de titres dans ${out}`);
