// Uji tanpa jaringan dan tanpa token: parser RSS, saringan repo privat, data kontribusi, dan build kosong.
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseFeed, cleanRepos, sampleData, fetchGithub } from "./lib/data.mjs";
import { traceData } from "./lib/sections-terminal.mjs";
import { width, wrap } from "./lib/text.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let n = 0;
const ok = (name, fn) => { fn(); n++; console.log("ok  " + name); };
const okAsync = async (name, fn) => { await fn(); n++; console.log("ok  " + name); };

ok("parseFeed membaca RSS 2.0 dan mengurutkan terbaru dulu", () => {
  const xml = `<rss><channel>
    <item><title><![CDATA[Lama &amp; usang]]></title><link>https://x.test/a</link><pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate></item>
    <item><title>Baru</title><link>https://x.test/b</link><pubDate>Tue, 02 Jan 2024 00:00:00 GMT</pubDate></item></channel></rss>`;
  const r = parseFeed(xml, 3);
  assert.equal(r.length, 2); assert.equal(r[0].title, "Baru"); assert.equal(r[1].title, "Lama & usang");
});
ok("parseFeed membaca Atom dan membuang entri tanpa tautan http", () => {
  const xml = `<feed><entry><title>Satu</title><link href="https://x.test/1"/><updated>2024-03-01T00:00:00Z</updated></entry>
    <entry><title>Rusak</title><link href="javascript:alert(1)"/></entry></feed>`;
  const r = parseFeed(xml, 3);
  assert.equal(r.length, 1); assert.equal(r[0].link, "https://x.test/1");
});
ok("parseFeed menolak feed kosong", () => assert.throws(() => parseFeed("<rss></rss>")));
ok("cleanRepos membuang repo privat dan tidak menyisakan namanya", () => {
  const r = cleanRepos([
    { name: "rahasia-klien", url: "https://g/x", isPrivate: true, stargazerCount: 9 },
    { name: "publik", url: "https://g/y", isPrivate: false, stargazerCount: 2, primaryLanguage: { name: "Astro", color: "#f00" } },
    { name: "tanpa-flag", url: "https://g/z" }, null,
  ]);
  assert.deepEqual(r.map((x) => x.name), ["publik"]);
  assert.ok(!JSON.stringify(r).includes("rahasia"));
});
ok("traceData: jumlah pekan, petir saling berjarak, maksimal tiga", () => {
  const d = sampleData().days, t = traceData(d);
  assert.ok(t.weeks.length >= 52 && t.weeks.length <= 54);
  assert.equal(t.weeks.reduce((a, b) => a + b, 0), d.reduce((a, b) => a + b.n, 0));
  assert.ok(t.bolts.length >= 1 && t.bolts.length <= 3);
  for (let i = 0; i < t.bolts.length; i++) for (let j = i + 1; j < t.bolts.length; j++) assert.ok(Math.abs(t.bolts[i].wi - t.bolts[j].wi) >= 5);
});
ok("traceData: tanpa data tetap menghasilkan garis datar", () => {
  const t = traceData([]);
  assert.ok(t.weeks.length >= 53 && t.weeks.every((v) => v === 0) && t.bolts.length === 0 && t.active === 0);
});
ok("wrap tidak melewati lebar dan memberi elipsis", () => {
  const lines = wrap("in400", 14, "Satu kalimat yang sangat panjang sekali untuk menguji pemotongan baris otomatis di dalam kartu", 150, 2);
  assert.equal(lines.length, 2);
  for (const l of lines) assert.ok(width("in400", 14, l) <= 150 + 1);
  assert.ok(lines[1].endsWith("…"));
});

ok("README memakai URL absolut bila ASSETS_BASE diset (hasil render ada di branch assets)", () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "pawang-base-"));
  execFileSync(process.execPath, [path.join(root, "scripts/generate.mjs"), "--offline", "--no3d", "--out", out], { cwd: root, stdio: "pipe", env: { ...process.env, ASSETS_BASE: "https://raw.githubusercontent.com/o/r/assets/" } });
  const readme = fs.readFileSync(path.join(out, "README.md"), "utf8");
  const srcs = [...readme.matchAll(/(?:src|srcset)="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(srcs.length > 15);
  for (const u of srcs) assert.ok(u.startsWith("https://raw.githubusercontent.com/o/r/assets/") && !u.includes("//assets") && !u.includes("assets//"), "URL tidak sesuai: " + u);
  fs.rmSync(out, { recursive: true, force: true });
});

