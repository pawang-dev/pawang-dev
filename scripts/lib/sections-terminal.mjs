// Empat section berjendela terminal: proyek (ls -l), kontribusi (detak server), aktivitas (htop), footer (status bar).
import { W, doc } from "./theme.mjs";
import { text, width, fit, paragraph } from "./text.mjs";
import { round1 as r1 } from "./text.mjs";
import { BULAN, fmtDate } from "./data.mjs";

const WX = 20, WW = 760, RAD = 14, BAR = "#10141C";
const STEAM_CSS = `.steam{animation:st 4.6s ease-in-out infinite}@keyframes st{0%{opacity:0;transform:translateY(5px)}35%{opacity:.75}100%{opacity:0;transform:translateY(-7px)}}.led{animation:ld 1.6s steps(1) infinite}@keyframes ld{50%{opacity:.25}}.dot{animation:dt 2s ease-in-out infinite}@keyframes dt{50%{opacity:.3}}`;
const fmtInt = (n) => new Intl.NumberFormat("id-ID").format(n);

// ---------- rangka jendela, dipotong per irisan supaya bisa disambung rapat ----------
const side = (P, y1, y2) => `<path d="M${WX + 0.7} ${y1}V${y2}M${WX + WW - 0.7} ${y1}V${y2}" stroke="${P.cardBorder}" stroke-width="1.4"/>`;
function winTop(P, h, label) {
  const t = 8, bar = t + 34;
  return (
    `<path d="M${WX} ${h}V${t + RAD}Q${WX} ${t} ${WX + RAD} ${t}H${WX + WW - RAD}Q${WX + WW} ${t} ${WX + WW} ${t + RAD}V${h}Z" fill="${P.card}"/>` +
    `<path d="M${WX} ${bar}V${t + RAD}Q${WX} ${t} ${WX + RAD} ${t}H${WX + WW - RAD}Q${WX + WW} ${t} ${WX + WW} ${t + RAD}V${bar}Z" fill="${BAR}"/>` +
    `<path d="M${WX} ${bar}H${WX + WW}" stroke="${P.cardBorder}" stroke-width="1.4"/>` +
    `<path d="M${WX + 0.7} ${h}V${t + RAD}Q${WX + 0.7} ${t + 0.7} ${WX + RAD} ${t + 0.7}H${WX + WW - RAD}Q${WX + WW - 0.7} ${t + 0.7} ${WX + WW - 0.7} ${t + RAD}V${h}" fill="none" stroke="${P.cardBorder}" stroke-width="1.4"/>` +
    `<circle cx="${WX + 20}" cy="${t + 17}" r="4.5" fill="${P.err}" fill-opacity=".85"/><circle cx="${WX + 36}" cy="${t + 17}" r="4.5" fill="${P.accent}" fill-opacity=".85"/><circle cx="${WX + 52}" cy="${t + 17}" r="4.5" fill="${P.ok}" fill-opacity=".85"/>` +
    text("m400", 12, label, WX + 70, t + 21, { fill: P.mute }) +
    `<circle class="dot" cx="${WX + WW - 20}" cy="${t + 17}" r="3.6" fill="${P.ok}"/>`
  );
}
const winMid = (P, h) => `<rect x="${WX}" y="0" width="${WW}" height="${h}" fill="${P.card}"/>` + side(P, 0, h);
function winBottom(P, h, end) {
  return (
    `<path d="M${WX} 0V${end - RAD}Q${WX} ${end} ${WX + RAD} ${end}H${WX + WW - RAD}Q${WX + WW} ${end} ${WX + WW} ${end - RAD}V0Z" fill="${P.card}"/>` +
    `<path d="M${WX + 0.7} 0V${end - RAD}Q${WX + 0.7} ${end - 0.7} ${WX + RAD} ${end - 0.7}H${WX + WW - RAD}Q${WX + WW - 0.7} ${end - 0.7} ${WX + WW - 0.7} ${end - RAD}V0" fill="none" stroke="${P.cardBorder}" stroke-width="1.4"/>`
  );
}
const heading = (P, h1, sub, extra = "") =>
  text("jk800", 24, h1, WX + 24, 8 + 34 + 36, { fill: P.ink }) +
  text("in400", 14, fit("in400", 14, sub, WW - 48), WX + 24, 8 + 34 + 60, { fill: P.mute }) + extra;

