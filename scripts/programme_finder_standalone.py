"""Standalone shareable, filterable NextGenz course finder page."""
import json
from html import escape
from urllib.parse import quote

PAGE_PATH = "/programmes/find/"
JS_PATH = "programmes/site-assets/find-course.js"

CSS = """
<style id="ng-find-style">
.ng-find-shell{background:#F0E3D2;color:#0F1F38}
.ng-find-intro{margin:0 0 26px;padding:24px 28px;background:#F7EBD9;border:1px solid #C5A059;border-radius:20px}
.ng-find-intro h2{margin-top:0;color:#0F1F38}
.ng-find-form{display:grid;grid-template-columns:1fr 1fr minmax(220px,1.6fr);gap:16px;align-items:end;margin:22px 0}
.ng-find-form label{display:block;font-size:.84rem;font-weight:800;color:#0F1F38}
.ng-find-form select,.ng-find-form input{display:block;width:100%;height:50px;margin-top:7px;border:1px solid #B99555;border-radius:12px;background:#F0E3D2;color:#0F1F38;padding:10px 14px;font:inherit;font-size:.9rem}
.ng-find-form select:focus-visible,.ng-find-form input:focus-visible{outline:3px solid #C5A059;outline-offset:2px}
.ng-find-chips{display:flex;gap:9px;flex-wrap:wrap;margin:22px 0}
.ng-find-chips button,.ng-find-clear{background:#E2CFB3;border:1px solid #C5A059;color:#0F1F38;border-radius:99px;padding:9px 13px;font:inherit;font-size:.82rem;font-weight:800;cursor:pointer}
.ng-find-chips button:hover,.ng-find-clear:hover{background:#C5A059}
.ng-find-heading{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin:26px 0 16px}
.ng-find-heading h2{margin:0;color:#0F1F38}
.ng-find-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.ng-find-card{background:#F7EBD9;border:1px solid #C5A059;border-radius:18px;padding:21px;display:flex;flex-direction:column;gap:13px;min-width:0}
.ng-find-uni{display:flex;align-items:center;gap:11px;font-size:.82rem;color:#0F1F38;font-weight:800}
.ng-find-monogram{width:46px;height:46px;display:grid;place-items:center;flex:none;border:1px solid #C5A059;border-radius:13px;background:#E2CFB3;font-weight:900;font-size:.72rem}
.ng-find-uni span{display:block;color:#665138;font-size:.75rem;font-weight:600}
.ng-find-level{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;font-weight:900;color:#75531D}
.ng-find-card h3{font-size:1rem;line-height:1.45;margin:0;color:#0F1F38}
.ng-find-card h3 a{color:#0F1F38;text-decoration:none}
.ng-find-card h3 a:hover{text-decoration:underline}
.ng-find-fee{background:#E2CFB3;border-left:3px solid #C5A059;border-radius:10px;padding:10px 12px;font-size:.8rem;color:#0F1F38}
.ng-find-fee strong{display:block;color:#0F1F38}
.ng-find-card-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:auto}
.ng-find-card-actions a{display:grid;place-items:center;text-decoration:none;text-align:center;font-size:.77rem;font-weight:850;line-height:1.4;border-radius:10px;padding:11px 9px;border:1px solid #C5A059;color:#0F1F38;background:#E2CFB3}
.ng-find-card-actions a:first-child{grid-column:1/-1;background:#C5A059}
.ng-find-card-actions a:hover{background:#D4AF37}
.ng-find-notice{margin-top:13px;color:#624B29;font-size:.76rem}
.ng-find-more{margin:28px auto 10px;display:block;border-radius:12px;background:#C5A059;color:#0F1F38;border:1px solid #B99555;padding:13px 24px;font-weight:850;font:inherit;cursor:pointer}
.ng-find-empty{padding:24px;border-radius:16px;background:#F7EBD9;border:1px solid #C5A059;color:#0F1F38}
.ng-find-footnote{background:#0F1F38;border:1px solid #C5A059;border-radius:20px;color:#F0E3D2;padding:26px;margin-top:40px}
.ng-find-footnote h2,.ng-find-footnote p{color:#F0E3D2}
.ng-find-footnote a{color:#E7C37B}
@media(max-width:980px){.ng-find-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:680px){.ng-find-form{grid-template-columns:1fr}.ng-find-grid{grid-template-columns:1fr}.ng-find-intro{padding:20px}.ng-find-card{padding:18px}}
</style>
"""

