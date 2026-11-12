#!/usr/bin/env python3
"""
Static blog generator for talpaperin.com.

Reads Markdown posts from blog/posts/*.md (each with a small front matter
header) and writes fully static, SEO-optimized HTML:

  blog/<slug>.html   one page per post (meta tags + BlogPosting JSON-LD)
  blog/index.html    the listing page
  blog/rss.xml       RSS 2.0 feed
  sitemap.xml        rebuilt to include the homepage, /he/, the blog, and posts

No server-side build runs on Vercel. Run this locally, then commit the output:

  python3 blog/build.py

Front matter format (between the two --- lines at the top of each .md file):

  ---
  title: Your Post Title
  description: One-sentence meta description for search and social.
  date: 2026-06-10
  tags: B2B Sales, Fractional CRO
  image: /og-image.jpg        (optional, absolute path on the site)
  updated: 2026-06-12         (optional, defaults to date)
  ---
  Markdown body starts here. Use ## for section headings.
"""

import os
import re
import html
import datetime
import importlib.util

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blog")
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
POSTS_DIR_HE = os.path.join(BLOG_DIR, "posts-he")
HE_BLOG_DIR = os.path.join(ROOT, "he", "blog")
SITE = "https://talpaperin.com"

# Service pages are defined in services/build.py; pull them in for sitemap + llms.
_svc_spec = importlib.util.spec_from_file_location(
    "svcbuild", os.path.join(ROOT, "services", "build.py"))
_svc_mod = importlib.util.module_from_spec(_svc_spec)
_svc_spec.loader.exec_module(_svc_mod)
SERVICES = _svc_mod.SERVICES
GUIDES = _svc_mod.GUIDES
HE_GUIDES = _svc_mod.HE_GUIDES

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTHS_HE = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי",
             "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
RFC822_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
RFC822_MONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]

ANALYTICS = ('<!-- Google tag (gtag.js): the library is loaded after the page, or on first interaction, so it never blocks rendering -->\n'
             '  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
             "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'granted'});gtag('consent','default',{analytics_storage:'denied',region:['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH'],wait_for_update:500});try{var tpc=localStorage.getItem('tp_consent');if(tpc)gtag('consent','update',{analytics_storage:tpc==='yes'?'granted':'denied'});}catch(e){}gtag('js',new Date());gtag('config','G-GG3XFQTX11');(function(){var d=0;function l(){if(d)return;d=1;var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id=G-GG3XFQTX11';document.head.appendChild(s);}if(document.readyState==='complete')setTimeout(l,1);else addEventListener('load',function(){setTimeout(l,1);});['pointerdown','keydown','touchstart','scroll'].forEach(function(e){addEventListener(e,l,{once:true,passive:true});});})();</script>\n"
             '  <script src="https://analytics.ahrefs.com/analytics.js" '
             'data-key="yw4L2JvlOTPBX9ieFq8jZg" async></script>\n'
             '  <script src="/site.js?v=14" defer></script>')

# Fonts are served from /fonts (no request to Google). Faces are inlined so text paints
# without waiting for a stylesheet; the two used above the fold are preloaded.
FONT_FACES_EN = "@font-face{font-family:'Anton';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/anton-latin-ext.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}@font-face{font-family:'Anton';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/anton-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}@font-face{font-family:'Space Grotesk';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/spacegrotesk-latin-ext.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}@font-face{font-family:'Space Grotesk';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/spacegrotesk-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}"
FONTS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml" />\n'
         '  <link rel="icon" href="/favicon.ico" sizes="any" />\n'
         '  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n'
         '  <link rel="preload" href="/fonts/anton-latin.woff2" as="font" type="font/woff2" crossorigin />\n'
         '  <link rel="preload" href="/fonts/spacegrotesk-latin.woff2" as="font" type="font/woff2" crossorigin />\n'
         '  <style>' + FONT_FACES_EN + '</style>\n'
         '  <link rel="stylesheet" href="/site.css?v=14" />')

FLAG_SVG = ('<svg width="31" height="21" viewBox="0 0 22 15" aria-hidden="true">'
            '<rect width="22" height="15" fill="#fff"/>'
            '<rect width="22" height="1.7" y="2.3" fill="#0038b8"/>'
            '<rect width="22" height="1.7" y="11" fill="#0038b8"/>'
            '<path d="M11 4.5 L8.4 9 L13.6 9 Z" fill="none" stroke="#0038b8" stroke-width=".7"/>'
            '<path d="M11 10.5 L8.4 6 L13.6 6 Z" fill="none" stroke="#0038b8" stroke-width=".7"/></svg>')

FLAG_US = ('<svg width="31" height="21" viewBox="0 0 22 15" aria-hidden="true">'
           '<rect width="22" height="15" fill="#b22234"/>'
           '<g fill="#fff"><rect width="22" height="1.15" y="1.15"/><rect width="22" height="1.15" y="3.46"/>'
           '<rect width="22" height="1.15" y="5.77"/><rect width="22" height="1.15" y="8.08"/>'
           '<rect width="22" height="1.15" y="10.38"/><rect width="22" height="1.15" y="12.69"/></g>'
           '<rect width="9" height="8.08" fill="#3c3b6e"/></svg>')

HAMBURGER = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" '
             'stroke-linecap="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/>'
             '<line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>')

WA_SVG = ('<svg viewBox="0 0 32 32" fill="#fff" aria-hidden="true"><path d="M16 .4C7.4.4.4 '
          '7.4.4 16c0 2.8.7 5.5 2.1 7.9L.3 31.6l7.9-2.1c2.3 1.3 4.9 1.9 7.6 1.9 8.6 0 '
          '15.6-7 15.6-15.6C31.6 7.4 24.6.4 16 .4zm0 28.5c-2.4 0-4.7-.6-6.7-1.8l-.5-.3-4.7 '
          '1.2 1.3-4.6-.3-.5c-1.3-2.1-2-4.5-2-6.9C3.3 9 8.9 3.3 16 3.3c3.4 0 6.6 1.3 9 '
          '3.7 2.4 2.4 3.7 5.6 3.7 9 0 7.1-5.7 12.9-12.7 12.9zm7-9.6c-.4-.2-2.3-1.1-2.6-1.3-.4-.1-.6-.2-.9.2-.3.4-1 '
          '1.3-1.2 1.5-.2.2-.4.3-.8.1-.4-.2-1.6-.6-3.1-1.9-1.1-1-1.9-2.3-2.1-2.7-.2-.4 0-.6.2-.8.2-.2.4-.4.5-.7.2-.2.2-.4.4-.6.1-.3.1-.5 '
          '0-.7-.1-.2-.9-2.2-1.3-3-.3-.7-.6-.6-.9-.7h-.8c-.3 0-.7.1-1 .5-.4.4-1.4 1.3-1.4 '
          '3.3 0 1.9 1.4 3.8 1.6 4.1.2.3 2.8 4.3 6.8 6 1 .4 1.7.7 2.3.9 1 .3 1.8.3 '
          '2.5.2.8-.1 2.3-.9 2.6-1.9.3-.9.3-1.7.2-1.9-.1-.1-.4-.2-.8-.4z"/></svg>')

