// Cyber-Nusantara / Mystical Terminal. Semua angka dari data GitHub/RSS; tidak ada data karangan di jalur live.
import { W, doc } from "./theme.mjs";
import { text, width, paragraph, fit } from "./text.mjs";
import { round1 as r1 } from "./text.mjs";
import { BULAN, fmtDate } from "./data.mjs";

const M = 20;
const CW = W - 2 * M; // 760
const CSS_COMMON =
  `.steam{animation:st 5s ease-in-out infinite}@keyframes st{0%{opacity:0;transform:translateY(6px)}30%{opacity:.7}100%{opacity:0;transform:translateY(-10px)}}` +
  `.blink{animation:bk 1.1s steps(1) infinite}@keyframes bk{50%{opacity:0}}` +
  `.led{animation:ld 2.4s ease-in-out infinite}@keyframes ld{50%{opacity:.35}}` +
  `.breathe{animation:br 5s ease-in-out infinite;transform-origin:0 0}@keyframes br{50%{transform:scale(1,1.02)}}`;

// ------------------------------------------------------------------ pembantu gambar
const card = (P, x, y, w, h, { r = 14, accent = null } = {}) =>
  `<rect x="${x + 1}" y="${y + 3}" width="${w}" height="${h}" rx="${r}" fill="#000" fill-opacity=".35"/>` +
  (accent ? `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${accent}" fill-opacity=".05"/>` : "") +
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${accent ? "none" : P.card}" stroke="${accent || P.cardBorder}" stroke-opacity="${accent ? 0.45 : 1}" stroke-width="1.4"/>` +
  (accent ? `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${P.card}" fill-opacity=".0"/>` : "");

/** Jendela terminal: tiga titik + judul mono. */
const windowBar = (P, x, y, w, label) =>
  `<path d="M${x} ${y + 34}H${x + w}" stroke="${P.cardBorder}" stroke-width="1.4"/>` +
  `<circle cx="${x + 18}" cy="${y + 17}" r="4.5" fill="${P.err}" fill-opacity=".85"/><circle cx="${x + 34}" cy="${y + 17}" r="4.5" fill="${P.accent}" fill-opacity=".85"/><circle cx="${x + 50}" cy="${y + 17}" r="4.5" fill="${P.ok}" fill-opacity=".85"/>` +
  text("m400", 12, label, x + 68, y + 21, { fill: P.mute });

/** Awan = server infrastruktur: kontur awan berisi slot server dan LED. */
const cloudServer = (P, x, y, s, { op = 1, stroke } = {}) =>
  `<g transform="translate(${r1(x)} ${r1(y)}) scale(${s})" opacity="${op}">` +
  `<path d="M-52 32H52C76 32 78 -4 54 -8 58 -40 18 -52 4 -26 -10 -44 -48 -34 -42 -6 -66 -4 -72 32 -52 32Z" fill="${P.card}" stroke="${stroke || P.line2}" stroke-width="2.4" stroke-linejoin="round"/>` +
  [-10, 4, 18].map((yy, i) => `<rect x="-34" y="${yy}" width="68" height="9" rx="3" fill="${P.bg}" stroke="${P.line2}"/><circle class="led" style="animation-delay:${-i * 0.8}s" cx="-27" cy="${yy + 4.5}" r="2.2" fill="${i === 1 ? P.accent : P.ok}"/><path d="M-12 ${yy + 4.5}h32" stroke="${P.line2}" stroke-width="2"/>`).join("") +
  `</g>`;

