
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
