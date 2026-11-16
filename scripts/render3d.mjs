// Render 3D (three.js + WebGL di headless Chromium) menjadi animasi WebP berulang untuk README.
// GitHub tidak menjalankan JavaScript/WebGL di README, jadi adegan dirender di sini lalu dipasang sebagai gambar.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";
import { chromium } from "playwright-core";
import webpmux from "node-webpmux";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MIME = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".woff": "font/woff" };

function serve() {
  const srv = http.createServer((req, res) => {
    const u = decodeURIComponent(req.url.split("?")[0]);
    const map = u === "/" || u === "/trace.html" ? path.join(root, "scripts/scene/trace.html")
      : u.startsWith("/three/") ? path.join(root, "node_modules/three", u.slice(7))
      : u.startsWith("/fonts/") ? path.join(root, "fonts", u.slice(7)) : null;
    if (!map || !map.startsWith(root) || !fs.existsSync(map)) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { "content-type": MIME[path.extname(map)] || "application/octet-stream" });
    fs.createReadStream(map).pipe(res);
  });
  return new Promise((ok) => srv.listen(0, "127.0.0.1", () => ok(srv)));
}

/** Urutan percobaan: PAWANG_CHROME, Chromium dari playwright (CI), Chromium di PLAYWRIGHT_BROWSERS_PATH, Chrome sistem. */
function launchAttempts() {
  const out = [];
  if (process.env.PAWANG_CHROME) out.push({ executablePath: process.env.PAWANG_CHROME });
  out.push({}); // Chromium bawaan playwright-core bila sudah dipasang
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/pw-browsers";
  try {
    for (const d of fs.readdirSync(base).filter((x) => /^chromium-\d+$/.test(x)).sort().reverse()) {
      const p = path.join(base, d, "chrome-linux64", "chrome");
      if (fs.existsSync(p)) out.push({ executablePath: p });
    }
  } catch {}
  out.push({ channel: "chrome" });
  return out;
}

/** data: { weeks:number[], bolts:[{wi,n}], months:[{wi,label}] } -> { webp: Buffer, still: Buffer } */
export async function renderTrace(data, { frames = 54, fps = 18 } = {}) {
  const srv = await serve();
  const port = srv.address().port;
  let browser;
  try {
    let lastErr;
    for (const opt of launchAttempts()) {
      try {
        browser = await chromium.launch({
          ...opt, headless: true,
          args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--no-sandbox", "--disable-dev-shm-usage"],
        });
        break;
      } catch (e) { lastErr = e; }
    }
    if (!browser) throw new Error("Chromium tidak ditemukan: " + String(lastErr?.message || lastErr).split("\n")[0]);
    const page = await browser.newPage({ viewport: { width: 800, height: 300 }, deviceScaleFactor: 1 });
    page.on("pageerror", (e) => { throw e; });
    await page.goto(`http://127.0.0.1:${port}/trace.html`);
    await page.waitForFunction("window.ready === true", null, { timeout: 20000 });
    await page.evaluate("document.fonts.ready");
    await page.evaluate((d) => window.init(d), data);
    const frs = [];
    let still = null;
    const delay = Math.round(1000 / fps);
    for (let f = 0; f < frames; f++) {
      await page.evaluate((t) => window.frame(t), f / frames);
      const png = await page.screenshot({ type: "png", clip: { x: 0, y: 0, width: 800, height: 300 } });
      if (f === Math.round(frames * 0.5)) still = png;
      // tiap frame jadi WebP statis, lalu digabung jadi satu animasi (loop tak berhingga)
      const one = await sharp(png).webp({ quality: 74, effort: 5, smartSubsample: true }).toBuffer();
      frs.push(await webpmux.Image.generateFrame({ buffer: one, delay, x: 0, y: 0, blend: false, dispose: false }));
    }
    const webp = await webpmux.Image.save(null, { frames: frs, width: 800, height: 300, loops: 0, bgColor: [11, 14, 20, 255] });
    return { webp, still: await sharp(still).png({ palette: true, quality: 88 }).toBuffer() };
  } finally {
    if (browser) await browser.close().catch(() => {});
    srv.close();
  }
}