// ============================================================ PROYEK: ls -l + uap kopi
function mug(P, cx, base, rec, idx) {
  const rise = 10 + 20 * rec;
  const defs = "";
  const steam = [-5, 3, 11].map((dx, i) => {
    const x = cx + dx - 1, y0 = base - 28;
    return `<path class="steam" style="animation-delay:${-(idx * 0.7 + i * 1.4).toFixed(1)}s" d="M${x} ${y0}c-4-${r1(rise * 0.3)} 4-${r1(rise * 0.55)} 0-${r1(rise * 0.8)}" fill="none" stroke="${P.mute}" stroke-width="2.2" stroke-linecap="round"/>`;
  }).join("");
  return (
    `<ellipse cx="${cx + 3}" cy="${base + 1}" rx="17" ry="3.4" fill="#000" fill-opacity=".4"/>` +
    `<path d="M${cx - 13} ${base - 24}h26v18q0 6-6 6h-14q-6 0-6-6z" fill="url(#mg)"/>` +
    `<path d="M${cx + 13} ${base - 19}h3a5 5 0 0 1 0 10h-3" fill="none" stroke="#94A3B8" stroke-width="2.4"/>` +
    `<ellipse cx="${cx}" cy="${base - 24}" rx="13" ry="3.4" fill="#CBD5E1"/><ellipse cx="${cx}" cy="${base - 24}" rx="10.5" ry="2.4" fill="#5B3B20"/>` +
    steam
  );
}
export function projectWindow(P, ctx) {
  const repos = ctx.data.pinned.slice(0, ctx.cfg.featureLimit || 4);
  const defs = `<linearGradient id="mg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F1F5F9"/><stop offset="1" stop-color="#94A3B8"/></linearGradient>`;
  const sub = ctx.data.pinnedIsFallback ? "Belum ada repo yang dipin, jadi ini yang terbaru diperbarui. Makin tinggi uap kopinya, makin baru." : "Repo pilihan. Makin tinggi uap kopinya, makin baru dikerjakan.";
  const label = "pawang@dev: ~/mantra $ ls -l";
  const topH = 8 + 34 + 96;
  const out = [{
    name: "mantra-top", href: ctx.cfg.defaultLink, alt: "Mantra Pilihan: repo pilihan Pawang.dev",
    svg: doc(P, { h: topH, label: "Mantra Pilihan", body: winTop(P, topH, label) + heading(P, "Mantra Pilihan", sub, text("m400", 12, `total ${repos.length}`, WX + 24, 8 + 34 + 84, { fill: "#64748B" })) }),
  }];
  if (!repos.length) {
    out.push({
      name: "mantra-0", href: ctx.cfg.defaultLink, alt: "Belum ada repo yang dipin",
      svg: doc(P, { h: 56, label: "Belum ada repo yang dipin", body: winMid(P, 56) + text("m400", 13, "# belum ada repo yang dipin. Mantra pertama sedang ditulis.", WX + 24, 30, { fill: P.mute }) }),
    });
  }
  const now = Date.now(), rowH = 70;
  repos.forEach((r, i) => {
    const days = Math.max(0, (now - new Date(r.pushedAt).getTime()) / 86400000), rec = Math.exp(-days / 90);
    const d = new Date(r.pushedAt), dt = isNaN(d) ? "" : `${String(d.getUTCDate()).padStart(2, "0")} ${BULAN[d.getUTCMonth()]}`;
    const body =
      winMid(P, rowH) +
      text("m400", 12, "-rw-r--r--", WX + 24, 26, { fill: "#64748B" }) +
      text("m700", 12, `${fmtInt(r.stars)} bintang`, WX + 112, 26, { fill: P.accent }) +
      text("m400", 12, dt, WX + 212, 26, { fill: P.mute }) +
      text("m700", 15, "./", WX + 274, 28, { fill: P.accent }) + text("m700", 15, fit("m700", 15, r.name, 290), WX + 274 + width("m700", 15, "./"), 28, { fill: P.ink }) +
      text("in400", 13, fit("in400", 13, r.description || "Tanpa deskripsi.", 310), WX + 274, 50, { fill: P.mute }) +
      (r.lang ? `<circle cx="${WX + 600}" cy="22" r="4.5" fill="${r.langColor || P.cyan}"/>` + text("m400", 12, fit("m400", 12, r.lang, 80), WX + 610, 26, { fill: P.mute }) : "") +
      mug(P, WX + WW - 44, 60, rec, i) +
      `<path d="M${WX + 24} ${rowH - 1}H${WX + WW - 24}" stroke="${P.cardBorder}" stroke-dasharray="3 6"/>`;
    out.push({ name: `mantra-${i}`, href: r.url, alt: `Repo ${r.name}`, svg: doc(P, { h: rowH, label: `Repo ${r.name}`, defs, css: STEAM_CSS, body }) });
  });
  const bH = 30;
  out.push({ name: "mantra-end", href: ctx.cfg.defaultLink, alt: "Pawang.dev", svg: doc(P, { h: bH + 14, label: "Penutup jendela", body: winBottom(P, bH + 14, bH) }) });
  return out;
}