NAV = '''  <a class="skip-link" href="#main">Skip to content</a>
  <nav class="site">
    <div class="inner">
      <a class="brand" href="/">TAL PAPERIN</a>
      <div class="navlinks">
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/services">Services</a>
        <a href="/pricing">Pricing</a>
        <a href="/case-studies">Case Studies</a>
        <a href="/recommendations">Recommendations</a>
        <a href="/blog">Blog</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/he" hreflang="he" aria-label="Switch to Hebrew">''' + FLAG_SVG + '''</a>
        <a class="btn btn-primary" href="/contact">Let's Talk</a>
        <button class="navtoggle" aria-label="Menu" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

FOOTER = '''  <footer>
    <div class="wrap foot-grid">
      <div class="foot-col">
        <p class="foot-h">Services</p>
        <ul>
          <li><a href="/services/fractional-cro">Fractional CRO</a></li>
          <li><a href="/services/outsourced-sales">Outsourced Sales Teams</a></li>
          <li><a href="/services/pay-per-meeting">Pay-Per-Meeting</a></li>
          <li><a href="/services/go-to-market-strategy">Go-To-Market Strategy</a></li>
          <li><a href="/services/market-entry">Market Entry</a></li>
          <li><a href="/services">All services</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">Decide</p>
        <ul>
          <li><a href="/pricing">Pricing</a></li>
          <li><a href="/case-studies">Case Studies</a></li>
          <li><a href="/recommendations">Recommendations</a></li>
          <li><a href="/sales-cost-calculator">Sales cost calculator</a></li>
          <li><a href="/about">About Tal</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">Learn</p>
        <ul>
          <li><a href="/guides">Guides</a></li>
          <li><a href="/answers">Answers</a></li>
          <li><a href="/blog">Blog</a></li>
          <li><a href="/when-do-you-need-a-fractional-cro">When you need a fractional CRO</a></li>
          <li><a href="/fractional-cro-cost">What a fractional CRO costs</a></li>
          <li><a href="/fractional-vp-of-sales">Fractional VP of Sales</a></li>
          <li><a href="/fractional-cro-for-saas">Fractional CRO for B2B SaaS</a></li>
          <li><a href="/fractional-vp-sales-vs-full-time-vp-sales">Fractional vs full-time VP of Sales</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">Contact</p>
        <ul>
          <li><a href="/contact">Send a message</a></li>
          <li><a href="mailto:tal@ksw.solutions">tal@ksw.solutions</a></li>
          <li><a href="tel:+972545308119" dir="ltr">+972 54-530-8119</a></li>
          <li><a href="https://wa.me/972545308119" target="_blank" rel="noopener">WhatsApp</a></li>
          <li><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">LinkedIn</a></li>
        </ul>
      </div>
    </div>
    <div class="wrap inner">
      <span class="foot-legal">&copy; 2017-2026 Tal Paperin. All rights reserved. Tal Paperin operates through his company, <a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>. &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="Email Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="Call Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="Tal Paperin on LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
    function subSubmit(e){e.preventDefault();var f=e.target,b=f.querySelector('button'),m=f.parentNode.querySelector('.sub-msg');b.disabled=true;b.textContent='...';fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value})}).then(function(r){return r.json();}).then(function(d){if(d&&d.ok){f.style.display='none';m.hidden=false;m.style.color='var(--blue)';m.textContent='You are in. Welcome aboard.';}else{b.disabled=false;b.textContent='Subscribe';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please try again.';}}).catch(function(){b.disabled=false;b.textContent='Subscribe';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please try again.';});return false;}
  </script>'''

CTA_BOX = '''      <div class="cta-box">
        <h3>Your sales suck. You don't know why. I do.</h3>
        <p>A 15-minute call, no pitch. You will leave with at least one concrete thing to fix, whether or not we work together.</p>
        <a class="btn btn-primary" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">Book a 15-Minute Call</a>
      </div>'''

INLINE_CTA = ('<div class="inline-cta"><p><strong>This is exactly what I fix, '
              'hands-on.</strong> Monthly, no contract, no exit fines. If revenue is '
              'stuck, tell me where.</p>'
              '<a class="btn btn-secondary" href="/contact" data-cta="blog-mid">'
              "Let's Talk</a></div>")

HE_INLINE_CTA = ('<div class="inline-cta"><p><strong>זה בדיוק מה שאני מתקן, '
                 'בידיים.</strong> חודשי, בלי חוזה, בלי קנסות יציאה. אם ההכנסות תקועות, '
                 'ספרו לי איפה.</p>'
                 '<a class="btn btn-secondary" href="/he/contact" data-cta="blog-mid">'
                 'בואו נדבר</a></div>')


SUBSCRIBE = '''      <div class="subscribe-box">
        <h3>Get these in your inbox</h3>
        <p>No fluff. Sales, revenue and go-to-market, straight from the field.</p>
        <form class="sub-form" onsubmit="return subSubmit(event)">
          <input type="email" name="email" placeholder="Your email" required autocomplete="email" />
          <button class="btn btn-primary" type="submit">Subscribe</button>
        </form>
        <p class="sub-msg" hidden></p>
      </div>'''


# --- Hebrew (RTL) building blocks ------------------------------------------

# Fonts are served from /fonts (no request to Google). Faces are inlined so text paints
# without waiting for a stylesheet; the two used above the fold are preloaded.
FONT_FACES_HE = "@font-face{font-family:'Heebo';font-style:normal;font-weight:400 900;font-display:swap;src:url(/fonts/heebo-hebrew.woff2) format('woff2');unicode-range:U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F}@font-face{font-family:'Heebo';font-style:normal;font-weight:400 900;font-display:swap;src:url(/fonts/heebo-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}@font-face{font-family:'Rubik';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/rubik-hebrew.woff2) format('woff2');unicode-range:U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F}@font-face{font-family:'Rubik';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/rubik-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}"
HE_FONTS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml" />\n'
            '  <link rel="icon" href="/favicon.ico" sizes="any" />\n'
            '  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n'
            '  <link rel="preload" href="/fonts/heebo-hebrew.woff2" as="font" type="font/woff2" crossorigin />\n'
            '  <link rel="preload" href="/fonts/rubik-hebrew.woff2" as="font" type="font/woff2" crossorigin />\n'
            '  <style>' + FONT_FACES_HE + '</style>\n'
            '  <link rel="stylesheet" href="/site.css?v=14" />')

HE_NAV = '''  <a class="skip-link" href="#main">Skip to content</a>
  <nav class="site">
    <div class="inner">
      <a class="brand" href="/he">טל פאפרין</a>
      <div class="navlinks">
        <a href="/he">בית</a>
        <a href="/he/about">אודות</a>
        <a href="/he/services">שירותים</a>
        <a href="/he/pricing">תמחור</a>
        <a href="/he/case-studies">מקרי מבחן</a>
        <a href="/he/recommendations">המלצות</a>
        <a href="/he/blog">בלוג</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/" hreflang="en" aria-label="Switch to English">''' + FLAG_US + '''</a>
        <a class="btn btn-primary" href="/he/contact">בואו נדבר</a>
        <button class="navtoggle" aria-label="תפריט" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