const IC = {
  term: (P) => `<path d="M4.5 6.5l6 5.5-6 5.5" fill="none" stroke="${P.accent}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M12.5 18.5h7" stroke="${P.accent}" stroke-width="2.6" stroke-linecap="round"/>`,
  bars: (P) => `<rect x="3" y="12" width="5" height="9" rx="1.6" fill="${P.accent}"/><rect x="10" y="7" width="5" height="14" rx="1.6" fill="${P.accent}"/><rect x="17" y="3" width="5" height="18" rx="1.6" fill="${P.accent}"/>`,
  braces: (P) => `<path d="M8 4C5 4 5 6 5 8s0 3-2 4c2 1 2 2 2 4s0 4 3 4M16 4c3 0 3 2 3 4s0 3 2 4c-2 1-2 2-2 4s0 4-3 4" fill="none" stroke="${P.cyan}" stroke-width="2.2" stroke-linecap="round"/>`,
  doc: (P) => `<rect x="4.5" y="2.5" width="15" height="19" rx="3" fill="none" stroke="${P.ink}" stroke-width="2.2"/><path d="M8.5 9h7M8.5 13h7M8.5 17h4" stroke="${P.accent}" stroke-width="2.2" stroke-linecap="round"/>`,
  bolt: (P) => `<path d="M13.5 1.5L4.5 14h6.2l-1.4 8.5L19.5 9.6h-6.4z" fill="${P.accent}"/>`,
};
const icon = (P, kind, x, y, size) => `<g transform="translate(${r1(x)} ${r1(y)}) scale(${r1(size / 24)})">${IC[kind](P)}</g>`;
const STAT_ICON = {
  commit: (c) => `<g fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M2.5 12h5.3M16.2 12h5.3"/></g>`,
  pr: (c) => `<g fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="5.5" r="2.5"/><circle cx="6" cy="18.5" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="M6 8v8M18 16V10a3 3 0 0 0-3-3h-3m2.4-2.6L12 7l2.4 2.6"/></g>`,
  issue: (c) => `<g fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="13" r="6"/><path d="M12 7V4M7 9L4.5 7M17 9l2.5-2M6 13H3M18 13h3M8 18l-2.5 2M16 18l2.5 2"/></g>`,
  review: (c) => `<g fill="none" stroke="${c}" stroke-width="2.2" stroke-linejoin="round"><path d="M2 12s3.7-7 10-7 10 7 10 7-3.7 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></g>`,
};

/** Judul section: ikon + judul + teks mono di kanan. Tinggi 56. */
const title = (P, kind, label, right = "") =>
  icon(P, kind, M + 4, 14, 26) +
  text("jk800", 23, label, M + 40, 35, { fill: P.ink }) +
  (right ? text("m400", 12.5, right, W - M - 4, 34, { fill: P.mute, anchor: "end" }) : "");
const titleStrip = (P, name, kind, label, right) => ({ name, alt: label, svg: doc(P, { h: 60, label, body: title(P, kind, label, right) }) });

const glowFilter = `<filter id="gb" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>`;