// ============================================================ KONTRIBUSI: detak server
export function traceData(days) {
  const weeks = [];
  for (let i = 0; i < days.length; i += 7) weeks.push(days.slice(i, i + 7).reduce((a, d) => a + d.n, 0));
  if (weeks.length < 2) weeks.push(...Array(Math.max(0, 53 - weeks.length)).fill(0));
  const bolts = [];
  const cand = days.map((d, i) => ({ ...d, wi: Math.floor(i / 7) })).filter((d) => d.n >= 3).sort((a, b) => b.n - a.n || a.date.localeCompare(b.date));
  for (const d of cand) if (bolts.length < 3 && bolts.every((b) => Math.abs(b.wi - d.wi) >= 5)) bolts.push({ wi: d.wi, n: d.n, date: d.date });
  const months = [];
  let last = -1;
  days.forEach((d, i) => {
    if (i % 7 !== 0 || !d.date) return;
    const m = new Date(d.date + "T00:00:00Z").getUTCMonth();
    if (m !== last) { months.push({ wi: i / 7, label: BULAN[m] }); last = m; }
  });
  const active = days.filter((d) => d.n > 0).length;
  return { weeks, bolts, months, active };
}
const traceSub = (data, td) =>
  !data.days.length || !td.active
    ? "Garis lurus. Langit masih cerah, server tenang."
    : `${fmtInt(data.total ?? data.days.reduce((a, d) => a + d.n, 0))} kontribusi dalam 12 bulan · ${td.bolts.length ? `${td.bolts.length} petir, semuanya sudah ditangkap` : "belum ada petir"}`;