HE_FOOTER = '''  <footer>
    <div class="wrap foot-grid">
      <div class="foot-col">
        <p class="foot-h">שירותים</p>
        <ul>
          <li><a href="/he/services/fractional-cro">סמנכ״ל מכירות במיקור חוץ</a></li>
          <li><a href="/he/services/outsourced-sales">צוות מכירות במיקור חוץ</a></li>
          <li><a href="/he/services/pay-per-meeting">תשלום לפי פגישה</a></li>
          <li><a href="/he/services/go-to-market-strategy">אסטרטגיית Go-To-Market</a></li>
          <li><a href="/he/services/market-entry">חדירה לשווקים בינלאומיים</a></li>
          <li><a href="/he/services">כל השירותים</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">לפני שמחליטים</p>
        <ul>
          <li><a href="/he/pricing">תמחור</a></li>
          <li><a href="/he/case-studies">מקרי מבחן</a></li>
          <li><a href="/he/recommendations">המלצות</a></li>
          <li><a href="/he/sales-cost-calculator">מחשבון עלות המכירות</a></li>
          <li><a href="/he/about">אודות טל</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">מדריכים ותוכן</p>
        <ul>
          <li><a href="/he/guides">מדריכים</a></li>
          <li><a href="/he/answers">תשובות</a></li>
          <li><a href="/he/blog">בלוג</a></li>
          <li><a href="/he/when-do-you-need-a-fractional-cro">מתי צריך Fractional CRO?</a></li>
          <li><a href="/he/fractional-cro-cost">כמה עולה סמנכ״ל במיקור חוץ</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <p class="foot-h">יצירת קשר</p>
        <ul>
          <li><a href="/he/contact">שליחת הודעה</a></li>
          <li><a href="mailto:tal@ksw.solutions">tal@ksw.solutions</a></li>
          <li><a href="tel:+972545308119" dir="ltr">+972 54-530-8119</a></li>
          <li><a href="https://wa.me/972545308119" target="_blank" rel="noopener">וואטסאפ</a></li>
          <li><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">לינקדאין</a></li>
        </ul>
      </div>
    </div>
    <div class="wrap inner">
      <span class="foot-legal">&copy; 2017-2026 טל פאפרין. כל הזכויות שמורות. טל פאפרין פועל באמצעות החברה שלו, <a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>. &middot; <a href="/he/privacy">פרטיות</a> &middot; <a href="/he/terms">תנאי שימוש</a></span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="אימייל"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="טלפון"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="לינקדאין"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="שיחה בוואטסאפ">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
    function subSubmit(e){e.preventDefault();var f=e.target,b=f.querySelector('button'),m=f.parentNode.querySelector('.sub-msg');b.disabled=true;b.textContent='...';fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value})}).then(function(r){return r.json();}).then(function(d){if(d&&d.ok){f.style.display='none';m.hidden=false;m.style.color='var(--blue)';m.textContent='נרשמת. ברוכים הבאים!';}else{b.disabled=false;b.textContent='הרשמה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. נסו שוב.';}}).catch(function(){b.disabled=false;b.textContent='הרשמה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. נסו שוב.';});return false;}
  </script>'''

HE_CTA_BOX = '''      <div class="cta-box">
        <h3>המכירות שלכם תקועות. אתם לא יודעים למה. אני כן.</h3>
        <p>שיחה של 15 דקות, בלי פיץ'. תצאו ממנה עם לפחות דבר אחד קונקרטי לתקן, בין אם נעבוד יחד ובין אם לא.</p>
        <a class="btn btn-primary" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">לתיאום שיחה של 15 דקות</a>
      </div>'''

HE_SUBSCRIBE = '''      <div class="subscribe-box">
        <h3>קבלו את אלה למייל</h3>
        <p>בלי בולשיט. מכירות, הכנסות ו-Go-to-Market, ישר מהשטח.</p>
        <form class="sub-form" onsubmit="return subSubmit(event)">
          <input type="email" name="email" placeholder="המייל שלכם" required autocomplete="email" />
          <button class="btn btn-primary" type="submit">הרשמה</button>
        </form>
        <p class="sub-msg" hidden></p>
      </div>'''


def parse_front_matter(raw):
    """Split a .md file into (meta dict, markdown body)."""
    if not raw.startswith("---"):
        raise ValueError("missing front matter")
    parts = raw.split("---", 2)
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[k.strip().lower()] = v
    return meta, parts[2].strip()


def parse_date(s):
    return datetime.date(*[int(x) for x in s.split("-")])


def human_date(d, lang="en"):
    if lang == "he":
        return "%d ב%s %d" % (d.day, MONTHS_HE[d.month - 1], d.year)
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def rfc822(d):
    wd = RFC822_DAYS[d.weekday()]
    return "%s, %02d %s %d 00:00:00 +0000" % (wd, d.day, RFC822_MONS[d.month - 1], d.year)


def reading_time(text):
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 200))


def esc(s):
    return html.escape(s, quote=True)


def load_posts(directory=POSTS_DIR, lang="en"):
    posts = []
    if not os.path.isdir(directory):
        return posts
    for fn in os.listdir(directory):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(directory, fn), encoding="utf-8") as f:
            raw = f.read()
        meta, body_md = parse_front_matter(raw)
        slug = meta.get("slug") or re.sub(r"\.md$", "", fn)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
        date = parse_date(meta["date"])
        # Scheduled publishing: a post dated in the future stays hidden (out of the
        # index, RSS, sitemap and hreflang) until its date arrives. Set BUILD_FUTURE=1
        # to preview future-dated posts locally.
        if date > datetime.date.today() and os.environ.get("BUILD_FUTURE") != "1":
            continue
        updated = parse_date(meta["updated"]) if meta.get("updated") else date
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        md = markdown.Markdown(extensions=["extra", "sane_lists", "toc"])
        body_html = md.convert(body_md)
        posts.append({
            "slug": slug,
            "lang": lang,
            "title": meta["title"],
            # Optional SEO-optimized <title> tag; falls back to the H1 title.
            "seotitle": meta.get("seotitle", "").strip(),
            "description": meta["description"],
            "date": date,
            "updated": updated,
            "tags": tags,
            "image": meta.get("image", "/og-image.jpg"),
            # "alt" names the slug of the same post in the other language, if any.
            "alt": meta.get("alt", "").strip(),
            # "noindex: true" keeps a thin post readable and linked, but out of search
            # engines, the sitemap and llms.txt.
            "noindex": meta.get("noindex", "").strip().lower() in ("true", "yes", "1"),
            "body_html": body_html,
            "read": reading_time(body_md),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def insert_inline_cta(body_html, cta):
    """Drop a compact CTA roughly halfway through the article (after a </p>)."""
    parts = body_html.split("</p>")
    if len(parts) < 6:  # short post: bottom CTA is enough
        return body_html
    mid = len(parts) // 2
    parts[mid] = cta + parts[mid]
    return "</p>".join(parts)


def hreflang_block(slug, alt, lang):
    """Build the <link rel=alternate hreflang> tags for a post with a counterpart."""
    if not alt:
        return ""
    en = "%s/blog/%s" % (SITE, alt if lang == "he" else slug)
    he = "%s/he/blog/%s" % (SITE, slug if lang == "he" else alt)
    return ('  <link rel="alternate" hreflang="en" href="%s" />\n'
            '  <link rel="alternate" hreflang="he" href="%s" />\n'
            '  <link rel="alternate" hreflang="x-default" href="%s" />' % (en, he, en))


def render_post(p):
    he = p["lang"] == "he"
    base = "/he/blog/" if he else "/blog/"
    url = "%s%s%s" % (SITE, base, p["slug"])
    img = p["image"] if p["image"].startswith("http") else SITE + p["image"]
    tags_meta = "\n".join(
        '  <meta property="article:tag" content="%s" />' % esc(t) for t in p["tags"])
    keywords = ", ".join(p["tags"])
    tagrow = ""
    if p["tags"]:
        def _tag(t):
            slug = TAG_TOPIC[p["lang"]].get(t.lower())
            if slug and slug in p.get("live_topics", ()):
                return '<a class="tag" href="%s">%s</a>' % (topic_url(p["lang"], slug), esc(t))
            return '<span class="tag">%s</span>' % esc(t)
        tagrow = '<div class="tagrow">' + "".join(_tag(t) for t in p["tags"]) + "</div>"

    author = "טל פאפרין" if he else "Tal Paperin"
    home_name = "בית" if he else "Home"
    blog_name = "בלוג" if he else "Blog"

    ld = (
        '{"@context":"https://schema.org","@type":"BlogPosting",'
        '"mainEntityOfPage":{"@type":"WebPage","@id":"%s"},'
        '"headline":"%s","description":"%s","image":"%s",'
        '"datePublished":"%s","dateModified":"%s","inLanguage":"%s",'
        '"author":{"@id":"%s/#tal"},'
        '"publisher":{"@id":"%s/#business"},'
        '"keywords":"%s"}'
    ) % (url, esc(p["title"]), esc(p["description"]), img,
         p["date"].isoformat(), p["updated"].isoformat(), "he" if he else "en",
         SITE, SITE, esc(keywords))

    crumb = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"%s","item":"%s%s"},'
        '{"@type":"ListItem","position":2,"name":"%s","item":"%s%s"},'
        '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
    ) % (home_name, SITE, "/he" if he else "/", blog_name, SITE, base.rstrip("/"),
         esc(p["title"]), url)

    body = insert_inline_cta(p["body_html"], HE_INLINE_CTA if he else INLINE_CTA)

    template = TEMPLATE_POST_HE if he else TEMPLATE_POST
    return template \
        .replace("{{METATITLE}}", esc(p["seotitle"] or p["title"])) \
        .replace("{{ROBOTS}}", "noindex, follow" if p.get("noindex") else "index, follow") \
        .replace("{{TITLE}}", esc(p["title"])) \
        .replace("{{DESC}}", esc(p["description"])) \
        .replace("{{URL}}", url) \
        .replace("{{IMG}}", img) \
        .replace("{{KEYWORDS}}", esc(keywords)) \
        .replace("{{PUBLISHED}}", p["date"].isoformat()) \
        .replace("{{MODIFIED}}", p["updated"].isoformat()) \
        .replace("{{ARTICLE_TAGS}}", tags_meta) \
        .replace("{{HREFLANG}}", hreflang_block(p["slug"], p["alt"], p["lang"])) \
        .replace("{{LD}}", ld) \
        .replace("{{CRUMB}}", crumb) \
        .replace("{{HUMAN_DATE}}", human_date(p["date"], p["lang"])) \
        .replace("{{READ}}", str(p["read"])) \
        .replace("{{TAGROW}}", tagrow) \
        .replace("{{BODY}}", body) \
        .replace("{{NAV}}", HE_NAV if he else NAV) \
        .replace("{{FOOTER}}", (_svc_mod.BIO_HE + HE_FOOTER) if he else (_svc_mod.BIO_EN + FOOTER)) \
        .replace("{{SUBSCRIBE}}", HE_SUBSCRIBE if he else SUBSCRIBE) \
        .replace("{{CTA}}", HE_CTA_BOX if he else CTA_BOX) \
        .replace("{{FONTS}}", HE_FONTS if he else FONTS) \
        .replace("{{ANALYTICS}}", ANALYTICS + "\n\n  " + _svc_mod.graph_ld(he))


