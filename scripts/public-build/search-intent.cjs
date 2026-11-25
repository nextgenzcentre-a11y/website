// Evidence-based search-intent and discovery improvements. Run before AdSense injection.
const fs=require('node:fs'), path=require('node:path');
const root=path.resolve(__dirname,'../..'), base='https://www.nextgenzcentre.space';
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const write=(p,s)=>fs.writeFileSync(path.join(root,p),s);
const exists=p=>fs.existsSync(path.join(root,p));
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const decode=s=>s.replace(/&#x27;|&#39;|&apos;/g,"'").replace(/&quot;/g,'"').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const plain=s=>decode(s.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim());
const changed=new Set();
const priority={
 law:'programmes/subjects/bachelor-law-malaysia.html',
 camp:'guides/summer-winter-camps-malaysia.html',
 pharmacy:'programmes/courses/um/bachelor-of-pharmacy-e05de2.html'
};
const preserve=new Set([
 'programmes/courses/iium/master-degree-kenms-coursework-research-mixed-mode-0caa1e.html',
 'programmes/courses/upm/master-of-clinical-psychology-d1c83b.html',
 'programmes/courses/uum/bachelor-of-public-management-with-honours-48a603.html',
 'programmes/courses/upm/foundation-studies-for-agricultural-science-eb4625.html',
 'programmes/courses/um/master-of-business-administration-mba-ad2244.html'
]);
function edit(p,fn,substantive=true){
 const old=read(p), next=fn(old);
 if(next!==old){write(p,next);if(substantive)changed.add(p);}
 return next!==old;
}
function meta(s,title,desc){
 if(title){
   s=s.replace(/<title>[\s\S]*?<\/title>/,()=>'<title>'+esc(title)+'</title>');
   s=s.replace(/<meta property="og:title" content="[^"]*">/,()=>'<meta property="og:title" content="'+esc(title)+'">');
 }
 if(desc){
   s=s.replace(/<meta name="description" content="[^"]*">/,()=>'<meta name="description" content="'+esc(desc)+'">');
   s=s.replace(/<meta property="og:description" content="[^"]*">/,()=>'<meta property="og:description" content="'+esc(desc)+'">');
 }
 return s;
}
function lead(s,txt){return s.replace(/<p class="lead">[\s\S]*?<\/p>/,()=>'<p class="lead">'+esc(txt)+'</p>');}
function insert(s,anchor,body){
 if(!s.includes(anchor))throw Error('Missing insertion point: '+anchor);
 return s.replace(anchor,()=>body+anchor);
}
function section(title,body,id){
 return '<section class="catalog-wide" id="'+id+'"><h2>'+esc(title)+'</h2>'+body+'</section>';
}
function addLink(s,href,label){
 const a='<p class="ng-search-context"><a href="/'+href+'">'+esc(label)+'</a></p>';
 if(s.includes(a))return s;
 return insert(s,'</main>',a);
}
function schema(s,fn){
 return s.replace(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g,(m,j)=>{
  try{const d=JSON.parse(j);fn(d);return '<script type="application/ld+json">'+JSON.stringify(d).replace(/</g,'\\u003c')+'</script>';}catch{return m;}
 });
}
// Target 1: the English law page is currently unknown to Google; use the
// existing canonical URL, align the heading and title, and give direct links.
edit(priority.law,s=>{
 s=s.replaceAll('Bachelor in Law in Malaysia','Bachelor of Law in Malaysia')
    .replaceAll('Bachelor%20in%20Law%20in%20Malaysia','Bachelor%20of%20Law%20in%20Malaysia')
    .replace('>Bachelor in</span><span class="accent">Law in Malaysia','>Bachelor of</span><span class="accent">Law in Malaysia');
 s=meta(s,'Bachelor of Law in Malaysia: Universities & LLB Entry Guide','Compare law degrees in Malaysia, including LLB and Shariah law pathways. Review university options, admission questions, fees and professional recognition.');
 s=lead(s,'Compare bachelor of law programmes in Malaysia, including LLB, law and commerce, and Shariah law pathways. Review the actual award, international entry requirements, tuition and professional recognition before applying.');
 return insert(s,'<h2>What does Law study involve?</h2>',section('Bachelor of Law (LLB) in Malaysia: choosing the right degree',
  '<p>The awards listed below are not interchangeable. An LLB, a combined law and commerce degree and a Shariah law degree may lead to different professional routes. Compare the official award and entry requirements, and confirm recognition in the country where you intend to practise.</p><p>For example, Universiti Malaya publishes a separate <a href="https://study.um.edu.my/bachelor-of-laws" rel="noopener noreferrer">Bachelor of Laws programme</a>. Its official page describes a four-year full-time programme. This is an official-source reference, not an additional verified listing in our finder; confirm international availability and fees with UM.</p>','law-llb-guide'));
});
for(const p of ['programmes/index.html','programmes/subjects/index.html','programmes/levels/bachelor.html','programmes/universities/um.html']){
 if(exists(p))edit(p,s=>addLink(s,priority.law,'Compare Bachelor of Law (LLB) programmes in Malaysia'),false);
}
// Target 2: retain the indexed camp guide and put the winter decision first.
// Provider dates and ages are drawn from its existing, dated source section.
edit(priority.camp,s=>{
 const title='Winter Camp Malaysia 2026–2027: English Camps in Kuala Lumpur';
 const desc='Compare winter English camps in Malaysia for children and teens: ACE and Sheffield dates, ages, duration, supervision and package costs. Summer camp advice included.';
 s=meta(s,title,desc);
 s=s.replace(/<h1>[^<]+<\/h1>/,()=>'<h1>'+esc(title)+'</h1>')
    .replace(/<p class="intro">[^<]+<\/p>/,()=>'<p class="intro">Compare winter holiday English programmes in Kuala Lumpur, their advertised dates, age groups, supervision and the costs to confirm before booking. Summer camp guidance is included below.</p>');
 s=schema(s,d=>{if(d['@type']==='BlogPosting'){d.headline=title;d.description=desc;d.dateModified='2026-11-25';}});
 return insert(s,'<h2>Winter English camps in Kuala Lumpur:',section('Winter camp in Malaysia: December 2026 and early 2027',
  '<p>Start with your child’s age and travel dates. The provider listings reviewed on 22 November below describe ACE’s December–February windows and Sheffield’s usual December–January season. Exact start dates, vacancies and prices must be confirmed with the provider.</p><p>Request a written package covering lessons, activities, accommodation (if needed), supervision, airport transfers and any additional costs. Do not assume these are included in the advertised tuition.</p>','winter-camp-malaysia'));
});
for(const p of ['guides/index.html','guides/english-courses-in-malaysia.html'])if(exists(p))edit(p,s=>addLink(s,priority.camp,'Winter Camp Malaysia 2026–2027: English camps, ages and dates'),false);
// Target 3: exact Malay search terminology plus official faculty source.
// Retain the original finder amount as an indicative reference.
edit(priority.pharmacy,s=>{
 const title='UM Pharmacy (Farmasi UM) – Bachelor of Pharmacy with Honours';
 const desc='Bachelor of Pharmacy with Honours at Universiti Malaya (UM): Farmasi UM, international entry questions, four-year programme and finder-listed tuition reference.';
 s=meta(s,title,desc);
 s=lead(s,'Explore the Bachelor of Pharmacy with Honours at Universiti Malaya (UM), also known as Farmasi UM. Compare the four-year programme, finder-listed tuition and international admission questions before applying.');
 return insert(s,'<section class="catalog-verified catalog-source-check"',section('Farmasi UM – Sarjana Muda Farmasi (Kepujian)',
  '<p lang="ms">Fakulti Farmasi Universiti Malaya (UM) menawarkan program Sarjana Muda Farmasi (Kepujian). Semak syarat kemasukan pelajar antarabangsa, tempoh pengajian, yuran dan tarikh pengambilan dengan pihak universiti sebelum memohon.</p><p>The <a href="https://pharmacy.um.edu.my/bachelor-of-pharmacy-with-hons" rel="noopener noreferrer">UM Faculty of Pharmacy</a> identifies the official honours award. The <a href="https://pharmacy.um.edu.my/dean-s-message" rel="noopener noreferrer">faculty overview</a> describes the four-year programme. Check the <a href="https://study.um.edu.my/how-to-apply" rel="noopener noreferrer">official admissions page</a> for current intake and application requirements. The fee in our finder remains indicative.</p>','farmasi-um'));
});
for(const p of ['programmes/universities/um.html','programmes/subjects/bachelor-pharmacy-malaysia.html'])if(exists(p))edit(p,s=>addLink(s,priority.pharmacy,'Farmasi UM – Bachelor of Pharmacy with Honours at Universiti Malaya'),false);
// Homepage discovery links are in the static fallback AND retained after React
// rendering on the public landing page via the existing catalogue links.
let sitemap=read('sitemap.xml');
const urls=[...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]);
const files=new Map();
for(const url of urls){
 if(!url.startsWith(base+'/'))continue;
 const p=url.slice(base.length+1)+(url.endsWith('/')?'index.html':'');
 if(p.endsWith('.html')&&exists(p))files.set(url,p);
}
let languageLinks=0, metadata=0, subjectTitles=0, validAlternates=0;
const alternates=new Map();
for(const [url,p] of files){
 if(!/^programmes\//.test(p))continue;
 let s=read(p), old=s;
 const links=[...s.matchAll(/<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">/g)]
   .map(m=>({lang:m[1],url:m[2]})).filter(a=>files.has(a.url));
 const explicit=links.filter(a=>a.lang!=='x-default');
 if(explicit.length>=2){
  alternates.set(url,links);
  validAlternates++;
  // Crawlable, reciprocal HTML links, not JS-only language selection.
  if(!s.includes('id="ng-language-editions"')&&s.includes('</main>')){
   const labels={en:'English',ar:'العربية','zh-Hans':'简体中文',fr:'Français',ms:'Bahasa Melayu'};
   const nav='<nav id="ng-language-editions" class="wrap" aria-label="Page language editions" style="padding:16px 0;color:#0F1F38;background:#F0E3D2"><span>'+ (p.startsWith('programmes/ar/')?'اللغة: ':p.startsWith('programmes/zh/')?'语言：':'Read in: ')+'</span>'+explicit.map(a=>'<a lang="'+(a.lang==='zh-Hans'?'zh-CN':a.lang)+'" hreflang="'+a.lang+'" href="'+esc(a.url)+'"'+(a.url===url?' aria-current="page"':'')+'>'+esc(labels[a.lang]||a.lang)+'</a>').join(' · ')+'</nav>';
   s=s.replace('</main>',nav+'</main>');languageLinks++;
  }
 }
 // Improve generic English course descriptions using existing course facts,
 // preserving established winners and verified editorial descriptions.
 if(/^programmes\/courses\/[^/]+\/[^/]+\.html$/.test(p)&&!preserve.has(p)&&p!==priority.pharmacy){
   const title=s.match(/<title>([^<]+)<\/title>/)?.[1]||'';
   const d=s.match(/<meta name="description" content="([^"]*)">/)?.[1]||'';
   const fact=label=>plain(s.match(new RegExp('<strong>'+label+'</strong><span>([\\s\\S]*?)</span>'))?.[1]||'');
   const course=fact('Programme title in finder'), institution=fact('Institution'), intake=fact('Intake reference');
   const fee=fact('Tuition fee \\(finder reference\\)').replace(/\s*·\s*Fee breakdown.*$/,'').trim();
   if(course&&institution&&/Check .*entry requirements, tuition and upcoming intakes before applying\./.test(decode(d))){
    const uni=institution.match(/\(([A-Za-z0-9]+)\)\s*$/)?.[1]||institution;
    const prefix=course+' at '+uni+'.';
    const details=[/^Finder-listed (?:MYR|RM|USD)\s/i.test(fee)&&fee.length<50?fee+' (indicative).':'',/^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:[ ,/]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))*$/.test(intake)?'Intake reference: '+intake+'.':'','Check entry requirements and fees.'].filter(Boolean);
    let desc=prefix+' '+details.join(' ');
    if(desc.length>165)desc=prefix+' Check admission requirements, tuition and intake references.';
    if(desc.length<=185){s=meta(s,null,desc);metadata++;changed.add(p);}
   }
   // Only repair visibly truncated titles, never discard the full award H1.
   if(title.includes('…')&&course&&institution){
    const uni=institution.match(/\(([A-Za-z0-9]+)\)\s*$/)?.[1];
    if(uni&&course.length<=100){s=meta(s,course+' | '+uni+' Malaysia',null);changed.add(p);}
   }
 }
 if(/^programmes\/subjects\/bachelor-[^/]+\.html$/.test(p)&&p!==priority.law){
   const t=s.match(/<title>([^<]+)<\/title>/)?.[1]||'';
   if(t.startsWith('Bachelor in ')){
    const title=decode(t).replace(/^Bachelor in /,'Bachelor of ');
    s=meta(s,title,null).replace('>Bachelor in</span>','>Bachelor of</span>');
    s=schema(s,d=>{if(d['@type']==='CollectionPage'&&typeof d.name==='string')d.name=d.name.replace(/^Bachelor in /,'Bachelor of ');});
    subjectTitles++;changed.add(p);
   }
 }
 if(s!==old)write(p,s);
}
// Mirror validated alternates in XML to make language clusters discoverable.
// Preserve all existing loc entries and lastmod except pages with changed main content.
sitemap=sitemap.replace(/<urlset\b([^>]*)>/, (m,a)=>m.includes('xmlns:xhtml=')?m:'<urlset'+a+' xmlns:xhtml="http://www.w3.org/1999/xhtml">');
sitemap=sitemap.replace(/<url>([\s\S]*?)<\/url>/g,(m,b)=>{
 const url=b.match(/<loc>([^<]+)<\/loc>/)?.[1];
 if(!url)return m;
 const p=files.get(url);
 const al=alternates.get(url);
 // Only mark the three editorial content changes, not metadata or navigation alone.
 if(Object.values(priority).includes(p))b=b.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>2026-11-25</lastmod>');
 if(al&&!b.includes('xhtml:link'))b+=al.map(a=>'<xhtml:link rel="alternate" hreflang="'+esc(a.lang)+'" href="'+esc(a.url)+'" />').join('');
 return '<url>'+b+'</url>';
});
write('sitemap.xml',sitemap);
if(!read(priority.law).includes('Bachelor of Law in Malaysia')||!read(priority.camp).includes('Winter Camp Malaysia 2026')||!read(priority.pharmacy).includes('Farmasi UM')||languageLinks<3000||validAlternates<3000||metadata<100)throw Error('SEO validation failed');
console.log('SEO discovery: '+languageLinks+' pages with crawlable language links; '+validAlternates+' sitemap language clusters; '+metadata+' course descriptions; '+subjectTitles+' bachelor subject titles; 3 priority pages improved; '+preserve.size+' performing English course titles/descriptions preserved.');
