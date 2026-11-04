// Rend la couverture du post (film/couverture.html) en PNG, sur une image du téléphone.
// Usage : node capture-couverture.mjs <image de fond> <sortie.png>
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const [fond, out] = process.argv.slice(2);
const browser = await chromium.launch({ channel: "chrome", headless: true, args: ["--allow-file-access-from-files"] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
const html = pathToFileURL(new URL("./film/couverture.html", import.meta.url).pathname.slice(1)).href;
await page.goto(`${html}?fond=${encodeURIComponent(pathToFileURL(resolve(fond)).href)}`);
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => document.getElementById("fond").complete);
await page.screenshot({ path: out });
await browser.close();
console.log(out);
