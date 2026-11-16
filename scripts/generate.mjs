// Generator profil Pawang.dev. Menulis SVG per section (terang + gelap) dan README.md.
//   node scripts/generate.mjs              -> data live (butuh GH_TOKEN)
//   node scripts/generate.mjs --offline    -> keadaan kosong, tanpa jaringan (tidak ada data karangan)
//   node scripts/generate.mjs --sample --out preview  -> DATA CONTOH untuk pratinjau (bukan data Pawang.dev)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PAL } from "./lib/theme.mjs";
import { esc } from "./lib/text.mjs";
import { fetchGithub, fetchArticles, fetchOgImage, loadIcon, loadBrand, sampleData, sampleArticles, emptyData } from "./lib/data.mjs";
import * as S from "./lib/sections.mjs";
import * as T from "./lib/sections-terminal.mjs";
import { renderTrace } from "./render3d.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const flag = (n) => args.includes("--" + n);
const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 ? args[i + 1] : d; };
const outDir = path.resolve(root, opt("out", "assets"));
const cfg = JSON.parse(fs.readFileSync(path.join(root, "profile.config.json"), "utf8"));
const brandCache = new Map();
const brand = (n) => { if (!brandCache.has(n)) brandCache.set(n, loadBrand(root, n)); return brandCache.get(n); };
const iconCache = new Map();
const icon = (n) => { if (!iconCache.has(n)) iconCache.set(n, loadIcon(root, n)); return iconCache.get(n); };