// ------------------------------------------------------------------ HERO
export function hero(P, ctx) {
  const { cfg } = ctx;
  const H = 462;
  const LK = { w: 647, h: 169 }, lkW = 250, lkH = Math.round((lkW * LK.h) / LK.w);
  const MK = { w: 267, h: 257 };
  const wx = 436, wy = 30, ww = 344, wh = 172;
  const cmds = ["pawang jinakkan website", "pawang rapikan data", "pawang tuntun seo", "pawang rakit otomasi"];
  const css = CSS_COMMON +
    `.row{animation:rw 10s ease-in-out infinite}@keyframes rw{0%{opacity:0;transform:translateX(-8px)}8%,90%{opacity:1;transform:none}100%{opacity:0}}`;
  const defs = `<radialGradient id="gg" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="${P.accent}" stop-opacity=".14"/><stop offset="1" stop-color="${P.accent}" stop-opacity="0"/></radialGradient>`;
  let rows = "";
  cmds.forEach((c, i) => {
    const y = wy + 66 + i * 30;
    rows += `<g class="row" style="animation-delay:${-i * 0.6}s">` +
      text("m700", 13, "$", wx + 20, y, { fill: P.accent }) +
      text("m400", 13, c, wx + 38, y, { fill: P.ink }) +
      `<rect x="${wx + ww - 58}" y="${y - 14}" width="38" height="20" rx="6" fill="${P.ok}" fill-opacity=".14" stroke="${P.ok}" stroke-opacity=".6"/>` +
      text("m700", 11.5, "OK", wx + ww - 39, y, { fill: P.ok, anchor: "middle" }) + `</g>`;
  });
  const sub = paragraph("in400", 16, cfg.hero.sub, 36, 250, 372, 5, 25, { fill: P.mute });
  const promptY = 250 + sub.lines.length * 25 + 26;
  const promptW = width("m400", 15, "> " + cfg.hero.prompt);
  const mug =
    `<path d="M736 398h40v30q0 8-8 8h-24q-8 0-8-8z" fill="${P.card}" stroke="${P.line2}" stroke-width="2"/>` +
    `<path d="M776 406h5a7 7 0 0 1 0 16h-5" fill="none" stroke="${P.line2}" stroke-width="2.4"/>` +
    `<ellipse cx="756" cy="398" rx="20" ry="4.2" fill="#6B4A2B"/>` +
    [746, 756, 766].map((x, i) => `<path class="steam" style="animation-delay:${-i * 1.5}s" d="M${x} 388c-6-9 6-13 0-22s6-13 0-22" fill="none" stroke="${P.mute}" stroke-width="2.4" stroke-linecap="round"/>`).join("");
  const body =
    `<circle cx="640" cy="230" r="280" fill="url(#gg)"/>` +
    cloudServer(P, 80, 410, 0.9, { op: 0.35 }) +
    // kolom kiri
    `<image href="${ctx.brand("lockup-dark")}" x="36" y="30" width="${lkW}" height="${lkH}"/>` +
    text("jk800", 38, cfg.hero.line1, 36, 156, { fill: P.ink }) +
    text("jk800", 38, cfg.hero.line2, 36, 202, { fill: P.accent }) +
    sub.svg +
    `<rect x="36" y="${promptY - 18}" width="${r1(promptW + 56)}" height="34" rx="9" fill="${P.card}" stroke="${P.cardBorder}"/>` +
    text("m700", 15, ">", 50, promptY + 4, { fill: P.accent }) +
    text("m400", 15, cfg.hero.prompt, 50 + width("m400", 15, "> "), promptY + 4, { fill: P.ink }) +
    `<rect class="blink" x="${r1(50 + promptW + 4)}" y="${promptY - 9}" width="9" height="18" fill="${P.accent}"/>` +
    // jendela terminal
    card(P, wx, wy, ww, wh) + windowBar(P, wx, wy, ww, "pawang@dev: ~") + rows +
    // maskot Dev asli (dari brandboard)
    `<g transform="translate(${r1(wx - 10 + MK.w / 2 - 8)} ${r1(H - 8)})"><g class="breathe"><image href="${ctx.brand("mascot-dark")}" x="${-MK.w / 2}" y="${-MK.h + 8}" width="${MK.w}" height="${MK.h}"/></g></g>` +
    // awan = server, tenang
    cloudServer(P, 736, 262, 0.72, { stroke: P.ok }) +
    text("m400", 11.5, "status: tenang", 736, 318, { fill: P.ok, anchor: "middle" }) +
    mug;
  return { name: "hero", alt: "Pawang.dev. Digitalmu liar? Serahkan ke Pawang. Website, SEO, dashboard, dan otomasi.", svg: doc(P, { h: H, label: "Pawang.dev: Digitalmu liar? Serahkan ke Pawang.", defs, css, body, grid: true }) };
}

