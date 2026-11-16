// Sumber data: GitHub GraphQL, RSS artikel, OG image. Tidak ada data karangan di jalur live.
import fs from "node:fs";
import path from "node:path";
import sharp from "sharp";

const UA = "pawang-dev-profile-generator (+https://www.pawang.dev)";

export const BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
export const fmtDate = (d) => {
  const x = new Date(d);
  return isNaN(x) ? "" : `${x.getUTCDate()} ${BULAN[x.getUTCMonth()]} ${x.getUTCFullYear()}`;
};

export function loadIcon(root, name) {
  const f = path.join(root, "brand", "icons", "png", name + ".png");
  if (!fs.existsSync(f)) return null;
  return "data:image/png;base64," + fs.readFileSync(f).toString("base64");
}

export function loadBrand(root, name) {
  const f = path.join(root, "brand", name + ".png");
  if (!fs.existsSync(f)) throw new Error("Aset brand hilang: " + name);
  return "data:image/png;base64," + fs.readFileSync(f).toString("base64");
}

const QUERY = `
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    login name bio websiteUrl location email
    followers{ totalCount }
    pinnedItems(first:6, types:REPOSITORY){ nodes{ ... on Repository{
      name description url stargazerCount isPrivate pushedAt primaryLanguage{ name color } } } }
    repositories(first:6, privacy:PUBLIC, isFork:false, ownerAffiliations:OWNER, orderBy:{field:PUSHED_AT, direction:DESC}){ nodes{
      name description url stargazerCount isPrivate pushedAt primaryLanguage{ name color } } }
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions totalIssueContributions
      totalPullRequestContributions totalPullRequestReviewContributions
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
  }
}`;

const QUERY_ORG = `
query($login:String!){
  organization(login:$login){
    login name description websiteUrl location email
    pinnedItems(first:6, types:REPOSITORY){ nodes{ ... on Repository{
      name description url stargazerCount isPrivate pushedAt primaryLanguage{ name color } } } }
    repositories(first:6, privacy:PUBLIC, isFork:false, orderBy:{field:PUSHED_AT, direction:DESC}){ nodes{
      name description url stargazerCount isPrivate pushedAt primaryLanguage{ name color } } }
  }
}`;

async function gql(query, variables, token) {
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `bearer ${token}`, "user-agent": UA },
    body: JSON.stringify({ query, variables }),
    signal: AbortSignal.timeout(30000),
  });
  if (!res.ok) throw new Error(`GitHub GraphQL HTTP ${res.status}`);
  const j = await res.json();
  if (j.errors && !j.data) throw new Error("GitHub GraphQL: " + j.errors.map((e) => e.message).join("; "));
  return j.data;
}

/** Repo privat TIDAK pernah lolos: disaring di sini sebelum dipakai di mana pun. */
export function cleanRepos(nodes) {
  return (nodes || [])
    .filter((r) => r && r.name && r.url && r.isPrivate === false)
    .map((r) => ({
      name: r.name, description: r.description || "", url: r.url, stars: r.stargazerCount || 0,
      pushedAt: r.pushedAt, lang: r.primaryLanguage?.name || "", langColor: r.primaryLanguage?.color || "",
    }));
}

/** Data profil live. Repo privat TIDAK pernah dikembalikan (disaring di cleanRepos). */
export async function fetchGithub(login, token) {
  if (!token) throw new Error("GH_TOKEN kosong");
  const to = new Date();
  const from = new Date(to.getTime() - 364 * 86400000);
  let data = await gql(QUERY, { login, from: from.toISOString(), to: to.toISOString() }, token).catch((e) => {
    if (/Could not resolve to a User/i.test(String(e))) return { user: null };
    throw e;
  });
  let kind = "user";
  let p = data.user;
  if (!p) {
    data = await gql(QUERY_ORG, { login }, token);
    p = data.organization;
    kind = "organization";
  }
  if (!p) throw new Error(`Akun ${login} tidak ditemukan`);

  let pinned = cleanRepos(p.pinnedItems?.nodes);
  let pinnedIsFallback = false;
  if (!pinned.length) { pinned = cleanRepos(p.repositories?.nodes); pinnedIsFallback = pinned.length > 0; }

  const cc = p.contributionsCollection;
  const days = cc
    ? cc.contributionCalendar.weeks.flatMap((w) => w.contributionDays).map((d) => ({ date: d.date, n: d.contributionCount }))
    : [];
  return {
    kind,
    profile: {
      name: p.name || login, bio: p.bio || p.description || "", website: p.websiteUrl || "",
      location: p.location || "", email: p.email || "", followers: p.followers?.totalCount ?? null,
    },
    pinned,
    pinnedIsFallback,
    days: days.slice(-365),
    total: cc ? cc.contributionCalendar.totalContributions : null,
    activity: cc
      ? { commit: cc.totalCommitContributions, pr: cc.totalPullRequestContributions, issue: cc.totalIssueContributions, review: cc.totalPullRequestReviewContributions }
      : null,
  };
}

