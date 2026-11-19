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
  let id=0;
  socket.onmessage=({data})=>{const r=JSON.parse(data);if(pending.has(r.id)){pending.get(r.id)(r);pending.delete(r.id)}};
  async function call(method,params={}) {
    const key=++id;const result=new Promise(ok=>pending.set(key,ok));socket.send(JSON.stringify({id:key,method,params}));
    const response=await result;assert(!response.error,JSON.stringify(response.error));return response.result;
  }
  await call('Network.enable');
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
  socket.close();console.log('PASS: '+paths.length+' representative pages at 390px and 1440px vs '+previous);
} finally {
  chrome.kill();for(const s of servers)s.kill();execFileSync('git',['worktree','remove','--force',base]);
}
