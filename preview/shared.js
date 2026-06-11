(function(){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine=matchMedia('(pointer:fine)').matches;
  var V=parseInt(document.body.getAttribute('data-v')||'1',10);

  // ----- selector bar -----
  var NAMES=['Glitch','Orbit','Network','Ticker','Word Storm','3D Deck','Spotlight','Dashboard','Liquid','Comets'];
  var sel=document.createElement('div');sel.className='selector';
  var html='<span class="lbl">Hero concepts</span>';
  for(var i=1;i<=10;i++){var href=(i===1?'/preview/':'/preview/'+i);html+='<a class="'+(i===V?'on':'')+'" href="'+href+'">'+i+' · '+NAMES[i-1]+'</a>';}
  html+='<a class="live" href="/">Live site</a>';
  sel.innerHTML=html;document.body.insertBefore(sel,document.body.firstChild);

  // ----- inject common scaffold into #hero -----
  var hero=document.getElementById('hero');
  if(hero){
    var s='';
    s+='<div class="photo-wrap" id="photo"><img class="photo" src="/tal-paperin.jpg" alt="Tal Paperin, Fractional CRO"></div>';
    s+='<div class="fade"></div>';
    s+='<div class="content" id="content"><div class="inner">';
    s+='<p class="eyebrow"><span class="dot"></span> Fractional CRO · 20+ years · 4 continents</p>';
    s+='<h1 class="name" data-text="Tal Paperin">Tal Paperin</h1>';
    s+='<div class="rotator"><b id="rot">Your sales suck. <span class="accent">I know why.</span></b></div>';
    s+='<p class="sub">I rebuild revenue functions and fix broken B2B sales, fast. 30+ companies rebuilt, $20M ARR managed, deals closed on four continents.</p>';
    s+='<div class="cta"><a class="btn btn-solid magnetic" href="#">Let’s Talk</a><a class="btn btn-outline magnetic" href="#">See the Work</a></div>';
    s+='<div class="stats">';
    s+='<div class="stat"><b data-to="30" data-suffix="+">0</b><span>B2B companies rebuilt</span></div>';
    s+='<div class="stat"><b data-prefix="$" data-to="20" data-suffix="M">0</b><span>ARR managed</span></div>';
    s+='<div class="stat"><b data-to="20" data-suffix="+">0</b><span>years on the number</span></div>';
    s+='<div class="stat"><b data-to="4">0</b><span>continents</span></div>';
    s+='</div></div></div>';
    s+='<div class="scrollcue"><span>Scroll</span><i></i></div>';
    hero.insertAdjacentHTML('beforeend',s);
  }

  // ----- spotlight -----
  var spot=document.createElement('div');spot.className='spot';document.body.appendChild(spot);
  // ----- interactions -----
  var photo=document.getElementById('photo'),content=document.getElementById('content');
  if(!reduce&&fine){
    window.addEventListener('pointermove',function(e){
      spot.style.opacity='1';spot.style.left=e.clientX+'px';spot.style.top=e.clientY+'px';
      var cx=e.clientX/innerWidth-0.5,cy=e.clientY/innerHeight-0.5;
      if(photo&&!document.body.classList.contains('nopar'))photo.style.transform='scale(1.05) translate('+(cx*-20)+'px,'+(cy*-15)+'px)';
      if(content)content.style.transform='translate('+(cx*11)+'px,'+(cy*8)+'px)';
    },{passive:true});
  }

  // rotator
  var lines=['Your sales suck. <span class="accent">I know why.</span>','I rebuild <span class="accent">broken revenue.</span>','I own <span class="accent">the number.</span>','No fluff. <span class="accent">Just revenue.</span>'];
  var rot=document.getElementById('rot'),li=0;
  if(rot&&!reduce){setInterval(function(){
    rot.style.opacity='0';rot.style.transform='translateY(-45%)';
    setTimeout(function(){li=(li+1)%lines.length;rot.innerHTML=lines[li];rot.style.transition='none';rot.style.transform='translateY(45%)';rot.offsetHeight;rot.style.transition='';rot.style.opacity='1';rot.style.transform='translateY(0)';},460);
  },2600);}

  // count-up
  function countUp(el){var to=parseFloat(el.getAttribute('data-to')),pre=el.getAttribute('data-prefix')||'',suf=el.getAttribute('data-suffix')||'';
    if(reduce){el.textContent=pre+to+suf;return;}
    var dur=1200,start=null;function step(t){if(!start)start=t;var p=Math.min((t-start)/dur,1);var v=Math.round(to*(0.5-Math.cos(Math.PI*p)/2));el.textContent=pre+v+suf;if(p<1)requestAnimationFrame(step);}requestAnimationFrame(step);}
  setTimeout(function(){document.querySelectorAll('.stat b').forEach(countUp);},900);

  // magnetic buttons
  if(!reduce&&fine){document.querySelectorAll('.magnetic').forEach(function(b){
    b.addEventListener('pointermove',function(e){var r=b.getBoundingClientRect();b.style.transform='translate('+(e.clientX-r.left-r.width/2)*0.3+'px,'+(e.clientY-r.top-r.height/2)*0.45+'px)';});
    b.addEventListener('pointerleave',function(){b.style.transform='';});
  });}

  window.PV_REDUCE=reduce;window.PV_FINE=fine;
})();
