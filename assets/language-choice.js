// Keep each public URL stable. Suggest an edition without redirecting a visitor or crawler.
(() => {
  const key = 'nextgenz-language';
  const path = location.pathname;
  const catalogue = path.startsWith('/programmes/');
  const home = path === '/' || path === '/index.html';
  const here = document.documentElement.lang.split('-')[0];
  const normalize = value => (value || '').toLowerCase().split('-')[0];
  function saved() { try { return localStorage.getItem(key); } catch { return null; } }
  function remember(code) { try { localStorage.setItem(key,code); } catch {} }
  document.addEventListener('click',event => {
    const a = event.target.closest('a[lang],a[data-edition]');
    if (a) remember(normalize(a.lang || a.dataset.edition));
  });
  async function findLanguage() {
    if (saved()) return saved();
    for (const language of navigator.languages || [navigator.language]) {
      const base = normalize(language);
      if (base === 'ar' || base === 'zh') return base;
      if (base === 'en') break;
    }
    try {
      const response = await fetch('/api/language-region',{credentials:'omit'});
      if (response.ok) return (await response.json()).language;
    } catch {}
    return null;
  }
  findLanguage().then(lang => {
    if (!['ar','zh','en'].includes(lang) || lang === here) return;
    const alternate = document.querySelector('link[hreflang="'+(lang === 'zh' ? 'zh-Hans' : lang)+'"]') ||
      document.querySelector('link[hreflang="'+(lang === 'zh' ? 'zh-CN' : lang)+'"]');
    const href = alternate?.href || (lang === 'en' ? '/programmes/' : '/programmes/'+lang+'/');
    function render() {
      if (document.querySelector('[data-edition-suggestion]')) return;
      if (home && (location.hash || location.search)) return;
      const box = document.querySelector(home ? '.ng-hero-bottom-actions' : 'main .hero .wrap,main .article');
      if (!box) return;
      const a = document.createElement('a');
      a.dataset.editionSuggestion = ''; a.lang = lang; a.dir = lang === 'ar' ? 'rtl' : 'ltr'; a.href = href;
      a.textContent = lang === 'ar' ? (catalogue || alternate ? 'عرض هذه الصفحة بالعربية' : 'تصفّح التخصصات بالعربية') :
        lang === 'zh' ? (catalogue || alternate ? '查看简体中文版' : '用简体中文浏览专业') : 'View in English';
      a.className = home ? 'text-[#C5A059] hover:text-white' : 'button secondary';
      box.appendChild(a);
    }
    render();
    if (home) {
      const observer = new MutationObserver(render);
      observer.observe(document.getElementById('root') || document.body,{subtree:true,childList:true});
    }
  });
})();
