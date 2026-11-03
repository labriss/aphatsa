// Rend la couche des titres (film/titres.html) en PNG transparents, image par image.
// Usage : node capture-titres.mjs <sortie> <instants en s, séparés par des virgules | début:fin:ips>
import { mkdirSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const [out, when] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
let times;
if (when.includes(":")) {
  const [a, b, fps] = when.split(":").map(Number);
  times = Array.from({ length: Math.round((b - a) * fps) }, (_, i) => a + i / fps);
} else {
  times = when.split(",").map(Number);
}

const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(pathToFileURL(new URL("./film/titres.html", import.meta.url).pathname.slice(1)).href);
await page.evaluate(() => document.fonts.ready);
for (const [i, t] of times.entries()) {
  await page.evaluate((t) => window.rendre(t), t);
  await page.screenshot({ path: `${out}/titres_${String(i + 1).padStart(4, "0")}.png`, omitBackground: true });
}
await browser.close();
console.log(`${times.length} images dans ${out}`);