JS = r"""
(() => {
  const source=document.getElementById('ng-find-data');
  const form=document.getElementById('ng-find-form');
  if(!source||!form)return;
  const data=JSON.parse(source.textContent);
  const university=form.elements.namedItem('university');
  const level=form.elements.namedItem('level');
  const keyword=form.elements.namedItem('keyword');
  const grid=document.getElementById('ng-find-grid');
  const count=document.getElementById('ng-find-count');
  const more=document.getElementById('ng-find-more');
  const empty=document.getElementById('ng-find-empty');
  const clear=document.getElementById('ng-find-clear');
  const params=new URLSearchParams(location.search);
  university.value=params.get('university')||'';
  level.value=params.get('level')||'';
  keyword.value=params.get('q')||'';
  let limit=12;
  const el=(tag,klass,content)=>{
    const node=document.createElement(tag);
    if(klass)node.className=klass;
    if(content!==undefined)node.textContent=content;
    return node;
  };
  function makeCard(p){
    const card=el('article','ng-find-card');
    const universityRow=el('div','ng-find-uni');
    universityRow.append(el('div','ng-find-monogram',p.s));
    const universityDetails=el('div','',p.u);
    universityDetails.append(el('span','',p.c+', Malaysia'));
    universityRow.append(universityDetails);
    const badge=el('span','ng-find-level',p.l+' programme');
    const title=el('h3');
    const titleLink=el('a','',p.n);
    titleLink.href=p.d;
    title.append(titleLink);
    const fee=el('div','ng-find-fee');
    fee.append(el('strong','',p.f),el('span','', 'Tuition reference · confirm fees for your intake'));
    const actions=el('div','ng-find-card-actions');
    const detail=el('a','','View programme details');
    detail.href=p.d;
    const context=p.n+' at '+p.u;
    const consult=el('a','','Free consultation on WhatsApp');
    consult.href='https://wa.me/601167701210?text='+encodeURIComponent('Hello NextGenz Centre. Please advise me on '+context+'. I need verified admission requirements, tuition and available intakes.');
    consult.target='_blank';consult.rel='noopener noreferrer';
    const apply=el('a','','Apply Now');
    apply.href='/?programme='+encodeURIComponent(context)+'#/registerasstudent';
    actions.append(detail,consult,apply);
    card.append(universityRow,badge,title,fee,actions);
    if(/[(/,]/.test(p.n))card.append(el('p','ng-find-notice','Check the exact course title and specialisation before applying.'));
    return card;
  }
  function render(){
    const uni=university.value;
    const lev=level.value;
    const terms=keyword.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const results=data.filter(p=>
      (!uni||p.s===uni)&&(!lev||p.l===lev)&&
      terms.every(w=>(p.n+' '+p.u+' '+p.s+' '+p.l).toLowerCase().includes(w))
    );
    const shown=results.slice(0,limit);
    grid.replaceChildren(...shown.map(makeCard));
    count.textContent=results.length.toLocaleString('en-MY')+' matching programmes · showing '+shown.length.toLocaleString('en-MY');
    empty.hidden=results.length!==0;
    more.hidden=shown.length>=results.length;
    const url=new URL(location.href);
    for(const key of ['q','university','level'])url.searchParams.delete(key);
    if(keyword.value.trim())url.searchParams.set('q',keyword.value.trim());
    if(uni)url.searchParams.set('university',uni);
    if(lev)url.searchParams.set('level',lev);
    history.replaceState(null,'',url.pathname+url.search+url.hash);
  }
  function update(){limit=12;render()}
  university.addEventListener('change',update);
  level.addEventListener('change',update);
  keyword.addEventListener('input',update);
  form.addEventListener('submit',event=>{event.preventDefault();render()});
  more.addEventListener('click',()=>{limit+=12;render()});
  clear.addEventListener('click',()=>{university.value='';level.value='';keyword.value='';update();keyword.focus()});
  for(const chip of document.querySelectorAll('[data-ng-find-keyword]')){
    chip.addEventListener('click',()=>{keyword.value=chip.dataset.ngFindKeyword;university.value='';level.value='';update()});
  }
  window.addEventListener('popstate',()=>{
    const p=new URLSearchParams(location.search);
    university.value=p.get('university')||'';
    level.value=p.get('level')||'';
    keyword.value=p.get('q')||'';
    update();
  });
  render();
})();
"""

