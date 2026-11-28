const fs = require('node:fs');
const path = require('node:path');
const {gunzipSync} = require('node:zlib');
const root = path.resolve(__dirname, '../..');
const data = file => JSON.parse(fs.readFileSync(path.join(__dirname, file), 'utf8'));
const regions = data('areas.json');
const guides = data('properties.json');
const landmarks = data('landmarks.json');
const catalogue = JSON.parse(gunzipSync(fs.readFileSync(path.join(__dirname, 'rooms.json.gz')))).properties;
const buildings = new Map(catalogue.map(p => [p.slug, p]));
const origin = 'https://www.nextgenzcentre.space';
const hub = '/services/student-accommodation-malaysia.html';
const assets = '/assets/stays/';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug = value => value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,' and ').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const regionUrl = id => `/services/stays/${id}.html`;
const currentSlugs = {'quill-residences':'quill-residence','arden-one-bukit-senyum':'arden-obs'};
const propertyUrl = id => `/services/stays/${currentSlugs[id] || id}.html`;
const partnerBooking = 'https://stay.naibnb.com/book/nextgenz-centr-bh3jec';
const nightlyOffer = 'Book through NextGenz Centre for 30% off each night’s room rate during NaiBnb’s activation promotion.';
function partnerLink(label = 'Choose dates and book') {
  return `<a class="btn" href="${partnerBooking}" rel="sponsored noopener noreferrer" target="_blank">${esc(label)}</a>`;
}
const roomCover = item => assets + 'rooms/' + item.cover;
const landmarkUrl = id => assets + 'places/' + landmarks[id].file;
const bedLabel = n => n === 0 ? 'Studio' : `${n}-bedroom`;
const plural = (n, word, form = word + 's') => `${n} ${n === 1 ? word : form}`;
const regionMedia = {
  'klang-valley':['kuala-lumpur','saloma-link','bukit-bintang'],
  'genting-highlands':['genting','genting-skyworlds'],
  'johor-bahru':['johor-bahru','mount-austin','johor-mosque'],
  putrajaya:['putrajaya'], sarawak:['sarawak']
};
const localMedia = {
  'agile-bukit-bintang':['trx','pavilion'], 'axon-bukit-bintang':['bukit-bintang','pavilion'],
  'regalia-residence':['sunway-putra','chow-kit'], 'the-colony-by-infinitum':['chow-kit','saloma-link'],
  'quill-residences':['quill-city','chow-kit'], 'yolo-signature-suites':['sunway-pyramid','sunway-lagoon'],
  'antara-genting':['genting','genting-skyworlds'], 'skyline-embassy':['klcc-park'],
  'cappella-embassy':['klcc-park'], 'grand-damansara':['petaling-jaya','the-curve'],
  'aliva-mount-austin':['mount-austin'], 'arden-one-bukit-senyum':['johor-bahru'],
  'amora-park-tampoi':['johor-mosque']
};
const statusLabel = {catalogue:'Explore apartments',enquiry:'Enquire about stays',upcoming:'Upcoming project'};
const regionStatus = {catalogue:'Apartments and room photos',planned:'Planned projects',upcoming:'Upcoming destination'};
const regionNames = {'klang-valley':'Kuala Lumpur & Klang Valley','genting-highlands':'Genting Highlands','johor-bahru':'Johor Bahru',putrajaya:'Putrajaya',sarawak:'Sarawak'};
const urls = new Map();
for (const p of catalogue) {
  const used = new Set();
  for (const config of p.configurations) {
    let name = slug(config.name);
    if (used.has(name)) name += '-' + config.code.toLowerCase();
    used.add(name);
    config.url = '/services/stays/rooms/' + p.slug + '/' + name + '.html';
    const bedroomCounts = new Set(config.units.map(u => u.bedrooms));
    if (bedroomCounts.size === 1) config.bedrooms = config.units[0].bedrooms;
    const sameName = p.configurations.filter(other => other.name.toLowerCase() === config.name.toLowerCase());
    const distinction = config.units.length > 1 ? plural(config.units.length,'design') : 'up to '+plural(config.units[0].guests,'guest');
    config.displayName = sameName.length > 1 ? config.name+' · '+distinction : config.name;
  }
}
const contact = message => 'https://wa.me/601167701210?text=' + encodeURIComponent(message);
function bookingLink(topic, label='Book now on WhatsApp', style='btn') {
  const message = `Hi NextGenz Centre, please check the live price and availability for ${topic}. My check-in date is ___, check-out date is ___, and there are ___ guests.`;
  return `<a class="${style}" href="${esc(contact(message))}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
}
function chips(items) {
  return `<ul class="facts">${items.filter(Boolean).map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
}
function hero({crumbs, eyebrow, heading, intro, actions='', image, alt, caption, inset, insetAlt, facts=[]}) {
  return `<section class="hero ${inset?'':'hero-sub'}"><div class="wrap">
    <nav class="crumb" aria-label="Breadcrumb">${crumbs.map((b,i)=>`${i?'<span aria-hidden="true">/</span>':''}${i===crumbs.length-1?`<span aria-current="page">${esc(b[0])}</span>`:`<a href="${esc(b[1])}">${esc(b[0])}</a>`}`).join('')}</nav>
    <div class="hero-grid"><div class="hero-main"><p class="eyebrow">${esc(eyebrow)}</p><h1>${heading}</h1><p class="intro">${esc(intro)}</p>${facts.length?chips(facts):''}<div class="actions">${actions}</div></div>
    <figure class="portrait ${inset?'hub-portrait':''}"><img class="main-pic" src="${esc(image)}" alt="${esc(alt)}" fetchpriority="high" width="1000" height="740">${inset?`<img class="inset-pic" src="${esc(inset)}" alt="${esc(insetAlt)}" width="380" height="380">`:''}<figcaption>${esc(caption)}</figcaption></figure>
    </div></div></section>`;
}
function photographCredits(ids, map) {
  const unique = [...new Set(ids)];
  if (!unique.length && !map) return '';
  return `<details class="credits"><summary>Photography and map credits</summary><ul>${unique.map(id=>{
    const l=landmarks[id];
    return `<li><a href="${esc(l.sourcePage)}">${esc(l.originalTitle || l.name)}</a> by ${esc(l.author)}. <a href="${esc(l.licenseUrl)}">${esc(l.license)}</a>. ${esc(l.changes)}${/BY-SA/i.test(l.license)?' The adapted photograph uses the same licence.':''}</li>`;
  }).join('')}${map?'<li>Map outlines from <a href="https://www.naturalearthdata.com/about/terms-of-use/">Natural Earth</a>, public domain. Sarawak is represented by Kuching.</li>':''}</ul></details>`;
}
function frame({url, title, description, crumbs, photo, body, credits=[], map=false, entity}) {
  if (urls.has(url)) throw Error('Duplicate page ' + url);
  urls.set(url,photo);
  const graph = [
    {'@type':'WebPage','@id':origin+url+'#page',url:origin+url,name:title,description,inLanguage:'en',primaryImageOfPage:{'@type':'ImageObject',url:origin+photo}},
    {'@type':'BreadcrumbList',itemListElement:crumbs.map(([name,href],i)=>({'@type':'ListItem',position:i+1,name,item:origin+href}))}
  ];
  if(entity) graph.push(entity);
  const structured=JSON.stringify({'@context':'https://schema.org','@graph':graph}).replace(/</g,'\\u003c');
  const page=`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(title)}</title><meta name="description" content="${esc(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="${origin+url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="NextGenz Centre"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:url" content="${origin+url}"><meta property="og:image" content="${origin+photo}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0f1f38">
<link rel="icon" href="/assets/brand/nextgenz-official-crest-fallback.png"><link rel="stylesheet" href="${assets}guide.css"><script defer src="${assets}guide.js"></script><script type="application/ld+json">${structured}</script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="sitebar"><div class="wrap bar"><a class="brand" href="/"><img src="/assets/brand/nextgenz-official-crest-fallback.png" alt="" width="38" height="42"><span>NextGenz Centre<small>STAYS IN MALAYSIA</small></span></a><nav aria-label="Accommodation navigation"><a href="${hub}#destinations">Destinations</a><a href="${hub}#apartments">Apartments</a><a class="nav-contact" href="${contact('Hi NextGenz Centre, I would like help finding accommodation in Malaysia.')}" target="_blank" rel="noopener noreferrer">WhatsApp</a></nav></div></header>
<main id="main">${body}</main><footer class="wrap"><div class="foot"><strong>NextGenz Centre</strong><nav aria-label="Footer"><a href="${hub}">Malaysia stays</a><a href="/#services">All services</a><a href="/programmes/">Study programmes</a><a href="/privacy-policy.html">Privacy</a></nav></div>${photographCredits(credits,map)}</footer></body></html>`;
  const target = path.join(root,url.slice(1));
  fs.mkdirSync(path.dirname(target),{recursive:true});
  fs.writeFileSync(target,page);
}
const homeCrumb = ['Home','/'];
const stayCrumb = ['Accommodation',hub];
const section = (id, label, title, body) => `<section class="section" id="${id}"><div class="wrap">${label?`<p class="section-kicker">${esc(label)}</p>`:''}<h2>${esc(title)}</h2>${body}</div></section>`;
function booking(topic, status) {
  if (['upcoming', 'planned', 'enquiry'].includes(status)) {
    const message = 'Hi NextGenz Centre, please update me about future stays in ' + topic + '. My preferred dates are ___.';
    return `<section id="stayEnquiry" class="booking"><div class="wrap"><h2>Planning a future visit?</h2><p>Tell us the area and month of your visit. We can check which projects are taking enquiries and suggest available alternatives.</p><a class="btn" target="_blank" rel="noopener noreferrer" href="${esc(contact(message))}">Ask about future stays</a></div></section>`;
  }
  return `<section id="stayEnquiry" class="booking"><div class="wrap">
    <h2>Book at the NextGenz nightly rate</h2>
    <p>${esc(nightlyOffer)} Choose your dates to see the discounted room price. Your booking total includes any applicable fees and taxes.</p>
    <div class="actions">${partnerLink()}${bookingLink(topic, 'Book now on WhatsApp', 'btn outline partner-link')}</div>
    <p class="rate-note"><a href="${hub}#how-to-book">How to book through NextGenz Centre</a></p>
  </div></section>`;
}
function bookingGuide() {
  return section('how-to-book', 'NextGenz Centre × NaiBnb', 'How to book your apartment in Malaysia', `
    <div class="booking-guide">
      <div>
        <p class="section-lead"><strong>Save 30% on each night’s room rate.</strong> NaiBnb applies the 25% NextGenz partner rate plus an activation promotion worth another 5% of the original room rate. Your search shows the rate for your dates. Cleaning fees and applicable taxes are calculated separately at checkout.</p>
        <ol class="booking-steps">
          <li><h3>Choose your dates</h3><p>Open the NextGenz partner booking page. Choose your check-in and check-out dates and select <strong>Search</strong>. Set the guest count and filter by city, building or beds.</p></li>
          <li><h3>Choose an apartment</h3><p>Compare the photos and the discounted nightly prices. Select <strong>Add</strong>. If several units share a layout, use <strong>Want a specific room number?</strong> and <strong>Pick</strong> to request one.</p></li>
          <li><h3>Review the total and pay</h3><p>Select <strong>Proceed to checkout</strong>. Enter your name, email, phone and guest details. Review the room price, fees and applicable taxes, then choose from the payment options offered for your booking. NaiBnb sends the confirmation to your email.</p></li>
        </ol>
        <div class="actions">${partnerLink()}${bookingLink('an apartment in Malaysia', 'Ask on WhatsApp', 'btn outline')}</div>
      </div>
      <figure class="booking-flyer"><a href="${partnerBooking}" target="_blank" rel="sponsored noopener noreferrer"><img src="${assets}nextgenz-naibnb-booking-guide.webp" width="864" height="1536" loading="lazy" alt="NextGenz Centre and Nai Hospitality partner flyer. Scan the QR code or open the partner booking page."></a></figure>
    </div>`);
}
function localSection(title, subtitle, places, images) {
  const visuals=images.slice(0,2).map(key=>{const l=landmarks[key];return `<figure><img src="${landmarkUrl(key)}" width="${l.width}" height="${l.height}" alt="${esc(l.caption)}" loading="lazy"><figcaption>${esc(l.caption)}</figcaption></figure>`}).join('');
  return section('local-guide','Around the area',title,`<div class="places"><div><p class="section-lead">${esc(subtitle)}</p><div class="place-list">${places.map(l=>`<article class="place-card"><h3>${esc(l.name)}</h3><p>${esc(l.detail)}</p>${l.url?`<a href="${esc(l.url)}">Visitor information for ${esc(l.name)}</a>`:''}</article>`).join('')}</div></div><div class="local-images">${visuals}</div></div>`);
}
function propertyCard(p, filterable=false) {
  const g=guides[p.slug];
  return `<article class="card" ${filterable?`data-stay-card data-search="${esc((p.name+' '+g.locality+' '+regionNames[g.area]).toLowerCase())}" data-region="${g.area}"`:''}><a href="${propertyUrl(p.slug)}"><img src="${roomCover(p)}" width="800" height="500" alt="${esc(p.coverAlt)}" loading="lazy"><small>${esc(g.locality)}</small><h3>${esc(p.name)}</h3><p>${esc(g.note)}</p></a></article>`;
}
function plannedProjects(gs) {
  return `<div class="project-list">${gs.map(([id,g])=>`<article><span class="tag">${statusLabel[g.projectStatus]}</span><h3><a href="${propertyUrl(id)}">${esc(g.name)}</a></h3><p>${esc(g.note)}</p></article>`).join('')}</div>`;
}
function range(units,key,one,many=one+'s') {
  const nums=units.map(u=>u[key]).filter(n=>typeof n==='number' && n>0);
  if(!nums.length) return '';
  const min=Math.min(...nums),max=Math.max(...nums);
  return min===max?plural(min,one,many):`${min}–${max} ${many}`;
}
function roomSummary(c) {
  return [range(c.units,'beds','bed') || c.units[0].sleepingAreas?.[0]?.beds,range(c.units,'bathrooms','bathroom'),range(c.units,'guests','guest')].filter(Boolean);
}
const regionCrumb = id => [regionNames[id],regionUrl(id)];
function unitFacts(u) {
  return [bedLabel(u.bedrooms),u.beds ? plural(u.beds,'bed') : (u.sleepingAreas?.[0]?.beds || 'Bed arrangement on request'),plural(u.bathrooms,'bathroom'),`Up to ${plural(u.guests,'guest')}`];
}
const link = (url,text,style='btn') => `<a class="${style}" href="${esc(url)}">${esc(text)}</a>`;
function filteredList(cards, id, controls) {
  return `<div class="controls" data-filter-for="${id}" hidden>${controls}<output aria-live="polite"></output></div><div class="cards" id="${id}">${cards}</div>`;
}
function renderHub() {
  const crumbs=[homeCrumb,stayCrumb], pic=landmarkUrl('kuala-lumpur');
  const body=hero({crumbs,eyebrow:'NextGenz Centre × NaiBnb',heading:'Student &amp; family accommodation <em>in Malaysia.</em>',intro:'Find furnished short-stay apartments in Kuala Lumpur, Bandar Sunway and Genting Highlands for students, families and visitors. Compare room photos and sleeping arrangements, then check prices for your dates. '+nightlyOffer,actions:partnerLink()+link('#apartments','Explore apartments','btn outline')+link('#how-to-book','How to book','text-action'),image:pic,alt:landmarks['kuala-lumpur'].caption,caption:'Kuala Lumpur skyline and an Agile Bukit Bintang apartment.',inset:roomCover(buildings.get('agile-bukit-bintang')),insetAlt:buildings.get('agile-bukit-bintang').coverAlt})
    +section('destinations','Destination guide','Where would you like to stay?',`<div class="destination-links">${Object.entries(regions).map(([id,r])=>`<a class="route" href="${regionUrl(id)}"><img src="${landmarkUrl(regionMedia[id][0])}" width="54" height="54" loading="lazy" alt=""><span><strong>${esc(regionNames[id])}</strong><small>${regionStatus[r.status]}</small></span></a>`).join('')}</div>`)
    +section('apartments','The apartment collection','Explore the apartments',`<p class="section-lead">Choose a building to compare room layouts and see photos for each apartment. For a campus visit, start with the neighbourhood closest to your appointments.</p>`+filteredList(catalogue.map(p=>propertyCard(p,true)).join(''),'property-cards',`<label>Property or neighbourhood<input type="search" placeholder="e.g. Quill or Bandar Sunway"></label><label>Destination<select><option value="">All apartment destinations</option>${Object.keys(regions).filter(id=>regions[id].status==='catalogue').map(id=>`<option value="${id}">${esc(regionNames[id])}</option>`).join('')}</select></label>`))
    +section('compare-stays','Choose by location','Compare short-stay apartments by neighbourhood',`<p class="section-lead">For a central Kuala Lumpur visit, compare <a href="${propertyUrl('agile-bukit-bintang')}">Agile Bukit Bintang apartments near TRX</a> and <a href="${propertyUrl('axon-bukit-bintang')}">Axon Bukit Bintang apartments near Pavilion</a>. Around Jalan Sultan Ismail and Chow Kit, explore <a href="${propertyUrl('quill-residences')}">Quill Residences</a>, <a href="${propertyUrl('regalia-residence')}">Regalia Residence</a> and <a href="${propertyUrl('the-colony-by-infinitum')}">The Colony by Infinitum</a>. For campus visits in Bandar Sunway, see <a href="${propertyUrl('yolo-signature-suites')}">Yolo Signature Suites</a>. For a hill-resort break, see <a href="${propertyUrl('antara-genting')}">Antara Genting apartments</a>. Compare the exact lobby, sleeping arrangements and live rate before booking.</p>`)
    +section('network','Nai Hospitality projects','Our accommodation network',`<p class="section-lead">Explore the project map for Peninsular Malaysia and Sarawak. Each destination guide shows which buildings have apartment galleries and which are planned.</p><iframe id="ng-map" class="network-frame" src="/assets/accommodation-network/network.html" title="Interactive map of Nai Hospitality projects in Malaysia" loading="lazy"></iframe><noscript><img src="${assets}destination-map.webp" width="1320" height="600" alt="Destination map of Peninsular Malaysia and Sarawak"></noscript>`)
    +bookingGuide()
    +section('arrival','For students and visiting families','Plan your first weeks',`<div class="related">${link('/guides/first-weeks-accommodation-malaysia.html','Your first weeks in Malaysia','pill')}${link('/guides/choosing-student-apartment-malaysia.html','How to choose a student apartment','pill')}${link('/guides/furnished-apartments-for-students-malaysia.html','What a furnished apartment includes','pill')}</div><details class="faq"><summary>Do the photos show the apartment I choose?</summary><p>Each design has its own NG reference and gallery. Include that reference when booking so we can check the same apartment for your dates.</p></details><details class="faq"><summary>Can I check prices before I travel?</summary><p>Yes. Enter your dates on the NextGenz partner booking page, or send them on WhatsApp with the guest count and your preferred apartment.</p></details>`)
    +booking('an apartment in Malaysia');
  frame({url:hub,title:'Student Accommodation in Malaysia | NextGenz 30% Nightly Offer',description:'Book furnished short-stay apartments in Kuala Lumpur, Bandar Sunway and Genting Highlands for students and families. Save 30% on room rates during the promotion.',crumbs,photo:pic,body,credits:['kuala-lumpur',...Object.values(regionMedia).map(a=>a[0])],map:true,entity:{'@type':'ItemList',name:'Apartment guides in Malaysia',itemListElement:catalogue.map((p,i)=>({'@type':'ListItem',position:i+1,name:p.name,url:origin+propertyUrl(p.slug)}))}});
}
function renderRegion(id,r) {
  const name=regionNames[id], url=regionUrl(id), crumbs=[homeCrumb,stayCrumb,regionCrumb(id)];
  const photos=regionMedia[id], pic=landmarkUrl(photos[0]);
  const active=catalogue.filter(p=>guides[p.slug].area===id);
  const future=Object.entries(guides).filter(([,g])=>g.area===id&&g.projectStatus!=='catalogue');
  let body=hero({crumbs,eyebrow:active.length?'Malaysia destination guide':regionStatus[r.status],heading:`${esc(name)} <em>${active.length?'apartment stays':'stay guide'}</em>`,intro:r.intro,image:pic,alt:landmarks[photos[0]].caption,caption:landmarks[photos[0]].caption,actions:link(active.length?'#apartments':future.length?'#projects':'#local-guide',active.length?'See apartments':future.length?'Explore planned projects':'Explore the area')});
  if(active.length)body+=section('apartments','Places to stay',`Apartments in ${name}`,`<div class="cards">${active.map(p=>propertyCard(p)).join('')}</div>`);
  if(future.length)body+=section('projects','Project guide',active.length?'More projects in the Klang Valley':'Projects to watch',plannedProjects(future));
  body+=localSection('Places to go in '+name,r.advice,r.places,photos.slice(1).length?photos.slice(1):photos)+booking(name,r.status);
  frame({url,title:r.searchTitle || `${name} Accommodation & Area Guide | NextGenz`,description:r.intro,crumbs,photo:pic,body,credits:photos});
}
function renderProperty(id,g) {

  const p=buildings.get(id),url=propertyUrl(id),crumbs=[homeCrumb,stayCrumb,regionCrumb(g.area),[g.name,url]];
  const photos=localMedia[id]||regionMedia[g.area],pic=p?roomCover(p):landmarkUrl(photos[0]);
  const listing = p ? partnerLink()+link('#rooms','Browse room types','btn outline') : link('#local-guide','Explore the area');
  let body=hero({crumbs,eyebrow:p?g.locality:statusLabel[g.projectStatus],heading:esc(g.name)+(p?' <em>short-stay apartments</em>':''),intro:g.intro,image:pic,alt:p?p.coverAlt:landmarks[photos[0]].caption,caption:p?`${g.name} · ${g.locality}`:landmarks[photos[0]].caption,actions:listing,facts:p?[plural(p.configurations.length,'room type'),g.locality]:[g.locality]});
  if(p) {
    const layouts=[...new Set(p.configurations.map(c=>c.bedrooms).filter(Number.isInteger))].sort((a,b)=>a-b).map(bedLabel);
    const capacities=p.configurations.flatMap(c=>c.units).map(u=>u.guests).filter(n=>Number.isFinite(n)&&n>0);
    const capacity=capacities.length?` The listed designs accommodate ${Math.min(...capacities)===Math.max(...capacities)?Math.max(...capacities):Math.min(...capacities)+'–'+Math.max(...capacities)} guests, depending on the apartment.`:'';
    body+=section('booking-options','Compare before booking','Short-stay options at '+g.name,`<p class="section-lead">${esc(g.name)} in ${esc(g.locality)} has ${plural(p.configurations.length,'room type')} in our published apartment catalogue${layouts.length?': '+esc(layouts.join(', ')):''}.${esc(capacity)} Browse the individual room pages for photographs and bed arrangements. Available units and nightly prices depend on your dates.</p><p>${esc(nightlyOffer)} Cleaning fees and applicable taxes are calculated separately. Use the partner booking page to check your dates, guest count and final total.</p><div class="actions">${partnerLink('Check live apartment rates')}${link(hub+'#how-to-book','Booking instructions','btn outline')}</div>`);
    const cards=p.configurations.map(c=>`<article class="card" data-stay-card data-search="${esc(c.name.toLowerCase())}" data-region="${c.bedrooms}"><a href="${c.url}"><img src="${roomCover(c)}" alt="${esc(c.coverAlt)}" width="800" height="500" loading="lazy"><small>${esc(bedLabel(c.bedrooms))} · ${plural(c.units.length,'apartment design')}</small><h3>${esc(c.displayName)}</h3><p>${esc(roomSummary(c).join(' · '))}</p></a></article>`).join('');
    const controls=p.configurations.length>4?`<label>Room type<input type="search" placeholder="e.g. studio"></label><label>Bedrooms<select><option value="">Any layout</option>${[...new Set(p.configurations.map(c=>c.bedrooms))].sort((a,b)=>a-b).map(n=>`<option value="${n}">${bedLabel(n)}</option>`).join('')}</select></label>`:'';
    body+=section('rooms','The collection','Room types at '+p.name,controls?filteredList(cards,'room-cards',controls):`<div class="cards">${cards}</div>`);
  }
  body+=g.places.length?localSection('What to do around '+g.name,g.advice,g.places,photos):section('local-guide',g.locality,'Plan for the opening',`<p class="section-lead">${esc(g.advice)}</p>${link(regionUrl(g.area),'See current Klang Valley apartments','btn outline')}`);
  if(p){
    const alternatives=catalogue.filter(q=>q.slug!==id&&guides[q.slug].area===g.area);
    if(alternatives.length)body+=section('nearby-alternatives','Compare locations','Other short-stay apartments in '+regionNames[g.area],`<div class="related">${alternatives.map(q=>link(propertyUrl(q.slug),q.name+' — '+guides[q.slug].locality,'pill')).join('')}</div>`);
  }
  body+=booking(g.name,g.projectStatus);
  const entity=p?{'@type':'ApartmentComplex',name:p.name,url:origin+url,description:g.intro,image:origin+pic,address:{'@type':'PostalAddress',addressLocality:g.locality,addressCountry:'MY'}}:undefined;
  frame({url,title:id==='agile-bukit-bintang'?'Agile Bukit Bintang Short-Stay Apartments near TRX, KL | NextGenz':g.searchTitle || `${g.name} Project Guide in ${g.locality} | NextGenz`,description:p?`${g.name}, ${g.locality}: compare ${plural(p.configurations.length,'room type')}, apartment photos and sleeping arrangements. Check live nightly rates through NextGenz and NaiBnb.`:g.intro,crumbs,photo:pic,body,credits:g.places.length?photos:[],entity});
}
function unitGallery(p,c,u,index) {
  const media = u.photos.map((id,i)=>`<figure><img data-enlarge src="/accommodation-images/${id}.jpg" alt="${esc(`${p.name}, ${c.name}, apartment ${u.code}, photo ${i+1}`)}" width="640" height="426" loading="lazy" decoding="async"></figure>`);
  const sleeping=(u.sleepingAreas||[]).map(x=>`${x.label} (${x.beds})`).join(' · ');
  const more=media.length>3?`<details class="more"><summary>View all ${media.length} photos</summary><div class="gallery">${media.slice(3).join('')}</div></details>`:'';
  return `<details class="unit" id="${u.code.toLowerCase()}" ${index===0?'open':''}><summary><span><strong>Apartment ${esc(u.code)}</strong><small>${esc(unitFacts(u).slice(1).join(' · '))} · ${plural(u.photos.length,'photo')}</small></span></summary><div class="unit-body">${sleeping?`<p><strong>Sleeping arrangements</strong> · ${esc(sleeping)}</p>`:''}${u.amenities.length?`<p><strong>Apartment features</strong> · ${esc(u.amenities.join(', '))}</p>`:''}${bookingLink(`${p.name}, ${c.name} (apartment ${u.code})`)}<div class="gallery">${media.slice(0,3).join('')}</div>${more}</div></details>`;
}
function renderRoom(p,c) {
  const g=guides[p.slug],crumbs=[homeCrumb,stayCrumb,regionCrumb(g.area),[p.name,propertyUrl(p.slug)],[c.displayName,c.url]];
  const limits=roomSummary(c);
  const intro = c.units.length === 1
    ? `See the sleeping arrangement and room photos for this ${c.name} at ${p.name} in ${g.locality}. Check availability for up to ${plural(c.units[0].guests,'guest')} on your dates.`
    : `Explore ${plural(c.units.length,'apartment design')} for the ${c.name} at ${p.name} in ${g.locality}. Compare the beds and photographs for each apartment before choosing a reference.`;
    const other=p.configurations.filter(x=>x!==c).sort((a,b)=>Math.abs(a.bedrooms-c.bedrooms)-Math.abs(b.bedrooms-c.bedrooms)).slice(0,4);
  const body=hero({crumbs,eyebrow:p.name,heading:esc(c.displayName),intro,image:roomCover(c),alt:c.coverAlt,caption:`${p.name} · Apartment ${c.coverReference}`,facts:[...limits],actions:link('#designs','See apartments and photos')+partnerLink('Check dates on NaiBnb')})
    +section('designs','Photos and sleeping arrangements','Choose an apartment design',`<p class="section-lead">Open an apartment to see its photographs and sleeping arrangements. Its reference travels with your WhatsApp enquiry.</p>${c.units.map((u,i)=>unitGallery(p,c,u,i)).join('')}<dialog class="lightbox" aria-label="Apartment photo viewer"><div class="viewer-bar"><button type="button" data-step="-1">Previous</button><button type="button" data-close autofocus>Close</button><button type="button" data-step="1">Next</button></div><img alt=""><p class="viewer-caption" aria-live="polite"></p></dialog>`)
    +booking(p.name+', '+c.name)
    +section('neighbourhood',g.locality,'Plan your stay',`<p class="section-lead">${esc(g.note)} ${esc(g.places[0].detail)}</p><div class="related">${link(propertyUrl(p.slug)+'#local-guide','Neighbourhood guide to '+p.name,'pill')}${link(regionUrl(g.area),'Explore '+regionNames[g.area],'pill')}</div>`)
    +(other.length?section('more-rooms','At the same property','Other room types',`<div class="related">${other.map(x=>link(x.url,x.displayName,'pill')).join('')}</div>`):'');
  frame({url:c.url,title:`${c.displayName} at ${p.name} | NextGenz Stays`,description:`${c.displayName} at ${p.name} in ${g.locality}. View ${plural(c.units.length,'apartment design')}, compare sleeping arrangements and check the NextGenz nightly rate for your dates.`,crumbs,photo:roomCover(c),body,entity:{'@type':'Apartment',name:c.name,containedInPlace:{'@type':'ApartmentComplex',name:p.name,url:origin+propertyUrl(p.slug)},image:origin+roomCover(c),url:origin+c.url}});
}
renderHub();
for(const [id,r] of Object.entries(regions))renderRegion(id,r);
for(const [id,g] of Object.entries(guides))renderProperty(id,g);
for(const p of catalogue)for(const c of p.configurations)renderRoom(p,c);
// Add contextual backlinks from existing student-arrival articles.
const guideLinks={
 'first-weeks-accommodation-malaysia.html':[['klang-valley','Kuala Lumpur and Klang Valley short-stay apartments'],['agile-bukit-bintang','Agile Bukit Bintang near TRX']],
 'choosing-student-apartment-malaysia.html':[['agile-bukit-bintang','Agile Bukit Bintang room types'],['quill-residences','Quill Residences apartments'],['regalia-residence','Regalia Residence apartments']],
 'furnished-apartments-for-students-malaysia.html':[['agile-bukit-bintang','Agile Bukit Bintang furnished apartments'],['yolo-signature-suites','Yolo Signature Suites in Bandar Sunway']]
};
for(const [file,items] of Object.entries(guideLinks)){
 const target=path.join(root,'guides',file);
 let html=fs.readFileSync(target,'utf8');
 const marker='id="ng-stays-location-links"';
 if(html.includes(marker))continue;
 if(!html.includes('</article>'))throw Error('Missing guide article: '+file);
 const links=items.map(([id,label])=>{
   const url=regions[id]?regionUrl(id):propertyUrl(id);
   if(!urls.has(url))throw Error('Unknown accommodation guide link '+url);
   return link(url,label,'');
 }).join(' · ');
 html=html.replace('</article>','<section '+marker+'><h2>Compare named apartment buildings</h2><p>Use the building guides to compare location and room layouts before checking the current rate for your dates.</p><p>'+links+'</p></section></article>');
 fs.writeFileSync(target,html);
}
// Check all generated canonicals, crawl directives and intended public navigation.
for(const url of urls.keys()){
 const html=fs.readFileSync(path.join(root,url.slice(1)),'utf8');
 if(!html.includes('<link rel="canonical" href="'+origin+url+'">')||!html.includes('name="robots" content="index,follow,max-image-preview:large"')||html.includes('href="/portal-app.html#services"'))throw Error('Accommodation SEO check failed '+url);
}
const sitemapFile=path.join(root,'sitemap.xml');
let sitemap=fs.readFileSync(sitemapFile,'utf8').replace(/<url>([\s\S]*?)<\/url>/g,(match,inside)=>{
  const loc=inside.match(/<loc>([^<]*)<\/loc>/)?.[1];
  return loc&&(loc===origin+hub||loc.startsWith(origin+'/services/stays/'))?'':match;
});
if(!sitemap.includes('xmlns:image='))sitemap=sitemap.replace('<urlset ','<urlset xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" ');
const entries=[...urls].map(([url,img])=>`<url><loc>${origin+url}</loc><image:image><image:loc>${origin+img}</image:loc></image:image></url>`).join('\n');
if(!sitemap.includes('</urlset>'))throw Error('Main sitemap must be a URL set');
fs.writeFileSync(sitemapFile,sitemap.replace('</urlset>',entries+'\n</urlset>'));
console.log(`Built ${urls.size} accommodation guides with ${catalogue.length} apartment buildings and ${catalogue.flatMap(p=>p.configurations).flatMap(c=>c.units).length} apartment galleries.`);