// ------------------------------------------------------------------ CTA (emas)
export function cta(P) {
  const H = 108, bw = 316, bh = 54, bx = (W - bw) / 2, by = 38;
  const css = `.pulse{animation:cp 3s ease-in-out infinite}@keyframes cp{0%,100%{opacity:.28}50%{opacity:.55}}`;
  const label = "Konsultasi Gratis", lw = width("jk800", 20, label), gw = width("m700", 19, ">_") + 12 + lw;
  const sx = W / 2 - gw / 2;
  const body =
    text("m400", 13, "// ceritakan bagian digital yang paling bikin pusing", W / 2, 24, { fill: P.mute, anchor: "middle" }) +
    `<rect class="pulse" x="${bx}" y="${by + 6}" width="${bw}" height="${bh}" rx="12" fill="${P.accent}" filter="url(#gb)"/>` +
    `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="12" fill="${P.accent}"/>` +
    `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="12" fill="none" stroke="#fff" stroke-opacity=".25"/>` +
    text("m700", 19, ">_", sx, by + 34, { fill: P.onAccent }) +
    text("jk800", 20, label, sx + width("m700", 19, ">_") + 12, by + 34, { fill: P.onAccent });
  return { name: "cta", alt: "Konsultasi Gratis", svg: doc(P, { h: H, label: "Tombol Konsultasi Gratis", defs: glowFilter, css, body }) };
}

// ------------------------------------------------------------------ STATUS
export function status(P, ctx) {
  const days = ctx.data.days || [];
  const last7 = days.slice(-7).reduce((a, d) => a + d.n, 0);
  let badge, col, l1, l2;
  if (!days.length) { badge = "MENUNGGU DATA"; col = P.mute; l1 = "Belum ada data pertama."; l2 = "Status diperbarui otomatis setiap hari."; }
  else if (last7 > 0) { badge = "TERKENDALI"; col = P.ok; l1 = "Pawang sedang berjaga."; l2 = `${last7} kontribusi publik dalam 7 hari terakhir.`; }
  else { badge = "ISTIRAHAT"; col = P.accent; l1 = "Pawang sedang istirahat sebentar."; l2 = "Belum ada kontribusi publik dalam 7 hari terakhir."; }
  const H = 134, y0 = 10, hh = 114, cx = M + 70, cy = y0 + hh / 2;
  const bw = width("m700", 12, "STATUS: " + badge) + 40;
  const css = `.dot{animation:dt 2s ease-in-out infinite}@keyframes dt{50%{opacity:.3}}`;
  const body =
    card(P, M, y0, CW, hh, { accent: col }) +
    `<circle cx="${cx}" cy="${cy}" r="34" fill="${col}" fill-opacity=".12" stroke="${col}" stroke-width="2.6"/>` +
    (badge === "TERKENDALI"
      ? `<path d="M${cx - 14} ${cy + 1}l10 10 18-21" fill="none" stroke="${col}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>`
      : badge === "ISTIRAHAT"
        ? `<path d="M${cx - 8} ${cy - 14}v28M${cx + 8} ${cy - 14}v28" stroke="${col}" stroke-width="5.5" stroke-linecap="round"/>`
        : `<path d="M${cx - 14} ${cy}h28" stroke="${col}" stroke-width="5.5" stroke-linecap="round"/>`) +
    `<rect x="${M + 130}" y="${y0 + 18}" width="${r1(bw)}" height="24" rx="7" fill="${col}" fill-opacity=".14" stroke="${col}" stroke-opacity=".6"/>` +
    `<circle class="dot" cx="${M + 144}" cy="${y0 + 30}" r="3.6" fill="${col}"/>` +
    text("m700", 12, "STATUS: " + badge, M + 154, y0 + 34, { fill: col }) +
    text("jk800", 22, "Status Pawang", M + 130, y0 + 70, { fill: P.ink }) +
    text("in600", 15, l1, M + 130 + width("jk800", 22, "Status Pawang") + 16, y0 + 69, { fill: P.ink }) +
    text("in400", 14, fit("in400", 14, l2, 560), M + 130, y0 + 94, { fill: P.mute });
  return { name: "status", alt: "Status Pawang", svg: doc(P, { h: H, label: "Status Pawang", css, body }) };
}

