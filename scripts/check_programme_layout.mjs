// Compare the original landing-page components with the generated catalogue on a hosted Chrome runner.
import assert from 'node:assert/strict';
import {execFileSync, spawn} from 'node:child_process';
import {mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const base = mkdtempSync(join(tmpdir(), 'nextgenz-before-'));
const profile = mkdtempSync(join(tmpdir(), 'nextgenz-chrome-'));
const previous = process.env.BEFORE_SHA || 'HEAD^';
execFileSync('git', ['worktree','add','--quiet','--detach',base,previous]);
const servers = [base,process.cwd()].map((cwd,i) =>
  spawn('python3',['-m','http.server',String(9810+i),'--bind','127.0.0.1'],{cwd,stdio:'ignore'}));
const chrome = spawn(process.env.CHROME_BIN || 'google-chrome', ['--headless','--no-sandbox','--disable-dev-shm-usage',
  '--remote-debugging-port=9820','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
try {
  let tab;
  for(let i=0;i<80 && !tab;i++){
    try { tab=(await (await fetch('http://127.0.0.1:9820/json/list')).json()).find(t=>t.type==='page'); }
    catch {await delay(200);}
  }
  assert(tab,'Chrome failed to start');
  const socket=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((ok,fail)=>{socket.onopen=ok;socket.onerror=fail});
  const pending=new Map();
  const browserErrors=[];
  let id=0;
  socket.onmessage=({data})=>{
    const r=JSON.parse(data);
    if(r.method==='Runtime.exceptionThrown')browserErrors.push(r.params?.exceptionDetails?.text+' '+r.params?.exceptionDetails?.exception?.description);
    if(pending.has(r.id)){pending.get(r.id)(r);pending.delete(r.id)}
  };
  async function call(method,params={}) {
    const key=++id;const result=new Promise(ok=>pending.set(key,ok));socket.send(JSON.stringify({id:key,method,params}));
    const response=await result;assert(!response.error,JSON.stringify(response.error));return response.result;
  }
  await call('Network.enable');
  await call('Runtime.enable');
  await call('Network.setBlockedURLs',{urls:['https://*']});
  const paths=['programmes/','programmes/subjects/','programmes/subjects/master-pharmacy-malaysia.html',
    'programmes/topics/mechanical-engineering-degree-malaysia.html','programmes/levels/bachelor.html',
    'programmes/universities/unikl.html','programmes/ar/universities/unikl.html','programmes/zh/universities/unikl.html','programmes/universities/um.html','programmes/courses/um/foundation-in-life-sciences-a5be48.html',
    'programmes/english-language-centres.html','guides/compare-universities-malaysia.html',
    'ar/study-in-malaysia.html','zh/study-in-malaysia.html','services/education-consultant-malaysia.html'];
  for(const width of [390,1440]){
    await call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});
    for(const path of paths){
      const samples=[];
      for(const port of [9810,9811]){
        const url='http://127.0.0.1:'+port+'/'+path;
        await call('Page.navigate',{url});
        let value;
        for(let i=0;i<80&&!value;i++){
          const r=await call('Runtime.evaluate',{expression:`location.href===${JSON.stringify(url)} && document.readyState==='complete' && (() => {
            const h=document.querySelector('h1'),head=document.querySelector('header'),s=getComputedStyle(h);
            const row=document.querySelector('.catalog-list li'), fee=row?.querySelector('[data-ng-action="fee"]');
            return {rowDisplay:row && getComputedStyle(row).display,feeLabel:fee?.textContent,weight:s.fontWeight, surface:getComputedStyle(document.body).backgroundColor, font:s.fontFamily,size:s.fontSize,color:s.color,header:head.offsetHeight,overflow:document.documentElement.scrollWidth,
              actions:[...document.querySelectorAll('main a[data-ng-action="consult"],main a[data-ng-action="apply"]')].map(a=>a.offsetWidth>0 && a.offsetHeight>0)}
          })()`,returnByValue:true});
          value=r.result.value;if(!value)await delay(100);
        }
        assert(value,path);samples.push(value);
      }
      const [before,after]=samples;
      if (path.endsWith('/universities/unikl.html')) {
        assert.equal(after.rowDisplay,width===390?'block':'grid',path);
        assert.equal(after.feeLabel,path.includes('/ar/')?'المزيد':path.includes('/zh/')?'更多':'More',path);
      }
      assert.match(after.font,/Montserrat/,path);
      assert.equal(after.weight,'900',path);
      assert.equal(after.surface,'rgb(245, 247, 250)',path);
      assert(after.overflow<=Math.max(width,before.overflow)+1,path+' new page overflow at '+width);
      assert(after.actions.length>=4 && after.actions.every(Boolean),path+' hidden action');
    }
  }
  // Exercise a real catalogue menu and the section entrance under both OS motion preferences.
  const evalValue = async expression => (await call('Runtime.evaluate',{expression,returnByValue:true})).result.value;
  const testUrl='http://127.0.0.1:9811/programmes/universities/unikl.html';
  for (const width of [390,1440]) {
    await call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});
    await call('Page.navigate',{url:testUrl});
    for(let i=0;i<80;i++) {
      if(await evalValue("location.href.endsWith('/universities/unikl.html') && document.readyState==='complete' && !!document.querySelector('.mobile-fee-label')")) break;
      await delay(100);
    }
    const mobile=width===390;
    assert.equal(await evalValue("getComputedStyle(document.querySelector('.catalog-list-labels')).display"),mobile?'none':'grid');
    assert.equal(await evalValue("getComputedStyle(document.querySelector('.mobile-fee-label')).display"),mobile?'inline':'none');
    const menu=mobile?'.ng-brand-mobile':'.ng-brand-language';
    for (const motion of ['no-preference','reduce']) {
      await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:motion}]});
      await evalValue("document.querySelector('"+menu+"').open=false");
      await evalValue("document.querySelector('"+menu+" > summary').click()");
      const animation=await evalValue("getComputedStyle(document.querySelector('"+menu+"').lastElementChild).animationName");
      assert.equal(animation,motion==='reduce'?'none':'ng-public-enter');
    }
    await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
    await call('Runtime.evaluate',{expression:'new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))',awaitPromise:true});
    await evalValue("document.querySelectorAll('.catalog-wide > h2')[2].scrollIntoView({behavior:'instant'})");
    for(let i=0;i<30 && !await evalValue("document.querySelectorAll('.catalog-wide > h2')[2].classList.contains('ng-enter-view')");i++) await delay(100);
    assert(await evalValue("document.querySelectorAll('.catalog-wide > h2')[2].classList.contains('ng-enter-view')"));
  }
  // The offline comparison deliberately blocks Firebase/CDN calls. The public
  // homepage requires Firebase for its interactive React mount, so test its
  // server-visible fallback with the app bundle disabled rather than expecting
  // the interactive portal to boot without its dependency. Test the real common
  // footer on both static public pages below.
  for (const width of [390,1440]) {
    await call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});
    await call('Network.setBlockedURLs',{urls:['https://*','*public-app.js']});
    await call('Page.navigate',{url:'http://127.0.0.1:9811/'});
    for(let i=0;i<50;i++){
      if(await evalValue("location.pathname==='/' && !!document.querySelector('.ng-crawl-first h1')")) break;
      await delay(100);
    }
    assert(await evalValue("!!document.querySelector('.ng-crawl-first h1') && !!document.querySelector('.ng-crawl-first a[href=\"/programmes/\"]') && !!document.querySelector('.ng-crawl-first .brand-first')"),'Homepage SEO fallback');
    await call('Network.setBlockedURLs',{urls:['https://*']});
    for (const path of ['/why-malaysia.html','/programmes/levels/foundation.html','/programmes/ar/universities/usm.html','/programmes/zh/universities/usm.html']) {
      await call('Page.navigate',{url:'http://127.0.0.1:9811'+path});
      for(let i=0;i<150;i++){
        if(await evalValue("location.pathname==="+JSON.stringify(path)+" && !!document.querySelector('.ng-footer-grid')")) break;
        await delay(200);
      }
      const foundFooter=await evalValue("location.pathname==="+JSON.stringify(path)+" && !!document.querySelector('.ng-footer-grid')");
      if(!foundFooter){
        const domDebug=await evalValue("JSON.stringify({state:document.readyState,footer:!!document.querySelector('footer')})");
        console.error('Footer diagnostic:',path,domDebug,'Runtime errors:',browserErrors.slice(-8));
      }
      assert(foundFooter,path+' landing-page footer');
      assert(await evalValue("getComputedStyle(document.querySelector('.ng-footer-grid')).gridTemplateColumns.split(' ').length === "+(width===390?1:4)),path+' footer columns');
      assert(await evalValue("getComputedStyle(document.querySelector('#ng-site-footer .ng-footer-grid .ng-footer-link')).overflowWrap === 'normal'"),path+' no letter-by-letter footer links');
      assert(await evalValue("document.querySelector('#ng-site-footer').scrollWidth <= document.querySelector('#ng-site-footer').clientWidth + 3"),path+' no horizontal footer overflow');
      assert(await evalValue("getComputedStyle(document.querySelector('#ng-site-footer .ng-footer-grid nav.grid')).gridTemplateColumns.split(' ').length===1"),path+' one-column quick links, no narrow text columns');
      assert(await evalValue("getComputedStyle(document.body).fontFamily.includes('Montserrat')"),path+' landing-page body font');
      assert(await evalValue("getComputedStyle(document.querySelector('#ng-site-footer')).fontFamily.includes('Montserrat')"),path+' landing-page footer font');
      if(path==='/why-malaysia.html'){
        assert(await evalValue("!!document.querySelector('.ng-why-hero h1') && document.querySelectorAll('.ng-why-page .ng-why-figure img').length >= 20 && [...document.querySelectorAll('.ng-why-page img')].every(img=>img.getAttribute('src').includes('/assets/malaysia/generated/'))"),'Why Malaysia editorial gallery');
        assert(await evalValue("getComputedStyle(document.querySelector('.ng-why-hero h1')).fontFamily.includes('Montserrat')"),'Why Malaysia landing-page typography');
      }
    }
  }
  socket.close();console.log('PASS: '+paths.length+' representative pages at 390px and 1440px vs '+previous);
} finally {
  chrome.kill();for(const s of servers)s.kill();execFileSync('git',['worktree','remove','--force',base]);
}