ok("README statis terhadap data: angka dan stempel waktu tidak boleh masuk (hindari commit README harian)", () => {
  const build = (flagName) => {
    const out = fs.mkdtempSync(path.join(os.tmpdir(), "pawang-static-"));
    execFileSync(process.execPath, [path.join(root, "scripts/generate.mjs"), flagName, "--no3d", "--out", out], { cwd: root, stdio: "pipe", env: { ...process.env, ASSETS_BASE: "https://raw.githubusercontent.com/o/r/assets" } });
    const lines = fs.readFileSync(path.join(out, "README.md"), "utf8").split("\n");
    fs.rmSync(out, { recursive: true, force: true });
    // baris per-item (repo, artikel) memang mengikuti isi akun; sisanya harus identik
    return lines.filter((l) => !/(mantra-\d|article-\d|articles-head)/.test(l));
  };
  const a = build("--offline"), b = build("--sample");
  assert.deepEqual(a, b, "README berubah mengikuti data (cek alt/href yang memuat angka atau waktu)");
  assert.ok(!a.some((l) => /\d{2}\.\d{2} WIB|kontribusi \d|aktivitas dalam/.test(l)), "alt memuat angka/waktu");
});

ok("build kosong menghasilkan SVG sah, tanpa referensi luar, README tidak punya gambar hilang", () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "pawang-"));
  execFileSync(process.execPath, [path.join(root, "scripts/generate.mjs"), "--offline", "--no3d", "--out", out], { cwd: root, stdio: "pipe" });
  const svgs = fs.readdirSync(out).filter((f) => f.endsWith(".svg"));
  assert.ok(svgs.length >= 15, "terlalu sedikit SVG: " + svgs.length);
  for (const f of svgs) {
    const s = fs.readFileSync(path.join(out, f), "utf8");
    assert.ok(s.startsWith("<svg") && s.trimEnd().endsWith("</svg>"), f + ": bukan dokumen SVG");
    const stack = [];
    for (const m of s.matchAll(/<(\/?)([A-Za-z][\w:-]*)([^>]*?)(\/?)>/g)) {
      if (m[4]) continue;
      if (m[1]) assert.equal(stack.pop(), m[2], f + ": tag tidak seimbang di " + m[2]); else stack.push(m[2]);
    }
    assert.equal(stack.length, 0, f + ": tag belum ditutup");
    assert.ok(!/<script|<foreignObject|javascript:|onload=/i.test(s), f + ": elemen terlarang");
    assert.ok(!/(?:href|src)="https?:|url\(https?:/.test(s), f + ": referensi eksternal");
    assert.ok(/prefers-reduced-motion/.test(s), f + ": tanpa fallback reduced-motion");
  }
  const readme = fs.readFileSync(path.join(out, "README.md"), "utf8");
  for (const m of readme.matchAll(/(?:src|srcset)="([^"]+)"/g)) assert.ok(fs.existsSync(path.join(out, m[1])), "README merujuk berkas hilang: " + m[1]);
  fs.rmSync(out, { recursive: true, force: true });
});

await okAsync("fetchGithub: tanpa pin memakai repo publik terbaru, repo privat tidak pernah lolos", async () => {
  const real = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    assert.equal(url, "https://api.github.com/graphql");
    const body = {
      data: { user: {
        login: "x", name: "X", bio: "", websiteUrl: "", location: "", email: "", followers: { totalCount: 3 },
        pinnedItems: { nodes: [] },
        repositories: { nodes: [
          { name: "klien-rahasia", description: "", url: "https://g/1", stargazerCount: 0, isPrivate: true, pushedAt: "2026-01-01T00:00:00Z", primaryLanguage: null },
          { name: "publik-baru", description: "ok", url: "https://g/2", stargazerCount: 1, isPrivate: false, pushedAt: "2026-02-01T00:00:00Z", primaryLanguage: { name: "Astro", color: "#f00" } },
        ] },
        contributionsCollection: { totalCommitContributions: 5, totalIssueContributions: 1, totalPullRequestContributions: 2, totalPullRequestReviewContributions: 3,
          contributionCalendar: { totalContributions: 11, weeks: [{ contributionDays: [{ date: "2026-02-01", contributionCount: 4 }] }] } },
      } },
    };
    return { ok: true, status: 200, json: async () => body };
  };
  try {
    const d = await fetchGithub("x", "token");
    assert.equal(d.pinnedIsFallback, true);
    assert.deepEqual(d.pinned.map((r) => r.name), ["publik-baru"]);
    assert.ok(!JSON.stringify(d).includes("klien-rahasia"));
    assert.deepEqual(d.activity, { commit: 5, pr: 2, issue: 1, review: 3 });
    assert.equal(d.days.length, 1);
  } finally { globalThis.fetch = real; }
});
await okAsync("fetchGithub: tanpa token gagal tegas (tidak menimpa gambar lama)", async () => {
  await assert.rejects(() => fetchGithub("x", ""), /GH_TOKEN/);
});

console.log(`\n${n} uji lulus.`);