// ---------- RSS ----------
const decode = (s) =>
  String(s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&")
    .replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
const tag = (x, t) => {
  const m = x.match(new RegExp(`<${t}[^>]*>([\\s\\S]*?)</${t}>`, "i"));
  return m ? decode(m[1]) : "";
};

export function parseFeed(xml, limit = 3) {
  const blocks = [...xml.matchAll(/<(item|entry)[\s>][\s\S]*?<\/\1>/gi)].map((m) => m[0]);
  if (!blocks.length) throw new Error("RSS tidak berisi item");
  const items = blocks.map((b) => {
    let link = tag(b, "link");
    if (!link) link = (b.match(/<link[^>]*href=["']([^"']+)["']/i) || [])[1] || "";
    const date = tag(b, "pubDate") || tag(b, "published") || tag(b, "updated") || tag(b, "dc:date");
    return { title: tag(b, "title"), link: decode(link), date };
  }).filter((x) => x.title && /^https?:\/\//.test(x.link));
  items.sort((a, b) => (new Date(b.date) || 0) - (new Date(a.date) || 0));
  return items.slice(0, limit);
}

export async function fetchArticles(feed, limit) {
  const res = await fetch(feed, { headers: { "user-agent": UA, accept: "application/rss+xml, application/atom+xml, text/xml, */*" }, signal: AbortSignal.timeout(20000) });
  if (!res.ok) throw new Error(`RSS HTTP ${res.status}`);
  return parseFeed(await res.text(), limit);
}

/** Ambil og:image halaman artikel, perkecil, kembalikan data URI JPEG (atau null). */
export async function fetchOgImage(pageUrl) {
  try {
    const res = await fetch(pageUrl, { headers: { "user-agent": UA }, signal: AbortSignal.timeout(20000), redirect: "follow" });
    if (!res.ok) return null;
    const html = (await res.text()).slice(0, 400000);
    const metas = [...html.matchAll(/<meta\s[^>]*>/gi)].map((m) => m[0]);
    let src = "";
    for (const m of metas) {
      if (/(property|name)=["']og:image(:secure_url)?["']/i.test(m)) {
        const c = m.match(/content=["']([^"']+)["']/i);
        if (c) { src = decode(c[1]); break; }
      }
    }
    if (!src) return null;
    const abs = new URL(src, pageUrl).href;
    if (!/^https?:/.test(abs)) return null;
    const ir = await fetch(abs, { headers: { "user-agent": UA }, signal: AbortSignal.timeout(25000) });
    if (!ir.ok) return null;
    const buf = Buffer.from(await ir.arrayBuffer());
    if (buf.length > 12 * 1024 * 1024) return null;
    const out = await sharp(buf).resize(440, 230, { fit: "cover", position: "centre" }).jpeg({ quality: 70, mozjpeg: true }).toBuffer();
    return "data:image/jpeg;base64," + out.toString("base64");
  } catch {
    return null;
  }
}

// ---------- DATA CONTOH (hanya untuk --sample / pratinjau; BUKAN data Pawang.dev) ----------
export function sampleData() {
  const days = [];
  const end = new Date(Date.UTC(2026, 10, 14));
  let s = 7;
  const R = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  for (let i = 364; i >= 0; i--) {
    const d = new Date(end.getTime() - i * 86400000);
    const wd = d.getUTCDay();
    let n = R() < (wd === 0 || wd === 6 ? 0.25 : 0.62) ? Math.floor(R() * R() * 9) + 1 : 0;
    if (i > 40 && i < 52) n += Math.floor(R() * 10) + 6; // pekan ledakan contoh
    if (i === 46) n = 31;
    days.push({ date: d.toISOString().slice(0, 10), n });
  }
  const now = Date.now();
  return {
    kind: "user",
    profile: { name: "Contoh", bio: "", website: "https://www.pawang.dev", location: "", email: "", followers: 42 },
    pinned: [
      { name: "contoh-proyek-satu", description: "Data contoh untuk pratinjau tampilan.", url: "https://www.pawang.dev", stars: 12, pushedAt: new Date(now - 3 * 86400000).toISOString(), lang: "TypeScript", langColor: "#3178c6" },
      { name: "contoh-proyek-dua", description: "Repo yang baru diperbarui terlihat menyala.", url: "https://www.pawang.dev", stars: 4, pushedAt: new Date(now - 40 * 86400000).toISOString(), lang: "Astro", langColor: "#ff5a03" },
      { name: "contoh-proyek-tiga", description: "Repo yang lama jadi abu.", url: "https://www.pawang.dev", stars: 0, pushedAt: new Date(now - 300 * 86400000).toISOString(), lang: "JavaScript", langColor: "#f1e05a" },
    ],
    days,
    total: days.reduce((a, d) => a + d.n, 0),
    activity: { commit: 412, pr: 58, issue: 21, review: 33 },
  };
}
export function sampleArticles() {
  return [
    { title: "Contoh judul tulisan pertama yang cukup panjang untuk menguji pemotongan baris", link: "https://www.pawang.dev", date: "2026-11-10", img: null },
    { title: "Contoh tulisan kedua", link: "https://www.pawang.dev", date: "2026-10-28", img: null },
    { title: "Contoh tulisan ketiga tentang dashboard", link: "https://www.pawang.dev", date: "2026-10-02", img: null },
  ];
}
export function emptyData() {
  return { kind: "user", profile: { name: "Pawang.dev", bio: "", website: "", location: "", email: "", followers: null }, pinned: [], days: [], total: null, activity: null };
}
