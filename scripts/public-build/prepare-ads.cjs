// Publish AdSense only on static, public editorial/catalogue documents.
// The root React app also hosts private portals, so it gets verification metadata
// but never loads third-party advertising JavaScript.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const publisher = 'ca-pub-4481064346396356';
const meta = '<meta name="google-adsense-account" content="'+publisher+'">';
const ad = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+publisher+'" crossorigin="anonymous"></script>';
const index = fs.readFileSync(path.join(root,'index.html'),'utf8');
const bundle = fs.readFileSync(path.join(root,'programmes/site-assets/public-app.js'),'utf8');
if (!bundle.includes('Reconnecting automatically') || /Could not (?:establish|verify) the database session/.test(bundle)) {
  throw Error('Firebase bundle is stale; stop publishing');
}
if (!index.includes(meta) || /<script[^>]+src=["'][^"']*adsbygoogle\.js/i.test(index)) {
  throw Error('Shared homepage/portal must contain verification metadata only');
}
const sitemap = fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
const pages = new Set();
for (const match of sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)) {
  const url = new URL(match[1]);
  if (url.origin !== 'https://www.nextgenzcentre.space' || url.search || url.hash) continue;
  const p = decodeURIComponent(url.pathname);
  if (!/^\/(?:programmes|guides|services|ar|zh|fr|ms)\/|^\/(?:about-nextgenz-centre|why-malaysia)\.html$/.test(p)) continue;
  if (/(?:^|\/)(?:admin|studentportal|agentportal|registerasstudent|registerasagent|login|account|dashboard|checkout)(?:\/|\.html|$)/i.test(p)) continue;
  const relative = p.slice(1) + (p.endsWith('/') ? 'index.html' : '');
  if (!relative.endsWith('.html')) continue;
  const file = path.resolve(root, relative);
  if (!file.startsWith(root+path.sep)) throw Error('Invalid sitemap path');
  if (fs.existsSync(file)) pages.add(file);
}
let published=0, skipped=0;
for (const file of pages) {
  let html=fs.readFileSync(file,'utf8');
  // Never introduce ads into a private/shared dynamic app or login/form-only page.
  if (/id=["']app-source|firebase-auth|public-app\.js|<input[^>]+type=["']password/i.test(html)) { skipped++; continue; }
  if (!/<\/head>/i.test(html)) throw Error('Missing head: '+path.relative(root,file));
  if (!html.includes(meta)) html=html.replace(/<\/head>/i,meta+'\n</head>');
  if (!/adsbygoogle\.js/.test(html)) html=html.replace(/<\/head>/i,ad+'\n</head>');
  fs.writeFileSync(file,html);
  published++;
}
if (published<100) throw Error('Unexpectedly few public pages: '+published);
console.log('AdSense public HTML pages: '+published+'; private/shared pages skipped: '+skipped+'; Firebase compiled bundle verified.');