# --- Listing pages: 20 posts per page, plus topic pages built from the tags ------------
PER_PAGE = 20
# (slug, English label, Hebrew label, English tags, Hebrew tags). A post belongs to every
# topic one of its tags maps to. A topic page is only built when it has at least MIN_TOPIC posts.
MIN_TOPIC = 5
TOPICS = [
    ("b2b-sales", "B2B Sales", "מכירות B2B",
     ["B2B Sales", "Sales Strategy", "Negotiation"], ["מכירות B2B", "אסטרטגיית מכירות"]),
    ("revenue-leadership", "Revenue Leadership", "מנהיגות הכנסות",
     ["Revenue Leadership", "Fractional CRO", "Sales Leadership", "Sales Management", "Revenue", "Revenue Growth"],
     ["מנהיגות הכנסות", "Fractional CRO", "ניהול מכירות", "צמיחת הכנסות", "סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ"]),
    ("go-to-market", "Go-To-Market", "Go-To-Market",
     ["Go-To-Market", "Marketing", "Business Model", "Pricing"], ["Go-To-Market", "אסטרטגיית Go-To-Market"]),
    ("market-entry", "Market Entry", "חדירה לשוק",
     ["Market Entry", "International Sales", "Expansion", "Israel"],
     ["חדירה לשוק", "כניסה לשוק", "מכירות בינלאומיות", "ישראל"]),
    ("sales-teams", "Sales Teams", "צוותי מכירות",
     ["Sales Team", "Hiring & Teams", "Hiring", "Scaling Sales"], ["צוות מכירות", "גיוס וצוותים"]),
    ("startups", "Startups", "סטארטאפים", ["Startups"], ["סטארטאפים"]),
    ("pipeline", "Pipeline and Outbound", "פייפליין ואאוטבאונד",
     ["Pipeline", "Forecasting", "Outbound"], ["פייפליין", "אאוטבאונד"]),
    ("frum-business", "Frum and Heimishe Business", "", ["Frum", "Heimishe Business"], []),
]
TAG_TOPIC = {"en": {}, "he": {}}
for _slug, _en, _he, _ten, _the in TOPICS:
    for _t in _ten:
        TAG_TOPIC["en"].setdefault(_t.lower(), _slug)
    for _t in _the:
        TAG_TOPIC["he"].setdefault(_t.lower(), _slug)


def _base(lang):
    return "/he/blog/" if lang == "he" else "/blog/"


def index_url(lang, page=1):
    return _base(lang).rstrip("/") if page == 1 else "%spage-%d" % (_base(lang), page)


def topic_url(lang, slug, page=1):
    return "%stopic-%s%s" % (_base(lang), slug, "" if page == 1 else "-page-%d" % page)


def post_topics(p):
    m = TAG_TOPIC[p["lang"]]
    out = []
    for t in p["tags"]:
        slug = m.get(t.lower())
        if slug and slug not in out:
            out.append(slug)
    return out


def topic_groups(posts, lang):
    """[(slug, label, [posts])] for topics with enough posts, in TOPICS order."""
    out = []
    for slug, en, he, _a, _b in TOPICS:
        label = he if lang == "he" else en
        mine = [p for p in posts if slug in post_topics(p)]
        if label and len(mine) >= MIN_TOPIC:
            out.append((slug, label, mine))
    return out


def _post_cards(posts, lang):
    he = lang == "he"
    base = _base(lang)
    read_lbl = "דק' קריאה" if he else "min read"
    more_lbl = "לקריאת הפוסט &larr;" if he else "Read the post &rarr;"
    cards = []
    for p in posts:
        url = "%s%s" % (base, p["slug"])
        tagrow = ""
        if p["tags"]:
            tagrow = '<div class="tagrow">' + "".join(
                '<span class="tag">%s</span>' % esc(t) for t in p["tags"]) + "</div>"
        cards.append(
            '      <a class="post-card" href="%s">\n'
            '        <span class="meta">%s &middot; %s %s</span>\n'
            '        <h2>%s</h2>\n'
            '        <p>%s</p>\n'
            '        %s\n'
            '        <span class="more">%s</span>\n'
            '      </a>' % (url, human_date(p["date"], lang), p["read"], read_lbl,
                           esc(p["title"]), esc(p["description"]), tagrow, more_lbl))
    return cards


def _pager(lang, page, pages, url_for):
    if pages < 2:
        return ""
    he = lang == "he"
    newer, older = ("חדשים יותר", "ישנים יותר") if he else ("Newer", "Older")
    a1, a2 = ("&rarr;", "&larr;") if he else ("&larr;", "&rarr;")
    parts = []
    if page > 1:
        parts.append('<a class="pg-step" rel="prev" href="%s">%s %s</a>' % (url_for(page - 1), a1, newer))
    nums = []
    for n in range(1, pages + 1):
        if n == page:
            nums.append('<span class="pg-cur" aria-current="page">%d</span>' % n)
        elif n in (1, pages) or abs(n - page) <= 2:
            nums.append('<a href="%s">%d</a>' % (url_for(n), n))
        elif nums and nums[-1] != '<span class="pg-gap">...</span>':
            nums.append('<span class="pg-gap">...</span>')
    parts.append('<span class="pg-nums">%s</span>' % "".join(nums))
    if page < pages:
        parts.append('<a class="pg-step" rel="next" href="%s">%s %s</a>' % (url_for(page + 1), older, a2))
    return '      <nav class="pager" aria-label="%s">%s</nav>' % ("עמודים" if he else "Pages", "".join(parts))


