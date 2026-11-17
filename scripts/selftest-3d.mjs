// Uji render 3D (butuh Chromium): memastikan three.js + WebGL + perakit WebP benar-benar menghasilkan animasi.
// Dipakai di CI supaya bump three/playwright-core tidak diam-diam merusak animasi.
import assert from "node:assert/strict";
import sharp from "sharp";
import { renderTrace } from "./render3d.mjs";

const weeks = Array.from({ length: 53 }, (_, i) => Math.max(0, Math.round(6 + 5 * Math.sin(i / 4) + (i === 38 ? 60 : 0))));
const r = await renderTrace(
  { weeks, bolts: [{ wi: 38, n: 31 }, { wi: 12, n: 9 }], months: [{ wi: 0, label: "Nov" }, { wi: 20, label: "Mar" }] },
  { frames: 6, fps: 18 },
);
const head = r.webp.subarray(0, 12).toString("latin1");
assert.ok(head.startsWith("RIFF") && head.endsWith("WEBP"), "bukan berkas WebP");
const txt = r.webp.toString("latin1");
assert.ok(txt.includes("ANIM"), "WebP tidak beranimasi");
assert.equal(txt.split("ANMF").length - 1, 6, "jumlah frame tidak sesuai");
assert.ok(r.webp.length > 8 * 1024, "WebP terlalu kecil, kemungkinan kosong");

const { data } = await sharp(r.still).removeAlpha().raw().toBuffer({ resolveWithObject: true });
let emerald = 0, gold = 0;
for (let i = 0; i < data.length; i += 3) {
  const R = data[i], G = data[i + 1], B = data[i + 2];
  if (G > R + 50 && G > B + 10) emerald++;
  if (R > 200 && G > 160 && B < 90) gold++;
}
assert.ok(emerald > 300, `ridge hijau tidak tampak (piksel hijau: ${emerald})`);
assert.ok(gold > 40, `petir emas tidak tampak (piksel emas: ${gold})`);
console.log(`ok  render 3D: ${(r.webp.length / 1024).toFixed(0)} KB, 6 frame, hijau ${emerald}, emas ${gold}`);