// ------------------------------------------------------------------ TENTANG (jendela README.md)
export function banner(P, ctx) {
  const { svg: sentence, lines } = paragraph("in600", 17, ctx.cfg.whatIs.sentence, M + 24, 0, CW - 48, 4, 25, { fill: P.ink });
  const y0 = 8, bodyTop = y0 + 34 + 30;
  const h = 34 + 30 + lines.length * 25 + 38;
  const H = y0 + h + 14;
  const body =
    card(P, M, y0, CW, h) + windowBar(P, M, y0, CW, "README.md") +
    text("m400", 13, "// tentang pawang.dev", M + 24, bodyTop - 8, { fill: P.accent }) +
    `<g transform="translate(0 ${bodyTop + 14})">${sentence}</g>` +
    text("m400", 12.5, "// di bawah: divisi, status, kontribusi, proyek, tulisan", M + 24, y0 + h - 14, { fill: P.mute });
  return { name: "banner", alt: ctx.cfg.whatIs.sentence, svg: doc(P, { h: H, label: "Tentang Pawang.dev", body }) };
}

// ------------------------------------------------------------------ DIVISI (liar -> mantra)
export function services(P, ctx) {
  const { cfg } = ctx;
  const rowH = 94, gap = 10, top = 64;
  const tiersTop = top + cfg.services.length * (rowH + gap) + 8;
  const H = tiersTop + 118;
  let rows = "";
  cfg.services.forEach((s, i) => {
    const y = top + i * (rowH + gap);
    const lx = M + 190, ax = lx + 244, mx = ax + 34;
    rows +=
      card(P, M, y, CW, rowH, { accent: s.accent }) +
      `<rect x="${M}" y="${y + 16}" width="5" height="${rowH - 32}" rx="2.5" fill="${s.accent}"/>` +
      text("m700", 13, `PAWANG ${s.short.toUpperCase()}`, M + 22, y + 28, { fill: s.ink || s.accent }) +
      s.icons.map((nm, j) => {
        const src = ctx.icon(nm), ix = M + 22 + 15 + j * 36, iy = y + 62;
        return src ? `<circle cx="${ix}" cy="${iy}" r="15" fill="#F1F5F9"/><image href="${src}" x="${ix - 10}" y="${iy - 10}" width="20" height="20"/>` : "";
      }).join("") +
      text("m700", 11.5, "LIAR", lx, y + 26, { fill: P.err }) +
      paragraph("in400", 14, s.liar, lx, y + 46, 232, 3, 18, { fill: P.ink }).svg +
      `<path d="M${ax} ${y + rowH / 2}h18m-6-6 6 6-6 6" fill="none" stroke="${P.mute}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>` +
      text("m700", 11.5, "MANTRA", mx, y + 26, { fill: P.ok }) +
      paragraph("in400", 14, s.mantra, mx, y + 46, W - M - mx - 14, 3, 18, { fill: P.ink }).svg;
  });
  let tiers = text("m400", 12.5, "// paket di setiap divisi", M + 4, tiersTop + 8, { fill: P.mute });
  const tw = CW / 3;
  cfg.tiers.forEach((t, i) => {
    const x = M + 4 + i * tw, pw = width("m700", 12.5, t.name.toUpperCase()) + 24;
    tiers +=
      `<rect x="${x}" y="${tiersTop + 24}" width="${r1(pw)}" height="26" rx="8" fill="${t.accent}" fill-opacity=".14" stroke="${t.accent}" stroke-opacity=".7"/>` +
      text("m700", 12.5, t.name.toUpperCase(), x + pw / 2, tiersTop + 42, { fill: t.ink || t.accent, anchor: "middle" }) +
      text("in400", 14, fit("in400", 14, t.desc, tw - 16), x, tiersTop + 72, { fill: P.mute });
  });
  return { name: "services", alt: "Lima divisi Pawang: " + cfg.services.map((s) => "Pawang " + s.short).join(", "), svg: doc(P, { h: H, label: "Lima divisi Pawang.dev", body: title(P, "term", "Lima Divisi Pawang", "liar -> mantra") + rows + tiers }) };
}