def render_index(posts, lang="en", page=1, pages=1, topic=None, groups=(), other_lang_topics=()):
    """One listing page. `posts` is the slice for this page. `topic` is (slug, label) or None."""
    he = lang == "he"
    base = _base(lang)
    cards = _post_cards(posts, lang)
    empty = 'בקרוב הפוסטים הראשונים.' if he else 'First posts coming soon.'
    listing = "\n".join(cards) if cards else \
        '      <p style="color:var(--soft)">%s</p>' % empty

    ld = (
        '{"@context":"https://schema.org","@type":"Blog","@id":"%s%s",'
        '"name":"Tal Paperin Insights","url":"%s%s",'
        '"description":"%s",'
        '"inLanguage":"%s",'
        '"author":{"@id":"%s/#tal"},"publisher":{"@id":"%s/#business"}}</script>\n'
        '  <script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"%s","item":"%s%s"},'
        '{"@type":"ListItem","position":2,"name":"%s","item":"%s%s"}]}'
    ) % (SITE, base.rstrip("/"), SITE, base.rstrip("/"),
         ("רשימות מהשטח על מכירות B2B, מנהיגות הכנסות, Go-to-Market ותיקון מערכי הכנסות שבורים."
          if he else
          "Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue."),
         "he" if he else "en", SITE, SITE,
         "בית" if he else "Home", SITE, "/he" if he else "/",
         "בלוג" if he else "Blog", SITE, base.rstrip("/"))

    # topic chips (same on every listing page)
    chips = ""
    if groups:
        all_lbl = "הכול" if he else "All posts"
        chips = '      <nav class="topic-nav" aria-label="%s"><a class="tag%s" href="%s">%s</a>%s</nav>\n' % (
            "נושאים" if he else "Topics", "" if topic else " on", index_url(lang), all_lbl,
            "".join('<a class="tag%s" href="%s">%s</a>' % (
                " on" if topic and topic[0] == g[0] else "", topic_url(lang, g[0]), esc(g[1])) for g in groups))
    url_for = (lambda n: topic_url(lang, topic[0], n)) if topic else (lambda n: index_url(lang, n))
    pager = _pager(lang, page, pages, url_for)

    template = TEMPLATE_INDEX_HE if he else TEMPLATE_INDEX
    html = template \
        .replace('      <div class="post-list">\n{{LISTING}}\n      </div>',
                 chips + '      <div class="post-list">\n{{LISTING}}\n      </div>' + ("\n" + pager if pager else "")) \
        .replace("{{LISTING}}", listing) \
        .replace("{{LD}}", ld) \
        .replace("{{NAV}}", HE_NAV if he else NAV) \
        .replace("{{FOOTER}}", (_svc_mod.BIO_HE + HE_FOOTER) if he else (_svc_mod.BIO_EN + FOOTER)) \
        .replace("{{FONTS}}", HE_FONTS if he else FONTS) \
        .replace("{{ANALYTICS}}", ANALYTICS + "\n\n  " + _svc_mod.graph_ld(he))
    if page == 1 and not topic:
        return html

    # Variants (page 2+, topic pages): own title, description, canonical and robots.
    site_name = "טל פאפרין" if he else "Tal Paperin"
    self_url = SITE + url_for(page)
    pg = (" (עמוד %d)" % page if he else " (page %d)" % page) if page > 1 else ""
    if topic:
        title = ("%s: פוסטים%s | %s" if he else "%s: posts%s | %s") % (topic[1], pg, site_name)
        desc = (("כל הפוסטים של טל פאפרין בנושא %s, מהחדש לישן." if he else
                 "Every post by Tal Paperin on %s, newest first.") % topic[1])
        h1 = topic[1]
        html = re.sub(r'<h1>.*?</h1>', lambda m: '<h1>%s</h1>' % esc(h1), html, count=1)
    else:
        title = ("הבלוג%s | %s" if he else "Blog%s | %s") % (pg, site_name)
        desc = None
    html = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % esc(title), html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + esc(title) + '"', html, count=1)
    html = re.sub(r'(<meta name="twitter:title" content=")[^"]*"', lambda m: m.group(1) + esc(title) + '"', html, count=1)
    if desc:
        html = re.sub(r'(<meta name="description" content=")[^"]*"', lambda m: m.group(1) + esc(desc) + '"', html, count=1)
    html = re.sub(r'(<link rel="canonical" href=")[^"]*"', lambda m: m.group(1) + self_url + '"', html, count=1)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + self_url + '"', html, count=1)
    # hreflang: a topic's first page pairs with the same topic in the other language when it exists.
    alt = ""
    if topic and page == 1 and topic[0] in other_lang_topics:
        en_u = SITE + topic_url("en", topic[0])
        he_u = SITE + topic_url("he", topic[0])
        alt = ('  <link rel="alternate" hreflang="en" href="%s" />\n'
               '  <link rel="alternate" hreflang="he" href="%s" />\n'
               '  <link rel="alternate" hreflang="x-default" href="%s" />\n' % (en_u, he_u, en_u))
    html = re.sub(r'(?:  <link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n)+', lambda m: alt, html, count=1)
    if page > 1:
        html = html.replace('<meta name="robots" content="index, follow" />',
                            '<meta name="robots" content="noindex, follow" />', 1)
    return html


