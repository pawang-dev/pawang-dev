// Alat bantu lokal (bukan bagian Actions): render SVG ke PNG untuk dicek mata.
//   node scripts/render-png.mjs <folder-svg> <folder-out> nama1 nama2 ...
import sharp from "sharp";
import fs from "node:fs";
const [, , dir, out, ...names] = process.argv;
fs.mkdirSync(out, { recursive: true });
for (const n of names) await sharp(fs.readFileSync(`${dir}/${n}.svg`), { density: 96 }).png().toFile(`${out}/${n}.png`);
