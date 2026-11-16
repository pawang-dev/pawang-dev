// Tema: Cyber-Nusantara / Mystical Terminal. Satu palet gelap (wajib dark mode).
import { esc, glyphDefs } from "./text.mjs";

export const W = 800;

export const PAL = {
  dark: {
    mode: "dark",
    bg: "#0B0E14", // Void Dark
    card: "#151A23", // Smoke Incense
    cardBorder: "#1F2633", // Cloud Slate
    line2: "#2B3548", // garis yang sedikit lebih terang
    accent: "#FACC15", // Lightning Gold (CTA); teks di atasnya #0B0E14
    accentInk: "#FACC15",
    onAccent: "#0B0E14",
    ok: "#10B981", // Tamed Emerald
    err: "#EF4444", // Danger Bug
    ink: "#F8FAFC",
    mute: "#94A3B8",
    cyan: "#06B6D4",
    purple: "#A855F7",
    orange: "#F97316",
  },
};

export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s += 0x6d2b79f5;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}";

/** Pembungkus SVG. Latar rata Void Dark supaya tumpukan section menyatu; grid titik opsional (hanya hero/footer). */
export function doc(P, { w = W, h, label, defs = "", css = "", body, grid = false }) {
  const pattern = grid
    ? `<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="${P.line2}"/></pattern>` +
      `<linearGradient id="dotfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>` +
      `<mask id="dotmask"><rect width="${w}" height="${h}" fill="url(#dotfade)"/></mask>`
    : "";
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="${esc(label)}">` +
    `<title>${esc(label)}</title>` +
    `<defs>${pattern}${defs}${glyphDefs(body)}</defs>` +
    `<style>${css}${REDUCED}</style>` +
    `<rect width="${w}" height="${h}" fill="${P.bg}"/>` +
    (grid ? `<rect width="${w}" height="${h}" fill="url(#dots)" mask="url(#dotmask)" opacity=".8"/>` : "") +
    body +
    `</svg>`
  );
}