def write_listings(posts, lang, out_dir, other_lang_topics=()):
    """Write index.html, page-N.html and the topic pages. Returns the list of file names written
    and the topic slugs that got a page."""
    groups = topic_groups(posts, lang)
    written = []

    def emit(name, html):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(html)
        written.append(name)

    pages = max(1, -(-len(posts) // PER_PAGE))
    for n in range(1, pages + 1):
        chunk = posts[(n - 1) * PER_PAGE:n * PER_PAGE]
        emit("index.html" if n == 1 else "page-%d.html" % n,
             render_index(chunk, lang, n, pages, None, groups, other_lang_topics))
    for slug, label, mine in groups:
        tp = max(1, -(-len(mine) // PER_PAGE))
        for n in range(1, tp + 1):
            chunk = mine[(n - 1) * PER_PAGE:n * PER_PAGE]
            emit("topic-%s%s.html" % (slug, "" if n == 1 else "-page-%d" % n),
                 render_index(chunk, lang, n, tp, (slug, label), groups, other_lang_topics))
    return written, [g[0] for g in groups]


def clean_stale(out_dir, keep):
    """Remove generated .html files in a blog folder that no longer have a source."""
    keep = set(keep)
    for fn in os.listdir(out_dir):
        if fn.endswith(".html") and fn not in keep:
            os.remove(os.path.join(out_dir, fn))


def render_rss(posts, lang="en"):
    he = lang == "he"
    base = "/he/blog/" if he else "/blog/"
    items = []
    for p in posts[:30]:
        url = "%s%s%s" % (SITE, base, p["slug"])
        items.append(
            "    <item>\n"
            "      <title>%s</title>\n"
            "      <link>%s</link>\n"
            "      <guid isPermaLink=\"true\">%s</guid>\n"
            "      <pubDate>%s</pubDate>\n"
            "      <description>%s</description>\n"
            "    </item>" % (esc(p["title"]), url, url, rfc822(p["date"]),
                            esc(p["description"])))
    build_date = rfc822(datetime.date.today())
    template = TEMPLATE_RSS_HE if he else TEMPLATE_RSS
    return template \
        .replace("{{BUILD_DATE}}", build_date) \
        .replace("{{ITEMS}}", "\n".join(items))


def render_sitemap(posts, he_posts=None, topics=(), he_topics=()):
    he_posts = [p for p in (he_posts or []) if not p.get("noindex")]
    posts = [p for p in posts if not p.get("noindex")]
    today = datetime.date.today().isoformat()
    urls = [
        ('%s/' % SITE, '1.0', today),
        ('%s/he' % SITE, '0.9', today),
        ('%s/blog' % SITE, '0.8', today),
        ('%s/he/blog' % SITE, '0.7', today),
        ('%s/about' % SITE, '0.7', today),
        ('%s/guides' % SITE, '0.7', today),
        ('%s/answers' % SITE, '0.8', today),
        ('%s/sales-cost-calculator' % SITE, '0.7', today),
        ('%s/services' % SITE, '0.8', today),
        ('%s/case-studies' % SITE, '0.8', today),
        ('%s/pricing' % SITE, '0.8', today),
        ('%s/recommendations' % SITE, '0.7', today),
        ('%s/contact' % SITE, '0.7', today),
        ('%s/privacy' % SITE, '0.3', today),
        ('%s/terms' % SITE, '0.3', today),
    ]
    for s in SERVICES:
        urls.append(('%s/services/%s' % (SITE, s["slug"]), '0.7', today))
    for g in GUIDES:
        urls.append(('%s/%s' % (SITE, g["slug"]), '0.8', today))
    for c in _svc_mod.CASE_STUDIES:
        urls.append(('%s/case-studies/%s' % (SITE, _svc_mod.case_slug(c)), '0.7', today))
        urls.append(('%s/he/case-studies/%s' % (SITE, _svc_mod.case_slug(c)), '0.5', today))
    for g in HE_GUIDES:
        urls.append(('%s/he/%s' % (SITE, g["slug"]), '0.6', today))
    urls.append(('%s/he/services' % SITE, '0.7', today))
    for s in SERVICES:
        urls.append(('%s/he/services/%s' % (SITE, s["slug"]), '0.6', today))
    urls.append(('%s/he/challenges' % SITE, '0.6', today))
    urls.append(('%s/he/about' % SITE, '0.6', today))
    urls.append(('%s/he/guides' % SITE, '0.6', today))
    urls.append(('%s/he/answers' % SITE, '0.6', today))
    urls.append(('%s/he/case-studies' % SITE, '0.7', today))
    urls.append(('%s/he/pricing' % SITE, '0.6', today))
    urls.append(('%s/he/sales-cost-calculator' % SITE, '0.6', today))
    urls.append(('%s/he/recommendations' % SITE, '0.6', today))
    urls.append(('%s/he/contact' % SITE, '0.6', today))
    urls.append(('%s/he/privacy' % SITE, '0.3', today))
    urls.append(('%s/he/terms' % SITE, '0.3', today))
    for t in topics:
        urls.append((SITE + topic_url("en", t), '0.5', today))
    for t in he_topics:
        urls.append((SITE + topic_url("he", t), '0.4', today))
    for p in posts:
        urls.append(('%s/blog/%s' % (SITE, p["slug"]), '0.7', p["updated"].isoformat()))
    for p in he_posts:
        urls.append(('%s/he/blog/%s' % (SITE, p["slug"]), '0.6', p["updated"].isoformat()))
    body = "\n".join(
        '  <url>\n    <loc>%s</loc>\n    <changefreq>weekly</changefreq>\n'
        '    <priority>%s</priority>\n    <lastmod>%s</lastmod>\n  </url>'
        % (loc, pri, lm) for loc, pri, lm in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + body + "\n</urlset>\n")


def render_llms(posts):
    lines = [
        "# Tal Paperin",
        "",
        "> Fractional CRO and fractional VP of Sales for B2B companies, including B2B SaaS. "
        "Operator, not advisor. Week one: I find what's broken. Week two: you get the plan. "
        "Then I rebuild the sales engine and own the revenue number. I bring my own sales team "
        "(SDRs and account executives) and my own marketing team, led by a fractional CMO. "
        "30-plus B2B companies rebuilt, $20M ARR managed last year, work across five continents. "
        "Most clients are in the US; also North America, Europe and APAC. Pricing is "
        "month-to-month, Advisor $2,000 to CRO Ownership $22,000, plus a performance share.",
        "",
        "## Canonical site",
        "- %s/" % SITE,
        "",
        "## Legal entity",
        "- KSW Solutions (https://ksw.solutions) is Tal Paperin's company and the legal entity behind talpaperin.com. "
        "Both sites describe the same fractional CRO practice, led by Tal Paperin.",
        "",
        "## Key pages",
        "- [Tal Paperin, Fractional CRO (home)](%s/): what I fix, how I work, case studies, "
        "pricing and contact." % SITE,
        "- [About Tal Paperin](%s/about): background, experience, the teams he brings, credentials and how he works." % SITE,
        "- [Services](%s/services): fractional CRO, fractional VP of Sales, outsourced sales leadership, go-to-market, team building and market entry." % SITE,
        "- [Fractional CRO](%s/services/fractional-cro): the seat that owns the revenue number, strategy, team, pipeline and forecast." % SITE,
        "- [Fractional VP of Sales](%s/fractional-vp-of-sales): builds and runs the B2B sales team, playbook and pipeline, part-time." % SITE,
        "- [Fractional CRO for B2B SaaS](%s/fractional-cro-for-saas): ICP, pricing, outbound, the team and the forecast for B2B SaaS companies." % SITE,
        "- [What a fractional CRO costs](%s/fractional-cro-cost): $2,000 to $22,000 a month, billed monthly, no contract, plus a performance share." % SITE,
        "- [Fractional CRO vs hiring a VP of Sales](%s/fractional-cro-vs-vp-of-sales): when a fractional CRO beats a full-time VP hire." % SITE,
        "- [Fractional VP of Sales vs a full-time VP of Sales](%s/fractional-vp-sales-vs-full-time-vp-sales): the same seat, part-time and month to month, compared with a full-time hire." % SITE,
        "- [Outsourced sales team vs in-house](%s/outsourced-sales-team-vs-in-house): how to choose by stage." % SITE,
        "- [When founder-led sales stops scaling](%s/founder-led-sales-wont-scale): why it stalls and how to hand the motion to a team." % SITE,
        "- [Why VP of Sales hires fail](%s/why-did-my-vp-of-sales-leave): usually the seat, not only the person." % SITE,
        "- [Fractional CRO for US market entry](%s/fractional-cro-for-the-us-market): beachhead, motion and team for B2B companies entering the United States." % SITE,
        "- [Pricing](%s/pricing): Advisor $2,000, Starter $6,000, Growth $12,000, CRO Ownership $22,000 a month, plus a performance share. No long contracts." % SITE,
        "- [Recommendations](%s/recommendations): what founders and executives say, in their words." % SITE,
        "- [Case studies](%s/case-studies): engagements across SaaS, IoT, manufacturing, medical and retail, on five continents." % SITE,
        "- [Answers](%s/answers): straight answers to the questions founders ask when revenue is stuck." % SITE,
        "- [Guides](%s/guides): every guide and comparison in one place." % SITE,
        "- [Blog](%s/blog): field notes on B2B sales, B2B SaaS, go-to-market and fixing stalled revenue." % SITE,
        "- [Contact](%s/contact): email, WhatsApp, a 15-minute booking link and a contact form." % SITE,
        "- [Hebrew site](%s/he): Hebrew version of the site." % SITE,
        "- TheDealMentor.AI (https://thedealmentor.ai): Tal's own product, a virtual CRO for founders who want to run the motion themselves.",
        "",
        "## Services",
    ]
    for s in SERVICES:
        lines.append("- [%s](%s/services/%s): %s" % (s["h1"], SITE, s["slug"], s["desc"]))
    lines += ["", "## Guides"]
    for g in GUIDES:
        lines.append("- [%s](%s/%s): %s" % (g["h1"], SITE, g["slug"], g["desc"]))
    lines += ["", "## Case studies"]
    for c in _svc_mod.CASE_STUDIES:
        lines.append("- [%s](%s/case-studies/%s): %s" % (
            _svc_mod.CASE_PAGES_EN[c["id"]]["h1"], SITE, _svc_mod.case_slug(c),
            _svc_mod.CASE_PAGES_EN[c["id"]]["desc"]))
    lines += ["", "## Hebrew (עברית)",
              "- [Services in Hebrew](%s/he/services): Fractional CRO, outsourced sales, GTM, team building, distributors and market entry, in Hebrew." % SITE,
              "- [International B2B sales guide (Hebrew)](%s/he/challenges): the bold guide to selling B2B internationally from Israel." % SITE,
              "", "## Blog posts"]
    # Lead with the broad B2B posts; the frum/heimishe niche cluster goes last.
    def _is_niche(p):
        return any(k in p["slug"] for k in ("frum", "heimishe", "yiddish"))
    ordered = [p for p in posts if not _is_niche(p)] + [p for p in posts if _is_niche(p)]
    for p in ordered:
        lines.append("- [%s](%s/blog/%s): %s" % (p["title"], SITE, p["slug"], p["description"]))
    lines += [
        "",
        "## Contact",
        "- Email: tal@ksw.solutions",
        "- LinkedIn: https://www.linkedin.com/in/talpaperin/",
        "- Book a call: https://calendly.com/ksw/15min",
    ]
    return "\n".join(lines) + "\n"


# --- HTML templates (CSS lives in blog/blog.css so no braces collide) ---

TEMPLATE_POST = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{METATITLE}} | Tal Paperin</title>
  <meta name="description" content="{{DESC}}" />
  <meta name="keywords" content="{{KEYWORDS}}" />
  <meta name="author" content="Tal Paperin" />
  <meta name="robots" content="{{ROBOTS}}" />
  <link rel="canonical" href="{{URL}}" />
{{HREFLANG}}

  <meta property="og:type" content="article" />
  <meta property="og:url" content="{{URL}}" />
  <meta property="og:title" content="{{TITLE}}" />
  <meta property="og:description" content="{{DESC}}" />
  <meta property="og:image" content="{{IMG}}" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta property="og:locale" content="en_US" />
  <meta property="article:published_time" content="{{PUBLISHED}}" />
  <meta property="article:modified_time" content="{{MODIFIED}}" />
  <meta property="article:author" content="Tal Paperin" />
{{ARTICLE_TAGS}}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{{TITLE}}" />
  <meta name="twitter:description" content="{{DESC}}" />
  <meta name="twitter:image" content="{{IMG}}" />

  {{FONTS}}
  <link rel="stylesheet" href="/blog/blog.css" />
  <link rel="alternate" type="application/rss+xml" title="Tal Paperin Insights" href="/blog/rss.xml" />

  {{ANALYTICS}}

  <script type="application/ld+json">{{LD}}</script>
  <script type="application/ld+json">{{CRUMB}}</script>
</head>
<body>
{{NAV}}

  <main class="page" id="main">
    <div class="wrap">
      <article class="article">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog">Blog</a></nav>
        <h1>{{TITLE}}</h1>
        <div class="postmeta">
          <span>By Tal Paperin</span><span class="dot">&middot;</span>
          <time datetime="{{PUBLISHED}}">{{HUMAN_DATE}}</time><span class="dot">&middot;</span>
          <span>{{READ}} min read</span>
        </div>
        {{TAGROW}}
        <div class="body">
{{BODY}}
        </div>
{{SUBSCRIBE}}
{{CTA}}
        <a class="backlink" href="/blog">&larr; All posts</a>
      </article>
    </div>
  </main>

{{FOOTER}}
<style>.magnetic{transition:transform .25s cubic-bezier(.2,.7,.2,1)}</style>
<script>
(function(){
  if(!matchMedia('(hover:hover) and (pointer:fine)').matches)return;
  document.querySelectorAll('.btn-primary,.btn-secondary').forEach(function(btn){
    btn.classList.add('magnetic');
    btn.addEventListener('pointermove',function(e){var r=btn.getBoundingClientRect();var mx=e.clientX-(r.left+r.width/2),my=e.clientY-(r.top+r.height/2);btn.style.transform='translate('+(mx*0.28).toFixed(1)+'px,'+(my*0.4).toFixed(1)+'px)';});
    btn.addEventListener('pointerleave',function(){btn.style.transform='';});
  });
})();
</script>
</body>
</html>
'''

TEMPLATE_INDEX = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>B2B Sales and Fractional CRO Notes | Tal Paperin</title>
  <meta name="description" content="Field notes from fractional CRO Tal Paperin on B2B sales, B2B SaaS, go-to-market and fixing revenue functions that have stalled." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/blog" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/blog" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/blog" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/blog" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/blog" />
  <meta property="og:title" content="B2B Sales and Fractional CRO Notes | Tal Paperin" />
  <meta property="og:description" content="Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="B2B Sales and Fractional CRO Notes | Tal Paperin" />
  <meta name="twitter:description" content="Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {{FONTS}}
  <link rel="stylesheet" href="/blog/blog.css" />
  <link rel="alternate" type="application/rss+xml" title="Tal Paperin Insights" href="/blog/rss.xml" />

  {{ANALYTICS}}

  <script type="application/ld+json">{{LD}}</script>
</head>
<body>
{{NAV}}

  <main class="page" id="main">
    <div class="wrap">
      <div class="blog-head">
        <div class="glowline"></div>
        <div class="eyebrow">Blog</div>
        <h1>Notes on selling, scaling and fixing revenue.</h1>
        <p>Practical takes on B2B sales, fractional CRO leadership and go-to-market, from 20-plus years carrying the number on five continents.</p>
      </div>
      <div class="post-list">
{{LISTING}}
      </div>
    </div>
  </main>

{{FOOTER}}
<style>.magnetic{transition:transform .25s cubic-bezier(.2,.7,.2,1)}</style>
<script>
(function(){
  if(!matchMedia('(hover:hover) and (pointer:fine)').matches)return;
  document.querySelectorAll('.btn-primary,.btn-secondary').forEach(function(btn){
    btn.classList.add('magnetic');
    btn.addEventListener('pointermove',function(e){var r=btn.getBoundingClientRect();var mx=e.clientX-(r.left+r.width/2),my=e.clientY-(r.top+r.height/2);btn.style.transform='translate('+(mx*0.28).toFixed(1)+'px,'+(my*0.4).toFixed(1)+'px)';});
    btn.addEventListener('pointerleave',function(){btn.style.transform='';});
  });
})();
</script>
</body>
</html>
'''

TEMPLATE_RSS = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Tal Paperin Insights</title>
    <link>https://talpaperin.com/blog</link>
    <atom:link href="https://talpaperin.com/blog/rss.xml" rel="self" type="application/rss+xml" />
    <description>Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue.</description>
    <language>en-us</language>
    <lastBuildDate>{{BUILD_DATE}}</lastBuildDate>
{{ITEMS}}
  </channel>
</rss>
'''

TEMPLATE_POST_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{METATITLE}} | טל פאפרין</title>
  <meta name="description" content="{{DESC}}" />
  <meta name="keywords" content="{{KEYWORDS}}" />
  <meta name="author" content="Tal Paperin" />
  <meta name="robots" content="{{ROBOTS}}" />
  <link rel="canonical" href="{{URL}}" />
{{HREFLANG}}

  <meta property="og:type" content="article" />
  <meta property="og:url" content="{{URL}}" />
  <meta property="og:title" content="{{TITLE}}" />
  <meta property="og:description" content="{{DESC}}" />
  <meta property="og:image" content="{{IMG}}" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta property="og:locale" content="he_IL" />
  <meta property="article:published_time" content="{{PUBLISHED}}" />
  <meta property="article:modified_time" content="{{MODIFIED}}" />
  <meta property="article:author" content="Tal Paperin" />
{{ARTICLE_TAGS}}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{{TITLE}}" />
  <meta name="twitter:description" content="{{DESC}}" />
  <meta name="twitter:image" content="{{IMG}}" />

  {{FONTS}}
  <link rel="stylesheet" href="/he/he-pages.css" />
  <link rel="alternate" type="application/rss+xml" title="Tal Paperin Insights" href="/he/blog/rss.xml" />

  {{ANALYTICS}}

  <script type="application/ld+json">{{LD}}</script>
  <script type="application/ld+json">{{CRUMB}}</script>
</head>
<body>
{{NAV}}

  <main class="page" id="main">
    <div class="wrap">
      <article class="article">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/he">בית</a> / <a href="/he/blog">בלוג</a></nav>
        <h1>{{TITLE}}</h1>
        <div class="postmeta">
          <span>מאת טל פאפרין</span><span class="dot">&middot;</span>
          <time datetime="{{PUBLISHED}}">{{HUMAN_DATE}}</time><span class="dot">&middot;</span>
          <span>{{READ}} דק' קריאה</span>
        </div>
        {{TAGROW}}
        <div class="body">
{{BODY}}
        </div>
{{SUBSCRIBE}}
{{CTA}}
        <a class="backlink" href="/he/blog">&rarr; כל הפוסטים</a>
      </article>
    </div>
  </main>

{{FOOTER}}
<style>.magnetic{transition:transform .25s cubic-bezier(.2,.7,.2,1)}</style>
<script>
(function(){
  if(!matchMedia('(hover:hover) and (pointer:fine)').matches)return;
  document.querySelectorAll('.btn-primary,.btn-secondary').forEach(function(btn){
    btn.classList.add('magnetic');
    btn.addEventListener('pointermove',function(e){var r=btn.getBoundingClientRect();var mx=e.clientX-(r.left+r.width/2),my=e.clientY-(r.top+r.height/2);btn.style.transform='translate('+(mx*0.28).toFixed(1)+'px,'+(my*0.4).toFixed(1)+'px)';});
    btn.addEventListener('pointerleave',function(){btn.style.transform='';});
  });
})();
</script>
</body>
</html>
'''

TEMPLATE_INDEX_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>תובנות על מכירות B2B ומנהיגות הכנסות | טל פאפרין</title>
  <meta name="description" content="רשימות מהשטח של טל פאפרין על מכירות B2B, מנהיגות הכנסות, אסטרטגיית Go-to-Market ותיקון מערכי הכנסות שבורים." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/blog" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/blog" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/blog" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/blog" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/blog" />
  <meta property="og:title" content="תובנות על מכירות B2B ומנהיגות הכנסות | טל פאפרין" />
  <meta property="og:description" content="רשימות מהשטח על מכירות B2B, מנהיגות הכנסות ו-Go-to-Market." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="תובנות על מכירות B2B ומנהיגות הכנסות | טל פאפרין" />
  <meta name="twitter:description" content="רשימות מהשטח על מכירות B2B, מנהיגות הכנסות ו-Go-to-Market." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {{FONTS}}
  <link rel="stylesheet" href="/he/he-pages.css" />
  <link rel="alternate" type="application/rss+xml" title="Tal Paperin Insights" href="/he/blog/rss.xml" />

  {{ANALYTICS}}

  <script type="application/ld+json">{{LD}}</script>
</head>
<body>
{{NAV}}

  <main class="page" id="main">
    <div class="wrap">
      <div class="blog-head">
        <div class="glowline"></div>
        <div class="eyebrow">בלוג</div>
        <h1>מכירות, פיתוח עסקי וגדילה</h1>
        <p>תובנות מעשיות על מכירות B2B, מנהיגות הכנסות ו-Go-to-Market, מתוך יותר מ-20 שנה של אחריות על התוצאות בחמש יבשות.</p>
      </div>
      <div class="post-list">
{{LISTING}}
      </div>
    </div>
  </main>

{{FOOTER}}
<style>.magnetic{transition:transform .25s cubic-bezier(.2,.7,.2,1)}</style>
<script>
(function(){
  if(!matchMedia('(hover:hover) and (pointer:fine)').matches)return;
  document.querySelectorAll('.btn-primary,.btn-secondary').forEach(function(btn){
    btn.classList.add('magnetic');
    btn.addEventListener('pointermove',function(e){var r=btn.getBoundingClientRect();var mx=e.clientX-(r.left+r.width/2),my=e.clientY-(r.top+r.height/2);btn.style.transform='translate('+(mx*0.28).toFixed(1)+'px,'+(my*0.4).toFixed(1)+'px)';});
    btn.addEventListener('pointerleave',function(){btn.style.transform='';});
  });
})();
</script>
</body>
</html>
'''

TEMPLATE_RSS_HE = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Tal Paperin Insights (עברית)</title>
    <link>https://talpaperin.com/he/blog</link>
    <atom:link href="https://talpaperin.com/he/blog/rss.xml" rel="self" type="application/rss+xml" />
    <description>רשימות מהשטח על מכירות B2B, מנהיגות הכנסות ו-Go-to-Market.</description>
    <language>he</language>
    <lastBuildDate>{{BUILD_DATE}}</lastBuildDate>
{{ITEMS}}
  </channel>
</rss>
'''


def main():
    posts = load_posts(POSTS_DIR, "en")
    he_posts = load_posts(POSTS_DIR_HE, "he")

    # Pair translations: if an EN and HE post share a slug, cross-link them
    # via hreflang. Native Hebrew posts with no English twin stay unpaired.
    en_slugs = {p["slug"] for p in posts}
    he_slugs = {p["slug"] for p in he_posts}
    for p in posts:
        if not p["alt"] and p["slug"] in he_slugs:
            p["alt"] = p["slug"]
    for p in he_posts:
        if not p["alt"] and p["slug"] in en_slugs:
            p["alt"] = p["slug"]

    # Per-post social cards (headline on the brand background). Skipped without Pillow.
    try:
        import og_cards
        cards = og_cards.ensure_cards(posts + he_posts, ROOT)
    except Exception as e:  # the build must never fail because of a card
        print("Social cards skipped: %s" % e)
        cards = {}
    for p in posts + he_posts:
        if p["image"] == "/og-image.jpg" and (p["lang"], p["slug"]) in cards:
            p["image"] = cards[(p["lang"], p["slug"])]

    en_topics = [g[0] for g in topic_groups(posts, "en")]
    he_topics = [g[0] for g in topic_groups(he_posts, "he")]
    for p in posts:
        p["live_topics"] = en_topics
    for p in he_posts:
        p["live_topics"] = he_topics

    for p in posts:
        with open(os.path.join(BLOG_DIR, p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(render_post(p))
    written, _ = write_listings(posts, "en", BLOG_DIR, he_topics)
    clean_stale(BLOG_DIR, written + [p["slug"] + ".html" for p in posts])
    with open(os.path.join(BLOG_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(render_rss(posts, "en"))

    if he_posts:
        os.makedirs(HE_BLOG_DIR, exist_ok=True)
        for p in he_posts:
            with open(os.path.join(HE_BLOG_DIR, p["slug"] + ".html"), "w", encoding="utf-8") as f:
                f.write(render_post(p))
        written, _ = write_listings(he_posts, "he", HE_BLOG_DIR, en_topics)
        clean_stale(HE_BLOG_DIR, written + [p["slug"] + ".html" for p in he_posts])
        with open(os.path.join(HE_BLOG_DIR, "rss.xml"), "w", encoding="utf-8") as f:
            f.write(render_rss(he_posts, "he"))

    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(render_sitemap(posts, he_posts, en_topics, he_topics))
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(render_llms([p for p in posts if not p.get("noindex")]))
    _svc_mod.optimize_html_dirs([BLOG_DIR, HE_BLOG_DIR])
    print("Built %d EN post(s) and %d HE post(s)." % (len(posts), len(he_posts)))


if __name__ == "__main__":
    main()
