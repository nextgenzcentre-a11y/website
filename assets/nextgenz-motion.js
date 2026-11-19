// Animate once as public content enters the viewport. Everything is readable before JS runs.
(() => {
  if (!('IntersectionObserver' in window)) return;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const targets = '.ng-home-preview, .ng-market .ng-service-card, main .tile, main .catalog-wide > h2, main .article h2, main .section > .wrap > h2';
  let observer, changes;
  function configure() {
    observer?.disconnect();
    changes?.disconnect();
    if (preference.matches) return;
    const seen = new WeakSet();
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.unobserve(entry.target);
        entry.target.classList.add('ng-enter-view');
      }
    }, {threshold: 0});
    function register(node) {
      if (seen.has(node)) return;
      seen.add(node);
      if (node.getBoundingClientRect().top >= innerHeight) observer.observe(node);
    }
    function scan(node) {
      if (node.nodeType !== Node.ELEMENT_NODE) return;
      if (node.matches(targets)) register(node);
      node.querySelectorAll(targets).forEach(register);
    }
    scan(document.body);
    const root = document.getElementById('root');
    if (root) {
      changes = new MutationObserver(records => {
        for (const record of records) record.addedNodes.forEach(scan);
      });
      changes.observe(root, {childList:true, subtree:true});
    }
  }
  configure();
  preference.addEventListener('change', configure);
})();
