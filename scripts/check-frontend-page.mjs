/**
 * Smoke-test do login no Vite dev (captura erros JS).
 * Uso: node scripts/check-frontend-page.mjs [url]
 */
import { chromium } from "playwright";

const url = process.argv[2] || "http://127.0.0.1:5173/login";

const errors = [];
const browser = await chromium.launch();
const page = await browser.newPage();
page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));
page.on("console", (m) => {
  if (m.type() === "error") errors.push(`console: ${m.text()}`);
});

await page.goto(url, { waitUntil: "networkidle", timeout: 60_000 });
const text = await page.locator("body").innerText();
console.log("URL:", url);
console.log("BODY_TEXT_LEN:", text.length);
console.log("BODY_SNIP:", text.slice(0, 400).replace(/\s+/g, " "));
console.log("ERRORS:", errors.length ? errors : "(none)");
await browser.close();
process.exit(errors.length || text.length < 20 ? 1 : 0);