// ------------------------------------------------------------------ TULISAN (kartu OG)
export const articlesHead = (P) => titleStrip(P, "articles-head", "doc", "Tulisan", "terbaru dari pawang.dev");
export function articleCards(P, ctx) {
  const items = ctx.articles.slice(0, 3), n = 3, gap = 14;
  const cwCard = (CW - gap * (n - 1)) / n, tw = Math.round(CW / n), H = 316;
  return items.map((a, i) => {
    const cx0 = Math.max(0, Math.round((cwCard + gap) * i - tw * i)), top = 6, ih = Math.round(cwCard / 1.91);
    const defs = `<clipPath id="ci"><path d="M${cx0} ${top + ih}V${top + 14}Q${cx0} ${top} ${cx0 + 14} ${top}H${r1(cx0 + cwCard - 14)}Q${r1(cx0 + cwCard)} ${top} ${r1(cx0 + cwCard)} ${top + 14}V${top + ih}Z"/></clipPath>` +
      `<linearGradient id="ph" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B0E14"/><stop offset="1" stop-color="#1F2633"/></linearGradient>`;
    const body =
      card(P, cx0, top, r1(cwCard), H - 20) +
      (a.img
        ? `<image href="${a.img}" x="${cx0}" y="${top}" width="${r1(cwCard)}" height="${ih}" preserveAspectRatio="xMidYMid slice" clip-path="url(#ci)"/>`
        : `<g clip-path="url(#ci)"><rect x="${cx0}" y="${top}" width="${r1(cwCard)}" height="${ih}" fill="url(#ph)"/>${cloudServer(P, cx0 + cwCard / 2, top + ih / 2 + 4, 0.75, { stroke: P.line2 })}</g>`) +
      `<path d="M${cx0} ${top + ih}H${r1(cx0 + cwCard)}" stroke="${P.accent}" stroke-opacity=".5" stroke-width="1.6"/>` +
      paragraph("jk800", 16, a.title, cx0 + 16, top + ih + 30, cwCard - 32, 3, 21, { fill: P.ink }).svg +
      text("m400", 12, fmtDate(a.date), cx0 + 16, H - 38, { fill: P.mute }) +
      text("jk800", 14, "Baca", r1(cx0 + cwCard - 40), H - 38, { fill: P.accent, anchor: "end" }) +
      `<path d="M${r1(cx0 + cwCard - 34)} ${H - 43}l5 5-5 5" fill="none" stroke="${P.accent}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>`;
    return { name: `article-${i}`, href: a.link, w: tw, alt: `Tulisan: ${a.title}`, svg: doc(P, { w: tw, h: H, label: `Tulisan: ${a.title}`, defs, body }) };
  });
}

// ------------------------------------------------------------------ SOSIAL
export const connectHead = (P) => titleStrip(P, "connect-head", "bolt", "Temui Pawang", "pilih jalurmu");
export function socialTiles(P, ctx) {
  const items = ctx.cfg.socials.filter((s) => ctx.icon(s.icon));
  const per = 4, gap = 12, cw = (CW - gap * (per - 1)) / per, tw = Math.round(CW / per), H = 84;
  return items.map((s, i) => {
    const k = i % per, cx0 = Math.max(0, Math.round((cw + gap) * k - tw * k));
    const body =
      card(P, cx0, 6, r1(cw), 66) +
      `<circle cx="${r1(cx0 + 36)}" cy="39" r="22" fill="#F1F5F9"/>` +
      `<image href="${ctx.icon(s.icon)}" x="${r1(cx0 + 22)}" y="25" width="28" height="28"/>` +
      text("jk700", 14, fit("jk700", 14, s.short || s.label, cw - 80), r1(cx0 + 66), 44, { fill: P.ink });
    return { name: `social-${i}`, href: s.url, w: tw, alt: s.label, svg: doc(P, { w: tw, h: H, label: s.label, body }) };
  });
}
