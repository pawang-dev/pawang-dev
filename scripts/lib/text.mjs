// Teks diubah jadi path (outline) dari font Plus Jakarta Sans + Inter yang ada di repo.
// Hasilnya: tampilan konsisten tanpa font eksternal, dan lebar teks bisa diukur persis.
import opentype from "opentype.js";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const FD = path.join(here, "..", "..", "fonts");
const load = (f) => {
  const b = fs.readFileSync(path.join(FD, f));
  return opentype.parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
};

export const FONTS = {
  jk800: load("plus-jakarta-sans-latin-800-normal.woff"),
  jk700: load("plus-jakarta-sans-latin-700-normal.woff"),
  // Plus Jakarta Sans untuk heading dan isi; JetBrains Mono untuk kode, badge, istilah teknis.
  in600: load("plus-jakarta-sans-latin-600-normal.woff"),
  in400: load("plus-jakarta-sans-latin-400-normal.woff"),
  m400: load("jetbrains-mono-latin-400-normal.woff"),
  m700: load("jetbrains-mono-latin-700-normal.woff"),
};

const clean = (font, s) => {
  // Karakter di luar font diganti agar tidak muncul kotak kosong.
  let out = "";
  for (const ch of String(s).normalize("NFC")) {
    if (ch === "\n" || ch === "\t") { out += " "; continue; }
    const g = font.charToGlyph(ch);
    out += g && g.index !== 0 ? ch : "·";
  }
  return out;
};

const GLYPHS = new Map(); // id -> path data (satuan em font, y ke bawah, garis dasar di 0)
function layout(fontKey, str, trackUnits = 0) {
  const f = FONTS[fontKey];
  const s = clean(f, str);
  const items = [];
  let x = 0, prev = null;
  for (const ch of s) {
    const g = f.charToGlyph(ch);
    if (prev) x += f.getKerningValue(prev, g) || 0;
    if (ch !== " ") {
      const id = `g${fontKey}-${g.index}`;
      if (!GLYPHS.has(id)) GLYPHS.set(id, g.getPath(0, 0, f.unitsPerEm).toPathData(0));
      items.push([id, Math.round(x)]);
    }
    x += g.advanceWidth + trackUnits;
    prev = g;
  }
  return { adv: x, items, s };
}
const advW = (fontKey, size, str) => (layout(fontKey, str).adv * size) / FONTS[fontKey].unitsPerEm;

export function width(fontKey, size, str) {
  return advW(fontKey, size, str);
}

/** <defs> glyph yang dipakai body; dipanggil oleh doc(). */
export function glyphDefs(body) {
  const ids = new Set([...body.matchAll(/href="#(g[a-z]+\d+-\d+)"/g)].map((m) => m[1]));
  return [...ids].map((id) => `<path id="${id}" d="${GLYPHS.get(id)}"/>`).join("");
}

const r1 = (n) => Math.round(n * 10) / 10;

/** Satu baris teks sebagai deretan <use> glyph. anchor: start | middle | end */
export function text(fontKey, size, str, x, y, { fill = "#000", anchor = "start", opacity = 1, track = 0 } = {}) {
  const f = FONTS[fontKey];
  const L = layout(fontKey, str, (track * f.unitsPerEm) / size);
  const k = size / f.unitsPerEm;
  const w = L.adv * k;
  const x0 = anchor === "middle" ? x - w / 2 : anchor === "end" ? x - w : x;
  const o = opacity !== 1 ? ` fill-opacity="${opacity}"` : "";
  return `<g transform="translate(${r1(x0)} ${r1(y)}) scale(${Math.round(k * 100000) / 100000})" fill="${fill}"${o}>${L.items.map(([id, gx]) => `<use href="#${id}" x="${gx}"/>`).join("")}</g>`;
}

/** Potong teks jadi beberapa baris sesuai lebar; baris terakhir diberi elipsis bila terpotong. */
export function wrap(fontKey, size, str, maxW, maxLines = 3) {
  const f = FONTS[fontKey];
  const words = clean(f, str).split(/\s+/).filter(Boolean);
  const W_ = (t) => advW(fontKey, size, t);
  const lines = [];
  let cur = "";
  let i = 0;
  for (; i < words.length; i++) {
    const t = cur ? cur + " " + words[i] : words[i];
    if (W_(t) <= maxW) { cur = t; continue; }
    if (!cur) {
      cur = words[i];
      while (cur.length > 1 && W_(cur + "…") > maxW) cur = cur.slice(0, -1);
      cur += "…";
      lines.push(cur); cur = "";
      if (lines.length === maxLines) { i++; break; }
      continue;
    }
    lines.push(cur); cur = words[i];
    if (lines.length === maxLines) break;
  }
  if (lines.length < maxLines && cur) { lines.push(cur); i = words.length; }
  const consumed = lines.join(" ").split(/\s+/).length;
  if (lines.length === maxLines && (consumed < words.length || i < words.length)) {
    let last = lines[maxLines - 1];
    while (last.length > 1 && W_(last + "…") > maxW) last = last.slice(0, -1);
    if (!last.endsWith("…")) last = last.replace(/[\s.,;:!?-]+$/, "") + "…";
    lines[maxLines - 1] = last;
  }
  return lines;
}

/** Teks berbaris: kembalikan { svg, lines }. */
export function paragraph(fontKey, size, str, x, y, maxW, maxLines, lineH, opt = {}) {
  const lines = wrap(fontKey, size, str, maxW, maxLines);
  const svg = lines.map((l, k) => text(fontKey, size, l, x, y + k * lineH, opt)).join("");
  return { svg, lines };
}

/** Potong satu baris agar muat di lebar tertentu. */
export function fit(fontKey, size, str, maxW) {
  let s = clean(FONTS[fontKey], str);
  if (advW(fontKey, size, s) <= maxW) return s;
  while (s.length > 1 && advW(fontKey, size, s + "…") > maxW) s = s.slice(0, -1);
  return s.replace(/\s+$/, "") + "…";
}

export const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
export const round1 = r1;
