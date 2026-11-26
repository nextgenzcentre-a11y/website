'use strict';
(async () => {
  const $=id=>document.getElementById(id), api='/api/accommodation';
  const status=$('reviewStatus');
  let catalogue=[],collection,variant,unit,shown=24,index=0;
  try {
    const response=await fetch(api+'?part=public',{credentials:'same-origin',cache:'no-store'});
    if (!response.ok) throw Error(response.status===403?'The accommodation catalogue is temporarily unavailable. Please contact NextGenz for current apartment options.':'The accommodation catalogue could not load. Please reload or contact NextGenz.');
    catalogue=await response.json();
    if (!Array.isArray(catalogue) || !catalogue.length) throw Error('The catalogue is temporarily unavailable.');
  } catch(e) { status.textContent=e.message;return; }
  const pad=n=>String(n).padStart(2,'0');
  function options(node,arr,label,key) {
    node.replaceChildren(...arr.map((row,i)=>new Option(label(row,i),row[key])));
  }
  function imageURL(i) {
    return api+'?'+new URLSearchParams({part:'public-photo',code:unit.code,index:String(i)});
  }
  function message(dates) {
    const details=dates?' Check-in '+$('inDate').value+', check-out '+$('outDate').value+', '+$('guests').value+' guest(s).':'';
    return 'https://wa.me/601167701210?text='+encodeURIComponent('Hello NextGenz Centre, I would like to book '+unit.code+' in '+collection.city+'.'+details+' Please confirm the live price and availability.');
  }
  function setCollection(){
    collection=catalogue.find(c=>c.id===$('collection').value);
    options($('config'),collection.variants,v=>v.id+' · up to '+v.guests+' guests','id');setVariant();
  }
  function setVariant(){
    variant=collection.variants.find(v=>v.id===$('config').value);
    options($('unit'),variant.units,(u,i)=>'Apartment '+pad(i+1)+' · '+u.code,'code');setUnit();
  }
  function setUnit(){
    unit=variant.units.find(u=>u.code===$('unit').value);shown=24;index=0;
    $('roomTitle').textContent=unit.code;
    $('facts').textContent=collection.title+' · '+variant.beds+' bed'+(variant.beds===1?'':'s')+' · '+variant.bathrooms+' bathroom'+(variant.bathrooms===1?'':'s')+' · Up to '+variant.guests+' guests';
    $('features').textContent=variant.features.join(' · ');
    $('galleryCount').textContent=unit.pictures+' photos of the apartment and its shared spaces';
    $('guests').max=String(variant.guests);$('guests').value=String(Math.min(variant.guests,Number($('guests').value)||1));
    $('quickBook').href=message(false);$('photos').replaceChildren();showPhotos();
  }
  function showPhotos() {
    for(let i=$('photos').children.length;i<Math.min(shown,unit.pictures);i++){
      const b=document.createElement('button');b.className='tile';b.type='button';b.setAttribute('aria-label','View apartment photo '+(i+1));
      const im=new Image();im.loading='lazy';im.decoding='async';im.alt=unit.code+', apartment photo '+(i+1);im.src=imageURL(i);b.append(im);
      b.onclick=()=>{index=i;large();$('light').showModal();};$('photos').append(b);
    }
    $('more').hidden=shown>=unit.pictures;
    $('more').textContent='Show more photos ('+Math.max(0,unit.pictures-shown)+' remaining)';
  }
  function large(){$('large').src=imageURL(index);$('large').alt=unit.code+', photo '+(index+1);$('photoLabel').textContent=unit.code+' · Photo '+(index+1)+' of '+unit.pictures;}
  $('collection').onchange=setCollection;$('config').onchange=setVariant;$('unit').onchange=setUnit;
  $('more').onclick=()=>{shown+=24;showPhotos();};
  $('prev').onclick=()=>{index=(index+unit.pictures-1)%unit.pictures;large();};$('next').onclick=()=>{index=(index+1)%unit.pictures;large();};$('closeLight').onclick=()=>$('light').close();
  $('light').onkeydown=e=>{if(e.key==='ArrowRight')$('next').click();if(e.key==='ArrowLeft')$('prev').click();};
  $('datedBook').onsubmit=e=>{e.preventDefault();if($('outDate').value<=$('inDate').value){$('outDate').setCustomValidity('Choose a date after check-in.');$('outDate').reportValidity();return;}window.open(message(true),'_blank','noopener,noreferrer');};
  $('inDate').oninput=$('outDate').oninput=()=>$('outDate').setCustomValidity('');
  options($('collection'),catalogue,c=>c.id+' · '+c.title,'id');setCollection();const requested=new URLSearchParams(location.search).get('unit');if(requested){for(const c of catalogue){const v=c.variants.find(v=>v.units.some(u=>u.code===requested));if(v){$('collection').value=c.id;setCollection();$('config').value=v.id;setVariant();$('unit').value=requested;setUnit();break;}}}$('workspace').hidden=false;status.textContent='';
})();

addEventListener("message",e=>{const f=document.getElementById("ng-map");if(f&&e.origin===location.origin&&e.source===f.contentWindow&&e.data?.type==="ng-accommodation-map-height"&&Number.isFinite(e.data.height))f.style.height=Math.min(2400,Math.max(300,e.data.height))+"px"});
