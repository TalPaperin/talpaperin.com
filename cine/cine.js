/* Cinematic layer: one lit atmosphere behind every page,
   headings that cast light, film-style reveals, and the homepage intro. */
(function(){
  var D=document,html=D.documentElement;html.classList.add('cine');
  var $=function(s){return D.querySelector(s)};
  var QS=new URLSearchParams(location.search);
  var FZ=parseFloat(QS.get('t'));if(isNaN(FZ))FZ=-1;
  var RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine=matchMedia('(pointer:fine)').matches;
  function clamp(v){return v<0?0:v>1?1:v}
  function seg(t,a,b){return clamp((t-a)/(b-a))}
  function lerp(a,b,k){return a+(b-a)*k}
  function eo(k){return 1-Math.pow(1-k,3)}
  function eio(k){return k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2}
  function flick(t){var x=Math.sin(Math.floor(t*26)*91.7)*437.5;return (x-Math.floor(x))>.42?1:.15}
  function mk(tag,cls,id){var e=D.createElement(tag);if(cls)e.className=cls;if(id)e.id=id;e.setAttribute('aria-hidden','true');D.body.appendChild(e);return e}

  // ---------- shared layers ----------
  var glc=$('#gl')||mk('canvas','','gl'),dust=$('#dust')||mk('canvas','','dust');
  if(!$('.fxvig'))mk('div','fxvig');
  var grain=$('#grain')||mk('div','fxgrain','grain');
  (function(){var c=D.createElement('canvas');c.width=c.height=180;var x=c.getContext('2d'),d=x.createImageData(180,180);for(var i=0;i<d.data.length;i+=4){var v=Math.random()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255}x.putImageData(d,0,0);grain.style.backgroundImage='url('+c.toDataURL()+')'})();
  var dctx=dust.getContext('2d');

  // ---------- headings: split into words, they reveal like title cards and cast the light ----------
  function wrapWords(el){
    var tw=D.createTreeWalker(el,NodeFilter.SHOW_TEXT,null),nodes=[],n;while((n=tw.nextNode()))nodes.push(n);
    var i=0;nodes.forEach(function(tn){if(!tn.nodeValue.trim())return;var f=D.createDocumentFragment();
      tn.nodeValue.split(/(\s+)/).forEach(function(p){if(!p)return;if(/^\s+$/.test(p)){f.appendChild(D.createTextNode(p));return}
        var s=D.createElement('span');s.className='w';s.style.transitionDelay=(Math.min(i++,14)*.07).toFixed(2)+'s';s.textContent=p;f.appendChild(s)});
      tn.parentNode.replaceChild(f,tn)});
  }
  var hs=[].slice.call(D.querySelectorAll('main h1,main h2,.section-head h2,.final h2')).filter(function(h){
    return !h.closest('.chero,nav,footer,.post-card,.svc-card,.marquee')&&h.textContent.trim().length>1});
  hs.forEach(function(h){wrapWords(h);h.classList.add('cvh')});
  var maskLW=[];

  // ---------- scroll reveals for page content ----------
  var blocks=[].slice.call(D.querySelectorAll('main .eyebrow,main .glowline,main .lead,main .breadcrumb,main p,main ul,main ol,main figure,main details,main table,main blockquote,main form,main .svc-case,main .cta-box,main .post-card,main .svc-card,main .case-study,main .contact-card,main .channel,main .tier,main .tcard,main .subscribe-box,main .photo-gallery,main .postmeta,main .tagrow,main .quote-calc,main iframe,main .svc-related'))
    .filter(function(e){return !e.closest('.chero,.marquee,.cvh')});
  var set=new Set(blocks);blocks=blocks.filter(function(e){var p=e.parentElement;while(p&&p!==D.body){if(set.has(p))return false;p=p.parentElement}return true});
  if(!RM&&'IntersectionObserver' in window){
    blocks.forEach(function(e){e.classList.add('cv')});
    var first=true,io=new IntersectionObserver(function(es){var k=0;es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target;
        if(first)el.style.transitionDelay=Math.min(.35+k++*.09,1.3).toFixed(2)+'s';
        el.classList.add('cv-in');io.unobserve(el);if(first)setTimeout(function(){el.style.transitionDelay=''},2600)});first=false},{rootMargin:'0px 0px -6% 0px',threshold:.08});
    blocks.forEach(function(e){io.observe(e)});
    var hio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('cv-in');hio.unobserve(e.target)}})},{threshold:.2});
    hs.forEach(function(h){if(h.closest('.chero'))return;if(D.body.classList.contains('cine-home')||!h.matches('main h1'))hio.observe(h);else setTimeout(function(){h.classList.add('cv-in')},450)});
    var sio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('lit');sio.unobserve(e.target)}})},{threshold:.15});
    [].forEach.call(D.querySelectorAll('section.accent-top,section.final,section.logos'),function(s){sio.observe(s)});
  }else{hs.forEach(function(h){h.classList.add('cv-in')});[].forEach.call(D.querySelectorAll('section'),function(s){s.classList.add('lit')})}

  // ---------- homepage intro ----------
  var hero=$('#stage')?$('#main'):null,H={};
  if(hero){
    H={stage:$('#stage'),subj:$('#subj'),sweep:$('#sweep'),scrim:$('#scrim'),flash:$('#flash'),t1:$('#t1'),t3:$('#t3'),shade:$('#tshade'),nav:$('nav.site'),bar:$('#introbar'),
      reveals:[].slice.call(hero.querySelectorAll('[data-at]')),stats:[].slice.call(hero.querySelectorAll('.stats b')),mts:[].slice.call(hero.querySelectorAll('.mt'))};
    H.sweep.style.webkitMaskImage=H.sweep.style.maskImage='url('+H.subj.src+')';
  }
  var AR=1012/1000,DUR=[1.5,2.2,2.2,1.7,1.6],CUTS=[],c0=3.85;DUR.forEach(function(d){CUTS.push(c0);c0+=d+.05});
  var PRE=c0+.35,IMPACT=PRE+.6,MV=IMPACT+2.7;

  // ---------- WebGL: smoke + volumetric light shining through the subject or the heading in view ----------
  var gl=null,U={},q=.5,mc2=D.createElement('canvas'),tex2=null;
  function mkTex(unit,src,flip,wrap){var t=gl.createTexture();gl.activeTexture(gl.TEXTURE0+unit);gl.bindTexture(gl.TEXTURE_2D,t);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,flip);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,src);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,wrap);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,wrap);if(unit===2)tex2=t}
  function initGL(){
    gl=glc.getContext('webgl',{antialias:false,alpha:false});if(!gl)return;
    var NS=innerWidth<=760?40:56;
    var fs=[
    '#ifdef GL_FRAGMENT_PRECISION_HIGH','precision highp float;','#else','precision mediump float;','#endif',
    'uniform vec2 R;uniform float T,LI,SM,SH,A,CORE;uniform vec2 L;uniform vec4 MR,MR2;uniform vec3 LC;uniform sampler2D M,N,M2;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return v;}',
    'float oc(vec2 uv,vec4 r,sampler2D t){vec2 m=(uv-r.xy)/r.zw;if(m.x<0.||m.y<0.||m.x>1.||m.y>1.)return 0.;return texture2D(t,m).a;}',
    'void main(){',
    ' vec2 uv=gl_FragCoord.xy/R;vec2 as=vec2(A,1.);vec2 d=(uv-L)*as;float dist=length(d);',
    ' vec2 st=(uv-L)/'+NS+'.;vec2 s=uv;float ill=0.,dec=1.;',
    ' for(int i=0;i<'+NS+';i++){s-=st;vec2 dd=(s-L)*as;float g=exp(-dot(dd,dd)*16.);float nz=texture2D(N,s*vec2(1.6,.9)+vec2(T*.012,-T*.006)).r;float o=max(oc(s,MR,M),oc(s,MR2,M2));ill+=g*(1.-o)*(.25+1.2*nz*nz)*dec;dec*=.972;}',
    ' ill*=LI*.05*56./'+NS+'.;',
    ' vec2 qq=uv*as*2.;float sm=fbm(qq+vec2(T*.04,T*.015)+.6*fbm(qq*1.4-vec2(T*.025,T*.01)));sm=smoothstep(.3,1.05,sm);',
    ' float lit=exp(-dist*dist*2.2)*LI;',
    ' vec3 c=LC*.022*sm*SM*(.3+1.*lit);',
    ' float r=SH*1.5;c+=mix(LC,vec3(1.),.4)*(SH>0.?exp(-pow((dist-r)*12.,2.))*(1.-SH)*(.4+1.*sm):0.);',
    ' c+=mix(LC,vec3(1.),.1)*ill*(.4+.5*sm);',
    ' c+=mix(LC,vec3(1.),.5)*exp(-dist*dist*70.)*LI*.6*CORE;',
    ' c=1.-exp(-c*1.5);',
    ' c+=(h(gl_FragCoord.xy+T)-.5)/255.;',
    ' gl_FragColor=vec4(c,1.);}'].join('\n');
    function sh(t,src){var o=gl.createShader(t);gl.shaderSource(o,src);gl.compileShader(o);if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(o);return o}
    var pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}'));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fs));gl.linkProgram(pr);gl.useProgram(pr);
    var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
    var loc=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
    ['R','T','LI','SM','SH','A','CORE','L','MR','MR2','LC','M','N','M2'].forEach(function(k){U[k]=gl.getUniformLocation(pr,k)});
    var mc=D.createElement('canvas');mc.width=mc.height=512;if(hero)mc.getContext('2d').drawImage(H.subj,0,0,512,512);
    mkTex(0,mc,true,gl.CLAMP_TO_EDGE);
    var raw=D.createElement('canvas');raw.width=raw.height=64;var rx=raw.getContext('2d'),id=rx.createImageData(64,64);
    for(var i=0;i<id.data.length;i+=4){var v=Math.random()*255;id.data[i]=id.data[i+1]=id.data[i+2]=v;id.data[i+3]=255}rx.putImageData(id,0,0);
    // tile 3x3, blur, keep the centre: the texture wraps with no seam
    var t3=D.createElement('canvas');t3.width=t3.height=768;var tx=t3.getContext('2d');for(var gx=0;gx<3;gx++)for(var gy=0;gy<3;gy++)tx.drawImage(raw,gx*256,gy*256,256,256);
    var tb=D.createElement('canvas');tb.width=tb.height=768;var bx=tb.getContext('2d');bx.filter='blur(3px)';bx.drawImage(t3,0,0);
    var nc=D.createElement('canvas');nc.width=nc.height=256;nc.getContext('2d').drawImage(tb,256,256,256,256,0,0,256,256);
    mkTex(1,nc,false,gl.REPEAT);
    mc2.width=mc2.height=2;mkTex(2,mc2,true,gl.CLAMP_TO_EDGE);
    gl.uniform1i(U.M,0);gl.uniform1i(U.N,1);gl.uniform1i(U.M2,2);
  }
  function drawMask(i){
    var h=hs[i],r=h.getBoundingClientRect(),sc=Math.min(1,1024/Math.max(1,r.width)),x=mc2.getContext('2d');
    mc2.width=Math.max(2,Math.ceil(r.width*sc));mc2.height=Math.max(2,Math.ceil(r.height*sc));
    var cs=getComputedStyle(h),up=cs.textTransform==='uppercase';x.clearRect(0,0,mc2.width,mc2.height);x.fillStyle='#fff';x.textBaseline='middle';
    x.font=cs.fontWeight+' '+(parseFloat(cs.fontSize)*sc)+'px '+cs.fontFamily;
    var lw=0,hr=r;[].forEach.call(h.querySelectorAll('.w'),function(w){var ox=w.offsetLeft-h.offsetLeft,oy=w.offsetTop-h.offsetTop;
      if(w.offsetParent!==h.offsetParent){var wr=w.getBoundingClientRect();ox=wr.left-hr.left;oy=wr.top-hr.top}
      x.fillText(up?w.textContent.toUpperCase():w.textContent,ox*sc,(oy+w.offsetHeight*.54)*sc);lw=Math.max(lw,ox+w.offsetWidth)});
    maskLW[i]=Math.min(lw||r.width,r.width);
    if(gl){gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,tex2);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,mc2)}
  }

  // ---------- dust ----------
  var P=[],sprite,RC='196,226,255',LC=[.45,.68,1.0];
  (function(){var c=D.createElement('canvas');c.width=c.height=64;var x=c.getContext('2d'),g=x.createRadialGradient(32,32,0,32,32,32);
    g.addColorStop(0,'rgba('+RC+',1)');g.addColorStop(.35,'rgba('+RC+',.55)');g.addColorStop(1,'rgba('+RC+',0)');x.fillStyle=g;x.fillRect(0,0,64,64);sprite=c})();

  var W,VH,S,mob,t0=0,mx=0,my=0,tmx=0,tmy=0,last={},lastNow=0,marked=false,cur=-1,pend=-1,fs=0,loadT=performance.now();
  var dpr=Math.min(window.devicePixelRatio||1,1.5);
  function resize(){
    mob=innerWidth<=760;W=D.documentElement.clientWidth;VH=innerHeight;
    glc.width=Math.round(W*q);glc.height=Math.round(VH*q);dust.width=Math.round(W*dpr);dust.height=Math.round(VH*dpr);
    P=[];for(var i=0,n=mob?45:95;i<n;i++)P.push({x:Math.random(),y:Math.random(),z:Math.pow(Math.random(),1.6),vx:(Math.random()-.5)*.00012,vy:-(.00008+Math.random()*.0003),ph:Math.random()*6.3});
    last={};cur=-1;pend=-1;fs=0;
  }
  function geom(t,m,full){
    S=mob?full*(1-.4*m):full;var ih,iw,top,cx;
    if(mob){ih=Math.min(S*.9,W*1.3*AR);top=lerp(S-ih,S*.12,m);iw=ih/AR;cx=W*.5}
    else{ih=S*.95;top=S*.08;iw=ih/AR;cx=lerp(W*.5,Math.max(W*.3,iw*.4),m)}
    var push=(1-m)*.07*eio(seg(t,0,IMPACT))+(1-m)*.06,sc=1+push,w=iw*sc,h=ih*sc;
    return {iw:iw,ih:ih,w:w,h:h,x:cx-w/2,y:top-(sc-1)*ih*.22,cx:cx,sc:sc};
  }
  function title(el,t,a,b){var k=eo(seg(t,a,a+.75)),o=seg(t,b,b+.38);
    el.style.opacity=(k*(1-o)).toFixed(3);el.style.letterSpacing=(lerp(.5,.06,k)+o*.25).toFixed(3)+'em';
    el.style.filter='blur('+((1-k)*14+o*12).toFixed(1)+'px)';el.style.transform='scale('+(1+.035*seg(t,a,b+.4))+')'}

  // hero frame: returns the light it wants this frame
  function heroFrame(t,now,hTop,hHeight){
    var m=eio(seg(t,MV,MV+1.15)),full=mob?VH:hHeight,G=geom(t,m,full);
    if(mob&&Math.abs((last.S||0)-S)>.5){H.stage.style.height=S+'px';last.S=S}
    var LI;
    if(t<.55)LI=0;else if(t<1.5)LI=.9*eo(seg(t,.55,1.5));else if(t<PRE)LI=.9+.07*Math.sin(t*3.1);
    else if(t<IMPACT)LI=.9*(1-seg(t,PRE,PRE+.3))*flick(t);else LI=1+1.6*Math.exp(-(t-IMPACT)*3.2)+.07*Math.sin(t*.8);
    if(t<PRE)CUTS.forEach(function(c){if(t>=c)LI+=.45*Math.exp(-(t-c)*3.5)});
    var SM=seg(t,.1,1.5)*.75+.25*seg(t,IMPACT,IMPACT+1.05),SH=(t>=IMPACT&&t<IMPACT+1.3)?(t-IMPACT)/1.3:0;
    var sk=t>=IMPACT?Math.pow(1-seg(t,IMPACT,IMPACT+.55),2)*16:0,shx=(Math.random()-.5)*sk,shy=(Math.random()-.5)*sk;
    var px=-mx*14,py=-my*8,sx=G.x+px+shx,sy=G.y+py+shy,tr='translate3d('+sx.toFixed(1)+'px,'+sy.toFixed(1)+'px,0) scale('+G.sc.toFixed(4)+')';
    if(last.tr!==tr){[H.subj,H.sweep].forEach(function(e){e.style.width=G.iw+'px';e.style.height=G.ih+'px';e.style.transform=tr});last.tr=tr}
    var br=t<IMPACT?0:(t<IMPACT+.12?lerp(0,1.45,seg(t,IMPACT,IMPACT+.12)):lerp(1.45,1.0,eo(seg(t,IMPACT+.12,IMPACT+.95))));
    var ra=t<IMPACT?.75*Math.min(1,LI+.15):lerp(.9,.22,seg(t,IMPACT,IMPACT+1.25)),rr=t<IMPACT?10:lerp(26,14,seg(t,IMPACT,IMPACT+1.25));
    var f='brightness('+br.toFixed(3)+') contrast(1.28) saturate(1.06) drop-shadow(0 0 '+rr.toFixed(1)+'px rgba('+RC+','+ra.toFixed(3)+'))';
    if(last.f!==f){H.subj.style.filter=f;last.f=f}
    H.sweep.style.opacity=t>IMPACT+.05&&t<IMPACT+1.15?1:0;H.sweep.style.backgroundPosition=(100-100*eio(seg(t,IMPACT+.05,IMPACT+1.05)))+'% 0';
    var lxp=G.x+G.w*.53+px*.5+mx*W*.02,lyp=G.y+G.h*.2+py*.5+my*S*.02;
    var k3=eo(seg(t,IMPACT,IMPACT+.4)),o3=seg(t,IMPACT+2.1,IMPACT+2.55),ca=t>=IMPACT?12*Math.pow(1-seg(t,IMPACT,IMPACT+.45),2):0;
    H.t3.style.opacity=(t<IMPACT?0:k3*(1-o3)).toFixed(3);H.t3.style.filter='blur('+((1-k3)*12+o3*10).toFixed(1)+'px)';
    H.t3.style.transform='scale('+(lerp(1.35,1,k3)*(1+.03*seg(t,IMPACT,IMPACT+2.5))).toFixed(4)+')';
    H.t3.style.textShadow=(ca>.3?(-ca)+'px 0 rgba(255,40,90,.7),'+ca+'px 0 rgba(40,220,255,.7),':'')+'0 0 26px rgba(0,0,0,.9),0 0 50px rgba(0,0,0,.6),0 0 50px rgba(var(--lc),.55)';
    title(H.t1,t,1.0,3.45);
    H.mts.forEach(function(e,i){var a=CUTS[i],d=DUR[i],k=eo(seg(t,a,a+.4)),o=seg(t,a+d-.35,a+d);e.style.opacity=(k*(1-o)).toFixed(3);e.style.filter='blur('+((1-k)*8+o*8).toFixed(1)+'px)';e.style.transform='scale('+(1.06-.06*eo(seg(t,a,a+d))).toFixed(4)+')'});
    H.flash.style.opacity=t>=IMPACT?(.75*Math.exp(-(t-IMPACT)*7)).toFixed(3):0;
    var tsh=Math.max(+H.t1.style.opacity||0,+H.t3.style.opacity||0);H.mts.forEach(function(e){tsh=Math.max(tsh,+e.style.opacity||0)});H.shade.style.opacity=tsh.toFixed(3);
    H.nav.style.opacity=seg(t,MV+.7,MV+1.5).toFixed(3);H.nav.style.pointerEvents=t<MV+.7?'none':'';
    H.scrim.style.opacity=eo(seg(t,MV+.1,MV+1.3)).toFixed(3);
    H.reveals.forEach(function(e){var on=t>=MV+parseFloat(e.getAttribute('data-at'));if(e._on!==on){e._on=on;e.classList.toggle('on',on)}});
    var kk=eio(seg(t,MV+1.4,MV+2.8));H.stats.forEach(function(b){var v=Math.round(parseInt(b.getAttribute('data-v'),10)*kk),s=v>=1000?v.toLocaleString('en-US'):''+v,txt=b.getAttribute('data-f').replace('{}',s);if(b.textContent!==txt)b.textContent=txt});
    var inIntro=t<MV+1.6;if(last.intro!==inIntro){D.body.classList.toggle('intro',inIntro);last.intro=inIntro}
    var showBar=inIntro&&t>.3&&t<MV+.3;if(last.bar!==showBar){H.bar.classList.toggle('hide',!showBar);last.bar=showBar}
    if(!inIntro&&!marked){marked=true;try{sessionStorage.setItem('tp_intro','1')}catch(e){}}
    return {Lx:lxp,Ly:lyp+hTop,LI:LI*.8,SM:SM*.5,SH:SH,mr:[sx/W,1-(sy+hTop+G.h)/VH,G.w/W,G.h/VH],shx:shx,shy:shy,boost:t>=IMPACT&&t<IMPACT+.6};
  }

  function frame(now){
    var dt=Math.min(.05,(now-(lastNow||now))/1000);lastNow=now;
    if(!fine){tmx=Math.sin(now/1000*.35)*.6;tmy=Math.sin(now/1000*.5)*.3}
    mx+=(tmx-mx)*.05;my+=(tmy-my)*.05;
    var rects=hs.map(function(h){return h.getBoundingClientRect()});
    var hv=null,heroVis=0;
    if(hero){var hr=hero.getBoundingClientRect(),t=FZ>=0?FZ:(now-t0)/1000;hv=heroFrame(t,now,hr.top,hr.height);heroVis=clamp(1+hr.top/(hr.height*.6))}
    // the heading nearest the eye line holds the light
    var best=-1,bv=0;rects.forEach(function(r,i){if(!r.height||(hero&&hs[i].closest('.chero')))return;var c=(r.top+r.height/2)/VH,v=1-Math.abs(c-.4)/.5;if(v>bv){bv=v;best=i}});
    if(best!==pend)pend=best;
    if(pend!==cur){fs-=dt*3.5;if(fs<=0){fs=0;cur=pend;if(cur>=0)drawMask(cur)}}
    else{var tg=(cur>=0&&!hs[cur].classList.contains('cv-in'))?0:1;fs+=(tg-fs)*Math.min(1,dt*2.2)}
    var L,LIo,SMo=.45,SHo=0,CORE=.28,mr=[-9,-9,1,1],mr2=[-9,-9,1,1],shx=0,shy=0,open=hero?1:1+1.1*Math.exp(-(now-loadT)/1000*1.3);
    if(hv&&(heroVis>.02||cur<0)){L=[hv.Lx,hv.Ly];LIo=hv.LI*heroVis;SMo=hv.SM;SHo=hv.SH;CORE=1;mr=hv.mr;shx=hv.shx;shy=hv.shy}
    else if(cur>=0){var r=rects[cur],isH1=hs[cur].tagName==='H1',fin=hs[cur].closest('.final');
      var vis=eo(clamp(1-Math.abs((r.top+r.height/2)/VH-.4)/.5));
      L=[r.left+maskLW[cur]*.5,r.top+r.height*(isH1?.4:.2)];LIo=vis*fs*(fin?.85:isH1?.8:.6)*open;mr2=[r.left/W,1-r.bottom/VH,r.width/W,r.height/VH]}
    else{L=[W*.5,-VH*.2];LIo=0}
    if(gl){gl.viewport(0,0,glc.width,glc.height);
      gl.uniform2f(U.R,glc.width,glc.height);gl.uniform1f(U.A,W/VH);
      gl.uniform1f(U.T,now/1000);gl.uniform1f(U.LI,LIo);gl.uniform1f(U.SM,SMo);gl.uniform1f(U.SH,SHo);gl.uniform1f(U.CORE,CORE);
      gl.uniform2f(U.L,L[0]/W,1-L[1]/VH);gl.uniform4f(U.MR,mr[0],mr[1],mr[2],mr[3]);gl.uniform4f(U.MR2,mr2[0],mr2[1],mr2[2],mr2[3]);
      gl.uniform3f(U.LC,LC[0],LC[1],LC[2]);gl.drawArrays(gl.TRIANGLE_STRIP,0,4)}
    // dust drifts through the light, with depth as you scroll
    var dw=dust.width,dh=dust.height,dv=hero?seg(hero&&FZ<0?(now-t0)/1000:9,.6,1.8)*(heroVis>.02?1:.6):.6,sy0=window.scrollY||0;
    dctx.setTransform(1,0,0,1,0,0);dctx.clearRect(0,0,dw,dh);dctx.globalCompositeOperation='lighter';
    var sxs=dw/W,sys=dh/VH,LIc=Math.min(LIo,1.6),boost=hv&&hv.boost;
    for(var i=0;i<P.length;i++){var p=P[i];p.x+=p.vx+Math.sin(now/1000*.4+p.ph)*.00008;p.y+=p.vy*(boost?6:1);
      if(p.y<-.05){p.y=1.05;p.x=Math.random()}if(p.x<-.05)p.x=1.05;if(p.x>1.05)p.x=-.05;
      var X=p.x*W-mx*60*p.z+shx*p.z,Y=((p.y*VH-sy0*.35*p.z)%VH+VH)%VH-my*30*p.z+shy*p.z,ddx=X-L[0],ddy=Y-L[1],lit=Math.exp(-(ddx*ddx+ddy*ddy)/(2*Math.pow(W*.28,2)));
      var size=(2+p.z*p.z*34)*(mob?.7:1),a=(.05+.9*lit*LIc)*(p.z>.75?.28:1)*dv*(.6+.4*Math.sin(now/600+p.ph));
      if(a<.01)continue;dctx.globalAlpha=Math.min(1,a);dctx.drawImage(sprite,(X-size/2)*sxs,(Y-size/2)*sys,size*sxs,size*sys)}
    dctx.globalAlpha=1;
    requestAnimationFrame(frame);
  }

  addEventListener('pointermove',function(e){if(!fine)return;tmx=(e.clientX/innerWidth-.5)*2;tmy=(e.clientY/innerHeight-.5)*2});
  var lw=innerWidth;addEventListener('resize',function(){if(mob&&Math.abs(innerWidth-lw)<2)return;lw=innerWidth;resize()});
  if(hero){
    var skip=function(){var now=performance.now();if((now-t0)/1000<MV)t0=now-MV*1000};
    ['wheel','touchmove'].forEach(function(ev){addEventListener(ev,function(){if((performance.now()-t0)/1000<MV)skip()},{passive:true})});
    addEventListener('keydown',function(e){if(['ArrowDown','PageDown',' ','End'].indexOf(e.key)>=0&&(performance.now()-t0)/1000<MV)skip()});
    $('#skipintro').onclick=skip;
    var rp=$('#replay');if(rp)rp.onclick=function(){try{sessionStorage.removeItem('tp_intro')}catch(e){}marked=false;window.scrollTo(0,0);t0=performance.now()};
  }
  function go(){try{initGL()}catch(e){console.warn(e);gl=null}resize();
    if(hero){var seen=false;try{seen=sessionStorage.getItem('tp_intro')==='1'}catch(e){}var now=performance.now();t0=(seen||RM||window.scrollY>50)?now-(MV+4)*1000:now;marked=seen}
    requestAnimationFrame(frame)}
  var ready=function(){(D.fonts?D.fonts.ready:Promise.resolve()).then(go)};
  if(!hero||(H.subj.complete&&H.subj.naturalWidth))ready();else H.subj.addEventListener('load',ready);
})();