const TRACE_LABEL = "pawang@dev: ~/log $ ./detak-server";
export function traceTop(P, ctx, td) {
  const h = 8 + 34 + 76;
  const sub = traceSub(ctx.data, td);
  return { name: "trace-top", alt: `Detak Server: ${sub}`, svg: doc(P, { h, label: "Detak Server", body: winTop(P, h, TRACE_LABEL) + heading(P, "Detak Server", sub) }) };
}
export function traceBottom(P, ctx, td) {
  const total = ctx.data.total ?? ctx.data.days.reduce((a, d) => a + d.n, 0);
  const status = td.active
    ? `kontribusi ${fmtInt(total)}  ·  hari aktif ${fmtInt(td.active)}  ·  petir ${td.bolts.length} (ditangkap)`
    : "# belum ada hujan. uptime tenang";
  const end = 46;
  return { name: "trace-bottom", alt: status, svg: doc(P, { h: end + 14, label: "Status detak server", body: winBottom(P, end + 14, end) + text("m400", 12, status, WX + 24, 22, { fill: P.mute }) }) };
}
/** Cadangan 2D bila Chromium/WebGL tidak tersedia. Lebar 800, tinggi 300, bingkai sama dengan versi 3D. */
export function traceFallback(P, ctx, td) {
  const H = 300, x0 = WX + 40, x1 = WX + WW - 40, yb = 232, n = td.weeks.length, step = (x1 - x0) / (n - 1);
  const hh = (v) => Math.min(120, 9 * Math.sqrt(Math.max(0, v)));
  const pts = td.weeks.map((v, i) => [x0 + i * step, yb - hh(v)]);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${r1(p[0])} ${r1(p[1])}`).join("");
  const bars = td.weeks.map((v, i) => `<rect x="${r1(x0 + i * step - step * 0.3)}" y="${r1(yb - hh(v))}" width="${r1(step * 0.6)}" height="${r1(hh(v))}" fill="${P.ok}" fill-opacity=".3"/>`).join("");
  const bolts = td.bolts.map((b) => { const x = x0 + b.wi * step, y = yb - hh(td.weeks[b.wi]); return `<path d="M${r1(x - 4)} ${r1(y - 56)}h10l-7 18h9l-14 24 3-17h-9z" fill="${P.accent}"/>` + text("m700", 11, `×${b.n}`, x, y - 66, { fill: P.accent, anchor: "middle" }); }).join("");
  const months = td.months.map((m) => text("m400", 10.5, m.label, x0 + m.wi * step, yb + 24, { fill: "#64748B", anchor: "middle" })).join("");
  const body = winMid(P, H) + bars + `<path d="${line}" fill="none" stroke="${P.ok}" stroke-width="2.4" stroke-linejoin="round"/>` + bolts + months;
  return { name: "trace-3d", ext: "svg", alt: "Detak server: kontribusi setahun sebagai gelombang", svg: doc(P, { h: H, label: "Detak server (2D)", body }) };
}

// ============================================================ AKTIVITAS: htop
export function activityWindow(P, ctx) {
  const a = ctx.data.activity;
  const items = [
    { k: "Commit", v: a?.commit ?? 0, c: P.accent }, { k: "Pull request", v: a?.pr ?? 0, c: P.ok },
    { k: "Review", v: a?.review ?? 0, c: P.cyan }, { k: "Issue", v: a?.issue ?? 0, c: P.err },
  ];
  const total = items.reduce((s, i) => s + i.v, 0), dom = [...items].sort((x, y) => y.v - x.v)[0];
  const sub = total ? `${fmtInt(total)} aktivitas dalam 12 bulan · terbanyak: ${dom.k}` : "Angin tenang. Belum ada aktivitas.";
  const y0 = 8 + 34 + 76, rowH = 50, N = 36, bx = WX + 178, pitch = 12;
  const topH = y0 + 4 * rowH + 6, end = topH + 30, H = end + 14;
  let rows = "";
  items.forEach((it, i) => {
    const y = y0 + 22 + i * rowH, share = total ? it.v / total : 0, filled = it.v ? Math.max(1, Math.round(share * N)) : 0;
    let segs = "";
    for (let s = 0; s < N; s++) segs += `<rect ${s === filled - 1 ? 'class="led" ' : ""}x="${r1(bx + s * pitch)}" y="${y - 13}" width="9.4" height="18" rx="2" fill="${s < filled ? it.c : P.cardBorder}"${s < filled ? "" : ' fill-opacity=".8"'}/>`;
    rows +=
      text("m400", 12, String(i + 1), WX + 24, y + 1, { fill: "#64748B" }) +
      text("jk700", 15, it.k, WX + 46, y + 2, { fill: P.ink }) +
      text("m400", 18, "[", bx - 14, y + 4, { fill: "#64748B" }) + segs + text("m400", 18, "]", bx + N * pitch + 2, y + 4, { fill: "#64748B" }) +
      text("m700", 14, (share * 100).toFixed(1) + "%", bx + N * pitch + 24, y + 3, { fill: it.c }) +
      text("m400", 13, fmtInt(it.v), WX + WW - 24, y + 3, { fill: P.mute, anchor: "end" });
  });
  const body =
    winTop(P, end, "pawang@dev: ~/meter $ htop") + heading(P, "Meter Angin", sub) + rows +
    `<path d="M${WX} ${topH}H${WX + WW}" stroke="${P.cardBorder}" stroke-dasharray="3 6"/>` +
    text("m400", 12, "# persen = porsi dari total aktivitas", WX + 24, topH + 22, { fill: "#64748B" }) +
    `<path d="M${WX + 0.7} ${end - RAD}Q${WX + 0.7} ${end - 0.7} ${WX + RAD} ${end - 0.7}H${WX + WW - RAD}Q${WX + WW - 0.7} ${end - 0.7} ${WX + WW - 0.7} ${end - RAD}" fill="none" stroke="${P.cardBorder}" stroke-width="1.4"/>`;
  return { name: "meter", alt: `Meter Angin: ${sub}`, svg: doc(P, { h: H, label: "Meter Angin", css: STEAM_CSS, body }) };
}

// ============================================================ FOOTER: status bar tmux/powerline
export function footerBar(P, ctx) {
  const wib = new Date(Date.now() + 7 * 3600000);
  const stamp = `${wib.getUTCDate()} ${BULAN[wib.getUTCMonth()]} ${wib.getUTCFullYear()} ${String(wib.getUTCHours()).padStart(2, "0")}.${String(wib.getUTCMinutes()).padStart(2, "0")} WIB`;
  const y = 22, h = 38, tip = 15;
  const segs = [
    { t: "pawang.dev", bg: P.accent, fg: P.onAccent, f: "m700" },
    { t: "main", bg: P.ok, fg: "#04241A", f: "m700", check: true },
    { t: `diperbarui otomatis ${stamp}`, bg: "#1F2633", fg: P.ink, f: "m700" },
  ];
  let x = WX, out = "";
  const clipId = "pl";
  segs.forEach((sg, i) => {
    const tw = width(sg.f, 12.5, sg.t) + (sg.check ? 22 : 0), w = tw + (i ? 40 : 30);
    const nxt = segs[i + 1]?.bg || "#0F131B";
    out += `<rect x="${r1(x)}" y="${y}" width="${r1(w)}" height="${h}" fill="${sg.bg}"/><rect x="${r1(x + w)}" y="${y}" width="${tip}" height="${h}" fill="${nxt}"/><path d="M${r1(x + w)} ${y}L${r1(x + w + tip)} ${y + h / 2}L${r1(x + w)} ${y + h}Z" fill="${sg.bg}"/>`;
    const tx = x + (i ? 22 : 15);
    out += text(sg.f, 12.5, sg.t, tx, y + 24, { fill: sg.fg });
    if (sg.check) out += `<path d="M${r1(tx + width(sg.f, 12.5, sg.t) + 8)} ${y + 19}l4 4 8-9" fill="none" stroke="${sg.fg}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
    x += w;
  });
  const tag = "Tenang, ada Pawang.";
  const body =
    `<clipPath id="${clipId}"><rect x="${WX}" y="${y}" width="${WW}" height="${h}" rx="10"/></clipPath>` +
    `<g clip-path="url(#${clipId})"><rect x="${WX}" y="${y}" width="${WW}" height="${h}" fill="#0F131B"/>${out}</g>` +
    `<rect x="${WX + 0.7}" y="${y + 0.7}" width="${WW - 1.4}" height="${h - 1.4}" rx="10" fill="none" stroke="${P.cardBorder}" stroke-width="1.4"/>` +
    text("m700", 12.5, tag, WX + WW - 20, y + 24, { fill: P.accent, anchor: "end" });
  return { name: "footer", alt: `Pawang.dev. ${tag} Diperbarui otomatis ${stamp}`, svg: doc(P, { h: 84, label: `Pawang.dev. ${tag}`, body }) };
}