async function main() {
  let data, articles = null, articlesFailed = false;
  if (flag("sample")) { data = sampleData(); articles = sampleArticles(); }
  else if (flag("offline")) { data = emptyData(); }
  else {
    data = await fetchGithub(process.env.GH_USER || cfg.login, process.env.GH_TOKEN); // gagal -> exit non-zero, tidak menulis apa pun
    if (cfg.sections.articles.enabled) {
      try {
        const items = await fetchArticles(cfg.sections.articles.feed, cfg.sections.articles.limit);
        articles = await Promise.all(items.map(async (it) => ({ ...it, img: await fetchOgImage(it.link) })));
      } catch (e) {
        articlesFailed = true;
        console.warn("RSS gagal, section artikel lama dipertahankan:", String(e.message || e));
      }
    }
  }

  const files = new Map(); // nama file -> isi
  const meta = []; // urutan tumpukan
  const build = (fn, extra = {}) => {
    const per = {};
    let first;
    for (const mode of cfg.modes) {
      const r = fn(PAL[mode], { cfg, data, articles: articles || [], icon, brand, ...extra });
      per[mode] = r;
      first ||= r;
    }
    return { first, per };
  };
  const addSingle = (fn, href, extra) => {
    const { first, per } = build(fn, extra);
    for (const mode of cfg.modes) files.set(`${first.name}-${mode}.svg`, per[mode].svg);
    meta.push({ kind: "single", name: first.name, alt: first.alt, href, w: 800 });
  };
  const addRow = (fn, key, extra, perLine = 0) => {
    const { first, per } = build(fn, extra);
    const rows = first; // array
    rows.forEach((r, i) => {
      for (const mode of cfg.modes) files.set(`${r.name}-${mode}.svg`, per[mode][i].svg);
    });
    meta.push({ kind: "row", key, perLine, items: rows.map((r) => ({ name: r.name, alt: r.alt, href: r.href, w: r.w })) });
  };

  const D = cfg.defaultLink;
  // 3D: three.js + WebGL di headless Chromium -> animasi WebP. Bila gagal, jatuh ke SVG 2D.
  const td = T.traceData(data.days.length ? data.days : []);
  let trace3d = null;
  if (!flag("no3d")) {
    try {
      const t0 = Date.now();
      trace3d = await renderTrace({ weeks: td.weeks, bolts: td.bolts, months: td.months }, { frames: 54, fps: 18 });
      console.log(`3D: ${(trace3d.webp.length / 1024).toFixed(0)} KB WebP, ${((Date.now() - t0) / 1000).toFixed(1)} dtk`);
    } catch (e) {
      console.warn("3D gagal, memakai SVG 2D:", String(e.message || e).split("\n")[0]);
    }
  }
  if (!trace3d && !flag("no3d")) {
    const wp = path.join(outDir, "trace-3d.webp"), st = path.join(outDir, "trace-3d-still.png");
    if (fs.existsSync(wp) && fs.existsSync(st)) { trace3d = { webp: fs.readFileSync(wp), still: fs.readFileSync(st) }; console.warn("Memakai animasi 3D sebelumnya."); }
  }
  // helper: satu irisan SVG bertautan
  const addStack = (fn, extra = {}) => {
    const per = {};
    for (const mode of cfg.modes) per[mode] = fn(PAL[mode], { cfg, data, articles: articles || [], icon, brand, ...extra });
    const first = per[cfg.modes[0]];
    first.forEach((r, i) => {
      for (const mode of cfg.modes) files.set(`${r.name}-${mode}.svg`, per[mode][i].svg);
      meta.push({ kind: "single", name: r.name, alt: r.alt, href: r.href, w: 800 });
    });
  };

  addSingle(S.hero, D);
  addSingle(S.cta, cfg.cta.url);
  addSingle(S.status, D);
  addSingle(S.banner, D);
  addSingle(S.services, D);
  addStack(T.projectWindow);
  addSingle((P, c) => T.traceTop(P, c, td), D);
  if (trace3d) {
    files.set("trace-3d.webp", trace3d.webp);
    files.set("trace-3d-still.png", trace3d.still);
    meta.push({ kind: "anim", name: "trace-3d", alt: "Detak server: kontribusi setahun sebagai ridge 3D dengan petir yang ditangkap", href: D, w: 800 });
  } else {
    const fb = T.traceFallback(PAL[cfg.modes[0]], { cfg, data }, td);
    for (const mode of cfg.modes) files.set(`trace-3d-${mode}.svg`, T.traceFallback(PAL[mode], { cfg, data }, td).svg);
    meta.push({ kind: "single", name: "trace-3d", alt: fb.alt, href: D, w: 800 });
  }
  addSingle((P, c) => T.traceBottom(P, c, td), D);
  addSingle(T.activityWindow, D);
  const haveArticles = articles && articles.length > 0;
  if (haveArticles) { addSingle(S.articlesHead, D); addRow(S.articleCards, "articles"); }
  addSingle(S.connectHead, D);
  addRow(S.socialTiles, "social", {}, 4);
  addSingle(T.footerBar, D);

  // Artikel gagal diambil: pakai file lama kalau ada.
  let keepOldArticles = false;
  if (!haveArticles && articlesFailed) {
    const old = fs.readdirSync(outDir).filter((f) => /^article(s-head)?-?\d*-(light|dark)\.svg$/.test(f));
    keepOldArticles = old.length > 0;
  }

  fs.mkdirSync(outDir, { recursive: true });
  // Bersihkan SVG lama kecuali artikel yang dipertahankan.
  for (const f of fs.readdirSync(outDir)) {
    if (!/\.(svg|webp)$/.test(f) && !/^trace-3d-still\.png$/.test(f)) continue;
    if (keepOldArticles && /^article/.test(f)) continue;
    fs.rmSync(path.join(outDir, f));
  }
  for (const [name, svg] of files) fs.writeFileSync(path.join(outDir, name), svg);

  // README: tumpukan rapat tanpa celah.
  const readmeDir = outDir === path.join(root, "assets") ? root : outDir;
  const rel = path.relative(readmeDir, outDir).split(path.sep).join("/") || ".";
  const pic = (name, alt, w, extra = "") =>
    cfg.modes.length === 1
      ? `<img src="${rel}/${name}-${cfg.modes[0]}.svg" width="${w}" alt="${esc(alt)}" align="top"${extra}>`
      : `<picture><source media="(prefers-color-scheme: dark)" srcset="${rel}/${name}-dark.svg"><img src="${rel}/${name}-light.svg" width="${w}" alt="${esc(alt)}" align="top"${extra}></picture>`;
  const lines = [];
  const stackMeta = [...meta];
  if (keepOldArticles) {
    const at = stackMeta.findIndex((m) => m.name === "connect-head");
    const keep = fs.readdirSync(outDir).filter((f) => /^article-\d+-dark\.svg$/.test(f)).sort();
    stackMeta.splice(at, 0,
      { kind: "single", name: "articles-head", alt: "Tulisan terbaru", href: D, w: 800 },
      { kind: "row", key: "articles", items: keep.map((f) => ({ name: f.replace("-dark.svg", ""), alt: "Tulisan terbaru", href: D, w: 266 })) });
  }
  for (const m of stackMeta) {
    if (m.kind === "anim")
      lines.push(`<a href="${esc(m.href)}"><picture><source media="(prefers-reduced-motion: reduce)" srcset="${rel}/${m.name}-still.png"><img src="${rel}/${m.name}.webp" width="${m.w}" alt="${esc(m.alt)}" align="top"></picture></a><br>`);
    else if (m.kind === "single") lines.push(`<a href="${esc(m.href)}">${pic(m.name, m.alt, m.w)}</a><br>`);
    else {
      const per = m.perLine || m.items.length;
      for (let k = 0; k < m.items.length; k += per)
        lines.push(m.items.slice(k, k + per).map((it) => `<a href="${esc(it.href)}">${pic(it.name, it.alt, it.w)}</a>`).join("") + "<br>");
    }
  }
  const readme = `<!-- Dibuat otomatis oleh scripts/generate.mjs. Jangan edit tangan; ubah profile.config.json atau scripts. -->\n<p align="center">\n${lines.join("\n")}\n</p>\n`;
  fs.writeFileSync(path.join(readmeDir, "README.md"), readme);

  const total = [...files.values()].reduce((a, s) => a + Buffer.byteLength(s), 0);
  console.log(`OK: ${files.size} SVG, ${(total / 1024).toFixed(0)} KB -> ${path.relative(root, outDir) || "."}`);
}

main().catch((e) => { console.error("GAGAL:", e.message || e); process.exit(1); });
