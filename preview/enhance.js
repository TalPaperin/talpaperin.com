/* Premium enhancement layer (visual only). Loads after GSAP/ScrollTrigger/Lenis. */
(function(){
  var RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE=matchMedia('(pointer:fine)').matches;
  var ON_PREVIEW=location.pathname.indexOf('/preview/')===0;

  /* preview ribbon (only on the preview copy) */
  if(ON_PREVIEW){
    var rib=document.createElement('div');rib.id='pvribbon';
    rib.innerHTML='<span class="t">Enhanced preview</span><a href="/">Live site</a>';
    document.body.appendChild(rib);
  }

  /* scroll progress + nav state */
  var prog=document.createElement('div');prog.id='scrollprog';document.body.appendChild(prog);
  var nav=document.querySelector('nav.site');
  function onScroll(){
    var st=window.scrollY||document.documentElement.scrollTop;
    var h=document.documentElement.scrollHeight-innerHeight;
    prog.style.width=(h>0?(st/h*100):0)+'%';
    if(nav)nav.classList.toggle('scrolled',st>40);
  }
  addEventListener('scroll',onScroll,{passive:true});onScroll();

  /* counter that preserves the exact existing text (prefix, digits, suffix, commas) */
  function animateCount(el){
    var txt=el.textContent.trim();
    var m=txt.match(/^([^\d]*)([\d,]+)(.*)$/);
    if(!m){return;}
    var pre=m[1],raw=m[2],suf=m[3],to=parseInt(raw.replace(/,/g,''),10);
    if(!to){return;}
    var comma=raw.indexOf(',')>=0;
    function fmt(n){return comma?n.toLocaleString('en-US'):(''+n);}
    if(RM){el.textContent=txt;return;}
    var dur=1500,start=null;
    function step(t){if(!start)start=t;var p=Math.min((t-start)/dur,1);
      var v=Math.round(to*(0.5-Math.cos(Math.PI*p)/2));
      el.textContent=pre+fmt(v)+suf;
      if(p<1)requestAnimationFrame(step);else{el.classList.add('counted');}
    }
    requestAnimationFrame(step);
  }

  /* 3D tilt + cursor sheen for the engagement / product cards */
  function addTilt(el,max){
    if(!FINE||RM)return;el.classList.add('tilt');
    el.addEventListener('pointermove',function(e){
      var r=el.getBoundingClientRect();var px=(e.clientX-r.left)/r.width-.5,py=(e.clientY-r.top)/r.height-.5;
      el.style.setProperty('--mx',((px+.5)*100)+'%');el.style.setProperty('--my',((py+.5)*100)+'%');
      el.style.transform='perspective(950px) rotateY('+(px*(max||6))+'deg) rotateX('+(-py*(max||6))+'deg) translateY(-6px)';
    });
    el.addEventListener('pointerleave',function(){el.style.transform='';});
  }

  /* decorative ascending revenue chart inside the final CTA section */
  function injectDeco(){
    var final=document.querySelector('.final');if(!final||final.querySelector('.deco-chart'))return;
    var svg='<svg class="deco-chart" viewBox="0 0 100 60" preserveAspectRatio="none" aria-hidden="true">'+
      '<defs><linearGradient id="dcg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1f6fb2"/><stop offset="1" stop-color="#5ab0ff"/></linearGradient>'+
      '<linearGradient id="dca" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(90,176,255,.22)"/><stop offset="1" stop-color="rgba(90,176,255,0)"/></linearGradient></defs>'+
      '<polygon class="ar" points="0,56 14,50 28,52 42,40 56,44 70,30 84,20 100,8 100,60 0,60"/>'+
      '<polyline class="ln" points="0,56 14,50 28,52 42,40 56,44 70,30 84,20 100,8"/>'+
      '<circle class="tip" cx="100" cy="8" r="1.6"/></svg>';
    final.insertAdjacentHTML('afterbegin',svg);
  }

  /* Lenis smooth scrolling (desktop, motion-allowed), anchor-safe */
  var lenis=null;
  function initLenis(){
    if(RM||!window.Lenis)return;
    lenis=new Lenis({duration:1.1,smoothWheel:true,smoothTouch:false});
    function raf(t){lenis.raf(t);requestAnimationFrame(raf);}requestAnimationFrame(raf);
    if(window.ScrollTrigger)lenis.on('scroll',ScrollTrigger.update);
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
      a.addEventListener('click',function(e){var id=a.getAttribute('href');if(id.length>1){var t=document.querySelector(id);if(t){e.preventDefault();lenis.scrollTo(t,{offset:-72});}}});
    });
  }

  function gsapStuff(){
    if(!(window.gsap&&window.ScrollTrigger)){
      /* fallback counters via IntersectionObserver */
      var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){animateCount(e.target);io.unobserve(e.target);}});},{threshold:.6});
      document.querySelectorAll('.hero .stats b').forEach(function(b){io.observe(b);});
      return;
    }
    gsap.registerPlugin(ScrollTrigger);

    if(!RM){
      var htext=document.querySelector('.hero .text');
      if(htext)gsap.to(htext,{yPercent:-7,ease:'none',scrollTrigger:{trigger:'.hero',start:'top top',end:'bottom top',scrub:true}});
    }

    /* counters on enter */
    document.querySelectorAll('.hero .stats b').forEach(function(b){
      ScrollTrigger.create({trigger:b,start:'top 92%',once:true,onEnter:function(){animateCount(b);}});
    });

    /* decorative chart draws itself when the final CTA arrives */
    var ln=document.querySelector('.deco-chart .ln'),tip=document.querySelector('.deco-chart .tip');
    if(ln&&!RM){var len=ln.getTotalLength();ln.style.strokeDasharray=len;ln.style.strokeDashoffset=len;if(tip)tip.style.opacity=0;
      ScrollTrigger.create({trigger:'.final',start:'top 78%',once:true,onEnter:function(){
        gsap.to(ln,{strokeDashoffset:0,duration:1.7,ease:'power2.out'});
        if(tip)gsap.to(tip,{opacity:1,duration:.4,delay:1.5});
      }});
    }
    setTimeout(function(){ScrollTrigger.refresh();},300);
  }

  function start(){
    injectDeco();
    initLenis();
    gsapStuff();
    document.querySelectorAll('.card3').forEach(function(c){addTilt(c,6);});
  }
  if(document.readyState!=='loading')start();else addEventListener('DOMContentLoaded',start);
})();
