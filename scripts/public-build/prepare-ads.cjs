// Build distinct public and private documents from the same React application.
// Ads are loaded only on the public homepage and eligible static documents.
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
if (!index.includes(meta) || /<script[^>]+src=["'][^"']*adsbygoogle\.js/i.test(index)) throw Error('Expected clean source document');
const documentHtml = index.replace(/<script type="text\/plain" id="app-source">[\s\S]*?<\/script>/, '');
if (documentHtml.length >= index.length || documentHtml.includes('id="app-source"')) throw Error('Could not strip duplicate app source from deployed HTML');
const privateDoc = documentHtml.replace('<meta name="robots" content="index,follow,max-image-preview:large">','<meta name="robots" content="noindex,nofollow">');
if (!privateDoc.includes('content="noindex,nofollow"')) throw Error('Missing portal robots directive');
fs.writeFileSync(path.join(root,'portal-app.html'),privateDoc);
// Old links from the static catalogue and Google results remain functional.
// Redirect private hashes and admin entry before React executes; public
// homepage never transitions into a private application in the same document.
const router = `<script>(function(){
  function route() {
    var key=location.hash.replace(/^#\\/?/,'').toLowerCase();
    var query=new URLSearchParams(location.search);
    var map={student:'/student',studentportal:'/student',agent:'/agent',agentportal:'/agent',registerasstudent:'/registerasstudent',registerstudent:'/registerasstudent',registerasagent:'/registerasagent',registeragent:'/registerasagent'};
    if(query.get('open')==='admin'){location.replace('/portal-app.html'+location.search+location.hash);return;}
    if(Object.prototype.hasOwnProperty.call(map,key)){location.replace(map[key]+location.search);return;}
    if(key==='about'||key==='why-malaysia'){location.replace(key==='about'?'/about-nextgenz-centre.html':'/why-malaysia.html');return;}
    if(['universities','services','portals','process','agents','faq','contact','articles'].indexOf(key)>=0){location.replace('/portal-app.html'+location.search+location.hash);}
  }
  route();window.addEventListener('hashchange',route);
})();</script>`;
let home=documentHtml.replace('<html lang="en" class="scroll-smooth">','<html lang="en" class="scroll-smooth" data-ng-public-home>')
  .replace('<script>document.documentElement.classList.add(\'ng-boot\'); setTimeout(function(){document.documentElement.classList.remove(\'ng-boot\')},8000)</script>','')
const firebaseStart=home.indexOf('<!-- Firebase (Auth + Realtime Database) -->');
const translateStart=home.indexOf('<!-- Google Translate Script -->',firebaseStart);
if(firebaseStart<0||translateStart<firebaseStart)throw Error('Missing Firebase bootstrap block');
home=home.slice(0,firebaseStart)+home.slice(translateStart);
home=home.replace('<head>','<head>\n'+router+'\n').replace('</head>',ad+'\n</head>');
if(!home.includes('data-ng-public-home>') || /<script[^>]+src=["'][^"']*firebase-(?:app|auth|database)-compat\.js/i.test(home) || !home.includes(ad) || /classList\.add\('ng-boot'\)/.test(home)) throw Error('Homepage isolation check failed');
fs.writeFileSync(path.join(root,'index.html'),home);
console.log('AdSense homepage enabled; portal document is ad-free and private Firebase SDKs are not loaded on the homepage.');
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
console.log('AdSense public HTML pages: '+(published+1)+'; private/shared pages skipped: '+skipped+'; Firebase compiled bundle verified.');
