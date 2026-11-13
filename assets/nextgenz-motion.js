(function(){
  "use strict";
  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var observer = new IntersectionObserver(function(entries){
    entries.forEach(function(entry) {
      if(entry.isIntersecting){entry.target.classList.add("ng-visible");observer.unobserve(entry.target);}
    });
  },{threshold:0.08,rootMargin:"0px 0px 40px 0px"});
  function scan(){
    document.querySelectorAll(".ng-reveal:not([data-ng-reveal-bound])").forEach(function(el){
      el.setAttribute("data-ng-reveal-bound","1");
      if(el.getBoundingClientRect().top < window.innerHeight*0.98){el.classList.add("ng-visible");}
      el.classList.add("ng-motion-enabled");
      observer.observe(el);
    });
  }
  var scheduled=false;
  function scheduleScan(){if(scheduled)return;scheduled=true;requestAnimationFrame(function(){scheduled=false;scan();});}
  document.addEventListener("DOMContentLoaded",function(){
    scan();
    var target=document.getElementById("root");
    if(target){new MutationObserver(scheduleScan).observe(target,{childList:true,subtree:true});}
  });
})();