def publish_find_page(records, universities, *, write, wrap_page, page_head, outputs, h):
    """Create direct-access catalogue search with intact university course links."""
    entries=[{
        "n":r["name"], "u":r["uni"], "s":r["short"], "l":r["level"],
        "c":r["location"], "f":r["fee"], "d":r["detail"]
    } for r in records]
    data=json.dumps(entries,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    uni_options=''.join('<option value="'+h(u["shortName"])+'">'+h(u["university"])+'</option>' for u in universities)
    levels=['Foundation','Diploma','Bachelor','Master','Doctorate','Other']
    level_options=''.join('<option value="'+h(l)+'">'+h(l)+'</option>' for l in levels)
    initial=[]
    for r in entries[:12]:
        topic=r["n"]+' at '+r["u"]
        consult="https://wa.me/601167701210?text="+quote("Hello NextGenz Centre. Please advise me on "+topic+". I need verified admission requirements, tuition and available intakes.",safe="")
        apply="/?programme="+quote(topic,safe="")+"#/registerasstudent"
        initial.append(
          '<article class="ng-find-card"><div class="ng-find-uni"><div class="ng-find-monogram">'+h(r["s"])+'</div><div>'+h(r["u"])+'<span>'+h(r["c"])+', Malaysia</span></div></div>'
          '<span class="ng-find-level">'+h(r["l"])+' programme</span>'
          '<h3><a href="'+h(r["d"])+'">'+h(r["n"])+'</a></h3>'
          '<div class="ng-find-fee"><strong>'+h(r["f"])+'</strong>Tuition reference · confirm fees for your intake</div>'
          '<div class="ng-find-card-actions"><a href="'+h(r["d"])+'">View programme details</a>'
          '<a href="'+h(consult)+'" target="_blank" rel="noopener noreferrer">Free consultation on WhatsApp</a>'
          '<a href="'+h(apply)+'">Apply Now</a></div></article>'
        )
    main=(
      '<section class="hero"><div class="wrap"><span class="eyebrow">NEXTGENZ · UNIVERSITY DISCOVERY</span>'
      '<h1>Find a course that fits your future</h1>'
      '<p class="lead">Search '+format(len(records),",")+' listed programmes across '+str(len(universities))+' Malaysian universities. '
      'Choose a university, study level or subject, then open a dedicated course page with the available facts, fees guidance and application steps.</p></div></section>'
      '<section class="section ng-find-shell"><div class="wrap">'
      '<div class="ng-find-intro"><h2>Discover first. Let us handle the details.</h2>'
      '<p>Compare the real programme titles from our university finder. Use <strong>View programme details</strong> for '
      'each course; our advisors can then help verify official intakes, entry requirements and the full international fee schedule.</p>'
      '<form id="ng-find-form" class="ng-find-form" role="search">'
      '<label>University<select name="university"><option value="">All universities</option>'+uni_options+'</select></label>'
      '<label>Study level<select name="level"><option value="">Any level</option>'+level_options+'</select></label>'
      '<label>Programme keyword<input type="search" name="keyword" placeholder="e.g. Computer Science" maxlength="120"></label>'
      '</form><div class="ng-find-chips" aria-label="Popular course searches">'
      '<button type="button" data-ng-find-keyword="computer">Computer Science &amp; IT</button>'
      '<button type="button" data-ng-find-keyword="business">Business &amp; Management</button>'
      '<button type="button" data-ng-find-keyword="engineering">Engineering</button>'
      '<button type="button" data-ng-find-keyword="medicine">Healthcare &amp; Medicine</button>'
      '<button type="button" data-ng-find-keyword="english">English pathways</button>'
      '</div></div>'
      '<div class="ng-find-heading"><h2>Programme matches</h2><button id="ng-find-clear" class="ng-find-clear" type="button">Clear filters</button></div>'
      '<p class="catalog-count" role="status" id="ng-find-count">'+str(len(records))+' matching programmes · showing 12</p>'
      '<div id="ng-find-grid" class="ng-find-grid" aria-live="polite">'+''.join(initial)+'</div>'
      '<p id="ng-find-empty" class="ng-find-empty" hidden>No matching programmes. Try a shorter keyword or clear your filters.</p>'
      '<button id="ng-find-more" class="ng-find-more" type="button">Show more programmes</button>'
      '<div class="ng-find-footnote"><h2>Not sure which programme to choose?</h2>'
      '<p>The finder is a reference catalogue. Some titles group multiple specialisations, and tuition or intake information may change. '
      'Choose the exact award with the university and request a current written fee schedule before paying.</p>'
      '<p><a href="/programmes/">Browse university and study-level directories</a> · '
      '<a href="/guides/how-to-study-in-malaysia.html">International student application guide</a></p></div>'
      '</div></section>'
      '<script id="ng-find-data" type="application/json">'+data+'</script>'
      '<script defer src="/programmes/site-assets/find-course.js?v=20261122"></script>'
    )
    head=page_head(
      "Find a Course in Malaysia | University Programme Finder | NextGenz Centre",
      "Search university programmes in Malaysia by institution, study level and subject. Open dedicated course pages, compare options and apply with NextGenz Centre.",
      PAGE_PATH,
      {"@context":"https://schema.org","@type":"CollectionPage","name":"Find a course that fits your future","url":"https://www.nextgenzcentre.space"+PAGE_PATH}
    )
    head=head.replace("</head>",CSS+"</head>",1)
    write("programmes/find/index.html",wrap_page(head,main),outputs)
    write(JS_PATH,JS,outputs)
