(function guide(){
  'use strict';
  for(const controls of document.querySelectorAll('[data-filter-for]')){
    const box=document.getElementById(controls.dataset.filterFor);
    const cards=[...box.querySelectorAll('[data-stay-card]')];
    const input=controls.querySelector('input'), select=controls.querySelector('select'), count=controls.querySelector('output');
    function filter(){
      const term=input.value.trim().toLowerCase();
      let visible=0;
      for(const card of cards){
        card.hidden=!(card.dataset.search.includes(term)&&(!select.value||select.value===card.dataset.region));
        if(!card.hidden)visible++;
      }
      count.textContent=visible?`${visible} ${visible===1?'match':'matches'}`:'No matches. Try another name or destination.';
    }
    input.addEventListener('input',filter); select.addEventListener('change',filter);
    controls.hidden=false; filter();
  }
  const network=document.querySelector('#ng-map');
  if(network){
    window.addEventListener('message',event=>{
      if(event.origin!==location.origin||event.source!==network.contentWindow||event.data?.type!=='ng-accommodation-map-height')return;
      const height=event.data.height;
      if(Number.isFinite(height))network.style.height=Math.min(2400,Math.max(300,height))+'px';
    });
  }
  const viewer=document.querySelector('dialog.lightbox');
  if(!viewer||!viewer.showModal)return;
  const image=viewer.querySelector('img'), caption=viewer.querySelector('.viewer-caption');
  let pictures=[], offset=0, trigger=null;
  function show(next){
    offset=(next+pictures.length)%pictures.length;
    const thumb=pictures[offset];
    image.alt=thumb.alt; image.src=thumb.currentSrc||thumb.src;
    caption.textContent=`Photo ${offset+1} of ${pictures.length} · ${thumb.closest('details.unit').id.toUpperCase()}`;
  }
  function enable(unit){
    if(!unit.open)return;
    for(const thumb of unit.querySelectorAll('img[data-enlarge]')){
      if(thumb.parentElement.matches('button.photo'))continue;
      const button=document.createElement('button');
      button.type='button';button.className='photo';button.setAttribute('aria-label','Enlarge '+thumb.alt);
      thumb.replaceWith(button);button.appendChild(thumb);
    }
  }
  for(const unit of document.querySelectorAll('.unit')){
    enable(unit);
    unit.addEventListener('toggle',()=>enable(unit));
  }
  function followReference(){
    const selected=document.getElementById(location.hash.slice(1).toLowerCase());
    if(selected?.matches('.unit')){selected.open=true;enable(selected);selected.scrollIntoView({block:'start'});}
  }
  window.addEventListener('hashchange',followReference);followReference();
  document.addEventListener('click',event=>{
    const button=event.target.closest('button.photo');
    if(!button)return;
    trigger=button;
    pictures=[...button.closest('.unit').querySelectorAll('img[data-enlarge]')];
    show(pictures.indexOf(button.querySelector('img')));
    viewer.showModal();
  });
  viewer.addEventListener('click',event=>{
    const button=event.target.closest('button');
    if(button?.hasAttribute('data-close'))viewer.close();
    if(button?.hasAttribute('data-step'))show(offset+Number(button.dataset.step));
  });
  viewer.addEventListener('keydown',event=>{
    if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();show(offset+(event.key==='ArrowRight'?1:-1));}
  });
  viewer.addEventListener('close',()=>{image.removeAttribute('src');if(trigger?.isConnected)trigger.focus();});
})();
