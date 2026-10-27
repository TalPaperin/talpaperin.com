#!/usr/bin/env python3
"""
Static service-page generator for talpaperin.com.

Generates /services/index.html and one SEO-optimized page per service,
reusing the blog's dark-theme stylesheet (/blog/blog.css). Run:

  python3 services/build.py

Service URLs are also pulled into sitemap.xml and llms.txt by blog/build.py,
so run this first, then blog/build.py.

These templates are the source of truth and reproduce the live pages exactly
(About's "Fractional CRO / CGO" positioning, the Headcount ERC case study, the
btn-primary/btn-secondary classes and the magnetic-button block are all in the
templates). Edit the templates here, not the generated HTML, then re-run.
"""

import os
import re
import html
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVC_DIR = os.path.join(ROOT, "services")
SITE = "https://talpaperin.com"

ANALYTICS = ('<!-- Google tag (gtag.js) -->\n'
             '  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GG3XFQTX11"></script>\n'
             '  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
             "gtag('js',new Date());gtag('config','G-GG3XFQTX11');</script>\n"
             '  <script src="https://analytics.ahrefs.com/analytics.js" '
             'data-key="yw4L2JvlOTPBX9ieFq8jZg" async></script>')
FONTS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml" />\n' '  <link rel="icon" href="/favicon.ico" sizes="any" />\n' '  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n' '  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Anton&'
         'family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />')

HAMBURGER = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" '
             'stroke-linecap="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/>'
             '<line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>')

FLAG_IL = ('<svg width="31" height="21" viewBox="0 0 22 15" aria-hidden="true">'
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
        <a href="/services/">Services</a>
        <a href="/pricing">Pricing</a>
        <a href="/case-studies">Case Studies</a>
        <a href="/recommendations">Recommendations</a>
        <a href="/blog/">Blog</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/he/" hreflang="he" aria-label="Switch to Hebrew">''' + FLAG_IL + '''</a>
        <a class="btn btn-primary" href="/contact">Let's Talk</a>
        <button class="navtoggle" aria-label="Menu" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 Tal Paperin. All rights reserved. &middot; <a href="/guides">Guides</a></span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="Email Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="Call Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="Tal Paperin on LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
  </script>
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
</script>'''

CTA_BOX = '''      <div class="cta-box">
        <h3>Tell me where revenue stalled. I'll tell you why.</h3>
        <p>A 15-minute call, no pitch. You will leave with at least one concrete thing to fix, whether or not we work together.</p>
        <a class="btn btn-primary" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">Book a 15-Minute Call</a>
        <a class="btn btn-secondary" href="https://wa.me/972545308119?text=Hi%20Tal%2C%20I%20found%20your%20site%20and%20want%20to%20talk%20go-to-market." target="_blank" rel="noopener">WhatsApp me</a>
      </div>'''

# ---- Decision infographics (ported from the KSW sales page, rebuilt in HTML/CSS) ----
IG_SIGNS_EN = '''<div class="ig-signs">
<div class="ig-sign"><div class="n">01</div><p>Sales have plateaued</p></div>
<div class="ig-sign"><div class="n">02</div><p>The founder still leads every deal</p></div>
<div class="ig-sign"><div class="n">03</div><p>Marketing and sales do not agree</p></div>
<div class="ig-sign"><div class="n">04</div><p>Pipeline is full but deals do not close</p></div>
<div class="ig-sign"><div class="n">05</div><p>You are preparing to scale</p></div>
<div class="ig-sign"><div class="n">06</div><p>Forecasts are guesses, not a system</p></div>
<div class="ig-sign"><div class="n">07</div><p>Your third VP Sales left this year</p></div>
<div class="ig-sign"><div class="n">08</div><p>Product and funding are here, a sales team is not</p></div>
</div>
<p class="ig-cap">Two or more of these, and it is time for an owner of the number.</p>'''
IG_SIGNS_HE = '''<div class="ig-signs">
<div class="ig-sign"><div class="n">01</div><p>המכירות נתקעו ולא צומחות</p></div>
<div class="ig-sign"><div class="n">02</div><p>המייסד עדיין מוביל כל עסקה</p></div>
<div class="ig-sign"><div class="n">03</div><p>שיווק ומכירות לא מסונכרנים</p></div>
<div class="ig-sign"><div class="n">04</div><p>הפייפליין מלא אבל עסקאות לא נסגרות</p></div>
<div class="ig-sign"><div class="n">05</div><p>אתם נערכים לצמיחה</p></div>
<div class="ig-sign"><div class="n">06</div><p>התחזיות הן ניחוש, לא מערכת</p></div>
<div class="ig-sign"><div class="n">07</div><p>סמנכ״ל המכירות השלישי עזב השנה</p></div>
<div class="ig-sign"><div class="n">08</div><p>יש מוצר ויש גיוס, אין צוות מכירות</p></div>
</div>
<p class="ig-cap">שניים או יותר מאלה, והגיע הזמן לבעל אחראי על המספר.</p>'''

IG_ENGINE_EN = '''<div class="ig-engine">
<span class="node">CEO</span>
<div class="conn"></div>
<span class="node cro">Fractional CRO</span>
<div class="conn"></div>
<div class="funcs"><span class="node">Marketing</span><span class="node">Sales</span><span class="node">Customer Success</span><span class="node">Revenue Operations</span></div>
<p class="cap">One accountable executive across the whole revenue engine.</p>
</div>'''
IG_ENGINE_HE = '''<div class="ig-engine">
<span class="node">מנכ״ל</span>
<div class="conn"></div>
<span class="node cro">סמנכ״ל הכנסות במיקור חוץ</span>
<div class="conn"></div>
<div class="funcs"><span class="node">שיווק</span><span class="node">מכירות</span><span class="node">הצלחת לקוחות</span><span class="node">תפעול הכנסות</span></div>
<p class="cap">מנהל אחד אחראי על כל מנוע ההכנסות.</p>
</div>'''

IG_PHASES_EN = '''<div class="ig-phases">
<div class="ig-phase"><div class="wk">Week 1</div><h4>Diagnose</h4><ul><li>Revenue audit</li><li>Pipeline review</li><li>CRM analysis</li><li>Leadership interviews</li><li>Customer journey</li></ul></div>
<div class="ig-phase"><div class="wk">Weeks 2-3</div><h4>Build</h4><ul><li>Sales process</li><li>ICP and messaging</li><li>Hiring plan</li><li>Playbooks</li><li>KPIs</li></ul></div>
<div class="ig-phase"><div class="wk">Weeks 4-12</div><h4>Scale</h4><ul><li>Forecasting cadence</li><li>Management rhythm</li><li>Pipeline reviews</li><li>Team scaling</li><li>Ongoing leadership</li></ul></div>
</div>
<p class="ig-cap">Exact timing depends on the retainer and the starting point.</p>'''
IG_PHASES_HE = '''<div class="ig-phases">
<div class="ig-phase"><div class="wk">שבוע 1</div><h4>אבחון</h4><ul><li>ביקורת הכנסות</li><li>סקירת פייפליין</li><li>ניתוח CRM</li><li>ראיונות הנהלה</li><li>מסע לקוח</li></ul></div>
<div class="ig-phase"><div class="wk">שבועות 2-3</div><h4>בנייה</h4><ul><li>תהליך מכירה</li><li>ICP ומסרים</li><li>תוכנית גיוס</li><li>פלייבוקים</li><li>מדדי KPI</li></ul></div>
<div class="ig-phase"><div class="wk">שבועות 4-12</div><h4>הרחבה</h4><ul><li>קצב תחזיות</li><li>שגרת ניהול</li><li>סקירות פייפליין</li><li>הרחבת צוות</li><li>הובלה מתמשכת</li></ul></div>
</div>
<p class="ig-cap">העיתוי המדויק תלוי בחבילת הריטיינר ובנקודת הפתיחה.</p>'''

IG_CAREER_EN = '''<div class="ig-career">
<div class="it"><div class="yr">2001</div><div class="lbl">International sales</div></div>
<div class="it"><div class="yr">2005</div><div class="lbl">Managing global teams</div></div>
<div class="it"><div class="yr">2010</div><div class="lbl">Building international distribution</div></div>
<div class="it"><div class="yr">2015</div><div class="lbl">SaaS, manufacturing and IoT</div></div>
<div class="it"><div class="yr">2019</div><div class="lbl">Co-founded KSW Solutions</div></div>
<div class="it"><div class="yr">2023+</div><div class="lbl">Fractional CRO and revenue leadership</div></div>
</div>'''
IG_CAREER_HE = '''<div class="ig-career">
<div class="it"><div class="yr">2001</div><div class="lbl">מכירות בינלאומיות</div></div>
<div class="it"><div class="yr">2005</div><div class="lbl">ניהול צוותים גלובליים</div></div>
<div class="it"><div class="yr">2010</div><div class="lbl">בניית הפצה בינלאומית</div></div>
<div class="it"><div class="yr">2015</div><div class="lbl">SaaS, ייצור ו-IoT</div></div>
<div class="it"><div class="yr">2019</div><div class="lbl">הקמת KSW Solutions</div></div>
<div class="it"><div class="yr">2023+</div><div class="lbl">סמנכ״ל הכנסות והובלת הכנסות</div></div>
</div>'''

IG_OWNS_EN = '''<div class="ig-two">
<div class="ig-col pos"><h4>A fractional CRO owns</h4><ul><li>Marketing and demand</li><li>The sales team and the motion</li><li>Pipeline and forecast</li><li>Customer success and retention</li><li>The revenue number, end to end</li></ul></div>
<div class="ig-col"><h4>A VP of Sales owns</h4><ul><li>The sales team</li><li>Pipeline and closing</li><li>Quota attainment</li></ul></div>
</div>
<p class="ig-cap">A VP of Sales runs the sales team. A CRO owns the whole engine that produces revenue.</p>'''
IG_OWNS_HE = '''<div class="ig-two">
<div class="ig-col pos"><h4>סמנכ״ל הכנסות במיקור חוץ אחראי על</h4><ul><li>שיווק וביקוש</li><li>צוות המכירות והמהלך</li><li>פייפליין ותחזית</li><li>הצלחת לקוחות ושימור</li><li>מספר ההכנסות, מקצה לקצה</li></ul></div>
<div class="ig-col"><h4>VP מכירות אחראי על</h4><ul><li>צוות המכירות</li><li>פייפליין וסגירה</li><li>עמידה ביעד</li></ul></div>
</div>
<p class="ig-cap">VP מכירות מריץ את צוות המכירות. CRO אחראי על כל המנוע שמייצר הכנסות.</p>'''

IG_BA_EN = '''<div class="ig-two">
<div class="ig-col"><h4>Before</h4><ul><li>Every deal runs through the founder</li><li>Nobody actually owns the number</li><li>The forecast is a guess</li><li>Revenue is lumpy and stalling</li><li>Marketing and sales blame each other</li></ul></div>
<div class="ig-col pos"><h4>After</h4><ul><li>The motion runs without the founder</li><li>A senior operator owns the number</li><li>A real forecast, updated every week</li><li>Repeatable, growing revenue</li><li>One accountable revenue function</li></ul></div>
</div>'''
IG_BA_HE = '''<div class="ig-two">
<div class="ig-col"><h4>לפני</h4><ul><li>כל עסקה עוברת דרך המייסד</li><li>אף אחד באמת לא אחראי על המספר</li><li>התחזית היא ניחוש</li><li>ההכנסות מקוטעות ונתקעות</li><li>שיווק ומכירות מאשימים זה את זה</li></ul></div>
<div class="ig-col pos"><h4>אחרי</h4><ul><li>המהלך רץ בלי המייסד</li><li>איש ביצוע בכיר אחראי על המספר</li><li>תחזית אמיתית, מתעדכנת כל שבוע</li><li>הכנסות חוזרות וצומחות</li><li>פונקציית הכנסות אחת אחראית</li></ul></div>
</div>'''

IG_DOES_EN = '''<div class="ig-does">
<div class="ig-do"><h4>Build the go-to-market</h4><p>The motion, the ICP, the messaging and the sales process, built to scale, not just advised on.</p></div>
<div class="ig-do"><h4>Hire and run the team</h4><p>SDRs, AEs and managers, recruited, trained and managed, with the ones who cannot perform replaced.</p></div>
<div class="ig-do"><h4>Own pipeline and forecast</h4><p>A real pipeline and a forecast you can trust, run on a weekly cadence instead of a guess.</p></div>
<div class="ig-do"><h4>Carry the number</h4><p>Accountable for revenue and the result, not a deck and a goodbye.</p></div>
</div>'''
IG_DOES_HE = '''<div class="ig-does">
<div class="ig-do"><h4>בניית הליכה לשוק</h4><p>המהלך, ה-ICP, המסרים ותהליך המכירה, בנויים להתרחבות, לא רק ייעוץ.</p></div>
<div class="ig-do"><h4>גיוס וניהול הצוות</h4><p>SDR, AE ומנהלים, מגויסים, מוכשרים ומנוהלים, ומי שלא מתפקד מוחלף.</p></div>
<div class="ig-do"><h4>אחריות על פייפליין ותחזית</h4><p>פייפליין אמיתי ותחזית שאפשר לסמוך עליה, בקצב שבועי במקום ניחוש.</p></div>
<div class="ig-do"><h4>נשיאה במספר</h4><p>אחריות על ההכנסות ועל התוצאה, לא מצגת ולהתראות.</p></div>
</div>'''


# --- Structured data (JSON-LD) --------------------------------------------
# One canonical entity graph, referenced by @id from every page. This gives
# Google a single, consistent business + person entity to reconcile, and gives
# AI assistants a clean node to answer "who is Tal Paperin / what does he do /
# how much" from. See graph_ld() for the shared @graph and the per-page nodes
# (Service, Review/AggregateRating, OfferCatalog) that reference it.

BUSINESS_ID = SITE + "/#business"
PERSON_ID = SITE + "/#tal"
WEBSITE_ID = SITE + "/#website"

_BIZ_DESC_EN = ("Fractional CRO, Chief Growth Officer and B2B sales consultant. Twenty years "
                "building and running revenue engines across five continents: fractional CRO "
                "leadership, outsourced sales teams, go-to-market strategy and international "
                "market entry.")
_BIZ_DESC_HE = ("סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, Chief Growth Officer ויועץ מכירות B2B. "
                "עשרים שנה של בנייה והרצה של מנועי הכנסות בחמש יבשות: הובלת מכירות במיקור חוץ, "
                "צוותי מכירות, אסטרטגיית Go-To-Market וחדירה לשווקים בינלאומיים.")


def _person_node(he=False):
    name = "טל פאפרין" if he else "Tal Paperin"
    return (
        '{"@type":"Person","@id":"%s","name":"%s","url":"%s/",'
        '"image":"%s/img/site/fractional-cro-portrait.jpg",'
        '"jobTitle":"Fractional CRO and Chief Growth Officer",'
        '"email":"mailto:tal@ksw.solutions","telephone":"+972-54-530-8119",'
        '"knowsLanguage":["English","Hebrew","Russian","Chinese"],'
        '"alumniOf":{"@type":"CollegeOrUniversity","name":"Hebrew University of Jerusalem"},'
        '"worksFor":{"@type":"Organization","name":"KSW Solutions","url":"https://ksw.solutions"},'
        '"sameAs":["https://www.linkedin.com/in/talpaperin/"]}'
    ) % (PERSON_ID, name, SITE, SITE)


def _business_node(he=False, offers=None):
    name = "טל פאפרין, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ" if he else "Tal Paperin, Fractional CRO"
    desc = _BIZ_DESC_HE if he else _BIZ_DESC_EN
    extra = ""
    # No Review markup: Google requires an aggregateRating alongside multiple
    # reviews, and Tal's testimonials carry no numeric ratings we would honestly
    # assert. The testimonials still render as visible HTML on the page.
    if offers:
        items = ",".join(
            '{"@type":"Offer","name":"%s","price":"%s","priceCurrency":"USD",'
            '"priceSpecification":{"@type":"UnitPriceSpecification","price":"%s",'
            '"priceCurrency":"USD","unitText":"per month"},'
            '"itemOffered":{"@type":"Service","name":"%s"}}'
            % (_jsonesc(nm), pr, pr, _jsonesc(nm)) for nm, pr in offers)
        cat_name = "חבילות שירות" if he else "Service packages"
        extra += (',"hasOfferCatalog":{"@type":"OfferCatalog","name":"%s",'
                  '"itemListElement":[%s]}') % (cat_name, items)
    return (
        '{"@type":"ProfessionalService","@id":"%s","name":"%s","url":"%s/",'
        '"logo":"%s/img/icon-512.png","image":"%s/og-image.jpg",'
        '"description":"%s","priceRange":"$2,000-$22,000",'
        '"email":"mailto:tal@ksw.solutions","telephone":"+972-54-530-8119",'
        '"founder":{"@id":"%s"},"employee":{"@id":"%s"},'
        '"areaServed":[{"@type":"Country","name":"United States"},'
        '{"@type":"Country","name":"Israel"},{"@type":"Place","name":"Europe"},'
        '{"@type":"Place","name":"Asia-Pacific"}],'
        '"knowsAbout":["Fractional CRO","B2B sales","Go-to-market strategy",'
        '"Sales team building","International market entry","Outsourced sales",'
        '"Distributor and channel recruitment"],'
        '"sameAs":["https://www.linkedin.com/in/talpaperin/"],'
        '"contactPoint":{"@type":"ContactPoint","telephone":"+972-54-530-8119",'
        '"email":"tal@ksw.solutions","contactType":"sales",'
        '"availableLanguage":["English","Hebrew"]}%s}'
    ) % (BUSINESS_ID, _jsonesc(name), SITE, SITE, SITE, _jsonesc(desc),
         PERSON_ID, PERSON_ID, extra)


def _website_node(he=False):
    lang = "he" if he else "en"
    return ('{"@type":"WebSite","@id":"%s","url":"%s/","name":"Tal Paperin",'
            '"inLanguage":"%s","publisher":{"@id":"%s"}}') % (WEBSITE_ID, SITE, lang, BUSINESS_ID)


def graph_ld(he=False, offers=None):
    """The shared entity graph (ProfessionalService + Person + WebSite),
    dropped into every page so @id references from Service/Offer nodes
    resolve on-page."""
    nodes = "%s,%s,%s" % (_business_node(he, offers),
                          _person_node(he), _website_node(he))
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@graph":[%s]}</script>') % nodes


# Guide slugs that are genuinely informational (comparisons / explainers) and
# should stay Article. Everything else in GUIDES is a service offering (e.g.
# "Fractional CRO for Fintech") and is marked up as Service.
ARTICLE_GUIDES = {
    "fractional-cro-cost", "fractional-cro-vs-outsourced-sales",
    "fractional-cro-vs-vp-of-sales", "how-to-hire-a-fractional-cro",
    "when-do-you-need-a-fractional-cro", "fractional-cro-roi",
    "sales-training",
    "founder-led-sales-wont-scale", "building-a-sales-team-after-funding",
    "sales-team-missing-quota", "sales-forecast-always-wrong", "hired-reps-but-no-pipeline",
    "how-to-build-a-sales-team", "sales-compensation-plan", "setting-sales-quotas",
    "b2b-go-to-market-strategy", "b2b-positioning-and-messaging", "go-to-market-motion",
    "sell-in-israel-first-or-go-global", "when-to-expand-to-the-us",
    "tal-paperin-podcasts-and-press",
}


def guide_ld(g, url, he=False):
    """Service for offering pages, Article for informational guides."""
    if g["slug"] in ARTICLE_GUIDES:
        lang = ',"inLanguage":"he"' if he else ""
        author_url = SITE + "/he/" if he else SITE + "/"
        author = "טל פאפרין" if he else "Tal Paperin"
        return ('{"@context":"https://schema.org","@type":"Article",'
                '"headline":"%s","description":"%s"%s,'
                '"author":{"@type":"Person","@id":"%s","name":"%s","url":"%s"},'
                '"publisher":{"@id":"%s"},"mainEntityOfPage":"%s"}'
                ) % (esc(g["h1"]), esc(g["desc"]), lang, PERSON_ID, author,
                     author_url, BUSINESS_ID, url)
    lang = ',"inLanguage":"he"' if he else ""
    return ('{"@context":"https://schema.org","@type":"Service",'
            '"name":"%s","description":"%s","serviceType":"Fractional CRO"%s,'
            '"provider":{"@id":"%s"},"areaServed":[{"@type":"Country","name":"United States"},'
            '{"@type":"Country","name":"Israel"}],"url":"%s","mainEntityOfPage":"%s"}'
            ) % (esc(g["h1"]), esc(g["desc"]), lang, BUSINESS_ID, url, url)


def _price_num(s):
    return "".join(ch for ch in s if ch.isdigit())


# --- Service content -------------------------------------------------------

# Pay-per-meeting price ladder (reused on the service page and the pricing page)
PPM_SETUP = "$2,500"
PPM_TIERS = [("Up to 3 meetings a month", "$3,000"), ("4 to 6 meetings", "$4,500"),
             ("7 to 14 meetings", "$6,500"), ("15+ meetings", "$9,000")]
PPM_TIERS_HE = [("עד 3 פגישות בחודש", "$3,000"), ("4 עד 6 פגישות", "$4,500"),
                ("7 עד 14 פגישות", "$6,500"), ("15+ פגישות", "$9,000")]


def _ppm_price_block(setup_label, rows, note, mo):
    r = "".join(
        '<div style="display:flex;justify-content:space-between;align-items:baseline;padding:10px 0;'
        'border-bottom:1px solid rgba(255,255,255,.08)"><span style="color:#cdd6e0">' + lbl + '</span>'
        '<span style="color:#fff;font-weight:700">' + amt +
        '<span style="color:#9aa7b5;font-weight:600;font-size:.85rem">' + mo + '</span></span></div>'
        for lbl, amt in rows)
    return (
        '<div class="ppm-price" style="background:radial-gradient(80% 130% at 18% 0%,#0c2237 0%,#0a0e14 60%);'
        'border:1px solid rgba(90,176,255,.35);border-radius:18px;padding:24px;margin:18px 0;max-width:460px">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;padding-bottom:12px;'
        'margin-bottom:6px;border-bottom:1px solid rgba(255,255,255,.14)">'
        '<span style="color:#fff;font-weight:700">' + setup_label + '</span>'
        '<span style="color:#E67E22;font-weight:800;font-size:1.2rem">' + PPM_SETUP + '</span></div>'
        + r + '<p style="color:#9aa7b5;font-size:.85rem;margin:14px 0 0">' + note + '</p></div>')


PPM_PRICE_EN = _ppm_price_block("Setup, one-time", PPM_TIERS,
    "You pay the tier that matches the meetings we book that month. No long contracts, no exit fines.", "/mo")
PPM_PRICE_HE = _ppm_price_block("הקמה, חד פעמי", PPM_TIERS_HE,
    "אתם משלמים את המדרגה שתואמת למספר הפגישות שקבענו באותו חודש. בלי חוזים ארוכים, בלי קנסות יציאה.", "לחודש")

SERVICES = [
 {"slug":"pay-per-meeting","nav":"Pay-Per-Meeting","h1":"Pay-Per-Meeting B2B Sales Meetings",
  "title":"Pay-Per-Meeting B2B Appointment Setting | Tal Paperin",
  "desc":"You pay for the B2B sales meetings we book, not emails or lists. We define your ICP, find the people, and put qualified meetings on your calendar.",
  "eyebrow":"Service",
  "lead":"You need sales meetings. I get them for you. Not another retainer for activity, you pay based on the number of qualified meetings we actually book on your calendar.",
  "card":"Outbound that bills by results. You pay for the qualified B2B meetings we book, not emails, lists or leads.",
  "sections":[
    {"h":"You need meetings, not another pipeline lecture","p":[
      "Most companies do not need another consultant telling them they need more pipeline. They need meetings. That is all this service does.",
      "You tell us what you sell and who you want to sell it to. Together we define exactly what a relevant prospect looks like: industry, geography, company size, type of company and the people inside those companies you want to meet. Then we go get them.",
      "You do not pay me to send emails. You do not pay me for leads. You do not pay me for lists. You pay based on the number of sales meetings we book. Simple."]},
    {"h":"How it works","ul":[
      "You tell us who you want to meet. We agree on your ICP and target personas, for example US financial services companies, 500-plus employees, targeting the CIO, CTO and VP Engineering. You approve it. That is who we go after.",
      "We do the work. We find the companies, find the people, build the lists, create and run the outreach, follow up and manage the whole process. SDRs, researchers, email, LinkedIn, phone, data and tooling: that is our problem, not yours.",
      "We put meetings on your calendar. When someone matching the agreed ICP and persona says yes to a date and time, we have done our job. You take the meeting, run discovery, demo, qualify, negotiate and close. We create the conversation, you take it from there."]},
    {"h":"What you pay","p":[
      "An initial setup fee launches the campaign. After that, what you pay depends on how many meetings we actually book. A weaker month, you pay less. More meetings, you pay more. That is intentional: you should not pay the same for three meetings as for fifteen."],
     "html":PPM_PRICE_EN},
    {"h":"What counts as a meeting","p":[
      "No catch, but we agree on what a meeting means before we start. You approve the ICP and the personas. We go after them. If someone who matches those criteria agrees to meet and we schedule a date and time, that is a booked meeting.",
      "We count meetings booked, not meetings attended. If the prospect later reschedules, cancels or does not show, that does not undo the work that created the meeting, so the meeting still counts and is still paid.",
      "That said, I am not here to bill you for a name on a calendar that never shows. If a booked meeting no-shows or cancels, we rebook it for you at no extra charge. To be clear, the original booking still counts and is still paid: the free rebooking is a courtesy on top, because what you are really buying is the conversation, and we keep working until you get it.",
      "And a booked meeting is not a guaranteed sale. We are responsible for getting the right person to agree to a sales conversation. What happens in and after that conversation depends on your product, offer, process and salespeople."]},
    {"h":"Why pay this way","p":[
      "Because it aligns us. A traditional SDR service charges a flat retainer, allocates people, sends thousands of emails and sends you activity reports. Maybe you get meetings, maybe you do not, and you pay the same either way.",
      "I prefer a simpler conversation: how many meetings did we book? Three, you pay the three-meeting tier. Seventeen, you pay the fifteen-plus tier. The incentive is obvious. The more meetings we get you, the more we make."]},
    {"h":"Why there is a setup fee","p":[
      "Before we can book meetings we build the campaign. The first two to three weeks cover defining the ICP and personas, building prospect data, creating the messaging, preparing the outreach, standing up the infrastructure and training the people involved. Once that is done, the focus is simple: book meetings."]},
    {"h":"Who this is for, and who it is not","p":[
      "This works for B2B companies that already have something to sell and need more conversations. You might have a sales team, a single AE, or still be founder-led. You might be entering a new market or simply short on pipeline. What matters is that you know what to do when someone gives you a meeting."],
     "ul":[
      "Good fit: you can take a relevant prospect from first conversation through discovery, proposal and close",
      "Too early: you do not yet know what you sell or who buys it",
      "Wrong fit: you expect every meeting to become an opportunity, or you want one service to both book and close for you"]},
    {"h":"Why KSW","p":[
      "I have spent more than 20 years building and managing B2B sales around the world: software, SaaS, hardware, services and complex enterprise deals. I have built teams from zero, recruited and managed SDRs and AEs, and opened international markets. So when we go get you meetings, it is not a generic lead-generation exercise. We understand sales, we understand who needs to be in the room, and we know the only reason to run outbound is to create real sales conversations.",
      "Tell me who you want to sell to and we will get you in front of them. No SDR to recruit, no team to manage, no technology to figure out, no lists to build. We book the meetings. You sell."]}]},
 {"slug":"fractional-cmo","nav":"Fractional CMO","h1":"Fractional CMO and Marketing Leadership",
  "title":"Fractional CMO and Marketing Leadership | Tal Paperin",
  "desc":"Senior marketing leadership on demand: senior oversight or full fractional CMO ownership, so marketing and sales run as one revenue engine.",
  "eyebrow":"Service",
  "lead":"Marketing that actually feeds sales. Senior oversight or full ownership of the marketing function, aligned to the number, without a full-time CMO salary.",
  "card":"Senior marketing leadership, oversight or full ownership, run as one engine with sales.",
  "sections":[
    {"h":"When you need a fractional CMO","p":["Marketing is running but nobody senior owns whether it actually produces pipeline. Or you have a capable doer who needs direction, prioritization and accountability. That is the gap a fractional CMO fills, without a full-time executive salary."],
     "ul":["Marketing spends but you cannot tie it to revenue","A capable marketing person needs senior direction and standards","Sales and marketing point fingers instead of working as one engine","You are entering a new market and need positioning and demand from zero"]},
    {"h":"What I own","p":["Two levels, depending on what you need. Oversight: senior review of plans, priorities and spend, with clear guidance on what to pursue, pause or stop. Full ownership: I lead the marketing function, its priorities and its people, and I answer for the results."],
     "ul":["Positioning, messaging and the demand-generation plan","Priorities, budget and what to stop doing","Alignment between marketing, sales and the executive team","One accountable owner for marketing performance"]},
    {"h":"Marketing and sales as one engine","p":["Most companies run marketing and sales as two departments that blame each other. I run them as one revenue engine, so the leads marketing creates are the leads sales can actually close. Delivered together with KSW Solutions, the firm I co-lead."]}]},
 {"slug":"fractional-cro","nav":"Fractional CRO","h1":"Fractional CRO",
  "title":"Fractional CRO | Tal Paperin",
  "desc":"A fractional CRO who sits in the seat and owns your revenue number, strategy, team, pipeline and forecast, without a $250K full-time hire.",
  "eyebrow":"Service",
  "lead":"Senior revenue leadership, in the seat, owning the number. Without a $250,000 full-time hire or a long-term lock-in.",
  "card":"Me in the seat, owning your revenue and answering for the number. The middle rung most companies choose.",
  "sections":[
    {"h":"When you need a fractional CRO","p":[
      "You need CRO-level judgment, but the work is not yet a full week. Or you need results now and cannot wait two quarters for a full-time hire to ramp. That is the gap a fractional CRO fills."],
     "ul":[
      "Revenue has stalled and nobody actually owns the number",
      "You are scaling and need a leader before you can justify a full-time CRO",
      "A full-time CRO runs $250,000-plus all in, with months to find and ramp and real severance risk"]},
    {"h":"What I own","ul":[
      "Revenue strategy, the forecast and the accountability, end to end",
      "The go-to-market motion, the pipeline and the team that runs it",
      "Marketing that actually feeds pipeline, not just activity",
      "The hard calls: who to hire, who to train, who to replace"]},
    {"h":"How it works","p":[
      "Week one I diagnose where deals stall and leak. Week two you have a plan and a real forecast. Week three I am running it. You get a senior operator who has done this 30-plus times on five continents, not a strategy deck that sits in a drawer."]},
    {"h":"Priced by how much of me you need","p":[
      "From a weekly advisor to a fully embedded CRO. The more of me you take, the more I own. The only thing that changes is how much of my week is on your business."],
     "ul":[
      "Advisor, $2,000 a month: about three hours a week, a standing strategy call plus access between calls",
      "Starter, $6,000 a month: two hours a day, every working day. What most companies choose",
      "Growth, $12,000 a month: half time, four hours a day, hands-on. Full-time and exclusive available on request"]},
    {"img": "/img/site/fractional-cro-portrait.jpg", "alt": "Tal Paperin, fractional CRO", "cap": "Senior revenue leadership, in the seat.", "portrait": True},
  ]},

 {"slug":"outsourced-sales","nav":"Outsourced Sales","h1":"Outsourced Sales Teams",
  "title":"Outsourced Sales Teams | Tal Paperin",
  "desc":"Outsource your entire sales function. Native-speaking SDRs and AEs, senior leadership and a VP, hired, trained and managed for you by KSW Solutions.",
  "eyebrow":"Service",
  "lead":"Hand off the whole revenue function. A complete sales team that lives outside your headcount, built, trained, managed and reported on for you.",
  "card":"Outsource sales entirely. A full team, native-speaking reps, leadership and a VP, run for you outside your headcount.",
  "sections":[
    {"h":"What you get","ul":[
      "Native-speaking SDRs and AEs for your target markets",
      "Senior sales leadership and a VP overseeing the motion",
      "A team we recruit, train, manage and report on daily",
      "The CRM, the playbook, the pipeline and the process, built and run"]},
    {"h":"When outsourced sales makes sense","p":[
      "When building an in-house team is too slow, too expensive, or too risky for your stage. You get a working revenue engine in weeks, not the 6-12 months it takes to hire and ramp one yourself, and none of the severance risk if the fit is wrong."]},
    {"h":"Who runs it","p":[
      "KSW Solutions, led by me. 20-plus years building and running B2B sales across the US, Europe, APAC and the former Soviet markets. Your sales function, owned by people who have done it before."]},
    {"img": "/img/site/outsourced-team.jpg", "alt": "Tal Paperin with a sales team", "cap": "A full team, run for you, outside your headcount."},
  ]},

 {"slug":"go-to-market-strategy","nav":"Go-To-Market Strategy","h1":"Go-To-Market Strategy",
  "title":"Go-To-Market Strategy Consultant | Tal Paperin",
  "desc":"A go-to-market strategy you can actually execute, including SaaS GTM. ICP, positioning, channels, playbook and a real forecast, then I help you run it.",
  "eyebrow":"Service",
  "lead":"Most GTM decks die in a drawer. I build a plan with targets and timelines, then lead the execution with you, for B2B and SaaS alike.",
  "card":"ICP, positioning, channels, playbook and a real forecast, including SaaS go-to-market, then I lead the execution, not just the slides.",
  "sections":[
    {"h":"What a real GTM plan includes","ul":[
      "A validated ICP, positioning and messaging, not a guess you wrote down once",
      "The right markets and channels for your stage",
      "An executable playbook: talk tracks, decision criteria, the outbound motion",
      "A real forecast with milestones, not a hope"]},
    {"h":"Strategy is not enough","p":[
      "I do not stop at the slide deck. I build the plan, then lead the execution with you, until you have pipeline, partners and first sales. From the high-level plan to the work in the field, I am there."]},
    {"h":"Including SaaS go-to-market","p":[
      "The same applies, sharpened, to software: positioning, the motion, the channel and the team built for the SaaS sale, including the long, technical, trust-based sale to enterprise, universities, research labs and pharma."]},
    {"h":"Across markets","p":[
      "North America, the EU, Eastern and Central Europe, and APAC. I have opened markets others wrote off, and I know the expensive mistakes before you make them."]},
    {"h":"Go deeper in the guides","links":[
      ["B2B go-to-market strategy guide", "/b2b-go-to-market-strategy"],
      ["B2B positioning and messaging", "/b2b-positioning-and-messaging"],
      ["How to choose your go-to-market motion", "/go-to-market-motion"]]},
    {"img": "/img/site/gtm-excel-london.jpg", "alt": "Tal Paperin at ExCeL London trade show", "cap": "Going to market means showing up where the market is."},
  ]},

 {"slug":"sales-team-building","nav":"Team Building","h1":"Sales Team Building and Training",
  "title":"Sales Team Building and Training | Tal Paperin",
  "desc":"Build your in-house sales team that actually closes. I hire, train and manage SDRs, AEs and BDs, and replace who can't.",
  "eyebrow":"Service",
  "lead":"Reps who can't close are not a people problem. They are a system problem. I build your in-house team and the system that makes them hit quota.",
  "card":"Build and train your in-house team: hire, train and manage SDRs, AEs and BDs on a playbook that makes them hit quota. Replace who can't, fast.",
  "sections":[
    {"h":"What I do","ul":[
      "Recruit and hire SDRs, AEs, BDs, post-sales and tech support",
      "Build a training plan tailored to your ICP and your GTM",
      "Manage the team day to day until they hit quota",
      "Replace who can't, fast, before they burn a year"]},
    {"h":"This builds your in-house team","p":[
      "This service builds and trains your own team, the people, the playbook and the standards that stay inside your company. If you would rather not build in-house at all and have the whole team run for you outside your headcount, that is outsourced sales, a separate engagement."]},
    {"h":"Go deeper on building a team","links":[
      ["How to build and scale a sales team","/how-to-build-a-sales-team"],
      ["How to build a sales compensation plan","/sales-compensation-plan"],
      ["How to set sales quotas reps can hit","/setting-sales-quotas"]]},
    {"img":"/img/site/training.jpg","alt":"Tal Paperin training a sales team","cap":"Training a sales team, hands-on, not from a slide deck."},
  ]},

 {"slug":"distributor-channel-recruitment","nav":"Channel & Distributors","h1":"Distributor and Channel Partner Recruitment",
  "title":"Distributor and Channel Partner Recruitment | Tal Paperin",
  "desc":"Open new territories through the right distributors and channel partners. I recruit, sign and manage them for the long term.",
  "eyebrow":"Service",
  "lead":"New markets open through partners. I find the real decision-makers, sign the distributors and channel partners that matter, and manage them for the long term.",
  "card":"Find the real decision-makers, sign distributors, resellers and channel partners, and manage them for the long term.",
  "sections":[
    {"h":"What I do","ul":[
      "Map the channel and the real decision-makers on the ground",
      "Recruit and sign distributors, resellers, integrators and channel partners",
      "Build the partner program that keeps them selling",
      "Manage the relationships for the long term, not just to the signature"]},
    {"h":"Proven on the ground","p":[
      "I have signed multiple distributors and retail chains across a region a global manufacturer had written off, and built distributor networks across the FSU, the EU and APAC. Partners are not a logo on a slide. They are revenue, if you pick and manage them right."]},
    {"img": "/img/site/distributor-booth.jpg", "alt": "Tal Paperin with channel partners at a trade show", "cap": "Meeting the distributors and partners that open new territories."},
  ]},

 {"slug":"market-entry","nav":"Market Entry & Global Markets","h1":"International Market Entry and Global Markets",
  "title":"International Market Entry and Global Expansion | Tal Paperin",
  "desc":"Break into new markets without the expensive mistakes. I have built sales, teams and subsidiaries across five continents. How I pick a market and win it.",
  "eyebrow":"Service",
  "lead":"Five continents. More than forty countries. Hundreds of cities, on the ground, not over email. Entering a new market is where companies burn the most money. I do not just enter a market, I help you choose the right one, then build and run it.",
  "card":"Pick the right market, then build and run the whole operation: sales, subsidiary, support and customer service. Built across five continents.",
  "sections":[
    {"h":"I choose the market, then build it","p":[
      "The most expensive mistake in expansion is entering the wrong market, fast. I start by assessing whether a market is even yours, the pain, the access, the willingness to pay, the competition, and then I build the operation only where it makes sense. Planning and execution, from the same person who answers for the number."]},
    {"h":"What I do","ul":[
      "Market-entry strategy and a milestone-by-milestone plan",
      "The right territories, channels and decision-makers",
      "Lead the negotiations and close the first deals personally",
      "Build the local presence, direct or through partners"]},
    {"h":"The full operation, not just the sale","ul":[
      "Sales teams: SDRs, AEs and leadership, hired, trained and managed",
      "Subsidiaries opened when customers or hiring require a local entity",
      "Tech support and customer service operations stood up and run",
      "Pricing, positioning and the go-to-market built for the local buyer",
      "The CRM, pipeline, forecast and accountability behind the number"]},
    {"h":"Done repeatedly, for multiple companies","p":[
      "This is not a one-time story. I have built, hired, trained and managed teams across these markets more than once, for more than one company, on five continents. Different products, different buyers, the same discipline. I also run B2G and complex public-sector deals across the globe."]},
    {"img":"/img/site/market-entry-expo.jpg","alt":"An international trade show floor","cap":"Global markets, up close. Where new business actually gets opened."},
    {"h":"Regions","links":[
      ["European Union","/blog/selling-b2b-in-the-eu"],
      ["Nordics","/blog/selling-b2b-in-the-nordics"],
      ["Central & Eastern Europe","/blog/selling-b2b-in-central-and-eastern-europe"],
      ["FSU","/blog/selling-b2b-in-the-fsu"],
      ["Asia-Pacific","/blog/selling-b2b-in-asia-pacific"],
      ["Australia & New Zealand","/blog/selling-b2b-in-australia-and-new-zealand"],
      ["South America","/blog/selling-b2b-in-south-america"],
      ["Central America","/blog/selling-b2b-in-central-america"],
      ["Africa","/blog/selling-b2b-in-africa"]]},
    {"h":"Countries","links":[
      ["United States","/blog/building-a-sales-operation-in-the-united-states"],
      ["United Kingdom","/blog/building-a-sales-operation-in-the-uk"],
      ["Germany","/blog/building-a-sales-operation-in-germany"],
      ["France","/blog/building-a-sales-operation-in-france"],
      ["Netherlands","/blog/building-a-sales-operation-in-the-netherlands"],
      ["Japan","/blog/building-a-sales-operation-in-japan"],
      ["China","/blog/building-a-sales-operation-in-china"],
      ["South Korea","/blog/building-a-sales-operation-in-south-korea"],
      ["Brazil","/blog/building-a-sales-operation-in-brazil"],
      ["Finland","/blog/selling-b2b-in-the-nordics"],["Poland","/blog/selling-b2b-in-central-and-eastern-europe"],["Romania","/blog/selling-b2b-in-central-and-eastern-europe"],["Hungary","/blog/selling-b2b-in-central-and-eastern-europe"],["Russia","/blog/selling-b2b-in-the-fsu"],["Taiwan","/blog/selling-b2b-in-asia-pacific"]]},
  ]},

 {"slug":"b2g-public-sector","nav":"B2G & Public Sector","h1":"B2G and Public-Sector Sales",
  "title":"B2G and Public-Sector Sales, RFIs and RFQs | Tal Paperin",
  "desc":"Win complex government and public-sector deals. RFIs, RFQs and B2G projects across the globe, run by someone who has actually closed them.",
  "eyebrow":"Service",
  "lead":"Government deals go to die in red tape. I run B2G and complex public-sector sales, RFIs, RFQs and government projects, across the globe.",
  "card":"Win complex government and public-sector deals: RFIs, RFQs and B2G projects, run by someone who has closed them.",
  "sections":[
    {"h":"When you need this","p":["Public-sector and government sales are a different sport: long cycles, formal processes, procurement gatekeepers and paperwork that kills momentum. Most commercial sales teams stall the moment an RFI lands."],
     "ul":["You are stuck in RFIs, RFQs and tenders that go nowhere","Your product fits the public sector but the process is foreign to you","You need someone who has navigated government procurement before"]},
    {"h":"What I do","ul":["Run B2G and complex public-sector deals end to end","Handle RFIs, RFQs, tenders and government projects across the globe","Map the real decision-makers and the procurement path","Position you to win, not just to submit"]},
    {"h":"Why B2G is its own game","p":["Selling to a government is not selling to a company. The buyer, the rules and the timeline are different, and the cost of getting it wrong is a year lost. I have run these deals internationally and I know where they stall."]},
    {"img":"/img/site/embassy-delegation.jpg","alt":"Tal Paperin with a US embassy delegation and ambassador","cap":"On the ground with a US embassy delegation. B2G runs on relationships and presence."},
  ]},

 {"slug":"contract-negotiation","nav":"Contract Negotiation","h1":"Contract Negotiation",
  "title":"B2B Contract Negotiation | Tal Paperin",
  "desc":"Take over the negotiation and close the complex, high-value agreements. I lead the deals that move the number.",
  "eyebrow":"Service",
  "lead":"Big deals slip away in the negotiation. I take over contract negotiation and close the complex, high-value agreements.",
  "card":"I take over the negotiation and close the complex, high-value deals that move the number.",
  "sections":[
    {"h":"When you need this","p":["Your biggest deals are the ones you can least afford to lose, and the ones most likely to stall in negotiation: pricing, terms, legal, procurement, and a buyer who senses hesitation."],
     "ul":["High-value deals keep slipping at the negotiation stage","Your team is strong at selling but not at closing the hard terms","You need a steady hand on the deals that matter most"]},
    {"h":"What I do","ul":["Take over the negotiation on your complex, high-value deals","Hold price and terms without losing the deal","Manage procurement, legal and the decision-makers","Close the agreements that actually move the number"]},
    {"h":"How it works","p":["I step into the live deal, get the full picture fast, and lead it to signature. Twenty years of closing complex B2B and B2G agreements across five continents means I have seen the tactics before they are used on you."]},
  ]},

 {"slug":"saas-sales","nav":"SaaS Sales","h1":"SaaS Sales and Go-To-Market",
  "title":"SaaS Sales and Go-To-Market | Tal Paperin",
  "desc":"Sell SaaS to a hard B2B buyer. Positioning, motion, channel and the team, built for software companies going to market.",
  "eyebrow":"Service",
  "lead":"Selling SaaS is its own discipline. I build the positioning, the motion, the channel and the team for software companies, including the long, technical, high-trust sale.",
  "card":"Positioning, motion, channel and team for software companies, built for the SaaS sale.",
  "sections":[
    {"h":"When you need this","p":["A great product is not a go-to-market. SaaS buyers are skeptical, technical and surrounded by alternatives, and a generic sales motion does not move them."],
     "ul":["Strong product, but the SaaS sales motion is not converting","You sell to technical or scientific buyers who need a different approach","You need a channel and a team built for software, not improvised"]},
    {"h":"What I do","ul":["Sharpen positioning, the ICP and the value proposition for a SaaS buyer","Build the outbound and the playbook the motion runs on","Build the channel: resellers, integrators and partners","Hire, train and manage the SaaS sales team"]},
    {"h":"Across the SaaS sale","p":["I have sold SaaS to startups, to enterprise, and to some of the hardest buyers there are, universities, research labs and pharma, where the sale is long, technical and built entirely on trust."]},
  ]},

 {"slug":"global-markets","nav":"Global Markets","h1":"Global Markets: Where I Build and Run Revenue",
  "title":"Global Markets: International Sales Expansion | Tal Paperin",
  "desc":"I have built and run sales teams, subsidiaries and support across five continents for multiple companies. Here is how I pick a market and build revenue in it.",
  "eyebrow":"Global",
  "lead":"Five continents. More than forty countries. Hundreds of cities, on the ground, not over email. I do not just enter a market, I help you choose the right one, then build and run it.",
  "card":"Built revenue across five continents. I help you pick the right market, then build and run the whole operation there.",
  "sections":[
    {"h":"I choose the market, then build it","p":[
      "The most expensive mistake in expansion is entering the wrong market, fast. I start by assessing whether a market is even yours, the pain, the access, the willingness to pay, the competition, and then I build the operation only where it makes sense. Planning and execution, from the same person who answers for the number."]},
    {"h":"The full operation, not just the sale","ul":[
      "Sales teams: SDRs, AEs and leadership, hired, trained and managed",
      "Subsidiaries opened when customers or hiring require a local entity",
      "Tech support and customer service operations stood up and run",
      "Pricing, positioning and the go-to-market built for the local buyer",
      "The CRM, pipeline, forecast and accountability behind the number"]},
    {"h":"Done repeatedly, for multiple companies","p":[
      "This is not a one-time story. I have built, hired, trained and managed teams across these markets more than once, for more than one company, on five continents. Different products, different buyers, the same discipline."]},
    {"h":"Regions","links":[
      ["European Union","/blog/selling-b2b-in-the-eu"],
      ["Nordics","/blog/selling-b2b-in-the-nordics"],
      ["Central & Eastern Europe","/blog/selling-b2b-in-central-and-eastern-europe"],
      ["FSU","/blog/selling-b2b-in-the-fsu"],
      ["Asia-Pacific","/blog/selling-b2b-in-asia-pacific"],
      ["Australia & New Zealand","/blog/selling-b2b-in-australia-and-new-zealand"],
      ["South America","/blog/selling-b2b-in-south-america"],
      ["Central America","/blog/selling-b2b-in-central-america"],
      ["Africa","/blog/selling-b2b-in-africa"]]},
    {"h":"Countries","links":[
      ["United States","/blog/building-a-sales-operation-in-the-united-states"],
      ["United Kingdom","/blog/building-a-sales-operation-in-the-uk"],
      ["Germany","/blog/building-a-sales-operation-in-germany"],
      ["France","/blog/building-a-sales-operation-in-france"],
      ["Netherlands","/blog/building-a-sales-operation-in-the-netherlands"],
      ["Japan","/blog/building-a-sales-operation-in-japan"],
      ["China","/blog/building-a-sales-operation-in-china"],
      ["South Korea","/blog/building-a-sales-operation-in-south-korea"],
      ["Brazil","/blog/building-a-sales-operation-in-brazil"],
      ["Finland","/blog/selling-b2b-in-the-nordics"],["Poland","/blog/selling-b2b-in-central-and-eastern-europe"],["Romania","/blog/selling-b2b-in-central-and-eastern-europe"],["Hungary","/blog/selling-b2b-in-central-and-eastern-europe"],["Russia","/blog/selling-b2b-in-the-fsu"],["Taiwan","/blog/selling-b2b-in-asia-pacific"]]},
  ]},
]


def esc(s):
    return html.escape(s, quote=True)


def img_size(src):
    """Return (width, height) for a local JPEG, or None. Pure stdlib so the
    generator never depends on PIL. Used to set width/height on content images
    (reserves layout space, prevents Cumulative Layout Shift)."""
    path = os.path.join(ROOT, src.lstrip("/"))
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if data[:2] != b"\xff\xd8":
        return None
    i, n = 2, len(data)
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
           0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while i + 9 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in sof:
            h = (data[i + 5] << 8) | data[i + 6]
            w = (data[i + 7] << 8) | data[i + 8]
            return (w, h)
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        i += 2 + ((data[i + 2] << 8) | data[i + 3])
    return None


def render_sections(svc):
    out = []
    for sec in svc["sections"]:
        if sec.get("h"):
            out.append("        <h2>%s</h2>" % esc(sec["h"]))
        for p in sec.get("p", []):
            out.append("        <p>%s</p>" % esc(p))
        if sec.get("img"):
            cap = ('<figcaption>%s</figcaption>' % esc(sec["cap"])) if sec.get("cap") else ""
            cls = "svc-photo portrait" if sec.get("portrait") else "svc-photo"
            dim = img_size(sec["img"])
            wh = (' width="%d" height="%d"' % dim) if dim else ""
            out.append('        <figure class="%s"><img src="%s" alt="%s"%s loading="lazy" />%s</figure>'
                       % (cls, sec["img"], esc(sec.get("alt", "")), wh, cap))
        if sec.get("ul"):
            out.append("        <ul>")
            for li in sec["ul"]:
                out.append("          <li>%s</li>" % esc(li))
            out.append("        </ul>")
        if sec.get("links"):
            out.append('        <div class="svc-links">')
            for text, href in sec["links"]:
                if href:
                    out.append('          <a href="%s">%s</a>' % (href, esc(text)))
                else:
                    out.append('          <span>%s</span>' % esc(text))
            out.append('        </div>')
        if sec.get("html"):
            out.append(sec["html"])
    return "\n".join(out)


def render_related(slug):
    links = ['<a href="/services/%s">%s</a>' % (s["slug"], esc(s["nav"]))
             for s in SERVICES if s["slug"] != slug][:3]
    return " &middot; ".join(links)


PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />
{hreflang}

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{h1} | Tal Paperin" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{h1} | Tal Paperin" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
  {faqld}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a></p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
{case}
{faq}
{cta}
        <div class="svc-related">Related services: {related} &middot; <a href="/blog/">Read the blog</a></div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''

INDEX = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Services: Fractional CRO, Outsourced Sales &amp; GTM | Tal Paperin</title>
  <meta name="description" content="How I fix and run revenue: fractional CRO, outsourced sales, go-to-market strategy, sales team building, channel and distributor recruitment, and international market entry." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/services/" />
  <link rel="alternate" hreflang="en" href="{site}/services/" />
  <link rel="alternate" hreflang="he" href="{site}/he/services/" />
  <link rel="alternate" hreflang="x-default" href="{site}/services/" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{site}/services/" />
  <meta property="og:title" content="Services | Tal Paperin" />
  <meta property="og:description" content="Fractional CRO, outsourced sales, go-to-market, team building, channel recruitment and market entry." />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Services | Tal Paperin" />
  <meta name="twitter:description" content="Fractional CRO, outsourced sales, go-to-market, team building, channel recruitment and market entry." />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Services</p>
        <h1>What I do.</h1>
        <p class="lead">The ways I fix and run revenue. Pick the one that matches your problem, or just tell me where it hurts and I will point you to the right one.</p>
      </div>
      <div class="svc-grid">
{cards}
      </div>
      <p style="text-align:center;margin-top:34px"><a class="btn btn-secondary" href="/pricing">See pricing &rarr;</a></p>
      <h2 class="cases-recs-h">On the ground, on five continents</h2>
{gallery}
    </div>
  </main>

{footer}
</body>
</html>
'''


# --- Hebrew (RTL) ----------------------------------------------------------

HE_FONTS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml" />\n' '  <link rel="icon" href="/favicon.ico" sizes="any" />\n' '  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n' '  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            '  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800;900&'
            'family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet" />')

HE_NAV = '''  <a class="skip-link" href="#main">Skip to content</a>
  <nav class="site">
    <div class="inner">
      <a class="brand" href="/he/">טל פאפרין</a>
      <div class="navlinks">
        <a href="/he/">בית</a>
        <a href="/he/about">אודות</a>
        <a href="/he/services/">שירותים</a>
        <a href="/he/pricing">תמחור</a>
        <a href="/he/case-studies">מקרי מבחן</a>
        <a href="/he/recommendations">המלצות</a>
        <a href="/he/blog/">בלוג</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/" hreflang="en" aria-label="Switch to English">''' + FLAG_US + '''</a>
        <a class="btn btn-primary" href="/he/contact">בואו נדבר</a>
        <button class="navtoggle" aria-label="תפריט" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

HE_FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 טל פאפרין. כל הזכויות שמורות. &middot; <a href="/he/guides">מדריכים</a></span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="אימייל"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="טלפון"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="לינקדאין"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="שיחה בוואטסאפ">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
  </script>
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
</script>'''

HE_CTA = '''      <div class="cta-box">
        <h3>ספרו לי איפה המכירות נתקעו. אני אגיד לכם למה.</h3>
        <p>שיחה של 15 דקות, בלי ניסיונות מכירה. תצאו ממנה עם לפחות דבר אחד פרקטי לתקן, בין אם נעבוד יחד ובין אם לא.</p>
        <a class="btn btn-primary" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">תיאום שיחה של 15 דקות</a>
        <a class="btn btn-secondary" href="https://wa.me/972545308119?text=%D7%94%D7%99%D7%99%20%D7%98%D7%9C%2C%20%D7%94%D7%92%D7%A2%D7%AA%D7%99%20%D7%93%D7%A8%D7%9A%20%D7%94%D7%90%D7%AA%D7%A8%20%D7%95%D7%90%D7%A9%D7%9E%D7%97%20%D7%9C%D7%93%D7%91%D7%A8." target="_blank" rel="noopener">דברו איתי בוואטסאפ</a>
      </div>'''

HE_SERVICES = [
 {"slug":"pay-per-meeting","nav":"תשלום לפי פגישה","h1":"פגישות מכירה B2B בתשלום לפי פגישה",
  "title":"פגישות מכירה B2B בתשלום לפי פגישה | טל פאפרין",
  "desc":"אתם משלמים על פגישות המכירה שאנחנו קובעים, לא על מיילים או רשימות. אנחנו מגדירים את ה-ICP, מוצאים את האנשים ושמים פגישות מוכשרות ביומן שלכם.",
  "eyebrow":"שירות",
  "lead":"אתם צריכים פגישות מכירה. אני משיג לכם אותן. לא עוד ריטיינר על פעילות, אתם משלמים לפי מספר הפגישות המוכשרות שאנחנו באמת קובעים ביומן שלכם.",
  "card":"אאוטבאונד שמחייב לפי תוצאה. אתם משלמים על פגישות B2B מוכשרות שאנחנו קובעים, לא על מיילים, רשימות או לידים.",
  "sections":[
    {"h":"אתם צריכים פגישות, לא עוד הרצאה על פייפליין","p":[
      "רוב החברות לא צריכות עוד יועץ שאומר להן שהן צריכות יותר פייפליין. הן צריכות פגישות. זה כל מה שהשירות הזה עושה.",
      "אתם אומרים לנו מה אתם מוכרים ולמי אתם רוצים למכור. יחד אנחנו מגדירים בדיוק איך נראה פרוספקט רלוונטי: תעשייה, גיאוגרפיה, גודל חברה, סוג חברה והאנשים בתוך אותן חברות שאתם רוצים לפגוש. ואז אנחנו הולכים להשיג אותם.",
      "אתם לא משלמים לי כדי לשלוח מיילים. לא משלמים לי על לידים. לא משלמים לי על רשימות. אתם משלמים לפי מספר פגישות המכירה שאנחנו קובעים. פשוט."]},
    {"h":"איך זה עובד","ul":[
      "אתם אומרים לנו את מי אתם רוצים לפגוש. אנחנו מסכמים על ה-ICP והפרסונות, למשל חברות שירותים פיננסיים בארה״ב, 500+ עובדים, בכיוון CIO, CTO ו-VP Engineering. אתם מאשרים. זה מי שאנחנו הולכים אליו.",
      "אנחנו עושים את העבודה. מוצאים את החברות, מוצאים את האנשים, בונים את הרשימות, יוצרים ומריצים את הפנייה, עושים מעקב ומנהלים את כל התהליך. SDRs, חוקרים, מייל, לינקדאין, טלפון, דאטה וכלים: זו הבעיה שלנו, לא שלכם.",
      "אנחנו שמים פגישות ביומן שלכם. כשמישהו שתואם ל-ICP ולפרסונה שסיכמנו אומר כן לתאריך ושעה, עשינו את העבודה שלנו. אתם לוקחים את הפגישה, מריצים דיסקברי, דמו, כישור, משא ומתן וסגירה. אנחנו יוצרים את השיחה, אתם ממשיכים משם."]},
    {"h":"מה אתם משלמים","p":[
      "דמי הקמה חד פעמיים משיקים את הקמפיין. אחרי זה, מה שאתם משלמים תלוי בכמה פגישות אנחנו באמת קובעים. חודש חלש, אתם משלמים פחות. יותר פגישות, אתם משלמים יותר. זה מכוון: אתם לא אמורים לשלם על שלוש פגישות אותו דבר כמו על חמש עשרה."],
     "html":PPM_PRICE_HE},
    {"h":"מה נחשב פגישה","p":[
      "אין קאץ׳, אבל אנחנו מסכמים מה זו פגישה לפני שמתחילים. אתם מאשרים את ה-ICP ואת הפרסונות. אנחנו הולכים אליהם. אם מישהו שתואם לקריטריונים מסכים להיפגש ואנחנו קובעים תאריך ושעה, זו פגישה שנקבעה.",
      "אנחנו סופרים פגישות שנקבעו, לא פגישות שהתקיימו. אם הפרוספקט אחר כך דוחה, מבטל או לא מגיע, זה לא מבטל את העבודה שיצרה את הפגישה, ולכן הפגישה עדיין נספרת ועדיין משולמת.",
      "עם זאת, אני לא כאן כדי לחייב אתכם על שם ביומן שלא מגיע. אם פגישה שנקבעה לא מתקיימת או מבוטלת, אנחנו קובעים אותה מחדש בלי חיוב נוסף. שיהיה ברור: הפגישה המקורית עדיין נספרת ועדיין משולמת, הקביעה מחדש היא בונוס מצדנו, כי מה שאתם באמת קונים זו השיחה, ואנחנו ממשיכים לעבוד עד שתקבלו אותה.",
      "ופגישה שנקבעה היא לא מכירה מובטחת. אנחנו אחראים להביא את האדם הנכון להסכים לשיחת מכירה. מה שקורה במהלך השיחה ואחריה תלוי במוצר, בהצעה, בתהליך ובאנשי המכירות שלכם."]},
    {"h":"למה לשלם ככה","p":[
      "כי זה מיישר אותנו. שירות SDR מסורתי גובה ריטיינר קבוע, מקצה אנשים, שולח אלפי מיילים ושולח לכם דוחות פעילות. אולי תקבלו פגישות, אולי לא, ואתם משלמים אותו דבר כך או כך.",
      "אני מעדיף שיחה פשוטה יותר: כמה פגישות קבענו? שלוש, אתם משלמים את מדרגת שלוש הפגישות. שבע עשרה, אתם משלמים את מדרגת ה-15+. התמריץ ברור. ככל שנשיג לכם יותר פגישות, כך נרוויח יותר."]},
    {"h":"למה יש דמי הקמה","p":[
      "לפני שאנחנו יכולים לקבוע פגישות אנחנו בונים את הקמפיין. השבועיים שלושה הראשונים כוללים הגדרת ICP ופרסונות, בניית דאטה על פרוספקטים, יצירת מסרים, הכנת הפנייה, הקמת התשתית והכשרת האנשים המעורבים. אחרי שזה נעשה, המיקוד פשוט: לקבוע פגישות."]},
    {"h":"למי זה מתאים, ולמי לא","p":[
      "זה עובד לחברות B2B שכבר יש להן מה למכור וצריכות יותר שיחות. אולי יש לכם צוות מכירות, אולי AE אחד, אולי אתם עדיין מובלים על ידי המייסד. אולי אתם נכנסים לשוק חדש או פשוט חסר לכם פייפליין. מה שחשוב זה שאתם יודעים מה לעשות כשמישהו נותן לכם פגישה."],
     "ul":[
      "התאמה טובה: אתם יכולים לקחת פרוספקט רלוונטי משיחה ראשונה דרך דיסקברי, הצעה וסגירה",
      "מוקדם מדי: אתם עדיין לא יודעים מה אתם מוכרים או מי קונה",
      "לא מתאים: אתם מצפים שכל פגישה תהפוך להזדמנות, או רוצים ששירות אחד גם יקבע וגם יסגור בשבילכם"]},
    {"h":"למה KSW","p":[
      "ביליתי יותר מ-20 שנה בבניית וניהול מכירות B2B ברחבי העולם: תוכנה, SaaS, חומרה, שירותים ועסקאות אנטרפרייז מורכבות. בניתי צוותים מאפס, גייסתי וניהלתי SDRs ו-AEs, ופתחתי שווקים בינלאומיים. אז כשאנחנו הולכים להשיג לכם פגישות, זה לא תרגיל גנרי של יצירת לידים. אנחנו מבינים מכירות, מבינים מי צריך להיות בחדר, ויודעים שהסיבה היחידה להריץ אאוטבאונד היא ליצור שיחות מכירה אמיתיות.",
      "תגידו לי למי אתם רוצים למכור ואנחנו נביא אתכם מולם. בלי SDR לגייס, בלי צוות לנהל, בלי טכנולוגיה להבין, בלי רשימות לבנות. אנחנו קובעים את הפגישות. אתם מוכרים."]}]},
 {"slug":"fractional-cmo","nav":"סמנכ״ל שיווק","h1":"סמנכ״ל שיווק במיקור חוץ והובלת שיווק",
  "title":"סמנכ״ל שיווק במיקור חוץ | טל פאפרין",
  "desc":"הובלת שיווק בכירה לפי דרישה: פיקוח בכיר או בעלות מלאה כסמנכ״ל שיווק, כך שהשיווק והמכירות פועלים כמנוע הכנסות אחד.",
  "eyebrow":"שירות",
  "lead":"שיווק שבאמת מזין מכירות. פיקוח בכיר או בעלות מלאה על פונקציית השיווק, מיושר לתוצאות, בלי משכורת של סמנכ״ל שיווק במשרה מלאה.",
  "card":"הובלת שיווק בכירה, פיקוח או בעלות מלאה, מנוהלת כמנוע אחד עם המכירות.",
  "sections":[
    {"h":"מתי צריך סמנכ״ל שיווק במיקור חוץ","p":["השיווק רץ אבל אף אחד בכיר לא אחראי אם הוא באמת מייצר פייפליין. או שיש לכם עושה מלאכה מוכשר שצריך כיוון, תעדוף ואחריותיות. זה הפער שסמנכ״ל שיווק במיקור חוץ ממלא, בלי משכורת ניהולית מלאה."],
     "ul":["מוציאים על שיווק אבל לא מצליחים לקשור אותו להכנסות","איש שיווק מוכשר צריך כיוון בכיר וסטנדרטים","מכירות ושיווק מאשימים זה את זה במקום לעבוד כמנוע אחד","אתם נכנסים לשוק חדש וצריכים מיצוב וביקוש מאפס"]},
    {"h":"על מה אני אחראי","p":["שתי רמות, לפי מה שאתם צריכים. פיקוח: סקירה בכירה של תוכניות, עדיפויות ותקציב, עם הכוונה ברורה על מה לרדוף, להשהות או לעצור. בעלות מלאה: אני מוביל את פונקציית השיווק, את העדיפויות ואת האנשים, ואחראי על התוצאות."],
     "ul":["מיצוב, מסרים ותוכנית יצירת ביקוש","עדיפויות, תקציב ומה להפסיק לעשות","תיאום בין שיווק, מכירות וההנהלה הבכירה","בעל אחריות אחד לביצועי השיווק"]},
    {"h":"שיווק ומכירות כמנוע אחד","p":["רוב החברות מריצות שיווק ומכירות כשתי מחלקות שמאשימות זו את זו. אני מריץ אותן כמנוע הכנסות אחד, כך שהלידים שהשיווק מייצר הם לידים שהמכירות באמת יכולות לסגור. השירות ניתן יחד עם KSW Solutions, החברה שאני מוביל."]}]},
 {"slug":"fractional-cro","nav":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ","h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ",
  "title":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ | טל פאפרין",
  "desc":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ שלוקח אחריות על התוצאות. אסטרטגיה, צוות, פייפליין ותחזית, בלי גיוס יקר של משרה מלאה.",
  "eyebrow":"שירות",
  "lead":"מנהיגות הכנסות בכירה שלוקחת אחריות על התוצאות. בלי משכורת של רבע מיליון דולר ובלי התחייבות ארוכת טווח.",
  "card":"אני לוקח אחריות על ההכנסות ועל התוצאות. שלב הביניים שרוב החברות בוחרות בו.",
  "sections":[
    {"h":"מתי צריך סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ?",
     "p":["אתם צריכים שיקול דעת ברמת סמנכ״ל מכירות ופיתוח עסקי, אבל הנפח עדיין לא מצדיק משרה מלאה. או שאתם צריכים תוצאות עכשיו ולא יכולים לחכות שני רבעונים שמישהו חדש יתחמם. בדיוק לפער הזה נכנס סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ."],
     "ul":["המכירות נתקעו ואף אחד לא באמת אחראי על התוצאות","אתם בצמיחה וצריכים מנהיג עוד לפני שאפשר להצדיק סמנכ״ל מכירות ופיתוח עסקי במשרה מלאה","סמנכ״ל מכירות ופיתוח עסקי שכיר עולה רבע מיליון דולר ומעלה בשנה, עם חודשים של גיוס וחימום וסיכוני פיצויים"]},
    {"h":"על מה אני לוקח אחריות",
     "ul":["אסטרטגיית ההכנסות, התחזית והאחריות, מקצה לקצה","תנועת ה-Go-to-Market, הפייפליין והצוות שמריץ אותם","שיווק שבאמת מזין את הפייפליין, לא רק מייצר פעילות","ההחלטות הקשות: את מי לגייס, את מי להכשיר ואת מי להחליף"]},
    {"h":"איך זה עובד",
     "p":["בשבוע הראשון אני מאבחן איפה העסקאות נתקעות ודולפות. בשבוע השני יש לכם תוכנית ותחזית אמיתית. בשבוע השלישי אני כבר מריץ אותה. אתם מקבלים מנהל מנוסה שעשה את זה יותר מ-30 פעם בחמש יבשות, לא עוד מצגת אסטרטגיה שנשארת במגירה."]},
    {"h":"מתומחר לפי כמה ממני אתם צריכים",
     "p":["מיועץ שבועי ועד סמנכ״ל הכנסות מוטמע במלואו. ככל שאתם לוקחים יותר ממני, אני לוקח יותר אחריות. הדבר היחיד שמשתנה הוא כמה מהשבוע שלי בעסק שלכם."],
     "ul":["Advisor, 2,000 דולר בחודש: כשלוש שעות בשבוע, שיחת אסטרטגיה קבועה וגישה אליי בין השיחות","Starter, 6,000 דולר בחודש: שעתיים ביום, בכל יום עבודה. מה שרוב החברות בוחרות","Growth, 12,000 דולר בחודש: חצי משרה, ארבע שעות ביום, בידיים. משרה מלאה ובלעדית זמינה לפי בקשה"]},
    {"img": "/img/site/fractional-cro-portrait.jpg", "alt": "טל פאפרין, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ", "cap": "מנהיגות הכנסות בכירה, בידיים.", "portrait": True},
  ]},

 {"slug":"outsourced-sales","nav":"מכירות במיקור חוץ","h1":"צוות מכירות במיקור חוץ",
  "title":"צוות מכירות במיקור חוץ | טל פאפרין",
  "desc":"מיקור חוץ מלא של מערך המכירות. אנשי SDR ו-AE דוברי שפת אם, הובלה בכירה ומנהל VP, מגויסים, מוכשרים ומנוהלים עבורכם על ידי KSW Solutions.",
  "eyebrow":"שירות",
  "lead":"להעביר את כל מערך ההכנסות החוצה. צוות מכירות שלם שחי מחוץ למצבת כוח האדם שלכם, נבנה, מוכשר, מנוהל ומדווח עבורכם.",
  "card":"מיקור חוץ מלא של המכירות. צוות שלם, אנשי מכירות דוברי שפת אם, הובלה ו-VP, שמורץ עבורכם מחוץ למצבת כוח האדם.",
  "sections":[
    {"h":"מה אתם מקבלים",
     "ul":["אנשי SDR ו-AE דוברי שפת אם לשווקי היעד שלכם","הובלת מכירות בכירה ומנהל VP שמפקח על התנועה","צוות שאנחנו מגייסים, מכשירים, מנהלים ומדווחים עליו מדי יום","ה-CRM, ה-Playbook, הפייפליין והתהליך, בנויים ומורצים"]},
    {"h":"מתי מיקור חוץ של מכירות הוא המהלך הנכון",
     "p":["כשבניית צוות פנימי איטית מדי, יקרה מדי או מסוכנת מדי לשלב שלכם. אתם מקבלים מנוע מכירות עובד תוך שבועות, לא ב-6 עד 12 חודשים של גיוס וחימום, ובלי סיכון הפיצויים אם ההתאמה לא נכונה."]},
    {"h":"מי מריץ את זה",
     "p":["KSW Solutions, בהובלתי. מעל 20 שנה של בנייה וניהול מכירות B2B בארה״ב, אירופה, APAC והשווקים הפוסט-סובייטיים. מערך המכירות שלכם, בידיים של מי שכבר עשה את זה."]},
    {"img": "/img/site/outsourced-team.jpg", "alt": "טל פאפרין עם צוות מכירות", "cap": "צוות שלם שמורץ עבורכם, מחוץ למצבת כוח האדם."},
  ]},

 {"slug":"go-to-market-strategy","nav":"אסטרטגיית GTM","h1":"אסטרטגיית Go-To-Market",
  "title":"אסטרטגיית Go-To-Market ותוכנית שיווק בינלאומית | טל פאפרין",
  "desc":"אסטרטגיית Go-To-Market שאפשר באמת לבצע, כולל GTM ל-SaaS. ICP, מיצוב, ערוצים, Playbook ותחזית אמיתית, ואז אני מוביל איתכם את הביצוע.",
  "eyebrow":"שירות",
  "lead":"רוב מצגות ה-GTM מתות במגירה. אני בונה תוכנית עם יעדים ולוחות זמנים, ואז מוביל איתכם את הביצוע, גם ל-B2B וגם ל-SaaS.",
  "card":"ICP, מיצוב, ערוצים, Playbook ותחזית אמיתית, כולל Go-To-Market ל-SaaS, ואז אני מוביל את הביצוע, לא רק את השקפים.",
  "sections":[
    {"h":"מה כוללת תוכנית GTM אמיתית",
     "ul":["ICP מתוקף, מיצוב ומסרים, לא ניחוש שרשמתם פעם אחת","השווקים והערוצים הנכונים לשלב שלכם","Playbook בר-ביצוע: תסריטי שיחה, קריטריונים להחלטה ותנועת אאוטבאונד","תחזית אמיתית עם אבני דרך, לא תקווה"]},
    {"h":"אסטרטגיה זה לא מספיק",
     "p":["אני לא עוצר במצגת. אני בונה את התוכנית, ואז מוביל איתכם את הביצוע, עד שיש פייפליין, שותפים ומכירות ראשונות. מהתכנון הגבוה ועד העבודה בשטח, אני שם."]},
    {"h":"כולל Go-To-Market ל-SaaS",
     "p":["אותו דבר, מחודד, לתוכנה: מיצוב, תנועה, ערוץ וצוות שנבנים למכירת ה-SaaS, כולל המכירה הארוכה, הטכנית ועתירת האמון לארגונים גדולים, אוניברסיטאות, מעבדות מחקר וחברות פארמה."]},
    {"h":"לרוחב השווקים",
     "p":["צפון אמריקה, האיחוד האירופי, מזרח ומרכז אירופה ו-APAC. פתחתי שווקים שאחרים מחקו, ואני מכיר את הטעויות היקרות לפני שאתם עושים אותן."]},
    {"h":"להעמיק במדריכים","links":[
      ["מדריך אסטרטגיית Go-To-Market ל-B2B", "/he/b2b-go-to-market-strategy"],
      ["מיצוב ומסר ל-B2B", "/he/b2b-positioning-and-messaging"],
      ["איך בוחרים מהלך הליכה לשוק", "/he/go-to-market-motion"]]},
    {"img": "/img/site/gtm-excel-london.jpg", "alt": "טל פאפרין בתערוכת ExCeL לונדון", "cap": "Go-To-Market זה להגיע לאן שהשוק נמצא."},
  ]},

 {"slug":"sales-team-building","nav":"בניית צוות","h1":"בניית והכשרת צוות מכירות",
  "title":"בניית והכשרת צוות מכירות | טל פאפרין",
  "desc":"לבנות את צוות המכירות הפנימי שלכם שבאמת סוגר. אני מגייס, מכשיר ומנהל SDRs, AEs ו-BDs, ומחליף את מי שלא מתאים.",
  "eyebrow":"שירות",
  "lead":"אנשי מכירות שלא סוגרים זו לא בעיה של אנשים. זו בעיה של שיטה. אני בונה את הצוות הפנימי שלכם ואת השיטה שגורמים להם לפגוע ביעד.",
  "card":"בנייה והכשרה של הצוות הפנימי שלכם: גיוס, הכשרה וניהול של SDRs, AEs ו-BDs על Playbook שמביא אותם ליעד. החלפה מהירה של מי שלא מתאים.",
  "sections":[
    {"h":"מה אני עושה",
     "ul":["גיוס והשמה של SDRs, AEs, BDs, שירות שלאחר מכירה ותמיכה טכנית","בניית תוכנית הכשרה מותאמת ל-ICP ול-GTM שלכם","ניהול הצוות יום-יום עד שהוא פוגע ביעד","החלפה מהירה של מי שלא מתאים, לפני שהוא שורף שנה"]},
    {"h":"זה בונה את הצוות הפנימי שלכם",
     "p":["השירות הזה בונה ומכשיר את הצוות שלכם, האנשים, ה-Playbook והסטנדרטים שנשארים בתוך החברה. אם אתם מעדיפים לא לבנות פנימית בכלל ולקבל צוות שלם שמורץ עבורכם מחוץ למצבת כוח האדם, זה מכירות במיקור חוץ, התקשרות נפרדת."]},
    {"h":"העמיקו בבניית צוות","links":[
      ["איך בונים ומרחיבים צוות מכירות","/he/how-to-build-a-sales-team"],
      ["איך בונים תוכנית תגמול מכירות","/he/sales-compensation-plan"],
      ["איך קובעים יעדי מכירות שאפשר לעמוד בהם","/he/setting-sales-quotas"]]},
    {"img":"/img/site/training.jpg","alt":"טל פאפרין מכשיר צוות מכירות","cap":"הכשרת צוות מכירות, בידיים, לא ממצגת."},
  ]},

 {"slug":"distributor-channel-recruitment","nav":"מפיצים וערוצים","h1":"איתור וגיוס מפיצים וערוצי הפצה",
  "title":"איתור וגיוס מפיצים וערוצי הפצה | טל פאפרין",
  "desc":"לפתוח טריטוריות חדשות דרך המפיצים ושותפי ההפצה הנכונים. אני מאתר, מחתים ומנהל אותם לטווח הארוך.",
  "eyebrow":"שירות",
  "lead":"שווקים חדשים נפתחים דרך שותפים. אני מאתר את מקבלי ההחלטות האמיתיים, מחתים את המפיצים ושותפי ההפצה שמשנים את התמונה, ומנהל אותם לטווח הארוך.",
  "card":"איתור מקבלי ההחלטות האמיתיים, החתמת מפיצים, ריסלרים ושותפי ערוץ, וניהול שלהם לטווח הארוך.",
  "sections":[
    {"h":"מה אני עושה",
     "ul":["מיפוי הערוץ ומקבלי ההחלטות האמיתיים בשטח","איתור והחתמת מפיצים, ריסלרים, אינטגרטורים ושותפי ערוץ","בניית תוכנית השותפים שגורמת להם להמשיך למכור","ניהול הקשרים לטווח הארוך, לא רק עד החתימה"]},
    {"h":"מוכח בשטח",
     "p":["החתמתי מספר מפיצים ורשתות קמעונאות באזור שיצרן גלובלי כבר מחק, ובניתי רשתות מפיצים ב-FSU, באיחוד האירופי וב-APAC. שותפים הם לא לוגו על שקף. הם הכנסות, אם בוחרים ומנהלים אותם נכון."]},
    {"img": "/img/site/distributor-booth.jpg", "alt": "טל פאפרין עם שותפי ערוץ בתערוכה", "cap": "פגישה עם המפיצים והשותפים שפותחים טריטוריות חדשות."},
  ]},

 {"slug":"market-entry","nav":"חדירה לשווקים ושווקים גלובליים","h1":"חדירה לשווקים בינלאומיים ושווקים גלובליים",
  "title":"חדירה לשווקים בינלאומיים והתרחבות גלובלית | טל פאפרין",
  "desc":"לפרוץ לשווקים חדשים בלי הטעויות היקרות. בניתי וניהלתי מכירות, צוותים, חברות בנות ותמיכה בחמש יבשות, שוב ושוב ולמספר חברות. הנה איך אני בוחר שוק ובונה אותו.",
  "eyebrow":"שירות",
  "lead":"חמש יבשות. יותר מארבעים מדינות. מאות ערים, בשטח, לא מהאימייל. כניסה לשוק חדש זה המקום שבו חברות שורפות הכי הרבה כסף. אני לא רק נכנס לשוק, אני עוזר לכם לבחור את הנכון, ואז בונה ומנהל אותו.",
  "card":"בוחרים את השוק הנכון, ואז בונים ומנהלים את כל המערך: מכירות, חברה בת, תמיכה ושירות לקוחות. נבנה בחמש יבשות.",
  "sections":[
    {"h":"קודם בוחרים שוק, אחר כך בונים אותו",
     "p":["הטעות היקרה ביותר בהתרחבות היא להיכנס מהר לשוק הלא נכון. אני מתחיל בלשפוט אם השוק בכלל שלכם, הכאב, הנגישות, הנכונות לשלם, התחרות, ואז בונה את המערך רק איפה שזה הגיוני. תכנון וביצוע, מאותו אדם שאחראי על התוצאות."]},
    {"h":"מה אני עושה",
     "ul":["אסטרטגיית חדירה ותוכנית לפי אבני דרך","הטריטוריות, הערוצים ומקבלי ההחלטות הנכונים","הובלת המשא ומתן וסגירת העסקאות הראשונות באופן אישי","בניית נוכחות מקומית, ישירה או דרך שותפים"]},
    {"h":"כל המערך, לא רק המכירה",
     "ul":["צוותי מכירות: SDR, AE והובלה, מגויסים, מוכשרים ומנוהלים","חברות בנות שנפתחות כשלקוחות או גיוס דורשים ישות מקומית","מערכי תמיכה טכנית ושירות לקוחות שמוקמים ומנוהלים","תמחור, מיצוב ו-Go-To-Market שנבנים לקונה המקומי","ה-CRM, הפייפליין, התחזית והאחריות על התוצאות"]},
    {"h":"נעשה שוב ושוב, למספר חברות",
     "p":["זה לא סיפור חד פעמי. בניתי, גייסתי, הכשרתי וניהלתי צוותים בשווקים האלה יותר מפעם אחת, למספר חברות, בחמש יבשות. מוצרים שונים, קונים שונים, אותה משמעת. אני גם מנהל עסקאות B2G ומורכבות מול המגזר הציבורי בכל העולם."]},
    {"img":"/img/site/market-entry-expo.jpg","alt":"רחבת תערוכה בינלאומית","cap":"שווקים גלובליים מקרוב. איפה שבאמת פותחים עסקים חדשים."},
    {"h":"אזורים","links":[
      ["האיחוד האירופי","/he/blog/selling-b2b-in-the-eu"],
      ["מדינות נורדיות","/he/blog/selling-b2b-in-the-nordics"],
      ["מרכז ומזרח אירופה","/he/blog/selling-b2b-in-central-and-eastern-europe"],
      ["ברית המועצות לשעבר","/he/blog/selling-b2b-in-the-fsu"],
      ["אסיה-פסיפיק","/he/blog/selling-b2b-in-asia-pacific"],
      ["אוסטרליה וניו זילנד","/he/blog/selling-b2b-in-australia-and-new-zealand"],
      ["דרום אמריקה","/he/blog/selling-b2b-in-south-america"],
      ["מרכז אמריקה","/he/blog/selling-b2b-in-central-america"],
      ["אפריקה","/he/blog/selling-b2b-in-africa"]]},
    {"h":"מדינות","links":[
      ["ארצות הברית","/he/blog/building-a-sales-operation-in-the-united-states"],
      ["בריטניה","/he/blog/building-a-sales-operation-in-the-uk"],
      ["גרמניה","/he/blog/building-a-sales-operation-in-germany"],
      ["צרפת","/he/blog/building-a-sales-operation-in-france"],
      ["הולנד","/he/blog/building-a-sales-operation-in-the-netherlands"],
      ["יפן","/he/blog/building-a-sales-operation-in-japan"],
      ["סין","/he/blog/building-a-sales-operation-in-china"],
      ["דרום קוריאה","/he/blog/building-a-sales-operation-in-south-korea"],
      ["ברזיל","/he/blog/building-a-sales-operation-in-brazil"],
      ["פינלנד","/he/blog/selling-b2b-in-the-nordics"],["פולין","/he/blog/selling-b2b-in-central-and-eastern-europe"],["רומניה","/he/blog/selling-b2b-in-central-and-eastern-europe"],["הונגריה","/he/blog/selling-b2b-in-central-and-eastern-europe"],["רוסיה","/he/blog/selling-b2b-in-the-fsu"],["טאיוואן","/he/blog/selling-b2b-in-asia-pacific"]]},
  ]},

 {"slug":"b2g-public-sector","nav":"B2G ומגזר ציבורי","h1":"מכירות B2G ולמגזר הציבורי",
  "title":"מכירות B2G ולמגזר הציבורי, מכרזים, RFIs ו-RFQs | טל פאפרין",
  "desc":"לזכות בעסקאות מורכבות מול ממשלות והמגזר הציבורי. מכרזים, RFIs, RFQs ופרויקטים ממשלתיים בכל העולם, על ידי מי שכבר סגר כאלה.",
  "eyebrow":"שירות",
  "lead":"עסקאות ממשלתיות הולכות למות בבירוקרטיה. אני מנהל מכירות B2G ועסקאות מורכבות מול המגזר הציבורי, מכרזים, RFIs, RFQs ופרויקטים ממשלתיים, בכל העולם.",
  "card":"לזכות בעסקאות מורכבות מול ממשלות והמגזר הציבורי: מכרזים, RFIs ו-RFQs, על ידי מי שכבר סגר כאלה.",
  "sections":[
    {"h":"מתי צריך את זה","p":["מכירה למגזר הציבורי ולממשלות היא משחק אחר לגמרי: מחזורים ארוכים, תהליכים פורמליים, שומרי סף ברכש ובירוקרטיה שהורגת מומנטום. רוב צוותי המכירות המסחריים נתקעים ברגע שמגיע RFI."],
     "ul":["אתם תקועים במכרזים, RFIs ו-RFQs שלא מתקדמים","המוצר שלכם מתאים למגזר הציבורי אבל התהליך זר לכם","אתם צריכים מישהו שכבר ניווט ברכש ממשלתי"]},
    {"h":"מה אני עושה","ul":["ניהול עסקאות B2G ומורכבות מול המגזר הציבורי מקצה לקצה","טיפול במכרזים, RFIs, RFQs ופרויקטים ממשלתיים בכל העולם","מיפוי מקבלי ההחלטות האמיתיים ונתיב הרכש","מיצוב שלכם כדי לזכות, לא רק כדי להגיש"]},
    {"h":"למה B2G זה משחק אחר","p":["מכירה לממשלה היא לא מכירה לחברה. הקונה, הכללים ולוחות הזמנים שונים, והמחיר של טעות הוא שנה שאבדה. ניהלתי את העסקאות האלה בעולם ואני יודע איפה הן נתקעות."]},
    {"img":"/img/site/embassy-delegation.jpg","alt":"טל פאפרין עם משלחת שגרירות ארה״ב","cap":"בשטח עם משלחת שגרירות ארה״ב. B2G רץ על יחסים ונוכחות."},
  ]},

 {"slug":"contract-negotiation","nav":"משא ומתן","h1":"ניהול משא ומתן על חוזים",
  "title":"ניהול משא ומתן על חוזים B2B | טל פאפרין",
  "desc":"לקחת פיקוד על המשא ומתן ולסגור את ההסכמים המורכבים והגדולים. אני מוביל את העסקאות שמזיזות את התוצאות.",
  "eyebrow":"שירות",
  "lead":"עסקאות גדולות מתמסמסות במשא ומתן. אני לוקח פיקוד על המשא ומתן וסוגר את ההסכמים המורכבים והרווחיים.",
  "card":"אני לוקח פיקוד על המשא ומתן וסוגר את העסקאות המורכבות והגדולות שמזיזות את התוצאות.",
  "sections":[
    {"h":"מתי צריך את זה","p":["העסקאות הכי גדולות שלכם הן אלה שאתם הכי לא יכולים להרשות לעצמכם להפסיד, ואלה שהכי נוטות להיתקע במשא ומתן: מחיר, תנאים, משפטי, רכש, וקונה שמריח היסוס."],
     "ul":["עסקאות גדולות נתקעות שוב ושוב בשלב המשא ומתן","הצוות שלכם חזק במכירה אבל לא בסגירת התנאים הקשים","אתם צריכים יד יציבה על העסקאות הכי חשובות"]},
    {"h":"מה אני עושה","ul":["לקיחת פיקוד על המשא ומתן בעסקאות המורכבות והגדולות שלכם","החזקת מחיר ותנאים בלי לאבד את העסקה","ניהול הרכש, המשפטי ומקבלי ההחלטות","סגירת ההסכמים שבאמת מזיזים את התוצאות"]},
    {"h":"איך זה עובד","p":["אני נכנס לעסקה החיה, קולט את התמונה המלאה מהר, ומוביל אותה עד החתימה. 20 שנה של סגירת הסכמים מורכבים B2B ו-B2G בחמש יבשות, אני מכיר את הטקטיקות עוד לפני שמפעילים אותן עליכם."]},
  ]},

 {"slug":"saas-sales","nav":"מכירות SaaS","h1":"מכירות SaaS ו-Go-To-Market",
  "title":"מכירות SaaS ו-Go-To-Market | טל פאפרין",
  "desc":"למכור SaaS לקונה B2B קשה. מיצוב, תנועה, ערוץ וצוות, בנויים לחברות תוכנה שיוצאות לשוק.",
  "eyebrow":"שירות",
  "lead":"מכירת SaaS היא דיסציפלינה בפני עצמה. אני בונה את המיצוב, התנועה, הערוץ והצוות לחברות תוכנה, כולל המכירה הארוכה, הטכנית ועתירת האמון.",
  "card":"מיצוב, תנועה, ערוץ וצוות לחברות תוכנה, בנויים למכירת ה-SaaS.",
  "sections":[
    {"h":"מתי צריך את זה","p":["מוצר מעולה הוא לא Go-to-Market. קוני SaaS הם ספקנים, טכניים ומוקפים באלטרנטיבות, ותנועת מכירות גנרית לא מזיזה אותם."],
     "ul":["מוצר חזק, אבל תנועת מכירות ה-SaaS לא ממירה","אתם מוכרים לקונים טכניים או מדעיים שצריכים גישה אחרת","אתם צריכים ערוץ וצוות בנויים לתוכנה, לא מאולתרים"]},
    {"h":"מה אני עושה","ul":["חידוד המיצוב, ה-ICP והצעת הערך לקונה SaaS","בניית האאוטבאונד וה-Playbook שהתנועה רצה עליו","בניית הערוץ: ריסלרים, אינטגרטורים ושותפים","גיוס, הכשרה וניהול של צוות מכירות ה-SaaS"]},
    {"h":"לאורך מכירת ה-SaaS","p":["מכרתי SaaS לסטארטאפים, לארגונים גדולים, ולחלק מהקונים הכי קשים שיש, אוניברסיטאות, מעבדות מחקר וחברות פארמה, שם המכירה ארוכה, טכנית ובנויה כולה על אמון."]},
  ]},

 {"slug":"global-markets","nav":"שווקים גלובליים","h1":"שווקים גלובליים: איפה אני בונה ומנהל הכנסות",
  "title":"שווקים גלובליים: התרחבות מכירות בינלאומית | טל פאפרין",
  "desc":"בניתי, גייסתי, הכשרתי וניהלתי צוותי מכירות, פתחתי חברות בנות וניהלתי תמיכה ושירות לקוחות בחמש יבשות, שוב ושוב ולמספר חברות. הנה איך אני בוחר שוק ובונה אותו.",
  "eyebrow":"גלובלי",
  "lead":"חמש יבשות. יותר מארבעים מדינות. מאות ערים, בשטח, לא מהאימייל. אני לא רק נכנס לשוק, אני עוזר לכם לבחור את הנכון, ואז בונה ומנהל אותו.",
  "card":"בניתי הכנסות בחמש יבשות. אני עוזר לכם לבחור את השוק הנכון, ואז בונה ומנהל שם את כל המערך.",
  "sections":[
    {"h":"קודם בוחרים שוק, אחר כך בונים אותו","p":[
      "הטעות היקרה ביותר בהתרחבות היא להיכנס מהר לשוק הלא נכון. אני מתחיל בלשפוט אם השוק בכלל שלכם, הכאב, הנגישות, הנכונות לשלם, התחרות, ואז בונה את המערך רק איפה שזה הגיוני. תכנון וביצוע, מאותו אדם שאחראי על התוצאות."]},
    {"h":"כל המערך, לא רק המכירה","ul":[
      "צוותי מכירות: SDR, AE והובלה, מגויסים, מוכשרים ומנוהלים",
      "חברות בנות שנפתחות כשלקוחות או גיוס דורשים ישות מקומית",
      "מערכי תמיכה טכנית ושירות לקוחות שמוקמים ומנוהלים",
      "תמחור, מיצוב ו-Go-To-Market שנבנים לקונה המקומי",
      "ה-CRM, הפייפליין, התחזית והאחריות על התוצאות"]},
    {"h":"נעשה שוב ושוב, למספר חברות","p":[
      "זה לא סיפור חד פעמי. בניתי, גייסתי, הכשרתי וניהלתי צוותים בשווקים האלה יותר מפעם אחת, למספר חברות, בחמש יבשות. מוצרים שונים, קונים שונים, אותה משמעת."]},
    {"h":"אזורים","links":[
      ["האיחוד האירופי","/he/blog/selling-b2b-in-the-eu"],
      ["מדינות נורדיות","/he/blog/selling-b2b-in-the-nordics"],
      ["מרכז ומזרח אירופה","/he/blog/selling-b2b-in-central-and-eastern-europe"],
      ["ברית המועצות לשעבר","/he/blog/selling-b2b-in-the-fsu"],
      ["אסיה-פסיפיק","/he/blog/selling-b2b-in-asia-pacific"],
      ["אוסטרליה וניו זילנד","/he/blog/selling-b2b-in-australia-and-new-zealand"],
      ["דרום אמריקה","/he/blog/selling-b2b-in-south-america"],
      ["מרכז אמריקה","/he/blog/selling-b2b-in-central-america"],
      ["אפריקה","/he/blog/selling-b2b-in-africa"]]},
    {"h":"מדינות","links":[
      ["ארצות הברית","/he/blog/building-a-sales-operation-in-the-united-states"],
      ["בריטניה","/he/blog/building-a-sales-operation-in-the-uk"],
      ["גרמניה","/he/blog/building-a-sales-operation-in-germany"],
      ["צרפת","/he/blog/building-a-sales-operation-in-france"],
      ["הולנד","/he/blog/building-a-sales-operation-in-the-netherlands"],
      ["יפן","/he/blog/building-a-sales-operation-in-japan"],
      ["סין","/he/blog/building-a-sales-operation-in-china"],
      ["דרום קוריאה","/he/blog/building-a-sales-operation-in-south-korea"],
      ["ברזיל","/he/blog/building-a-sales-operation-in-brazil"],
      ["פינלנד","/he/blog/selling-b2b-in-the-nordics"],["פולין","/he/blog/selling-b2b-in-central-and-eastern-europe"],["רומניה","/he/blog/selling-b2b-in-central-and-eastern-europe"],["הונגריה","/he/blog/selling-b2b-in-central-and-eastern-europe"],["רוסיה","/he/blog/selling-b2b-in-the-fsu"],["טאיוואן","/he/blog/selling-b2b-in-asia-pacific"]]},
  ]},
]

# Final service order (top sellers first); also drops merged/removed slugs
# (contract-negotiation folded into fractional CRO / B2G, saas-sales into GTM,
# global-markets merged into market-entry).
_SVC_ORDER = ["fractional-cro", "outsourced-sales", "pay-per-meeting", "go-to-market-strategy", "fractional-cmo", "market-entry",
              "sales-team-building", "distributor-channel-recruitment", "b2g-public-sector"]


def _order_services(lst):
    by = {s["slug"]: s for s in lst}
    return [by[k] for k in _SVC_ORDER if k in by]


SERVICES = _order_services(SERVICES)
HE_SERVICES = _order_services(HE_SERVICES)


HE_FAQ = {
 "slug": "challenges",
 "title": "אתגרי השיווק והמכירות הבינלאומיים, המדריך | טל פאפרין",
 "desc": "המדריך הישיר לחדירה לשווקים בינלאומיים: מוכנות, לקוחות ראשונים, מפיצים, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול VP במשרה מלאה, ותחרות מול הענקים.",
 "eyebrow": "מדריך",
 "h1": "אתגרי השיווק והמכירות הבינלאומיים",
 "lead": "כל מה שחברה ישראלית צריכה לדעת לפני שהיא יוצאת לשווקים הבינלאומיים. בלי בולשיט, מהשטח.",
 "items": [
  ('האם החברה שלכם בכלל מוכנה לשיווק בינלאומי?',
   ['רוב החברות יוצאות לחו״ל לא מוכנות, ומשלמות על זה ביוקר: תדמית חלשה, מפיצים טובים שלא רוצים לגעת בכם, תהליכי מכירה שלא מבשילים, וזמן וכסף שנשרפו.',
    'לפני שאתם משקיעים שקל בחו״ל, צריך אבחון כנה: האם ה-ICP מוגדר, האם המסר חד, והאם יש לכם סיפור שמוריד ללקוח את הסיכון לקנות מחברה לא מוכרת. בדיוק את זה אני עושה בשבוע הראשון.']),
  ('איך משיגים את הלקוחות הראשונים בחו״ל?',
   ['במכירות B2B, references זה הכל. הלקוח הראשון שמיישם אתכם בהצלחה שווה יותר מכל ברושור.',
    'המהלך: לאתר את ה-Early Adopters, אלה שמרגישים כאב אמיתי ומוכנים לקחת סיכון על חברה לא מוכרת, לחדד להם הצעת ערך שמסבירה בשנייה למה אתם ולא הענק הגלובלי, ולסגור את הלקוח האסטרטגי הראשון שאחריו יבואו השאר.']),
  ('צריך VP מכירות במשרה מלאה, או מיקור חוץ?',
   ['זאת הטעות הכי יקרה שאני רואה. חברות שוכרות VP מכירות שכיר בשלב שבו עוד אין מספיק פייפליין שיצדיק אותו, והמשכורת שורפת להן את התקציב כל חודש.',
    'עד שמנוע המכירות עובד ומזין לידים, <a href="/he/services/fractional-cro">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a> או מנהל מכירות במיקור חוץ נותן לכם את אותה מנהיגות בכירה בשבריר מהעלות: בלי משכורת, בלי תנאים סוציאליים ובלי סיכון פיצויים. כשהמשפך מתמלא, אז שוכרים משרה מלאה.']),
  ('איך מאתרים ובוחרים את המפיצים הנכונים?',
   ['המפיץ הראשון שפנה אליכם הוא כמעט אף פעם לא הנכון. חתימה על הסכם עם מי שמזדמן זה מתכון לחודשים של שקט מצדו ותירוצים מצדכם.',
    'קודם מגדירים אילו פונקציות המפיץ צריך למלא, בונים פרופיל של מפיץ אידיאלי, ורק אז מאתרים. מפיץ טוב גם בודק אתכם, ואם תשתית השיווק והמכירות שלכם חלשה הוא לא יתחבר. אני <a href="/he/services/distributor-channel-recruitment">בונה את התשתית ומנהל את התהליך</a> נכון.']),
  ('איך מתחרים בענקים הגלובליים עם כל המשאבים?',
   ['לא מנצחים אותם בתקציב. מנצחים אותם במיקוד. הענקים לא רוצים או לא יכולים לתפור פתרון לנישה ספציפית, ושם בדיוק יש לכם יתרון.',
    'מזהים קבוצת לקוחות עם כאב משותף שאתם פותרים טוב מכולם, מנסחים USP חד, ונלחמים על הלקוח האסטרטגי הראשון, גם אם מתפשרים על המחיר. אחריו באים האחרים.']),
  ('כמה זמן לוקח לראות תוצאות?',
   ['אצלי, מהר. אבחון בשבוע הראשון, תוכנית בשבוע השני, ביצוע מהשבוע השלישי. אני לא מוכר מצגת, אני לוקח אחריות על התוצאות.']),
  ('מה ההבדל בינך לבין יועץ שיווק?',
   ['יועץ נותן לכם המלצות והולך. אני נכנס, בונה את מערך המכירות, מגייס ומנהל את הצוות, סוגר עסקאות בעצמי ולוקח אחריות על התוצאה. <a href="/he/services/">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, לא יועץ מהצד</a>.']),
 ],
}


def render_he_related(slug):
    links = ['<a href="/he/services/%s">%s</a>' % (s["slug"], esc(s["nav"]))
             for s in HE_SERVICES if s["slug"] != slug][:3]
    return " &middot; ".join(links)


def _jsonesc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


HE_PAGE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />
  <link rel="alternate" hreflang="en" href="{en}" />
  <link rel="alternate" hreflang="he" href="{url}" />
  <link rel="alternate" hreflang="x-default" href="{en}" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{h1} | טל פאפרין" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
  {faqld}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/he/">בית</a> / <a href="/he/services/">שירותים</a></p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
{case}
{faq}
{cta}
        <div class="svc-related">שירותים נוספים: {related} &middot; <a href="/he/blog/">לבלוג</a></div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''

HE_INDEX = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>סמנכ״ל מכירות ו-GTM במיקור חוץ | טל פאפרין</title>
  <meta name="description" content="איך אני מתקן ומריץ מכירות: סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, מכירות במיקור חוץ, אסטרטגיית Go-To-Market, בניית צוות מכירות, גיוס מפיצים וחדירה לשווקים בינלאומיים." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/he/services/" />
  <link rel="alternate" hreflang="en" href="{site}/services/" />
  <link rel="alternate" hreflang="he" href="{site}/he/services/" />
  <link rel="alternate" hreflang="x-default" href="{site}/services/" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{site}/he/services/" />
  <meta property="og:title" content="שירותים | טל פאפרין" />
  <meta property="og:description" content="סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, מכירות במיקור חוץ, GTM, בניית צוות, גיוס מפיצים וחדירה לשווקים." />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">שירותים</p>
        <h1>מה אני עושה.</h1>
        <p class="lead">הדרכים שבהן אני מתקן ומריץ מכירות. בחרו את זו שמתאימה לבעיה שלכם, או <a href="/he/challenges">קראו את המדריך</a> ותגלו איפה כואב.</p>
      </div>
      <div class="svc-grid">
{cards}
      </div>
      <p style="text-align:center;margin-top:34px"><a class="btn btn-secondary" href="/he/pricing">לתמחור &larr;</a></p>
      <h2 class="cases-recs-h">בשטח, בחמש יבשות</h2>
{gallery}
    </div>
  </main>

{footer}
</body>
</html>
'''

HE_FAQPAGE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/he/challenges" />

  <meta property="og:type" content="article" />
  <meta property="og:url" content="{site}/he/challenges" />
  <meta property="og:title" content="{h1} | טל פאפרין" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  <script type="application/ld+json">{faqld}</script>
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{items}
{cta}
        <div class="svc-related">קראו עוד: <a href="/he/services/">השירותים שלי</a> &middot; <a href="/he/blog/">הבלוג</a></div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


CONTACT_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Contact Tal Paperin | Fractional CRO</title>
  <meta name="description" content="Book a 15-minute call, send a message, or reach Tal Paperin directly by email, phone or WhatsApp. Tell me where revenue stalled." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/contact" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/contact" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/contact" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/contact" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/contact" />
  <meta property="og:title" content="Contact Tal Paperin" />
  <meta property="og:description" content="Book a call, send a message, or reach me directly." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Contact Tal Paperin" />
  <meta name="twitter:description" content="Book a call, send a message, or reach me directly." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="contact-flank">
        <img class="contact-side" src="/img/site/contact-left.jpg" alt="Tal Paperin" loading="lazy" />
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Contact</p>
        <h1>Let's talk.</h1>
        <p class="lead">Tell me where revenue stalled. Book a call, send a message, or reach me directly. I read everything.</p>

        <div class="contact-cols">
          <div class="contact-card">
            <h2>Send a message</h2>
            <p class="contact-sub">I read every one. Replies within one business day.</p>
            <form class="cf-form" onsubmit="return submitForm(event)">
              <input type="text" id="cf-hp" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);clip-path:inset(50%);white-space:nowrap;opacity:0" />
              <input type="hidden" id="cf-loaded" value="" />
              <label for="cf-name">Your name</label>
              <input id="cf-name" type="text" name="name" required />
              <label for="cf-email">Email</label>
              <input id="cf-email" type="email" name="email" required autocomplete="email" />
              <label for="cf-message">Message</label>
              <textarea id="cf-message" name="message" required></textarea>
              <button class="btn btn-primary" type="submit">Send Message &rarr;</button>
              <p class="cf-msg" hidden></p>
            </form>
          </div>
          <div class="contact-card">
            <h2>Other channels</h2>
            <p class="contact-sub">Pick the one that fits.</p>
            <div class="channels">
              <a class="channel" href="https://calendly.com/ksw/15min" onclick="return openCal()">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#5ab0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></span>
                <span class="ch-text"><span class="ch-label">Book a call</span><span class="ch-val">15 minutes with Tal &middot; strategy session</span></span>
              </a>
              <a class="channel" href="mailto:tal@ksw.solutions">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#5ab0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg></span>
                <span class="ch-text"><span class="ch-label">Email</span><span class="ch-val">tal@ksw.solutions</span></span>
              </a>
              <a class="channel" href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="#5ab0ff" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 17V9.99H6V17h2.34zM7.17 8.93a1.36 1.36 0 1 0 0-2.72 1.36 1.36 0 0 0 0 2.72zM18 17v-3.86c0-2.06-1.1-3.02-2.57-3.02-1.19 0-1.72.65-2.02 1.11V9.99h-2.34V17h2.34v-3.91c0-.21.02-.41.08-.56.16-.41.54-.84 1.17-.84.83 0 1.16.63 1.16 1.55V17H18z"/></svg></span>
                <span class="ch-text"><span class="ch-label">LinkedIn</span><span class="ch-val">Connect with Tal Paperin</span></span>
              </a>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  </main>

{footer}
{contactjs}
</body>
</html>
'''

CONTACT_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>צור קשר | טל פאפרין</title>
  <meta name="description" content="תיאום שיחה של 15 דקות, שליחת הודעה, או יצירת קשר ישיר עם טל פאפרין במייל, טלפון או וואטסאפ. ספרו לי איפה המכירות נתקעו." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/contact" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/contact" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/contact" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/contact" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/contact" />
  <meta property="og:title" content="צור קשר | טל פאפרין" />
  <meta property="og:description" content="תיאום שיחה, שליחת הודעה, או יצירת קשר ישיר." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="contact-flank">
        <img class="contact-side" src="/img/site/contact-left.jpg" alt="טל פאפרין" loading="lazy" />
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">צור קשר</p>
        <h1>בואו נדבר.</h1>
        <p class="lead">ספרו לי איפה המכירות נתקעו. תאמו שיחה, שלחו הודעה, או צרו קשר ישיר. אני קורא הכל.</p>

        <div class="contact-cols">
          <div class="contact-card">
            <h2>שליחת הודעה</h2>
            <p class="contact-sub">אני קורא כל אחת. מענה תוך יום עסקים אחד.</p>
            <form class="cf-form" onsubmit="return submitForm(event)">
              <input type="text" id="cf-hp" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);clip-path:inset(50%);white-space:nowrap;opacity:0" />
              <input type="hidden" id="cf-loaded" value="" />
              <label for="cf-name">שם</label>
              <input id="cf-name" type="text" name="name" required />
              <label for="cf-email">אימייל</label>
              <input id="cf-email" type="email" name="email" required autocomplete="email" />
              <label for="cf-message">הודעה</label>
              <textarea id="cf-message" name="message" required></textarea>
              <button class="btn btn-primary" type="submit">שליחת הודעה &larr;</button>
              <p class="cf-msg" hidden></p>
            </form>
          </div>
          <div class="contact-card">
            <h2>ערוצים נוספים</h2>
            <p class="contact-sub">בחרו את זה שמתאים.</p>
            <div class="channels">
              <a class="channel" href="https://calendly.com/ksw/15min" onclick="return openCal()">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#5ab0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></span>
                <span class="ch-text"><span class="ch-label">תיאום שיחה</span><span class="ch-val">15 דקות עם טל &middot; שיחת אסטרטגיה</span></span>
              </a>
              <a class="channel" href="mailto:tal@ksw.solutions">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#5ab0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg></span>
                <span class="ch-text"><span class="ch-label">מייל</span><span class="ch-val">tal@ksw.solutions</span></span>
              </a>
              <a class="channel" href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">
                <span class="ch-icon"><svg viewBox="0 0 24 24" fill="#5ab0ff" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 17V9.99H6V17h2.34zM7.17 8.93a1.36 1.36 0 1 0 0-2.72 1.36 1.36 0 0 0 0 2.72zM18 17v-3.86c0-2.06-1.1-3.02-2.57-3.02-1.19 0-1.72.65-2.02 1.11V9.99h-2.34V17h2.34v-3.91c0-.21.02-.41.08-.56.16-.41.54-.84 1.17-.84.83 0 1.16.63 1.16 1.55V17H18z"/></svg></span>
                <span class="ch-text"><span class="ch-label">לינקדאין</span><span class="ch-val">התחברו עם טל פאפרין</span></span>
              </a>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  </main>

{footer}
{contactjs}
</body>
</html>
'''


CONTACT_JS_EN = '''  <link rel="stylesheet" href="https://assets.calendly.com/assets/external/widget.css" />
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
  <script>
    (function(){var cl=document.getElementById('cf-loaded');if(cl)cl.value=String(Date.now());})();
    function openCal(){try{gtag('event','book_a_call');}catch(e){}if(window.Calendly){Calendly.initPopupWidget({url:'https://calendly.com/ksw/15min'});return false;}return true;}
    function cfDone(f,m){var els=f.querySelectorAll('input,textarea,button,label');for(var i=0;i<els.length;i++){els[i].style.display='none';}m.hidden=false;m.style.color='var(--blue)';m.textContent='Thanks. Your message is on its way, I will reply within one business day.';}
    function submitForm(e){e.preventDefault();var f=e.target,m=f.querySelector('.cf-msg'),b=f.querySelector('button');
      if(f.querySelector('#cf-hp').value){cfDone(f,m);return false;}
      var loaded=parseInt(f.querySelector('#cf-loaded').value||'0',10);
      if(loaded&&Date.now()-loaded<3000){cfDone(f,m);return false;}
      var n=f.querySelector('[name=name]').value,em=f.querySelector('[name=email]').value,msg=f.querySelector('[name=message]').value;
      b.disabled=true;b.textContent='Sending...';
      fetch('https://formspree.io/f/xykbgowb',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({name:n,email:em,message:msg})})
        .then(function(r){if(r.ok){try{gtag('event','generate_lead');}catch(e){}cfDone(f,m);}else{b.disabled=false;b.textContent='Send Message';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please email tal@ksw.solutions.';}})
        .catch(function(){b.disabled=false;b.textContent='Send Message';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please email tal@ksw.solutions.';});
      return false;}
  </script>'''

CONTACT_JS_HE = '''  <link rel="stylesheet" href="https://assets.calendly.com/assets/external/widget.css" />
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
  <script>
    (function(){var cl=document.getElementById('cf-loaded');if(cl)cl.value=String(Date.now());})();
    function openCal(){try{gtag('event','book_a_call');}catch(e){}if(window.Calendly){Calendly.initPopupWidget({url:'https://calendly.com/ksw/15min'});return false;}return true;}
    function cfDone(f,m){var els=f.querySelectorAll('input,textarea,button,label');for(var i=0;i<els.length;i++){els[i].style.display='none';}m.hidden=false;m.style.color='var(--blue)';m.textContent='תודה. ההודעה שלך בדרך, אענה תוך יום עסקים אחד.';}
    function submitForm(e){e.preventDefault();var f=e.target,m=f.querySelector('.cf-msg'),b=f.querySelector('button');
      if(f.querySelector('#cf-hp').value){cfDone(f,m);return false;}
      var loaded=parseInt(f.querySelector('#cf-loaded').value||'0',10);
      if(loaded&&Date.now()-loaded<3000){cfDone(f,m);return false;}
      var n=f.querySelector('[name=name]').value,em=f.querySelector('[name=email]').value,msg=f.querySelector('[name=message]').value;
      b.disabled=true;b.textContent='שולח...';
      fetch('https://formspree.io/f/xykbgowb',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({name:n,email:em,message:msg})})
        .then(function(r){if(r.ok){try{gtag('event','generate_lead');}catch(e){}cfDone(f,m);}else{b.disabled=false;b.textContent='שליחת הודעה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. אפשר לכתוב ל-tal@ksw.solutions.';}})
        .catch(function(){b.disabled=false;b.textContent='שליחת הודעה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. אפשר לכתוב ל-tal@ksw.solutions.';});
      return false;}
  </script>'''


CASE_STUDIES = [
 {"company":"Headcount ERC","id":"headcount-erc","meta":"US tax-credit (ERC) recovery, Go-to-market and sales team build",
  "situation":"A US firm helping eligible businesses claim the federal Employee Retention Credit, money many of them were genuinely owed and had no idea they qualified for. The offer was real and the addressable market was enormous, but there was no go-to-market motion to reach it at scale and no sales team to run it. On top of that it was a high-velocity, high-volume sale against the clock: a closing filing window and a buyer who had already been cold-called by a dozen ERC shops and trusted none of them. Trust had to be earned fast, at scale.",
  "did":["Built the entire go-to-market plan and sales strategy from scratch","Defined the ICP, the qualification criteria and the outbound messaging that cut through the ERC noise","Designed the full sales process and playbook, from first touch to signed engagement","Recruited, hired and onboarded the team of SDRs and AEs","Managed the SDRs and AEs day to day: targets, scripts, coaching, pipeline and performance"],
  "result":"A go-to-market motion and a trained SDR and AE sales floor where there had been neither, turning a huge but skeptical, hard-to-reach market into a managed, repeatable outbound engine."},
 {"company":"KanduAI","id":"kanduai","meta":"AI SaaS startup, Fractional VP of Sales",
  "situation":"An early-stage AI startup with a product and no way to sell it. No pipeline, no process, no team, and nobody who had ever built a sales motion from zero. They did not need advice, they needed someone to take the revenue side off the founders' plate and build the engine, then keep it alive when the product pivoted out from under it. Twice.",
  "did":["Owned go-to-market end to end as Fractional VP of Sales from day one","Defined and validated the ICP, positioning and messaging before a single rep dialed","Built the outbound playbook and the entire motion from zero","Hired, trained and managed the SDR team","Relaunched the whole go-to-market through the pivot, twice, without losing momentum"],
  "result":"An outbound engine that existed where there had been nothing, rebuilt from scratch through two pivots. The founders got a real motion and a trained team instead of guessing at sales between everything else they were carrying."},
 {"company":"LoneStar Tracking","id":"lonestar","meta":"Founder-led IoT business, Outsourced sales leadership",
  "situation":"Marketing was doing its job and generating real interest. The problem was everything that happened after the lead came in. Deals stalled and died because there was no sales engine to convert them and founders who had never sold for a living. They were paying to create demand and watching it leak straight out the bottom.",
  "did":["Built the entire sales strategy and motion from scratch","Selected and implemented the CRM and the full sales stack","Built the process, the playbook and the pipeline","Recruited, hired and trained the sales team","Ran the team and the motion day to day as outsourced sales leadership"],
  "result":"Full VP-level sales leadership at a fraction of the cost of a hire, with a real process catching the demand marketing was paying to create instead of letting it bleed away."},
 {"company":"Bacsoft","id":"bacsoft","meta":"Israeli industrial IoT, backed by Japan's SUN Corp, VP of Global Sales",
  "situation":"An Israeli industrial IoT company, backed by Japan's SUN Corp, that made existing equipment smart and connected for water and wastewater utilities, manufacturers and smart cities. The technology was real and the global demand was there, with projects from Peru to Holland to Australia. What was missing was the engine to actually sell complex industrial IoT across borders: a strategy, a distributor network across continents, and the patience to win public-sector deals with long RFI and RFQ cycles.",
  "did":["Owned the global sales strategy end to end","Recruited and managed distributors across continents, from Europe to South America to APAC","Ran direct B2B sales of SaaS, hardware and services into utilities, manufacturers and municipalities","Led B2G: RFIs, RFQs and complex government and utility projects across the globe","Represented the company at international industry shows and managed marketing and marcom"],
  "result":"A global channel and a live B2G pipeline for a small Israeli company selling complex industrial IoT, hardware, software and services, to utilities and governments on five continents."},
 {"company":"Palram","id":"palram","meta":"Global manufacturer, Eastern Europe market entry",
  "situation":"A global manufacturer had looked at Eastern Europe and decided there was no money in it, so they stayed out and left the territory blank on the map. The assumption had never actually been tested against the real channel or the real buyers on the ground. It was a story the company told itself, not a fact.",
  "did":["Built the market-entry strategy and the milestone plan","Mapped the channel and the real decision-makers on the ground","Led every negotiation personally","Signed multiple distributors and retail chains across the region"],
  "result":"Product on shelves in a market the company had written off entirely, proving there was real money in Eastern Europe and that the only thing missing had been someone willing to go open it."},
 {"company":"Limat","id":"limat","meta":"Market research and a Western Europe sales machine, focused on the UK and Eastern Europe",
  "situation":"Limat wanted to grow in Western Europe but did not want to bet on it blind. They needed someone to find where the real opportunity was, then actually go build the sales motion to chase it, not hand over a strategy deck and walk away. The brief was simple: research the market, pick the fights worth picking, and build the machine.",
  "did":["Ran the market research to find where the genuine demand and the right entry points were","Focused the push on the UK and Eastern Europe, the markets that justified the investment","Built the sales machine to go after those markets, not just a plan on paper"],
  "result":"A research-backed entry into Western Europe, concentrated on the UK and Eastern Europe, with a sales machine built to chase it instead of a report nobody acts on."},
 {"company":"BT9","id":"bt9","meta":"Xsense cold chain monitoring (IoT and SaaS), International sales across FSU, EU and APAC",
  "situation":"BT9 built Xsense, a real-time cold chain monitoring system that tracks the temperature and humidity of perishables from inside the carton, through every link of the supply chain, so food companies can act before a shipment spoils. Great product, and almost no international sales operation to put it in front of the world. Three very different regions, the FSU, the EU and APAC, each with its own buyers, channels and rules, and the whole machine had to be built from the ground up.",
  "did":["Built an international sales operation from zero across the FSU, the EU and APAC","Ran direct sales of the Xsense SaaS, hardware and services to food and perishables companies","Recruited and managed the distributor network market by market","Represented the product at international trade shows like Fruit Logistica in Berlin","Hired, trained and ran the team day to day: SDRs, post-sales and tech support"],
  "result":"A working international cold chain sales engine across three regions, built from scratch, selling through both direct sales and a managed distributor network."},
 {"company":"TAG Medical","id":"tag-medical","meta":"Dental implants and digital guided surgery, International sales and marketing, EU",
  "situation":"TAG Medical (TAG Dental) made dental implants and digital guided-surgery systems, CAD/CAM kits that hand the surgeon everything needed for a procedure and cut both error and chair time. Pushing that into the EU meant selling into a cautious, heavily regulated, high-trust market where the buyer does not gamble. They needed more than a salesperson. They needed a full commercial function, sales and marketing both.",
  "did":["Ran international sales across the EU","Drove direct B2B sales of dental implants and guided-surgery systems","Recruited and managed distributors across European markets","Built and ran the entire marketing department, online and offline, including the company's first video commercials and the launch of its digital CAD/CAM center"],
  "result":"A complete sales and marketing engine for dental implants and guided surgery across Europe: direct sales and a distributor network on one side, a full marketing department on the other."},
 {"company":"SOURCE Vagabond","id":"source-vagabond","meta":"Consumer products, North American retail",
  "situation":"An Israeli consumer brand almost nobody in the US had heard of, trying to get onto the shelves of large American retailers and big-box chains. That is the hardest room in the building to walk into as an unknown overseas name, where buyers have every reason to say no and no reason to gamble on you.",
  "did":["Sold direct to large retailers and big-box stores across North America","Recruited and managed distributors to extend the reach","Built the positioning that got an unknown brand taken seriously by major chains"],
  "result":"An unknown overseas brand turned into product sitting in major North American retail, sold in direct to the big chains and backed by a distributor network."},
 {"company":"Synergix","id":"synergix","meta":"Scientific SaaS, North America",
  "situation":"Scientific SaaS sold to possibly the hardest buyer there is: universities, research labs and pharma. Technical, skeptical, slow to trust and impossible to bluff. Reps could not wing this one, and the company had no playbook for selling into a room full of scientists who can smell a sales pitch from across the building.",
  "did":["Drove direct B2B SaaS sales to universities, research facilities and pharma companies","Wrote the sales scripts and the playbook the reps actually used","Led and motivated the sales effort through a long, technical cycle"],
  "result":"SaaS sold into US academia and pharma, a long, technical, high-trust sale, run off scripts and a playbook the reps could execute instead of improvising every call."},
]

HE_CASES = [
 {"company":"Headcount ERC","id":"headcount-erc","meta":"החזרי מס (ERC) בארה״ב, בניית GTM וצוות מכירות",
  "situation":"חברה אמריקאית שעוזרת לעסקים זכאים לתבוע את ה-Employee Retention Credit הפדרלי, כסף שרבים מהם באמת היו זכאים לו ולא ידעו שהם עומדים בקריטריונים. ההצעה הייתה אמיתית והשוק הפוטנציאלי ענק, אבל לא הייתה תנועת GTM להגיע אליו בקנה מידה ולא צוות מכירות שיריץ אותה. נוסף על כך, זו הייתה מכירה מהירה ובנפח גבוה במרוץ נגד השעון: חלון הגשה שנסגר, וקונה שכבר קיבל שיחות קרות מתריסר חברות ERC ולא בטח באף אחת מהן. היה צריך לבנות אמון מהר, בקנה מידה.",
  "did":["בניתי את כל תוכנית ואסטרטגיית ה-GTM מאפס","הגדרתי את ה-ICP, קריטריוני הסינון והמסרים שחתכו את הרעש בשוק ה-ERC","תכננתי את כל תהליך המכירה וה-Playbook, מהמגע הראשון ועד החתימה","גייסתי, הכשרתי וקלטתי את צוות ה-SDR וה-AE","ניהלתי את ה-SDRs וה-AEs יום-יום: יעדים, סקריפטים, אימון, פייפליין וביצועים"],
  "result":"תנועת GTM וצוות מכירות מיומן של SDRs ו-AEs במקום שבו לא היה אף אחד מהם, שהפכו שוק ענק אך סקפטי וקשה להשגה למנוע אאוטבאונד מנוהל וניתן לשחזור."},
 {"company":"KanduAI","id":"kanduai","meta":"סטארטאפ AI SaaS, VP מכירות במיקור חוץ",
  "situation":"סטארטאפ AI בתחילת הדרך עם מוצר וללא שום דרך למכור אותו. בלי פייפליין, בלי תהליך, בלי צוות, ובלי אף אחד שאי פעם בנה מערך מכירות מאפס. הם לא היו צריכים עצות, הם היו צריכים מישהו שייקח את צד ההכנסות מהמייסדים ויבנה את המנוע, ואז ישמור עליו חי כשהמוצר עבר פיבוט מתחת לרגליים. פעמיים.",
  "did":["לקחתי אחריות מלאה על ה-GTM כ-VP מכירות במיקור חוץ מהיום הראשון","הגדרתי ותיקפתי את ה-ICP, המיצוב והמסרים לפני שנציג אחד הרים טלפון","בניתי את ה-Playbook ואת כל תנועת האאוטבאונד מאפס","גייסתי, הכשרתי וניהלתי את צוות ה-SDR","השקתי מחדש את כל ה-GTM דרך הפיבוט, פעמיים, בלי לאבד תאוצה"],
  "result":"מנוע אאוטבאונד שהתקיים במקום שבו לא היה כלום, שנבנה מחדש מאפס דרך שני פיבוטים. המייסדים קיבלו תנועת מכירות אמיתית וצוות מיומן במקום לנחש מכירות בין כל שאר הדברים שנשאו על הגב."},
 {"company":"LoneStar Tracking","id":"lonestar","meta":"עסק IoT בהובלת מייסדים, הובלת מכירות במיקור חוץ",
  "situation":"השיווק עשה את שלו וייצר עניין אמיתי. הבעיה הייתה כל מה שקרה אחרי שהליד נכנס. עסקאות נתקעו ומתו כי לא היה מנוע מכירות שימיר אותן, ומייסדים שמעולם לא מכרו למחייתם. הם שילמו כדי לייצר ביקוש וצפו בו דולף החוצה מהתחתית.",
  "did":["בניתי את כל אסטרטגיית ותהליכי המכירה מאפס","בחרתי והטמעתי CRM ומערך כלי מכירה מלא","בניתי תהליך, Playbook ופייפליין","גייסתי, הכשרתי ובניתי את צוות המכירות","ניהלתי את הצוות ואת התנועה יום-יום כהובלת מכירות במיקור חוץ"],
  "result":"הובלת מכירות מלאה ברמת VP בשבריר מעלות של גיוס, עם תהליך אמיתי שתפס את הביקוש שהשיווק שילם כדי לייצר, במקום לתת לו להתנדף."},
 {"company":"Bacsoft","id":"bacsoft","meta":"חברת IoT תעשייתית ישראלית בגיבוי SUN Corp מיפן, VP מכירות גלובלי",
  "situation":"חברת IoT תעשייתית ישראלית, בגיבוי SUN Corp מיפן, שהפכה ציוד קיים לחכם ומחובר עבור תאגידי מים וביוב, יצרנים וערים חכמות. הטכנולוגיה הייתה אמיתית והביקוש הגלובלי היה שם, עם פרויקטים מפרו ועד הולנד ועד אוסטרליה. מה שחסר היה המנוע שבאמת ימכור IoT תעשייתי מורכב מעבר לגבולות: אסטרטגיה, רשת מפיצים בכמה יבשות, והסבלנות לזכות בעסקאות מול המגזר הציבורי עם מחזורי RFI ו-RFQ ארוכים.",
  "did":["לקחתי אחריות מלאה על אסטרטגיית המכירות הגלובלית","גייסתי וניהלתי מפיצים בכמה יבשות, מאירופה ועד דרום אמריקה ועד APAC","הרצתי מכירה ישירה B2B של SaaS, חומרה ושירותים לתאגידי מים, יצרנים ורשויות","הובלתי B2G: מכרזים, RFIs, RFQs ופרויקטים ממשלתיים ותשתיתיים מורכבים בכל העולם","ייצגתי את החברה בתערוכות תעשייה בינלאומיות וניהלתי את השיווק וה-Marcom"],
  "result":"רשת ערוצים גלובלית ופייפליין B2G חי, לחברה ישראלית קטנה שמוכרת IoT תעשייתי מורכב, חומרה, תוכנה ושירותים, לתאגידים ולממשלות בחמש יבשות."},
 {"company":"Palram","id":"palram","meta":"יצרן גלובלי, חדירה לשוק במזרח אירופה",
  "situation":"יצרן גלובלי הסתכל על מזרח אירופה והחליט שאין שם כסף, ולכן נמנע מלהיכנס והשאיר את הטריטוריה ריקה על המפה. ההנחה הזו מעולם לא נבחנה באמת מול הערוץ האמיתי או הקונים האמיתיים בשטח. זה היה סיפור שהחברה סיפרה לעצמה, לא עובדה.",
  "did":["בניתי את אסטרטגיית החדירה ותוכנית אבני הדרך","מיפיתי את הערוץ ואת מקבלי ההחלטות האמיתיים בשטח","ניהלתי כל משא ומתן באופן אישי","החתמתי מספר מפיצים ורשתות קמעונאות באזור"],
  "result":"מוצר על המדפים בשוק שהחברה כבר מחקה לחלוטין, והוכחה שיש שם כסף אמיתי ושכל מה שחסר היה מישהו שמוכן ללכת ולפתוח אותו."},
 {"company":"Limat","id":"limat","meta":"מחקר שוק ומכונת מכירות במערב אירופה, במיקוד על בריטניה ומזרח אירופה",
  "situation":"Limat רצו לצמוח במערב אירופה, אבל לא רצו להמר על זה בעיניים עצומות. הם היו צריכים מישהו שימצא איפה ההזדמנות האמיתית, ואז באמת ילך ויבנה את מערך המכירות שירדוף אחריה, לא שיגיש מצגת אסטרטגיה וייעלם. הבריף היה פשוט: לחקור את השוק, לבחור את הקרבות ששווה לבחור, ולבנות את המכונה.",
  "did":["ביצעתי את מחקר השוק כדי למצוא איפה הביקוש האמיתי ונקודות הכניסה הנכונות","מיקדתי את המהלך בבריטניה ובמזרח אירופה, השווקים שהצדיקו את ההשקעה","בניתי את מכונת המכירות שתרדוף אחרי השווקים האלה, לא רק תוכנית על הנייר"],
  "result":"כניסה מבוססת מחקר למערב אירופה, ממוקדת בבריטניה ובמזרח אירופה, עם מכונת מכירות שנבנתה כדי לרדוף אחריה במקום דוח שאף אחד לא פועל לפיו."},
 {"company":"BT9","id":"bt9","meta":"Xsense, ניטור שרשרת קור (IoT ו-SaaS), מכירות בינלאומיות ב-FSU, באיחוד האירופי וב-APAC",
  "situation":"BT9 בנתה את Xsense, מערכת ניטור שרשרת קור בזמן אמת שעוקבת אחר הטמפרטורה והלחות של מוצרים מתכלים מתוך האריזה עצמה, לאורך כל חוליה בשרשרת, כדי שחברות מזון יוכלו לפעול לפני שמשלוח מתקלקל. מוצר מצוין, וכמעט בלי מערך מכירות בינלאומי שיציג אותו לעולם. שלוש טריטוריות שונות מאוד, FSU, האיחוד האירופי ו-APAC, לכל אחת קונים, ערוצים וכללים משלה, וכל המכונה הייתה צריכה להיבנות מהיסוד.",
  "did":["בניתי מערך מכירות בינלאומי מאפס ב-FSU, באיחוד האירופי וב-APAC","הרצתי מכירה ישירה של Xsense, SaaS, חומרה ושירותים לחברות מזון ומוצרים מתכלים","גייסתי וניהלתי את רשת המפיצים, שוק אחר שוק","ייצגתי את המוצר בתערוכות בינלאומיות כמו Fruit Logistica בברלין","גייסתי, הכשרתי וניהלתי את הצוות יום-יום: SDR, פוסט-סייל ותמיכה טכנית"],
  "result":"מנוע מכירות בינלאומי עובד לשרשרת קור בשלוש טריטוריות, שנבנה מאפס, ומוכר גם במכירה ישירה וגם דרך רשת מפיצים מנוהלת."},
 {"company":"TAG Medical","id":"tag-medical","meta":"שתלים דנטליים וכירורגיה מונחית דיגיטלית, מכירות ושיווק בינלאומיים באיחוד האירופי",
  "situation":"TAG Medical (TAG Dental) ייצרה שתלים דנטליים ומערכות כירורגיה מונחית דיגיטלית, ערכות CAD/CAM שנותנות למנתח את כל מה שצריך להליך ומצמצמות גם טעויות וגם זמן כיסא. לדחוף את זה לאיחוד האירופי משמעו למכור לשוק זהיר, מפוקח מאוד ועתיר אמון, שבו הקונה לא מהמר. הם היו צריכים יותר מאיש מכירות. הם היו צריכים פונקציה מסחרית מלאה, גם מכירות וגם שיווק.",
  "did":["ניהלתי מכירות בינלאומיות בכל האיחוד האירופי","הובלתי מכירה ישירה B2B של שתלים דנטליים ומערכות כירורגיה מונחית","גייסתי וניהלתי מפיצים בשווקים האירופיים","בניתי וניהלתי את כל מחלקת השיווק, אונליין ואופליין, כולל סרטוני הפרסומת הראשונים של החברה והשקת מרכז ה-CAD/CAM הדיגיטלי שלה"],
  "result":"מערך מכירות ושיווק שלם לשתלים דנטליים וכירורגיה מונחית בכל אירופה: מכירה ישירה ורשת מפיצים מצד אחד, מחלקת שיווק מלאה מצד שני."},
 {"company":"SOURCE Vagabond","id":"source-vagabond","meta":"מוצרי צריכה, קמעונאות בצפון אמריקה",
  "situation":"מותג צריכה ישראלי שכמעט אף אחד בארה״ב לא שמע עליו, שמנסה להגיע למדפים של קמעונאים אמריקאים גדולים ורשתות Big Box. זה החדר הכי קשה להיכנס אליו בתור שם זר ולא מוכר, שבו לקונים יש כל סיבה להגיד לא ואף סיבה להמר עליך.",
  "did":["מכרתי ישירות לקמעונאים גדולים ולרשתות Big Box בכל צפון אמריקה","גייסתי וניהלתי מפיצים כדי להרחיב את הטווח","בניתי את המיצוב שגרם למותג לא מוכר להילקח ברצינות על ידי רשתות גדולות"],
  "result":"מותג זר לא מוכר שהפך למוצר על המדפים של הקמעונאות הגדולה בצפון אמריקה, נמכר ישירות לרשתות הגדולות ונתמך ברשת מפיצים."},
 {"company":"Synergix","id":"synergix","meta":"SaaS מדעי, צפון אמריקה",
  "situation":"SaaS מדעי שנמכר אולי לקונה הכי קשה שיש: אוניברסיטאות, מעבדות מחקר ופארמה. טכני, ספקן, איטי לתת אמון ובלתי אפשרי לבלוף. נציגים לא יכלו לאלתר את זה, ולחברה לא היה Playbook למכירה לחדר מלא מדענים שמריחים מצגת מכירות מקצה הבניין.",
  "did":["הובלתי מכירה ישירה B2B של SaaS לאוניברסיטאות, מוסדות מחקר וחברות פארמה","כתבתי את תסריטי המכירה ואת ה-Playbook שהנציגים באמת השתמשו בהם","הובלתי והנעתי את צוות המכירות לאורך מחזור מכירה ארוך וטכני"],
  "result":"SaaS שנמכר לאקדמיה ולפארמה בארה״ב, מכירה ארוכה, טכנית ועתירת אמון, שרצה על תסריטים ו-Playbook שהנציגים יכלו לבצע במקום לאלתר כל שיחה."},
]


LOGO_MAP = {"Headcount ERC":"headcount","KanduAI":"kanduai","LoneStar Tracking":"lonestar","Bacsoft":"bacsoft",
            "Palram":"palram","BT9":"bt9","SOURCE Vagabond":"source","Limat":"limat"}


def render_cases(cases, rlabel):
    out = []
    for c in cases:
        logo = LOGO_MAP.get(c["company"], "")
        img = ('<img class="cs-logo" src="/logos/%s.jpg" alt="%s" loading="lazy" />\n        '
               % (logo, esc(c["company"]))) if logo else ""
        lis = "".join("<li>%s</li>" % esc(x) for x in c["did"])
        cid = (' id="%s"' % esc(c["id"])) if c.get("id") else ""
        out.append('      <div class="case-study"%s>\n        %s'
                    '<h2>%s</h2>\n        <div class="meta">%s</div>\n'
                    '        <p class="situation">%s</p>\n        <ul>%s</ul>\n'
                    '        <div class="result"><span>%s</span>%s</div>\n      </div>'
                    % (cid, img, esc(c["company"]), esc(c["meta"]), esc(c["situation"]), lis,
                       esc(rlabel), esc(c["result"])))
    return "\n".join(out)


def _initials(name):
    parts = [p for p in re.split(r"[\s.,\"']+", name) if p and p[0].isalpha()]
    a = parts[0][0] if parts else "?"
    b = parts[1][0] if len(parts) > 1 else ""
    return (a + b).upper()


# Testimonial tag -> service label (EN, HE), linked to the matching service page.
SVC_TAG = {
    "fractional-cro": ("Fractional CRO", "סמנכ״ל מכירות"),
    "outsourced-sales": ("Outsourced Sales", "מכירות במיקור חוץ"),
    "go-to-market-strategy": ("Go-To-Market", "Go-To-Market"),
    "market-entry": ("Market Entry", "חדירה לשוק"),
    "sales-team-building": ("Sales Team", "בניית צוות מכירות"),
    "distributor-channel-recruitment": ("Channels", "מפיצים וערוצים"),
    "b2g-public-sector": ("B2G", "B2G"),
}


def _tcard(t, he=False):
    name = t["name"]
    photo = t.get("photo")
    if photo:
        av = '<img class="tavatar" src="%s" alt="%s" loading="lazy" />' % (esc(photo), esc(name))
    else:
        av = '<span class="tavatar tavatar-i">%s</span>' % esc(_initials(name))
    role = ('<span class="trole">%s</span>' % esc(t["role"])) if t.get("role") else ""
    company = ('<span class="tco">%s</span>' % esc(t["company"])) if t.get("company") else ""
    tag = ""
    slug = t.get("tag")
    if slug in SVC_TAG:
        label = SVC_TAG[slug][1 if he else 0]
        base = "/he/services/" if he else "/services/"
        tag = '<div class="tcard-foot"><a class="ttag" href="%s%s">%s</a></div>' % (base, slug, esc(label))
    return ('<div class="tcard"><div class="tcard-top">%s'
            '<span class="tcard-id"><strong>%s</strong>%s%s</span></div>'
            '<p class="tcard-q">%s</p>%s</div>'
            % (av, esc(name), role, company, esc(t["q"]), tag))


def render_testimonials(quotes, he=False):
    inner = "".join(_tcard(t, he) for t in quotes)
    return ('<div class="marquee tmarquee"><div class="marquee-track">%s%s</div></div>'
            % (inner, inner))


TESTIMONIALS_EN = [
 {"q": "We brought in Tal Paperin as our Fractional VP of Sales from day one at KanduAi. He wasn't just a consultant, he acted as a true VP of Sales. He defined our Ideal Customer Profile, built our outbound playbook, hired and trained SDRs, and launched our outbound motion twice. If you're a founder trying to launch or relaunch sales from zero, Tal is who you want in your corner.", "name": "Ariel Shemesh", "role": "Co-Founder & CEO", "company": "KanduAI", "tag": "fractional-cro", "photo": "/img/testimonials/ariel-shemesh.jpg"},
 {"q": "Tal has been a pleasure to work with. I own and operate a small business in the IoT sector, and have very little experience in sales and marketing. Tal was able to quickly develop a strategy for us, implement a CRM, and start building and training our sales team. If you are a small (or large) business needing to get your sales and marketing straightened out, Tal is your guy.", "name": "Tommy Remmert", "role": "Co-Founder & CTO", "company": "LoneStar Tracking", "tag": "outsourced-sales", "photo": "/img/testimonials/tommy-remmert.jpg"},
 {"q": "He got involved. He trained with us, worked through deals, challenged how we approached conversations ... his training produced results. It made us better salespeople, improved our conversations with prospects, and helped us close more deals. ... The ones who can actually teach, motivate, strategize, and still connect with their team are harder to find than people think. Tal is one of those leaders.", "name": "Rich Martinez", "role": "Sr. Practice Growth Consultant", "company": "ClinicMind", "tag": "fractional-cro", "photo": "/img/testimonials/rich-martinez.jpg"},
 {"q": "If you are looking for someone who understands sales, Tal is your address. His grasp on the overall sales process, how to move a prospect forward and his on point grasp of how to move your business forward is invaluable. Follow him. Listen to him. Take his advice. Grow your business as a result.", "name": "Helen Gottstein", "role": "Public Speaking & Executive Communications", "company": "", "tag": "go-to-market-strategy", "photo": "/img/testimonials/helen-gottstein.jpg"},
 {"q": "Tal is a hard-working and trustworthy person. I have experience as a client, a partner and working for him directly. He is a man of his word, delivers on what he promises. A competent salesperson and strategist I would recommend him to any company wanting a fractional sales leader, channel manager or strategist.", "name": "Steve Burton", "role": "CRO", "company": "The Point Company", "tag": "fractional-cro", "photo": "/img/testimonials/steve-burton.jpg"},
 {"q": "Working with Tal has been impactful. He helped us understand where the issues were in our sales process and provided us a roadmap to increase sales by creating custom SOPs and demonstrating every step very clearly. He is very responsive and communicates well. Highly recommended.", "name": "Amitay Stern", "role": "CEO", "company": "TypoDuctions & DRIFT", "tag": "go-to-market-strategy", "photo": "/img/testimonials/amitay-stern.jpg"},
 {"q": "Tal is a sharp and smart marketer. In a short conversation, he was able to understand and analyze complex problems of understanding the market, customer analysis, and consumer mapping. He brought us quick and good solutions that do the job.", "name": "David Gallula, Ph.D.", "role": "Head of UED Research Institute, CEO of ProUX", "company": "", "tag": "go-to-market-strategy", "photo": "/img/testimonials/david-gallula-ph-d.jpg"},
 {"q": "With just an initial 15 minute consulting call with Tal, I was able to identify new approaches that I am confident will lead to a significant increase in successful prospect meetings. Tal was friendly, gracious with his time, and a good listener. This session was one of the most helpful resources I have encountered.", "name": "Michael Teichberg", "role": "Founder", "company": "InventivHR", "tag": "sales-team-building", "photo": "/img/testimonials/michael-teichberg.jpg"},
 {"q": "Tal provided me with wise advice. He listened to me and asked great questions that showed an advanced level of understanding and attention, and then gave very helpful advice and shared his ways of thinking on the matter. I was most impressed by his methodical way of thinking and experimenting in sales.", "name": "Neriya Rosner", "role": "Founder & CEO", "company": "SpecBite", "tag": "go-to-market-strategy", "photo": "/img/testimonials/neriya-rosner.jpg"},
 {"q": "Tal is a real professional! I've asked him to provide an opinion on commercialization of a medical device product. What I received is a deep dive into entire world of terms, key players and possibilities and, on the other hand, a clear recommendation and a guidance for proper planning of my next steps.", "name": "Yakov Nedlin", "role": "Founder", "company": "LIBACCORD", "tag": "market-entry", "photo": "/img/testimonials/yakov-nedlin.jpg"},
 {"q": "I had a great experience working with Tal Paperin. He gave me some great insight and ideas about how to take my business to the next dimension. He provides an array of services to help businesses make more money from domestic or international expansion. I would recommend using them for sure.", "name": "Sherman Barnes II", "role": "Head of Sales & Marketing", "company": "Trio Trucking", "tag": "market-entry", "photo": "/img/testimonials/sherman-barnes-ii.jpg"},
 {"q": "KSW is an incredible resource, but more importantly, there are very few people as talented as Tal when it comes to sales strategy. He helped close a publicly traded company for my startup.", "name": "Huw Nierenberg", "role": "Co-Founder", "company": "ePropertyCare", "tag": "fractional-cro", "photo": "/img/testimonials/huw-nierenberg.jpg"},
 {"q": "I had the pleasure to work with Tal. I can tell that Tal is a great team player, very energetic and enthusiastic to get things done. He was always willing to help and share his experience in international sales and project management. He is practical, analytic with solving skills and nice to have around!", "name": "Luisa Arroyave", "role": "Senior Manager", "company": "Walmart Global Sourcing", "tag": "market-entry", "photo": "/img/testimonials/luisa-arroyave.jpg"},
 {"q": "Tal Paperin has everything you want and need in a solutions consulting company: years of experience in both pre and post sales, connections in all the BRIC countries, knowledge in how to standout in many different types of markets, and more ways to increase your company's profitability.", "name": "Gabriel Heifets", "role": "HW Lead Engineer", "company": "Annapurna Labs (Amazon)", "tag": "market-entry", "photo": "/img/testimonials/gabriel-heifets.jpg"},
 {"q": "Tal has the knowledge and deep understanding to analyze and map the market competition in order to promote the comparative advantage for any category of products. Tal is the one you would like to have as your team leader.", "name": "Barak Kav", "role": "CEO", "company": "TAG Dental", "tag": "go-to-market-strategy", "photo": "/img/testimonials/barak-kav.jpg"},
 {"q": "Tal is extremely enthusiastic about his job, smart, professional and thorough, and was a pleasure to work with.", "name": "Daniel Weiser", "role": "Sr. Director BD & Sales, Americas", "company": "Silicom Ltd.", "tag": "fractional-cro", "photo": "/img/testimonials/daniel-weiser.jpg"},
 {"q": "Tal has great negotiating skills and secured several big deals for the company. He is incredibly capable and is a huge asset to any company that he works for.", "name": "Laura Gillman", "role": "", "company": "Meshi Pharm", "tag": "fractional-cro", "photo": ""},
 {"q": "I had the pleasure of meeting Tal to discuss strategies and ideas for developing my business and improving sales. Tal had excellent ideas and opinions that I will be putting to use in the coming months. I highly recommend Tal for your business.", "name": "Daniel Tarlow", "role": "", "company": "GK8 by Galaxy", "tag": "go-to-market-strategy", "photo": "/img/testimonials/daniel-tarlow.jpg"},
 {"q": "After great achievements in a rapidly growing company (Mobileye, an Intel Company), Tal listened carefully and gave concise, precise advice of great value, on negotiating projects by added value and expanding global markets through more personalised channels. He has a rare talent for thinking in-depth and forward.", "name": "Judith Rozen-Romano", "role": "Founder & CEO", "company": "Divine Italy", "tag": "distributor-channel-recruitment", "photo": ""},
 {"q": "Having Tal as a contact is valuable. Having him in your corner is priceless. He is always prepared with insights and market focus, so every minute with him is energised and filled with possibility. He extracts the essence of any business idea and distils it into action and a roadmap to your goal.", "name": "Daniel Zatman", "role": "Co-Founder", "company": "Qii78", "tag": "go-to-market-strategy", "photo": "/img/testimonials/daniel-zatman.jpg"},
 {"q": "I worked alongside Tal on the BizDev and Sales team at TAG Dental. I was always impressed by his professionalism and personal qualities. Tal brings creative problem-solving, wide cross-discipline knowledge and a willingness to do whatever it takes to get a productive result.", "name": "Bar Libach", "role": "Global Head of Sales & BD", "company": "MIS Implants Technologies", "tag": "sales-team-building", "photo": "/img/testimonials/bar-libach.jpg"},
 {"q": "I needed sound, no-bs advice on sales and marketing for a new business. Tal didn't hesitate to help, and his advice really put things into perspective. It became obvious that Tal is not only an expert in his field, but also a gracious person willing to help others.", "name": "Hans Bronkhorst", "role": "IT Manager", "company": "Bauwatch Group", "tag": "go-to-market-strategy", "photo": "/img/testimonials/hans-bronkhorst.jpg"},
 {"q": "I had the honor of working with Tal for over a year. He proved himself professional, dedicated and a valuable asset. Tal is methodical with great attention to detail, combined with the ability to see the big picture and excellent people skills, which made him a pivotal figure in every project.", "name": "Yair Rosenzweig", "role": "VP Sales & Services", "company": "Galcon", "tag": "fractional-cro", "photo": "/img/testimonials/yair-rosenzweig.jpg"},
 {"q": "We recently had Tal direct a seminar on fundraising for Chabad on Campus Israel rabbis. The feedback was overwhelmingly positive. The presentation was flawless, engaging and very practical. Tal is a pleasure to work with, and his skills in marketing are second to none.", "name": "Rabbi Nosson Rodin", "role": "Director", "company": "Chabad on Campus", "tag": "go-to-market-strategy", "photo": "/img/testimonials/rabbi-nosson-rodin.jpg"},
 {"q": "I had a consult with Tal on LinkedIn and sales strategies and could not recommend him more. He told me clearly and concisely exactly what my next steps were to capitalize on LinkedIn further. He has a huge wealth of knowledge and gives it over in a way that is easy to understand and implement. Highly recommend!", "name": "Elisheva Hudson", "role": "Documentary Filmmaker", "company": "Hudson Films", "tag": "go-to-market-strategy", "photo": "/img/testimonials/elisheva-hudson.jpg"},
 {"q": "Tal is smart and full of experience. He gave us great insight and ideas on how to make sure we covered all our sales angles, with in-depth market research.", "name": "Sam Ginzberg", "role": "Revenue Architect", "company": "SG Consulting", "tag": "go-to-market-strategy", "photo": "/img/testimonials/sam-ginzberg.jpg"},
 {"q": "Before I knew Tal I did not know the world of global sales. Tal introduced me to a new world I was not aware of and impressed me with his deep knowledge. I am sure he is one of the experts in his field, and I would love to recommend him as one of the best salespeople in the world.", "name": "Ariel Perets", "role": "Owner & CEO", "company": "AP Engineering", "tag": "market-entry", "photo": "/img/testimonials/ariel-perets.jpg"},
 {"q": "I had a very helpful discussion with Tal. We took stock of where my startup venture is now, and I got valuable feedback and further guidance on the business validation path I have been pursuing, the results obtained, and what to focus on next to advance the venture.", "name": "Daniel Gross, PhD", "role": "Applied Researcher & Consultant", "company": "", "tag": "go-to-market-strategy", "photo": ""},
 {"q": "Tal Paperin has the uncanny ability to find lessons, especially sales lessons, in every little thing in life, and somehow apply them successfully to the business world. If you are looking for a sales professional who lives, eats and breathes sales, open a dialogue with him.", "name": "Phil Guimond", "role": "Senior DevSecOps Engineer", "company": "Optro", "tag": "fractional-cro", "photo": "/img/testimonials/phil-guimond.jpg"},
 {"q": "Tal's insights in business, especially sales, are amazing. I always look forward to reading his thoughts. They are sometimes witty and funny, but always very informative, and they show the forte of his years of experience.", "name": "Udo Kalu", "role": "Electro-Biomedical Engineer", "company": "St George's University Hospitals NHS", "tag": "go-to-market-strategy", "photo": "/img/testimonials/udo-kalu.jpg"},
 {"q": "Tal has a unique, cut-to-the-chase, no-nonsense style of helping clients find their target market, reach them, and position themselves so they get noticed. He goes the extra mile and gives continuous value, because he cares about your success. Do yourself a favor and reach out to him.", "name": "Dovid Urbach", "role": "Social Worker", "company": "Jerusalem Mental Health Center", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-urbach.jpg"},
 {"q": "As the Internet Department Manager at SOURCE, I worked closely with Tal. He has a great ability to communicate with people from around the globe, and his client support and management are exceptional. He is courteous and supportive, and his people skills are outstanding. Tal expanded our online presence by engaging our clients and leads, many of which he found himself. He is also an expert in information gathering and data mining: if it is out there, Tal will find it, sort it and present it in the best way possible.", "name": "John Dvir", "role": "Digital Marketing Manager", "company": "adactive", "tag": "go-to-market-strategy", "photo": "/img/testimonials/john-dvir.jpg"},
 {"q": "Tal is detail-oriented with a professional, easy-going attitude. He is very responsive and easy to work with. He quickly establishes credibility and confidence, and his straightforward manner makes him fun to work with.", "name": "Kasia Wenker", "role": "VP of Solutions Engineering", "company": "ITS Logistics", "tag": "fractional-cro", "photo": "/img/testimonials/kasia-wenker.jpg"},
 {"q": "Tal is our sales rep for SOURCE. He has been very helpful and very persistent about getting information to me in the format I requested. He has gone above and beyond for me. I highly recommend him.", "name": "Bonnie Meyers", "role": "Business Owner", "company": "Unstoppable Learning", "tag": "outsourced-sales", "photo": "/img/testimonials/bonnie-meyers.jpg"},
 {"q": "Tal is great to work with. He is very professional and highly motivated, and a great source of advice and guidance for moving your business forward.", "name": "Dovid Shaw", "role": "Director", "company": "WoW Discoveries", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-shaw.jpg"},
 {"q": "Tal is a take-charge person who presents creative ideas and communicates their benefits. He successfully developed several marketing plans for our company. Beyond being an asset to our sales efforts, he wrote effective script modules for our sales representatives and took a leadership role in sales meetings, inspiring and motivating other employees. I highly recommend Tal for any organization.", "name": "Ouri Fischel", "role": "VP Business Development", "company": "agrematch", "tag": "sales-team-building", "photo": "/img/testimonials/ouri-fischel.jpg"},
]

TESTIMONIALS_HE = [
 {"q": "הבאנו את טל פאפרין כ-VP Sales במיקור חוץ מהיום הראשון שלנו ב-KanduAi. הוא לא היה סתם יועץ, הוא תפקד כ-VP Sales אמיתי לכל דבר. הוא הגדיר את פרופיל הלקוח האידיאלי שלנו, בנה את ה-playbook לאאוטבאונד, גייס והכשיר אנשי SDR, והניע את תהליך האאוטבאונד שלנו פעמיים מאפס. אם אתם מייסדים שמנסים להניע או להניע מחדש מערך מכירות מאפס, טל הוא האיש שאתם רוצים לצידכם.", "name": "אריאל שמש", "role": "שותף מייסד ומנכ\"ל", "company": "KanduAI", "tag": "fractional-cro", "photo": "/img/testimonials/ariel-shemesh.jpg"},
 {"q": "העבודה עם טל היא תענוג צרוף. אני הבעלים והמנהל של עסק קטן בתחום ה-IoT, ויש לי מעט מאוד ניסיון במכירות ובשיווק. טל ידע לפתח עבורנו אסטרטגיה במהירות, להטמיע CRM, ולהתחיל לבנות ולהכשיר את צוות המכירות שלנו. אם אתם עסק קטן (או גדול) שצריך לעשות סדר ולקחת את המכירות והשיווק בידיים, טל הוא האיש שלכם.", "name": "תומאס רמרט", "role": "שותף מייסד ו-CTO", "company": "LoneStar Tracking", "tag": "outsourced-sales", "photo": "/img/testimonials/tommy-remmert.jpg"},
 {"q": "הוא היה מעורב. הוא התאמן איתנו, עבר יחד איתנו על עסקאות, אתגר את הדרך שבה ניגשנו לשיחות ... ההדרכה שלו הניבה תוצאות. היא הפכה אותנו לאנשי מכירות טובים יותר, שיפרה את השיחות שלנו עם לקוחות פוטנציאליים, ועזרה לנו לסגור יותר עסקאות. ... אלה שבאמת יודעים ללמד, להניע, לתכנן אסטרטגיה ועדיין להתחבר לצוות שלהם, נדירים יותר ממה שחושבים. טל הוא אחד מהמנהיגים האלה.", "name": "ריץ׳ מרטינז", "role": "Sr. Practice Growth Consultant", "company": "ClinicMind", "tag": "fractional-cro", "photo": "/img/testimonials/rich-martinez.jpg"},
 {"q": "אם אתם מחפשים מישהו שבאמת מבין מכירות, טל הוא הכתובת שלכם. התפיסה שלו לגבי תהליך המכירה הכולל, היכולת שלו להניע לקוח פוטנציאלי קדימה, וההבנה המדויקת שלו איך לדחוף את העסק שלכם להצלחה, הן פשוט נכס שאין לו מחיר. תעקבו אחריו. תקשיבו לו. קחו את העצות שלו, ותראו איך העסק שלכם צומח.", "name": "הלן גוטשטיין", "role": "דוברות ותקשורת ניהולית", "company": "", "tag": "go-to-market-strategy", "photo": "/img/testimonials/helen-gottstein.jpg"},
 {"q": "טל הוא אדם חרוץ ואיש סוד שניתן לסמוך עליו בעיניים עצומות. יש לי ניסיון איתו כלקוח, כשותף וגם כמי שעבד תחתיו באופן ישיר. הוא איש של מילה, ומספק בדיוק את מה שהוא מבטיח. כאיש מכירות ואסטרטג בחסד, אני ממליץ עליו בחום לכל חברה שמחפשת מנהל מכירות במיקור חוץ, מנהל ערוצי הפצה או אסטרטג עסקי.", "name": "סטיב ברטון", "role": "CRO", "company": "The Point Company", "tag": "fractional-cro", "photo": "/img/testimonials/steve-burton.jpg"},
 {"q": "העבודה עם טל השפיעה עלינו בצורה מטורפת. הוא עזר לנו להבין בדיוק איפה היו הבעיות בתהליך המכירה שלנו, וסיפק לנו מפת דרכים ברורה להגדלת המכירות על ידי יצירת נהלי עבודה (SOPs) מותאמים אישית והדגמה חיונית של כל שלב ושלב. הוא זמין מאוד ותקשורתי ברמות הגבוהות ביותר. מומלץ בחום.", "name": "אמיתי שטרן", "role": "מנכ\"ל", "company": "TypoDuctions ו-DRIFT", "tag": "go-to-market-strategy", "photo": "/img/testimonials/amitay-stern.jpg"},
 {"q": "טל הוא איש שיווק חד וחכם בצורה יוצאת דופן. בשיחה קצרה אחת, הוא הצליח להבין ולנתח בעיות מורכבות של הבנת שוק, ניתוח לקוחות ומיפוי צרכנים. הוא הביא לנו פתרונות מהירים ומעולים שעושים את העבודה בשטח.", "name": "ד\"ר דיוויד גלולה", "role": "מנהל מכון המחקר UED, מנכ\"ל ProUX", "company": "", "tag": "go-to-market-strategy", "photo": "/img/testimonials/david-gallula-ph-d.jpg"},
 {"q": "כבר בשיחת ייעוץ ראשונית של 15 דקות בלבד עם טל, הצלחתי לזהות גישות חדשות שאני בטוח שיובילו לעלייה משמעותית בפגישות מוצלחות עם לקוחות פוטנציאליים. טל היה חברותי, נדיב בזמנו וקשוב מאוד. השיחה הזו הייתה אחד הכלים הכי יעילים ומועילים שנתקלתי בהם.", "name": "מייקל טייכברג", "role": "מייסד", "company": "InventivHR", "tag": "sales-team-building", "photo": "/img/testimonials/michael-teichberg.jpg"},
 {"q": "טל נתן לי עצות חכמות ומדויקות. הוא הקשיב לי, שאל שאלות מצוינות שהראו רמת הבנה ותשומת לב גבוהה, ואז נתן עצות מועילות במיוחד ושיתף את דרכי החשיבה שלו בנושא. מה שהכי הרשים אותי זו הדרך המתודית שבה הוא חושב ומנווט בעולם המכירות.", "name": "נריה רוזנר", "role": "מייסדת ומנכ\"לית", "company": "SpecBite", "tag": "go-to-market-strategy", "photo": "/img/testimonials/neriya-rosner.jpg"},
 {"q": "טל הוא מקצוען אמיתי! ביקשתי ממנו חוות דעת על מסחור של מוצר בתחום המכשור הרפואי. מה שקיבלתי היה צלילת עומק מטורפת לכל עולם המושגים, שחקני המפתח והאפשרויות, ומצד שני, המלצה ברורה והכוונה מדויקת לתכנון השלבים הבאים שלי.", "name": "יעקב נדלין", "role": "מייסד", "company": "LIBACCORD", "tag": "market-entry", "photo": "/img/testimonials/yakov-nedlin.jpg"},
 {"q": "הייתה לי חוויה מדהימה בעבודה עם טל פאפרין. הוא נתן לי תובנות ורעיונות מעולים איך לקחת את העסק שלי לשלב הבא. הוא מציע מגוון רחב של שירותים שעוזרים לעסקים להרוויח יותר כסף מהתרחבות מקומית או בינלאומית. אני ממליץ לעבוד איתו ללא ספק.", "name": "שרמן בארנס השני", "role": "מנהל מכירות ושיווק", "company": "Trio Trucking", "tag": "market-entry", "photo": "/img/testimonials/sherman-barnes-ii.jpg"},
 {"q": "KSW היא משאב מדהים, אבל חשוב מכך, יש מעט מאוד אנשים מוכשרים כמו טל כשזה מגיע לאסטרטגיית מכירות. הוא עזר לסטארטאפ שלי לסגור עסקה עם חברה הנסחרת בבורסה.", "name": "היו ניירנברג", "role": "שותף מייסד", "company": "ePropertyCare", "tag": "fractional-cro", "photo": "/img/testimonials/huw-nierenberg.jpg"},
 {"q": "היה לי העונג לעבוד עם טל. אני יכולה להגיד שטל הוא שחקן צוות מדהים, מלא באנרגיה ורעב להשיג תוצאות. הוא תמיד שמח לעזור ולשתף מהניסיון שלו במכירות בינלאומיות ובניהול פרויקטים. הוא מעשי, אנליטי, בעל יכולת פתרון בעיות גבוהה, ופשוט אדם שכיף לעבוד לצידו!", "name": "לואיזה ארויאבה", "role": "מנהלת בכירה", "company": "Walmart Global Sourcing", "tag": "market-entry", "photo": "/img/testimonials/luisa-arroyave.jpg"},
 {"q": "לטל פאפרין יש כל מה שאתם רוצים וצריכים מחברת ייעוץ פתרונות: שנים של ניסיון ב-Pre-sales וב-Post-sales, קשרים ענפים בכל מדינות ה-BRIC, ידע מעשי איך להבליט את העסק שלכם בסוגים שונים של שווקים, והמון דרכים להגדיל את הרווחיות של החברה שלכם.", "name": "גבריאל הייפץ", "role": "מהנדס חומרה מוביל", "company": "Annapurna Labs (Amazon)", "tag": "market-entry", "photo": "/img/testimonials/gabriel-heifets.jpg"},
 {"q": "לטל יש את הידע וההבנה העמוקה הדרושים כדי לנתח ולמפות את תחרות השוק, במטרה לקדם את היתרון היחסי של כל קטגוריית מוצרים. טל הוא בדיוק האדם שאתם רוצים שיוביל את הצוות שלכם.", "name": "ברק קב", "role": "מנכ\"ל", "company": "TAG Dental", "tag": "go-to-market-strategy", "photo": "/img/testimonials/barak-kav.jpg"},
 {"q": "טל מלא בתשוקה ואנרגיה לעבודה שלו, הוא חכם, מקצועי ויסודי בצורה בלתי רגילה, והיה פשוט תענוג לעבוד איתו.", "name": "דניאל וייזר", "role": "מנהל בכיר BD ומכירות, אמריקה", "company": "Silicom Ltd.", "tag": "fractional-cro", "photo": "/img/testimonials/daniel-weiser.jpg"},
 {"q": "לטל יש יכולות ניהול משא ומתן פנומנליות, והוא סגר כמה עסקאות ענק עבור החברה. הוא מוכשר ברמות הגבוהות ביותר ומהווה נכס אדיר לכל חברה שהוא עובד איתה.", "name": "לורה גילמן", "role": "", "company": "Meshi Pharm", "tag": "fractional-cro", "photo": ""},
 {"q": "היה לי העונג להיפגש עם טל ולדבר על אסטרטגיות ורעיונות לפיתוח העסק ולשיפור המכירות. לטל היו רעיונות ודעות מעולים שאני איישם בחודשים הקרובים. אני ממליץ בחום על טל לעסק שלכם.", "name": "דניאל תרלו", "role": "", "company": "GK8 by Galaxy", "tag": "go-to-market-strategy", "photo": "/img/testimonials/daniel-tarlow.jpg"},
 {"q": "אחרי הישגים גדולים בחברה שצמחה במהירות (Mobileye, חברת אינטל), טל הקשיב בקפידה ונתן עצות תמציתיות ומדויקות בעלות ערך רב, על ניהול פרויקטים לפי ערך מוסף והרחבת שווקים גלובליים דרך ערוצים מותאמים אישית. יש לו כישרון נדיר לחשוב לעומק וקדימה.", "name": "ג׳ודית רוזן-רומנו", "role": "מייסדת ומנכ״לית", "company": "Divine Italy", "tag": "distributor-channel-recruitment", "photo": ""},
 {"q": "טל כאיש קשר הוא נכס. טל לצידך לא יסולא בפז. הוא תמיד מגיע עם תובנות ומיקוד שוק, וכל דקה איתו מלאת אנרגיה ואפשרויות. הוא מזקק את המהות של כל רעיון עסקי והופך אותו לפעולה ולמפת דרכים ליעד שלך.", "name": "דניאל זטמן", "role": "שותף מייסד", "company": "Qii78", "tag": "go-to-market-strategy", "photo": "/img/testimonials/daniel-zatman.jpg"},
 {"q": "עבדתי לצד טל בצוות ה-BizDev והמכירות ב-TAG Dental. תמיד התרשמתי מהמקצועיות ומהתכונות האישיות שלו. טל מביא פתרון בעיות יצירתי, ידע רחב בין-תחומי ונכונות לעשות מה שצריך כדי להגיע לתוצאה.", "name": "בר ליבך", "role": "ראש מכירות ופיתוח עסקי גלובלי", "company": "MIS Implants", "tag": "sales-team-building", "photo": "/img/testimonials/bar-libach.jpg"},
 {"q": "הייתי צריך עצה כנה ובלי בולשיט על מכירות ושיווק לעסק חדש. טל לא היסס לעזור, והעצה שלו באמת סידרה לי את הראש. התברר שטל הוא לא רק מומחה בתחומו אלא גם אדם נדיב שמוכן לעזור לאחרים.", "name": "הנס ברונקהורסט", "role": "מנהל IT", "company": "Bauwatch Group", "tag": "go-to-market-strategy", "photo": "/img/testimonials/hans-bronkhorst.jpg"},
 {"q": "היה לי הכבוד לעבוד עם טל במשך יותר משנה. הוא הוכיח את עצמו כמקצוען, מסור ונכס יקר. טל מתודי עם תשומת לב יוצאת דופן לפרטים, יחד עם יכולת לראות את התמונה הגדולה וכישורי אנשים מעולים, מה שהפך אותו לדמות מרכזית בכל פרויקט.", "name": "יאיר רוזנצוויג", "role": "סמנכ״ל מכירות ושירות", "company": "Galcon", "tag": "fractional-cro", "photo": "/img/testimonials/yair-rosenzweig.jpg"},
 {"q": "טל העביר עבורנו סמינר בנושא גיוס כספים לרבני חב\"ד בקמפוסים בישראל. המשובים היו חיוביים בצורה גורפת. ההרצאה הייתה חלקה, מרתקת ומאוד פרקטית. טל הוא תענוג לעבוד איתו, וכישורי השיווק שלו הם מהטובים שיש.", "name": "הרב נתן רודין", "role": "מנהל", "company": "Chabad on Campus", "tag": "go-to-market-strategy", "photo": "/img/testimonials/rabbi-nosson-rodin.jpg"},
 {"q": "התייעצתי עם טל על אסטרטגיות מכירה ו-LinkedIn, ואני לא יכולה להמליץ עליו מספיק. הוא אמר לי בצורה ברורה ותמציתית בדיוק מה הצעדים הבאים שלי כדי למנף את LinkedIn הלאה. יש לו ים של ידע, והוא מעביר אותו בצורה שקל להבין וליישם. ממליצה בחום!", "name": "אלישבע הדסון", "role": "יוצרת סרטים תיעודיים", "company": "Hudson Films", "tag": "go-to-market-strategy", "photo": "/img/testimonials/elisheva-hudson.jpg"},
 {"q": "טל חכם ומלא ניסיון. הוא נתן לנו תובנות ורעיונות מעולים איך לוודא שכיסינו את כל זוויות המכירה, עם מחקר שוק מעמיק.", "name": "סם גינזברג", "role": "אדריכל הכנסות", "company": "SG Consulting", "tag": "go-to-market-strategy", "photo": "/img/testimonials/sam-ginzberg.jpg"},
 {"q": "לפני שהכרתי את טל לא הכרתי את עולם המכירות הגלובליות. טל פתח לי עולם חדש שלא הכרתי והרשים אותי בידע העמוק שלו. אני בטוח שהוא אחד המומחים בתחומו, ואשמח להמליץ עליו כאחד מאנשי המכירות הטובים בעולם.", "name": "אריאל פרץ", "role": "בעלים ומנכ\"ל", "company": "AP Engineering", "tag": "market-entry", "photo": "/img/testimonials/ariel-perets.jpg"},
 {"q": "ניהלתי שיחה מאוד מועילה עם טל. עשינו סדר באיפה הסטארטאפ שלי נמצא היום, וקיבלתי משוב חשוב והכוונה נוספת על מסלול האימות העסקי שאני מוביל, על התוצאות שהשגתי, ועל מה להתמקד בשלב הבא כדי לקדם את המיזם.", "name": "דניאל גרוס", "role": "חוקר ויועץ", "company": "", "tag": "go-to-market-strategy", "photo": ""},
 {"q": "לטל פאפרין יש יכולת מדהימה למצוא לקחים, במיוחד לקחי מכירות, בכל דבר קטן בחיים, ואיכשהו ליישם אותם בהצלחה בעולם העסקי. אם אתם מחפשים איש מכירות שחי, אוכל ונושם מכירות, פתחו איתו שיחה.", "name": "פיל גימונד", "role": "מהנדס DevSecOps בכיר", "company": "Optro", "tag": "fractional-cro", "photo": "/img/testimonials/phil-guimond.jpg"},
 {"q": "התובנות של טל בעסקים, ובמיוחד במכירות, מדהימות. אני תמיד מצפה לקרוא את המחשבות שלו. לפעמים הן שנונות ומצחיקות, אבל תמיד מאוד מלמדות, ומשקפות את החוזק של שנות הניסיון שלו.", "name": "אודו קאלו", "role": "מהנדס ביו-רפואי", "company": "St George's University Hospitals NHS", "tag": "go-to-market-strategy", "photo": "/img/testimonials/udo-kalu.jpg"},
 {"q": "לטל יש סגנון ייחודי, ישיר ובלי שטויות, של לעזור ללקוחות למצוא את קהל היעד שלהם, להגיע אליו, ולמצב את עצמם כך שיבחינו בהם. הוא הולך את הקילומטר הנוסף ונותן ערך מתמשך, כי אכפת לו מההצלחה שלכם. תעשו לעצמכם טובה ופנו אליו.", "name": "דוד אורבך", "role": "עובד סוציאלי", "company": "Jerusalem Mental Health Center", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-urbach.jpg"},
 {"q": "כמנהל מחלקת האינטרנט ב-SOURCE עבדתי בצמוד לטל. יש לו יכולת מעולה לתקשר עם אנשים מכל העולם, והתמיכה והניהול שלו מול לקוחות יוצאי דופן. הוא אדיב ותומך, וכישורי האנוש שלו מצוינים. טל הרחיב את הנוכחות הדיגיטלית שלנו דרך מעורבות עם לקוחות ולידים, רבים מהם הוא מצא בעצמו. הוא גם מומחה באיסוף מידע וב-Data Mining: אם זה קיים שם בחוץ, טל ימצא, ימיין ויציג את זה בצורה הטובה ביותר.", "name": "ג'ון דביר", "role": "מנהל שיווק דיגיטלי", "company": "adactive", "tag": "go-to-market-strategy", "photo": "/img/testimonials/john-dvir.jpg"},
 {"q": "טל הוא איש פרטים עם גישה מקצועית ונעימה. הוא מאוד זמין וקל לעבודה. הוא מבסס במהירות אמינות וביטחון, והישירות שלו הופכת את העבודה איתו לכיף.", "name": "קסיה ונקר", "role": "סמנכ\"לית הנדסת פתרונות", "company": "ITS Logistics", "tag": "fractional-cro", "photo": "/img/testimonials/kasia-wenker.jpg"},
 {"q": "טל הוא איש המכירות שלנו ב-SOURCE. הוא היה מאוד מועיל ומאוד עקבי בלהביא לי את המידע בדיוק בפורמט שביקשתי. הוא עשה למעני הרבה מעבר למצופה. אני ממליצה עליו בחום.", "name": "בוני מאיירס", "role": "בעלת עסק", "company": "Unstoppable Learning", "tag": "outsourced-sales", "photo": "/img/testimonials/bonnie-meyers.jpg"},
 {"q": "טל הוא תענוג לעבוד איתו. הוא מאוד מקצועי ובעל מוטיבציה גבוהה, ומקור מצוין לעצה והכוונה בקידום העסק שלכם.", "name": "דוד שו", "role": "מנהל", "company": "WoW Discoveries", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-shaw.jpg"},
 {"q": "טל הוא אדם שלוקח אחריות, מציג רעיונות יצירתיים ויודע להעביר את הערך שבהם. הוא פיתח עבורנו בהצלחה כמה תוכניות שיווק. מעבר לזה שהיה נכס למאמצי המכירות שלנו, הוא כתב מודולי תסריטים אפקטיביים לנציגי המכירות ולקח תפקיד מוביל בישיבות מכירות, כשהוא מעורר השראה ומניע עובדים אחרים. אני ממליץ בחום על טל לכל ארגון.", "name": "אורי פישל", "role": "סמנכ\"ל פיתוח עסקי", "company": "agrematch", "tag": "sales-team-building", "photo": "/img/testimonials/ouri-fischel.jpg"},
]


LOGOS = [
 ("hirematch","HireMatch AI"),("vectorize","Vectorize"),("clinicmind","ClinicMind"),
 ("tagmedical","TAG Medical"),("teva","Teva Pharmaceuticals"),
 ("palram","Palram Applications"),("motorad","MotoRad"),("source","Source"),("bt9","BT9"),
 ("limat","Limat Group"),
 ("lonestar","LoneStar Tracking"),("supra","Supra National Express"),
 ("bacsoft","Bacsoft"),("ofekpoint","OfekPoint"),("headcount","Headcount ERC"),
 ("structshare","StructShare"),("hiarc","HiArc"),("cornsys","Cornsys"),
 ("epropertycare","ePropertyCare"),("chabad","Chabad on Campus"),
 ("kanduai","KanduAI"),("plasticplace","PlasticPlace"),
 ("typoductions","TypoDuctions"),("drift","DRIFT"),
 ("agat","AGAT Software"),("bmt","BMT Diagnostics"),("oppeo","Oppeo"),
 ("valmar","Valmar Surgical"),("appsgrade","AppsGrade"),("nuversys","NuVersys"),
 ("substrata","Substrata"),("royalcare","Royal Care"),("theboxny","TheBoxNY"),
]


def render_logo_wall(logos):
    # Two-row auto-scrolling carousel. Each row's set is duplicated so the
    # CSS translateX(-50%) loop is seamless; the duplicate is aria-hidden.
    mid = (len(logos) + 1) // 2
    rows = [logos[:mid], logos[mid:]]

    def track(items, cls):
        # NOT loading="lazy": the track is a transform:translateX marquee, so every logo is laid
        # out off-screen to the right (width:max-content) and the browser never fires lazy-load for
        # them as the animation scrolls them in - they'd stay blank #f5f5f5 cards. Load eagerly
        # (small logos) and decode async so the whole wall renders.
        base = "".join(
            '<img src="/logos/%s.jpg" alt="%s" decoding="async" />' % (slug, esc(name))
            for slug, name in items)
        dup = "".join(
            '<img src="/logos/%s.jpg" alt="" aria-hidden="true" decoding="async" />' % slug
            for slug, _ in items)
        return '<div class="proof-track %s">%s%s</div>' % (cls, base, dup)

    return ('<div class="proof-carousel" aria-label="Companies Tal has built sales for">%s%s</div>'
            % (track(rows[0], "ltr"), track(rows[1], "rtl")))


def render_gallery(alt="Tal Paperin in the field"):
    d = os.path.join(ROOT, "img", "gallery")
    if not os.path.isdir(d):
        return ""
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(".jpg"))
    tiles = "".join(
        '<img src="/img/gallery/%s" alt="%s" loading="lazy" />' % (f, esc(alt))
        for f in files)
    return '<div class="photo-gallery">%s</div>' % tiles


def render_quote_grid(quotes, he=False):
    return '<div class="rec-quotes">%s</div>' % "".join(_tcard(t, he) for t in quotes)


REC_PAGE_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Recommendations &amp; Clients | Tal Paperin, Fractional CRO</title>
  <meta name="description" content="What founders and executives say about working with Tal Paperin, and the companies he has built sales for, from multinationals to startups, on five continents." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/recommendations" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/recommendations" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/recommendations" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/recommendations" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/recommendations" />
  <meta property="og:title" content="Recommendations &amp; Clients | Tal Paperin" />
  <meta property="og:description" content="In their words: founders and executives on working with Tal Paperin, plus the companies he has built sales for." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Recommendations &amp; Clients | Tal Paperin" />
  <meta name="twitter:description" content="In their words: founders and executives on working with Tal Paperin." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">Recommendations</p>
        <h1>Don't take my word for it. Take theirs.</h1>
        <p class="lead">From multinational corporations to small startups, here are the companies I have built sales for, and what the founders and executives who worked with me actually say.</p>
        <h2 class="cases-recs-h">Companies I have built sales for</h2>
{logos}
        <h2 class="cases-recs-h">In their words</h2>
{quotes}
{cta}
        <div class="svc-related">See the <a href="/case-studies">case studies</a> behind these, or explore the <a href="/services/">services</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''

REC_PAGE_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>המלצות ולקוחות | טל פאפרין, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</title>
  <meta name="description" content="מה מייסדים ומנהלים אומרים על עבודה עם טל פאפרין, והחברות שבנה להן מכירות, מתאגידים רב-לאומיים ועד סטארטאפים, בחמש יבשות." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/recommendations" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/recommendations" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/recommendations" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/recommendations" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/recommendations" />
  <meta property="og:title" content="המלצות ולקוחות | טל פאפרין" />
  <meta property="og:description" content="בלשונם: מייסדים ומנהלים על עבודה עם טל פאפרין, והחברות שבנה להן מכירות." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">המלצות</p>
        <h1>אל תאמינו לי. תאמינו להם.</h1>
        <p class="lead">מתאגידים רב-לאומיים ועד סטארטאפים קטנים, אלה החברות שבניתי להן מכירות, ומה שהמייסדים והמנהלים שעבדו איתי באמת אומרים.</p>
        <h2 class="cases-recs-h">חברות שבניתי להן מכירות</h2>
{logos}
        <h2 class="cases-recs-h">בלשונם</h2>
{quotes}
{cta}
        <div class="svc-related">ראו את <a href="/he/case-studies">מקרי המבחן</a> שמאחורי אלה, או עיינו ב<a href="/he/services/">שירותים</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


CS_PAGE_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Case Studies | Tal Paperin, Fractional CRO</title>
  <meta name="description" content="Real results from a fractional CRO: building sales engines, opening markets and closing complex deals for B2B companies across startups, IoT, manufacturing, medical and SaaS, on five continents." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/case-studies" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/case-studies" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/case-studies" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/case-studies" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/case-studies" />
  <meta property="og:title" content="Case Studies | Tal Paperin" />
  <meta property="og:description" content="Real companies, real problems, real ownership. Sales engines built, markets opened, complex deals closed." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Case Studies | Tal Paperin" />
  <meta name="twitter:description" content="Real companies, real problems, real ownership." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Case Studies</p>
        <h1>Brought in to build the engine, not just advise on it.</h1>
        <p class="lead">Real companies, real problems, real ownership. Here is what I have built and fixed, across startups, IoT, manufacturing, medical devices, retail and SaaS, on five continents.</p>
        <div class="cases-list">
{cases}
        </div>
        <h2 class="cases-recs-h">What clients say</h2>
{testimonials}
        <h2 class="cases-recs-h">On the ground, on five continents</h2>
{gallery}
{cta}
        <div class="svc-related">See the <a href="/services/">services</a> behind these, or <a href="/blog/">read the blog</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''

CS_PAGE_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>מקרי מבחן | טל פאפרין, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</title>
  <meta name="description" content="תוצאות אמיתיות: בניית מנועי מכירות, פתיחת שווקים וסגירת עסקאות מורכבות לחברות B2B, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי ו-SaaS, בחמש יבשות." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/case-studies" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/case-studies" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/case-studies" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/case-studies" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/case-studies" />
  <meta property="og:title" content="מקרי מבחן | טל פאפרין" />
  <meta property="og:description" content="חברות אמיתיות, בעיות אמיתיות, אחריות אמיתית. מנועי מכירות שנבנו, שווקים שנפתחו, עסקאות מורכבות שנסגרו." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">מקרי מבחן</p>
        <h1>הגעתי כדי לבנות את המנוע, לא רק לייעץ עליו.</h1>
        <p class="lead">חברות אמיתיות, בעיות אמיתיות, אחריות אמיתית. הנה מה שבניתי ותיקנתי, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי, קמעונאות ו-SaaS, בחמש יבשות.</p>
        <div class="cases-list">
{cases}
        </div>
        <h2 class="cases-recs-h">מה הלקוחות אומרים</h2>
{testimonials}
        <h2 class="cases-recs-h">בשטח, בחמש יבשות</h2>
{gallery}
{cta}
        <div class="svc-related">ראו את <a href="/he/services/">השירותים</a> שמאחורי אלה, או <a href="/he/blog/">קראו את הבלוג</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


SERVICE_CASE_EN = {
 "fractional-cro":{"company":"KanduAI","anchor":"kanduai","line":"An early-stage AI startup with a product and no way to sell it: no pipeline, no process, no team. I came in as Fractional VP of Sales and owned the revenue side end to end.","bullets":["Defined the ICP, positioning and messaging, then built the outbound motion from zero","Hired, trained and managed the SDR team","Relaunched the entire go-to-market through two product pivots without losing momentum"],"result":"A working outbound engine, rebuilt from scratch through a pivot, with speed and precision."},
 "outsourced-sales":{"company":"LoneStar Tracking","anchor":"lonestar","line":"Strong marketing generating real demand, a sales engine that was not converting it, and founders who had never sold for a living. I built and ran the entire sales side as outsourced leadership.","bullets":["Built the sales strategy, process, playbook and pipeline from scratch","Selected and implemented the CRM and the full sales stack","Recruited, trained and ran the team day to day"],"result":"Full VP-level sales leadership at a fraction of the cost of a hire."},
 "go-to-market-strategy":{"company":"Bacsoft","anchor":"bacsoft","line":"An Israeli IIoT company, backed by Japan's SUN Corp, that needed a real global go-to-market: strategy, a channel across continents, and complex public-sector deals. I owned all of it.","bullets":["Built the global sales strategy and the distributor network worldwide","Ran direct B2B sales of SaaS, hardware and services","Led B2G across long RFI and RFQ cycles with governments and enterprises"],"result":"A global channel and a B2G pipeline, built for complex IIoT sold worldwide."},
 "sales-team-building":{"company":"KanduAI","anchor":"kanduai","line":"A startup with no sales team and no playbook for one. I built the team and the motion from zero, and kept rebuilding it as the product pivoted.","bullets":["Hired and trained the SDR team from scratch","Built the outbound playbook the reps actually ran","Rebuilt the motion through two pivots without losing the team"],"result":"A trained team running a real outbound playbook, not improvising every call."},
 "distributor-channel-recruitment":{"company":"Palram","anchor":"palram","line":"A global manufacturer convinced there was no money in Eastern Europe, so they stayed out. I went and tested the assumption against the real channel on the ground.","bullets":["Mapped the channel and the real decision-makers in the territory","Led every negotiation personally","Signed multiple distributors and retail chains across the region"],"result":"Multiple distributors and retail chains signed in a market they had written off."},
 "market-entry":{"company":"BT9","anchor":"bt9","line":"A company that needed an entire international sales operation built from the ground up, across three very different regions: the FSU, the EU and APAC.","bullets":["Built the sales operation from zero across all three regions","Ran direct sales of SaaS, hardware and services","Recruited and managed the distributor network, the team, post-sales and tech support"],"result":"A working international sales engine across three regions, built from scratch."},
 "b2g-public-sector":{"company":"Bacsoft","anchor":"bacsoft","line":"Led B2G for an Israeli IIoT company backed by Japan's SUN Corp: long, complex public-sector deals across the globe, where patience and process win and pitches do not.","bullets":["Ran RFIs, RFQs and complex government projects worldwide","Built the process to carry deals through long public-sector cycles","Aligned the channel and direct sales around the B2G motion"],"result":"A B2G pipeline built for complex public-sector deals worldwide."},
 "contract-negotiation":{"company":"Palram","anchor":"palram","line":"Opening a market a global manufacturer had abandoned meant negotiating every deal myself, with distributors and chains who had no reason to bet on a brand that had ignored them.","bullets":["Led every negotiation personally, start to finish","Structured terms that worked for both the company and the channel","Signed the distributors and chains that put product on the shelves"],"result":"Signed the distributors and chains that put product on the shelves."},
 "saas-sales":{"company":"Synergix","anchor":"synergix","line":"Scientific SaaS sold to the hardest buyer there is: universities, research labs and pharma. Technical, skeptical and impossible to bluff. I built the motion and ran it.","bullets":["Drove direct B2B SaaS sales into academia and pharma","Wrote the scripts and the playbook the reps used","Led the effort through a long, technical, high-trust cycle"],"result":"SaaS sold into US academia and pharma, a long, technical, high-trust sale."},
}

SERVICE_CASE_HE = {
 "fractional-cro":{"company":"KanduAI","anchor":"kanduai","line":"סטארטאפ AI בתחילת הדרך עם מוצר וללא דרך למכור אותו: בלי פייפליין, בלי תהליך, בלי צוות. נכנסתי כ-VP מכירות במיקור חוץ ולקחתי אחריות מלאה על צד ההכנסות.","bullets":["הגדרתי ICP, מיצוב ומסרים, ואז בניתי את תנועת האאוטבאונד מאפס","גייסתי, הכשרתי וניהלתי את צוות ה-SDR","השקתי מחדש את כל ה-GTM דרך שני פיבוטים בלי לאבד תאוצה"],"result":"מנוע אאוטבאונד עובד, שנבנה מחדש מאפס דרך פיבוט, במהירות ובדיוק."},
 "outsourced-sales":{"company":"LoneStar Tracking","anchor":"lonestar","line":"שיווק חזק שייצר ביקוש אמיתי, מנוע מכירות שלא המיר אותו, ומייסדים שמעולם לא מכרו למחייתם. בניתי והרצתי את כל צד המכירות כהובלה במיקור חוץ.","bullets":["בניתי את אסטרטגיית המכירות, התהליך, ה-Playbook והפייפליין מאפס","בחרתי והטמעתי CRM ומערך כלי מכירה מלא","גייסתי, הכשרתי וניהלתי את הצוות יום-יום"],"result":"הובלת מכירות מלאה ברמת VP בשבריר מעלות של גיוס."},
 "go-to-market-strategy":{"company":"Bacsoft","anchor":"bacsoft","line":"חברת IIoT ישראלית, בגיבוי SUN Corp מיפן, שהייתה צריכה Go-to-Market גלובלי אמיתי: אסטרטגיה, ערוץ בכמה יבשות ועסקאות מורכבות מול המגזר הציבורי. לקחתי אחריות על הכל.","bullets":["בניתי את אסטרטגיית המכירות הגלובלית ואת רשת המפיצים בעולם","הרצתי מכירה ישירה B2B של SaaS, חומרה ושירותים","הובלתי B2G לאורך מחזורי RFI ו-RFQ ארוכים מול ממשלות וארגונים"],"result":"רשת ערוצים גלובלית ופייפליין B2G, שנבנו ל-IIoT מורכב שנמכר בעולם."},
 "sales-team-building":{"company":"KanduAI","anchor":"kanduai","line":"סטארטאפ בלי צוות מכירות ובלי Playbook לאחד. בניתי את הצוות ואת התנועה מאפס, והמשכתי לבנות אותם מחדש כשהמוצר עבר פיבוט.","bullets":["גייסתי והכשרתי את צוות ה-SDR מאפס","בניתי את ה-Playbook לאאוטבאונד שהנציגים באמת הריצו","בניתי מחדש את התנועה דרך שני פיבוטים בלי לאבד את הצוות"],"result":"צוות מיומן שמריץ Playbook אאוטבאונד אמיתי, לא מאלתר כל שיחה."},
 "distributor-channel-recruitment":{"company":"Palram","anchor":"palram","line":"יצרן גלובלי שהיה בטוח שאין כסף במזרח אירופה, ולכן נמנע מלהיכנס. הלכתי ובחנתי את ההנחה מול הערוץ האמיתי בשטח.","bullets":["מיפיתי את הערוץ ואת מקבלי ההחלטות האמיתיים בטריטוריה","ניהלתי כל משא ומתן באופן אישי","החתמתי מספר מפיצים ורשתות קמעונאות באזור"],"result":"מספר מפיצים ורשתות קמעונאות שהוחתמו בשוק שהחברה כבר מחקה."},
 "market-entry":{"company":"BT9","anchor":"bt9","line":"חברה שהייתה צריכה מערך מכירות בינלאומי שלם שייבנה מהיסוד, בשלוש טריטוריות שונות מאוד: FSU, האיחוד האירופי ו-APAC.","bullets":["בניתי את מערך המכירות מאפס בכל שלוש הטריטוריות","הרצתי מכירה ישירה של SaaS, חומרה ושירותים","גייסתי וניהלתי את רשת המפיצים, הצוות, הפוסט-סייל והתמיכה הטכנית"],"result":"מנוע מכירות בינלאומי עובד בשלוש טריטוריות, שנבנה מאפס."},
 "b2g-public-sector":{"company":"Bacsoft","anchor":"bacsoft","line":"הובלתי B2G לחברת IIoT ישראלית בגיבוי SUN Corp מיפן: עסקאות ארוכות ומורכבות מול המגזר הציבורי בכל העולם, שבהן סבלנות ותהליך מנצחים, לא מצגות.","bullets":["הרצתי מכרזים, RFIs, RFQs ופרויקטים ממשלתיים מורכבים בעולם","בניתי את התהליך שמוביל עסקאות לאורך מחזורי מגזר ציבורי ארוכים","יישרתי את הערוץ ואת המכירה הישירה סביב תנועת ה-B2G"],"result":"פייפליין B2G שנבנה לעסקאות מורכבות מול המגזר הציבורי בעולם."},
 "contract-negotiation":{"company":"Palram","anchor":"palram","line":"לפתוח שוק שיצרן גלובלי כבר נטש דרש לנהל כל עסקה בעצמי, מול מפיצים ורשתות שלא הייתה להם שום סיבה להמר על מותג שהתעלם מהם.","bullets":["ניהלתי כל משא ומתן באופן אישי, מהתחלה ועד הסוף","בניתי תנאים שעבדו גם לחברה וגם לערוץ","החתמתי את המפיצים והרשתות שהביאו את המוצר למדפים"],"result":"החתמתי את המפיצים והרשתות שהביאו את המוצר למדפים."},
 "saas-sales":{"company":"Synergix","anchor":"synergix","line":"SaaS מדעי שנמכר לקונה הכי קשה שיש: אוניברסיטאות, מעבדות מחקר ופארמה. טכני, ספקן ובלתי אפשרי לבלוף. בניתי את התנועה והרצתי אותה.","bullets":["הרצתי מכירה ישירה B2B של SaaS לאקדמיה ולפארמה","כתבתי את התסריטים ואת ה-Playbook שהנציגים השתמשו בהם","הובלתי את המאמץ לאורך מחזור ארוך, טכני ועתיר אמון"],"result":"SaaS שנמכר לאקדמיה ולפארמה בארה״ב, מכירה ארוכה, טכנית ועתירת אמון."},
}


def render_case_callout(case, label, rlabel, more, url):
    if not case:
        return ""
    bullets = ""
    if case.get("bullets"):
        bullets = ('\n        <ul>'
                   + "".join("<li>%s</li>" % esc(b) for b in case["bullets"])
                   + '</ul>')
    href = (url + "#" + case["anchor"]) if case.get("anchor") else url
    return ('      <div class="svc-case">\n'
            '        <span class="svc-case-label">%s</span>\n'
            '        <h3>%s</h3>\n        <p>%s</p>%s\n'
            '        <p class="svc-case-result"><strong>%s:</strong> %s</p>\n'
            '        <a class="svc-case-link" href="%s">%s</a>\n      </div>'
            % (esc(label), esc(case["company"]), esc(case["line"]), bullets,
               esc(rlabel), esc(case["result"]), href, esc(more)))


# --- Lead-focused SEO landing pages (buying-intent + niche) ----------------

GUIDE_PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />
{hreflang}

  <meta property="og:type" content="article" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{h1} | Tal Paperin" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{h1} | Tal Paperin" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
  {faqld}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/">Home</a> / {h1}</p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
{faq}
{cta}
        <div class="svc-related">{related}</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


def render_faq(faqs, heading="Common questions"):
    """Return (visible HTML, FAQPage JSON-LD script tag) for a list of {q,a}."""
    if not faqs:
        return "", ""
    html = ['        <h2>%s</h2>' % esc(heading), '        <div class="faq">']
    items = []
    for f in faqs:
        html.append('          <details class="faq-item"><summary>%s</summary><p>%s</p></details>'
                     % (esc(f["q"]), esc(f["a"])))
        items.append('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                     % (_jsonesc(f["q"]), _jsonesc(f["a"])))
    html.append('        </div>')
    schema = ('<script type="application/ld+json">{"@context":"https://schema.org",'
              '"@type":"FAQPage","mainEntity":[%s]}</script>') % ",".join(items)
    return "\n".join(html), schema


SERVICE_FAQS_EN = {
 "pay-per-meeting":[
  {"q":"What is pay-per-meeting appointment setting?","a":"You pay for the qualified B2B sales meetings we book on your calendar, not for emails, leads or lists. We define your ICP, find and contact the right people, and book the meetings. You run and close them."},
  {"q":"How much does it cost?","a":"A one-time $2,500 setup to launch the campaign, then a monthly fee that tracks the meetings we book: $3,000 for up to 3, $4,500 for 4 to 6, $6,500 for 7 to 14, and $9,000 for 15 or more. Fewer meetings, you pay less."},
  {"q":"Do you count meetings booked or attended?","a":"Booked. If a prospect who matches the agreed ICP agrees to a date and time, that is a booked meeting, and it counts and is paid even if they later reschedule or no-show. That said, if a booked meeting no-shows we rebook it for you free of charge as a courtesy, since what you really want is the conversation."},
  {"q":"How is this different from a retainer SDR service?","a":"A retainer bills you the same whether you get meetings or not. This bills by results: the more meetings we book, the more we make, so our incentives are aligned with yours."}],
 "fractional-cro":[
  {"q":"What is a fractional CRO?","a":"A senior revenue leader who owns your strategy, team, pipeline, forecast and the number, part time, without a full-time CRO salary or a long-term lock-in."},
  {"q":"How is a fractional CRO different from a consultant?","a":"A consultant hands you a deck and leaves. I do the work, in the pipeline and the deals, and answer for the result."},
  {"q":"How much does a fractional CRO cost?","a":"$2,000 to $12,000 a month depending on how many hours a day you need, versus $250,000-plus for a full-time CRO, billed monthly with no contract."}],
 "outsourced-sales":[
  {"q":"What do I get with outsourced sales?","a":"A full team: native-speaking SDRs and AEs, senior leadership and a VP, hired, trained, managed and reported on, living outside your headcount."},
  {"q":"When does outsourcing beat hiring in-house?","a":"When building a team is too slow, too costly or too risky for your stage. You get a working engine in weeks, not six to twelve months, with no severance risk."},
  {"q":"Who runs the team?","a":"KSW Solutions, led by me. Twenty-plus years building and running B2B sales across the US, Europe, APAC and the former Soviet markets."}],
 "go-to-market-strategy":[
  {"q":"What does a go-to-market engagement include?","a":"ICP, positioning, pricing, channels, a playbook and a real forecast, then I help you execute it, not just hand over slides."},
  {"q":"Do you cover SaaS go-to-market?","a":"Yes, including SaaS GTM, as well as hardware, services and complex B2B."},
  {"q":"Will you execute or just advise?","a":"I build the plan and then lead the execution with you until you have pipeline, partners and first sales."}],
 "market-entry":[
  {"q":"How do you choose which market to enter?","a":"I assess the real pain, access, willingness to pay and competition, then build only where it makes sense, instead of spreading thin across everywhere."},
  {"q":"Have you actually opened foreign markets?","a":"Yes, repeatedly and for multiple companies, building teams, subsidiaries and support across the US, the EU, APAC and the former Soviet markets."},
  {"q":"Do you build the operation or just the plan?","a":"Both. I plan the entry and then build and run the team, the channel and the sales on the ground."}],
 "sales-team-building":[
  {"q":"What does sales team building include?","a":"Recruiting, hiring, training and managing your in-house SDRs, AEs and BDs on a playbook that makes them hit quota, and replacing who cannot."},
  {"q":"How is this different from outsourced sales?","a":"This builds your own in-house team that stays inside your company. Outsourced sales is a full team run for you outside your headcount."},
  {"q":"How fast can a new team be productive?","a":"I build the training and the playbook around your ICP so reps ramp on a system instead of improvising every call."}],
 "distributor-channel-recruitment":[
  {"q":"What do you do for channel and distributors?","a":"I find, vet, sign and manage the distributors, resellers and partners that open new territories and actually deliver."},
  {"q":"Direct sales or channel?","a":"Whichever fits the market. I decide and structure direct versus channel market by market."},
  {"q":"Have you built distributor networks before?","a":"Yes, across Europe, South America, APAC and the former Soviet markets, for IoT, manufacturing and medical companies."}],
 "b2g-public-sector":[
  {"q":"What does B2G sales involve?","a":"Running RFIs, RFQs, tenders and complex government and public-sector projects, mapping the real decision-makers and the procurement path."},
  {"q":"Have you closed government deals?","a":"Yes, internationally, including long RFI and RFQ cycles for industrial IoT into utilities and governments."},
  {"q":"Why is B2G different from commercial sales?","a":"Different buyer, different rules and a different timeline, and the cost of getting it wrong is a year lost. I know where these deals stall."}],
 "contract-negotiation":[
  {"q":"When should I bring you into a negotiation?","a":"The moment a high-value deal stalls on price, terms, legal or procurement, or whenever the deal is too important to risk on a hesitant close. The earlier I step in, the more leverage we keep."},
  {"q":"Do you take over the deal or coach my team?","a":"Either. I can lead the negotiation to signature myself, or sit alongside your team and steer the hard moments. Whatever gives the deal the best odds."},
  {"q":"What kind of deals have you closed?","a":"Complex, high-value B2B and B2G agreements across five continents, twenty-plus years of holding price and terms without losing the deal."}],
}

SERVICE_FAQS_HE = {
 "pay-per-meeting":[
  {"q":"מה זה תשלום לפי פגישה?","a":"אתם משלמים על פגישות המכירה המוכשרות ב-B2B שאנחנו קובעים ביומן שלכם, לא על מיילים, לידים או רשימות. אנחנו מגדירים ICP, מוצאים ופונים לאנשים הנכונים וקובעים את הפגישות. אתם מריצים וסוגרים אותן."},
  {"q":"כמה זה עולה?","a":"דמי הקמה חד פעמיים של 2,500 דולר להשקת הקמפיין, ואז תשלום חודשי שתואם למספר הפגישות שקבענו: 3,000 דולר עד 3, 4,500 דולר ל-4 עד 6, 6,500 דולר ל-7 עד 14, ו-9,000 דולר ל-15 ומעלה. פחות פגישות, אתם משלמים פחות."},
  {"q":"אתם סופרים פגישות שנקבעו או שהתקיימו?","a":"שנקבעו. אם פרוספקט שתואם ל-ICP שסיכמנו מסכים לתאריך ושעה, זו פגישה שנקבעה, והיא נספרת ומשולמת גם אם אחר כך ידחו או לא יגיעו. עם זאת, אם פגישה שנקבעה לא מתקיימת אנחנו קובעים אותה מחדש בלי חיוב כבונוס, כי מה שאתם באמת רוצים זו השיחה."},
  {"q":"במה זה שונה משירות SDR בריטיינר?","a":"ריטיינר גובה מכם אותו דבר בין אם קיבלתם פגישות ובין אם לא. כאן משלמים לפי תוצאה: ככל שנקבע יותר פגישות, כך נרוויח יותר, כך שהתמריצים שלנו מיושרים עם שלכם."}],
 "fractional-cro":[
  {"q":"מה זה סמנכ\"ל מכירות ופיתוח עסקי במיקור חוץ?","a":"מנהיג הכנסות בכיר שלוקח אחריות על האסטרטגיה, הצוות, הפייפליין, התחזית והתוצאות, במשרה חלקית, בלי שכר של משרה מלאה ובלי התחייבות ארוכת טווח."},
  {"q":"במה זה שונה מיועץ?","a":"יועץ מגיש מצגת והולך. אני עושה את העבודה, בתוך הפייפליין ובתוך העסקאות, ואחראי על התוצאה."},
  {"q":"כמה זה עולה?","a":"בין 2,000 ל-12,000 דולר בחודש לפי כמה שעות ביום אתם צריכים, מול 250 אלף דולר ומעלה למשרה מלאה, בתשלום חודשי בלי חוזה."}],
 "outsourced-sales":[
  {"q":"מה מקבלים במכירות במיקור חוץ?","a":"צוות שלם: אנשי SDR ו-AE דוברי שפת אם, הנהגה בכירה ו-VP, מגויסים, מוכשרים, מנוהלים ומדווחים, מחוץ למצבת כוח האדם שלכם."},
  {"q":"מתי מיקור חוץ עדיף על גיוס פנימי?","a":"כשבניית צוות איטית, יקרה או מסוכנת מדי לשלב שלכם. מקבלים מנוע עובד תוך שבועות, לא שישה עד שנים-עשר חודשים, בלי סיכון פיצויים."},
  {"q":"מי מנהל את הצוות?","a":"KSW Solutions, בהובלתי. מעל עשרים שנה של בנייה וניהול מכירות B2B בארה\"ב, אירופה, APAC והשווקים הפוסט-סובייטיים."}],
 "go-to-market-strategy":[
  {"q":"מה כולל פרויקט Go-To-Market?","a":"ICP, מיצוב, תמחור, ערוצים, Playbook ותחזית אמיתית, ואז אני עוזר לכם לבצע, לא רק מגיש שקפים."},
  {"q":"האם זה כולל GTM ל-SaaS?","a":"כן, כולל GTM ל-SaaS, וגם חומרה, שירותים ו-B2B מורכב."},
  {"q":"אתה מבצע או רק מייעץ?","a":"אני בונה את התוכנית ואז מוביל את הביצוע איתכם עד שיש פייפליין, שותפים ומכירות ראשונות."}],
 "market-entry":[
  {"q":"איך בוחרים לאיזה שוק להיכנס?","a":"אני בוחן את הכאב האמיתי, הנגישות, הנכונות לשלם והתחרות, ואז בונה רק איפה שהגיוני, במקום להתפזר דק על הכל."},
  {"q":"באמת פתחת שווקים בחו\"ל?","a":"כן, יותר מפעם אחת ולמספר חברות, כולל בניית צוותים, חברות בנות ותמיכה בארה\"ב, באיחוד האירופי, ב-APAC ובשווקים הפוסט-סובייטיים."},
  {"q":"אתה בונה את המערך או רק את התוכנית?","a":"גם וגם. אני מתכנן את הכניסה ואז בונה ומריץ את הצוות, הערוץ והמכירות בשטח."}],
 "sales-team-building":[
  {"q":"מה כוללת בניית צוות מכירות?","a":"גיוס, השמה, הכשרה וניהול של אנשי SDR, AE ו-BD פנימיים על Playbook שמביא אותם ליעד, והחלפה של מי שלא מתאים."},
  {"q":"במה זה שונה ממכירות במיקור חוץ?","a":"זה בונה את הצוות הפנימי שלכם שנשאר בתוך החברה. מכירות במיקור חוץ זה צוות שלם שמורץ עבורכם מחוץ למצבת כוח האדם."},
  {"q":"כמה מהר צוות חדש מתחיל לייצר?","a":"אני בונה את ההכשרה וה-Playbook סביב ה-ICP שלכם כך שהנציגים עולים על מערכת במקום לאלתר כל שיחה."}],
 "distributor-channel-recruitment":[
  {"q":"מה אתה עושה בתחום המפיצים והערוצים?","a":"אני מאתר, בודק, מחתים ומנהל את המפיצים, המשווקים והשותפים שפותחים טריטוריות חדשות ובאמת מביאים תוצאות."},
  {"q":"מכירה ישירה או ערוץ?","a":"מה שמתאים לשוק. אני מחליט ובונה ישיר מול ערוץ, שוק אחר שוק."},
  {"q":"בנית רשתות מפיצים בעבר?","a":"כן, באירופה, בדרום אמריקה, ב-APAC ובשווקים הפוסט-סובייטיים, ל-IoT, יצרנים וחברות רפואיות."}],
 "b2g-public-sector":[
  {"q":"מה כוללת מכירה B2G?","a":"ניהול מכרזים, RFIs, RFQs ופרויקטים ממשלתיים מורכבים, ומיפוי מקבלי ההחלטות האמיתיים ונתיב הרכש."},
  {"q":"סגרת עסקאות ממשלתיות?","a":"כן, בעולם, כולל מחזורי RFI ו-RFQ ארוכים ל-IoT תעשייתי מול תאגידי מים וממשלות."},
  {"q":"למה B2G שונה ממכירה מסחרית?","a":"קונה אחר, כללים אחרים ולוח זמנים אחר, והמחיר של טעות הוא שנה שאבדה. אני יודע איפה העסקאות האלה נתקעות."}],
 "contract-negotiation":[
  {"q":"מתי כדאי לשלב אותך במשא ומתן?","a":"ברגע שעסקה בעלת ערך גבוה נתקעת על מחיר, תנאים, משפטי או רכש, או בכל פעם שהעסקה חשובה מכדי לסכן אותה בסגירה מהוססת. ככל שאכנס מוקדם יותר, כך נשמור על יותר מנוף."},
  {"q":"אתה משתלט על העסקה או מלווה את הצוות?","a":"גם וגם. אני יכול להוביל את המשא ומתן עד החתימה בעצמי, או לשבת לצד הצוות ולכוון ברגעים הקשים. מה שייתן לעסקה את הסיכוי הטוב ביותר."},
  {"q":"אילו עסקאות סגרת?","a":"הסכמי B2B ו-B2G מורכבים ובעלי ערך גבוה בחמש יבשות, מעל עשרים שנה של החזקת מחיר ותנאים בלי לאבד את העסקה."}],
}


GUIDES = [
 {"slug":"sales-training",
  "title":"B2B Sales Training That Actually Sticks | Tal Paperin",
  "desc":"Most sales training fails because nobody runs it afterward. I have trained 2,000 salespeople worldwide, then managed them to the number. Here is what works.",
  "h1":"Sales Training Alone Does Not Work. Here Is What Does.","eyebrow":"Guide",
  "lead":"I am not a sales trainer. I am a CRO and VP of Sales who has trained more than 2,000 salespeople across the globe, then stayed to manage them until the training showed up in closed deals. That second half is the part everyone skips, and it is the reason most sales training is a waste of money.",
  "sections":[
    {"h":"Why most sales training is a waste of money","p":[
      "You bring in a trainer for two days. The team is fired up. They get a binder, a framework, maybe a role-play. Everyone feels sharper on Friday. By the following Wednesday they are back to selling exactly the way they did before, because nobody changed what happens after the training ends.",
      "Training is not the product. Behavior change is. And behavior only changes when someone senior inspects it, coaches it, and holds the line every single week. A trainer flies home. A sales leader stays."]},
    {"h":"I am not a trainer. I am a CRO who trains, then runs the team.","p":[
      "There is a difference between someone who teaches a workshop and someone who owns the number. I have carried a quota, built the playbook, and sat in the deals myself. When I train your team, I am not teaching theory I read in a book. I am teaching exactly how I would close your deals, because I have closed deals like yours.",
      "Then I do the part a trainer cannot: I manage the team to make sure it works. I sit in on calls, I inspect the pipeline, I coach the reps who are drifting, and I keep raising the standard until the new way of selling is simply the way your team sells."]},
    {"h":"2,000 salespeople, then managed to the number","p":[
      "Over 20-plus years I have trained more than 2,000 salespeople on five continents: SDRs, closers, channel partners and whole teams, in startups and in large organizations. The training was never the point. The point was what happened next: deals closed, cycles shortened, and the number went up and stayed up.",
      "That is the test I hold myself to. Not how good the session felt on the day, but whether revenue actually moved a quarter later. It does."]},
    {"h":"What real sales training looks like","ul":[
      "It starts from your actual deals, your buyers and your real objections, not a generic curriculum",
      "It is taught by an operator who owns the number and gets into the real deals, so the reps respect it and use it",
      "It is followed by weekly coaching, call reviews and pipeline inspection, not a binder on a shelf",
      "It is enforced by a leader who owns the number, so the new behavior sticks",
      "It is measured in closed revenue and shorter cycles, not in attendance and smiles"]},
    {"h":"Training without management is theater","p":[
      "If you only want a one-off workshop to tick a box, I am the wrong person, and honestly you should keep your money. But if you want your team to sell better and keep selling better, you need the training and the management together, from the same person, until it holds. That is what a fractional CRO does, and it is why my clients watch the numbers actually move."]},
  ],
  "faqs":[
    {"q":"Do you offer sales training?","a":"Yes, but not as a standalone workshop. I train your team as part of owning your sales, which means I also manage the team afterward to make sure the training turns into closed deals. I have trained more than 2,000 salespeople worldwide."},
    {"q":"Why does most sales training not work?","a":"Because the trainer leaves and nobody changes what happens next. Behavior only sticks when a senior leader coaches it, inspects it and holds the standard every week. Training without ongoing management is theater."},
    {"q":"Who does the training?","a":"I do. I am a CRO and VP of Sales who has carried the number hands-on. I teach exactly how I would close your deals, from your real pipeline, not a generic curriculum out of a book."},
    {"q":"How is this different from hiring a sales trainer?","a":"A trainer runs a session and flies home. I train your team and then stay to manage them to the number: call reviews, pipeline inspection and weekly coaching until the new way of selling is simply how your team sells."},
    {"q":"How much does it cost?","a":"Training is part of a fractional CRO engagement, which runs $2,000 to $12,000 a month depending on how hands-on you need me. Use the calculator on the pricing page for a number in about a minute."}],
  "related":'See <a href="/services/sales-team-building">sales team building</a>, the <a href="/services/fractional-cro">fractional CRO service</a>, <a href="/pricing">pricing</a>, or read <a href="/blog/why-sales-training-fails">why most sales training fails</a>.'},

 {"slug":"fractional-cro-cost",
  "title":"How Much Does a Fractional CRO Cost? | Tal Paperin",
  "desc":"A straight answer on fractional CRO pricing: what it costs per month, how it compares to a $250K full-time CRO, and when each level is worth it.",
  "h1":"What a Fractional CRO Actually Costs","eyebrow":"Guide",
  "lead":"Most consultants hide the number, hand you a deck, and disappear. I am an operator who owns the number, I bill monthly with no contract, and here is exactly what a fractional CRO costs, in plain figures.",
  "sections":[
    {"h":"The short answer","p":[
      "A full-time CRO runs $250,000 and up all in, once you add base, equity, bonus, severance risk and a months-long hiring cycle. A fractional CRO gives you the same senior ownership for a monthly fee. The role is identical at every level. The only thing that changes is how many hours a day I am in your business."]},
    {"h":"The three levels, priced by how much of me","tiers":[
      "Advisor, $2,000 a month. About three hours a week. A standing weekly strategy call plus access to me between calls for the real decisions. For founders who want senior direction while they run the day to day themselves.",
      "Starter, $6,000 a month. Me as your CRO embedded two hours a day, every working day. I own the strategy, the system and the standards, and your team carries more of the daily execution. What most companies choose.",
      "Growth, $12,000 a month. Half time, four hours a day. Not just steering, driving: I run the motion week to week, manage the team hands-on, and carry the number with you. Full-time, exclusive engagements available on request."]},
    {"h":"Why it is cheaper than a full-time hire","ul":[
      "No $250K base, equity, bonus or severance risk",
      "No three-month hiring search and no two-quarter ramp",
      "Monthly billing, no contract, no lock-in, no exit fines: do not like it, we are done at the end of the month",
      "Results in week one, not month six"]},
    {"h":"You are hiring an operator, not an advisor","p":[
      "Most consultants hand you a deck and disappear. They have never carried a number. I am an ex VP of Global Sales and CRO. I own the number, build and manage the team that delivers it, and step into the big deals myself. And I bill monthly with no contract, so I keep the work by being good at it, not by trapping you in one."]},
    {"h":"When a fractional CRO is the wrong call","p":[
      "If your sales motion is already proven and the work is genuinely a full week every week, hire full-time. Fractional wins when the motion is not yet proven, the volume is not yet a full week, or you need results before committing to a permanent hire."]},
  ],
  "faqs":[
    {"q":"How much does a fractional CRO cost?","a":"My engagements run $2,000 to $12,000 a month depending on the level of involvement, versus $250,000 and up for a full-time CRO once you include equity, bonus and severance."},
    {"q":"Is a fractional CRO cheaper than a full-time CRO?","a":"Yes. You get the same senior ownership without the base salary, equity, bonus, severance risk, hiring cycle or long ramp, and without a long-term lock-in."},
    {"q":"What is included?","a":"The same at every tier: a revenue diagnosis, a sales strategy and forecast, a playbook, CRM and pipeline structure, team training, hands-on management of the motion, hiring and performance, and full CRO-level ownership across sales, marketing and go-to-market. What changes between tiers is how many hours a day I am in your business: two hours, four hours, or full time."},
    {"q":"How long are fractional CRO engagements?","a":"There is no long-term lock-in. You scale the involvement up as you grow, or hand the function off once it is built."},
    {"q":"Do I have to sign a long contract?","a":"No. I bill monthly with no contract and no exit fines. If you do not like what I deliver, we are done at the end of the month and you owe nothing more."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO service</a>, <a href="/case-studies">case studies</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"fractional-cro-vs-outsourced-sales",
  "title":"Fractional CRO vs Outsourced Sales: Which Do You Need? | Tal Paperin",
  "desc":"Fractional CRO, fully outsourced sales, or a do-it-yourself system? A straight breakdown of which fits your stage, and how to choose.",
  "h1":"Fractional CRO vs Outsourced Sales","eyebrow":"Guide",
  "lead":"Three ways to fix revenue, one decision. Whichever you pick, you get an operator who owns the number, billed monthly with no contract and no lock-in. Here is which one fits your stage, and which one wastes your money.",
  "sections":[
    {"h":"The three options","tiers":[
      "Do it yourself. You have the founder energy and the time to run the motion, you just need the system: the playbook, scripts, battle cards and daily guidance. Lowest cost, most of your time.",
      "Fractional CRO. You need a senior leader to own the number and run the motion with you, but the work is not yet a full-time job. Me, in the seat. The middle rung, and what most companies choose.",
      "Fully outsourced sales. You want the whole function off your plate: native-speaking SDRs and AEs, senior leadership and a VP, a complete team hired, trained, managed and reported on daily, living outside your headcount."]},
    {"h":"How to choose","ul":[
      "If the problem is that you have no system, do it yourself with the right tools",
      "If the problem is that nobody owns the number, get a fractional CRO",
      "If the problem is that you have no team and no time to build one, outsource the whole function"]},
    {"h":"The honest test","p":[
      "Ask one question: is your sales motion proven? If it is, you mostly need execution, so a system or an outsourced team can run it. If it is not, you need senior ownership to find the motion first, which is exactly what a fractional CRO does before you spend on a team."]},
  ],
  "faqs":[
    {"q":"Should I hire a fractional CRO or outsource my sales?","a":"Hire a fractional CRO when nobody owns the number and the motion is not yet proven. Outsource the whole function when you have no team and no time to build one and just want sales to happen outside your headcount."},
    {"q":"What is the difference between a fractional CRO and an outsourced sales team?","a":"A fractional CRO is a single senior leader who owns strategy, the forecast and the motion. An outsourced sales team is a full crew of SDRs, AEs and a VP that runs day to day. One is leadership, the other is delivery."},
    {"q":"Which is cheaper?","a":"A do-it-yourself system is cheapest, a fractional CRO is the middle, and a fully outsourced team is the largest commitment because you are buying a whole function."}],
  "related":'See <a href="/services/fractional-cro">fractional CRO</a>, <a href="/services/outsourced-sales">outsourced sales</a>, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-israel",
  "title":"Fractional CRO in Israel | Tal Paperin",
  "desc":"A fractional CRO for Israeli B2B companies selling at home and abroad. Senior revenue leadership, in Hebrew or English, without a $250K full-time hire.",
  "h1":"Fractional CRO in Israel","eyebrow":"Guide",
  "lead":"Senior revenue leadership for Israeli companies, in Hebrew or English, built for selling into the US, the EU and beyond.",
  "sections":[
    {"h":"Built for Israeli companies selling abroad","p":[
      "Israeli B2B companies build great products and then hit the same wall: selling them into markets that do not work the way the local one does. I have spent 20-plus years opening the US, the EU, the FSU and APAC for Israeli companies, direct and through channel."]},
    {"h":"What I own","ul":[
      "Revenue strategy, the forecast and accountability for the number",
      "The go-to-market motion for international markets, not just the local one",
      "The team: hiring, training, and replacing where needed",
      "Distributors, channel and complex contract negotiation across borders"]},
    {"h":"In Hebrew or English","p":[
      "I work with founders and teams in Hebrew and run the actual selling in English, or whatever the target market speaks. You get a leader who knows the Israeli starting point and the foreign finish line."]},
  ],
  "faqs":[
    {"q":"Do you work with Israeli companies?","a":"Yes. Most of my work is taking Israeli B2B companies into the US, the EU and other markets, direct and through distributors."},
    {"q":"Can we work in Hebrew?","a":"Yes. I work with Israeli founders and teams in Hebrew and run the international selling in English or the target market's language."},
    {"q":"How much does a fractional CRO in Israel cost?","a":"Engagements run $2,000 to $12,000 a month depending on involvement, far below a $250,000-plus full-time CRO hire."}],
  "related":'Weighing local versus global? See <a href="/sell-in-israel-first-or-go-global">sell in Israel first, or go global?</a> and <a href="/when-to-expand-to-the-us">when to expand to the US</a>. Or see the <a href="/services/market-entry">market entry</a> and <a href="/services/fractional-cro">fractional CRO</a> services, or <a href="/he/">the Hebrew site</a>.'},

 {"slug":"fractional-cro-vs-vp-of-sales",
  "title":"Fractional CRO vs Hiring a VP of Sales | Tal Paperin",
  "desc":"Tired of $30K-a-month VP of Sales hires you fire in 90 days? A fractional CRO gives you proven revenue leadership with no hiring gamble and no lock-in.",
  "h1":"Fractional CRO vs Hiring a VP of Sales","eyebrow":"Guide",
  "lead":"You have done this before. Hire a VP of Sales at thirty grand a month, wait, watch nothing move, fire them at month three, eat the severance, start over. Here is the alternative.",
  "sections":[
    {"h":"The VP of Sales graveyard","p":[
      "A VP of Sales runs $30,000 a month or more, all in. The search takes months. The ramp takes a quarter. And if the fit is wrong, and it often is, you fire them at month two, three or four, eat the severance, and start the whole cycle again. I have watched founders burn hundreds of thousands of dollars this way, with nothing to show for it but lost time.",
      "The hire is a gamble. You are betting six figures on a resume and three interviews."]},
    {"h":"A fractional CRO is not a gamble","ul":[
      "I have built and run revenue for 30-plus B2B companies on five continents. You are not betting on whether I can do it. I have already done it.",
      "No recruiter fees, no equity, no severance risk, no months-long search",
      "Results in week one: I diagnose where deals leak, then I run the fix. No ramp, no learning curve"]},
    {"h":"I own the number. Myself. Hands on.","p":[
      "Most consultants hand you a deck and disappear. They have never carried a number. I am an ex VP of Global Sales and CRO. I diagnose where revenue is stuck, build and manage the team that fixes it, and step into the big deals myself. You are hiring an operator, not an advisor."]},
    {"h":"Monthly. No contract. No hostages.","p":[
      "I bill monthly. No long contract, no lock-in, no exit fines. You do not like what I deliver, we are done at the end of the month, and you owe nothing more. I keep the engagement because the work is good, not because a contract traps you. That is the opposite of a VP hire you cannot easily undo."]},
  ],
  "faqs":[
    {"q":"Is a fractional CRO better than hiring a VP of Sales?","a":"If your sales motion is not yet proven, yes. A VP hire is a six-figure gamble with months of search, a quarter of ramp and real severance risk. A fractional CRO who has done it 30-plus times delivers from week one, with no hiring risk and no lock-in."},
    {"q":"How much does a fractional CRO cost vs a VP of Sales?","a":"A VP of Sales runs $30,000 a month or more all in, plus recruiter fees, equity and severance. My fractional engagements run $2,000 to $12,000 a month, billed monthly with no contract."},
    {"q":"What if it is not working out?","a":"I bill monthly with no contract and no exit fines. If you do not like what I deliver, we are done at the end of the month and you owe nothing more."},
    {"q":"Do you do the work, or just advise?","a":"I do the work. I am an ex VP of Global Sales and CRO. I own the number, build and manage the team, and step into the big deals myself, not just the strategy decks."}],
  "related":'Compare the <a href="/fractional-cro-cost">cost</a>, see <a href="/fractional-cro-vs-outsourced-sales">fractional CRO vs outsourced sales</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"frum-business-consultant","en_only":True,
  "title":"Frum Business Consultant and Sales Leader | Tal Paperin",
  "desc":"A frum, shomer Shabbos business consultant and fractional sales leader who knows the heimishe, Yiddish-speaking business world and helps frum businesses grow.",
  "h1":"A Frum Business Consultant Who Gets the Heimishe World","eyebrow":"For Frum Businesses",
  "lead":"I am a frum, shomer Shabbos Yid from Eretz Yisrael who has built and run sales for businesses on five continents. If you are a frum business owner who wants a sales leader who shares your values and understands your world, not just your spreadsheet, this is for you.",
  "sections":[
    {"h":"A fellow Yid, not a stranger to your world","p":[
      "I am a frum business consultant and fractional sales leader, shomer Torah u'mitzvos, raised and based in Eretz Yisrael. I have spent over twenty years building sales engines for B2B companies, and a real part of my work has been with frum and heimishe business owners in the US, from Boro Park to Lakewood to Monsey. You will not have to explain to me why you do not pick up on Shabbos, why Yom Tov shuts the office, or why parnassa with kavod matters more than a vanity number."]},
    {"h":"What I actually do","p":[
      "The frum part is who I am. The work is hard revenue. I take ownership of your sales the way a senior VP would: the strategy, the team, the pipeline, the forecast and the number itself, hands-on, from diagnosis to execution.",
      "I build go-to-market from zero, hire and train salespeople, open new markets, recruit distributors, and run complex B2B and B2G deals. Same operator, whether the client wears a yarmulke or not."]},
    {"h":"Why frum business owners work with me","ul":[
      "Shared values and shared trust: a handshake with a fellow Yid means something",
      "I respect the calendar: no calls, no meetings, no pressure on Shabbos or Yom Tov",
      "I understand the heimishe, Yiddish-speaking business world and how it really buys and sells",
      "Bekavodik, straight, no bittul zman: I tell you the emes about your sales and then I fix it",
      "Discreet: I understand that in a close kehilla, your business is your business"]},
    {"h":"The heimishe and Yiddish-speaking market","p":[
      "Many of the business owners I work with are heimish and speak Yiddish as their first language. I do not speak fluent Yiddish, and I will never pretend otherwise. What I do have is years of working closely inside the Yiddish-speaking, heimishe business world, and a real feel for how it operates, who it trusts, and how deals actually get done in it. I have also run a fundraising seminar for Chabad on Campus rabbeim, so I know how to teach and sell to our world, not just the outside one."]},
    {"h":"From the frum world to the wider market, and back","p":[
      "A lot of frum businesses are great at selling to their own kehilla and freeze the moment they need to sell to the wider, secular or international market. That is exactly my expertise. I take frum-owned companies into the US mainstream, the EU and beyond, and I help outside companies sell respectfully into the frum market. Either direction, I have done it."]},
    {"h":"What you need","links":[
      ["A frum sales consultant","/blog/frum-sales-consultant"],
      ["Business development for frum businesses","/blog/frum-business-development"],
      ["Growing and expanding your frum business","/blog/growing-your-frum-business"]]},
    {"h":"Frum business consultant by community","links":[
      ["Lakewood","/blog/frum-business-consultant-lakewood"],
      ["Boro Park","/blog/frum-business-consultant-boro-park"],
      ["Williamsburg","/blog/frum-business-consultant-williamsburg"],
      ["Monsey","/blog/frum-business-consultant-monsey"],
      ["Crown Heights","/blog/frum-business-consultant-crown-heights"],
      ["Flatbush","/blog/frum-business-consultant-flatbush"],
      ["Five Towns","/blog/frum-business-consultant-five-towns"],
      ["Kiryas Joel","/blog/frum-business-consultant-kiryas-joel"],
      ["Passaic","/blog/frum-business-consultant-passaic"],
      ["Baltimore","/blog/frum-business-consultant-baltimore"],
      ["Los Angeles","/blog/frum-business-consultant-los-angeles"],
      ["Miami","/blog/frum-business-consultant-miami"],
      ["Chicago","/blog/frum-business-consultant-chicago"]]},
  ],
  "faqs":[
    {"q":"Do you work with frum business owners?","a":"Yes, and a real part of my work is with frum and heimishe business owners in the US and Eretz Yisrael. I am a frum, shomer Shabbos Yid myself, so we start from shared values and shared trust."},
    {"q":"Are you shomer Shabbos? Will you call on Shabbos or Yom Tov?","a":"I am shomer Shabbos. There are no calls, meetings or messages from me on Shabbos or Yom Tov, and I build the work around the Jewish calendar without being asked."},
    {"q":"Do you speak Yiddish?","a":"I do not speak fluent Yiddish and I will not pretend to. I have spent years working inside the Yiddish-speaking, heimishe business world, so I understand how it operates and how it buys and sells, and I work comfortably with Yiddish-speaking owners in English."},
    {"q":"What does a frum business consultant actually do for me?","a":"The same hard sales work any serious fractional sales leader does: strategy, team, pipeline, forecast and the number, hands-on. The difference is that you get someone who shares your values, respects your calendar, and understands the heimishe world you operate in."},
    {"q":"Can you help my frum business sell to the wider market?","a":"Yes. Taking frum-owned companies from selling inside the kehilla to selling into the US mainstream, the EU and international markets is one of the things I do best, and I also help outside companies sell respectfully into the frum market."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/market-entry">market entry</a> services, read more on the <a href="/blog/">blog</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"fractional-cro-for-saas","en_only":True,
  "title":"Fractional CRO for SaaS Companies | Tal Paperin",
  "desc":"A fractional CRO for B2B SaaS: ICP, pricing, the outbound motion, the team and the forecast, owned end to end, without a $250K full-time hire.",
  "h1":"Fractional CRO for SaaS","eyebrow":"Guide",
  "lead":"SaaS lives and dies on a repeatable motion. I build and own it: ICP, pricing, pipeline, the team and the number, without a full-time CRO salary.",
  "sections":[
    {"h":"Why SaaS needs this","p":[
      "Most SaaS companies have a product and a few referral deals, then stall because there is no repeatable motion and nobody senior owns the number. A great product does not sell itself, especially into technical, skeptical buyers. I have sold SaaS to the hardest rooms there are, from AI startups to scientific software bought by universities, labs and pharma."]},
    {"h":"What I own for a SaaS company","ul":[
      "ICP, positioning and pricing built for how SaaS actually gets bought",
      "The outbound and inbound motion, the playbook and the CRM and pipeline",
      "Hiring, training and managing SDRs and AEs who can sell technical SaaS",
      "The forecast and the number, owned end to end"]},
    {"h":"Done before, in real SaaS","p":[
      "At KanduAI I came in as Fractional VP of Sales from day one, defined the ICP, built the outbound motion from zero and rebuilt it through two pivots. For Synergix I sold scientific SaaS into universities, research labs and pharma, writing the scripts and playbook the reps actually ran. Different products, same discipline."]},
  ],
  "faqs":[
    {"q":"What does a fractional CRO do for a SaaS company?","a":"Owns the revenue motion end to end: ICP and pricing, the outbound and inbound playbook, the CRM and pipeline, hiring and managing the reps, and the forecast, all without a full-time CRO salary."},
    {"q":"Do you sell technical or scientific SaaS?","a":"Yes. I have sold SaaS into universities, research labs and pharma, and built the motion for AI SaaS startups from zero. Technical, skeptical buyers are exactly where most reps stall and where a real playbook wins."},
    {"q":"How much does a fractional CRO for SaaS cost?","a":"Engagements run $2,000 to $12,000 a month depending on how many hours a day you need, far below a $250,000-plus full-time CRO hire, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"fractional-cro-for-iot-hardware","en_only":True,
  "title":"Fractional CRO for IoT and Hardware Companies | Tal Paperin",
  "desc":"A fractional CRO for IoT and hardware: complex B2B sales of devices, software and services, direct and through distributors, across borders.",
  "h1":"Fractional CRO for IoT and Hardware","eyebrow":"Guide",
  "lead":"IoT and hardware sell differently: long cycles, mixed hardware, software and services, channel and direct, often across borders. I have built and run exactly this.",
  "sections":[
    {"h":"Why IoT and hardware are their own sport","p":[
      "You are selling a bundle, devices, software and services, often into utilities, manufacturers, municipalities and enterprises, with long evaluation cycles and a distributor network to manage. Generic SaaS playbooks do not fit. You need someone who has carried this exact motion."]},
    {"h":"What I own","ul":[
      "The global sales strategy across direct and channel",
      "Distributor and reseller networks, recruited and managed market by market",
      "Direct B2B sales of hardware, software and services",
      "B2G and long RFI and RFQ cycles where they apply",
      "The team: SDRs, post-sales and tech support, hired and run"]},
    {"h":"Done before, in real IoT","p":[
      "At Bacsoft, backed by Japan's SUN Corp, I owned global sales of industrial IoT to water utilities, manufacturers and smart cities, building a distributor network across continents and a live B2G pipeline. At BT9 I built an international cold-chain IoT sales operation from zero across the FSU, the EU and APAC. At LoneStar Tracking I built and ran the whole sales side for a founder-led IoT business."]},
  ],
  "faqs":[
    {"q":"Do you sell hardware as well as software?","a":"Yes. IoT deals are usually a bundle of hardware, software and services, and I have run exactly that, direct and through distributors, to utilities, manufacturers, municipalities and enterprises."},
    {"q":"Can you build and manage a distributor network for hardware?","a":"Yes. Recruiting, signing and managing distributors and resellers across markets is a core part of how I build IoT and hardware revenue, alongside a direct sales team."},
    {"q":"Do you handle public-sector and B2G IoT deals?","a":"Yes. I have run long RFI and RFQ cycles and complex government and utility projects internationally for industrial IoT companies."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a>, <a href="/services/distributor-channel-recruitment">distributor recruitment</a> and <a href="/services/b2g-public-sector">B2G</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-medical-devices","en_only":True,
  "title":"Fractional CRO for Medical Device Companies | Tal Paperin",
  "desc":"A fractional CRO for medical device and medtech companies: regulated, high-trust B2B sales, distributors and direct, across the EU and beyond.",
  "h1":"Fractional CRO for Medical Devices","eyebrow":"Guide",
  "lead":"Medical device sales is a cautious, regulated, high-trust game. I build the commercial function, sales and the channel, for medtech selling into Europe and beyond.",
  "sections":[
    {"h":"Why medtech is different","p":[
      "The buyer does not gamble. Selling devices and guided-surgery systems means a long, high-trust, regulated sale into clinicians and distributors who need proof, not a pitch. You need a full commercial function, not a single rep."]},
    {"h":"What I own","ul":[
      "International sales strategy across direct and distributor channels",
      "Distributor recruitment and management across regulated markets",
      "Direct B2B sales of devices and systems to clinical buyers",
      "Where needed, the marketing and marcom that supports a regulated sale"]},
    {"h":"Done before, in real medtech","p":[
      "At TAG Medical I ran international sales of dental implants and digital guided-surgery CAD/CAM systems across the EU, driving direct B2B sales, recruiting and managing distributors across European markets, and building the marketing function, including the company's first video commercials and the launch of its digital CAD/CAM center."]},
  ],
  "faqs":[
    {"q":"Do you have medical device sales experience?","a":"Yes. I ran international sales for a dental implant and guided-surgery company across the EU, both direct to clinical buyers and through a distributor network, and built the supporting marketing function."},
    {"q":"Can you sell into regulated European markets?","a":"Yes. Cautious, regulated, high-trust markets are exactly where I have sold medtech, choosing entry markets and building the distributor and direct motion for each."},
    {"q":"Do you handle distributors or just direct sales?","a":"Both. Medtech usually needs a distributor network plus direct selling into key accounts, and I build and run both."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a>, <a href="/services/market-entry">market entry</a> and <a href="/services/distributor-channel-recruitment">distributor recruitment</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-manufacturers","en_only":True,
  "title":"Fractional CRO for Manufacturers | Tal Paperin",
  "desc":"A fractional CRO for manufacturers: open new territories, sign distributors and retail chains, and get product onto shelves in markets you wrote off.",
  "h1":"Fractional CRO for Manufacturers","eyebrow":"Guide",
  "lead":"Manufacturers grow by opening territories and channels. I find the real buyers, sign the distributors and chains, and put product on shelves, including in markets you were told had no money.",
  "sections":[
    {"h":"Why manufacturers stall","p":[
      "A great product and a blank map. Most manufacturers leave whole regions empty because someone decided there was no money there, without ever testing it against the real channel and buyers on the ground. That assumption is usually a story, not a fact."]},
    {"h":"What I own","ul":[
      "Market-entry strategy and the milestone plan for each territory",
      "Mapping the real channel and the decision-makers on the ground",
      "Negotiating and signing distributors and retail chains",
      "Direct sales into large retailers and big-box chains where it fits"]},
    {"h":"Done before, in real manufacturing","p":[
      "Palram, a global manufacturer, had written off Eastern Europe. I built the entry plan, mapped the channel, led every negotiation personally and signed multiple distributors and retail chains, putting product on shelves in a market they had abandoned. For SOURCE I took an unknown overseas consumer brand into major North American retail, direct to the big chains and through a distributor network."]},
  ],
  "faqs":[
    {"q":"Can you open new geographic markets for a manufacturer?","a":"Yes. I build the entry plan, map the real channel and decision-makers, and sign the distributors and retail chains, including in markets a company had written off as not worth it."},
    {"q":"Do you sell direct to retailers or only through distributors?","a":"Both. I have sold direct into large retailers and big-box chains and built distributor and reseller networks to extend reach, depending on the market."},
    {"q":"How much does a fractional CRO for manufacturers cost?","a":"Engagements run $2,000 to $12,000 a month depending on involvement, billed monthly with no long-term lock-in, far below a full-time hire."}],
  "related":'See the <a href="/services/market-entry">market entry</a>, <a href="/services/distributor-channel-recruitment">distributor recruitment</a> and <a href="/services/fractional-cro">fractional CRO</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"how-to-hire-a-fractional-cro",
  "title":"How to Hire a Fractional CRO (Practical Guide) | Tal Paperin",
  "desc":"How to hire a fractional CRO: when you need one, what to look for, the questions to ask, and what it costs.",
  "h1":"How to Hire a Fractional CRO","eyebrow":"Guide",
  "lead":"A fractional CRO can fix your revenue without a $250,000 hire, but only if you pick the right one. Here is how, from someone who has been in the seat 30-plus times.",
  "sections":[
    {"h":"When you are ready for one","p":["You are ready when revenue has stalled and nobody senior owns the number, when you need results before you can justify a full-time CRO, or when you have burned money on VP hires that did not move the number. If you just need more hands, hire reps. If you need someone to own the strategy, the team and the forecast, hire a CRO."]},
    {"h":"What to look for","ul":["An operator who has carried a number, not a consultant who hands you a deck","Hands-on experience in your kind of sale: B2B, your deal size, your motion","Willingness to own hiring, training and replacing reps, not just advising","A clear diagnosis-then-execution approach with a forecast they will stand behind","Monthly terms and no long lock-in, so they keep earning the renewal"]},
    {"h":"Questions to ask before you sign","ul":["Walk me through a revenue function you rebuilt from zero and what you owned","What will you do in week one, week two, and the first month","How do you decide who to keep, train or replace on my team","What does your forecast look like and what are you accountable for","How many hours a day will you actually be in my business"]},
    {"h":"What it costs","p":["A fractional CRO is priced by how much of the week you need, not by a full salary. Expect roughly $2,000 a month for a weekly advisor, $6,000 for a couple of hours a day, up to $12,000 for half time, billed monthly, with full-time and exclusive available on request. Compare that to $250,000-plus all in for a full-time CRO once you add equity, bonus, severance risk and a long hiring cycle."]},
  ],
  "faqs":[
    {"q":"How much does it cost to hire a fractional CRO?","a":"Typically $2,000 to $12,000 a month depending on how many hours a day you need, billed monthly with no long-term lock-in, far below a $250,000-plus full-time CRO."},
    {"q":"How fast can a fractional CRO start?","a":"Quickly. A good one diagnoses in week one, gives you a plan and a real forecast in week two, and is running the motion by week three, instead of the months a full-time hire takes to find and ramp."},
    {"q":"Fractional CRO or full-time CRO?","a":"Hire fractional when the work is not yet a full week or you need results now without the cost and risk of a full-time hire. Move to full-time when the function is big enough to justify a senior salary all year."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service, compare <a href="/fractional-cro-vs-vp-of-sales">CRO vs VP of Sales</a> and <a href="/fractional-cro-cost">the cost</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"when-do-you-need-a-fractional-cro",
  "title":"When Do You Need a Fractional CRO? The Signs | Tal Paperin",
  "desc":"The clear signs you need a fractional CRO: stalled revenue, no owner of the number, churned VPs, a great product that will not sell.",
  "h1":"When Do You Need a Fractional CRO?","eyebrow":"Guide",
  "lead":"Most companies wait too long. Here are the signs you need a fractional CRO now, not after another lost quarter.",
  "sections":[
    {"h":"The eight signs it is time","html":IG_SIGNS_EN},
    {"h":"What a fractional CRO owns","html":IG_ENGINE_EN},
    {"h":"Fractional CRO or VP of Sales?","html":IG_OWNS_EN},
    {"h":"What changes when someone owns the number","p":["A fractional CRO takes the strategy, the team, the pipeline, the forecast and the accountability off your plate and onto theirs. Week one is diagnosis, week two is a plan and a real forecast, then they run it, hiring where needed, training the team you have and replacing who cannot. You stop guessing and start operating."]},
    {"h":"Before and after","html":IG_BA_EN},
    {"h":"What a fractional CRO actually does","html":IG_DOES_EN},
    {"h":"How an engagement unfolds","html":IG_PHASES_EN},
    {"h":"What waiting costs","p":["The cost of waiting is a wrong VP hire, a year lost, and six figures spent learning what a senior operator would have told you in week one. Stalled revenue rarely fixes itself, and the longer the motion stays broken, the more it costs to rebuild."]},
  ],
  "faqs":[
    {"q":"What is the difference between a fractional CRO and a consultant?","a":"A consultant hands you a deck and leaves. A fractional CRO owns the work, the pipeline, the deals and the number, and answers for the result."},
    {"q":"Is my company too small for a fractional CRO?","a":"If you have a product and some revenue but no repeatable motion or senior owner of the number, you are the right size. Fractional exists so you get CRO-level leadership without a full-time salary."},
    {"q":"How quickly will I see results?","a":"You get a diagnosis in week one and a plan and forecast in week two. Pipeline and process improvements follow as the motion gets built and run."}],
  "related":'See <a href="/how-to-hire-a-fractional-cro">how to hire a fractional CRO</a>, the <a href="/services/fractional-cro">service</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"founder-led-sales-wont-scale",
  "title":"Founder-Led Sales Won't Scale: How to Fix It | Tal Paperin",
  "desc":"Founder-led sales stalls when every deal still runs through you. Here is how to turn it into a motion a team can run, without losing what got you here.",
  "h1":"When Founder-Led Sales Stops Scaling","eyebrow":"Guide",
  "lead":"Founder-led sales works right up until it does not. Here is why it stalls, and how to hand the motion to a team without the number falling off a cliff.",
  "sections":[
    {"h":"Why it stalls","p":["Founder-led sales works early because you are the best salesperson in the building. You know the product cold, you carry the authority to bend terms, and buyers trust the person who built the thing. That is also the trap. The motion lives in your head, not in a system, so it cannot be copied. Growth stays capped at the number of hours you can personally sell."]},
    {"h":"The signs you have hit the ceiling","ul":["Every real deal still needs you on the call to close","Reps you hired are busy but not closing","Your pipeline and forecast are a guess, because only you know which deals are real","Revenue flattens the moment you step back to run the company","New hires take months to ramp and most never reach your numbers"]},
    {"h":"What actually needs to transfer","p":["Hiring reps does not fix this. You are not short on bodies, you are short on a repeatable motion. What has to move out of your head and onto paper is the whole system: who the real buyer is, the message that lands, the qualifying questions, the objection answers, the steps from first call to signed, and the way you read a deal. Transfer the motion, then the people can run it."]},
    {"h":"How I fix it","p":["Week one I diagnose what you actually do when you sell, including the parts you do not even notice. Week two I turn it into a documented motion with a real forecast. Then I build and train the team to run it, replace who cannot, and own the number while they ramp. You get your week back without watching revenue stall."]},
    {"h":"What waiting costs","p":["Every quarter you stay the only closer is a quarter the company cannot grow past you, and a quarter your best reps spend learning nothing transferable. Founders who wait usually pay twice: once for the reps who did not work, and again to rebuild the motion later under pressure."]},
  ],
  "faqs":[
    {"q":"Why can't my reps close like I do?","a":"Because the motion lives in your head, not in a system they can learn. Reps are not short on effort, they are short on a documented way to sell the way you do. Build the motion, train them on it, and closing becomes teachable."},
    {"q":"Should I just hire a VP of Sales?","a":"Only if you can define the motion for them to scale. Hiring a VP to invent your sales process from scratch is how founders churn through expensive VPs. A fractional CRO builds the motion first, then you hire to run it."},
    {"q":"How long until the team can sell without me?","a":"A documented motion and a real forecast come in the first two weeks. Reps ramping on it is a matter of weeks after that, not the many months an unled hire takes."}],
  "related":'Part of <a href="/how-to-build-a-sales-team">how to build and scale a sales team</a>. See <a href="/services/sales-team-building">the sales team building service</a>, <a href="/services/fractional-cro">the fractional CRO service</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"building-a-sales-team-after-funding",
  "title":"Building a Sales Team After You Raise | Tal Paperin",
  "desc":"Just raised? The fastest way to burn the round is hiring reps with no motion and no leader. Here is the order of operations that turns funding into revenue.",
  "h1":"How to Build a Sales Team After You Raise","eyebrow":"Guide",
  "lead":"A round does not buy you a market, it buys you time. Here is how to spend it building a sales team that produces revenue instead of burning the raise.",
  "sections":[
    {"h":"The post-raise trap","p":["The board wants growth, so the instinct is to hire fast: a handful of reps, maybe an SDR team, and go. Then two quarters pass, the reps are busy, the pipeline looks full, and almost nothing closes. The money went out, the revenue did not come in. The round did not fail you. Hiring a team before you had a motion did."]},
    {"h":"The order that works","ul":["Lock the motion first: who buys, why, the message, and the repeatable path from first call to signed","Prove it with a few deals a non-founder can close, not just you","Hire a sales leader, or a fractional one, before you scale the headcount","Then add reps against a motion that already works, so they ramp on a system instead of guessing","Build the forecast and pipeline discipline before you are reporting on it to a board"]},
    {"h":"Where the money actually burns","p":["Founders burn the round in predictable places: reps hired with no leader above them, an SDR team feeding a funnel nobody qualified, discounts given to force early wins that set a bad price, and a forecast built on hope. Each one feels like progress and each one costs you a quarter you cannot get back."]},
    {"h":"How I help post-raise","p":["I come in as a fractional CRO, build the motion, hire and train the team against it, and own the number while it ramps, so you are not betting the round on a full-time hire who takes months to find and may not fit. You get senior leadership now, at a fraction of a full CRO cost, exactly when the pressure to grow is highest."]},
  ],
  "faqs":[
    {"q":"Should I hire reps right after raising?","a":"Not first. Reps hired before you have a repeatable motion and a leader to run it are the most common way founders burn a round. Lock the motion, prove it, add the leader, then scale reps against it."},
    {"q":"Full-time CRO or fractional after a raise?","a":"Fractional is often right straight after a raise: you get senior leadership immediately, build the motion and the team, and avoid betting the round on a months-long full-time search. Move to full-time once the function justifies the salary."},
    {"q":"How fast should the team be producing?","a":"You should have a documented motion and a real forecast within the first two weeks, with reps ramping on it over the following weeks, rather than a team that looks busy for two quarters with nothing closing."}],
  "related":'Part of <a href="/how-to-build-a-sales-team">how to build and scale a sales team</a>. See <a href="/services/sales-team-building">sales team building</a>, <a href="/fractional-cro-for-startups">fractional CRO for startups</a>, <a href="/setting-sales-quotas">how to set sales quotas</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"sales-team-missing-quota",
  "title":"Sales Team Missing Quota? How to Fix It | Tal Paperin",
  "desc":"Your sales team keeps missing quota. It is usually not the reps. Here is the real diagnosis, from pipeline coverage to deal inspection, and how I fix it.",
  "h1":"When Your Sales Team Keeps Missing Quota","eyebrow":"Guide",
  "lead":"When a team misses quota two quarters running, the instinct is to blame the reps or swap them out. That is almost always the wrong move. Most quota misses are a pipeline and process problem, and you can fix those without firing anyone.",
  "sections":[
    {"h":"It is usually not an effort problem","p":["Reps who miss quota are rarely lazy. They are usually working hard against a motion that cannot produce the number. If there is not enough qualified pipeline in front of them, no amount of calls closes the gap. If the stages have no real meaning, deals that were never going to close sit in the forecast until the end of the quarter, then vanish. Before you touch the roster, look at what you are asking the team to run."]},
    {"h":"The real reasons teams miss","ul":["Thin pipeline. The rule of thumb is three to four times quota in qualified pipeline to have a real shot at the number. Below three times, the math is against you no matter how good the reps are","No qualification, so deals that will never close eat the quarter and die in the last two weeks","A quota set with no basis in capacity or historical win rates, so the team was never going to hit it","No deal inspection. Nobody looks at the real deals weekly, so at-risk deals get attention only after they are lost","Comp that pays for activity and meetings instead of closed revenue, so the team optimizes for the wrong thing","The wrong ICP, so reps spend the quarter selling to buyers who were never going to buy"]},
    {"h":"The diagnosis I run first","p":["Week one I pull the real numbers: pipeline coverage against quota, win rate by stage, average deal size and cycle length, and where deals actually die. That tells me whether the problem is top of funnel, mid-funnel qualification, late-stage closing, or a quota that was fiction from the start. Most of the time the answer is some mix of too little pipeline and stages that mean nothing, not a team that cannot sell."]},
    {"h":"How I fix it","p":["I rebuild pipeline generation so there is enough qualified volume to hit the number, define the stages with real entry and exit criteria, and run weekly deal inspection so deals get help while there is still time to save them. I retrain the reps who can improve, replace the ones who cannot, and reset the quota to something tied to real capacity so the team can win. Then I own the number while it recovers, instead of handing you a report and leaving."]},
    {"h":"What waiting costs","p":["Every quarter you blame the reps and churn the roster, you reset the ramp clock and lose the pipeline the leaving reps were carrying. The miss compounds: a bad quarter becomes a bad year, the board loses trust in the forecast, and you end up rebuilding the whole motion later under more pressure and less cash."]},
  ],
  "faqs":[
    {"q":"Should I fire reps who miss quota?","a":"Usually not first. Most misses trace back to thin pipeline, weak qualification or a quota with no basis, not rep effort. Diagnose the motion before you churn the roster, or you will reset the ramp clock and lose their pipeline for the same underlying problem."},
    {"q":"How much pipeline should my team have?","a":"A common benchmark is three to four times quota in qualified pipeline. Below three times, the math is against you regardless of how good the reps are. If coverage is thin, the fix is pipeline generation, not pressure."},
    {"q":"How fast can you turn a missing team around?","a":"I diagnose in week one and give you a plan and a real forecast in week two. Pipeline and process fixes follow, and the quota I reset is one the team can actually hit, so the recovery is real rather than another hopeful number."}],
  "related":'Part of <a href="/how-to-build-a-sales-team">how to build and scale a sales team</a>. See <a href="/setting-sales-quotas">how to set sales quotas reps can hit</a>, <a href="/sales-forecast-always-wrong">why your forecast is always wrong</a>, <a href="/hired-reps-but-no-pipeline">hired reps but no pipeline</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"sales-forecast-always-wrong",
  "title":"Why Your Sales Forecast Is Always Wrong | Tal Paperin",
  "desc":"You commit a number to the board, then miss it. Again. Here is why your sales forecast keeps missing, and the discipline that makes it trustworthy.",
  "h1":"Why Your Sales Forecast Is Always Wrong","eyebrow":"Guide",
  "lead":"You commit a number to the board, then miss it by a third. Next quarter, same story. A forecast that is always wrong is not bad luck. It is a pipeline you cannot trust and a process that lets everyone guess.",
  "sections":[
    {"h":"A forecast is only as honest as the pipeline under it","p":["A forecast is not a spreadsheet exercise. It is a claim about which deals will close and when, and it is only as good as the pipeline it reads from. If the pipeline is full of deals nobody qualified, stages that mean nothing, and probabilities reps set to feel good, the forecast will miss every time. The number on the board is downstream of the discipline in the CRM."]},
    {"h":"Why the number keeps missing","ul":["Stages with no documented entry and exit criteria, so a deal is in stage three because a rep felt like it, not because anything happened","Reps set their own close probability, so optimism and happy ears inflate the number","Deals that have sat untouched for months still counted as live, padding the pipeline","A stale CRM nobody updates, so the forecast reads last month's reality","Win probabilities that were never calibrated against your actual closed-won history","A side spreadsheet that disagrees with the CRM, so there is no single source of truth"]},
    {"h":"What a forecast you can trust actually needs","p":["Defined stages with real exit criteria, so a deal only advances when something concrete happened: a demo done, a champion confirmed, pricing agreed, procurement engaged. Probabilities calibrated to how your deals have actually closed, not round numbers. Weekly deal inspection where someone senior pressure-tests the real deals and calls them honestly. And one source of truth, the CRM, with no shadow spreadsheet running next to it."]},
    {"h":"How I fix it","p":["I define the stages and the exit criteria, clean the dead weight out of the pipeline, and calibrate probabilities to your real win history. Then I run weekly deal inspection and call the deals honestly, including the ones the team wants to believe in. Within a couple of weeks you have a forecast that holds up, and you can hire, spend and report against it without getting burned."]},
    {"h":"What a wrong forecast costs you","p":["A forecast you cannot trust poisons every decision that depends on it. You hire ahead of revenue that does not arrive, you commit cash against deals that were never real, and you lose the board's trust in every future number you give them. Once a board stops believing your forecast, every raise and every plan gets harder."]},
  ],
  "faqs":[
    {"q":"Why is my sales forecast always too high?","a":"Almost always because reps set their own probabilities and nobody inspects the deals. Optimism and happy ears inflate the number, dead deals stay in the pipeline, and stages have no real meaning. Fix the stage criteria and run honest weekly inspection and the forecast tightens fast."},
    {"q":"Is inaccurate forecasting a CRM problem or a sales problem?","a":"Both, and they feed each other. Undefined stages and uncalibrated probabilities are configuration problems; reps setting their own odds and nobody inspecting deals is a discipline problem. You have to fix the system and the habit together, which is exactly what I do in the first two weeks."},
    {"q":"How quickly can you make the forecast reliable?","a":"I define stages and exit criteria and clean the pipeline in the first week, then run weekly deal inspection from there. Within a couple of weeks the forecast reflects real deals, and it keeps tightening as the calibrated probabilities get tested against actual closes."}],
  "related":'See <a href="/services/fractional-cro">the fractional CRO service</a>, <a href="/sales-team-missing-quota">sales team missing quota</a>, <a href="/services/go-to-market-strategy">go-to-market strategy</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"hired-reps-but-no-pipeline",
  "title":"Hired Sales Reps but No Pipeline? Here Is Why | Tal Paperin",
  "desc":"You added sales headcount and the pipeline still will not grow. Here is why reps do not produce pipeline on their own, and how I build the motion that does.",
  "h1":"You Hired Sales Reps and Still Have No Pipeline","eyebrow":"Guide",
  "lead":"The headcount went up. The pipeline did not. You hired reps expecting pipeline to follow, and a couple of quarters later they look busy and nothing is in the funnel. Headcount is not a motion, and reps cannot manufacture one that does not exist yet.",
  "sections":[
    {"h":"Headcount is not a motion","p":["Hiring reps feels like buying pipeline. It is not. A rep can run a motion that already works, but almost none can invent one from scratch at a company they just joined. If you drop people into a seat with no ICP, no message, no target list and no outbound system, they will fill their day with activity and produce almost no pipeline. The gap is not effort. There is nothing for the effort to run on."]},
    {"h":"Why the pipeline stays empty","ul":["You hired closers and expected them to prospect. Most strong closers are weak at outbound and need leads handed to them","No outbound system exists: no sequences, no target list, no method, so every rep improvises and most do it badly","No sharp ICP, so reps spray across a market and nothing converts","SDRs hired with no playbook and no coach, left to figure out messaging on their own","You measure activity, calls and emails sent, instead of qualified pipeline created, so busy looks like progress","Nobody senior owns the motion, so there is no one job to build and fix the engine"]},
    {"h":"What has to exist before reps can produce","p":["Reps produce pipeline when there is a real motion to run: a sharp ICP, a message that lands with that buyer, a built target list, an outbound sequence that gets replies, qualifying questions that sort real from polite, and a documented playbook so the whole thing is teachable. Build that first and the same reps who were spinning start filling the funnel. Skip it and no hire fixes the number."]},
    {"h":"How I fix it","p":["I build the outbound motion from the ICP out: who to target, the message, the list, the sequence, the qualification. I put the right people in the right seats, SDRs to prospect and AEs to close, and train them on the motion instead of leaving them to guess. Then I inspect pipeline created, not activity, so we see what is actually working and double down. You get a funnel that fills, built by someone who has done it from zero more than once."]},
    {"h":"What it costs to wait","p":["Every quarter of busy-but-empty is salary spent on reps learning nothing transferable, and a funnel that stays dry while the board waits for growth. The longer it runs, the more your good hires burn out on a broken motion and leave, so you pay to hire, pay to wait, and pay again to rebuild."]},
  ],
  "faqs":[
    {"q":"Why aren't my new sales reps generating pipeline?","a":"Usually because there is no motion for them to run. No sharp ICP, no outbound system, no target list, no playbook. Strong closers in particular are weak at prospecting and need pipeline handed to them. Build the motion first and the same reps start producing."},
    {"q":"Should I hire more reps to get more pipeline?","a":"Not until a motion exists. Adding headcount to a broken motion multiplies the cost without multiplying the pipeline. Build and prove the outbound engine, then hire against something that already works so new reps ramp on a system instead of guessing."},
    {"q":"Do I need SDRs or AEs to fix an empty pipeline?","a":"Often both, in the right seats. SDRs prospect and book meetings, AEs close. The common mistake is hiring closers and expecting them to prospect, or hiring SDRs with no playbook. I put the right people in the right seats and train them on a built motion."}],
  "related":'See <a href="/services/fractional-cro">the fractional CRO service</a>, <a href="/services/sales-team-building">sales team building</a>, <a href="/founder-led-sales-wont-scale">founder-led sales will not scale</a>, <a href="/outsourced-sdr-team">an outsourced SDR team</a>, <a href="/go-to-market-motion">how to choose your go-to-market motion</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"how-to-build-a-sales-team",
  "title":"How to Build and Scale a B2B Sales Team | Tal Paperin",
  "desc":"The order that turns founder-led selling into a team that hits the number: prove the motion, hire a leader, then reps, comp, quotas and pipeline discipline.",
  "h1":"How to Build and Scale a B2B Sales Team","eyebrow":"Guide",
  "lead":"Most founders build a sales team in the wrong order. They hire reps first and hope a motion shows up. It does not. Here is the order that actually works, from the first deal you closed yourself to a team that hits the number without you in every call. It is the same sequence I run as a fractional CRO.",
  "sections":[
    {"h":"Headcount is the last step, not the first","p":["Hiring reps feels like buying revenue. It is not. A rep can run a sales motion that already works, but almost none can invent one at a company they just joined. Drop people into seats with no ICP, no message and no process, and they fill the day with activity while the pipeline stays dry. Build the team in the wrong order and you burn a year and a lot of salary proving that headcount is not a motion. Build it in the right order and the same hires produce.","The right order starts with what you already have: the deals you closed yourself. Those hold the first draft of the motion a team will run."]},
    {"h":"The order that works","tiers":["Prove the motion first. Pull apart your real closed deals: who bought, what hurt, what convinced them, and the path from first call to signature. That is your playbook, extracted from fact instead of invented in a room.","Prove a non-founder can run it. Get one or two deals closed by someone who is not you. If only the founder can close, you have charisma, not a motion.","Hire a leader before a pile of reps. Someone has to own the number, coach the floor and fix the engine. A full-time VP of Sales or a fractional one, but someone senior, before you scale headcount.","Make your first sales hires against a motion that works, so they ramp on a system instead of guessing.","Set comp that pays for the behavior you want, and quotas built from real capacity.","Run pipeline and forecast discipline from the start, so you can see which deals are real before the board asks."]},
    {"h":"Your first hire is a decision, not a job post","p":["The first salesperson you hire is the riskiest hire you will make, because there is no team around them to absorb a miss. The common mistake is hiring a senior closer and expecting them to build the motion and prospect their own pipeline. Most strong closers do neither. Decide what you actually need first: someone to run a motion you have already proven, or someone to help you prove it. Those are different people."]},
    {"h":"A leader before a floor of reps","p":["Reps without a leader do not manage themselves into a number. They drift. A sales leader owns the forecast, inspects the real deals weekly, coaches the people who can improve and replaces the ones who cannot. If you cannot justify a full-time VP of Sales yet, that is exactly the gap a fractional leader fills: senior ownership now, without the full-time salary, while the function is still too small to carry one."]},
    {"h":"Comp and quotas are the steering wheel","p":["Once there is a team, how you pay it decides how it behaves. Reps do exactly what the plan pays them to do, not what you said in the kickoff. Get the base-to-variable split right by role, set OTE to the market, and keep the plan simple enough that a rep can calculate their own check. Then set quotas from real capacity, not from the growth number the board wants, because a quota nobody can hit demotivates the team and hides who can actually sell."]},
    {"h":"The signs you scaled too early","ul":["Reps are busy but the pipeline is not growing","Only the founder can close a real deal","You hired closers and expected them to prospect","Nobody senior owns the number day to day","Comp pays for activity, so the team optimizes for the dashboard","The forecast is a guess because the stages mean nothing"]},
    {"h":"Go deeper on each part","links":[["When founder-led sales stops scaling","/founder-led-sales-wont-scale"],["Building a sales team after you raise","/building-a-sales-team-after-funding"],["How to build a sales compensation plan","/sales-compensation-plan"],["How to set sales quotas reps can hit","/setting-sales-quotas"],["When your team keeps missing quota","/sales-team-missing-quota"],["Hired reps but no pipeline","/hired-reps-but-no-pipeline"],["Sales team building service","/services/sales-team-building"]]},
    {"h":"How I build it","p":["I come in as a fractional CRO or VP of Sales, extract the motion from your real deals, hire and train the team against it, set the comp and the quotas, and own the number while the team ramps. You get senior revenue leadership exactly when the pressure to grow is highest, without betting a round on a months-long full-time search. If you are hiring reps and hoping, that is the problem I fix."]},
  ],
  "faqs":[
    {"q":"What is the right order to build a sales team?","a":"Prove the motion from your own closed deals, prove a non-founder can run it, hire a leader to own the number, then add reps against a motion that works, then set comp and quotas and run pipeline discipline. Headcount is the last step, not the first."},
    {"q":"Should I hire a sales leader or reps first?","a":"A leader, or a fractional one, before a pile of reps. Reps without someone senior owning the number, coaching the floor and inspecting deals tend to drift and miss. The leader builds and fixes the engine the reps run."},
    {"q":"When should founders stop selling and build a team?","a":"When you are the only one who can close, revenue is capped at your hours, and deals still run through you. That is the ceiling. The fix is to transfer the motion to a team, not to add more of your own time."},
    {"q":"Can a fractional CRO build the team instead of a full-time hire?","a":"Yes, and it is often the right call before the function justifies a full-time salary. A fractional CRO builds the motion, hires and trains the team, sets comp and quotas and owns the number, so you get senior leadership now without a long full-time search."}],
  "related":'See the <a href="/services/sales-team-building">sales team building</a> and <a href="/services/fractional-cro">fractional CRO</a> services, then go deeper on <a href="/sales-compensation-plan">sales compensation plans</a>, <a href="/setting-sales-quotas">setting sales quotas</a>, <a href="/founder-led-sales-wont-scale">why founder-led sales stops scaling</a> and <a href="/building-a-sales-team-after-funding">building a team after you raise</a>. Or read <a href="/blog/scale-founder-led-to-team">how to scale from founder-led to a team</a>.'},

 {"slug":"sales-compensation-plan",
  "title":"How to Build a Sales Compensation Plan | Tal Paperin",
  "desc":"Reps do exactly what you pay them to do. How to set base, variable, OTE and quota by role, keep the plan simple, and avoid the mistakes that backfire.",
  "h1":"How to Build a Sales Compensation Plan That Works","eyebrow":"Guide",
  "lead":"Show me a sales team behaving strangely and I will show you a comp plan that pays it to behave that way. Reps do exactly what the plan pays them to do, not what you say in the kickoff. If the behavior is wrong, the plan is wrong. Here is how to build one that pulls in the right direction.",
  "sections":[
    {"h":"Split base and variable by role","p":["Not every seat should carry the same risk. The split depends on how much control the person has over the outcome. Load variable onto a seat that only partly influences the result and you punish people for things outside their hands."],
     "tiers":["SDR, roughly 70/30 base to variable. They create pipeline but do not close, so you cannot hang all their pay on a number they only partly control. Pay them for qualified meetings and pipeline that converts, not raw activity.","AE, roughly 50/50, sometimes 60/40. They own the close, so more of their pay should ride on it. This is the seat where variable really bites.","Sales leader, mostly base with a component tied to team quota, so they are paid to build and coach the whole team, not to hoard the best deals for themselves."]},
    {"h":"Set OTE to the market","p":["OTE, on-target earnings, is the total a rep makes at 100 percent of quota. It is the number that recruits and retains, so anchor it to your market or you lose people to the companies that got it right. Underpay OTE and your best reps leave the moment someone offers them a fair number."]},
    {"h":"Get the quota-to-OTE ratio right","p":["The oldest rule in sales comp is that a rep should generate three to five times their total cost in bookings. An AE on a 150k OTE carries a quota somewhere around 450k to 750k, adjusted for margin, cycle and deal size. Set it too low and you overpay for mediocrity. Set it too high and reps decide it is unhittable and stop trying, which is the most expensive failure of all, because a demotivated team still draws base."]},
    {"h":"Pay for outcomes, and keep it simple","p":["Commission on closed revenue, not on calls made or emails sent. The moment you pay for activity you get activity, reps optimizing for the dashboard instead of the deal. Pay for the result and let them find the path.","Then keep it simple enough that a rep can calculate their own check. That is the test almost every plan fails. If a rep cannot do the math in their head after a deal closes, the plan is too complicated to motivate anyone. One or two clear levers and a rate they know cold beats a page of accelerators nobody understands."]},
    {"h":"The mistakes that backfire","ul":["Capping commission, so your best rep stops selling the day they hit the ceiling","Changing the plan mid-year because someone is making too much, which is the fastest way to kill trust","Too many accelerators and kickers nobody can follow","Quotas set by what the board wants instead of what the market supports","Paying on booked revenue with no clawback when the deal cancels, so you reward signings that never pay"]},
    {"h":"Where this fits","links":[["How to build and scale a sales team","/how-to-build-a-sales-team"],["How to set sales quotas reps can hit","/setting-sales-quotas"],["Sales team building service","/services/sales-team-building"]]},
  ],
  "faqs":[
    {"q":"What is a good base-to-variable split for sales reps?","a":"It depends on control over the outcome. SDRs sit around 70/30 base to variable because they create pipeline but do not close. AEs sit around 50/50, sometimes 60/40, because they own the close. A sales leader is mostly base with a slice tied to team quota."},
    {"q":"How do I set a sales quota against OTE?","a":"The common rule is that a rep should produce three to five times their total cost in bookings. An AE on a 150k OTE carries roughly a 450k to 750k quota, adjusted for margin, cycle and deal size. Too low overpays for mediocrity, too high gets ignored."},
    {"q":"Why is my sales comp plan not motivating the team?","a":"Usually because it pays for activity instead of outcomes, or it is too complex for a rep to calculate their own check. Pay commission on closed revenue, keep it to one or two clear levers, and set OTE to the market so the number is worth chasing."},
    {"q":"Should I cap sales commission?","a":"No. A cap tells your best rep to stop selling the day they hit the ceiling, which is the opposite of what you want. Uncapped commission with an honest quota keeps the top performers pushing all year."}],
  "related":'Part of <a href="/how-to-build-a-sales-team">how to build and scale a sales team</a>. See also <a href="/setting-sales-quotas">setting sales quotas</a>, the <a href="/services/sales-team-building">sales team building service</a>, or read <a href="/blog/sales-comp-plans-that-work">sales comp plans that actually motivate</a>.'},

 {"slug":"setting-sales-quotas",
  "title":"How to Set Sales Quotas That Work | Tal Paperin",
  "desc":"A quota nobody hits demotivates the team and hides who can sell. How to build quotas bottoms-up from rep capacity, ramp and pipeline math, not a board wish.",
  "h1":"How to Set Sales Quotas Reps Can Actually Hit","eyebrow":"Guide",
  "lead":"Most quotas are fiction. The board wants to triple revenue, so the growth number gets divided by the number of reps and handed out as targets. Nobody asked whether a single rep, working a full year, could produce that number. That is not a quota. It is a wish with a name on it. Here is how to set one the team can actually hit.",
  "sections":[
    {"h":"A quota is a claim about capacity, not a wish","p":["When nobody hits the number, everyone loses. Reps stop believing it, so they stop trying and start managing their excuses instead. You lose the one thing a quota is supposed to give you: a clean signal about who can sell and who cannot. A quota set from fantasy tells you nothing, because everyone misses it."]},
    {"h":"Build it bottoms-up, not top-down","p":["A real quota starts from what one rep can physically do. Take your actual numbers, not your hopes."],
     "ul":["Deals per rep per year: how many your best reps actually closed last year, across the full year, not the one good quarter","Average deal size: your real ACV weighted toward what closes, not the one whale you signed once","Ramp time: a rep hired in Q2 does not carry a full-year number, so prorate it or you are lying to yourself in the forecast"]},
    {"h":"The coverage math behind the number","p":["A quota only means something if there is enough pipeline to feed it. The rule of thumb is three to four times quota in qualified pipeline to have a real shot at the number. Below three times, the math is against the rep no matter how good they are. So a quota is really two numbers: the target, and the pipeline coverage that makes it reachable. Set the target and ignore the coverage and you are back to a wish."]},
    {"h":"The gap between the board number and reality is data","p":["When the bottoms-up number and the board number do not match, that gap is the most useful thing on the page. It tells you exactly what has to change: more reps, higher ACV, a better win rate, shorter cycles, or a different motion. That is a strategy conversation, not a spreadsheet you paper over by inflating individual targets. Companies that refuse to have it set the impossible number, miss it, blame the reps, churn them, and set the same number again."]},
    {"h":"Ramp quotas, so new hires are not set up to fail","p":["A new rep carrying a full quota from day one is a rep you are planning to disappoint. Ramp the quota over the first two or three quarters while they learn the motion and build pipeline. A ramp quota protects the hire, gives you an honest read on whether they are tracking, and keeps your forecast from counting revenue that was never going to land that quarter."]},
    {"h":"Where this fits","links":[["How to build and scale a sales team","/how-to-build-a-sales-team"],["How to build a sales compensation plan","/sales-compensation-plan"],["Sales team building service","/services/sales-team-building"]]},
  ],
  "faqs":[
    {"q":"How do I set a sales quota that is actually achievable?","a":"Build it bottoms-up from one rep's real capacity: deals per rep per year, average deal size and ramp time. Multiply deals by deal size, subtract for ramp, and you have the honest floor. Set the quota above it so it stretches, but within reach of a good rep having a good year."},
    {"q":"How much pipeline do I need to hit quota?","a":"A common benchmark is three to four times quota in qualified pipeline. Below three times, the math is against the rep regardless of how good they are. A quota is really two numbers: the target and the coverage that makes it reachable."},
    {"q":"What do I do when the board number is higher than capacity?","a":"Treat the gap as data, not a rounding error. It tells you what has to change: more reps, higher ACV, a better win rate or a different motion. That is a strategy decision, not something you fix by inflating each rep's target and hoping."},
    {"q":"Should new reps carry a full quota?","a":"No. Ramp the quota over the first two or three quarters while they learn the motion and build pipeline. A full number from day one sets the hire up to fail and puts revenue in your forecast that was never going to land."}],
  "related":'Part of <a href="/how-to-build-a-sales-team">how to build and scale a sales team</a>. See also <a href="/sales-compensation-plan">sales compensation plans</a>, <a href="/sales-team-missing-quota">when your team keeps missing quota</a>, the <a href="/services/sales-team-building">sales team building service</a>, or read <a href="/blog/set-sales-quotas-you-can-hit">how to set sales quotas your team can hit</a>.'},

 {"slug":"fractional-cro-for-startups",
  "title":"Fractional CRO for Startups | Tal Paperin",
  "desc":"A fractional CRO for startups: senior revenue leadership from first revenue to Series B without a full-time hire. The motion, the team and the number.",
  "h1":"Fractional CRO for Startups","eyebrow":"For Startups",
  "lead":"Startups need senior revenue leadership before they can afford it. That gap is what a fractional CRO fills: I build the motion, hire the team and own the number, without a full-time salary.",
  "sections":[
    {"h":"Why startups stall on revenue","p":["Most startups get the first deals from the founders and the network, then stall because there is no repeatable motion and nobody senior owns the number. Hiring a $250,000 CRO too early burns runway; hiring junior reps with no leader burns time. A fractional CRO gives you the senior owner now and builds the engine the reps will run."]},
    {"h":"What I build for a startup","ul":["A validated ICP, positioning and pricing for how you actually get bought","The outbound and inbound motion, the playbook, the CRM and the pipeline","The first sales hires, trained and managed, and the ones to replace","A real forecast the board can trust","The founders out of every deal and into the right ones"]},
    {"h":"Built for real startups","p":["I have come in as Fractional VP of Sales from day one, defined the ICP, built the outbound motion from zero and rebuilt it through pivots. Same discipline whether you are pre-seed or Series B: own the number, build the motion, make the team hit quota."]},
  ],
  "faqs":[
    {"q":"When should a startup hire a fractional CRO?","a":"When the founders are still the only ones closing, or you need a repeatable motion and a forecast before you can justify a full-time CRO. Usually from first revenue through Series B."},
    {"q":"Is a fractional CRO affordable for a startup?","a":"Yes, that is the point. You get senior revenue leadership for $2,000 to $12,000 a month, billed monthly, instead of a $250,000-plus full-time salary plus equity."},
    {"q":"Will you do the work or just advise?","a":"I do the work. I hire, train and manage the reps, own the pipeline and the forecast, and step into the big deals myself, not just hand you a slide deck."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"interim-cro",
  "title":"Interim CRO | Tal Paperin",
  "desc":"An interim CRO to own revenue during a gap, a transition or a turnaround. Senior leadership in the seat now, hands-on, without a permanent hire.",
  "h1":"Interim CRO","eyebrow":"Guide",
  "lead":"When you need a CRO in the seat now, during a gap, a transition or a turnaround, I step in and own the number while you decide on the permanent answer.",
  "sections":[
    {"h":"When you need an interim CRO","ul":["Your CRO or VP of Sales just left and the number cannot wait","You are mid-turnaround and need senior leadership immediately","You are between rounds or in a transition and need a steady hand","You need to stabilize revenue while you run a full-time search"]},
    {"h":"What I do in the seat","p":["I take ownership of the revenue function from day one: the team, the pipeline, the forecast and the deals. Week one is diagnosis, then I run it, keep the team productive, hold the key deals together, and hand over a healthier function than I found, whether that is to a permanent CRO or back to you."]},
    {"h":"Interim, fractional, or both","p":["Interim usually means full or near-full time for a defined stretch. Fractional means part of the week, ongoing. I do either, and many engagements start interim during a crisis and settle into fractional once the function is stable."]},
  ],
  "faqs":[
    {"q":"What is the difference between an interim CRO and a fractional CRO?","a":"Interim is typically full-time for a defined period, often to cover a gap or a turnaround. Fractional is part of the week on an ongoing basis. I do both and often move from one to the other."},
    {"q":"How fast can you step in as interim CRO?","a":"Fast. Interim engagements exist because the number cannot wait, so I diagnose in week one and am running the function immediately."},
    {"q":"Can you hand over to a permanent CRO?","a":"Yes. Part of an interim engagement is leaving a stronger, documented function and a clean handover to whoever takes the seat permanently."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-vp-of-sales",
  "title":"Fractional VP of Sales | Tal Paperin",
  "desc":"A Fractional VP of Sales who builds and runs your sales team, the playbook and the pipeline, hands-on, without a full-time hire.",
  "h1":"Fractional VP of Sales","eyebrow":"Guide",
  "lead":"Need someone to build the team and run the sales floor, not just set strategy? That is a Fractional VP of Sales. I hire, train and manage the reps and own the pipeline, part-time.",
  "sections":[
    {"h":"Fractional VP of Sales vs fractional CRO","p":["A VP of Sales runs the sales team and the pipeline day to day. A CRO owns all of revenue, sales, marketing and go-to-market, and the number itself. I do both; the right title depends on whether you need the sales floor run or the whole revenue function owned. Many companies start with a Fractional VP of Sales and grow the scope into CRO."]},
    {"h":"What I own as Fractional VP of Sales","ul":["Hiring, training and managing SDRs, AEs and BDs","The playbook, the talk tracks and the sales process","The CRM, the pipeline and the forecast","Coaching reps to quota and replacing who cannot","Day-to-day management of the sales floor"]},
    {"h":"Built the team before, many times","p":["I have recruited, trained and managed sales teams across five continents and 40-plus countries, from first reps to full floors with SDRs, AEs, post-sales and tech support. I make the team you have hit quota and build the team you do not have yet."]},
  ],
  "faqs":[
    {"q":"What does a Fractional VP of Sales do?","a":"Builds and runs your sales team and pipeline part-time: hiring, training and managing reps, owning the playbook, the CRM and the forecast, and coaching the team to quota."},
    {"q":"Fractional VP of Sales or fractional CRO?","a":"Choose a VP of Sales to run the sales team and pipeline. Choose a CRO to own all of revenue including marketing and go-to-market. I do both and can grow the scope as you do."},
    {"q":"How much does a Fractional VP of Sales cost?","a":"Typically $2,000 to $12,000 a month depending on hours, billed monthly with no lock-in, far below a full-time VP salary."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/sales-team-building">team building</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-chief-sales-officer",
  "title":"Fractional Chief Sales Officer (CSO) | Tal Paperin",
  "desc":"A fractional Chief Sales Officer who owns the sales organization, strategy and number, hands-on, without a full-time executive salary.",
  "h1":"Fractional Chief Sales Officer","eyebrow":"Guide",
  "lead":"A fractional Chief Sales Officer owns the sales organization end to end, strategy, structure, team and number, for the part of the week you need, without a full-time executive hire.",
  "sections":[
    {"h":"What a fractional CSO owns","ul":["Sales strategy, structure and segment or territory design","The leadership layer and the sales team beneath it","Comp plans, quotas, the playbook and the process","The pipeline, the forecast and the number","Hiring, coaching and the hard personnel calls"]},
    {"h":"CSO, CRO or VP of Sales","p":["A Chief Sales Officer owns the sales organization. A CRO owns all of revenue including marketing and go-to-market. A VP of Sales runs the team day to day. The labels matter less than the work; tell me where revenue is stuck and I will own the right scope."]},
    {"h":"Senior, hands-on, proven","p":["I have led as VP of Global and International Sales and stepped in as a fractional revenue leader for 30-plus B2B companies. I do not advise from the side; I own the strategy and then run it, hands-on."]},
  ],
  "faqs":[
    {"q":"What is a fractional Chief Sales Officer?","a":"A senior sales executive who owns your sales organization, strategy, team and number part-time, without a full-time CSO salary or long-term lock-in."},
    {"q":"How is a CSO different from a CRO?","a":"A CSO owns the sales organization. A CRO owns all of revenue, including marketing and go-to-market. I take on either depending on what you need owned."},
    {"q":"What does it cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-roi",
  "title":"Is a Fractional CRO Worth It? The ROI | Tal Paperin",
  "desc":"The business case for a fractional CRO: what it costs, what it returns, and how it compares to a full-time hire or doing nothing.",
  "h1":"Is a Fractional CRO Worth It?","eyebrow":"Guide",
  "lead":"A fractional CRO is not a cost, it is a bet on the number. Here is the honest business case: what you pay, what it returns, and what doing nothing costs.",
  "sections":[
    {"h":"What you pay","p":["Roughly $2,000 to $12,000 a month depending on how much of the week you need, billed monthly with no long-term contract. No equity, no bonus, no severance risk, no recruiting fee, no ramp."]},
    {"h":"What it returns","p":["A repeatable motion, a real forecast, a team that hits quota and senior ownership of the number, in weeks instead of quarters. The return is not the retainer you save; it is the revenue you stop leaving on the table because nobody senior owned the pipeline."]},
    {"h":"The cost of the alternatives","ul":["A full-time CRO: $250,000-plus all in, months to hire and ramp, real severance risk if the fit is wrong","A wrong VP hire: six figures and a year lost","Doing nothing: stalled revenue that rarely fixes itself"]},
  ],
  "faqs":[
    {"q":"Is a fractional CRO worth the money?","a":"If revenue is stalled and nobody senior owns the number, yes. You get CRO-level leadership for a fraction of a full-time salary, billed monthly, so it has to keep earning the renewal."},
    {"q":"How do you measure the return?","a":"Pipeline built, forecast accuracy, win rate, rep ramp time and the number itself. I own a forecast I am accountable for, not vanity activity."},
    {"q":"What if it does not work out?","a":"Engagements are monthly with no lock-in. If I am not delivering, you end it in a month. That is the point of fractional."}],
  "related":'Compare <a href="/fractional-cro-cost">the cost</a> and <a href="/fractional-cro-vs-vp-of-sales">CRO vs VP of Sales</a>, or <a href="/contact">get in touch</a>.'},

 {"slug":"outsourced-sales-and-marketing-department","en_only":True,
  "title":"Outsourced Sales and Marketing Department | KSW Solutions",
  "desc":"An entire outsourced sales and marketing department for hire: the people and the senior management under one roof, via KSW Solutions.",
  "h1":"Outsourced Sales and Marketing Department","eyebrow":"KSW Solutions",
  "lead":"Do not build a revenue function from scratch. Rent the whole thing. Through KSW Solutions you get an entire sales and marketing department, the people and the senior leadership both, under one roof.",
  "sections":[
    {"h":"The whole department, not a freelancer","p":["Most outsourcing gives you a freelancer or an agency that runs one channel. KSW Solutions gives you the entire revenue function: SDRs, AEs, BDs and marketing, plus the VP and CRO-level management that hires, trains, manages and owns the number. One accountable team, outside your headcount."]},
    {"h":"What you get","ul":["Native-speaking SDRs and AEs for your target markets","Marketing that feeds pipeline, not just activity","Senior sales leadership and a VP overseeing the motion","The CRM, the playbook, the pipeline and the process, built and run","A forecast and accountability for the number"]},
    {"h":"When it beats hiring in-house","p":["When building a team is too slow, too expensive or too risky for your stage. You get a working revenue engine in weeks, not the six to twelve months it takes to hire and ramp one yourself, and none of the severance risk if the fit is wrong. When you are ready to bring it in-house, we hand over a working function, not a mess."]},
  ],
  "faqs":[
    {"q":"What is an outsourced sales and marketing department?","a":"The entire revenue function run for you outside your headcount: SDRs, AEs, BDs and marketing plus the senior management that runs them, hired, trained, managed and accountable for the number."},
    {"q":"How is this different from a lead-gen agency?","a":"An agency runs one channel and hands you leads. KSW Solutions runs the whole function, sales and marketing, people and leadership, and owns the pipeline and the number end to end."},
    {"q":"Can we bring it in-house later?","a":"Yes. Many clients use us to stand up a working revenue engine fast, then transition it in-house with a clean handover once it is proven."}],
  "related":'Run by <a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>. See the <a href="/services/outsourced-sales">outsourced sales</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"outsourced-sdr-team","en_only":True,
  "title":"Outsourced SDR Team | KSW Solutions",
  "desc":"An outsourced SDR and BDR team that books qualified meetings, built, trained and managed for you outside your headcount.",
  "h1":"Outsourced SDR Team","eyebrow":"KSW Solutions",
  "lead":"Need pipeline, not headcount? Get an outsourced SDR team that books qualified meetings, built, trained and managed for you, with senior leadership over it.",
  "sections":[
    {"h":"What you get","ul":["Native-speaking SDRs and BDRs for your markets","The outbound motion, the lists, the sequences and the scripts","A manager and senior leadership over the team, not reps left alone","The CRM, the cadence and the reporting","Qualified meetings handed to your closers"]},
    {"h":"Why outsource the top of funnel","p":["Hiring, training and managing SDRs in-house is slow and high-churn, and most teams never build a real outbound system. We run the motion that books meetings while you focus on closing and product. You get pipeline in weeks, not after a long hiring cycle."]},
    {"h":"Run by people who have built floors","p":["This is not a call center. The SDR team sits under senior sales leadership that has recruited, trained and managed reps across five continents, on a playbook that actually books meetings."]},
  ],
  "faqs":[
    {"q":"What does an outsourced SDR team do?","a":"Runs your top of funnel: building lists, sequences and scripts, doing the outbound, and booking qualified meetings for your closers, all managed for you outside your headcount."},
    {"q":"Outsourced SDRs or in-house?","a":"Outsource when you need pipeline fast and do not want the hiring, training and churn of building an SDR function in-house. You can always bring it in-house once it is proven."},
    {"q":"Who manages the SDRs?","a":"KSW Solutions, under senior sales leadership, so the team runs on a real playbook with coaching and reporting, not reps left to fend for themselves."}],
  "related":'Run by <a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>. See <a href="/outsourced-sales-and-marketing-department">the full department</a> or <a href="/contact">get in touch</a>.'},

 {"slug":"b2b-lead-generation-services","en_only":True,
  "title":"B2B Lead Generation Services | KSW Solutions",
  "desc":"B2B lead generation that fills pipeline with qualified meetings, run by an outsourced sales and marketing team with senior leadership.",
  "h1":"B2B Lead Generation","eyebrow":"KSW Solutions",
  "lead":"Lead generation is not a list and a blast. It is ICP, message, motion and follow-through. We run the whole thing and fill your pipeline with qualified meetings.",
  "sections":[
    {"h":"Why most lead generation fails","p":["Most lead generation fails because it starts with volume instead of the right ICP and message, and because nobody owns what happens after the click. We start with who actually buys and why, build the message and the motion around it, and run it end to end so leads turn into meetings and pipeline."]},
    {"h":"What we run","ul":["ICP definition and target lists that match how you really win","Outbound sequences, scripts and the channels that fit your buyer","Inbound and content that feeds pipeline, not vanity traffic","Qualification, so your closers only get real meetings","Reporting tied to pipeline and revenue, not opens and clicks"]},
    {"h":"Part of the whole department","p":["Lead generation works best when it is not a silo. Through KSW Solutions it sits inside the full sales and marketing department, so the meetings we book flow straight into a managed pipeline with senior leadership owning the number."]},
  ],
  "faqs":[
    {"q":"What do B2B lead generation services include?","a":"ICP and list building, outbound and inbound motion, message and content, qualification, and reporting tied to pipeline, run for you by an outsourced team."},
    {"q":"How is this different from buying leads?","a":"Bought leads are names. We build qualified meetings: the right ICP, the right message, the motion and the follow-through, owned end to end."},
    {"q":"Can you just do lead generation, or the whole function?","a":"Either. Lead generation can run on its own or as part of the full outsourced sales and marketing department, which is where it performs best."}],
  "related":'Run by <a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>. See <a href="/outsourced-sales-and-marketing-department">the full department</a> or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-cybersecurity","en_only":True,
  "title":"Fractional CRO for Cybersecurity Companies | Tal Paperin",
  "desc":"A fractional CRO for cybersecurity: selling to CISOs through long technical evaluations and channel, owned end to end without a full-time hire.",
  "h1":"Fractional CRO for Cybersecurity","eyebrow":"Industry",
  "lead":"Cybersecurity sells to skeptical, technical buyers through long evaluations and a crowded channel. I build and own the revenue motion that wins those deals, without a full-time CRO salary.",
  "sections":[
    {"h":"Why cybersecurity sales are hard","p":["You are selling to CISOs and security teams who are pitched constantly, run long technical evaluations and proofs of concept, and buy through partners as often as direct. A great product is table stakes; the win goes to the team with a sharp ICP, a credible technical sale and a channel that delivers. Most security startups stall because nobody senior owns that whole motion."]},
    {"h":"What I build","ul":["An ICP and message sharpened for security buyers and their real pain","A sales motion that survives long technical evaluations and POCs","The channel: resellers, MSSPs and integrators that actually sell","Reps who can hold a technical, high-trust conversation","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for technical, high-trust sales","p":["I have sold into technical and skeptical buyers, from scientific software bought by universities, labs and pharma, to industrial IoT into utilities and governments. The discipline that wins those rooms, a credible technical sale built on trust and a channel that delivers, is the same discipline cybersecurity needs."]},
  ],
  "faqs":[
    {"q":"Do you have experience selling to technical buyers?","a":"Yes. I have built and run sales into technical, skeptical buyers, including scientific, industrial and government buyers, where the sale is long, technical and built on trust, the same dynamics as security."},
    {"q":"Can you build our channel and our direct motion?","a":"Both. Cybersecurity usually needs direct sales and a partner channel of resellers, MSSPs and integrators, and I build and run both."},
    {"q":"What does a fractional CRO for cybersecurity cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time CRO."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a>, <a href="/services/go-to-market-strategy">go-to-market</a> and <a href="/services/distributor-channel-recruitment">channel</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-fintech","en_only":True,
  "title":"Fractional CRO for Fintech Companies | Tal Paperin",
  "desc":"A fractional CRO for fintech: long, compliance-heavy B2B cycles into banks and enterprises, owned end to end without a full-time hire.",
  "h1":"Fractional CRO for Fintech","eyebrow":"Industry",
  "lead":"Fintech sells into cautious, regulated buyers through long cycles and heavy diligence. I build and own the revenue motion that closes those deals, without a full-time CRO salary.",
  "sections":[
    {"h":"Why fintech sales are hard","p":["Selling fintech B2B means long cycles, security and compliance reviews, procurement, and risk-averse buyers at banks, insurers and enterprises. Founders often get early traction then stall when deals get bigger and the buying process gets heavier. The fix is a motion built for that reality and someone senior owning the pipeline and the forecast."]},
    {"h":"What I build","ul":["An ICP and message for regulated, risk-averse buyers","A sales motion that survives compliance, security and procurement reviews","Reps who can run a long, multi-stakeholder enterprise sale","Partnerships and channels where they shorten the path","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for long, complex B2B sales","p":["I have run complex, high-value B2B and B2G deals across five continents, the kind with many stakeholders, formal procurement and a long road to signature. That is exactly the shape of a serious fintech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into regulated, enterprise buyers?","a":"Yes. I have run complex, high-value B2B and B2G deals with formal procurement and many stakeholders across five continents, the same shape as enterprise fintech sales."},
    {"q":"Can you handle long, compliance-heavy cycles?","a":"That is the job. I build a motion that survives security, compliance and procurement reviews and keeps multi-stakeholder deals moving to signature."},
    {"q":"What does a fractional CRO for fintech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-defense-tech","en_only":True,
  "title":"Fractional CRO for Defense Tech Companies | Tal Paperin",
  "desc":"A fractional CRO for defense and dual-use tech: government and B2G sales, RFIs and RFQs, long procurement, owned end to end.",
  "h1":"Fractional CRO for Defense Tech","eyebrow":"Industry",
  "lead":"Defense and dual-use tech sells into governments and primes through RFIs, RFQs and long procurement. I run exactly that kind of sale, and I build the revenue motion around it.",
  "sections":[
    {"h":"Why defense and B2G sales are their own sport","p":["Selling to governments and defense primes means formal procurement, RFIs and RFQs, security and compliance gates, and timelines measured in quarters and years. Most commercial sales teams stall the moment an RFI lands. Winning needs someone who has navigated government procurement and can position you to win, not just to submit."]},
    {"h":"What I build and run","ul":["B2G and complex public-sector deals end to end: RFIs, RFQs and tenders","The real decision-makers and the procurement path, mapped","Positioning to win, not just to respond","Partnerships with primes, integrators and local entities where required","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Real B2G and international experience","p":["I run B2G and complex public-sector deals across the globe, including long RFI and RFQ cycles for industrial IoT into utilities and governments, and I have worked on the ground with embassy delegations. Defense and dual-use tech sit squarely in that world."]},
  ],
  "faqs":[
    {"q":"Have you sold to government and public-sector buyers?","a":"Yes. I run B2G and complex public-sector deals internationally, including RFIs, RFQs and tenders, and I know where these long deals stall."},
    {"q":"Can you work with defense primes and integrators?","a":"Yes. Defense and dual-use often sell through primes, integrators and local entities, and building and managing those partnerships is part of the work."},
    {"q":"What does a fractional CRO for defense tech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/b2g-public-sector">B2G and public-sector</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-ai-companies","en_only":True,
  "title":"Fractional CRO for AI Companies | Tal Paperin",
  "desc":"A fractional CRO for AI and deep-tech startups: turning a powerful product into a repeatable B2B sales motion, owned end to end.",
  "h1":"Fractional CRO for AI Companies","eyebrow":"Industry",
  "lead":"AI startups have powerful products and no repeatable way to sell them. I turn the technology into a motion: ICP, pricing, pipeline, team and the number, without a full-time CRO.",
  "sections":[
    {"h":"Why AI companies stall on revenue","p":["AI and deep-tech teams are brilliant at the product and improvise the sales. The result is a few design-partner deals and no repeatable motion, unclear pricing, and buyers who are curious but not sure what they are buying. The fix is a sharp ICP, pricing and a motion built for a technical, skeptical buyer, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and a value proposition a buyer understands, not a demo","Pricing and packaging for an AI product that is still evolving","The outbound and inbound motion, the playbook and the pipeline","Reps who can sell a technical product to skeptical buyers","The forecast and the number, owned end to end"]},
    {"h":"Built selling hard technical products","p":["I came in as Fractional VP of Sales at an AI startup from day one, defined the ICP, built the outbound motion from zero and rebuilt it through pivots, and I have sold scientific and technical software into universities, labs and pharma. AI buyers are skeptical and technical, exactly where a real motion beats a great demo."]},
  ],
  "faqs":[
    {"q":"Can you sell a technical AI product?","a":"Yes. I have built the sales motion for an AI startup from zero and sold scientific and technical software into skeptical, technical buyers. The win comes from a real motion, not just a demo."},
    {"q":"How do you price an AI product that keeps changing?","a":"With packaging and pricing built for where the product is now and able to evolve, tied to the value the buyer actually gets, not to model costs."},
    {"q":"What does a fractional CRO for AI companies cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-digital-health","en_only":True,
  "title":"Fractional CRO for Digital Health Companies | Tal Paperin",
  "desc":"A fractional CRO for digital health and health tech: long clinical and enterprise cycles into providers and payers, owned end to end.",
  "h1":"Fractional CRO for Digital Health","eyebrow":"Industry",
  "lead":"Digital health sells into hospitals, payers and providers through long, evidence-driven cycles. I build and own the revenue motion that closes those deals, without a full-time CRO.",
  "sections":[
    {"h":"Why digital health sales are hard","p":["You sell into health systems, payers and providers with long cycles, committees, procurement, compliance and a demand for evidence. Clinical value is not enough on its own; you need a motion built for cautious, multi-stakeholder buyers and someone senior owning the pipeline and forecast."]},
    {"h":"What I build","ul":["An ICP and message for providers, payers and health systems","A sales motion that handles committees, procurement and compliance","Reps who can run a long, evidence-driven, multi-stakeholder sale","Channels and partnerships where they open doors","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for medical and regulated buyers","p":["I have built and run sales for medical device companies, including the commercialization path for a medical product, and run complex multi-stakeholder B2B and B2G deals. Digital health sits in that same careful, evidence-driven world."]},
  ],
  "faqs":[
    {"q":"Have you sold into healthcare buyers?","a":"Yes. I have worked on medical device commercialization and run complex, multi-stakeholder regulated deals, the same dynamics as digital health."},
    {"q":"Can you handle long clinical and procurement cycles?","a":"Yes. I build a motion that survives committees, procurement and compliance and keeps long deals moving to signature."},
    {"q":"What does a fractional CRO for digital health cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-medical-devices">medical devices</a> guide and the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-climate-tech","en_only":True,
  "title":"Fractional CRO for Climate Tech Companies | Tal Paperin",
  "desc":"A fractional CRO for climate and energy tech: long industrial and utility cycles, projects and channel, owned end to end.",
  "h1":"Fractional CRO for Climate Tech","eyebrow":"Industry",
  "lead":"Climate and energy tech sells into industrials, utilities and governments through long, project-driven cycles. I build and own the revenue motion that wins those deals.",
  "sections":[
    {"h":"Why climate tech sales are hard","p":["You are selling into utilities, industrials and governments, often a hardware, software and services mix, through long cycles, pilots, procurement and project financing. It is a complex, multi-stakeholder sale that most early teams are not built to run. The fix is a motion designed for it and someone senior who owns the number."]},
    {"h":"What I build","ul":["An ICP and message for industrial, utility and government buyers","A motion that handles pilots, procurement and long project cycles","The channel: distributors, integrators and partners that deliver","Direct sales into large industrial and utility accounts","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for industrial and B2G sales","p":["I have built international sales for IoT and hardware companies selling devices, software and services into utilities and governments, run B2G deals across the globe, and recruited the distributor networks that carry industrial products. That is the shape of a climate-tech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into utilities and industrials?","a":"Yes. I have built and run sales of industrial IoT, hardware and services into utilities and governments, including long RFI and RFQ cycles."},
    {"q":"Can you build the channel and the direct motion?","a":"Both. Climate tech usually needs direct sales into large accounts and a partner channel of distributors and integrators, and I build and run both."},
    {"q":"What does a fractional CRO for climate tech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guide and the <a href="/services/market-entry">market entry</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-foodtech","en_only":True,
  "title":"Fractional CRO for Foodtech Companies | Tal Paperin",
  "desc":"A fractional CRO for foodtech: selling into retailers, distributors and manufacturers, channel and direct, across borders, owned end to end.",
  "h1":"Fractional CRO for Foodtech","eyebrow":"Industry",
  "lead":"Foodtech sells into retailers, distributors and manufacturers through a tough channel and across borders. I build and own the revenue motion that gets you onto shelves and into accounts.",
  "sections":[
    {"h":"Why foodtech sales are hard","p":["Whether you sell ingredients, equipment or a platform, you are dealing with retailers, distributors, manufacturers and a crowded, margin-tight channel, often internationally. Getting onto shelves or into accounts takes a real channel strategy and direct selling into large buyers, not just a good product and a trade-show booth."]},
    {"h":"What I build","ul":["A channel of distributors, brokers and retail partners that actually sell","Direct sales into large retailers, manufacturers and chains","Market entry where the opportunity is across borders","An ICP, pricing and message for the trade, not just the end consumer","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built in real consumer and manufacturing channels","p":["I have taken an unknown overseas consumer brand into major North American retail, direct to the big chains and through a distributor network, and put a manufacturer's products onto shelves across a region they had written off. That channel-and-direct discipline is exactly what foodtech needs."]},
  ],
  "faqs":[
    {"q":"Can you get us into retailers and distributors?","a":"Yes. I have sold direct into large retailers and big-box chains and built the distributor and broker networks that get products onto shelves, including across borders."},
    {"q":"Do you handle international foodtech expansion?","a":"Yes. Market entry across five continents, including building the local channel, is one of the things I do."},
    {"q":"What does a fractional CRO for foodtech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/distributor-channel-recruitment">channel</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-agritech","en_only":True,
  "title":"Fractional CRO for Agritech Companies | Tal Paperin",
  "desc":"A fractional CRO for agritech: selling into growers, cooperatives, distributors and agribusiness, channel and direct, across borders.",
  "h1":"Fractional CRO for Agritech","eyebrow":"Industry",
  "lead":"Agritech sells into growers, cooperatives, distributors and agribusiness, often a hardware, software and services mix across borders. I build and own the motion that wins those deals.",
  "sections":[
    {"h":"Why agritech sales are hard","p":["Your buyers are growers, cooperatives, distributors and large agribusinesses, spread across regions and slow to change, and your product is often a mix of hardware, software and services. It is a channel-heavy, international, long-cycle sale that most teams are not built to run. The fix is a real channel strategy plus direct selling, owned by someone senior."]},
    {"h":"What I build","ul":["A channel of distributors and partners that reach growers and agribusiness","Direct sales into large agribusinesses and cooperatives","Market entry where the opportunity is across borders","An ICP, pricing and message for a practical, ROI-driven buyer","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for channel and cross-border sales","p":["I have built distributor networks and run international market entry for IoT, hardware and manufacturing companies, selling devices, software and services through channel and direct across five continents. Agritech sits squarely in that world."]},
  ],
  "faqs":[
    {"q":"Can you build our agritech channel?","a":"Yes. Reaching growers and agribusiness usually runs through distributors and partners, and building and managing that channel is part of the work, alongside direct sales into large accounts."},
    {"q":"Do you handle international expansion for agritech?","a":"Yes. I run market entry across five continents, including building the local channel and team."},
    {"q":"What does a fractional CRO for agritech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/distributor-channel-recruitment">channel</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-robotics","en_only":True,
  "title":"Fractional CRO for Robotics and Automation Companies | Tal Paperin",
  "desc":"A fractional CRO for robotics and automation: complex hardware-plus-software sales into industrial buyers, channel and direct, owned end to end.",
  "h1":"Fractional CRO for Robotics and Automation","eyebrow":"Industry",
  "lead":"Robotics and automation sell a complex hardware, software and services package into industrial buyers through long cycles. I build and own the revenue motion that closes those deals.",
  "sections":[
    {"h":"Why robotics sales are hard","p":["You sell a capital purchase that mixes hardware, software, integration and service, into industrial and manufacturing buyers who run pilots, demand ROI proof and buy slowly, often through integrators. A great machine does not sell itself; it needs a motion built for a long, technical, multi-stakeholder sale."]},
    {"h":"What I build","ul":["An ICP and ROI-driven message for industrial buyers","A motion that handles pilots, integration and long evaluations","The channel: integrators, resellers and partners that deliver","Direct sales into large industrial and manufacturing accounts","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for complex hardware sales","p":["I have built and run international sales for IoT and hardware companies selling devices, software and services, direct and through distributors and integrators, into industrial and government buyers. Robotics and automation sit in that same complex, capital-sale world."]},
  ],
  "faqs":[
    {"q":"Have you sold complex hardware and software together?","a":"Yes. I have run sales of mixed hardware, software and services for IoT and hardware companies, direct and through channel, into industrial buyers."},
    {"q":"Can you build the integrator channel?","a":"Yes. Robotics and automation often sell through integrators and resellers, and recruiting and managing that channel is part of the work."},
    {"q":"What does a fractional CRO for robotics cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guide and the <a href="/services/distributor-channel-recruitment">channel</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-semiconductors","en_only":True,
  "title":"Fractional CRO for Semiconductor Companies | Tal Paperin",
  "desc":"A fractional CRO for semiconductor and chip companies: long design-win cycles, OEMs and distributors, global sales, owned end to end.",
  "h1":"Fractional CRO for Semiconductors","eyebrow":"Industry",
  "lead":"Semiconductors sell through long design-win cycles into OEMs and a global distributor network. I build and own the revenue motion that lands and grows those accounts.",
  "sections":[
    {"h":"Why semiconductor sales are hard","p":["You sell into OEMs and design teams through long design-win cycles, technical evaluations and a global distributor and rep network, where one win can mean years of volume and a loss means years lost. It is one of the most technical, relationship-driven and international sales there is, and it needs senior ownership of the whole motion."]},
    {"h":"What I build","ul":["A motion built around design wins and the engineers who drive them","Management of the global distributor and rep network","Direct relationships with key OEM accounts","An ICP and message for technical, long-horizon buyers","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for technical, global, channel sales","p":["I have built international sales operations across the FSU, EU and APAC, run technical product sales through distributors and direct, and managed the kind of global channel a semiconductor business depends on. The discipline transfers directly."]},
  ],
  "faqs":[
    {"q":"Do you understand design-win sales cycles?","a":"Yes. The long, technical, relationship-driven sale into OEMs and design teams is the same discipline as the complex technical and channel sales I have built and run internationally."},
    {"q":"Can you manage a global distributor and rep network?","a":"Yes. Building and managing international distributor and channel networks across the FSU, EU and APAC is core to what I do."},
    {"q":"What does a fractional CRO for semiconductors cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guide and the <a href="/services/market-entry">market entry</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-logistics","en_only":True,
  "title":"Fractional CRO for Logistics and Supply Chain Companies | Tal Paperin",
  "desc":"A fractional CRO for logistics, supply chain and mobility tech: enterprise and operations buyers, long cycles, channel and direct.",
  "h1":"Fractional CRO for Logistics and Supply Chain","eyebrow":"Industry",
  "lead":"Logistics and supply-chain tech sells into operations-heavy enterprises through long, ROI-driven cycles. I build and own the revenue motion that wins those accounts.",
  "sections":[
    {"h":"Why logistics sales are hard","p":["You sell into operations, procurement and IT at enterprises that run on thin margins and do not change vendors lightly, through long cycles and hard ROI scrutiny, often internationally. Early traction stalls when deals get bigger and the buying committee grows. The fix is a motion built for that buyer and someone senior owning the pipeline and forecast."]},
    {"h":"What I build","ul":["An ICP and ROI-driven message for operations and procurement buyers","A motion that handles long cycles and multi-stakeholder committees","Direct sales into large enterprise and operations accounts","Channels and partnerships where they shorten the path","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for complex, international B2B","p":["I have built and run complex B2B sales into large enterprise and industrial accounts across five continents, including the operations-heavy, ROI-driven buyers that logistics and supply-chain tech sell to."]},
  ],
  "faqs":[
    {"q":"Have you sold into enterprise operations buyers?","a":"Yes. I have run complex B2B sales into large enterprise and industrial accounts internationally, the same operations-heavy, ROI-driven buyers logistics tech sells to."},
    {"q":"Can you handle long, multi-stakeholder cycles?","a":"Yes. I build a motion that keeps long, committee-driven deals moving to signature and a forecast you can trust."},
    {"q":"What does a fractional CRO for logistics cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"us-market-entry-for-israeli-startups","en_only":True,
  "title":"US Market Entry for Israeli Startups | Tal Paperin",
  "desc":"Break into the US market the right way. An operator who has built US and global sales for Israeli and international companies, on the ground.",
  "h1":"US Market Entry for Israeli Startups","eyebrow":"Market Entry",
  "lead":"The US is where Israeli startups win or burn their runway. I help you enter it the right way: pick the beachhead, build the motion and the team, and sell, on US hours, on the ground.",
  "sections":[
    {"h":"Why Israeli startups stumble in the US","p":["Great Israeli tech often stalls in the US because the sale is run from Israel on Israeli assumptions: the wrong ICP, a message that does not land, no US presence, and founders trying to close a market they do not yet understand. The US rewards focus and presence, not a part-time experiment from eight time zones away."]},
    {"h":"What I do","ul":["Pick the right beachhead segment instead of spreading thin","Adapt the ICP, positioning and pricing for the US buyer","Build the motion, hire the first US reps and manage them","Open the first accounts and lead the key deals personally","Stand up the US presence, direct or through partners"]},
    {"h":"Built for this exact move","p":["I am based in Israel and work US hours, and I have built and run sales in the US and across five continents for Israeli and international companies. I know the expensive mistakes before you make them, and I have opened markets others wrote off."]},
  ],
  "faqs":[
    {"q":"Can you help an Israeli startup enter the US market?","a":"Yes. I help pick the beachhead, adapt the ICP, positioning and pricing for the US buyer, build the motion and the first US team, and open the first accounts, working US hours."},
    {"q":"Do I need a US entity and US reps?","a":"Often eventually, but not always on day one. I help you sequence it: prove the motion, then stand up the presence and team, direct or through partners, when it is justified."},
    {"q":"What does this cost?","a":"Fractional engagements run $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time US sales leader."}],
  "related":'Deciding the timing and sequence? See <a href="/when-to-expand-to-the-us">when to expand to the US</a> and <a href="/sell-in-israel-first-or-go-global">sell in Israel first, or go global?</a>. Or see the <a href="/services/market-entry">market entry</a> service and the <a href="/fractional-cro-israel">fractional CRO in Israel</a> guide, or <a href="/contact">get in touch</a>.'},

 {"slug":"outsourced-cro",
  "title":"Outsourced CRO | Tal Paperin",
  "desc":"An outsourced CRO who owns your revenue function from outside your headcount: strategy, team, pipeline and the number, without a full-time hire.",
  "h1":"Outsourced CRO","eyebrow":"Guide",
  "lead":"Outsource the revenue leadership itself. I own your strategy, team, pipeline and number from outside your headcount: the senior operator you need without a full-time hire.",
  "sections":[
    {"h":"Outsourced CRO, fractional CRO, same idea","p":["Outsourced CRO, fractional CRO and part-time CRO all describe the same thing: senior revenue leadership you bring in from outside instead of hiring full-time. You get someone who has run the function before, owning the number, for the part of the week you need and the months you need it."]},
    {"h":"What I own","ul":["Revenue strategy, the forecast and the accountability","The go-to-market motion, the pipeline and the team that runs it","Hiring, training and the hard calls on who stays","Marketing that feeds pipeline, not just activity","The number itself, end to end"]},
    {"h":"Why outsource it","p":["A full-time CRO costs $250,000-plus all in, takes months to find and ramp, and carries real severance risk. Outsourcing the role gives you the same senior ownership in weeks, billed monthly, with no lock-in. When the function is big enough to justify a full-time hire, I help you make it and hand over."]},
  ],
  "faqs":[
    {"q":"What is an outsourced CRO?","a":"A senior revenue leader who owns your sales and revenue function from outside your headcount, part-time and on monthly terms, instead of a full-time CRO hire. The same as a fractional CRO."},
    {"q":"How is it different from a consultant?","a":"A consultant advises. An outsourced CRO owns the work, the pipeline and the number, and answers for the result."},
    {"q":"What does an outsourced CRO cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time CRO."}],
  "related":'See <a href="/how-to-hire-a-fractional-cro">how to hire one</a> and the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-insurtech","en_only":True,
  "title":"Fractional CRO for Insurtech Companies | Tal Paperin",
  "desc":"A fractional CRO for insurtech: selling to carriers, brokers and a regulated, conservative industry through long cycles, owned end to end.",
  "h1":"Fractional CRO for Insurtech","eyebrow":"Industry",
  "lead":"Insurtech sells into carriers, brokers and a cautious, regulated industry through long cycles and partnerships. I build and own the revenue motion that wins those deals.",
  "sections":[
    {"h":"Why insurtech sales are hard","p":["You sell into carriers, MGAs and brokers: conservative, regulated buyers with committees, compliance and procurement, and a strong preference for partners over newcomers. Distribution often runs through the incumbents you are trying to disrupt. It takes a motion built for long, relationship-heavy, regulated sales and someone senior owning the pipeline."]},
    {"h":"What I build","ul":["An ICP and message for carriers, MGAs and brokers","A motion that survives compliance, procurement and committees","Carrier and broker partnerships that become distribution","Reps who can run a long, multi-stakeholder regulated sale","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for regulated, partnership-driven sales","p":["I have run complex, high-value B2B and B2G deals with formal procurement and many stakeholders across five continents, and built channel and partner networks that became real distribution. That is the shape of an insurtech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into regulated, conservative industries?","a":"Yes. I have run complex, multi-stakeholder regulated deals with formal procurement across five continents, the same dynamics as selling to carriers and brokers."},
    {"q":"Can you build carrier and broker partnerships?","a":"Yes. Insurtech distribution often runs through carriers and brokers, and building and managing those partnerships is part of the work."},
    {"q":"What does a fractional CRO for insurtech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/distributor-channel-recruitment">channel</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-proptech","en_only":True,
  "title":"Fractional CRO for Proptech Companies | Tal Paperin",
  "desc":"A fractional CRO for proptech and real-estate tech: selling to owners, operators and brokerages in a slow-moving industry, owned end to end.",
  "h1":"Fractional CRO for Proptech","eyebrow":"Industry",
  "lead":"Proptech sells into owners, operators and brokerages, a relationship-driven, slow-to-change industry. I build and own the revenue motion that gets you adopted at scale.",
  "sections":[
    {"h":"Why proptech sales are hard","p":["Real estate owners, operators and brokerages are relationship-driven, fragmented and slow to adopt new tools, and a pilot in one building rarely rolls out on its own. You need a motion that lands the first accounts, proves ROI on the ground, and turns pilots into portfolio-wide deals, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and ROI-driven message for owners, operators and brokerages","A motion that turns single-site pilots into portfolio rollouts","Direct sales into large owners and operators","Partnerships and channels that reach a fragmented market","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for relationship-driven, on-the-ground sales","p":["I have opened markets on the ground across five continents, sold direct into large accounts and built the channel to reach fragmented buyers. Proptech rewards exactly that mix of direct selling and a real channel."]},
  ],
  "faqs":[
    {"q":"Can you turn proptech pilots into bigger deals?","a":"Yes. The job is building a motion that proves ROI in the first sites and expands pilots into portfolio-wide rollouts, not leaving them stuck as one-offs."},
    {"q":"Do you sell direct or through channel?","a":"Both. Proptech usually needs direct sales into large owners and operators plus partnerships to reach a fragmented market."},
    {"q":"What does a fractional CRO for proptech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-legaltech","en_only":True,
  "title":"Fractional CRO for Legaltech Companies | Tal Paperin",
  "desc":"A fractional CRO for legaltech: selling to law firms and general counsel, conservative buyers and procurement, owned end to end.",
  "h1":"Fractional CRO for Legaltech","eyebrow":"Industry",
  "lead":"Legaltech sells into law firms and general counsel, conservative buyers who move slowly and buy by committee. I build and own the revenue motion that wins those accounts.",
  "sections":[
    {"h":"Why legaltech sales are hard","p":["Law firms and in-house legal teams are risk-averse, consensus-driven and slow to change tools, with partners, committees and procurement all in the path. Adoption stalls without a clear ROI case and a motion built for cautious, multi-stakeholder buyers, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and message for law firms and general counsel","A motion that handles committees, partners and procurement","A clear ROI and risk case the buyer can defend internally","Reps who can run a long, consensus-driven sale","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for conservative, multi-stakeholder buyers","p":["I have run complex, high-value B2B deals with many stakeholders and formal procurement across five continents. The careful, consensus-driven legal buyer is exactly that kind of sale."]},
  ],
  "faqs":[
    {"q":"Have you sold to conservative, committee-driven buyers?","a":"Yes. Complex, multi-stakeholder deals with procurement and a long road to consensus are the deals I have run for years, the same shape as selling to law firms."},
    {"q":"How do you speed up a slow legal sale?","a":"With a clear ROI and risk case the buyer can defend internally, and a motion that keeps every stakeholder moving instead of letting the deal stall."},
    {"q":"What does a fractional CRO for legaltech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-hr-tech","en_only":True,
  "title":"Fractional CRO for HR Tech Companies | Tal Paperin",
  "desc":"A fractional CRO for HR tech: selling to People and HR leaders in a crowded market, mid-market and enterprise, owned end to end.",
  "h1":"Fractional CRO for HR Tech","eyebrow":"Industry",
  "lead":"HR tech is a crowded market selling into People and HR leaders with real budget scrutiny. I build and own the motion that cuts through and closes, mid-market and enterprise.",
  "sections":[
    {"h":"Why HR tech sales are hard","p":["You sell into People, HR and finance leaders in one of the most crowded software categories there is, where every competitor sounds the same and budgets get hard scrutiny. Winning takes a sharp ICP and differentiation, a motion built for mid-market and enterprise procurement, and someone senior owning the pipeline."]},
    {"h":"What I build","ul":["An ICP and differentiated message in a crowded category","A motion built for mid-market and enterprise buying","Reps who can sell value, not feature parity","Partnerships and channels where they shorten the path","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for crowded, competitive B2B","p":["I have built go-to-market from zero in competitive categories, sharpened positioning so reps sell value instead of features, and run the mid-market and enterprise motion. That is what HR tech needs to stand out."]},
  ],
  "faqs":[
    {"q":"How do you stand out in a crowded category?","a":"With a sharp ICP, real differentiation and a motion that sells value and outcomes, not feature parity, so you stop competing on the same checklist as everyone else."},
    {"q":"Mid-market or enterprise?","a":"Both. I build the motion and the team for the segment that fits your product and pricing, and the procurement that comes with it."},
    {"q":"What does a fractional CRO for HR tech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-edtech","en_only":True,
  "title":"Fractional CRO for Edtech Companies | Tal Paperin",
  "desc":"A fractional CRO for edtech: selling to schools, universities and districts through budget cycles and procurement, owned end to end.",
  "h1":"Fractional CRO for Edtech","eyebrow":"Industry",
  "lead":"Edtech sells into schools, universities and districts through budget cycles, committees and procurement that look a lot like government buying. I build and own the motion that wins.",
  "sections":[
    {"h":"Why edtech sales are hard","p":["Selling to schools, universities and districts means fixed budget cycles, committees, procurement and pilots, and buyers who are cautious and accountable to many stakeholders. It is close to a public-sector sale, and most commercial teams stall in it. The fix is a motion built for that reality and senior ownership of the pipeline."]},
    {"h":"What I build","ul":["An ICP and message for schools, universities and districts","A motion timed to budget cycles, pilots and procurement","Reps who can run a long, multi-stakeholder institutional sale","Partnerships and channels that open institutional doors","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for institutional and public-sector sales","p":["I have sold scientific software into universities and research labs, and run B2G and complex public-sector deals with formal procurement across the globe. Edtech buying sits squarely in that institutional world."]},
  ],
  "faqs":[
    {"q":"Have you sold into universities and institutions?","a":"Yes. I have sold scientific software into universities and research labs and run B2G and public-sector deals with formal procurement, the same dynamics as edtech."},
    {"q":"Can you work within budget cycles and procurement?","a":"Yes. I time the motion to budget cycles and pilots and build a sale that survives committees and procurement."},
    {"q":"What does a fractional CRO for edtech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/b2g-public-sector">B2G and public-sector</a> and <a href="/services/fractional-cro">fractional CRO</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-developer-tools","en_only":True,
  "title":"Fractional CRO for Developer Tools Companies | Tal Paperin",
  "desc":"A fractional CRO for developer tools and infrastructure: bottoms-up adoption plus enterprise expansion, technical buyers, owned end to end.",
  "h1":"Fractional CRO for Developer Tools","eyebrow":"Industry",
  "lead":"Developer tools win bottoms-up with engineers, then have to turn usage into enterprise revenue. I build and own the motion that converts adoption into contracts.",
  "sections":[
    {"h":"Why developer-tools sales are hard","p":["Engineers adopt your tool, but adoption is not revenue. The hard part is converting bottoms-up usage into enterprise contracts: finding the budget owner, building the business case, and running the security and procurement gauntlet, without alienating the developers who got you in. Most teams have the usage and no motion to monetize it."]},
    {"h":"What I build","ul":["A motion that turns bottoms-up adoption into enterprise deals","The enterprise sale on top of self-serve: budget owner, business case, procurement","Reps who can sell to technical buyers without losing trust","Pricing and packaging across free, team and enterprise","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built selling to technical buyers","p":["I have built sales motions for technical, skeptical buyers, from AI startups to scientific software bought by universities, labs and pharma. Selling on top of a developer base, without breaking the trust that got you there, is exactly that discipline."]},
  ],
  "faqs":[
    {"q":"Can you monetize a bottoms-up developer base?","a":"Yes. The job is building the enterprise motion on top of adoption: finding the budget owner, making the business case and running procurement, while keeping the developers who got you in."},
    {"q":"Do you understand technical buyers?","a":"Yes. I have built and run sales into technical, skeptical buyers for years, where trust and a credible technical sale win the deal."},
    {"q":"What does a fractional CRO for developer tools cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-saas">SaaS</a> and <a href="/fractional-cro-for-ai-companies">AI</a> guides and the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-biotech","en_only":True,
  "title":"Fractional CRO for Biotech and Life Sciences | Tal Paperin",
  "desc":"A fractional CRO for biotech, life sciences and lab tech: scientific buyers, pharma, research labs and long technical cycles, owned end to end.",
  "h1":"Fractional CRO for Biotech and Life Sciences","eyebrow":"Industry",
  "lead":"Biotech and life-sciences tools sell into scientists, labs and pharma through long, evidence-driven, technical cycles. I have sold into exactly those buyers, and I build the motion for them.",
  "sections":[
    {"h":"Why life-sciences sales are hard","p":["Your buyers are scientists, lab directors, research institutions and pharma: rigorous, evidence-driven and slow, with procurement, grants and committees in the path. The sale is long, technical and built on credibility, and a generic SaaS motion does not move it."]},
    {"h":"What I build","ul":["An ICP and message for scientific, research and pharma buyers","A motion built for long, evidence-driven, technical evaluations","Reps who can hold a credible scientific and technical conversation","Partnerships and distribution into labs and institutions","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Done in real scientific sales","p":["I sold scientific SaaS into universities, research labs and pharma, writing the scripts and the playbook the reps ran. Selling to the scientific buyer, where the sale is long, technical and built entirely on trust, is something I have actually done."]},
  ],
  "faqs":[
    {"q":"Have you sold to scientific and pharma buyers?","a":"Yes. I sold scientific software into universities, research labs and pharma and built the playbook the reps ran. That credibility-driven, technical sale is exactly this market."},
    {"q":"Can you handle long, evidence-driven cycles?","a":"Yes. I build a motion that survives technical evaluation, grants and procurement and keeps long deals moving."},
    {"q":"What does a fractional CRO for biotech cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-medical-devices">medical devices</a> and <a href="/fractional-cro-for-digital-health">digital health</a> guides, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-telecom","en_only":True,
  "title":"Fractional CRO for Telecom Companies | Tal Paperin",
  "desc":"A fractional CRO for telecom and connectivity: selling to carriers and operators through RFPs, long procurement and channel, owned end to end.",
  "h1":"Fractional CRO for Telecom","eyebrow":"Industry",
  "lead":"Telecom sells into carriers and operators through RFPs, long procurement and a global channel. I build and own the revenue motion that wins those deals.",
  "sections":[
    {"h":"Why telecom sales are hard","p":["Carriers and operators are large, bureaucratic and slow, buying through RFPs, long procurement and entrenched vendor relationships, often across borders. It is one of the hardest enterprise sales there is, and it needs someone who has run formal, multi-stakeholder, international deals owning the pipeline."]},
    {"h":"What I build","ul":["An ICP and message for carriers, operators and large enterprises","A motion built for RFPs, procurement and long cycles","The channel: integrators, resellers and partners that carry telecom","Direct relationships with key carrier and operator accounts","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for formal, international, channel sales","p":["I have run B2G and complex public-sector deals with RFIs and RFQs, built international distributor and channel networks, and managed long, formal procurement across five continents. Telecom sits squarely in that world."]},
  ],
  "faqs":[
    {"q":"Can you run RFP and procurement-driven deals?","a":"Yes. Formal RFIs, RFQs, RFPs and long procurement with many stakeholders are deals I have run internationally for years."},
    {"q":"Can you build the telecom channel?","a":"Yes. Telecom often sells through integrators and partners, and building and managing international channel networks is core to what I do."},
    {"q":"What does a fractional CRO for telecom cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/b2g-public-sector">B2G</a>, <a href="/services/distributor-channel-recruitment">channel</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-energy","en_only":True,
  "title":"Fractional CRO for Energy Companies | Tal Paperin",
  "desc":"A fractional CRO for energy, utilities and industrial tech: long project cycles, B2G and channel, owned end to end without a full-time hire.",
  "h1":"Fractional CRO for Energy","eyebrow":"Industry",
  "lead":"Energy and utility tech sells into industrials, utilities and governments through long, project-driven cycles. I have sold into exactly these buyers, and I build the motion for them.",
  "sections":[
    {"h":"Why energy sales are hard","p":["You sell into utilities, energy companies, industrials and governments: capital buyers with long cycles, pilots, procurement, regulation and project financing. A great technology is not enough; you need a motion built for complex, multi-stakeholder, often public-sector buying, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and message for utility, industrial and government buyers","A motion that handles pilots, procurement and long project cycles","B2G and public-sector deals where the buyer is a government or utility","The channel and partnerships that carry industrial products","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for industrial and B2G sales","p":["I built and ran international sales for IoT and hardware companies selling devices, software and services into utilities and governments, including long RFI and RFQ cycles, and recruited the distributor networks that carry industrial products. That is the shape of an energy-tech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into utilities and government?","a":"Yes. I have built and run sales of industrial IoT, hardware and services into utilities and governments, including long RFI and RFQ cycles."},
    {"q":"Can you handle long, project-driven cycles?","a":"Yes. I build a motion that survives pilots, procurement and project timelines and keeps capital deals moving to signature."},
    {"q":"What does a fractional CRO for energy cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-climate-tech">climate tech</a> and <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guides, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-professional-services","en_only":True,
  "title":"Fractional CRO for Professional Services Firms | Tal Paperin",
  "desc":"A fractional CRO for agencies, consultancies and professional-services firms: building real business development beyond founder-led referrals.",
  "h1":"Fractional CRO for Professional Services","eyebrow":"Industry",
  "lead":"Agencies and consultancies live on referrals and the founder's network, then plateau. I build the business-development engine that grows revenue beyond who you already know.",
  "sections":[
    {"h":"Why professional-services firms plateau","p":["Agencies, consultancies and services firms grow on referrals and the founders' relationships, then hit a ceiling when those run out. Most have never built real business development: a defined ICP, an outbound motion, a pipeline and someone who owns the number instead of waiting for the phone to ring."]},
    {"h":"What I build","ul":["A defined ICP and positioning beyond word of mouth","A real business-development motion and pipeline","The first business-development hires, trained and managed","The founders out of every pitch and into the right ones","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for relationship and services selling","p":["I have built go-to-market from zero and run the kind of relationship-driven, trust-based selling that services firms depend on, across five continents. The same discipline turns a referral business into one with a real pipeline."]},
  ],
  "faqs":[
    {"q":"Can you grow a referral-based services firm?","a":"Yes. The job is building real business development on top of referrals: an ICP, an outbound motion, a pipeline and someone owning the number, so growth does not depend on who you already know."},
    {"q":"Will the founders still need to sell?","a":"Less, and on the right deals. I build the motion and the team so the founders are not the only ones who can win business."},
    {"q":"What does a fractional CRO for professional services cost?","a":"Typically $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-the-us-market","en_only":True,
  "title":"Fractional CRO for the US Market | Tal Paperin",
  "desc":"A fractional CRO to take a foreign or global company into the US market: pick the beachhead, build the motion and the team, and sell, on US hours.",
  "h1":"Fractional CRO for the US Market","eyebrow":"Market Entry",
  "lead":"The US is the prize and the place most foreign companies burn cash. I help you enter it the right way: pick the beachhead, build the motion and the team, and open the first accounts, on US hours.",
  "sections":[
    {"h":"Why foreign companies stall in the US","p":["Companies from Europe, Israel, APAC and beyond bring a product that works at home and run the US sale on home assumptions: the wrong ICP, a message that does not land, no US presence and leadership eight time zones away. The US rewards focus and presence, and punishes a part-time experiment run from abroad."]},
    {"h":"What I do","ul":["Pick the right beachhead segment instead of spreading thin","Adapt the ICP, positioning and pricing for the US buyer","Build the motion, hire the first US reps and manage them","Open the first accounts and lead the key deals personally","Stand up the US presence, direct or through partners"]},
    {"h":"Built for cross-border entry into the US","p":["I am based in Israel and work US hours, and I have built and run sales in the US and across five continents and 40-plus countries for foreign and global companies. I know the expensive mistakes before you make them, and I have opened markets others wrote off."]},
  ],
  "faqs":[
    {"q":"Can you take a foreign company into the US market?","a":"Yes. I help pick the beachhead, adapt the ICP, positioning and pricing for the US buyer, build the motion and the first US team, and open the first accounts, working US hours."},
    {"q":"Do I need a US entity and US team on day one?","a":"Not always. I help you sequence it: prove the motion first, then stand up the presence and team, direct or through partners, when it is justified."},
    {"q":"What does this cost?","a":"Fractional engagements run $2,000 to $12,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time US sales leader."}],
  "related":'See the <a href="/services/market-entry">market entry</a> service and the <a href="/us-market-entry-for-israeli-startups">US entry for Israeli startups</a> guide, or <a href="/contact">get in touch</a>.'},

 {"slug":"tal-paperin-podcasts-and-press",
  "title":"Tal Paperin: Podcasts, Interviews and Panels",
  "desc":"Tal Paperin on go-to-market, B2B sales and revenue: selected podcasts, interviews and conference panels, in his own words.",
  "h1":"Tal Paperin: Podcasts, Interviews and Panels","eyebrow":"Featured",
  "lead":"Where I have talked go-to-market, sales and revenue in public. Podcasts, interviews and panels, aimed at founders and CEOs.",
  "sections":[
    {"h":"What I talk about","p":["The same things I do for clients: why founder-led sales stalls, how to build a go-to-market motion that scales, what actually changed in SaaS selling, and how to turn a raise into revenue. Direct, opinionated, aimed at founders and revenue leaders."]},
    {"h":"Selected appearances","p":["A sample of recent shows and panels is below. For a podcast, panel or talk, get in touch and I will make the time."]},
  ],
  "faqs":[
    {"q":"Is Tal Paperin available for podcasts and panels?","a":"Yes. I regularly join podcasts, interviews and conference panels on go-to-market, B2B sales, revenue and scaling founder-led sales. Get in touch with the details and I will make the time."},
    {"q":"What does Tal Paperin speak about?","a":"Go-to-market strategy, building and scaling B2B sales teams, why founder-led sales stalls, what changed in SaaS selling, and turning funding into revenue. Practical and direct, for founders and revenue leaders."}],
  "related":'<p>Selected appearances:</p><ul><li><a href="https://podcasts.apple.com/us/podcast/tal-paperin-ai-didnt-kill-saas-it-killed-lazy-sales-motion/id1812655142?i=1000750906146" target="_blank" rel="noopener">The Sales Strategist Podcast: "AI didn\'t kill SaaS, it killed lazy sales motion"</a> (<a href="https://open.spotify.com/episode/4GXV4h6wxRCVWXoyDzwynA" target="_blank" rel="noopener">Spotify</a>)</li><li><a href="https://marcuscauchi.podbean.com/e/success-comes-through-people-who-plan-execute-and-adapt-not-those-who-talk-about-it/" target="_blank" rel="noopener">TheInquisitor with Marcus Cauchi: "Success Comes To People Who Plan, Execute and Adapt"</a></li><li><a href="https://goodpods.com/podcasts/ask-win-114648/tal-paperin-part-2-5875148" target="_blank" rel="noopener">Ask Win: Tal Paperin (Part 2)</a></li><li><a href="https://davosinthedesert.us/israeli-technology-conference-speaker-podcasts/" target="_blank" rel="noopener">Davos in the Desert: Israeli Technology Conference panel</a></li></ul><p>More interviews and features:</p><ul><li>Solution Nation Podcast: "Investing in Israeli IIoT Companies" (2022)</li><li>The Business Blast Podcast with Tyler Wagner (2018)</li><li>The Daily Sales with Daniel Disney, on social selling (2018)</li><li>CEO Money with Michael Yorba (2018)</li><li>The Hard Corps Marketing Show: "Global Sales Fundamentals" (2018)</li><li>The Bob Low Show: "How to Penetrate New Markets" (2018)</li></ul><p>Also: "An Introduction to Sales in the 21st Century", Tal Paperin\'s eBook on B2B sales.</p><p><a href="/contact">Want me on your show or panel? Get in touch.</a></p>'},

 {"slug":"b2b-go-to-market-strategy",
  "title":"B2B Go-To-Market Strategy: The Operator's Guide | Tal Paperin",
  "desc":"A go-to-market strategy you can run, not file away. The five parts of a real B2B GTM, the order to build them, and the mistakes that burn the budget.",
  "h1":"B2B Go-To-Market Strategy, Built by Someone Who Runs It","eyebrow":"Guide",
  "lead":"Most go-to-market strategy is a deck that gets opened once and never again. A real one is an engine you run every week. Here are the five parts, the order they go in, and how to keep it alive until it produces pipeline. This is the same sequence I use in the first 90 days with a client.",
  "sections":[
    {"h":"A GTM strategy is a plan for turning a product into paying customers","p":[
      "Strip away the jargon and go-to-market is four questions with real answers: who you sell to, what you say to them, through which channel, and by what process. Add the number you expect it to produce and you have a strategy. Leave any one of them vague and every salesperson improvises, every marketing dollar points a different direction, and you cannot tell a channel problem from a message problem.",
      "I have opened the US, the EU, Eastern Europe and APAC for B2B companies, direct and through channel. The ones that scaled had answers to those questions written down and tested. The ones that burned a year had a product and a hope."]},
    {"h":"The five parts, in the order they matter","tiers":[
      "Ideal customer profile. Not \"B2B companies\" but a sharp profile: company size, industry, the buyer's role, and the specific pain they feel. Every part after this gets easier the sharper this is, and harder if you skip it.",
      "Positioning and message. The reason this buyer needs you, in their words, tied to a business outcome they already care about. Same product, a different message for each persona. This is where most GTM quietly fails.",
      "Motion and channel. How you actually reach them: outbound, inbound, product-led, partners, events. The mix depends on your price point, your buyer and your stage, not on what is trending.",
      "Sales process. The path from first touch to signature: the stages, who is involved, how long each takes, and what moves a deal forward. No defined process means no forecast and no way to improve.",
      "Forecast. A number with milestones and the math behind it, not a hope. If you cannot show the pipeline that produces the number, you do not have a forecast, you have a wish."]},
    {"h":"Build them in sequence, not all at once","p":[
      "The order is not decoration. A great message aimed at the wrong customer still misses. A perfect channel carrying a weak message still burns money. Nail the ICP, then write the message for that ICP, then pick the motion that reaches them, then build the process, then forecast what the process produces.",
      "Teams get this backwards constantly. They buy an outbound tool and hire an SDR before anyone has defined who to call or what to say. The tool works fine. The strategy underneath it does not exist."]},
    {"h":"Start from one closed deal, not a blank page","p":[
      "You do not invent a GTM in a conference room. You extract it from a real deal. Take the last customer you closed, or the one closest to closing, and dig: why they bought, what hurt before they did, what convinced them, and what the path actually looked like. One honest deal gives you the first draft of all five parts. Then you test whether it repeats. That is how you build an engine from fact instead of assumption."]},
    {"h":"The mistakes that burn the budget","ul":[
      "Selling before the ICP is defined, so you learn the wrong lessons from the wrong buyers",
      "A message that describes the product instead of the buyer's outcome",
      "Copying another company's motion when your price point and buyer are different",
      "Treating the GTM as a document to finish rather than an engine to run and correct",
      "Forecasting off gut feel because no sales process was ever defined"]},
    {"h":"Go deeper on each part","links":[
      ["B2B positioning and messaging", "/b2b-positioning-and-messaging"],
      ["How to choose your go-to-market motion", "/go-to-market-motion"],
      ["Go-to-market strategy service", "/services/go-to-market-strategy"]]},
    {"h":"Strategy that stays on the slide is worthless","p":[
      "The deck is the easy part. Running it is the job. I build the GTM with you, then lead the execution until you have pipeline, partners and first sales, correcting the plan against what the market actually does. If you are selling without a clear GTM, or with one that is not working, that is the work I do."]},
  ],
  "faqs":[
    {"q":"What is a B2B go-to-market strategy?","a":"It is the concrete plan for turning your product into paying customers: who you sell to, what you say, through which channel, by what process, and the number you expect it to produce. Written down and tested, not assumed."},
    {"q":"What are the parts of a GTM strategy?","a":"Five: a sharp ideal customer profile, positioning and message, the sales motion and channel, a defined sales process, and a forecast with the math behind it. Build them in that order, because each one depends on the one before it."},
    {"q":"Where do I start building a GTM?","a":"From one real deal, not a blank page. Take the last customer you closed and work out why they bought, what hurt, what convinced them and how the deal actually moved. That gives you the first draft of all five parts, which you then test for whether it repeats."},
    {"q":"Do I need a GTM strategy if I am already selling?","a":"If selling is inconsistent, slow or unforecastable, you are selling without a working GTM even if deals occasionally close. A defined strategy is what lets you tell a channel problem from a message problem and fix the right one."},
    {"q":"Can you build the GTM and help run it?","a":"Yes. I build the strategy with you and then lead the execution until there is pipeline, partners and first sales. I do not stop at the slide deck, because the deck is the part that does not sell."}],
  "related":'See the <a href="/services/go-to-market-strategy">go-to-market strategy service</a>, go deeper on <a href="/b2b-positioning-and-messaging">positioning and messaging</a> and <a href="/go-to-market-motion">choosing your GTM motion</a>, or read <a href="/blog/go-to-market-israeli-startup">a GTM strategy for a startup selling abroad</a> and <a href="/blog/ideal-customer-profile-icp">how to define an ICP that converts</a>. If the forecast part keeps missing, see <a href="/sales-forecast-always-wrong">why your sales forecast is always wrong</a>.'},

 {"slug":"b2b-positioning-and-messaging",
  "title":"B2B Positioning and Messaging That Wins Deals | Tal Paperin",
  "desc":"Positioning is why a buyer picks you over the status quo. How to build B2B positioning and a message that sells the outcome, not the feature list.",
  "h1":"B2B Positioning and Messaging That Makes Buyers Pick You","eyebrow":"Guide",
  "lead":"Most B2B messaging describes the product. Buyers do not care about your product. They care about the problem it ends and the outcome they get. Here is how to position a B2B product so the right buyer sees themselves in it and picks you over doing nothing.",
  "sections":[
    {"h":"Positioning is the frame, messaging is the words","p":[
      "Positioning is the decision about what category you are in, who you are for, and why you beat the alternative, including the alternative of changing nothing. Messaging is how you say that in language the buyer already uses. Get the positioning wrong and no amount of clever copy saves you. Get it right and the words almost write themselves.",
      "Your real competitor is rarely the other vendor. It is the status quo: the spreadsheet, the intern, the process they already tolerate. Position against that and the conversation changes."]},
    {"h":"Sell the outcome, not the feature","p":[
      "A feature is what your product does. An outcome is what the buyer gets: time back, risk removed, revenue added, a number they are measured on going the right way. Buyers approve budget for outcomes, not for features. The same feature list, reframed as the outcome a specific buyer cares about, is the difference between a demo that lands and one that gets a polite no.",
      "This is why positioning starts from the buyer, not the roadmap. If you cannot name the outcome in the buyer's own words, you have a feature list, not a message."]},
    {"h":"One product, a different message per persona","p":[
      "The CFO, the end user and the head of the department buy the same product for different reasons. The CFO wants the cost and the risk gone. The user wants their day to get easier. The department head wants the number they report on to move. Same product, three messages. Writing one message for everyone means writing one that fully convinces no one."]},
    {"h":"How to build it","ul":[
      "Start from your sharpest ICP, because you position for a specific buyer, not for everyone",
      "Name the status quo they live with today and why it quietly costs them",
      "State the outcome they get in their language, with a concrete before and after",
      "Pick the one claim you can prove and lead with it, instead of ten you can only assert",
      "Pressure-test every line against a real buyer, then cut whatever they skim past"]},
    {"h":"How to tell it is working","p":[
      "Good positioning shows up in the sales cycle, not in a brand survey. Deals move faster because less time goes on explaining what you are. Discovery calls start with the buyer describing their own pain back to you. Discounting drops, because you are no longer compared feature to feature with a cheaper tool. If none of that is happening, the positioning is the thing to fix before you spend another dollar on outreach."]},
    {"h":"Where this fits","links":[
      ["The full go-to-market strategy", "/b2b-go-to-market-strategy"],
      ["How to choose your go-to-market motion", "/go-to-market-motion"],
      ["Go-to-market strategy service", "/services/go-to-market-strategy"]]},
  ],
  "faqs":[
    {"q":"What is the difference between positioning and messaging?","a":"Positioning is the strategic decision about what category you are in, who you are for, and why you beat the alternative including doing nothing. Messaging is how you express that in the buyer's own words. Positioning comes first, because the words only work once the frame is right."},
    {"q":"Why is my B2B messaging not converting?","a":"Usually because it describes the product instead of the buyer's outcome, or because it is written for everyone and so convinces no one. Buyers approve budget for outcomes they are measured on, not for feature lists. Reframe each message around the specific outcome a specific persona cares about."},
    {"q":"Who is my real competitor?","a":"Most of the time it is the status quo, not another vendor: the spreadsheet, the manual process, the thing they already tolerate. Position against doing nothing and you address the decision the buyer is actually making."},
    {"q":"Should the message change by buyer?","a":"Yes. The CFO, the user and the department head buy the same product for different reasons, so each needs a message aimed at what they care about. One message for everyone is a message that fully persuades no one."}],
  "related":'Part of the <a href="/b2b-go-to-market-strategy">go-to-market strategy</a> cluster. See also <a href="/go-to-market-motion">choosing your GTM motion</a>, the <a href="/services/go-to-market-strategy">GTM service</a>, or read <a href="/blog/ideal-customer-profile-icp">how to define an ICP that converts</a>.'},

 {"slug":"go-to-market-motion",
  "title":"How to Choose Your Go-To-Market Motion | Tal Paperin",
  "desc":"Outbound, inbound, product-led or channel? How to choose the right B2B go-to-market motion by price point, buyer and stage, not by hype.",
  "h1":"How to Choose Your Go-To-Market Motion","eyebrow":"Guide",
  "lead":"Every quarter someone on LinkedIn declares a motion dead. Outbound is dead, inbound is dead, PLG killed sales, sales killed PLG. Ignore all of it. A go-to-market motion is a choice you make from your price point, your buyer and your stage, not a belief system. Here is how to pick the one that fits.",
  "sections":[
    {"h":"The motions, and who each one fits","tiers":[
      "Outbound. You go to the buyer: targeted outreach, SDRs, direct selling. Fits higher price points, defined buyers, and any early stage where you need control, speed and market knowledge now.",
      "Inbound. The buyer comes to you: content, SEO, reputation, word of mouth. Compounds beautifully and takes six to eighteen months to produce predictable pipeline, so it is an asset you build, not a switch you flip.",
      "Product-led. The product sells itself through a free tier or trial. Fits low price points, self-serve products and a user who can adopt without a committee. Breaks down the moment the deal needs sign-off.",
      "Channel and partners. Someone else's salesforce or distributor sells for you. Fits markets where trust is local, the buyer is hard to reach directly, or you cannot afford feet on the ground yet."]},
    {"h":"Choose by three things, not by trend","ul":[
      "Price point: low and self-serve leans product-led, high and committee-bought needs sales-led",
      "Buyer: easy to find and reach favors outbound, a broad self-serve user favors product-led",
      "Stage: early almost always needs outbound first, because you need control and learning now"]},
    {"h":"Why early-stage B2B almost always starts outbound","p":[
      "Founders want inbound: leads that arrive already interested. Who would not. The problem is that inbound is an asset you build over many months, and at the earliest stage you do not have the runway and you do not yet know enough to feed the machine. Outbound buys you control, speed and direct market knowledge now. You learn who actually buys and why by talking to them, and that learning is what lets you build inbound well later. Start outbound, earn the right to inbound.",
      "I built my own company by visiting a customer, not by posting and waiting. The principle holds for most B2B: go to the market before you expect it to come to you."]},
    {"h":"Most companies end up with a hybrid","p":[
      "The honest answer is rarely one motion. A typical B2B scales outbound for control early, layers in inbound as content and reputation compound, and adds channel where a market is hard to reach directly. Product-led sits underneath only if the product genuinely sells without a human. The mistake is picking a motion by ideology and forcing the business to fit it, instead of letting the buyer and the price point decide."]},
    {"h":"Where this fits","links":[
      ["The full go-to-market strategy", "/b2b-go-to-market-strategy"],
      ["B2B positioning and messaging", "/b2b-positioning-and-messaging"],
      ["Go-to-market strategy service", "/services/go-to-market-strategy"]]},
  ],
  "faqs":[
    {"q":"How do I choose a go-to-market motion?","a":"By three things: your price point, your buyer and your stage. Low price and self-serve leans product-led, high price and committee buying needs sales-led, an easy-to-reach buyer favors outbound, and a hard-to-reach local market favors channel. Pick from the business, not from whatever motion is trending."},
    {"q":"Should an early-stage startup do outbound or inbound?","a":"Outbound first, almost always. Inbound compounds but takes six to eighteen months, and early on you lack both the runway and the market knowledge to feed it. Outbound buys control, speed and direct learning about who actually buys, which is what lets you build inbound well later."},
    {"q":"When does product-led growth work?","a":"When the product genuinely sells itself: low price point, self-serve adoption, and a single user who does not need committee sign-off. The moment a deal requires approval from finance or a department head, you need a sales motion alongside it."},
    {"q":"Can I run more than one motion?","a":"Most B2B companies do, and should. A common path is outbound for control early, inbound layered in as it compounds, and channel added where a market is hard to reach directly. The error is forcing one motion by ideology instead of matching motions to the buyer and price point."}],
  "related":'Part of the <a href="/b2b-go-to-market-strategy">go-to-market strategy</a> cluster. See also <a href="/b2b-positioning-and-messaging">positioning and messaging</a>, the <a href="/services/go-to-market-strategy">GTM service</a>, or read <a href="/blog/outbound-vs-inbound-early-stage">outbound vs inbound for early-stage B2B</a> and <a href="/blog/product-led-vs-sales-led">product-led vs sales-led growth</a>. If you hired reps but have no pipeline, the missing piece is usually the motion itself: see <a href="/hired-reps-but-no-pipeline">hired reps but no pipeline</a>.'},

 {"slug":"sell-in-israel-first-or-go-global",
  "title":"Sell in Israel First, or Go Global? | Tal Paperin",
  "desc":"Should an Israeli B2B startup sell at home first or go straight abroad? The honest answer, when local-first helps, and when it quietly burns a year.",
  "h1":"Sell in Israel First, or Go Straight Abroad?","eyebrow":"Market Entry",
  "lead":"Most Israeli B2B founders frame it as a binary: Israel or abroad. Wrong frame. What matters is what the local market can actually teach you, and what it quietly hides until the day you try to sell in New York. Here is how I decide it with clients, and when selling at home first is a trap.",
  "sections":[
    {"h":"The Israeli market is too small to be your target, and that is the point","p":[
      "Israel has under ten million people and a small pool of buyers for any given B2B product. No serious Israeli company has ever been built on the domestic market alone, and most of my work for 20-plus years has been taking Israeli companies into the US, the EU, Eastern Europe and APAC. So when a founder says they will nail Israel first and expand later, I push back. Expand to what? The target was always abroad.",
      "That does not make the local market useless. It makes it a rehearsal room, not a stage. The trap is mistaking the rehearsal for the show."]},
    {"h":"What selling in Israel first is genuinely good for","ul":[
      "Testing the pitch cheaply, in person, with buyers you reach by driving across Tel Aviv instead of flying eight time zones",
      "Getting your first reference logos and case studies, even small ones, so a US buyer is not your first ever customer",
      "Learning the mechanics of your own sale: the objections, the stakeholders, how long a cycle really runs",
      "Pressure-testing the product against real procurement before the stakes are a make-or-break US account"]},
    {"h":"What it quietly hides, and why local-first burns a year","p":[
      "Israeli buyers are not American buyers. They negotiate harder on price, they tolerate a rougher product from a company they know personally, and they buy partly because the founder served with someone who vouched for you. None of that travels. You can close a dozen deals in Israel on relationships and informality, declare the motion proven, and then watch it fall apart the first time a US buyer who has never heard of you runs you through a real evaluation.",
      "That is the year founders burn. They treat local traction as proof the go-to-market works, scale on it, and discover in the US that they validated the wrong thing. The home market flattered them."]},
    {"h":"When local-first actually makes sense","tiers":[
      "Regulated or locally-bound products. If you sell to Israeli banks, hospitals, utilities or the public sector, the local market is a real market with real revenue, not a rehearsal. Start where you can win.",
      "Defense and government-adjacent. An IDF or Israeli government reference is an asset abroad, not a distraction. Here the local deal is strategic, not just practice.",
      "Hebrew-first or Israel-specific products. If the product only makes sense in the local language, regulation or market structure, abroad is a separate product, not a next step.",
      "Pure cash survival. If you need revenue this quarter to stay alive and the only reachable buyers are local, sell to them. Just do not confuse surviving with validating."]},
    {"h":"How I sequence it with clients","p":[
      "Use the local market to learn, not to prove. Close a handful of Israeli deals to sharpen the pitch and the mechanics, treat the results as a draft, and build the real go-to-market for the target market from day one. I built my own company by getting on a plane and visiting a customer, not by waiting for the home market to carry me. For most Israeli B2B companies the honest sequence is simple: learn at home if it is cheap and fast, but point the strategy, the ICP and the message at the US or the EU from the start."]},
    {"h":"Go deeper","links":[
      ["US market entry for Israeli startups", "/us-market-entry-for-israeli-startups"],
      ["When to expand to the US", "/when-to-expand-to-the-us"],
      ["Market entry service", "/services/market-entry"]]},
  ],
  "faqs":[
    {"q":"Should an Israeli startup sell in Israel before going abroad?","a":"For most B2B companies, treat Israel as a place to learn, not your target market. It is too small to build a company on, and local traction can flatter you because Israeli buyers buy on relationships and informality that do not travel. Sharpen the pitch at home if it is cheap, but build the go-to-market for the US or EU from day one."},
    {"q":"When does selling locally first make sense?","a":"When the local market is a real market with real revenue: regulated or locally-bound products sold to Israeli banks, hospitals, utilities or the public sector; defense and government deals where an Israeli reference is an asset abroad; Hebrew-first products; or pure cash survival when local buyers are the only ones you can reach now."},
    {"q":"Why do Israeli startups fail when they expand from a strong local base?","a":"Because they validated the wrong thing. Deals closed in Israel on personal relationships and a tolerance for a rough product do not predict how a US buyer who has never heard of you will evaluate you. Founders scale on home traction and find out abroad that the motion never actually worked for a cold market."},
    {"q":"Can you help an Israeli company sequence local and global sales?","a":"Yes. I have spent 20-plus years taking Israeli B2B companies into the US, the EU, Eastern Europe and APAC. I help decide what to learn at home, what to point abroad from day one, and then build and run the go-to-market for the target market."}],
  "related":'See <a href="/us-market-entry-for-israeli-startups">US market entry for Israeli startups</a>, <a href="/when-to-expand-to-the-us">when to expand to the US</a> and the <a href="/fractional-cro-israel">fractional CRO in Israel</a> guide. From the blog: <a href="/blog/choosing-first-market">how to choose your first market</a>, <a href="/blog/why-israeli-startups-fail-at-sales">why Israeli startups fail at sales abroad</a> and <a href="/blog/an-israeli-saas-company-sold-to-the-wrong-market-for">an Israeli SaaS company that sold to the wrong market</a>.'},

 {"slug":"when-to-expand-to-the-us",
  "title":"When to Expand to the US Market | Tal Paperin",
  "desc":"How to know your B2B company is ready for the US, the signals that say wait, and what to validate before you spend a dollar on a US move.",
  "h1":"When to Expand to the US Market","eyebrow":"Market Entry",
  "lead":"The US is the biggest prize and the fastest way to burn a raise. Most companies get the timing wrong in one of two directions: they race over to sell before they know anything, or they wait so long the home market becomes a ceiling. Here is how I read readiness, and what to prove before you commit a dollar.",
  "sections":[
    {"h":"Race to learn, not to sell","p":[
      "The most expensive US mistake is treating the move as a sales launch when it is really a learning exercise. Founders fly over, rent an office, hire two reps and expect pipeline in a quarter. Then nothing closes, the burn is real, and the raise is gone. The US does not reward presence alone. It rewards a company that already knows who buys, why, and what the sale looks like before it scales the spend.",
      "Expand when you are ready to learn fast and cheap in the US, not when you are desperate to book revenue there."]},
    {"h":"Signals you are ready","ul":[
      "You have referenceable customers, even small ones, who will take a call from a US prospect",
      "Your sale repeats: you can name the ICP, the stages and the cycle length without guessing",
      "US buyers are already pulling, inbound or in conversations, not just a market you assume wants you",
      "You have the runway to give it twelve to eighteen months, because a US motion does not pay back in a quarter",
      "A founder or senior leader can spend real time on US hours, not a rep left to sink or swim"]},
    {"h":"Signals you are not ready yet","ul":[
      "Sales still run entirely through the founder's personal network and nothing is documented",
      "You cannot describe your ICP without saying \"anyone who\"",
      "Your only proof is home-market deals closed on relationships, not a cold, repeatable motion",
      "You are expanding to escape a stalled home market rather than to chase real US demand",
      "The plan is to hire a US VP of Sales, hand them the problem and hope"]},
    {"h":"What to validate before you spend","p":[
      "Before the entity, the office and the first hire, have twenty real conversations with US buyers who fit your ICP. Not to sell. To learn whether the pain you solve is the pain they feel, whether your message lands in their words, and what they would actually pay. If US buyers take the meeting and lean in, that is the strongest readiness signal there is. If you cannot get them on the phone from Israel, a US office will not fix that.",
      "Then size it honestly: how much of your real addressable market sits in the US. If most of it does, the US is not a question of whether, only when and how."]},
    {"h":"Enter lean, then scale","p":[
      "Readiness does not mean relocating the company. The first US sales can come from your existing team working US hours, then a small landing team, then reps and an entity once the motion proves out. Sequence it: prove, then build the presence, direct or through partners, when it is justified. The companies that burn the US are the ones that build the whole apparatus before they have a single repeatable deal."]},
    {"h":"Go deeper","links":[
      ["US market entry for Israeli startups", "/us-market-entry-for-israeli-startups"],
      ["Fractional CRO for the US market", "/fractional-cro-for-the-us-market"],
      ["Sell in Israel first, or go global?", "/sell-in-israel-first-or-go-global"]]},
  ],
  "faqs":[
    {"q":"When should a startup expand to the US?","a":"When the sale already repeats and US buyers are pulling, not when you need revenue there to survive. Concretely: you have referenceable customers, a defined ICP and cycle, 12 to 18 months of runway, and a leader who can give it real time on US hours. If sales still run through the founder's network and nothing is documented, it is too early."},
    {"q":"How do I know if my company is ready for the US market?","a":"Have 20 real conversations with US buyers who fit your ICP before you spend a dollar on an entity or office. If they take the meeting and lean in, that is the strongest readiness signal. If you cannot get them on the phone from home, a US office will not fix it. Also check how much of your addressable market is actually in the US."},
    {"q":"Do I need a US office and team to start selling there?","a":"No. The first US sales can come from your existing team working US hours, then a small landing team, then reps and an entity once the motion proves out. Building the full apparatus before you have one repeatable deal is how companies burn the US."},
    {"q":"What is the most common US expansion mistake?","a":"Treating the move as a sales launch instead of a learning exercise. Founders rent an office and hire reps expecting pipeline in a quarter, then burn the raise when nothing closes. Expand to learn fast and cheap, not to book revenue you have not earned the right to yet."}],
  "related":'See <a href="/us-market-entry-for-israeli-startups">US market entry for Israeli startups</a>, <a href="/fractional-cro-for-the-us-market">fractional CRO for the US market</a> and <a href="/sell-in-israel-first-or-go-global">sell in Israel first, or go global?</a>. From the blog: <a href="/blog/entering-the-us-market">entering the US market</a>, <a href="/blog/setting-up-us-subsidiary">setting up a US subsidiary</a> and <a href="/blog/choosing-first-market">how to choose your first market</a>.'},
]


def render_guide_sections(g):
    out = []
    for sec in g["sections"]:
        out.append("        <h2>%s</h2>" % esc(sec["h"]))
        for p in sec.get("p", []):
            out.append("        <p>%s</p>" % esc(p))
        if sec.get("tiers"):
            out.append('        <ul class="guide-tiers">')
            for li in sec["tiers"]:
                out.append("          <li>%s</li>" % esc(li))
            out.append("        </ul>")
        if sec.get("ul"):
            out.append("        <ul>")
            for li in sec["ul"]:
                out.append("          <li>%s</li>" % esc(li))
            out.append("        </ul>")
        if sec.get("links"):
            out.append('        <div class="svc-links">')
            for text, href in sec["links"]:
                if href:
                    out.append('          <a href="%s">%s</a>' % (href, esc(text)))
                else:
                    out.append('          <span>%s</span>' % esc(text))
            out.append('        </div>')
        if sec.get("html"):
            out.append(sec["html"])
    return "\n".join(out)


HE_GUIDE_PAGE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />
{hreflang}

  <meta property="og:type" content="article" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{h1} | טל פאפרין" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta property="og:locale" content="he_IL" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{h1} | טל פאפרין" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {graph}
  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
  {faqld}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/he/">בית</a> / {h1}</p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
{faq}
{cta}
        <div class="svc-related">{related}</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


HE_GUIDES = [
 {"slug":"sales-training",
  "title":"הדרכת מכירות B2B שבאמת נדבקת | טל פאפרין",
  "desc":"רוב הדרכות המכירות נכשלות כי אף אחד לא מנהל אותן אחר כך. הכשרתי 2,000 אנשי מכירות בעולם, ואז ניהלתי אותם עד למספר. הנה מה שעובד.",
  "h1":"הדרכת מכירות לבדה לא עובדת. הנה מה שכן.","eyebrow":"מדריך",
  "lead":"אני לא מדריך מכירות. אני סמנכ״ל מכירות ו-CRO שהכשיר יותר מ-2,000 אנשי מכירות ברחבי העולם, ואז נשאר לנהל אותם עד שההדרכה הופיעה בעסקאות סגורות. החצי השני הזה הוא החלק שכולם מדלגים עליו, וזו הסיבה שרוב הדרכות המכירות הן בזבוז כסף.",
  "sections":[
    {"h":"למה רוב הדרכות המכירות הן בזבוז כסף","p":[
      "מביאים מדריך ליומיים. הצוות מתלהב. הם מקבלים חוברת, מתודולוגיה, אולי משחק תפקידים. כולם מרגישים חדים יותר ביום שישי. עד יום רביעי שאחרי הם חוזרים למכור בדיוק כמו קודם, כי אף אחד לא שינה את מה שקורה אחרי שההדרכה נגמרת.",
      "ההדרכה היא לא המוצר. שינוי ההתנהגות הוא המוצר. וההתנהגות משתנה רק כשמישהו בכיר בודק אותה, מאמן אותה, ומחזיק את הרף כל שבוע מחדש. מדריך טס הביתה. מנהל מכירות נשאר."]},
    {"h":"אני לא מדריך. אני CRO שמכשיר, ואז מנהל את הצוות.","p":[
      "יש הבדל בין מי שמעביר סדנה לבין מי שאחראי על המספר. נשאתי מכסה, בניתי את הפלייבוק, וישבתי בעסקאות בעצמי. כשאני מכשיר את הצוות שלכם, אני לא מלמד תיאוריה שקראתי בספר. אני מלמד בדיוק איך הייתי סוגר את העסקאות שלכם, כי סגרתי עסקאות כמו שלכם.",
      "ואז אני עושה את החלק שמדריך לא יכול: אני מנהל את הצוות כדי לוודא שזה עובד. אני יושב בשיחות, בודק את הפייפליין, מאמן את הנציגים שסוטים, ומעלה את הרף שוב ושוב עד שהדרך החדשה למכור היא פשוט הדרך שבה הצוות שלכם מוכר."]},
    {"h":"2,000 אנשי מכירות, ואז ניהול עד למספר","p":[
      "לאורך יותר מ-20 שנה הכשרתי יותר מ-2,000 אנשי מכירות בחמש יבשות: SDRs, סוגרים, שותפי ערוץ וצוותים שלמים, בסטארטאפים ובארגונים גדולים. ההדרכה מעולם לא הייתה העיקר. העיקר היה מה שקרה אחר כך: עסקאות נסגרו, מחזורי מכירה התקצרו, והמספר עלה ונשאר למעלה.",
      "זה המבחן שאני מציב לעצמי. לא כמה טובה הרגישה הסדנה באותו יום, אלא אם ההכנסות באמת זזו רבעון אחר כך. הן זזות."]},
    {"h":"איך נראית הדרכת מכירות אמיתית","ul":[
      "היא מתחילה מהעסקאות האמיתיות שלכם, מהקונים שלכם ומההתנגדויות האמיתיות, לא מתוכנית גנרית",
      "היא מועברת על ידי מפעיל שאחראי על המספר ונכנס לעסקאות האמיתיות, כך שהנציגים מכבדים אותה ומשתמשים בה",
      "אחריה מגיעים אימון שבועי, סקירת שיחות ובדיקת פייפליין, לא חוברת על המדף",
      "היא נאכפת על ידי מנהל שאחראי על המספר, כך שההתנהגות החדשה נדבקת",
      "היא נמדדת בהכנסות שנסגרו ובמחזורים קצרים יותר, לא בנוכחות וחיוכים"]},
    {"h":"הדרכה בלי ניהול היא הצגה","p":[
      "אם אתם רק רוצים סדנה חד פעמית כדי לסמן וי, אני האדם הלא נכון, ובכנות עדיף שתשמרו את הכסף. אבל אם אתם רוצים שהצוות שלכם ימכור טוב יותר וימשיך למכור טוב יותר, אתם צריכים את ההדרכה ואת הניהול יחד, מאותו אדם, עד שזה מחזיק. זה מה שסמנכ״ל מכירות במיקור חוץ עושה, וזו הסיבה שהלקוחות שלי רואים את המספרים באמת זזים."]},
  ],
  "faqs":[
    {"q":"אתה מציע הדרכת מכירות?","a":"כן, אבל לא כסדנה עצמאית. אני מכשיר את הצוות שלכם כחלק מלקיחת אחריות על המכירות, כלומר אני גם מנהל את הצוות אחר כך כדי לוודא שההדרכה הופכת לעסקאות סגורות. הכשרתי יותר מ-2,000 אנשי מכירות בעולם."},
    {"q":"למה רוב הדרכות המכירות לא עובדות?","a":"כי המדריך עוזב ואף אחד לא משנה את מה שקורה אחר כך. התנהגות נדבקת רק כשמנהל בכיר מאמן אותה, בודק אותה ומחזיק את הרף כל שבוע. הדרכה בלי ניהול מתמשך היא הצגה."},
    {"q":"מי מעביר את ההדרכה?","a":"אני. אני סמנכ״ל מכירות ו-CRO שנשא את המספר בידיים. אני מלמד בדיוק איך הייתי סוגר את העסקאות שלכם, מהפייפליין האמיתי שלכם, לא מתוכנית גנרית מתוך ספר."},
    {"q":"במה זה שונה משכירת מדריך מכירות?","a":"מדריך מעביר סדנה וטס הביתה. אני מכשיר את הצוות ואז נשאר לנהל אותו עד למספר: סקירת שיחות, בדיקת פייפליין ואימון שבועי עד שהדרך החדשה למכור היא פשוט איך שהצוות שלכם מוכר."},
    {"q":"כמה זה עולה?","a":"ההדרכה היא חלק מהתקשרות של סמנכ״ל מכירות במיקור חוץ, שנעה בין 2,000 ל-12,000 דולר בחודש תלוי כמה מעורבות אתם צריכים. השתמשו במחשבון בעמוד התמחור לקבלת מספר בערך בדקה."}],
  "related":'ראו <a href="/he/services/sales-team-building">בניית צוות מכירות</a>, את <a href="/he/services/fractional-cro">שירות סמנכ״ל המכירות במיקור חוץ</a>, <a href="/he/pricing">תמחור</a>, או קראו <a href="/he/blog/why-sales-training-fails">למה רוב הדרכות המכירות נכשלות</a>.'},

 {"slug":"fractional-cro-cost",
  "title":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ? | טל פאפרין",
  "desc":"תשובה ישירה על תמחור סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ: כמה זה עולה בחודש, איך זה משתווה למשרה מלאה של 250 אלף דולר, ומתי כל רמה שווה את זה.",
  "h1":"כמה באמת עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ","eyebrow":"מדריך",
  "lead":"רוב היועצים מסתירים את המחיר, מגישים לכם מצגת, ונעלמים. אני מפעיל שאחראי על המספר, מחייב חודשית בלי חוזה, והנה בדיוק כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, במספרים ברורים.",
  "sections":[
    {"h":"התשובה הקצרה","p":[
      "סמנכ״ל מכירות ופיתוח עסקי במשרה מלאה עולה 250 אלף דולר ומעלה בסך הכל, אחרי שמוסיפים בסיס, אקוויטי, בונוס, סיכון פיצויי פיטורין ומחזור גיוס של חודשים. סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ נותן לכם את אותה מנהיגות בכירה בתשלום חודשי. התפקיד זהה בכל רמה. הדבר היחיד שמשתנה הוא כמה שעות ביום אני בעסק שלכם."]},
    {"h":"שלוש הרמות, לפי כמה ממני אתם צריכים","tiers":[
      "Advisor, 2,000 דולר בחודש. כשלוש שעות בשבוע. שיחת אסטרטגיה שבועית קבועה וגישה אליי בין השיחות, להחלטות האמיתיות. למייסדים שרוצים כיוון בכיר בזמן שהם מריצים את היומיום בעצמם.",
      "Starter, 6,000 דולר בחודש. אני, סמנכ״ל המכירות ופיתוח העסקי שלכם, בתוך העסק שעתיים ביום, בכל יום עבודה. אני מחזיק את האסטרטגיה, השיטה והסטנדרטים, והצוות שלכם מבצע את רוב היומיום. מה שרוב החברות בוחרות.",
      "Growth, 12,000 דולר בחודש. חצי משרה, ארבע שעות ביום. כבר לא רק מכוון, מניע: אני מריץ את המוטור שבוע אחר שבוע, מנהל את הצוות בידיים, ונושא איתכם במספר. התקשרויות במשרה מלאה ובלעדיות זמינות לפי בקשה."]},
    {"h":"למה זה זול יותר מגיוס במשרה מלאה","ul":[
      "בלי בסיס של 250 אלף דולר, אקוויטי, בונוס או סיכון פיצויים",
      "בלי חיפוש גיוס של שלושה חודשים ובלי התברגות של שני רבעונים",
      "חיוב חודשי, בלי חוזה, בלי נעילה, בלי קנסות יציאה: לא אהבתם, סיימנו בסוף החודש",
      "תוצאות בשבוע הראשון, לא בחודש השישי"]},
    {"h":"אתם שוכרים מפעיל, לא יועץ","p":[
      "רוב היועצים מגישים לכם מצגת ונעלמים. הם מעולם לא נשאו אחריות על מספר. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר. אני לוקח אחריות על המספר, בונה ומנהל את הצוות שמביא אותו, ונכנס לעסקאות הגדולות בעצמי. ואני מחייב חודשית בלי חוזה, אז אני שומר על העבודה בזכות זה שאני טוב בה, לא בזכות חוזה שכולא אתכם."]},
  ],
  "faqs":[
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ?","a":"הפרויקטים שלי נעים בין 2,000 ל-12,000 דולר בחודש לפי רמת המעורבות, לעומת 250 אלף דולר ומעלה לסמנכ״ל מכירות ופיתוח עסקי במשרה מלאה אחרי אקוויטי, בונוס ופיצויים."},
    {"q":"האם סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ זול יותר מסמנכ״ל מכירות ופיתוח עסקי במשרה מלאה?","a":"כן. אתם מקבלים את אותה מנהיגות בכירה בלי המשכורת, האקוויטי, הבונוס, סיכון הפיצויים, מחזור הגיוס או ההתברגות הארוכה, ובלי נעילה לטווח ארוך."},
    {"q":"מה כלול?","a":"אותו דבר בכל רמה: אבחון הכנסות, אסטרטגיית מכירות ותחזית, Playbook, מבנה CRM ופייפליין, הכשרת צוות, ניהול מעשי של התנועה, החלטות גיוס וביצועים, ואחריות מלאה על מכירות, שיווק ו-Go-to-Market. מה שמשתנה בין הרמות הוא כמה שעות ביום אני בעסק שלכם: שעתיים, ארבע שעות, או משרה מלאה."},
    {"q":"כמה זמן נמשך פרויקט סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ?","a":"אין נעילה לטווח ארוך. אתם מגדילים את המעורבות ככל שאתם גדלים, או מעבירים את הפונקציה הלאה כשהיא בנויה."},
    {"q":"האם אני צריך לחתום על חוזה ארוך?","a":"לא. אני מחייב חודשית בלי חוזה ובלי קנסות יציאה. אם לא אהבתם מה שאני מספק, סיימנו בסוף החודש ואתם לא חייבים עוד כלום."}],
  "related":'ראו את <a href="/he/services/fractional-cro">שירות הסמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a>, <a href="/he/case-studies">מקרי מבחן</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>. מהבלוג: <a href="/he/blog/fractional-cro-explained">סמנכ״ל מכירות ופיתוח עסקי במשרה חלקית, מה זה</a>, <a href="/he/blog/cost-of-bad-vp-sales-hire">כמה עולה גיוס כושל של סמנכ״ל מכירות</a>.'},

 {"slug":"fractional-cro-vs-outsourced-sales",
  "title":"סמנכ״ל מכירות במיקור חוץ מול סוכנות מכירות | טל פאפרין",
  "desc":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, מכירות במיקור חוץ מלא, או מערכת שאתם מריצים לבד? פירוק ישיר של מה מתאים לשלב שלכם, ואיך לבחור.",
  "h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול מכירות במיקור חוץ","eyebrow":"מדריך",
  "lead":"שלוש דרכים לתקן הכנסות, החלטה אחת. בכל אחת אתם מקבלים מפעיל שאחראי על המספר, בחיוב חודשי בלי חוזה ובלי נעילה. הנה איזו מהן מתאימה לשלב שלכם, ואיזו מבזבזת לכם כסף.",
  "sections":[
    {"h":"שלוש האפשרויות","tiers":[
      "לעשות זאת בעצמכם. יש לכם את האנרגיה והזמן להריץ את התנועה, אתם רק צריכים את המערכת: ה-Playbook, התסריטים, כרטיסי הקרב והליווי היומי. העלות הנמוכה ביותר, רוב הזמן שלכם.",
      "סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ. אתם צריכים מנהיג בכיר שייקח אחריות על התוצאות וירוץ את התנועה איתכם, אבל העבודה עוד לא משרה מלאה. אני לוקח אחריות אישית. הרמה האמצעית, ומה שרוב החברות בוחרות.",
      "מכירות במיקור חוץ מלא. אתם רוצים את כל הפונקציה מחוץ לצלחת: אנשי SDR ו-AE דוברי שפת אם, הובלה בכירה ו-VP, צוות שלם שמגויס, מוכשר, מנוהל ומדווח עליו מדי יום, חי מחוץ למצבת כוח האדם שלכם."]},
    {"h":"איך לבחור","ul":[
      "אם הבעיה היא שאין לכם מערכת, עשו זאת בעצמכם עם הכלים הנכונים",
      "אם הבעיה היא שאף אחד לא אחראי על התוצאות, קחו סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ",
      "אם הבעיה היא שאין לכם צוות ואין לכם זמן לבנות אחד, הוציאו את כל הפונקציה למיקור חוץ"]},
    {"h":"המבחן הכן","p":[
      "שאלו שאלה אחת: האם תנועת המכירות שלכם מוכחת? אם כן, אתם בעיקר צריכים ביצוע, אז מערכת או צוות במיקור חוץ יכולים להריץ אותה. אם לא, אתם צריכים מנהיגות בכירה כדי למצוא את התנועה קודם, וזה בדיוק מה ש-סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ עושה לפני שאתם מוציאים על צוות."]},
  ],
  "faqs":[
    {"q":"כדאי לשכור סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ או להוציא את המכירות למיקור חוץ?","a":"שכרו סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ כשאף אחד לא אחראי על התוצאות והתנועה עוד לא מוכחת. הוציאו את כל הפונקציה למיקור חוץ כשאין לכם צוות ואין לכם זמן לבנות אחד ואתם רק רוצים שמכירות יקרו מחוץ למצבת כוח האדם."},
    {"q":"מה ההבדל בין סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ לצוות מכירות במיקור חוץ?","a":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ הוא מנהיג בכיר יחיד שבעל האסטרטגיה, התחזית והתנועה. צוות מכירות במיקור חוץ הוא צוות מלא של SDR, AE ו-VP שמריץ יום-יום. אחד הוא מנהיגות, השני הוא ביצוע."},
    {"q":"מה זול יותר?","a":"מערכת שאתם מריצים לבד היא הזולה ביותר, סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ הוא האמצע, וצוות במיקור חוץ מלא הוא ההתחייבות הגדולה ביותר כי אתם קונים פונקציה שלמה."}],
  "related":'ראו <a href="/he/services/fractional-cro">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a>, <a href="/he/services/outsourced-sales">מכירות במיקור חוץ</a>, או <a href="/he/contact">צרו קשר</a>. מהבלוג: <a href="/he/blog/outsourced-vp-sales-israel">סמנכ״ל מכירות במיקור חוץ</a>, <a href="/he/blog/building-international-sales-team">בניית צוות מכירות בינלאומי</a>.'},

 {"slug":"fractional-cro-israel",
  "title":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל | טל פאפרין",
  "desc":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ לחברות B2B ישראליות שמוכרות בבית ובחו״ל. מנהיגות הכנסות בכירה, בעברית או באנגלית, בלי גיוס במשרה מלאה של 250 אלף דולר.",
  "h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל","eyebrow":"מדריך",
  "lead":"מנהיגות הכנסות בכירה לחברות ישראליות, בעברית או באנגלית, בנויה למכירה לארה״ב, לאיחוד האירופי ומעבר.",
  "sections":[
    {"h":"בנוי לחברות ישראליות שמוכרות בחו״ל","p":[
      "חברות B2B ישראליות בונות מוצרים מצוינים ואז נתקלות באותו קיר: למכור אותם לשווקים שלא עובדים כמו השוק המקומי. ביליתי יותר מ-20 שנה בפתיחת ארה״ב, האיחוד האירופי, ה-FSU וה-APAC לחברות ישראליות, במכירה ישירה ודרך ערוצים."]},
    {"h":"על מה אני לוקח אחריות","ul":[
      "אסטרטגיית הכנסות, התחזית והאחריות על התוצאות",
      "תנועת ה-Go-to-Market לשווקים בינלאומיים, לא רק המקומי",
      "הצוות: גיוס, הכשרה והחלפה היכן שצריך",
      "מפיצים, ערוצים ומשא ומתן חוזי מורכב מעבר לגבולות"]},
    {"h":"בעברית או באנגלית","p":[
      "אני עובד עם מייסדים וצוותים בעברית ומריץ את המכירה בפועל באנגלית, או בכל שפה שהשוק היעד מדבר. אתם מקבלים מנהיג שמכיר את נקודת ההתחלה הישראלית ואת קו הסיום בחו״ל."]},
  ],
  "faqs":[
    {"q":"אתם עובדים עם חברות ישראליות?","a":"כן. רוב העבודה שלי היא לקחת חברות B2B ישראליות לארה״ב, לאיחוד האירופי ולשווקים נוספים, במכירה ישירה ודרך מפיצים."},
    {"q":"אפשר לעבוד בעברית?","a":"כן. אני עובד עם מייסדים וצוותים ישראליים בעברית ומריץ את המכירה הבינלאומית באנגלית או בשפת השוק היעד."},
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל?","a":"הפרויקטים נעים בין 2,000 ל-12,000 דולר בחודש לפי רמת המעורבות, הרבה מתחת לגיוס סמנכ״ל מכירות ופיתוח עסקי במשרה מלאה של 250 אלף דולר ומעלה."}],
  "related":'שוקלים מקומי מול גלובלי? ראו <a href="/he/sell-in-israel-first-or-go-global">למכור קודם בישראל, או ישר לחו״ל?</a> ו<a href="/he/when-to-expand-to-the-us">מתי להתרחב לשוק האמריקאי</a>. או ראו את שירותי <a href="/he/services/market-entry">כניסה לשוק</a> ו-<a href="/he/services/fractional-cro">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a>, או <a href="/fractional-cro-israel">הגרסה באנגלית</a>. מהבלוג: <a href="/he/blog/entering-the-us-market">כניסה לשוק האמריקאי</a>, <a href="/he/blog/why-israeli-startups-fail-at-sales">למה סטארטאפים ישראלים נכשלים במכירות בחו״ל</a>.'},

 {"slug":"fractional-cro-vs-vp-of-sales",
  "title":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול גיוס VP מכירות | טל פאפרין",
  "desc":"נמאס לכם מגיוסי VP מכירות של 30 אלף דולר בחודש שאתם מפטרים תוך 90 יום? סמנכ״ל הכנסות במיקור חוץ נותן מנהיגות הכנסות מוכחת בלי הימור גיוס ובלי נעילה.",
  "h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול גיוס VP מכירות","eyebrow":"מדריך",
  "lead":"כבר עשיתם את זה. שכרתם VP מכירות בשלושים אלף בחודש, חיכיתם, ראיתם שכלום לא זז, פיטרתם בחודש השלישי, אכלתם את הפיצויים, התחלתם מחדש. הנה האלטרנטיבה.",
  "sections":[
    {"h":"בית הקברות של ה-VP מכירות","p":[
      "VP מכירות עולה 30,000 דולר בחודש או יותר, בסך הכל. החיפוש לוקח חודשים. ההתברגות לוקחת רבעון. ואם ההתאמה שגויה, וזה קורה הרבה, אתם מפטרים בחודש השני, השלישי או הרביעי, אוכלים את הפיצויים, ומתחילים את כל המחזור מחדש. ראיתי מייסדים שורפים מאות אלפי דולרים ככה, בלי שום דבר להראות מלבד זמן אבוד.",
      "הגיוס הוא הימור. אתם מהמרים שש ספרות על קורות חיים ושלושה ראיונות."]},
    {"h":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ הוא לא הימור","ul":[
      "בניתי והרצתי הכנסות ל-30 ומעלה חברות B2B בחמש יבשות. אתם לא מהמרים אם אני יכול לעשות את זה. כבר עשיתי",
      "בלי דמי מגייסים, בלי אקוויטי, בלי סיכון פיצויים, בלי חיפוש של חודשים",
      "תוצאות בשבוע הראשון: אני מאבחן איפה העסקאות דולפות, ואז מריץ את התיקון. בלי התברגות, בלי עקומת למידה"]},
    {"h":"אני לוקח אחריות על המספר. בעצמי. ידיים בבוץ.","p":[
      "רוב היועצים מגישים לכם מצגת ונעלמים. הם מעולם לא נשאו אחריות על מספר. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר. אני מאבחן איפה ההכנסות נתקעו, בונה ומנהל את הצוות שמתקן את זה, ונכנס לעסקאות הגדולות בעצמי. אתם שוכרים מפעיל, לא יועץ."]},
    {"h":"חודשי. בלי חוזה. בלי בני ערובה.","p":[
      "אני מחייב חודשית. בלי חוזה ארוך, בלי נעילה, בלי קנסות יציאה. לא אהבתם מה שאני מספק, סיימנו בסוף החודש, ואתם לא חייבים עוד כלום. אני שומר על העבודה כי היא טובה, לא כי חוזה כולא אתכם. זה ההפך מגיוס VP שאי אפשר לבטל בקלות."]},
  ],
  "faqs":[
    {"q":"האם סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ עדיף על גיוס VP מכירות?","a":"אם תנועת המכירות שלכם עוד לא מוכחת, כן. גיוס VP הוא הימור של שש ספרות עם חודשי חיפוש, רבעון התברגות וסיכון פיצויים אמיתי. סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ שעשה את זה 30 פעמים ומעלה מספק מהשבוע הראשון, בלי סיכון גיוס ובלי נעילה."},
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול VP מכירות?","a":"VP מכירות עולה 30,000 דולר בחודש או יותר בסך הכל, פלוס דמי מגייסים, אקוויטי ופיצויים. הפרויקטים שלי במיקור חוץ נעים בין 2,000 ל-12,000 דולר בחודש, בחיוב חודשי בלי חוזה."},
    {"q":"ומה אם זה לא עובד?","a":"אני מחייב חודשית בלי חוזה ובלי קנסות יציאה. אם לא אהבתם מה שאני מספק, סיימנו בסוף החודש ואתם לא חייבים עוד כלום."},
    {"q":"אתה באמת עושה את העבודה, או רק מייעץ?","a":"אני עושה את העבודה. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר. אני לוקח אחריות על המספר, בונה ומנהל את הצוות, ונכנס לעסקאות הגדולות בעצמי, לא רק במצגות אסטרטגיה."}],
  "related":'השוו את <a href="/he/fractional-cro-cost">העלות</a>, ראו <a href="/he/fractional-cro-vs-outsourced-sales">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול מכירות במיקור חוץ</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>. מהבלוג: <a href="/he/blog/when-to-hire-vp-sales">מתי לגייס סמנכ״ל מכירות</a>, <a href="/he/blog/cost-of-bad-vp-sales-hire">כמה עולה גיוס כושל של סמנכ״ל מכירות</a>.'},

 {"slug":"how-to-hire-a-fractional-cro",
  "title":"איך לשכור Fractional CRO (מדריך מעשי) | טל פאפרין",
  "desc":"איך לשכור סמנכ״ל הכנסות במיקור חוץ: מתי צריך אחד, מה לחפש, אילו שאלות לשאול, וכמה זה עולה.",
  "h1":"איך לשכור Fractional CRO","eyebrow":"מדריך",
  "lead":"סמנכ״ל הכנסות במיקור חוץ יכול לתקן את ההכנסות שלכם בלי גיוס של רבע מיליון דולר, אבל רק אם תבחרו את הנכון. הנה איך, ממישהו שישב בכיסא הזה יותר מ-30 פעמים.",
  "sections":[
    {"h":"מתי אתם מוכנים לאחד","p":["אתם מוכנים כשההכנסות נתקעו ואף אחד בכיר לא אחראי על התוצאות, כשאתם צריכים תוצאות לפני שאפשר להצדיק משרה מלאה, או כששרפתם כסף על גיוסי VP שלא הזיזו את התוצאות. אם אתם רק צריכים עוד ידיים, גייסו נציגים. אם אתם צריכים מישהו שייקח אחריות על האסטרטגיה, הצוות והתחזית, גייסו CRO."]},
    {"h":"מה לחפש","ul":["איש ביצוע שנשא אחריות על תוצאות, לא יועץ שמגיש מצגת","ניסיון מעשי במכירה מהסוג שלכם: B2B, גודל העסקה שלכם, התהליך שלכם","נכונות לקחת אחריות על גיוס, הכשרה והחלפה של נציגים, לא רק לייעץ","גישה ברורה של אבחון ואז ביצוע, עם תחזית שהוא יעמוד מאחוריה","תנאים חודשיים בלי נעילה ארוכה, כך שהוא ממשיך להרוויח את החידוש"]},
    {"h":"שאלות לשאול לפני שחותמים","ul":["ספר לי על מערך הכנסות שבנית מאפס ומה היה באחריותך","מה תעשה בשבוע הראשון, בשבוע השני ובחודש הראשון","איך אתה מחליט את מי לשמור, להכשיר או להחליף בצוות שלי","איך נראית התחזית שלך ועל מה אתה אחראי","כמה שעות ביום אתה באמת תהיה בעסק שלי"]},
    {"h":"כמה זה עולה","p":["סמנכ״ל הכנסות במיקור חוץ מתומחר לפי כמה מהשבוע אתם צריכים, לא לפי משכורת מלאה. צפו לכ-2,000 דולר בחודש ליועץ שבועי, 6,000 לכמה שעות ביום, ועד 12,000 לחצי משרה, בחיוב חודשי, עם משרה מלאה ובלעדית לפי בקשה. השוו את זה ל-250,000 דולר ומעלה בסך הכל ל-CRO במשרה מלאה ברגע שמוסיפים אקוויטי, בונוס, סיכון פיצויים ומחזור גיוס ארוך."]},
  ],
  "faqs":[
    {"q":"כמה עולה לשכור Fractional CRO?","a":"בדרך כלל 2,000 עד 12,000 דולר בחודש לפי כמה שעות ביום אתם צריכים, בחיוב חודשי בלי נעילה, הרבה מתחת ל-CRO במשרה מלאה של 250,000 דולר ומעלה."},
    {"q":"כמה מהר אפשר להתחיל?","a":"מהר. טוב מאבחן בשבוע הראשון, נותן תוכנית ותחזית אמיתית בשבוע השני, ומריץ את התהליך מהשבוע השלישי, במקום החודשים שלוקח לגייס ולהתברג למשרה מלאה."},
    {"q":"Fractional CRO או CRO במשרה מלאה?","a":"שכרו במיקור חוץ כשהעבודה עוד לא שבוע מלא או כשאתם צריכים תוצאות עכשיו בלי העלות והסיכון של משרה מלאה. עברו למשרה מלאה כשהפונקציה גדולה מספיק כדי להצדיק משכורת בכירה כל השנה."}],
  "related":'ראו את שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a>, השוו <a href="/he/fractional-cro-vs-vp-of-sales">CRO מול VP מכירות</a> ו<a href="/he/fractional-cro-cost">העלות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"when-do-you-need-a-fractional-cro",
  "title":"מתי צריך Fractional CRO? הסימנים | טל פאפרין",
  "desc":"הסימנים הברורים שאתם צריכים סמנכ״ל הכנסות במיקור חוץ: הכנסות תקועות, אין בעלים לתוצאות, VP-ים שהתחלפו, מוצר מצוין שלא נמכר.",
  "h1":"מתי צריך Fractional CRO?","eyebrow":"מדריך",
  "lead":"רוב החברות מחכות יותר מדי. הנה הסימנים שאתם צריכים סמנכ״ל הכנסות במיקור חוץ עכשיו, לא אחרי עוד רבעון אבוד.",
  "sections":[
    {"h":"שמונה הסימנים שהגיע הזמן","html":IG_SIGNS_HE},
    {"h":"על מה סמנכ״ל הכנסות במיקור חוץ אחראי","html":IG_ENGINE_HE},
    {"h":"סמנכ״ל הכנסות במיקור חוץ או VP מכירות?","html":IG_OWNS_HE},
    {"h":"מה משתנה כשמישהו אחראי על התוצאות","p":["סמנכ״ל הכנסות במיקור חוץ לוקח את האסטרטגיה, הצוות, הפייפליין, התחזית והאחריות מהצלחת שלכם אל שלו. שבוע ראשון זה אבחון, שבוע שני זה תוכנית ותחזית אמיתית, ואז הוא מריץ את זה, מגייס איפה שצריך, מכשיר את הצוות שיש לכם ומחליף את מי שלא יכול. אתם מפסיקים לנחש ומתחילים לתפעל."]},
    {"h":"לפני ואחרי","html":IG_BA_HE},
    {"h":"מה סמנכ״ל הכנסות במיקור חוץ באמת עושה","html":IG_DOES_HE},
    {"h":"איך נראה תהליך העבודה","html":IG_PHASES_HE},
    {"h":"מה עולה לחכות","p":["המחיר של ההמתנה הוא גיוס VP שגוי, שנה שאבדה, ושש ספרות שהוצאו כדי ללמוד מה שאיש ביצוע בכיר היה אומר לכם בשבוע הראשון. הכנסות תקועות כמעט אף פעם לא מתקנות את עצמן, וככל שהתהליך נשאר שבור יותר זמן, כך עולה יותר לבנות אותו מחדש."]},
  ],
  "faqs":[
    {"q":"מה ההבדל בין Fractional CRO ליועץ?","a":"יועץ מגיש מצגת והולך. סמנכ״ל הכנסות במיקור חוץ לוקח אחריות על העבודה, על הפייפליין, על העסקאות ועל התוצאות, ועונה על התוצאה."},
    {"q":"החברה שלי קטנה מדי ל-Fractional CRO?","a":"אם יש לכם מוצר וקצת הכנסות אבל אין תהליך חוזר או בעלים בכיר לתוצאות, אתם בדיוק הגודל הנכון. מיקור חוץ קיים כדי שתקבלו הנהגה ברמת CRO בלי משכורת מלאה."},
    {"q":"כמה מהר אראה תוצאות?","a":"אתם מקבלים אבחון בשבוע הראשון ותוכנית ותחזית בשבוע השני. שיפורים בפייפליין ובתהליך מגיעים ככל שהתהליך נבנה ורץ."}],
  "related":'ראו <a href="/he/how-to-hire-a-fractional-cro">איך לשכור</a> ואת <a href="/he/services/fractional-cro">השירות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"founder-led-sales-wont-scale",
  "title":"מכירות מבוססות-מייסד לא מתרחבות: איך מתקנים | טל פאפרין",
  "desc":"מכירות מבוססות-מייסד נתקעות כשכל עסקה עדיין עוברת דרככם. הנה איך להפוך את זה למהלך שצוות יכול להריץ, בלי לאבד את מה שהביא אתכם לכאן.",
  "h1":"כשמכירות מבוססות-מייסד מפסיקות להתרחב","eyebrow":"מדריך",
  "lead":"מכירות מבוססות-מייסד עובדות בדיוק עד שהן מפסיקות. הנה למה זה נתקע, ואיך למסור את המהלך לצוות בלי שהמספר יתרסק.",
  "sections":[
    {"h":"למה זה נתקע","p":["מכירות מבוססות-מייסד עובדות בהתחלה כי אתם איש המכירות הטוב בחברה. אתם מכירים את המוצר לעומק, יש לכם הסמכות לכופף תנאים, וקונים סומכים על מי שבנה את הדבר. זו גם המלכודת. המהלך חי בראש שלכם, לא במערכת, ולכן אי אפשר להעתיק אותו. הצמיחה נשארת חסומה במספר השעות שאתם יכולים למכור בעצמכם."]},
    {"h":"הסימנים שהגעתם לתקרה","ul":["כל עסקה אמיתית עדיין צריכה אתכם בשיחה כדי להיסגר","הנציגים שגייסתם עסוקים אבל לא סוגרים","הפייפליין והתחזית הם ניחוש, כי רק אתם יודעים אילו עסקאות אמיתיות","ההכנסות משתטחות ברגע שאתם פונים לנהל את החברה","גיוסים חדשים לוקחים חודשים להיכנס לקצב ורובם לא מגיעים למספרים שלכם"]},
    {"h":"מה באמת צריך לעבור","p":["גיוס נציגים לא פותר את זה. אתם לא חסרים ידיים, אתם חסרים מהלך חוזר. מה שחייב לצאת מהראש שלכם אל הנייר הוא כל המערכת: מי הקונה האמיתי, המסר שעובד, שאלות הסינון, התשובות להתנגדויות, הצעדים משיחה ראשונה לחתימה, והדרך שבה אתם קוראים עסקה. העבירו את המהלך, ואז האנשים יכולים להריץ אותו."]},
    {"h":"איך אני מתקן","p":["בשבוע הראשון אני מאבחן מה אתם באמת עושים כשאתם מוכרים, כולל החלקים שאתם לא שמים לב אליהם. בשבוע השני אני הופך את זה למהלך מתועד עם תחזית אמיתית. אחר כך אני בונה ומאמן את הצוות להריץ אותו, מחליף את מי שלא מתאים, ולוקח אחריות על המספר בזמן שהם נכנסים לקצב. אתם מקבלים את השבוע שלכם בחזרה בלי לראות את ההכנסות נתקעות."]},
    {"h":"מה עולה ההמתנה","p":["כל רבעון שאתם נשארים הסוגר היחיד הוא רבעון שהחברה לא יכולה לצמוח מעבר אליכם, ורבעון שהנציגים הכי טובים שלכם מבזבזים על למידה שלא עוברת הלאה. מייסדים שמחכים בדרך כלל משלמים פעמיים: פעם על הנציגים שלא עבדו, ושוב על בניית המהלך מחדש אחר כך תחת לחץ."]},
  ],
  "faqs":[
    {"q":"למה הנציגים שלי לא סוגרים כמוני?","a":"כי המהלך חי בראש שלכם, לא במערכת שהם יכולים ללמוד. הנציגים לא חסרי מאמץ, הם חסרי דרך מתועדת למכור כמוכם. בנו את המהלך, אמנו אותם עליו, והסגירה הופכת לנלמדת."},
    {"q":"שאשכור פשוט סמנכ״ל מכירות?","a":"רק אם אתם יכולים להגדיר לו את המהלך להרחבה. לגייס סמנכ״ל כדי שימציא את תהליך המכירה מאפס זו הדרך שבה מייסדים שורפים סמנכ״לים יקרים. סמנכ״ל הכנסות במיקור חוץ בונה קודם את המהלך, ואז אתם מגייסים כדי להריץ אותו."},
    {"q":"כמה זמן עד שהצוות ימכור בלעדיי?","a":"מהלך מתועד ותחזית אמיתית מגיעים בשבועיים הראשונים. כניסת הנציגים לקצב עליו היא עניין של שבועות אחרי זה, לא החודשים הרבים שלוקח לגיוס לא-מונחה."}],
  "related":'חלק מ<a href="/he/how-to-build-a-sales-team">איך בונים ומרחיבים צוות מכירות</a>. ראו את <a href="/he/services/sales-team-building">שירות בניית צוות המכירות</a>, <a href="/he/services/fractional-cro">שירות ה-Fractional CRO</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"building-a-sales-team-after-funding",
  "title":"בניית צוות מכירות אחרי גיוס | טל פאפרין",
  "desc":"גייסתם? הדרך הכי מהירה לשרוף את הסבב היא לגייס נציגים בלי מהלך ובלי מנהיג. הנה סדר הפעולות שהופך גיוס להכנסה.",
  "h1":"איך בונים צוות מכירות אחרי גיוס","eyebrow":"מדריך",
  "lead":"סבב לא קונה לכם שוק, הוא קונה לכם זמן. הנה איך לבזבז אותו על בניית צוות מכירות שמייצר הכנסה במקום לשרוף את הגיוס.",
  "sections":[
    {"h":"המלכודת שאחרי הגיוס","p":["הדירקטוריון רוצה צמיחה, אז האינסטינקט הוא לגייס מהר: כמה נציגים, אולי צוות SDR, וקדימה. אחר כך עוברים שני רבעונים, הנציגים עסוקים, הפייפליין נראה מלא, וכמעט כלום לא נסגר. הכסף יצא, ההכנסה לא נכנסה. הסבב לא אכזב אתכם. גיוס צוות לפני שהיה לכם מהלך אכזב."]},
    {"h":"הסדר שעובד","ul":["קודם נעלו את המהלך: מי קונה, למה, המסר, והדרך החוזרת משיחה ראשונה לחתימה","הוכיחו אותו עם כמה עסקאות שאדם שאינו המייסד יכול לסגור, לא רק אתם","גייסו מנהיג מכירות, או כזה במיקור חוץ, לפני שאתם מרחיבים את כוח האדם","אז הוסיפו נציגים מול מהלך שכבר עובד, כך שהם נכנסים לקצב על מערכת במקום לנחש","בנו את התחזית ואת משמעת הפייפליין לפני שאתם מדווחים עליהן לדירקטוריון"]},
    {"h":"איפה הכסף באמת נשרף","p":["מייסדים שורפים את הסבב במקומות צפויים: נציגים שגויסו בלי מנהיג מעליהם, צוות SDR שמזין משפך שאף אחד לא סינן, הנחות שניתנו כדי לכפות ניצחונות מוקדמים שקובעים מחיר גרוע, ותחזית בנויה על תקווה. כל אחד מהם מרגיש כמו התקדמות וכל אחד מהם עולה לכם רבעון שלא תחזירו."]},
    {"h":"איך אני עוזר אחרי גיוס","p":["אני נכנס כסמנכ״ל הכנסות במיקור חוץ, בונה את המהלך, מגייס ומאמן את הצוות מולו, ולוקח אחריות על המספר בזמן שהוא נכנס לקצב, כך שאתם לא מהמרים את הסבב על גיוס במשרה מלאה שלוקח חודשים למצוא ואולי לא יתאים. אתם מקבלים הנהגה בכירה עכשיו, בשבריר מעלות CRO מלא, בדיוק כשהלחץ לצמוח הכי גבוה."]},
  ],
  "faqs":[
    {"q":"לגייס נציגים מיד אחרי גיוס?","a":"לא קודם. נציגים שגויסו לפני שיש מהלך חוזר ומנהיג שיריץ אותו הם הדרך הנפוצה ביותר שבה מייסדים שורפים סבב. נעלו את המהלך, הוכיחו אותו, הוסיפו את המנהיג, ואז הרחיבו נציגים מולו."},
    {"q":"CRO במשרה מלאה או במיקור חוץ אחרי גיוס?","a":"מיקור חוץ לרוב נכון מיד אחרי גיוס: אתם מקבלים הנהגה בכירה מיד, בונים את המהלך ואת הצוות, ונמנעים מהימור של הסבב על חיפוש ארוך למשרה מלאה. עברו למשרה מלאה כשהפונקציה מצדיקה את המשכורת."},
    {"q":"כמה מהר הצוות אמור לייצר?","a":"אתם אמורים לקבל מהלך מתועד ותחזית אמיתית תוך השבועיים הראשונים, עם נציגים שנכנסים לקצב בשבועות שאחרי, במקום צוות שנראה עסוק שני רבעונים בלי שכלום נסגר."}],
  "related":'חלק מ<a href="/he/how-to-build-a-sales-team">איך בונים ומרחיבים צוות מכירות</a>. ראו את <a href="/he/services/sales-team-building">בניית צוות מכירות</a>, <a href="/he/fractional-cro-for-startups">Fractional CRO לסטארטאפים</a>, <a href="/he/setting-sales-quotas">איך קובעים יעדי מכירות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"sales-team-missing-quota",
  "title":"צוות המכירות לא עומד ביעד? הנה למה ואיך מתקנים | טל פאפרין",
  "desc":"צוות המכירות שלכם לא עומד ביעד שוב ושוב. בדרך כלל זו לא אשמת הנציגים. הנה האבחון האמיתי, מכיסוי פייפליין ועד בדיקת עסקאות, ואיך אני מתקן.",
  "h1":"כשצוות המכירות לא עומד ביעד שוב ושוב","eyebrow":"מדריך",
  "lead":"כשצוות מפספס יעד שני רבעונים ברצף, האינסטינקט הוא להאשים את הנציגים או להחליף אותם. זה כמעט תמיד המהלך הלא נכון. רוב הפספוסים הם בעיה של פייפליין ותהליך, ואפשר לתקן אותם בלי לפטר אף אחד.",
  "sections":[
    {"h":"זו בדרך כלל לא בעיה של מאמץ","p":["נציגים שמפספסים יעד הם לעיתים רחוקות עצלנים. בדרך כלל הם עובדים קשה מול מהלך שלא יכול לייצר את המספר. אם אין מספיק פייפליין מסונן מולם, שום כמות שיחות לא תסגור את הפער. אם לשלבים אין משמעות אמיתית, עסקאות שלא היו נסגרות לעולם יושבות בתחזית עד סוף הרבעון ואז נעלמות. לפני שאתם נוגעים בהרכב, הסתכלו על מה אתם מבקשים מהצוות להריץ."]},
    {"h":"הסיבות האמיתיות לפספוס","ul":["פייפליין דק. כלל האצבע הוא פי שלושה עד ארבעה מהיעד בפייפליין מסונן כדי שיהיה סיכוי אמיתי. מתחת לפי שלושה, המתמטיקה נגדכם לא משנה כמה טובים הנציגים","אין סינון, אז עסקאות שלעולם לא ייסגרו אוכלות את הרבעון ומתות בשבועיים האחרונים","יעד שנקבע בלי בסיס ביכולת או בשיעורי הסגירה ההיסטוריים, כך שהצוות מעולם לא היה אמור לעמוד בו","אין בדיקת עסקאות. אף אחד לא מסתכל על העסקאות האמיתיות שבועית, אז עסקאות בסיכון מקבלות תשומת לב רק אחרי שאבדו","תמחור עמלות שמשלם על פעילות ופגישות במקום על הכנסה שנסגרה, אז הצוות ממקסם את הדבר הלא נכון","ICP שגוי, אז נציגים מבזבזים את הרבעון על קונים שלא היו קונים לעולם"]},
    {"h":"האבחון שאני מריץ קודם","p":["בשבוע הראשון אני מושך את המספרים האמיתיים: כיסוי פייפליין מול יעד, שיעור סגירה לפי שלב, גודל עסקה ממוצע ואורך מחזור, ואיפה עסקאות באמת מתות. זה אומר לי אם הבעיה היא בראש המשפך, בסינון באמצע, בסגירה המאוחרת, או ביעד שהיה דמיוני מההתחלה. רוב הזמן התשובה היא תערובת של מעט מדי פייפליין ושלבים חסרי משמעות, לא צוות שלא יודע למכור."]},
    {"h":"איך אני מתקן","p":["אני בונה מחדש את ייצור הפייפליין כך שיהיה מספיק נפח מסונן לעמוד במספר, מגדיר את השלבים עם קריטריוני כניסה ויציאה אמיתיים, ומריץ בדיקת עסקאות שבועית כך שעסקאות מקבלות עזרה בעוד יש זמן להציל אותן. אני מאמן מחדש את הנציגים שיכולים להשתפר, מחליף את מי שלא, ומאפס את היעד למשהו שקשור ליכולת אמיתית כדי שהצוות יוכל לנצח. אחר כך אני לוקח אחריות על המספר בזמן שהוא מתאושש, במקום למסור לכם דוח וללכת."]},
    {"h":"מה עולה ההמתנה","p":["כל רבעון שאתם מאשימים את הנציגים ומחליפים את ההרכב, אתם מאפסים את שעון הכניסה לקצב ומאבדים את הפייפליין שהעוזבים נשאו. הפספוס מצטבר: רבעון גרוע הופך לשנה גרועה, הדירקטוריון מאבד אמון בתחזית, ואתם בונים את כל המהלך מחדש בהמשך תחת יותר לחץ ופחות מזומן."]},
  ],
  "faqs":[
    {"q":"שאפטר נציגים שמפספסים יעד?","a":"בדרך כלל לא קודם. רוב הפספוסים חוזרים לפייפליין דק, סינון חלש או יעד בלי בסיס, לא למאמץ הנציגים. אבחנו את המהלך לפני שאתם מחליפים הרכב, אחרת תאפסו את שעון הכניסה לקצב ותאבדו את הפייפליין שלהם מול אותה בעיה."},
    {"q":"כמה פייפליין הצוות שלי צריך?","a":"מדד נפוץ הוא פי שלושה עד ארבעה מהיעד בפייפליין מסונן. מתחת לפי שלושה, המתמטיקה נגדכם ללא קשר לאיכות הנציגים. אם הכיסוי דק, התיקון הוא ייצור פייפליין, לא לחץ."},
    {"q":"כמה מהר אתה יכול להפוך צוות מפספס?","a":"אני מאבחן בשבוע הראשון ונותן לכם תוכנית ותחזית אמיתית בשבוע השני. תיקוני פייפליין ותהליך באים אחר כך, והיעד שאני מאפס הוא כזה שהצוות באמת יכול לעמוד בו, כך שההתאוששות אמיתית ולא עוד מספר מלא תקווה."}],
  "related":'חלק מ<a href="/he/how-to-build-a-sales-team">איך בונים ומרחיבים צוות מכירות</a>. ראו את <a href="/he/setting-sales-quotas">איך קובעים יעדי מכירות שאפשר לעמוד בהם</a>, <a href="/he/sales-forecast-always-wrong">למה התחזית תמיד שגויה</a>, <a href="/he/hired-reps-but-no-pipeline">גייסתם נציגים ואין פייפליין</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"sales-forecast-always-wrong",
  "title":"למה תחזית המכירות שלכם תמיד שגויה (ואיך מתקנים) | טל פאפרין",
  "desc":"אתם מתחייבים למספר מול הדירקטוריון, ואז מפספסים. שוב. הנה למה תחזית המכירות ממשיכה לפספס, והמשמעת שהופכת אותה לאמינה.",
  "h1":"למה תחזית המכירות שלכם תמיד שגויה","eyebrow":"מדריך",
  "lead":"אתם מתחייבים למספר מול הדירקטוריון, ואז מפספסים אותו בשליש. ברבעון הבא, אותו סיפור. תחזית שתמיד שגויה היא לא מזל רע. זה פייפליין שאי אפשר לסמוך עליו ותהליך שמרשה לכולם לנחש.",
  "sections":[
    {"h":"תחזית אמינה רק כמו הפייפליין שתחתיה","p":["תחזית היא לא תרגיל באקסל. היא טענה לגבי אילו עסקאות ייסגרו ומתי, והיא טובה רק כמו הפייפליין שהיא קוראת ממנו. אם הפייפליין מלא בעסקאות שאף אחד לא סינן, שלבים חסרי משמעות, והסתברויות שנציגים קובעים כדי להרגיש טוב, התחזית תפספס כל פעם. המספר מול הדירקטוריון הוא תוצאה של המשמעת ב-CRM."]},
    {"h":"למה המספר ממשיך לפספס","ul":["שלבים בלי קריטריוני כניסה ויציאה מתועדים, אז עסקה בשלב שלוש כי נציג הרגיש ככה, לא כי קרה משהו","נציגים קובעים את הסתברות הסגירה בעצמם, אז אופטימיות ואוזניים שומעות מה שנוח מנפחות את המספר","עסקאות שיושבות ללא מגע חודשים עדיין נספרות כחיות, ומנפחות את הפייפליין","CRM מיושן שאף אחד לא מעדכן, אז התחזית קוראת את המציאות של החודש שעבר","הסתברויות סגירה שמעולם לא כוילו מול היסטוריית הסגירות האמיתית שלכם","גיליון צדדי שלא מסכים עם ה-CRM, אז אין מקור אמת יחיד"]},
    {"h":"מה תחזית שאפשר לסמוך עליה באמת צריכה","p":["שלבים מוגדרים עם קריטריוני יציאה אמיתיים, כך שעסקה מתקדמת רק כשקרה משהו קונקרטי: דמו שבוצע, שגריר שאושר, תמחור שהוסכם, רכש שהתחיל. הסתברויות שמכוילות לאיך שהעסקאות שלכם באמת נסגרו, לא מספרים עגולים. בדיקת עסקאות שבועית שבה מישהו בכיר לוחץ על העסקאות האמיתיות וקורא אותן בכנות. ומקור אמת יחיד, ה-CRM, בלי גיליון צללים שרץ לצידו."]},
    {"h":"איך אני מתקן","p":["אני מגדיר את השלבים ואת קריטריוני היציאה, מנקה את המשקל המת מהפייפליין, ומכייל הסתברויות להיסטוריית הסגירות האמיתית שלכם. אחר כך אני מריץ בדיקת עסקאות שבועית וקורא את העסקאות בכנות, כולל אלה שהצוות רוצה להאמין בהן. תוך שבועיים יש לכם תחזית שמחזיקה, ואתם יכולים לגייס, להוציא ולדווח מולה בלי להיכוות."]},
    {"h":"מה עולה לכם תחזית שגויה","p":["תחזית שאי אפשר לסמוך עליה מרעילה כל החלטה שתלויה בה. אתם מגייסים לפני הכנסה שלא מגיעה, מתחייבים על מזומן מול עסקאות שמעולם לא היו אמיתיות, ומאבדים את אמון הדירקטוריון בכל מספר עתידי שתיתנו. ברגע שדירקטוריון מפסיק להאמין לתחזית שלכם, כל גיוס וכל תוכנית נהיים קשים יותר."]},
  ],
  "faqs":[
    {"q":"למה תחזית המכירות שלי תמיד גבוהה מדי?","a":"כמעט תמיד כי נציגים קובעים את ההסתברויות בעצמם ואף אחד לא בודק את העסקאות. אופטימיות ואוזניים נוחות מנפחות את המספר, עסקאות מתות נשארות בפייפליין, ולשלבים אין משמעות אמיתית. תקנו את קריטריוני השלבים והריצו בדיקה שבועית כנה והתחזית מתהדקת מהר."},
    {"q":"תחזית לא מדויקת היא בעיית CRM או בעיית מכירות?","a":"שתיהן, והן מזינות זו את זו. שלבים לא מוגדרים והסתברויות לא מכוילות הן בעיות קונפיגורציה; נציגים שקובעים את הסיכויים בעצמם ואף אחד שלא בודק עסקאות זו בעיית משמעת. חייבים לתקן את המערכת ואת ההרגל יחד, וזה בדיוק מה שאני עושה בשבועיים הראשונים."},
    {"q":"כמה מהר אתה יכול להפוך את התחזית לאמינה?","a":"אני מגדיר שלבים וקריטריוני יציאה ומנקה את הפייפליין בשבוע הראשון, ואז מריץ בדיקת עסקאות שבועית משם. תוך שבועיים התחזית משקפת עסקאות אמיתיות, והיא ממשיכה להתהדק ככל שההסתברויות המכוילות נבחנות מול סגירות אמיתיות."}],
  "related":'ראו את <a href="/he/services/fractional-cro">שירות ה-Fractional CRO</a>, <a href="/he/sales-team-missing-quota">צוות מכירות לא עומד ביעד</a>, <a href="/he/services/go-to-market-strategy">אסטרטגיית Go-To-Market</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"hired-reps-but-no-pipeline",
  "title":"גייסתם נציגי מכירות ואין פייפליין? הנה למה | טל פאפרין",
  "desc":"הוספתם כוח אדם למכירות והפייפליין עדיין לא גדל. הנה למה נציגים לא מייצרים פייפליין לבד, ואיך אני בונה את המהלך שכן.",
  "h1":"גייסתם נציגי מכירות ועדיין אין פייפליין","eyebrow":"מדריך",
  "lead":"כוח האדם עלה. הפייפליין לא. גייסתם נציגים בציפייה שפייפליין יבוא אחריהם, ואחרי כמה רבעונים הם נראים עסוקים וכלום לא במשפך. כוח אדם הוא לא מהלך, ונציגים לא יכולים לייצר מהלך שעדיין לא קיים.",
  "sections":[
    {"h":"כוח אדם הוא לא מהלך","p":["גיוס נציגים מרגיש כמו קניית פייפליין. זה לא. נציג יכול להריץ מהלך שכבר עובד, אבל כמעט אף אחד לא יכול להמציא אחד מאפס בחברה שרק הצטרף אליה. אם אתם מכניסים אנשים לכיסא בלי ICP, בלי מסר, בלי רשימת יעד ובלי מערכת אאוטבאונד, הם ימלאו את היום בפעילות ויפיקו כמעט אפס פייפליין. הפער הוא לא מאמץ. פשוט אין על מה המאמץ ירוץ."]},
    {"h":"למה הפייפליין נשאר ריק","ul":["גייסתם סוגרים וציפיתם שיעשו אאוטבאונד. רוב הסוגרים החזקים חלשים באאוטבאונד וצריכים שיגישו להם לידים","אין מערכת אאוטבאונד: אין רצפים, אין רשימת יעד, אין שיטה, אז כל נציג מאלתר ורובם עושים את זה גרוע","אין ICP חד, אז נציגים מתזים על פני שוק וכלום לא ממיר","SDR-ים שגויסו בלי playbook ובלי מאמן, נשארים לבד לפצח את המסר","אתם מודדים פעילות, שיחות ומיילים שנשלחו, במקום פייפליין מסונן שנוצר, אז עסוק נראה כמו התקדמות","אף אחד בכיר לא אחראי על המהלך, אז אין תפקיד אחד שבונה ומתקן את המנוע"]},
    {"h":"מה חייב להתקיים לפני שנציגים יכולים להפיק","p":["נציגים מפיקים פייפליין כשיש מהלך אמיתי להריץ: ICP חד, מסר שעובד על הקונה הזה, רשימת יעד בנויה, רצף אאוטבאונד שמקבל תשובות, שאלות סינון שממיינות אמיתי מנימוסי, ו-playbook מתועד כך שכל הדבר ניתן ללמידה. בנו את זה קודם ואותם נציגים שהסתובבו מתחילים למלא את המשפך. דלגו על זה ושום גיוס לא מתקן את המספר."]},
    {"h":"איך אני מתקן","p":["אני בונה את מהלך האאוטבאונד מה-ICP החוצה: למי לפנות, המסר, הרשימה, הרצף, הסינון. אני שם את האנשים הנכונים בכיסאות הנכונים, SDR-ים לפנייה ו-AE-ים לסגירה, ומאמן אותם על המהלך במקום להשאיר אותם לנחש. אחר כך אני בודק פייפליין שנוצר, לא פעילות, כך שאנחנו רואים מה באמת עובד ומכפילים עליו. אתם מקבלים משפך שמתמלא, בנוי בידי מי שעשה את זה מאפס יותר מפעם אחת."]},
    {"h":"מה עולה לחכות","p":["כל רבעון של עסוק-אבל-ריק הוא משכורת שהוצאה על נציגים שלומדים כלום שעובר הלאה, ומשפך שנשאר יבש בזמן שהדירקטוריון מחכה לצמיחה. ככל שזה נמשך, הגיוסים הטובים שלכם נשחקים על מהלך שבור ועוזבים, אז אתם משלמים לגייס, משלמים לחכות, ומשלמים שוב לבנות מחדש."]},
  ],
  "faqs":[
    {"q":"למה הנציגים החדשים שלי לא מייצרים פייפליין?","a":"בדרך כלל כי אין מהלך להריץ. אין ICP חד, אין מערכת אאוטבאונד, אין רשימת יעד, אין playbook. סוגרים חזקים במיוחד חלשים בפנייה וצריכים שיגישו להם פייפליין. בנו את המהלך קודם ואותם נציגים מתחילים להפיק."},
    {"q":"שאגייס עוד נציגים כדי לקבל יותר פייפליין?","a":"לא עד שקיים מהלך. הוספת כוח אדם למהלך שבור מכפילה את העלות בלי להכפיל את הפייפליין. בנו והוכיחו את מנוע האאוטבאונד, ואז גייסו מול משהו שכבר עובד כך שנציגים חדשים נכנסים לקצב על מערכת במקום לנחש."},
    {"q":"אני צריך SDR-ים או AE-ים כדי לתקן פייפליין ריק?","a":"לרוב את שניהם, בכיסאות הנכונים. SDR-ים פונים וקובעים פגישות, AE-ים סוגרים. הטעות הנפוצה היא לגייס סוגרים ולצפות שיפנו, או לגייס SDR-ים בלי playbook. אני שם את האנשים הנכונים בכיסאות הנכונים ומאמן אותם על מהלך בנוי."}],
  "related":'ראו את <a href="/he/services/fractional-cro">שירות ה-Fractional CRO</a>, <a href="/he/services/sales-team-building">בניית צוות מכירות</a>, <a href="/he/founder-led-sales-wont-scale">מכירות מבוססות-מייסד לא מתרחבות</a>, <a href="/he/go-to-market-motion">איך בוחרים את מהלך ה-GTM</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"how-to-build-a-sales-team",
  "title":"איך בונים ומרחיבים צוות מכירות B2B | טל פאפרין",
  "desc":"הסדר שהופך מכירות מבוססות-מייסד לצוות שעומד במספר: הוכיחו את המהלך, גייסו מנהיג, ואז נציגים, תגמול, יעדים ומשמעת פייפליין.",
  "h1":"איך בונים ומרחיבים צוות מכירות B2B","eyebrow":"מדריך",
  "lead":"רוב המייסדים בונים צוות מכירות בסדר הלא נכון. הם מגייסים נציגים קודם ומקווים שמהלך יופיע. הוא לא. הנה הסדר שבאמת עובד, מהעסקה הראשונה שסגרתם בעצמכם ועד צוות שעומד במספר בלי שאתם בכל שיחה. זה אותו רצף שאני מריץ כסמנכ״ל הכנסות במיקור חוץ.",
  "sections":[
    {"h":"כוח אדם הוא הצעד האחרון, לא הראשון","p":["גיוס נציגים מרגיש כמו קניית הכנסה. זה לא. נציג יכול להריץ מהלך מכירה שכבר עובד, אבל כמעט אף אחד לא יכול להמציא אחד בחברה שרק הצטרף אליה. הכניסו אנשים לכיסאות בלי ICP, בלי מסר ובלי תהליך, והם ימלאו את היום בפעילות בזמן שהפייפליין נשאר יבש. בנו את הצוות בסדר הלא נכון ותשרפו שנה והרבה משכורת כדי להוכיח שכוח אדם הוא לא מהלך. בנו אותו בסדר הנכון ואותם גיוסים מפיקים.","הסדר הנכון מתחיל ממה שכבר יש לכם: העסקאות שסגרתם בעצמכם. בהן טמונה הטיוטה הראשונה של המהלך שהצוות יריץ."]},
    {"h":"הסדר שעובד","tiers":["הוכיחו קודם את המהלך. פרקו את העסקאות האמיתיות שסגרתם: מי קנה, מה כאב, מה שכנע, והדרך משיחה ראשונה לחתימה. זה ה-playbook שלכם, מופק מעובדה במקום מומצא בחדר.","הוכיחו שאדם שאינו המייסד יכול להריץ אותו. סגרו עסקה או שתיים בידי מישהו שאינו אתם. אם רק המייסד סוגר, יש לכם כריזמה, לא מהלך.","גייסו מנהיג לפני ערימת נציגים. מישהו חייב להיות אחראי על המספר, לאמן את הרצפה ולתקן את המנוע. VP מכירות במשרה מלאה או כזה במיקור חוץ, אבל מישהו בכיר, לפני שאתם מרחיבים כוח אדם.","גייסו את נציגי המכירות הראשונים מול מהלך שעובד, כך שהם נכנסים לקצב על מערכת במקום לנחש.","קבעו תגמול שמשלם על ההתנהגות שאתם רוצים, ויעדים שבנויים מקיבולת אמיתית.","הריצו משמעת פייפליין ותחזית מההתחלה, כך שתראו אילו עסקאות אמיתיות לפני שהדירקטוריון שואל."]},
    {"h":"הגיוס הראשון הוא החלטה, לא משרה","p":["איש המכירות הראשון שתגייסו הוא הגיוס המסוכן ביותר שתעשו, כי אין צוות סביבו שיספוג פספוס. הטעות הנפוצה היא לגייס סוגר בכיר ולצפות שיבנה את המהלך ויפיק לעצמו את הפייפליין. רוב הסוגרים החזקים לא עושים אף אחד מהשניים. החליטו קודם מה אתם באמת צריכים: מישהו שיריץ מהלך שכבר הוכחתם, או מישהו שיעזור לכם להוכיח אותו. אלה אנשים שונים."]},
    {"h":"מנהיג לפני רצפה של נציגים","p":["נציגים בלי מנהיג לא מנהלים את עצמם אל תוך מספר. הם נסחפים. מנהיג מכירות אחראי על התחזית, בודק את העסקאות האמיתיות שבועית, מאמן את מי שיכול להשתפר ומחליף את מי שלא. אם אתם עדיין לא יכולים להצדיק VP מכירות במשרה מלאה, זה בדיוק הפער שמנהיג במיקור חוץ ממלא: בעלות בכירה עכשיו, בלי המשכורת המלאה, בזמן שהפונקציה עדיין קטנה מכדי לשאת אותה."]},
    {"h":"תגמול ויעדים הם ההגה","p":["ברגע שיש צוות, איך שאתם משלמים לו קובע איך הוא מתנהג. נציגים עושים בדיוק את מה שהתוכנית משלמת עליו, לא את מה שאמרתם בקיקאוף. כוונו נכון את פיצול הבסיס-למשתנה לפי תפקיד, קבעו OTE לפי השוק, ושמרו על התוכנית פשוטה מספיק שנציג יכול לחשב את הצ'ק שלו בעצמו. אחר כך קבעו יעדים מקיבולת אמיתית, לא ממספר הצמיחה שהדירקטוריון רוצה, כי יעד שאף אחד לא יכול לעמוד בו מדכא את הצוות ומסתיר מי באמת יודע למכור."]},
    {"h":"הסימנים שהרחבתם מוקדם מדי","ul":["נציגים עסוקים אבל הפייפליין לא גדל","רק המייסד יכול לסגור עסקה אמיתית","גייסתם סוגרים וציפיתם שיפנו","אף אחד בכיר לא אחראי על המספר ביום-יום","התגמול משלם על פעילות, אז הצוות מייעל עבור הדשבורד","התחזית היא ניחוש כי לשלבים אין משמעות"]},
    {"h":"העמיקו בכל חלק","links":[["כשמכירות מבוססות-מייסד מפסיקות להתרחב","/he/founder-led-sales-wont-scale"],["בניית צוות מכירות אחרי גיוס","/he/building-a-sales-team-after-funding"],["איך בונים תוכנית תגמול מכירות","/he/sales-compensation-plan"],["איך קובעים יעדי מכירות שאפשר לעמוד בהם","/he/setting-sales-quotas"],["כשהצוות לא עומד ביעד","/he/sales-team-missing-quota"],["גייסתם נציגים ואין פייפליין","/he/hired-reps-but-no-pipeline"],["שירות בניית צוות מכירות","/he/services/sales-team-building"]]},
    {"h":"איך אני בונה את זה","p":["אני נכנס כסמנכ״ל הכנסות או VP מכירות במיקור חוץ, מפיק את המהלך מהעסקאות האמיתיות שלכם, מגייס ומאמן את הצוות מולו, קובע את התגמול ואת היעדים, ולוקח אחריות על המספר בזמן שהצוות נכנס לקצב. אתם מקבלים הנהגת הכנסות בכירה בדיוק כשהלחץ לצמוח הכי גבוה, בלי להמר סבב על חיפוש ארוך למשרה מלאה. אם אתם מגייסים נציגים ומקווים, זו הבעיה שאני מתקן."]},
  ],
  "faqs":[
    {"q":"מה הסדר הנכון לבניית צוות מכירות?","a":"הוכיחו את המהלך מהעסקאות שסגרתם, הוכיחו שאדם שאינו המייסד יכול להריץ אותו, גייסו מנהיג שיהיה אחראי על המספר, אז הוסיפו נציגים מול מהלך שעובד, אז קבעו תגמול ויעדים והריצו משמעת פייפליין. כוח אדם הוא הצעד האחרון, לא הראשון."},
    {"q":"לגייס מנהיג מכירות או נציגים קודם?","a":"מנהיג, או כזה במיקור חוץ, לפני ערימת נציגים. נציגים בלי מישהו בכיר שאחראי על המספר, מאמן את הרצפה ובודק עסקאות נוטים להיסחף ולפספס. המנהיג בונה ומתקן את המנוע שהנציגים מריצים."},
    {"q":"מתי מייסדים צריכים להפסיק למכור ולבנות צוות?","a":"כשאתם היחידים שיכולים לסגור, ההכנסה חסומה בשעות שלכם, ועסקאות עדיין עוברות דרככם. זו התקרה. התיקון הוא להעביר את המהלך לצוות, לא להוסיף עוד מהזמן שלכם."},
    {"q":"האם סמנכ״ל הכנסות במיקור חוץ יכול לבנות את הצוות במקום גיוס במשרה מלאה?","a":"כן, ולרוב זה המהלך הנכון לפני שהפונקציה מצדיקה משכורת מלאה. סמנכ״ל הכנסות במיקור חוץ בונה את המהלך, מגייס ומאמן את הצוות, קובע תגמול ויעדים ולוקח אחריות על המספר, כך שאתם מקבלים הנהגה בכירה עכשיו בלי חיפוש ארוך."}],
  "related":'ראו את שירותי <a href="/he/services/sales-team-building">בניית צוות מכירות</a> ו<a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a>, אז העמיקו ב<a href="/he/sales-compensation-plan">תוכניות תגמול מכירות</a>, <a href="/he/setting-sales-quotas">קביעת יעדי מכירות</a>, <a href="/he/founder-led-sales-wont-scale">למה מכירות מבוססות-מייסד מפסיקות להתרחב</a> ו<a href="/he/building-a-sales-team-after-funding">בניית צוות אחרי גיוס</a>. או קראו <a href="/he/blog/scale-founder-led-to-team">איך להרחיב ממכירות מבוססות-מייסד לצוות</a>.'},

 {"slug":"sales-compensation-plan",
  "title":"איך בונים תוכנית תגמול מכירות | טל פאפרין",
  "desc":"נציגים עושים בדיוק את מה שאתם משלמים להם לעשות. איך לקבוע בסיס, משתנה, OTE ומכסה לפי תפקיד, לשמור על פשטות, ולהימנע מהטעויות שמתפוצצות.",
  "h1":"איך בונים תוכנית תגמול מכירות שעובדת","eyebrow":"מדריך",
  "lead":"תראו לי צוות מכירות שמתנהג מוזר ואני אראה לכם תוכנית תגמול שמשלמת לו להתנהג ככה. נציגים עושים בדיוק את מה שהתוכנית משלמת עליו, לא את מה שאתם אומרים בקיקאוף. אם ההתנהגות שגויה, התוכנית שגויה. הנה איך בונים אחת שמושכת לכיוון הנכון.",
  "sections":[
    {"h":"פצלו בסיס ומשתנה לפי תפקיד","p":["לא כל תפקיד צריך לשאת אותו סיכון. הפיצול תלוי בכמה שליטה יש לאדם על התוצאה. העמיסו משתנה על תפקיד שרק חלקית משפיע על התוצאה ואתם מענישים אנשים על דברים מחוץ לידיים שלהם."],
     "tiers":["SDR, בערך 70/30 בסיס למשתנה. הם יוצרים פייפליין אבל לא סוגרים, אז אי אפשר לתלות את כל השכר שלהם על מספר שהם רק חלקית שולטים בו. שלמו להם על פגישות מוכשרות ופייפליין שממיר, לא על פעילות גולמית.","AE, בערך 50/50, לפעמים 60/40. הם הבעלים של הסגירה, אז יותר מהשכר שלהם צריך להיות תלוי בה. זה התפקיד שבו המשתנה באמת נושך.","מנהיג מכירות, רובו בסיס עם רכיב קשור ליעד הצוות, כך שמשלמים לו לבנות ולאמן את כל הצוות, לא לאגור לעצמו את העסקאות הטובות."]},
    {"h":"קבעו OTE לפי השוק","p":["OTE, on-target earnings, הוא הסכום הכולל שנציג מרוויח ב-100 אחוז מהמכסה. זה המספר שמגייס ומשמר, אז עגנו אותו לשוק שלכם או שתאבדו אנשים לחברות שעשו את זה נכון. שלמו OTE בחסר והנציגים הכי טובים שלכם עוזבים ברגע שמישהו מציע להם מספר הוגן."]},
    {"h":"כוונו נכון את יחס המכסה ל-OTE","p":["הכלל הוותיק ביותר בתגמול מכירות הוא שנציג צריך לייצר פי שלוש עד חמש מהעלות הכוללת שלו בבוקינגס. AE עם OTE של 150 אלף נושא מכסה סביב 450 עד 750 אלף, מותאם למרווח, למחזור ולגודל העסקה. קבעו אותה נמוך מדי ואתם משלמים ביתר על בינוניות. קבעו אותה גבוה מדי והנציגים מחליטים שאי אפשר לעמוד בה ומפסיקים לנסות, וזה הכישלון היקר מכולם, כי צוות מדוכא עדיין מושך בסיס."]},
    {"h":"שלמו על תוצאות, ושמרו על פשטות","p":["עמלה על הכנסה שנסגרה, לא על שיחות או מיילים שנשלחו. ברגע שאתם משלמים על פעילות אתם מקבלים פעילות, נציגים שמייעלים עבור הדשבורד במקום עבור העסקה. שלמו על התוצאה ותנו להם למצוא את הדרך.","אחר כך שמרו על פשטות מספקת שנציג יכול לחשב את הצ'ק שלו בעצמו. זה המבחן שכמעט כל תוכנית נכשלת בו. אם נציג לא יכול לעשות את החשבון בראש אחרי שעסקה נסגרת, התוכנית מסובכת מדי מכדי להניע מישהו. מנוף אחד או שניים ברורים ושיעור שהם מכירים בעל פה עדיפים על עמוד של accelerators שאף אחד לא מבין."]},
    {"h":"הטעויות שמתפוצצות","ul":["הגבלת עמלה, כך שהנציג הכי טוב שלכם מפסיק למכור ביום שהוא מגיע לתקרה","שינוי התוכנית באמצע השנה כי מישהו מרוויח יותר מדי, וזו הדרך המהירה ביותר להרוג אמון","יותר מדי accelerators ותוספות שאף אחד לא מצליח לעקוב אחריהן","מכסות שנקבעו לפי מה שהדירקטוריון רוצה במקום לפי מה שהשוק תומך בו","תשלום על הכנסה שנרשמה בלי clawback כשהעסקה מתבטלת, כך שאתם מתגמלים חתימות שלא משלמות לעולם"]},
    {"h":"איפה זה משתלב","links":[["איך בונים ומרחיבים צוות מכירות","/he/how-to-build-a-sales-team"],["איך קובעים יעדי מכירות שאפשר לעמוד בהם","/he/setting-sales-quotas"],["שירות בניית צוות מכירות","/he/services/sales-team-building"]]},
  ],
  "faqs":[
    {"q":"מהו פיצול בסיס-למשתנה טוב לנציגי מכירות?","a":"זה תלוי בשליטה על התוצאה. SDR-ים סביב 70/30 בסיס למשתנה כי הם יוצרים פייפליין אבל לא סוגרים. AE-ים סביב 50/50, לפעמים 60/40, כי הם הבעלים של הסגירה. מנהיג מכירות רובו בסיס עם פרוסה קשורה ליעד הצוות."},
    {"q":"איך קובעים מכסה מול OTE?","a":"הכלל הנפוץ הוא שנציג צריך לייצר פי שלוש עד חמש מהעלות הכוללת שלו בבוקינגס. AE עם OTE של 150 אלף נושא מכסה של כ-450 עד 750 אלף, מותאם למרווח, למחזור ולגודל העסקה. נמוך מדי משלם ביתר על בינוניות, גבוה מדי זוכה להתעלמות."},
    {"q":"למה תוכנית התגמול שלי לא מניעה את הצוות?","a":"בדרך כלל כי היא משלמת על פעילות במקום על תוצאות, או שהיא מסובכת מדי מכדי שנציג יחשב את הצ'ק שלו. שלמו עמלה על הכנסה שנסגרה, שמרו על מנוף אחד או שניים ברורים, וקבעו OTE לפי השוק כך שהמספר שווה מרדף."},
    {"q":"האם כדאי להגביל עמלת מכירות?","a":"לא. תקרה אומרת לנציג הכי טוב שלכם להפסיק למכור ביום שהוא מגיע אליה, וזה ההפך ממה שאתם רוצים. עמלה בלי תקרה עם מכסה כנה שומרת על המובילים דוחפים כל השנה."}],
  "related":'חלק מ<a href="/he/how-to-build-a-sales-team">איך בונים ומרחיבים צוות מכירות</a>. ראו גם <a href="/he/setting-sales-quotas">קביעת יעדי מכירות</a>, את <a href="/he/services/sales-team-building">שירות בניית צוות המכירות</a>, או קראו <a href="/he/blog/sales-comp-plans-that-work">תוכניות תגמול מכירות שבאמת מניעות</a>.'},

 {"slug":"setting-sales-quotas",
  "title":"איך קובעים יעדי מכירות שעובדים | טל פאפרין",
  "desc":"יעד שאף אחד לא עומד בו מדכא את הצוות ומסתיר מי יודע למכור. איך לבנות יעדים מלמטה למעלה מקיבולת הנציג, התבססות ומתמטיקת פייפליין, לא ממשאלת דירקטוריון.",
  "h1":"איך קובעים יעדי מכירות שהצוות באמת יכול לעמוד בהם","eyebrow":"מדריך",
  "lead":"רוב היעדים הם בדיה. הדירקטוריון רוצה לשלש הכנסות, אז מספר הצמיחה מתחלק במספר הנציגים ומחולק כיעדים. אף אחד לא שאל אם נציג בודד, שעובד שנה מלאה, מסוגל לייצר את המספר הזה. זה לא יעד. זו משאלה עם שם עליה. הנה איך קובעים אחד שהצוות באמת יכול לעמוד בו.",
  "sections":[
    {"h":"יעד הוא טענה על קיבולת, לא משאלה","p":["כשאף אחד לא עומד במספר, כולם מפסידים. הנציגים מפסיקים להאמין בו, אז הם מפסיקים לנסות ומתחילים לנהל את התירוצים שלהם במקום. אתם מאבדים את הדבר היחיד שיעד אמור לתת לכם: סיגנל נקי על מי יודע למכור ומי לא. יעד שנקבע מפנטזיה לא אומר כלום, כי כולם מחטיאים אותו."]},
    {"h":"בונים מלמטה למעלה, לא מלמעלה למטה","p":["יעד אמיתי מתחיל ממה שנציג אחד באמת מסוגל לעשות. קחו את המספרים האמיתיים שלכם, לא את התקוות."],
     "ul":["עסקאות לנציג בשנה: כמה הנציגים הכי טובים שלכם באמת סגרו בשנה שעברה, לאורך השנה המלאה, לא הרבעון הטוב האחד","גודל עסקה ממוצע: ה-ACV האמיתי משוקלל לפי מה שנסגר, לא הלוויתן שחתמתם פעם אחת","זמן התבססות: נציג שנקלט ברבעון השני לא נושא מספר של שנה מלאה, אז חשבו יחסית או שאתם משקרים לעצמכם בתחזית"]},
    {"h":"מתמטיקת הכיסוי שמאחורי המספר","p":["יעד אומר משהו רק אם יש מספיק פייפליין להזין אותו. כלל האצבע הוא פי שלושה עד ארבעה מהיעד בפייפליין מסונן כדי שיהיה סיכוי אמיתי. מתחת לפי שלושה, המתמטיקה נגד הנציג לא משנה כמה הוא טוב. אז יעד הוא באמת שני מספרים: היעד, וכיסוי הפייפליין שהופך אותו לבר-השגה. קבעו את היעד והתעלמו מהכיסוי ואתם חזרה אצל משאלה."]},
    {"h":"הפער בין מספר הדירקטוריון למציאות הוא נתון","p":["כשהמספר מלמטה למעלה ומספר הדירקטוריון לא נפגשים, הפער הזה הוא הדבר הכי שימושי בעמוד. הוא אומר לכם בדיוק מה חייב להשתנות: יותר נציגים, ACV גבוה יותר, אחוז סגירה טוב יותר, מחזורים קצרים יותר, או תנועה אחרת. זו שיחת אסטרטגיה, לא גיליון שאתם מטייחים על ידי ניפוח יעדים אישיים. חברות שמסרבות לנהל אותה קובעות את המספר הבלתי אפשרי, מחטיאות, מאשימות את הנציגים, נוטשות אותם, וקובעות את אותו מספר שוב."]},
    {"h":"יעדי התבססות, כדי שגיוסים חדשים לא נידונים לכישלון","p":["נציג חדש שנושא מכסה מלאה מהיום הראשון הוא נציג שאתם מתכננים לאכזב. הדרגו את המכסה לאורך השניים או שלושה הרבעונים הראשונים בזמן שהוא לומד את המהלך ובונה פייפליין. מכסת התבססות מגינה על הגיוס, נותנת לכם קריאה כנה אם הוא בכיוון, ומונעת מהתחזית לספור הכנסה שלא היתה אמורה לנחות באותו רבעון."]},
    {"h":"איפה זה משתלב","links":[["איך בונים ומרחיבים צוות מכירות","/he/how-to-build-a-sales-team"],["איך בונים תוכנית תגמול מכירות","/he/sales-compensation-plan"],["שירות בניית צוות מכירות","/he/services/sales-team-building"]]},
  ],
  "faqs":[
    {"q":"איך קובעים יעד מכירות שבאמת אפשר לעמוד בו?","a":"בונים אותו מלמטה למעלה מקיבולת אמיתית של נציג אחד: עסקאות לנציג בשנה, גודל עסקה ממוצע וזמן התבססות. הכפילו עסקאות בגודל עסקה, הפחיתו עבור התבססות, ויש לכם את הרצפה הכנה. קבעו את היעד מעליה כדי שימתח, אבל בהישג ידו של נציג טוב בשנה טובה."},
    {"q":"כמה פייפליין צריך כדי לעמוד ביעד?","a":"מדד נפוץ הוא פי שלושה עד ארבעה מהיעד בפייפליין מסונן. מתחת לפי שלושה, המתמטיקה נגד הנציג ללא קשר לאיכותו. יעד הוא באמת שני מספרים: היעד והכיסוי שהופך אותו לבר-השגה."},
    {"q":"מה עושים כשמספר הדירקטוריון גבוה מהקיבולת?","a":"התייחסו לפער כאל נתון, לא כאל טעות עיגול. הוא אומר לכם מה חייב להשתנות: יותר נציגים, ACV גבוה יותר, אחוז סגירה טוב יותר או תנועה אחרת. זו החלטת אסטרטגיה, לא משהו שמתקנים בניפוח היעד של כל נציג ובתקווה."},
    {"q":"האם נציגים חדשים צריכים לשאת מכסה מלאה?","a":"לא. הדרגו את המכסה לאורך השניים או שלושה הרבעונים הראשונים בזמן שהם לומדים את המהלך ובונים פייפליין. מספר מלא מהיום הראשון דן את הגיוס לכישלון ומכניס לתחזית הכנסה שלא היתה אמורה לנחות."}],
  "related":'חלק מ<a href="/he/how-to-build-a-sales-team">איך בונים ומרחיבים צוות מכירות</a>. ראו גם <a href="/he/sales-compensation-plan">תוכניות תגמול מכירות</a>, <a href="/he/sales-team-missing-quota">כשהצוות לא עומד ביעד</a>, את <a href="/he/services/sales-team-building">שירות בניית צוות המכירות</a>, או קראו <a href="/he/blog/set-sales-quotas-you-can-hit">איך לקבוע יעדי מכירות שהצוות יכול לעמוד בהם</a>.'},

 {"slug":"fractional-cro-for-startups",
  "title":"Fractional CRO לסטארטאפים | טל פאפרין",
  "desc":"סמנכ״ל הכנסות במיקור חוץ לסטארטאפים: הנהגת הכנסות בכירה מההכנסה הראשונה ועד סבב B בלי משרה מלאה. התהליך, הצוות והתוצאות.",
  "h1":"Fractional CRO לסטארטאפים","eyebrow":"לסטארטאפים",
  "lead":"סטארטאפים צריכים הנהגת הכנסות בכירה לפני שהם יכולים להרשות אותה. את הפער הזה ממלא סמנכ״ל הכנסות במיקור חוץ: אני בונה את התהליך, מגייס את הצוות ולוקח אחריות על התוצאות, בלי משכורת מלאה.",
  "sections":[
    {"h":"למה סטארטאפים נתקעים על הכנסות","p":["רוב הסטארטאפים מקבלים את העסקאות הראשונות מהמייסדים ומהרשת, ואז נתקעים כי אין תהליך חוזר ואף אחד בכיר לא אחראי על התוצאות. גיוס CRO של 250,000 דולר מוקדם מדי שורף ראנוויי; גיוס נציגים זוטרים בלי מנהיג שורף זמן. סמנכ״ל הכנסות במיקור חוץ נותן לכם את הבעלים הבכיר עכשיו ובונה את המנוע שהנציגים יריצו."]},
    {"h":"מה אני בונה לסטארטאפ","ul":["ICP מאומת, מיצוב ותמחור לאיך שבאמת קונים מכם","תהליך אאוטבאונד ואינבאונד, ה-playbook, ה-CRM והפייפליין","הגיוסים הראשונים, מוכשרים ומנוהלים, ואת מי שצריך להחליף","תחזית אמיתית שהדירקטוריון יכול לסמוך עליה","המייסדים מחוץ לכל עסקה ובתוך הנכונות"]},
    {"h":"בנוי לסטארטאפים אמיתיים","p":["נכנסתי כ-VP מכירות במיקור חוץ מהיום הראשון, הגדרתי את ה-ICP, בניתי את תהליך האאוטבאונד מאפס ובניתי אותו מחדש דרך פיבוטים. אותה משמעת בין אם אתם בשלב מוקדם או סבב B: לקחת אחריות על התוצאות, לבנות את התהליך, לגרום לצוות לעמוד ביעד."]},
  ],
  "faqs":[
    {"q":"מתי סטארטאפ צריך לשכור Fractional CRO?","a":"כשהמייסדים עדיין היחידים שסוגרים, או כשאתם צריכים תהליך חוזר ותחזית לפני שאפשר להצדיק CRO במשרה מלאה. בדרך כלל מההכנסה הראשונה ועד סבב B."},
    {"q":"זה אפשרי כלכלית לסטארטאפ?","a":"כן, זו כל הנקודה. אתם מקבלים הנהגת הכנסות בכירה ב-2,000 עד 12,000 דולר בחודש, בחיוב חודשי, במקום משכורת מלאה של 250,000 דולר ומעלה פלוס אקוויטי."},
    {"q":"אתה באמת תעשה את העבודה או רק תייעץ?","a":"אני עושה את העבודה. אני מגייס, מכשיר ומנהל את הנציגים, לוקח אחריות על הפייפליין והתחזית, ונכנס לעסקאות הגדולות בעצמי, לא מגיש מצגת."}],
  "related":'ראו את שירותי <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a> ו<a href="/he/services/go-to-market-strategy">Go-To-Market</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"interim-cro",
  "title":"Interim CRO (סמנכ״ל הכנסות זמני) | טל פאפרין",
  "desc":"סמנכ״ל הכנסות זמני שלוקח אחריות על ההכנסות בתקופת מעבר, פער או היפוך מגמה. הנהגה בכירה בכיסא עכשיו, בידיים, בלי גיוס קבוע.",
  "h1":"Interim CRO","eyebrow":"מדריך",
  "lead":"כשאתם צריכים CRO בכיסא עכשיו, בתקופת פער, מעבר או היפוך מגמה, אני נכנס ולוקח אחריות על התוצאות בזמן שאתם מחליטים על הפתרון הקבוע.",
  "sections":[
    {"h":"מתי צריך Interim CRO","ul":["ה-CRO או VP המכירות שלכם עזב והתוצאות לא יכולות לחכות","אתם באמצע היפוך מגמה וצריכים הנהגה בכירה מיד","אתם בין סבבים או בתקופת מעבר וצריכים יד יציבה","אתם צריכים לייצב הכנסות בזמן שאתם מנהלים חיפוש למשרה מלאה"]},
    {"h":"מה אני עושה בכיסא","p":["אני לוקח אחריות על מערך ההכנסות מהיום הראשון: הצוות, הפייפליין, התחזית והעסקאות. שבוע ראשון זה אבחון, ואז אני מריץ את זה, שומר על הצוות פרודוקטיבי, מחזיק יחד את העסקאות המרכזיות, ומעביר מערך בריא יותר ממה שמצאתי, בין אם ל-CRO קבוע או חזרה אליכם."]},
    {"h":"זמני, במיקור חוץ, או שניהם","p":["זמני בדרך כלל אומר משרה מלאה או כמעט מלאה לתקופה מוגדרת. מיקור חוץ אומר חלק מהשבוע, באופן מתמשך. אני עושה את שניהם, והרבה פרויקטים מתחילים זמני במשבר ומתמסדים למיקור חוץ ברגע שהמערך יציב."]},
  ],
  "faqs":[
    {"q":"מה ההבדל בין Interim CRO ל-Fractional CRO?","a":"זמני בדרך כלל משרה מלאה לתקופה מוגדרת, לרוב לכיסוי פער או היפוך מגמה. מיקור חוץ הוא חלק מהשבוע באופן מתמשך. אני עושה את שניהם ולעיתים קרובות עובר מאחד לשני."},
    {"q":"כמה מהר אתה יכול להיכנס כ-Interim CRO?","a":"מהר. פרויקטים זמניים קיימים כי התוצאות לא יכולות לחכות, אז אני מאבחן בשבוע הראשון ומריץ את המערך מיד."},
    {"q":"אתה יכול להעביר ל-CRO קבוע?","a":"כן. חלק מפרויקט זמני הוא להשאיר מערך חזק ומתועד והעברה נקייה למי שלוקח את הכיסא לקבע."}],
  "related":'ראו את שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a> או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"fractional-vp-of-sales",
  "title":"VP מכירות במיקור חוץ (Fractional VP of Sales) | טל פאפרין",
  "desc":"VP מכירות במיקור חוץ שבונה ומריץ את צוות המכירות, ה-playbook והפייפליין, בידיים, בלי גיוס מלא.",
  "h1":"VP מכירות במיקור חוץ","eyebrow":"מדריך",
  "lead":"צריכים מישהו שיבנה את הצוות ויריץ את רצפת המכירות, לא רק יקבע אסטרטגיה? זה VP מכירות במיקור חוץ. אני מגייס, מכשיר ומנהל את הנציגים ולוקח אחריות על הפייפליין, במשרה חלקית.",
  "sections":[
    {"h":"VP מכירות במיקור חוץ מול Fractional CRO","p":["VP מכירות מריץ את צוות המכירות ואת הפייפליין יום-יום. CRO אחראי על כל ההכנסות, מכירות, שיווק ו-Go-To-Market, ועל התוצאות עצמן. אני עושה את שניהם; התפקיד הנכון תלוי אם אתם צריכים שיריצו את רצפת המכירות או שייקחו אחריות על כל מערך ההכנסות. הרבה חברות מתחילות עם VP מכירות במיקור חוץ ומגדילות את ההיקף ל-CRO."]},
    {"h":"מה באחריותי כ-VP מכירות במיקור חוץ","ul":["גיוס, הכשרה וניהול של SDR, AE ו-BD","ה-playbook, התסריטים ותהליך המכירה","ה-CRM, הפייפליין והתחזית","אימון נציגים ליעד והחלפת מי שלא יכול","ניהול יומיומי של רצפת המכירות"]},
    {"h":"בניתי את הצוות, הרבה פעמים","p":["גייסתי, הכשרתי וניהלתי צוותי מכירות בחמש יבשות וביותר מ-40 מדינות, מנציגים ראשונים ועד רצפות מלאות עם SDR, AE, פוסט-סייל ותמיכה טכנית. אני גורם לצוות שיש לכם לעמוד ביעד ובונה את הצוות שעוד אין לכם."]},
  ],
  "faqs":[
    {"q":"מה עושה VP מכירות במיקור חוץ?","a":"בונה ומריץ את צוות המכירות והפייפליין במשרה חלקית: גיוס, הכשרה וניהול נציגים, אחריות על ה-playbook, ה-CRM והתחזית, ואימון הצוות ליעד."},
    {"q":"VP מכירות במיקור חוץ או Fractional CRO?","a":"בחרו VP מכירות כדי להריץ את צוות המכירות והפייפליין. בחרו CRO כדי לקחת אחריות על כל ההכנסות כולל שיווק ו-Go-To-Market. אני עושה את שניהם ויכול להגדיל את ההיקף ככל שאתם גדלים."},
    {"q":"כמה עולה VP מכירות במיקור חוץ?","a":"בדרך כלל 2,000 עד 12,000 דולר בחודש לפי שעות, בחיוב חודשי בלי נעילה, הרבה מתחת למשכורת VP מלאה."}],
  "related":'ראו את שירותי <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות</a> ו<a href="/he/services/sales-team-building">בניית צוות</a>, או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"fractional-chief-sales-officer",
  "title":"סמנכ״ל מכירות ראשי במיקור חוץ (Fractional CSO) | טל פאפרין",
  "desc":"סמנכ״ל מכירות ראשי במיקור חוץ שלוקח אחריות על ארגון המכירות, האסטרטגיה והתוצאות, בידיים, בלי משכורת בכירה מלאה.",
  "h1":"סמנכ״ל מכירות ראשי במיקור חוץ","eyebrow":"מדריך",
  "lead":"סמנכ״ל מכירות ראשי במיקור חוץ לוקח אחריות על ארגון המכירות מקצה לקצה, אסטרטגיה, מבנה, צוות ותוצאות, לחלק מהשבוע שאתם צריכים, בלי גיוס בכיר מלא.",
  "sections":[
    {"h":"על מה אחראי CSO במיקור חוץ","ul":["אסטרטגיית מכירות, מבנה ועיצוב סגמנטים או טריטוריות","שכבת ההנהגה וצוות המכירות שתחתיה","תוכניות עמלות, יעדים, ה-playbook והתהליך","הפייפליין, התחזית והתוצאות","גיוס, אימון וההחלטות הקשות על כוח אדם"]},
    {"h":"CSO, CRO או VP מכירות","p":["סמנכ״ל מכירות ראשי אחראי על ארגון המכירות. CRO אחראי על כל ההכנסות כולל שיווק ו-Go-To-Market. VP מכירות מריץ את הצוות יום-יום. התוויות פחות חשובות מהעבודה; ספרו לי איפה ההכנסות תקועות ואני אקח את ההיקף הנכון."]},
    {"h":"בכיר, בידיים, מוכח","p":["הובלתי כ-VP מכירות גלובלי ובינלאומי ונכנסתי כמנהיג הכנסות במיקור חוץ ל-30 חברות B2B ומעלה. אני לא מייעץ מהצד; אני לוקח אחריות על האסטרטגיה ואז מריץ אותה, בידיים."]},
  ],
  "faqs":[
    {"q":"מה זה סמנכ״ל מכירות ראשי במיקור חוץ?","a":"מנהל מכירות בכיר שלוקח אחריות על ארגון המכירות שלכם, האסטרטגיה, הצוות והתוצאות במשרה חלקית, בלי משכורת CSO מלאה או נעילה ארוכה."},
    {"q":"במה CSO שונה מ-CRO?","a":"CSO אחראי על ארגון המכירות. CRO אחראי על כל ההכנסות, כולל שיווק ו-Go-To-Market. אני לוקח כל אחד מהם לפי מה שצריך שיהיה באחריות."},
    {"q":"כמה זה עולה?","a":"בדרך כלל 2,000 עד 12,000 דולר בחודש לפי מעורבות, בחיוב חודשי בלי נעילה."}],
  "related":'ראו את שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a> או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"fractional-cro-roi",
  "title":"האם Fractional CRO שווה את זה? ה-ROI | טל פאפרין",
  "desc":"התיק העסקי לסמנכ״ל הכנסות במיקור חוץ: כמה זה עולה, מה זה מחזיר, ואיך זה מול גיוס מלא או לא לעשות כלום.",
  "h1":"האם Fractional CRO שווה את זה?","eyebrow":"מדריך",
  "lead":"סמנכ״ל הכנסות במיקור חוץ הוא לא עלות, הוא הימור על התוצאות. הנה התיק העסקי הכן: כמה אתם משלמים, מה זה מחזיר, ומה עולה לא לעשות כלום.",
  "sections":[
    {"h":"כמה אתם משלמים","p":["בערך 2,000 עד 12,000 דולר בחודש לפי כמה מהשבוע אתם צריכים, בחיוב חודשי בלי חוזה ארוך. בלי אקוויטי, בלי בונוס, בלי סיכון פיצויים, בלי דמי גיוס, בלי התברגות."]},
    {"h":"מה זה מחזיר","p":["תהליך חוזר, תחזית אמיתית, צוות שעומד ביעד ובעלות בכירה על התוצאות, בשבועות במקום ברבעונים. ההחזר הוא לא הריטיינר שחסכתם; הוא ההכנסה שאתם מפסיקים להשאיר על השולחן כי אף אחד בכיר לא היה אחראי על הפייפליין."]},
    {"h":"העלות של החלופות","ul":["CRO במשרה מלאה: 250,000 דולר ומעלה בסך הכל, חודשים לגייס ולהתברג, וסיכון פיצויים אמיתי אם ההתאמה שגויה","גיוס VP שגוי: שש ספרות ושנה שאבדה","לא לעשות כלום: הכנסות תקועות שכמעט אף פעם לא מתקנות את עצמן"]},
  ],
  "faqs":[
    {"q":"האם Fractional CRO שווה את הכסף?","a":"אם ההכנסות תקועות ואף אחד בכיר לא אחראי על התוצאות, כן. אתם מקבלים הנהגה ברמת CRO בשבריר ממשכורת מלאה, בחיוב חודשי, כך שזה חייב להמשיך להרוויח את החידוש."},
    {"q":"איך מודדים את ההחזר?","a":"פייפליין שנבנה, דיוק התחזית, אחוז סגירה, זמן התברגות של נציגים והתוצאות עצמן. אני אחראי על תחזית שאני נמדד עליה, לא על פעילות ראווה."},
    {"q":"ומה אם זה לא עובד?","a":"הפרויקטים חודשיים בלי נעילה. אם אני לא מספק, מסיימים בסוף החודש. זו כל הנקודה של מיקור חוץ."}],
  "related":'השוו את <a href="/he/fractional-cro-cost">העלות</a> ו<a href="/he/fractional-cro-vs-vp-of-sales">CRO מול VP מכירות</a>, או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"outsourced-cro",
  "title":"סמנכ״ל הכנסות במיקור חוץ (Outsourced CRO) | טל פאפרין",
  "desc":"סמנכ״ל הכנסות במיקור חוץ שלוקח אחריות על מערך ההכנסות מחוץ למצבת כוח האדם: אסטרטגיה, צוות, פייפליין ותוצאות, בלי גיוס מלא.",
  "h1":"סמנכ״ל הכנסות במיקור חוץ","eyebrow":"מדריך",
  "lead":"הוציאו למיקור חוץ את הנהגת ההכנסות עצמה. אני לוקח אחריות על האסטרטגיה, הצוות, הפייפליין והתוצאות מחוץ למצבת כוח האדם: איש הביצוע הבכיר שאתם צריכים בלי גיוס מלא.",
  "sections":[
    {"h":"Outsourced CRO, Fractional CRO, אותו רעיון","p":["סמנכ״ל הכנסות במיקור חוץ, fractional CRO ו-part-time CRO מתארים את אותו דבר: הנהגת הכנסות בכירה שמביאים מבחוץ במקום לגייס למשרה מלאה. אתם מקבלים מישהו שכבר הריץ את הפונקציה, אחראי על התוצאות, לחלק מהשבוע שאתם צריכים ולחודשים שאתם צריכים."]},
    {"h":"על מה אני אחראי","ul":["אסטרטגיית הכנסות, התחזית והאחריות","תהליך ה-Go-To-Market, הפייפליין והצוות שמריץ אותו","גיוס, הכשרה וההחלטות הקשות על מי נשאר","שיווק שמזין פייפליין, לא רק פעילות","התוצאות עצמן, מקצה לקצה"]},
    {"h":"למה להוציא את זה למיקור חוץ","p":["CRO במשרה מלאה עולה 250,000 דולר ומעלה בסך הכל, לוקח חודשים לגייס ולהתברג, ונושא סיכון פיצויים אמיתי. מיקור חוץ של התפקיד נותן לכם את אותה בעלות בכירה בשבועות, בחיוב חודשי, בלי נעילה. כשהפונקציה גדולה מספיק כדי להצדיק גיוס מלא, אני עוזר לכם לעשות אותו ולהעביר."]},
  ],
  "faqs":[
    {"q":"מה זה סמנכ״ל הכנסות במיקור חוץ?","a":"מנהיג הכנסות בכיר שלוקח אחריות על מערך המכירות וההכנסות מחוץ למצבת כוח האדם, במשרה חלקית ובתנאים חודשיים, במקום גיוס CRO מלא. זהה ל-fractional CRO."},
    {"q":"במה זה שונה מיועץ?","a":"יועץ מייעץ. סמנכ״ל הכנסות במיקור חוץ לוקח אחריות על העבודה, על הפייפליין ועל התוצאות, ועונה על התוצאה."},
    {"q":"כמה עולה סמנכ״ל הכנסות במיקור חוץ?","a":"בדרך כלל 2,000 עד 12,000 דולר בחודש לפי מעורבות, בחיוב חודשי בלי נעילה, הרבה מתחת ל-CRO מלא."}],
  "related":'ראו <a href="/he/how-to-hire-a-fractional-cro">איך לשכור אחד</a> ואת שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות</a>, או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"tal-paperin-podcasts-and-press",
  "title":"טל פאפרין: פודקאסטים, ראיונות ופאנלים",
  "desc":"טל פאפרין על הליכה לשוק, מכירות B2B והכנסות: מבחר פודקאסטים, ראיונות ופאנלים, במילים שלו.",
  "h1":"טל פאפרין: פודקאסטים, ראיונות ופאנלים","eyebrow":"בתקשורת",
  "lead":"איפה דיברתי על הליכה לשוק, מכירות והכנסות בפומבי. פודקאסטים, ראיונות ופאנלים, לטובת מייסדים ומנכ״לים.",
  "sections":[
    {"h":"על מה אני מדבר","p":["אותם דברים שאני עושה ללקוחות: למה מכירות מבוססות-מייסד נתקעות, איך בונים מהלך הליכה לשוק שמתרחב, מה באמת השתנה במכירת SaaS, ואיך הופכים גיוס להכנסה. ישיר, דעתן, לטובת מייסדים ומובילי הכנסות."]},
    {"h":"מבחר הופעות","p":["דוגמה להופעות ופאנלים אחרונים למטה. לפודקאסט, פאנל או הרצאה, צרו קשר ואמצא את הזמן."]},
  ],
  "faqs":[
    {"q":"האם טל פאפרין זמין לפודקאסטים ופאנלים?","a":"כן. אני מצטרף באופן קבוע לפודקאסטים, ראיונות ופאנלים בכנסים על הליכה לשוק, מכירות B2B, הכנסות והרחבת מכירות מבוססות-מייסד. צרו קשר עם הפרטים ואמצא את הזמן."},
    {"q":"על מה טל פאפרין מדבר?","a":"אסטרטגיית הליכה לשוק, בנייה והרחבה של צוותי מכירות B2B, למה מכירות מבוססות-מייסד נתקעות, מה השתנה במכירת SaaS, והפיכת גיוס להכנסה. פרקטי וישיר, למייסדים ומובילי הכנסות."}],
  "related":'<p>מבחר הופעות:</p><ul><li><a href="https://podcasts.apple.com/us/podcast/tal-paperin-ai-didnt-kill-saas-it-killed-lazy-sales-motion/id1812655142?i=1000750906146" target="_blank" rel="noopener">The Sales Strategist Podcast: "AI didn\'t kill SaaS, it killed lazy sales motion"</a> (<a href="https://open.spotify.com/episode/4GXV4h6wxRCVWXoyDzwynA" target="_blank" rel="noopener">Spotify</a>)</li><li><a href="https://marcuscauchi.podbean.com/e/success-comes-through-people-who-plan-execute-and-adapt-not-those-who-talk-about-it/" target="_blank" rel="noopener">TheInquisitor with Marcus Cauchi: "Success Comes To People Who Plan, Execute and Adapt"</a></li><li><a href="https://goodpods.com/podcasts/ask-win-114648/tal-paperin-part-2-5875148" target="_blank" rel="noopener">Ask Win: Tal Paperin (Part 2)</a></li><li><a href="https://davosinthedesert.us/israeli-technology-conference-speaker-podcasts/" target="_blank" rel="noopener">Davos in the Desert: Israeli Technology Conference panel</a></li></ul><p>עוד ראיונות והופעות:</p><ul><li>Solution Nation Podcast: "Investing in Israeli IIoT Companies" (2022)</li><li>The Business Blast Podcast עם Tyler Wagner (2018)</li><li>The Daily Sales עם Daniel Disney, על מכירה חברתית (2018)</li><li>CEO Money עם Michael Yorba (2018)</li><li>The Hard Corps Marketing Show: "Global Sales Fundamentals" (2018)</li><li>The Bob Low Show: "How to Penetrate New Markets" (2018)</li></ul><p>בנוסף: "An Introduction to Sales in the 21st Century", הספר הדיגיטלי של טל פאפרין על מכירות B2B.</p><p><a href="/he/contact">רוצים אותי בשואו או בפאנל? צרו קשר.</a></p>'},

 {"slug":"b2b-go-to-market-strategy",
  "title":"אסטרטגיית Go-To-Market ל-B2B: המדריך של מפעיל | טל פאפרין",
  "desc":"אסטרטגיית הליכה לשוק שאפשר להריץ, לא להגניז. חמשת החלקים של GTM אמיתי ל-B2B, הסדר לבנות אותם, והטעויות ששורפות את התקציב.",
  "h1":"אסטרטגיית Go-To-Market ל-B2B, בנויה בידי מי שמריץ אותה","eyebrow":"מדריך",
  "lead":"רוב אסטרטגיות ה-GTM הן מצגת שנפתחת פעם אחת ולא שוב. אסטרטגיה אמיתית היא מנוע שמריצים כל שבוע. הנה חמשת החלקים, הסדר שבו הם באים, ואיך שומרים אותם חיים עד שהם מייצרים פייפליין. זה אותו רצף שאני מפעיל ב-90 הימים הראשונים אצל לקוח.",
  "sections":[
    {"h":"אסטרטגיית GTM היא תוכנית להפוך מוצר ללקוחות משלמים","p":[
      "כשמורידים את הבאזז, הליכה לשוק היא ארבע שאלות עם תשובות אמיתיות: למי אתם מוכרים, מה אתם אומרים להם, דרך איזה ערוץ, ובאיזה תהליך. מוסיפים את המספר שאתם מצפים שזה ייצר ויש לכם אסטרטגיה. משאירים אחת מהן מעורפלת, וכל איש מכירות מאלתר, כל דולר שיווק מצביע לכיוון אחר, ואי אפשר להבחין בין בעיית ערוץ לבעיית מסר.",
      "פתחתי את ארצות הברית, אירופה, מזרח אירופה ו-APAC לחברות B2B, ישירות ודרך ערוצים. לאלה שהתרחבו היו תשובות כתובות ובדוקות לשאלות האלה. לאלה ששרפו שנה היו מוצר ותקווה."]},
    {"h":"חמשת החלקים, לפי סדר החשיבות","tiers":[
      "פרופיל לקוח אידיאלי. לא \"חברות B2B\" אלא פרופיל חד: גודל חברה, תעשייה, תפקיד מקבל ההחלטה, והכאב הספציפי שהוא מרגיש. כל חלק שבא אחריו נעשה קל יותר ככל שזה חד יותר, וקשה יותר אם מדלגים עליו.",
      "מיצוב ומסר. הסיבה שהקונה הזה צריך אתכם, במילים שלו, קשורה לתוצאה עסקית שכבר אכפת לו ממנה. אותו מוצר, מסר שונה לכל פרסונה. כאן רוב ה-GTM נכשל בשקט.",
      "מהלך וערוץ. איך אתם באמת מגיעים אליהם: אאוטבאונד, אינבאונד, מוצר-מוביל, שותפים, אירועים. התמהיל תלוי בנקודת המחיר, בקונה ובשלב שלכם, לא במה שבאופנה.",
      "תהליך מכירה. הדרך ממגע ראשון לחתימה: השלבים, מי מעורב, כמה זמן לוקח כל שלב, ומה מקדם עסקה. בלי תהליך מוגדר אין תחזית ואין דרך להשתפר.",
      "תחזית. מספר עם אבני דרך והחשבון שמאחוריו, לא תקווה. אם אתם לא יכולים להראות את הפייפליין שמייצר את המספר, אין לכם תחזית, יש לכם משאלה."]},
    {"h":"בונים אותם ברצף, לא הכול בבת אחת","p":[
      "הסדר הוא לא קישוט. מסר מצוין שמכוון ללקוח הלא נכון עדיין מחטיא. ערוץ מושלם שנושא מסר חלש עדיין שורף כסף. קבעו קודם את ה-ICP, אז כתבו את המסר ל-ICP הזה, אז בחרו את המהלך שמגיע אליהם, אז בנו את התהליך, ואז חזו מה התהליך מייצר.",
      "צוותים עושים את זה הפוך כל הזמן. הם קונים כלי אאוטבאונד ומגייסים SDR לפני שמישהו הגדיר למי להתקשר ומה לומר. הכלי עובד מצוין. האסטרטגיה שמתחתיו פשוט לא קיימת."]},
    {"h":"מתחילים מעסקה אחת שנסגרה, לא מדף ריק","p":[
      "לא ממציאים GTM בחדר ישיבות. מחלצים אותו מעסקה אמיתית. קחו את הלקוח האחרון שסגרתם, או הקרוב ביותר לסגירה, וחפרו: למה הם קנו, מה כאב להם לפני, מה שכנע אותם, ואיך הדרך באמת נראתה. עסקה אחת כנה נותנת לכם טיוטה ראשונה של כל חמשת החלקים. אז בודקים אם זה חוזר על עצמו. כך בונים מנוע מתוך עובדה ולא מתוך הנחה."]},
    {"h":"הטעויות ששורפות את התקציב","ul":[
      "מכירה לפני שה-ICP מוגדר, כך שלומדים את הלקחים הלא נכונים מהקונים הלא נכונים",
      "מסר שמתאר את המוצר במקום את התוצאה של הקונה",
      "העתקת מהלך של חברה אחרת כשנקודת המחיר והקונה שלכם שונים",
      "התייחסות ל-GTM כמסמך שצריך לסיים במקום כמנוע שצריך להריץ ולתקן",
      "תחזית מתוך תחושת בטן כי תהליך מכירה מעולם לא הוגדר"]},
    {"h":"להעמיק בכל חלק","links":[
      ["מיצוב ומסר ל-B2B", "/he/b2b-positioning-and-messaging"],
      ["איך בוחרים את מהלך ההליכה לשוק", "/he/go-to-market-motion"],
      ["שירות אסטרטגיית Go-To-Market", "/he/services/go-to-market-strategy"]]},
    {"h":"אסטרטגיה שנשארת על השקף חסרת ערך","p":[
      "המצגת היא החלק הקל. להריץ אותה זו העבודה. אני בונה את ה-GTM אתכם, ואז מוביל את הביצוע עד שיש פייפליין, שותפים ומכירות ראשונות, תוך תיקון התוכנית מול מה שהשוק באמת עושה. אם אתם מוכרים בלי GTM ברור, או עם כזה שלא עובד, זו העבודה שאני עושה."]},
  ],
  "faqs":[
    {"q":"מה זה אסטרטגיית Go-To-Market ל-B2B?","a":"זו התוכנית הקונקרטית להפוך את המוצר ללקוחות משלמים: למי מוכרים, מה אומרים, דרך איזה ערוץ, באיזה תהליך, ומה המספר שמצפים שזה ייצר. כתוב ובדוק, לא מונח."},
    {"q":"מהם החלקים של אסטרטגיית GTM?","a":"חמישה: פרופיל לקוח אידיאלי חד, מיצוב ומסר, מהלך המכירה והערוץ, תהליך מכירה מוגדר, ותחזית עם החשבון שמאחוריה. בונים אותם בסדר הזה, כי כל אחד תלוי בקודמו."},
    {"q":"מאיפה מתחילים לבנות GTM?","a":"מעסקה אמיתית אחת, לא מדף ריק. קחו את הלקוח האחרון שסגרתם ובדקו למה קנו, מה כאב, מה שכנע ואיך העסקה זזה. זה נותן טיוטה ראשונה של כל חמשת החלקים, שאותה בודקים אם היא חוזרת."},
    {"q":"האם אני צריך אסטרטגיית GTM אם אני כבר מוכר?","a":"אם המכירה לא עקבית, איטית או לא ניתנת לחיזוי, אתם מוכרים בלי GTM עובד גם אם עסקאות נסגרות מדי פעם. אסטרטגיה מוגדרת היא מה שמאפשר להבחין בין בעיית ערוץ לבעיית מסר ולתקן את הנכונה."},
    {"q":"אתה יכול לבנות את ה-GTM וגם לעזור להריץ אותו?","a":"כן. אני בונה את האסטרטגיה אתכם ואז מוביל את הביצוע עד שיש פייפליין, שותפים ומכירות ראשונות. אני לא עוצר במצגת, כי המצגת היא החלק שלא מוכר."}],
  "related":'ראו את <a href="/he/services/go-to-market-strategy">שירות אסטרטגיית ה-GTM</a>, העמיקו ב<a href="/he/b2b-positioning-and-messaging">מיצוב ומסר</a> וב<a href="/he/go-to-market-motion">בחירת מהלך ה-GTM</a>, או קראו <a href="/he/blog/go-to-market-israeli-startup">אסטרטגיית GTM לסטארטאפ שמוכר בחו״ל</a> ו<a href="/he/blog/ideal-customer-profile-icp">איך מגדירים ICP שממיר</a>. אם חלק התחזית ממשיך לפספס, ראו <a href="/he/sales-forecast-always-wrong">למה תחזית המכירות תמיד שגויה</a>.'},

 {"slug":"b2b-positioning-and-messaging",
  "title":"מיצוב ומסר ל-B2B שמנצחים עסקאות | טל פאפרין",
  "desc":"מיצוב הוא הסיבה שקונה בוחר בכם ולא בלהישאר כמו שהם. איך בונים מיצוב ומסר ל-B2B שמוכרים את התוצאה, לא את רשימת הפיצ׳רים.",
  "h1":"מיצוב ומסר ל-B2B שגורמים לקונים לבחור בכם","eyebrow":"מדריך",
  "lead":"רוב המסרים ב-B2B מתארים את המוצר. לקונים לא אכפת מהמוצר שלכם. אכפת להם מהבעיה שהוא מסיים ומהתוצאה שהם מקבלים. הנה איך ממצבים מוצר B2B כך שהקונה הנכון רואה את עצמו בו ובוחר בכם במקום לא לעשות כלום.",
  "sections":[
    {"h":"מיצוב הוא המסגרת, מסר הוא המילים","p":[
      "מיצוב הוא ההחלטה באיזו קטגוריה אתם, למי אתם, ולמה אתם מנצחים את החלופה, כולל החלופה לא לשנות כלום. מסר הוא איך אומרים את זה בשפה שהקונה כבר משתמש בה. אם המיצוב שגוי, שום קופירייטינג חכם לא יציל. אם הוא נכון, המילים כמעט כותבות את עצמן.",
      "המתחרה האמיתי שלכם הוא לרוב לא הספק האחר. הוא הסטטוס קוו: הגיליון, המתמחה, התהליך שהם כבר סובלים. מצבו מול זה והשיחה משתנה."]},
    {"h":"מוכרים את התוצאה, לא את הפיצ׳ר","p":[
      "פיצ׳ר הוא מה שהמוצר עושה. תוצאה היא מה שהקונה מקבל: זמן שחוזר, סיכון שיורד, הכנסה שנוספת, מספר שהוא נמדד עליו שזז לכיוון הנכון. קונים מאשרים תקציב על תוצאות, לא על פיצ׳רים. אותה רשימת פיצ׳רים, ממוסגרת כתוצאה שאכפת לקונה מסוים ממנה, היא ההבדל בין דמו שנוחת לבין דמו שמקבל 'לא' מנומס.",
      "לכן מיצוב מתחיל מהקונה, לא מהרואדמאפ. אם אתם לא יכולים לנסח את התוצאה במילים של הקונה, יש לכם רשימת פיצ׳רים, לא מסר."]},
    {"h":"מוצר אחד, מסר שונה לכל פרסונה","p":[
      "סמנכ״ל הכספים, המשתמש הסופי וראש המחלקה קונים את אותו מוצר מסיבות שונות. הכספים רוצה שהעלות והסיכון יירדו. המשתמש רוצה שהיום שלו יהיה קל יותר. ראש המחלקה רוצה שהמספר שהוא מדווח עליו יזוז. אותו מוצר, שלושה מסרים. מסר אחד לכולם זה מסר שלא משכנע אף אחד עד הסוף."]},
    {"h":"איך בונים את זה","ul":[
      "התחילו מה-ICP החד ביותר, כי ממצבים לקונה ספציפי ולא לכולם",
      "נקבו בסטטוס קוו שהם חיים בו היום ולמה הוא עולה להם בשקט",
      "נסחו את התוצאה שהם מקבלים בשפה שלהם, עם לפני ואחרי קונקרטיים",
      "בחרו את הטענה האחת שאתם יכולים להוכיח והובילו איתה, במקום עשר שאתם רק מצהירים",
      "בדקו כל שורה מול קונה אמיתי, ואז מחקו כל מה שהוא מדלג עליו"]},
    {"h":"איך יודעים שזה עובד","p":[
      "מיצוב טוב מופיע במחזור המכירה, לא בסקר מותג. עסקאות זזות מהר יותר כי מבזבזים פחות זמן על הסבר מי אתם. שיחות גילוי נפתחות בכך שהקונה מתאר לכם בחזרה את הכאב שלו. ההנחות יורדות, כי כבר לא משווים אתכם פיצ׳ר מול פיצ׳ר לכלי זול יותר. אם כלום מזה לא קורה, המיצוב הוא הדבר לתקן לפני שמוציאים עוד דולר על פנייה."]},
    {"h":"איפה זה משתלב","links":[
      ["אסטרטגיית ה-GTM המלאה", "/he/b2b-go-to-market-strategy"],
      ["איך בוחרים את מהלך ההליכה לשוק", "/he/go-to-market-motion"],
      ["שירות אסטרטגיית Go-To-Market", "/he/services/go-to-market-strategy"]]},
  ],
  "faqs":[
    {"q":"מה ההבדל בין מיצוב למסר?","a":"מיצוב הוא ההחלטה האסטרטגית באיזו קטגוריה אתם, למי אתם, ולמה אתם מנצחים את החלופה כולל לא לעשות כלום. מסר הוא איך מבטאים את זה במילים של הקונה. מיצוב בא קודם, כי המילים עובדות רק כשהמסגרת נכונה."},
    {"q":"למה המסר שלי ב-B2B לא ממיר?","a":"לרוב כי הוא מתאר את המוצר במקום את התוצאה של הקונה, או כי הוא כתוב לכולם ולכן לא משכנע אף אחד. קונים מאשרים תקציב על תוצאות שהם נמדדים עליהן, לא על רשימות פיצ׳רים. מסגרו כל מסר סביב התוצאה הספציפית שאכפת לפרסונה ספציפית ממנה."},
    {"q":"מי המתחרה האמיתי שלי?","a":"רוב הזמן זה הסטטוס קוו, לא ספק אחר: הגיליון, התהליך הידני, הדבר שהם כבר סובלים. מצבו מול לא לעשות כלום ואתם מתייחסים להחלטה שהקונה באמת מקבל."},
    {"q":"האם המסר צריך להשתנות לפי קונה?","a":"כן. הכספים, המשתמש וראש המחלקה קונים את אותו מוצר מסיבות שונות, כך שכל אחד צריך מסר שמכוון למה שאכפת לו. מסר אחד לכולם הוא מסר שלא משכנע אף אחד עד הסוף."}],
  "related":'חלק מאשכול <a href="/he/b2b-go-to-market-strategy">אסטרטגיית ההליכה לשוק</a>. ראו גם <a href="/he/go-to-market-motion">בחירת מהלך ה-GTM</a>, את <a href="/he/services/go-to-market-strategy">שירות ה-GTM</a>, או קראו <a href="/he/blog/ideal-customer-profile-icp">איך מגדירים ICP שממיר</a>.'},

 {"slug":"go-to-market-motion",
  "title":"איך בוחרים את מהלך ה-Go-To-Market | טל פאפרין",
  "desc":"אאוטבאונד, אינבאונד, מוצר-מוביל או ערוץ? איך בוחרים את מהלך ההליכה לשוק הנכון ל-B2B לפי נקודת מחיר, קונה ושלב, לא לפי אופנה.",
  "h1":"איך בוחרים את מהלך ה-Go-To-Market","eyebrow":"מדריך",
  "lead":"כל רבעון מישהו בלינקדאין מכריז שמהלך מסוים מת. אאוטבאונד מת, אינבאונד מת, PLG הרג את המכירות, המכירות הרגו את PLG. התעלמו מהכול. מהלך הליכה לשוק הוא בחירה שעושים מתוך נקודת המחיר, הקונה והשלב שלכם, לא אמונה. הנה איך בוחרים את זה שמתאים.",
  "sections":[
    {"h":"המהלכים, ולמי כל אחד מתאים","tiers":[
      "אאוטבאונד. אתם הולכים לקונה: פנייה ממוקדת, SDRs, מכירה ישירה. מתאים לנקודות מחיר גבוהות, קונים מוגדרים, וכל שלב מוקדם שבו אתם צריכים שליטה, מהירות וידע שוק עכשיו.",
      "אינבאונד. הקונה בא אליכם: תוכן, SEO, מוניטין, מפה לאוזן. מצטבר יפה ולוקח שישה עד שמונה עשר חודשים לייצר פייפליין צפוי, כך שזה נכס שבונים, לא מתג שמדליקים.",
      "מוצר-מוביל. המוצר מוכר את עצמו דרך שכבה חינמית או ניסיון. מתאים לנקודות מחיר נמוכות, מוצרים בשירות עצמי ומשתמש שיכול לאמץ בלי ועדה. מתפרק ברגע שהעסקה צריכה אישור.",
      "ערוץ ושותפים. כוח מכירות או מפיץ של מישהו אחר מוכר בשבילכם. מתאים לשווקים שבהם האמון מקומי, הקונה קשה להשגה ישירה, או שאתם עדיין לא יכולים להרשות לעצמכם אנשים בשטח."]},
    {"h":"בוחרים לפי שלושה דברים, לא לפי אופנה","ul":[
      "נקודת מחיר: נמוכה ובשירות עצמי נוטה למוצר-מוביל, גבוהה ובקנייה בוועדה צריכה מכירה מובלת",
      "קונה: קל למצוא ולהגיע אליו מעדיף אאוטבאונד, משתמש רחב בשירות עצמי מעדיף מוצר-מוביל",
      "שלב: מוקדם כמעט תמיד צריך אאוטבאונד קודם, כי צריך שליטה ולמידה עכשיו"]},
    {"h":"למה B2B בשלב מוקדם כמעט תמיד מתחיל באאוטבאונד","p":[
      "מייסדים רוצים אינבאונד: לידים שמגיעים כבר מעוניינים. מי לא. הבעיה היא שאינבאונד הוא נכס שבונים לאורך חודשים רבים, ובשלב הכי מוקדם אין לכם את מסלול הריצה ואתם עדיין לא יודעים מספיק כדי להזין את המכונה. אאוטבאונד קונה לכם שליטה, מהירות וידע שוק ישיר עכשיו. אתם לומדים מי באמת קונה ולמה מתוך שיחה איתם, והלמידה הזו היא מה שמאפשר לבנות אינבאונד טוב אחר כך. התחילו באאוטבאונד, הרוויחו את הזכות לאינבאונד.",
      "בניתי את החברה שלי בכך שביקרתי לקוח, לא בכך שפרסמתי וחיכיתי. העיקרון מחזיק לרוב ה-B2B: לכו לשוק לפני שאתם מצפים שהוא יבוא אליכם."]},
    {"h":"רוב החברות מגיעות להיברידי","p":[
      "התשובה הכנה היא לעתים רחוקות מהלך אחד. B2B טיפוסי מרחיב אאוטבאונד לשליטה מוקדם, משלב אינבאונד ככל שתוכן ומוניטין מצטברים, ומוסיף ערוץ היכן ששוק קשה להשגה ישירה. מוצר-מוביל יושב מתחת רק אם המוצר באמת מוכר בלי בן אדם. הטעות היא לבחור מהלך מתוך אידאולוגיה ולהכריח את העסק להתאים לו, במקום לתת לקונה ולנקודת המחיר להחליט."]},
    {"h":"איפה זה משתלב","links":[
      ["אסטרטגיית ה-GTM המלאה", "/he/b2b-go-to-market-strategy"],
      ["מיצוב ומסר ל-B2B", "/he/b2b-positioning-and-messaging"],
      ["שירות אסטרטגיית Go-To-Market", "/he/services/go-to-market-strategy"]]},
  ],
  "faqs":[
    {"q":"איך בוחרים מהלך הליכה לשוק?","a":"לפי שלושה דברים: נקודת המחיר, הקונה והשלב שלכם. מחיר נמוך ושירות עצמי נוטים למוצר-מוביל, מחיר גבוה וקנייה בוועדה צריכים מכירה מובלת, קונה קל להשגה מעדיף אאוטבאונד, ושוק מקומי קשה להשגה מעדיף ערוץ. בוחרים מתוך העסק, לא מתוך מה שבאופנה."},
    {"q":"סטארטאפ בשלב מוקדם צריך אאוטבאונד או אינבאונד?","a":"אאוטבאונד קודם, כמעט תמיד. אינבאונד מצטבר אבל לוקח שישה עד שמונה עשר חודשים, ובהתחלה חסרים לכם גם מסלול הריצה וגם ידע השוק כדי להזין אותו. אאוטבאונד קונה שליטה, מהירות ולמידה ישירה על מי שבאמת קונה, וזה מה שמאפשר לבנות אינבאונד טוב אחר כך."},
    {"q":"מתי צמיחה מוצר-מובילה עובדת?","a":"כשהמוצר באמת מוכר את עצמו: נקודת מחיר נמוכה, אימוץ בשירות עצמי, ומשתמש יחיד שלא צריך אישור ועדה. ברגע שעסקה דורשת אישור מכספים או מראש מחלקה, אתם צריכים מהלך מכירה לצידו."},
    {"q":"אפשר להריץ יותר ממהלך אחד?","a":"רוב חברות ה-B2B עושות זאת, ונכון שיעשו. דרך נפוצה היא אאוטבאונד לשליטה מוקדם, אינבאונד משולב ככל שהוא מצטבר, וערוץ נוסף היכן ששוק קשה להשגה ישירה. הטעות היא להכריח מהלך אחד מתוך אידאולוגיה במקום להתאים מהלכים לקונה ולנקודת המחיר."}],
  "related":'חלק מאשכול <a href="/he/b2b-go-to-market-strategy">אסטרטגיית ההליכה לשוק</a>. ראו גם <a href="/he/b2b-positioning-and-messaging">מיצוב ומסר</a>, את <a href="/he/services/go-to-market-strategy">שירות ה-GTM</a>, או קראו <a href="/he/blog/outbound-vs-inbound-early-stage">אאוטבאונד מול אינבאונד בשלב מוקדם</a> ו<a href="/he/blog/product-led-vs-sales-led">צמיחה מוצר-מובילה מול מכירה-מובילה</a>. אם גייסתם נציגים ואין פייפליין, החלק החסר הוא לרוב המהלך עצמו: ראו <a href="/he/hired-reps-but-no-pipeline">גייסתם נציגים ואין פייפליין</a>.'},

 {"slug":"sell-in-israel-first-or-go-global",
  "title":"למכור קודם בישראל, או ישר לחו״ל? | טל פאפרין",
  "desc":"האם סטארטאפ B2B ישראלי צריך להוכיח מכירות בבית לפני חו״ל, או לדלג על השוק המקומי? התשובה הכנה, ומתי התחלה מקומית היא מלכודת.",
  "h1":"למכור קודם בישראל, או ישר לחו״ל?","eyebrow":"חדירה לשווקים",
  "lead":"רוב המייסדים הישראלים ממסגרים את זה כבינארי: ישראל או חו״ל. מסגרת שגויה. מה שחשוב הוא מה השוק המקומי באמת יכול ללמד אתכם, ומה הוא מסתיר בשקט עד היום שבו תנסו למכור בניו יורק. הנה איך אני מכריע את זה עם לקוחות, ומתי מכירה בבית קודם היא מלכודת.",
  "sections":[
    {"h":"השוק הישראלי קטן מכדי להיות היעד שלכם, וזו הנקודה","p":[
      "בישראל חיים פחות מעשרה מיליון אנשים ומאגר קטן של קונים לכל מוצר B2B נתון. אף חברה ישראלית רצינית לא נבנתה על השוק המקומי לבדו, ורוב העבודה שלי ביותר מ-20 שנה הייתה לקחת חברות ישראליות לארה״ב, לאיחוד האירופי, למזרח אירופה ול-APAC. אז כשמייסד אומר שהוא יכבוש קודם את ישראל ואז יתרחב, אני מתנגד. יתרחב לאן? היעד תמיד היה בחו״ל.",
      "זה לא הופך את השוק המקומי לחסר תועלת. זה הופך אותו לחדר חזרות, לא לבמה. המלכודת היא לבלבל בין החזרה להצגה."]},
    {"h":"במה מכירה בישראל קודם באמת טובה","ul":[
      "בדיקת המסר בזול, פנים אל פנים, מול קונים שמגיעים אליהם בנסיעה ברחבי תל אביב במקום בטיסה של שמונה אזורי זמן",
      "השגת הלוגואים ומקרי המבחן הראשונים, גם קטנים, כדי שקונה אמריקאי לא יהיה הלקוח הראשון שלכם אי פעם",
      "ללמוד את המכניקה של המכירה שלכם: ההתנגדויות, בעלי העניין, כמה זמן מחזור באמת נמשך",
      "לבחון את המוצר מול רכש אמיתי לפני שהסיכון הוא חשבון אמריקאי גורלי"]},
    {"h":"מה הוא מסתיר בשקט, ולמה התחלה מקומית שורפת שנה","p":[
      "קונים ישראלים הם לא קונים אמריקאים. הם מתמקחים חזק יותר על מחיר, סובלים מוצר גולמי יותר מחברה שהם מכירים אישית, וקונים בין היתר כי המייסד שירת עם מישהו שערב לכם. שום דבר מזה לא עובר לחו״ל. אפשר לסגור תריסר עסקאות בישראל על קשרים ואי-פורמליות, להכריז שהמהלך הוכח, ואז לראות אותו מתפרק ברגע שקונה אמריקאי שמעולם לא שמע עליכם מריץ אתכם בתהליך הערכה אמיתי.",
      "זו השנה שמייסדים שורפים. הם מתייחסים לטרקשן המקומי כהוכחה שה-Go-to-Market עובד, מתרחבים עליו, ומגלים בארה״ב שהם אימתו את הדבר הלא נכון. השוק הביתי החמיא להם."]},
    {"h":"מתי התחלה מקומית באמת הגיונית","tiers":[
      "מוצרים מפוקחים או קשורים למקום. אם אתם מוכרים לבנקים, בתי חולים, חברות תשתית או למגזר הציבורי בישראל, השוק המקומי הוא שוק אמיתי עם הכנסה אמיתית, לא חזרה. התחילו איפה שאתם יכולים לנצח.",
      "ביטחון וסמוך לממשל. רפרנס של צה״ל או של ממשלת ישראל הוא נכס בחו״ל, לא הסחת דעת. כאן העסקה המקומית אסטרטגית, לא רק אימון.",
      "מוצרים שעברית תחילה או ספציפיים לישראל. אם המוצר הגיוני רק בשפה, ברגולציה או במבנה השוק המקומי, חו״ל הוא מוצר נפרד, לא שלב הבא.",
      "הישרדות תזרימית טהורה. אם אתם צריכים הכנסה ברבעון הזה כדי לשרוד והקונים היחידים שבהישג יד הם מקומיים, מכרו להם. רק אל תבלבלו הישרדות עם אימות."]},
    {"h":"איך אני מסדר את הרצף עם לקוחות","p":[
      "השתמשו בשוק המקומי כדי ללמוד, לא כדי להוכיח. סגרו קומץ עסקאות ישראליות כדי לחדד את המסר ואת המכניקה, התייחסו לתוצאות כטיוטה, ובנו את ה-Go-to-Market האמיתי לשוק היעד מהיום הראשון. בניתי את החברה שלי בכך שעליתי על מטוס וביקרתי לקוח, לא בכך שחיכיתי שהשוק הביתי יישא אותי. לרוב חברות ה-B2B הישראליות הרצף הכן פשוט: ללמוד בבית אם זה זול ומהיר, אבל לכוון את האסטרטגיה, ה-ICP והמסר לארה״ב או לאיחוד האירופי מההתחלה."]},
    {"h":"להעמיק","links":[
      ["מתי להתרחב לשוק האמריקאי", "/he/when-to-expand-to-the-us"],
      ["סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל", "/he/fractional-cro-israel"],
      ["שירות כניסה לשוק", "/he/services/market-entry"]]},
  ],
  "faqs":[
    {"q":"האם סטארטאפ ישראלי צריך למכור בישראל לפני חו״ל?","a":"לרוב חברות ה-B2B, התייחסו לישראל כמקום ללמוד בו, לא כיעד. הוא קטן מכדי לבנות עליו חברה, והטרקשן המקומי יכול להחמיא לכם כי קונים ישראלים קונים על קשרים ואי-פורמליות שלא עוברים לחו״ל. חדדו את המסר בבית אם זה זול, אבל בנו את ה-Go-to-Market לארה״ב או לאיחוד האירופי מהיום הראשון."},
    {"q":"מתי מכירה מקומית קודם הגיונית?","a":"כשהשוק המקומי הוא שוק אמיתי עם הכנסה אמיתית: מוצרים מפוקחים או קשורים למקום שנמכרים לבנקים, בתי חולים, תשתיות או למגזר הציבורי בישראל; עסקאות ביטחון וממשל שבהן רפרנס ישראלי הוא נכס בחו״ל; מוצרים שעברית תחילה; או הישרדות תזרימית טהורה כשהקונים המקומיים הם היחידים בהישג יד עכשיו."},
    {"q":"למה סטארטאפים ישראלים נכשלים כשהם מתרחבים מבסיס מקומי חזק?","a":"כי הם אימתו את הדבר הלא נכון. עסקאות שנסגרו בישראל על קשרים אישיים וסובלנות למוצר גולמי לא מנבאות איך קונה אמריקאי שמעולם לא שמע עליכם יעריך אתכם. מייסדים מתרחבים על הטרקשן הביתי ומגלים בחו״ל שהמהלך מעולם לא באמת עבד לשוק קר."},
    {"q":"אתם יכולים לעזור לחברה ישראלית לסדר את רצף המכירות המקומי והגלובלי?","a":"כן. ביליתי יותר מ-20 שנה בלקיחת חברות B2B ישראליות לארה״ב, לאיחוד האירופי, למזרח אירופה ול-APAC. אני עוזר להחליט מה ללמוד בבית, מה לכוון לחו״ל מהיום הראשון, ואז לבנות ולהריץ את ה-Go-to-Market לשוק היעד."}],
  "related":'ראו <a href="/he/when-to-expand-to-the-us">מתי להתרחב לשוק האמריקאי</a>, את המדריך <a href="/he/fractional-cro-israel">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל</a> ואת <a href="/he/b2b-go-to-market-strategy">אסטרטגיית ה-Go-to-Market</a>. מהבלוג: <a href="/he/blog/choosing-first-market">איך לבחור את השוק הראשון</a>, <a href="/he/blog/why-israeli-startups-fail-at-sales">למה סטארטאפים ישראלים נכשלים במכירות בחו״ל</a> ו<a href="/he/blog/an-israeli-saas-company-sold-to-the-wrong-market-for">חברת SaaS ישראלית שמכרה לשוק הלא נכון</a>. או <a href="/sell-in-israel-first-or-go-global">הגרסה באנגלית</a>.'},

 {"slug":"when-to-expand-to-the-us",
  "title":"מתי להתרחב לשוק האמריקאי | טל פאפרין",
  "desc":"איך לדעת שהחברה שלכם מוכנה לארה״ב, הסימנים שאומרים לחכות, ומה לאמת לפני שתוציאו דולר על המהלך.",
  "h1":"מתי להתרחב לשוק האמריקאי","eyebrow":"חדירה לשווקים",
  "lead":"ארה״ב היא הפרס הגדול ביותר והדרך המהירה ביותר לשרוף גיוס. רוב החברות טועות בתזמון באחד משני כיוונים: הן ממהרות לשם למכור לפני שהן יודעות משהו, או מחכות כל כך הרבה שהשוק הביתי הופך לתקרה. הנה איך אני קורא מוכנות, ומה להוכיח לפני שמתחייבים לדולר.",
  "sections":[
    {"h":"רוצו ללמוד, לא למכור","p":[
      "הטעות האמריקאית היקרה ביותר היא להתייחס למהלך כהשקת מכירות כשהוא בעצם תרגיל למידה. מייסדים טסים לשם, שוכרים משרד, מגייסים שני נציגים ומצפים לפייפליין ברבעון. ואז כלום לא נסגר, השריפה אמיתית, והגיוס נגמר. ארה״ב לא מתגמלת נוכחות לבדה. היא מתגמלת חברה שכבר יודעת מי קונה, למה, ואיך המכירה נראית לפני שהיא מגדילה את ההוצאה.",
      "התרחבו כשאתם מוכנים ללמוד מהר ובזול בארה״ב, לא כשאתם נואשים להזמין שם הכנסה."]},
    {"h":"סימנים שאתם מוכנים","ul":[
      "יש לכם לקוחות שאפשר להפנות אליהם, גם קטנים, שיענו לשיחה מפרוספקט אמריקאי",
      "המכירה שלכם חוזרת על עצמה: אתם יכולים לנקוב ב-ICP, בשלבים ובאורך המחזור בלי לנחש",
      "קונים אמריקאים כבר מושכים, באינבאונד או בשיחות, לא רק שוק שאתם מניחים שרוצה אתכם",
      "יש לכם ראנוויי לתת לזה שנים עשר עד שמונה עשר חודשים, כי מהלך אמריקאי לא מחזיר ברבעון",
      "מייסד או מנהל בכיר יכול להקדיש זמן אמיתי לשעות ארה״ב, לא נציג שנזרק למים"]},
    {"h":"סימנים שאתם עוד לא מוכנים","ul":[
      "המכירות עדיין רצות כולן דרך הרשת האישית של המייסד ושום דבר לא מתועד",
      "אתם לא יכולים לתאר את ה-ICP בלי לומר כל מי ש",
      "ההוכחה היחידה שלכם היא עסקאות ביתיות שנסגרו על קשרים, לא מהלך קר שחוזר על עצמו",
      "אתם מתרחבים כדי לברוח משוק ביתי תקוע, לא כדי לרדוף אחרי ביקוש אמריקאי אמיתי",
      "התוכנית היא לגייס סמנכ״ל מכירות אמריקאי, למסור לו את הבעיה ולקוות"]},
    {"h":"מה לאמת לפני שמוציאים","p":[
      "לפני הישות, המשרד והגיוס הראשון, קיימו עשרים שיחות אמיתיות עם קונים אמריקאים שמתאימים ל-ICP שלכם. לא כדי למכור. כדי ללמוד אם הכאב שאתם פותרים הוא הכאב שהם מרגישים, אם המסר שלכם נוחת במילים שלהם, ומה הם באמת ישלמו. אם קונים אמריקאים מגיעים לפגישה ומתכופפים פנימה, זה סימן המוכנות החזק ביותר שיש. אם אתם לא מצליחים להשיג אותם בטלפון מישראל, משרד אמריקאי לא יתקן את זה.",
      "ואז העריכו ביושר: כמה מהשוק הפוטנציאלי האמיתי שלכם נמצא בארה״ב. אם רובו שם, ארה״ב היא לא שאלה של אם, רק של מתי ואיך."]},
    {"h":"חדרו רזה, ואז הגדילו","p":[
      "מוכנות לא אומרת להעתיק את החברה. המכירות האמריקאיות הראשונות יכולות לבוא מהצוות הקיים שעובד בשעות ארה״ב, אז צוות נחיתה קטן, אז נציגים וישות ברגע שהמהלך מוכיח את עצמו. סדרו את זה ברצף: להוכיח, ואז לבנות את הנוכחות, ישירות או דרך שותפים, כשזה מוצדק. החברות ששורפות את ארה״ב הן אלה שבונות את כל המנגנון לפני שיש להן עסקה אחת שחוזרת."]},
    {"h":"להעמיק","links":[
      ["למכור קודם בישראל, או ישר לחו״ל?", "/he/sell-in-israel-first-or-go-global"],
      ["סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל", "/he/fractional-cro-israel"],
      ["שירות כניסה לשוק", "/he/services/market-entry"]]},
  ],
  "faqs":[
    {"q":"מתי סטארטאפ צריך להתרחב לארה״ב?","a":"כשהמכירה כבר חוזרת על עצמה וקונים אמריקאים מושכים, לא כשאתם צריכים שם הכנסה כדי לשרוד. קונקרטית: יש לכם לקוחות להפניה, ICP ומחזור מוגדרים, ראנוויי של 12 עד 18 חודשים, ומנהיג שיכול להקדיש זמן אמיתי לשעות ארה״ב. אם המכירות עדיין רצות דרך הרשת של המייסד ושום דבר לא מתועד, מוקדם מדי."},
    {"q":"איך אני יודע אם החברה שלי מוכנה לשוק האמריקאי?","a":"קיימו 20 שיחות אמיתיות עם קונים אמריקאים שמתאימים ל-ICP שלכם לפני שאתם מוציאים דולר על ישות או משרד. אם הם מגיעים לפגישה ומתכופפים פנימה, זה סימן המוכנות החזק ביותר. אם אתם לא מצליחים להשיג אותם בטלפון מהבית, משרד אמריקאי לא יתקן את זה. בדקו גם כמה מהשוק הפוטנציאלי שלכם באמת בארה״ב."},
    {"q":"האם אני צריך משרד וצוות אמריקאי כדי להתחיל למכור שם?","a":"לא. המכירות האמריקאיות הראשונות יכולות לבוא מהצוות הקיים שעובד בשעות ארה״ב, אז צוות נחיתה קטן, אז נציגים וישות ברגע שהמהלך מוכיח את עצמו. לבנות את כל המנגנון לפני עסקה אחת שחוזרת זה איך חברות שורפות את ארה״ב."},
    {"q":"מה טעות ההתרחבות הנפוצה ביותר לארה״ב?","a":"להתייחס למהלך כהשקת מכירות במקום כתרגיל למידה. מייסדים שוכרים משרד ומגייסים נציגים מתוך ציפייה לפייפליין ברבעון, ואז שורפים את הגיוס כשכלום לא נסגר. התרחבו כדי ללמוד מהר ובזול, לא כדי להזמין הכנסה שעוד לא הרווחתם את הזכות אליה."}],
  "related":'ראו <a href="/he/sell-in-israel-first-or-go-global">למכור קודם בישראל, או ישר לחו״ל?</a>, את המדריך <a href="/he/fractional-cro-israel">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל</a> ואת <a href="/he/b2b-go-to-market-strategy">אסטרטגיית ה-Go-to-Market</a>. מהבלוג: <a href="/he/blog/entering-the-us-market">כניסה לשוק האמריקאי</a>, <a href="/he/blog/setting-up-us-subsidiary">הקמת חברת בת בארה״ב</a> ו<a href="/he/blog/choosing-first-market">איך לבחור את השוק הראשון</a>. או <a href="/when-to-expand-to-the-us">הגרסה באנגלית</a>.'},
]



ABOUT_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>About Tal Paperin | Fractional CRO / CGO and B2B Growth Leader</title>
  <meta name="description" content="Tal Paperin is a fractional CRO and Chief Growth Officer (CGO) with 20-plus years building and scaling revenue and growth engines across five continents. Operator, not advisor." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/about" />

  <meta property="og:type" content="profile" />
  <meta property="og:url" content="https://talpaperin.com/about" />
  <meta property="og:title" content="About Tal Paperin | Fractional CRO / CGO" />
  <meta property="og:description" content="Twenty years carrying the number on five continents. Fractional CRO and Chief Growth Officer. Operator, not advisor." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="About Tal Paperin | Fractional CRO / CGO" />
  <meta name="twitter:description" content="Twenty years carrying the number on five continents. Operator, not advisor." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">About</p>
        <h1>About Tal Paperin</h1>
        <p class="lead">Operator, not advisor. I own the number and make the team deliver it: I diagnose where revenue is stuck, then build, train and manage the team, or bring my own, until it moves. Twenty years of it, on five continents.</p>

        <figure class="svc-photo portrait"><img src="/img/site/fractional-cro-portrait.jpg" alt="Tal Paperin, fractional CRO" width="800" height="1200" loading="lazy" /><figcaption>Senior revenue leadership, in the seat.</figcaption></figure>

        <h2>Twenty years carrying the number</h2>
        <p>I am a veteran international sales operator, fractional CRO / CGO and business strategist with more than 20 years building and scaling B2B sales engines. I started in the mud, hands-on, as an SDR, moved up to Account Executive and Team Leader, then served as VP of Global Sales and Business Development for multinationals and venture-backed startups. I build and run revenue functions from zero, across North America, Europe, APAC and the Middle East.</p>
        <p>Along the way I have managed international distributor networks, owned CRM architecture and the sales stack, and run market-entry strategies, including putting written-off products back onto retail shelves across Eastern Europe, EMEA and APAC. Different products, different buyers, the same discipline: own the number, do the work.</p>

        <h2>20+ years building revenue organizations</h2>
{career}

        <h2>Fractional CRO or fractional CGO?</h2>
        <p>The title depends on the mandate. A Chief Revenue Officer owns the number: sales, pipeline, forecasting and the closing motion. A Chief Growth Officer owns the whole system that produces it: sales plus marketing, partnerships and channel, pricing and packaging, and entry into new markets. I have run both, and the distinction is real.</p>
        <p>Growth has always been the wider part of my work. KSW Solutions deliberately runs sales and marketing as one function, not two departments that blame each other. I have built distributor and channel networks across five continents, set pricing, and taken products into markets from zero. That is growth work, not just revenue work. So if your problem is &ldquo;we are not closing,&rdquo; you want a CRO. If it is &ldquo;we do not have a growth engine,&rdquo; you want a CGO. I can carry either seat, fractionally.</p>

        <h2>KSW Solutions</h2>
        <p><a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>, the firm I co-lead, is an entire sales and marketing department for hire. Not advisors on the side, the whole function under one roof: the people and the senior leadership both. SDRs, AEs, BDs and marketing, plus the VP and CRO-level management that runs them, hired, trained, managed and accountable. A company can outsource the entire revenue engine to us instead of building it.</p>
        <p>We deliver field-ready operations, not slideware, across SaaS, IoT and hardware, medical devices, manufacturing and consumer brands.</p>

        <h2>TheDealMentor.AI</h2>
        <p>Early-stage founders and lean teams rarely have access to senior sales leadership. So I built <a href="https://thedealmentor.ai" target="_blank" rel="noopener">TheDealMentor.AI</a>, a virtual CRO companion that automates the playbooks and structures complex deal-handling without the overhead of an executive retainer.</p>

        <h2>Background and credentials</h2>
        <ul>
          <li>20-plus years in B2B sales, from SDR to VP of Global Sales and Business Development</li>
          <li>Operates as both a fractional CRO (revenue) and a fractional CGO (full growth: sales, marketing, partnerships and market entry)</li>
          <li>Built and rebuilt revenue for 30-plus B2B companies, from startups to multinationals</li>
          <li>Worked across five continents and more than forty countries</li>
          <li>Served in the Israeli Air Force</li>
          <li>Dual B.A. from the Hebrew University of Jerusalem, in International Relations and Chinese and East Asian Studies</li>
          <li>Speaks English, Hebrew, Russian and Chinese</li>
        </ul>

        <h2>The short personal version</h2>
        <p>Born in the USSR in 1981, in Israel since 1990. Married to an American-born marketing executive, and a father of five. Off the clock I collect mechanical tool watches, read science fiction and post-apocalyptic novels, and keep a structured strength-training habit.</p>

        <p><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">View my full background on LinkedIn &rarr;</a></p>

        <h2>On podcasts and shows</h2>
        <div class="vids">
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/DAjZ6cnH08M" title="CEO Money with Michael Yorba" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">CEO Money with Michael Yorba</p></div>
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/Ft0fmJe7nes" title="Solution Nation Podcast" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">Solution Nation Podcast</p><p class="vsub">Investing in Israeli IIoT companies</p></div>
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/-w_sHvp2v1I" title="Hard Corps Marketing Show #34" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">Hard Corps Marketing Show #34</p><p class="vsub">Global sales fundamentals</p></div>
        </div>

        <h2 class="cases-recs-h">On the ground, on five continents</h2>
{gallery}
{cta}
        <div class="svc-related">See <a href="/services/">how I can help</a>, the <a href="/case-studies">case studies</a>, or <a href="/recommendations">what clients say</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''

ABOUT_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>אודות טל פאפרין | סמנכ״ל מכירות וצמיחה במיקור חוץ (CRO / CGO)</title>
  <meta name="description" content="טל פאפרין הוא סמנכ״ל מכירות במיקור חוץ וסמנכ״ל צמיחה (CRO / CGO) עם מעל 20 שנה של בנייה והרחבת מנועי הכנסות וצמיחה בחמש יבשות. איש ביצוע, לא יועץ." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/about" />

  <meta property="og:type" content="profile" />
  <meta property="og:url" content="https://talpaperin.com/he/about" />
  <meta property="og:title" content="אודות טל פאפרין | סמנכ״ל מכירות וצמיחה (CRO / CGO)" />
  <meta property="og:description" content="עשרים שנה של אחריות על התוצאות, בחמש יבשות. סמנכ״ל מכירות וצמיחה במיקור חוץ. איש ביצוע, לא יועץ." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="אודות טל פאפרין | סמנכ״ל מכירות וצמיחה (CRO / CGO)" />
  <meta name="twitter:description" content="עשרים שנה של אחריות על התוצאות, בחמש יבשות. איש ביצוע, לא יועץ." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {graph}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">אודות</p>
        <h1>אודות טל פאפרין</h1>
        <p class="lead">איש ביצוע, לא יועץ. אני לוקח אחריות על המספר ודואג שהצוות יספק אותו: מאבחן איפה ההכנסות נתקעו, ואז בונה, מכשיר ומנהל את הצוות, או מביא צוות משלי, עד שהמספר זז. עשרים שנה, בחמש יבשות.</p>

        <figure class="svc-photo portrait"><img src="/img/site/fractional-cro-portrait.jpg" alt="טל פאפרין" width="800" height="1200" loading="lazy" /><figcaption>הנהגת הכנסות בכירה, בכיסא.</figcaption></figure>

        <h2>עשרים שנה של אחריות על התוצאות</h2>
        <p>אני איש מכירות בינלאומי ותיק, סמנכ״ל מכירות וצמיחה במיקור חוץ (CRO / CGO) ואסטרטג עסקי עם מעל 20 שנה של בנייה והרחבת מנועי מכירות B2B. התחלתי בבוץ, ידיים, כאיש SDR, עליתי ל-Account Executive וראש צוות, ובהמשך כיהנתי כ-VP of Global Sales and Business Development בתאגידים רב-לאומיים ובסטארטאפים מגובי הון סיכון. אני בונה ומנהל מחלקות הכנסה מאפס, בצפון אמריקה, אירופה, APAC והמזרח התיכון.</p>
        <p>בדרך ניהלתי רשתות מפיצים בינלאומיות, הייתי אחראי על ארכיטקטורת ה-CRM ומערך המכירות, והרצתי אסטרטגיות חדירה לשווקים, כולל החזרת מוצרים שנמחקו אל מדפי הקמעונאות במזרח אירופה, EMEA ו-APAC. מוצרים שונים, קונים שונים, אותה משמעת: לקחת אחריות על התוצאות, ולעשות את העבודה.</p>

        <h2>20+ שנים של בניית מחלקות הכנסה</h2>
{career}

        <h2>סמנכ״ל הכנסות במיקור חוץ או סמנכ״ל צמיחה?</h2>
        <p>התואר תלוי במנדט. סמנכ״ל הכנסות (CRO) אחראי על המספר: מכירות, צינור, תחזית ומהלך הסגירה. סמנכ״ל צמיחה (CGO) אחראי על כל המערכת שמייצרת אותו: מכירות יחד עם שיווק, שותפויות וערוצי הפצה, תמחור ואריזה, וכניסה לשווקים חדשים. עשיתי את שני התפקידים, וההבדל אמיתי.</p>
        <p>הצמיחה תמיד הייתה החלק הרחב יותר בעבודה שלי. KSW Solutions מריצה בכוונה מכירות ושיווק כפונקציה אחת, לא שתי מחלקות שמאשימות זו את זו. בניתי רשתות מפיצים וערוצי הפצה בחמש יבשות, קבעתי תמחור, והכנסתי מוצרים לשווקים מאפס. זו עבודת צמיחה, לא רק עבודת הכנסות. אז אם הבעיה היא &rdquo;אנחנו לא סוגרים&ldquo;, אתם צריכים CRO. אם היא &rdquo;אין לנו מנוע צמיחה&ldquo;, אתם צריכים CGO. אני יכול לשבת בכל אחד מהכיסאות, במיקור חוץ.</p>

        <h2>KSW Solutions</h2>
        <p><a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>, החברה שאני מוביל, היא מחלקת מכירות ושיווק שלמה להשכרה. לא יועצים מהצד, אלא כל הפונקציה תחת קורת גג אחת: גם האנשים וגם ההנהגה הבכירה. אנשי SDR, AE, BD ושיווק, יחד עם ההנהלה ברמת VP ו-CRO שמנהלת אותם, מגויסים, מוכשרים, מנוהלים ואחראים. חברה יכולה להוציא אלינו את כל מנוע ההכנסות למיקור חוץ במקום לבנות אותו.</p>
        <p>אנחנו מספקים מערכים מוכנים לשטח, לא מצגות, ב-SaaS, IoT וחומרה, מכשור רפואי, תעשייה ומותגי צריכה.</p>

        <h2>TheDealMentor.AI</h2>
        <p>למייסדים בשלבים מוקדמים ולצוותים רזים כמעט אף פעם אין גישה להנהגת מכירות בכירה. אז בניתי את <a href="https://thedealmentor.ai" target="_blank" rel="noopener">TheDealMentor.AI</a>, מלווה CRO וירטואלי שמכניס ל-playbooks אוטומציה ומבנה לטיפול בעסקאות מורכבות, בלי העלות של ריטיינר למנהל בכיר.</p>

        <h2>רקע והסמכות</h2>
        <ul>
          <li>מעל 20 שנה במכירות B2B, מ-SDR ועד VP of Global Sales and Business Development</li>
          <li>פועל גם כסמנכ״ל הכנסות במיקור חוץ (CRO) וגם כסמנכ״ל צמיחה (CGO): מכירות, שיווק, שותפויות וכניסה לשווקים</li>
          <li>בניתי ובניתי מחדש הכנסות ל-30 ומעלה חברות B2B, מסטארטאפים ועד רב-לאומיות</li>
          <li>עבדתי בחמש יבשות ובמעל ארבעים מדינות</li>
          <li>שירתתי בחיל האוויר הישראלי</li>
          <li>תואר ראשון כפול מהאוניברסיטה העברית בירושלים, ביחסים בינלאומיים ובלימודי סין ומזרח אסיה</li>
          <li>דובר אנגלית, עברית, רוסית וסינית</li>
        </ul>

        <h2>הגרסה האישית הקצרה</h2>
        <p>נולדתי בברית המועצות ב-1981, בישראל מ-1990. נשוי למנהלת שיווק ילידת ארה"ב, ואב לחמישה. בשעות הפנאי אני אוסף שעוני כלי מכניים, קורא מדע בדיוני ורומנים פוסט-אפוקליפטיים, ושומר על שגרת אימוני כוח מסודרת.</p>

        <p><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">לרקע המלא שלי בלינקדאין &larr;</a></p>

        <h2>פודקאסטים ותוכניות</h2>
        <div class="vids">
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/DAjZ6cnH08M" title="CEO Money עם מייקל יורבה" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">CEO Money עם מייקל יורבה</p></div>
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/Ft0fmJe7nes" title="Solution Nation Podcast" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">Solution Nation Podcast</p><p class="vsub">השקעות בחברות IIoT ישראליות</p></div>
          <div><div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/-w_sHvp2v1I" title="Hard Corps Marketing Show #34" loading="lazy" allow="encrypted-media; picture-in-picture; web-share" allowfullscreen></iframe></div><p class="vtitle">Hard Corps Marketing Show #34</p><p class="vsub">יסודות ועקרונות במכירות בינלאומיות</p></div>
        </div>

        <h2 class="cases-recs-h">בשטח, בחמש יבשות</h2>
{gallery}
{cta}
        <div class="svc-related">ראו <a href="/he/services/">איך אני יכול לעזור</a>, את <a href="/he/case-studies">מקרי המבחן</a>, או <a href="/he/recommendations">מה לקוחות אומרים</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


GUIDE_CATS = [
 ("Fractional CRO, explained", "סמנכ״ל הכנסות במיקור חוץ, מוסבר", [
   "how-to-hire-a-fractional-cro", "when-do-you-need-a-fractional-cro", "fractional-cro-roi",
   "fractional-cro-cost", "fractional-cro-vs-vp-of-sales", "fractional-cro-vs-outsourced-sales",
   "interim-cro", "outsourced-cro", "fractional-vp-of-sales", "fractional-chief-sales-officer",
   "fractional-cro-for-startups", "sales-training",
   "sales-forecast-always-wrong", "hired-reps-but-no-pipeline"]),
 ("Building and scaling a sales team", "בניית והרחבת צוות מכירות", [
   "how-to-build-a-sales-team", "founder-led-sales-wont-scale", "building-a-sales-team-after-funding",
   "sales-team-missing-quota", "sales-compensation-plan", "setting-sales-quotas"]),
 ("By industry", "לפי תעשייה", [
   "fractional-cro-for-saas", "fractional-cro-for-iot-hardware", "fractional-cro-for-medical-devices",
   "fractional-cro-for-manufacturers", "fractional-cro-for-cybersecurity", "fractional-cro-for-fintech",
   "fractional-cro-for-defense-tech", "fractional-cro-for-ai-companies", "fractional-cro-for-digital-health",
   "fractional-cro-for-climate-tech", "fractional-cro-for-foodtech", "fractional-cro-for-agritech",
   "fractional-cro-for-robotics", "fractional-cro-for-semiconductors", "fractional-cro-for-logistics",
   "fractional-cro-for-insurtech", "fractional-cro-for-proptech", "fractional-cro-for-legaltech",
   "fractional-cro-for-hr-tech", "fractional-cro-for-edtech", "fractional-cro-for-developer-tools",
   "fractional-cro-for-biotech", "fractional-cro-for-telecom", "fractional-cro-for-energy",
   "fractional-cro-for-professional-services"]),
 ("Outsourced sales and marketing", "מכירות ושיווק במיקור חוץ", [
   "outsourced-sales-and-marketing-department", "outsourced-sdr-team", "b2b-lead-generation-services"]),
 ("Go-to-market strategy", "אסטרטגיית הליכה לשוק", [
   "b2b-go-to-market-strategy", "b2b-positioning-and-messaging", "go-to-market-motion"]),
 ("Market entry", "חדירה לשווקים", [
   "sell-in-israel-first-or-go-global", "when-to-expand-to-the-us",
   "us-market-entry-for-israeli-startups", "fractional-cro-for-the-us-market", "fractional-cro-israel"]),
 ("For frum businesses", "לעסקים פרומיים", ["frum-business-consultant"]),
 ("In the media", "בתקשורת", ["tal-paperin-podcasts-and-press"]),
]


def render_guides_hub(he=False):
    by = {g["slug"]: g for g in (HE_GUIDES if he else GUIDES)}
    base = "/he/" if he else "/"
    out = []
    for en_t, he_t, slugs in GUIDE_CATS:
        items = [by[s] for s in slugs if s in by]
        if not items:
            continue
        out.append('        <h2 class="cases-recs-h">%s</h2>' % esc(he_t if he else en_t))
        out.append('        <ul class="hub-list">')
        for g in items:
            label = g["h1"]
            if not he and label.startswith("Fractional CRO for "):
                label = label[len("Fractional CRO for "):]
                label = label[:1].upper() + label[1:]
            out.append('          <li><a href="%s%s">%s</a><span>%s</span></li>'
                       % (base, g["slug"], esc(label), esc(g["desc"])))
        out.append('        </ul>')
    return "\n".join(out)


HUB_PAGE_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Guides and Resources | Tal Paperin, Fractional CRO</title>
  <meta name="description" content="Guides on hiring a fractional CRO, the cost and ROI, outsourced sales and marketing, and fractional revenue leadership by industry." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/guides" />
  <link rel="alternate" hreflang="en" href="{site}/guides" />
  <link rel="alternate" hreflang="he" href="{site}/he/guides" />
  <link rel="alternate" hreflang="x-default" href="{site}/guides" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{site}/guides" />
  <meta property="og:title" content="Guides and Resources | Tal Paperin" />
  <meta property="og:description" content="Everything on fractional revenue leadership: how to hire, cost, ROI, outsourced sales and marketing, and by industry." />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Guides and Resources | Tal Paperin" />
  <meta name="twitter:description" content="Everything on fractional revenue leadership, by topic and by industry." />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">Guides and Resources</p>
        <h1>Guides and resources</h1>
        <p class="lead">Everything I know about fractional revenue leadership, in plain English: how to hire one, what it costs, the ROI, outsourced sales and marketing, and how it works in your industry.</p>
{groups}
        <div class="svc-related">See the <a href="/services/">services</a>, the <a href="/case-studies">case studies</a>, or <a href="/contact">tell me where revenue stalled</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


HUB_PAGE_HE = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>מדריכים ומשאבים | טל פאפרין</title>
  <meta name="description" content="מדריכים על שכירת סמנכ״ל הכנסות במיקור חוץ, העלות וה-ROI, מכירות ושיווק במיקור חוץ, והנהגת הכנסות לפי תפקיד." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/he/guides" />
  <link rel="alternate" hreflang="he" href="{site}/he/guides" />
  <link rel="alternate" hreflang="en" href="{site}/guides" />
  <link rel="alternate" hreflang="x-default" href="{site}/guides" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{site}/he/guides" />
  <meta property="og:title" content="מדריכים ומשאבים | טל פאפרין" />
  <meta property="og:description" content="הכול על הנהגת הכנסות במיקור חוץ: איך לשכור, עלות, ROI, ומכירות ושיווק במיקור חוץ." />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="מדריכים ומשאבים | טל פאפרין" />
  <meta name="twitter:description" content="הכול על הנהגת הכנסות במיקור חוץ, לפי נושא." />
  <meta name="twitter:image" content="{site}/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc svc-wide">
        <div class="glowline"></div>
        <p class="eyebrow">מדריכים ומשאבים</p>
        <h1>מדריכים ומשאבים</h1>
        <p class="lead">כל מה שאני יודע על הנהגת הכנסות במיקור חוץ, בעברית פשוטה: איך לשכור, כמה זה עולה, ה-ROI, ומכירות ושיווק במיקור חוץ.</p>
{groups}
        <div class="svc-related">ראו את <a href="/he/services/">השירותים</a>, את <a href="/he/case-studies">מקרי המבחן</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


PRICING_EN = {
 "cro_h":"Fractional CRO and business consulting",
 "cro":[
  {"commit":"~3 hours a week","name":"Advisor","price":"$2,000","per":"/mo",
   "bestfor":"Founders who want senior direction and a sounding board while they run the day to day themselves.",
   "incl":["A standing weekly strategy call","Async access between calls for the real decisions","I set the direction and the priorities, you execute"]},
  {"commit":"~2 hours a day","name":"Starter","price":"$6,000","per":"/mo",
   "bestfor":"Early-stage companies or small businesses needing foundational sales improvements.",
   "incl":["Revenue and sales motion review: where deals stall, leak or fail to convert","Sales plan and playbook: ICP, priority channels, talk tracks, decision criteria","Hire, train and manage your salespeople, part-time (about 2 hours a day)","Pipeline structure: CRM stages and definitions"]},
  {"commit":"Half-time, 4-5 hours a day","name":"Growth","price":"$12,000","per":"/mo","feat":True,"badge":"Most common",
   "bestfor":"Scaling companies that need hands-on management and strategic sales guidance.",
   "incl":["Revenue and sales performance oversight","Hire, train and manage your salespeople, hands-on and day to day (about 4-5 hours a day)","CRM and KPI ownership for forecasting and accountability","A living execution framework with goals, timelines and ownership"]},
  {"commit":"Full-time, exclusive","name":"CRO Ownership","price":"$22,000","per":"/mo",
   "bestfor":"End-to-end CRO-level revenue ownership across sales, marketing and GTM, with one accountable leader.",
   "incl":["Full CRO-level ownership of revenue strategy and execution","Authority over sales, marketing and GTM decisions","Leadership of revenue teams and cross-functional alignment","Hiring, onboarding and performance management for revenue roles","Ongoing intervention to course-correct execution and results"]},
 ],
 "sdr_h":"Add a sales team (salespeople)","add_label":"Add to any package","sdr_name":"Dedicated salespeople",
 "sdr_desc":"Need reps but don't want to hire in-house? I source, train and manage them, fully integrated with the leadership you are already paying for.",
 "sdr_incl":["Sourcing, hiring and onboarding of sales talent","Training on your process, messaging and objection handling","Ongoing performance management and coaching","Full integration with your KSW leadership and reporting"],
 "sdr_price_label":"Salespeople pricing","sdr_amount":"$6,000","sdr_amount_per":"/ 1 salesperson / mo",
 "sdr_tiers":["1 salesperson, $6,000/mo","2 salespeople, $11,000/mo","3+ salespeople, $5,000 each/mo"],
 "sdr_price_note":"Price includes full management, training and integration. No hidden management fees.",
 "ppm_h":"Pay-per-meeting sales development",
 "ppm_desc":"Prefer to buy meetings instead of managing a team? We define your ICP, run the outbound and put qualified meetings on your calendar. You pay by the meetings we book, not by activity. A one-time setup launches the campaign, then the monthly tracks results.",
 "ppm_price":PPM_PRICE_EN,
 "ppm_more":"Full details on the",
 "ppm_url":"/services/pay-per-meeting",
 "ppm_more_link":"pay-per-meeting service page",
 "mk_h":"Marketing leadership (via KSW)",
 "marketing":[
  {"commit":"Senior oversight","name":"Marketing Oversight","price":"$4,000","per":"/mo",
   "bestfor":"Teams that already have someone running marketing but need senior oversight to improve focus, prioritization and decisions.",
   "incl":["Ongoing senior review of plans, priorities and spend","Clear guidance on what to pursue, pause or stop","Leadership-level input to keep marketing aligned with the business"]},
  {"commit":"Full ownership","name":"Fractional CMO","price":"$8,000","per":"/mo",
   "bestfor":"Teams with a marketing function in place that need clear leadership, ownership and accountability.",
   "incl":["Leadership of the marketing function and its priorities","Alignment between marketing, sales and executive leadership","Ongoing intervention when execution or results fall short"]},
 ],
 "perf":{
  "h":"Skin in the game, in addition",
  "sub":"Every price above is fixed and monthly. On top of it, we share in the growth, measured against a baseline we agree up front.",
  "items":[
    ("3%","of net new ARR","Me, your CRO"),
    ("10%","of first-year deal value","Account Executives"),
    ("$50","per qualified meeting held","SDRs"),
  ],
  "note":"Added on top of the monthly fee, never instead of it. Client-funded, no hidden fees, no games.",
  "star_title":"Plus a performance share on top",
  "star_note":"★ Plus a performance share, added on top of this fee.",
  "star_link":"See the details",
 },
 "faq_h":"Common questions",
 "faq":[
  ("How does pricing work?","Flat monthly retainers, plus a performance share on top: 3% of net new ARR to me, 10% of first-year deal value to the account executives, and $50 per qualified meeting held to the SDRs. No long contracts and no exit fines. You can move up or down a tier as the business changes."),
  ("What is the difference between the tiers?","Advisor is senior direction on call. Starter and Growth are both hands-on: in both I hire, train and manage your salespeople and own the motion. The difference is time, Starter is about 2 hours a day, Growth is half my day, every day. CRO Ownership is full end-to-end ownership of revenue across sales, marketing and GTM."),
  ("Can I add a sales team?","Yes. SDRs can be added to any package. I source, train and manage them, integrated with the leadership you already have."),
  ("Do you handle marketing too?","Yes, through KSW Solutions: senior marketing oversight or full fractional CMO leadership, so sales and marketing run as one function."),
 ],
 "book":"Book a call",
 "calc_h":"Not sure which package? Build your quote.",
 "calc_intro":"Answer three quick questions. I'll recommend the package, tell you what you get each month and what it costs, then you can download it or send it to me.",
 "calc_prompt":"Answer the questions above and your recommended package appears here.",
 "calc_recommended":"Recommended for you","calc_outcome_h":"Your estimated monthly outcome","calc_cost_h":"Estimated monthly cost",
 "calc_name":"Your name","calc_email":"Your email","calc_company":"Company",
 "calc_download":"Download / print quote","calc_email_btn":"Email this to Tal","calc_book":"Book a call",
 "calc_note":"Estimate only, monthly, no long contracts, no exit fines. Final scope is confirmed on a call.",
 "calc_subject":"Quote request from talpaperin.com","calc_mo":"/mo",
 "calc_quote_title":"Your Quote","calc_print":"Print / Save as PDF","calc_lang":"en","calc_dir":"ltr",
 "calc_tagline":"Fractional CRO & Business Consulting",
 "calc_result_note":"Monthly, no long contracts, no exit fines. Slide the controls below to adjust the mix, the price updates live. Final scope is confirmed on a quick call.",
 "calc_sliders_h":"Adjust the mix","calc_slider_cro":"How much of me","calc_slider_sdr":"Sales team","calc_slider_mk":"Marketing","calc_none_label":"None","calc_sdr_word1":"salesperson","calc_sdr_wordN":"salespeople","calc_sdr_line":"Sales team",
 "calc_tier_outcomes":[
   "A senior revenue advisor on call, about 3 hours a week",
   "A fractional CRO in the seat about 2 hours a day, owning strategy, process and standards",
   "A fractional CRO 4 to 5 hours a day, running the motion and managing the team hands-on",
   "A full-time, exclusive CRO owning revenue end to end across sales, marketing and GTM"],
 "calc_sdr_outcome":"{n} {w}, full-time, dialing and booking meetings on your behalf",
 "calc_q":[
   {"q":"What do you need me to own?","opts":[
     {"t":"Senior direction and a sounding board","tier":0},
     {"t":"Building the sales foundations from scratch","tier":1},
     {"t":"Running the motion and the team, day to day","tier":2},
     {"t":"Owning revenue end to end: sales, marketing and GTM","tier":3}]},
   {"q":"Do you have a sales team?","opts":[
     {"t":"No team. I need reps hired, trained and run","sdr":1},
     {"t":"I have a team that needs leadership","sdr":0},
     {"t":"Not sure yet","sdr":0}]},
   {"q":"How many SDRs to start?","reps":True,"opts":[
     {"t":"1 rep","reps":1},{"t":"2 reps","reps":2},{"t":"3+ reps","reps":3}]},
   {"q":"What about marketing?","opts":[
     {"t":"Marketing is handled","mk":0,"mkname":"","mkout":""},
     {"t":"Someone runs it but needs oversight","mk":4000,"mkname":"Marketing Oversight","mkout":"senior marketing oversight, keeping spend and priorities aligned to sales"},
     {"t":"I need someone to own marketing","mk":8000,"mkname":"Fractional CMO","mkout":"a full marketing function and funnel, owned end to end"}]},
   {"q":"Want us to book sales meetings for you? (pay per meeting)","opts":[
     {"t":"No thanks","ppm":0},
     {"t":"Up to 3 a month","ppm":3000},
     {"t":"4 to 6 a month","ppm":4500},
     {"t":"7 to 14 a month","ppm":6500},
     {"t":"15+ a month","ppm":9000}]}],
 "calc_ppm_line":"Meetings booked (pay per meeting)",
 "calc_ppm_outcome":"Qualified sales meetings booked on your calendar, pay per meeting",
 "calc_ppm_setup_label":"one-time setup to launch the campaign",
 "calc_ppm_rec_name":"Pay-per-meeting sales development",
}

PRICING_HE = {
 "cro_h":"סמנכ״ל מכירות במיקור חוץ וייעוץ עסקי",
 "cro":[
  {"commit":"כ-3 שעות בשבוע","name":"Advisor","price":"$2,000","per":"לחודש",
   "bestfor":"מייסדים שרוצים כיוון בכיר ואוזן קשבת בזמן שהם מנהלים את היומיום בעצמם.",
   "incl":["שיחת אסטרטגיה שבועית קבועה","זמינות אסינכרונית ביני לבין השיחות להחלטות האמיתיות","אני קובע את הכיוון והעדיפויות, אתם מבצעים"]},
  {"commit":"כשעתיים ביום","name":"Starter","price":"$6,000","per":"לחודש",
   "bestfor":"חברות בשלב מוקדם או עסקים קטנים שצריכים שיפור מכירות בסיסי.",
   "incl":["סקירת הכנסות ותנועת מכירות: איפה עסקאות נתקעות, דולפות או לא נסגרות","תוכנית מכירות ו-Playbook: ICP, ערוצים, תסריטים וקריטריוני החלטה","גיוס, הכשרה וניהול של אנשי המכירות שלכם, במשרה חלקית (כשעתיים ביום)","מבנה פייפליין: שלבי CRM והגדרות"]},
  {"commit":"חצי משרה, 4-5 שעות ביום","name":"Growth","price":"$12,000","per":"לחודש","feat":True,"badge":"הנפוץ ביותר",
   "bestfor":"חברות בצמיחה שצריכות ניהול מעשי והכוונת מכירות אסטרטגית.",
   "incl":["פיקוח על ביצועי הכנסות ומכירות","גיוס, הכשרה וניהול של אנשי המכירות שלכם, יומיומי ובידיים (כ-4-5 שעות ביום)","בעלות על ה-CRM וה-KPIs לתחזית ואחריותיות","תוכנית ביצוע חיה עם יעדים, לוחות זמנים ובעלות"]},
  {"commit":"משרה מלאה, בלעדי","name":"CRO Ownership","price":"$22,000","per":"לחודש",
   "bestfor":"בעלות מלאה ברמת CRO על ההכנסות, לרוחב מכירות, שיווק ו-GTM, עם מוביל אחד אחראי.",
   "incl":["בעלות מלאה ברמת CRO על אסטרטגיית ההכנסות והביצוע","סמכות על החלטות מכירות, שיווק ו-GTM","הובלת צוותי הכנסות ותיאום בין-מחלקתי","גיוס, קליטה וניהול ביצועים לתפקידי הכנסות","התערבות שוטפת לתיקון מסלול ותוצאות"]},
 ],
 "sdr_h":"הוספת צוות מכירות (אנשי מכירות)","add_label":"הוספה לכל חבילה","sdr_name":"אנשי מכירות ייעודיים",
 "sdr_desc":"צריכים נציגים אבל לא רוצים לגייס פנימית? אני מאתר, מכשיר ומנהל אותם, משולבים במלואם בהנהגה שאתם כבר משלמים עליה.",
 "sdr_incl":["איתור, גיוס וקליטה של אנשי מכירות","הכשרה על התהליך, המסרים והתמודדות עם התנגדויות שלכם","ניהול ביצועים ואימון שוטפים","שילוב מלא עם ההנהגה והדיווח של KSW"],
 "sdr_price_label":"תמחור אנשי מכירות","sdr_amount":"$6,000","sdr_amount_per":"/ איש מכירות אחד / לחודש",
 "sdr_tiers":["איש מכירות אחד, $6,000 לחודש","שני אנשי מכירות, $11,000 לחודש","3+ אנשי מכירות, $5,000 כל אחד/לחודש"],
 "sdr_price_note":"המחיר כולל ניהול מלא, הכשרה ואינטגרציה. בלי דמי ניהול נסתרים.",
 "ppm_h":"פיתוח מכירות בתשלום לפי פגישה",
 "ppm_desc":"מעדיפים לקנות פגישות במקום לנהל צוות? אנחנו מגדירים את ה-ICP, מריצים את האאוטבאונד ושמים פגישות מוכשרות ביומן שלכם. אתם משלמים לפי הפגישות שאנחנו קובעים, לא לפי פעילות. הקמה חד פעמית משיקה את הקמפיין, ואז החודשי תואם לתוצאות.",
 "ppm_price":PPM_PRICE_HE,
 "ppm_more":"כל הפרטים ב",
 "ppm_url":"/he/services/pay-per-meeting",
 "ppm_more_link":"עמוד שירות התשלום לפי פגישה",
 "mk_h":"הובלת שיווק (דרך KSW)",
 "marketing":[
  {"commit":"פיקוח בכיר","name":"Marketing Oversight","price":"$4,000","per":"לחודש",
   "bestfor":"צוותים שכבר יש להם מישהו שמריץ שיווק, אבל צריכים פיקוח בכיר לשיפור מיקוד, תעדוף והחלטות.",
   "incl":["סקירה בכירה שוטפת של תוכניות, עדיפויות ותקציב","הכוונה ברורה על מה לרדוף, להשהות או לעצור","קלט ברמת הנהגה שמיישר את השיווק עם העסק"]},
  {"commit":"בעלות מלאה","name":"Fractional CMO","price":"$8,000","per":"לחודש",
   "bestfor":"צוותים עם פונקציית שיווק קיימת שצריכים הובלה, בעלות ואחריותיות ברורות.",
   "incl":["הובלת פונקציית השיווק והעדיפויות שלה","תיאום בין שיווק, מכירות והנהלה בכירה","התערבות שוטפת כשהביצוע או התוצאות לא עומדים ביעד"]},
 ],
 "perf":{
  "h":"אחריות על התוצאה, בנוסף",
  "sub":"כל מחיר למעלה הוא קבוע וחודשי. מעליו אנחנו שותפים לצמיחה, נמדדת מול בסיס שנסכם עליו מראש.",
  "items":[
    ("3%","מה-ARR נטו החדש","אני, ה-CRO שלכם"),
    ("10%","משווי העסקה בשנה הראשונה","אנשי מכירות (AE)"),
    ("$50","לכל פגישה מוכשרת שהתקיימה","SDRs"),
  ],
  "note":"מתווסף מעל התשלום החודשי, אף פעם לא במקומו. ממומן על ידי הלקוח, בלי עמלות נסתרות, בלי משחקים.",
  "star_title":"בתוספת שותפות בתוצאה, מעל התשלום",
  "star_note":"★ בתוספת שותפות בתוצאה, מעל התשלום הזה.",
  "star_link":"לפרטים",
 },
 "faq_h":"שאלות נפוצות",
 "faq":[
  ("איך התמחור עובד?","ריטיינרים חודשיים קבועים, בתוספת שותפות בתוצאה מעליהם: 3% מה-ARR נטו החדש אליי, 10% משווי העסקה בשנה הראשונה לאנשי המכירות, ו-50 דולר לכל פגישה מוכשרת שהתקיימה ל-SDRs. בלי חוזים ארוכים ובלי קנסות יציאה. אפשר לעלות או לרדת דרגה ככל שהעסק משתנה."),
  ("מה ההבדל בין החבילות?","Advisor הוא כיוון בכיר בטלפון. Starter ו-Growth שניהם בידיים: בשניהם אני מגייס, מכשיר ומנהל את אנשי המכירות שלכם ומחזיק את התנועה. ההבדל הוא זמן, Starter הוא כשעתיים ביום, Growth הוא חצי מהיום שלי, כל יום. CRO Ownership היא בעלות מלאה על ההכנסות לרוחב מכירות, שיווק ו-GTM."),
  ("אפשר להוסיף צוות מכירות?","כן. אפשר להוסיף SDRs לכל חבילה. אני מאתר, מכשיר ומנהל אותם, משולבים בהנהגה שכבר יש לכם."),
  ("אתם מטפלים גם בשיווק?","כן, דרך KSW Solutions: פיקוח שיווקי בכיר או הובלת CMO מלאה, כך שמכירות ושיווק פועלים כפונקציה אחת."),
 ],
 "book":"לתיאום שיחה",
 "calc_h":"לא בטוחים איזו חבילה? בנו הצעת מחיר.",
 "calc_intro":"ענו על שלוש שאלות קצרות. אמליץ על החבילה, אגיד לכם מה מקבלים כל חודש וכמה זה עולה, ואז אפשר להוריד או לשלוח אליי.",
 "calc_prompt":"ענו על השאלות למעלה והחבילה המומלצת תופיע כאן.",
 "calc_recommended":"מומלץ עבורכם","calc_outcome_h":"התוצאה החודשית המשוערת שלכם","calc_cost_h":"עלות חודשית משוערת",
 "calc_name":"השם שלכם","calc_email":"האימייל שלכם","calc_company":"חברה",
 "calc_download":"הורדה / הדפסה","calc_email_btn":"שליחת ההצעה לטל","calc_book":"לתיאום שיחה",
 "calc_note":"אומדן בלבד, חודשי, בלי חוזים ארוכים, בלי קנסות יציאה. ההיקף הסופי מאושר בשיחה.",
 "calc_subject":"בקשת הצעת מחיר מ-talpaperin.com","calc_mo":"לחודש",
 "calc_quote_title":"הצעת המחיר שלכם","calc_print":"הדפסה / שמירה כ-PDF","calc_lang":"he","calc_dir":"rtl",
 "calc_tagline":"סמנכ״ל מכירות במיקור חוץ וייעוץ עסקי",
 "calc_result_note":"חודשי, בלי חוזים ארוכים, בלי קנסות יציאה. הזיזו את הפקדים למטה כדי לשנות את התמהיל, המחיר מתעדכן בזמן אמת. ההיקף הסופי מאושר בשיחה קצרה.",
 "calc_sliders_h":"התאמת התמהיל","calc_slider_cro":"כמה ממני","calc_slider_sdr":"צוות מכירות","calc_slider_mk":"שיווק","calc_none_label":"ללא","calc_sdr_word1":"איש מכירות","calc_sdr_wordN":"אנשי מכירות","calc_sdr_line":"צוות מכירות",
 "calc_tier_outcomes":[
   "יועץ הכנסות בכיר בטלפון, כ-3 שעות בשבוע",
   "סמנכ״ל מכירות במיקור חוץ בכיסא כשעתיים ביום, אחראי על אסטרטגיה, תהליך וסטנדרטים",
   "סמנכ״ל מכירות 4 עד 5 שעות ביום, מריץ את התנועה ומנהל את הצוות בידיים",
   "סמנכ״ל מכירות במשרה מלאה ובלעדיות, אחראי על ההכנסות מקצה לקצה: מכירות, שיווק ו-GTM"],
 "calc_sdr_outcome":"{n} {w}, במשרה מלאה, מחייגים וקובעים פגישות עבורכם",
 "calc_q":[
   {"q":"על מה אתם צריכים שאהיה אחראי?","opts":[
     {"t":"כיוון בכיר ואוזן קשבת","tier":0},
     {"t":"לבנות את יסודות המכירה מאפס","tier":1},
     {"t":"להריץ את התנועה ואת הצוות, יום-יום","tier":2},
     {"t":"בעלות מלאה על ההכנסות: מכירות, שיווק ו-GTM","tier":3}]},
   {"q":"יש לכם צוות מכירות?","opts":[
     {"t":"אין צוות. צריך לגייס, להכשיר ולנהל נציגים","sdr":1},
     {"t":"יש צוות שצריך הנהגה","sdr":0},
     {"t":"עדיין לא בטוח","sdr":0}]},
   {"q":"כמה SDRs להתחלה?","reps":True,"opts":[
     {"t":"נציג אחד","reps":1},{"t":"שני נציגים","reps":2},{"t":"3+ נציגים","reps":3}]},
   {"q":"ומה עם שיווק?","opts":[
     {"t":"השיווק מטופל","mk":0,"mkname":"","mkout":""},
     {"t":"מישהו מריץ אבל צריך פיקוח","mk":4000,"mkname":"פיקוח שיווק","mkout":"פיקוח שיווקי בכיר, ששומר על התקציב והעדיפויות מיושרים למכירות"},
     {"t":"צריך מישהו שיהיה אחראי על השיווק","mk":8000,"mkname":"סמנכ״ל שיווק","mkout":"פונקציית שיווק ומשפך מלאים, בניהול מקצה לקצה"}]},
   {"q":"רוצים שנקבע לכם פגישות מכירה? (תשלום לפי פגישה)","opts":[
     {"t":"לא, תודה","ppm":0},
     {"t":"עד 3 בחודש","ppm":3000},
     {"t":"4 עד 6 בחודש","ppm":4500},
     {"t":"7 עד 14 בחודש","ppm":6500},
     {"t":"15+ בחודש","ppm":9000}]}],
 "calc_ppm_line":"פגישות שנקבעו (תשלום לפי פגישה)",
 "calc_ppm_outcome":"פגישות מכירה מוכשרות ביומן שלכם, בתשלום לפי פגישה",
 "calc_ppm_setup_label":"הקמה חד פעמית להשקת הקמפיין",
 "calc_ppm_rec_name":"פיתוח מכירות בתשלום לפי פגישה",
}

def render_pricing_body(d, cal):
    book = d["book"]
    star = ('<a href="#perf" title="%s" style="color:#E67E22;text-decoration:none;font-weight:800;'
            'font-size:1.15rem;vertical-align:super;line-height:0;margin-left:3px">&#9733;</a>'
            ) % esc(d.get("perf", {}).get("star_title", "")) if d.get("perf") else ""
    def card(t, mark=False):
        badge = ('<span class="badge">%s</span>' % esc(t["badge"])) if t.get("badge") else '<span class="badge badge-empty">&nbsp;</span>'
        feat = " feat" if t.get("feat") else ""
        lis = "".join("<li>%s</li>" % esc(x) for x in t["incl"])
        return ('<div class="tier%s">%s<span class="commit">%s</span><h3>%s</h3>'
                '<div class="amount">%s<span> %s</span>%s</div><p class="bestfor">%s</p>'
                '<ul class="incl">%s</ul></div>'
                ) % (feat, badge, esc(t["commit"]), esc(t["name"]), esc(t["price"]), esc(t["per"]),
                     star if mark else "", esc(t["bestfor"]), lis)
    out = []
    out.append('      <h2>%s</h2>' % esc(d["cro_h"]))
    out.append('      <div class="price-grid cols4">%s</div>' % "".join(card(t, mark=True) for t in d["cro"]))
    if d.get("perf"):
        out.append('      <p style="color:#E67E22;font-size:.9rem;margin-top:14px">%s <a href="#perf" style="color:#E67E22">%s</a></p>'
                   % (esc(d["perf"]["star_note"]), esc(d["perf"]["star_link"])))
    out.append('      <h2 class="price-h2">%s</h2>' % esc(d["sdr_h"]))
    left = ('<div class="tier"><span class="commit">%s</span><h3>%s</h3><p class="bestfor">%s</p><ul class="incl">%s</ul></div>'
            ) % (esc(d["add_label"]), esc(d["sdr_name"]), esc(d["sdr_desc"]),
                 "".join("<li>%s</li>" % esc(x) for x in d["sdr_incl"]))
    right = ('<div class="tier feat"><span class="commit">%s</span><div class="amount">%s<span> %s</span>%s</div>'
             '<ul class="incl">%s</ul><p class="price-note">%s</p></div>'
             ) % (esc(d["sdr_price_label"]), esc(d["sdr_amount"]), esc(d["sdr_amount_per"]), star,
                  "".join("<li>%s</li>" % esc(x) for x in d["sdr_tiers"]), esc(d["sdr_price_note"]))
    out.append('      <div class="price-grid cols2">%s%s</div>' % (left, right))
    if d.get("ppm_price"):
        out.append('      <h2 class="price-h2">%s</h2>' % esc(d["ppm_h"]))
        out.append('      <p class="bestfor">%s</p>' % esc(d["ppm_desc"]))
        out.append('      ' + d["ppm_price"])
        out.append('      <p class="price-note">%s <a href="%s" style="color:var(--blue);font-weight:600">%s</a>.</p>'
                   % (esc(d["ppm_more"]), d["ppm_url"], esc(d["ppm_more_link"])))
    out.append('      <h2 class="price-h2">%s</h2>' % esc(d["mk_h"]))
    out.append('      <div class="price-grid cols2">%s</div>' % "".join(card(t) for t in d["marketing"]))
    # performance-share banner (added on top of the fixed fees)
    p = d.get("perf")
    if p:
        items = "".join(
            ('<div style="flex:1 1 180px;background:#10151e;border:1px solid rgba(255,255,255,.10);'
             'border-radius:14px;padding:22px 18px;text-align:center">'
             '<div style="font-weight:800;font-size:2.4rem;line-height:1;color:#E67E22">%s</div>'
             '<div style="color:#fff;font-weight:600;font-size:.95rem;margin-top:8px">%s</div>'
             '<div style="color:var(--soft);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin-top:8px">%s</div>'
             '</div>') % (esc(a), esc(of), esc(who))
            for a, of, who in p["items"])
        out.append(
            '      <h2 class="price-h2" id="perf">%s</h2>' % esc(p["h"]))
        out.append(
            '      <div class="perf-banner" style="background:radial-gradient(80%% 130%% at 18%% 0%%,#0c2237 0%%,#0a0e14 60%%);'
            'border:1px solid rgba(90,176,255,.35);border-radius:18px;padding:30px 28px;margin-top:16px">'
            '<p style="color:var(--soft);margin:0 0 20px;max-width:640px">%s</p>'
            '<div style="display:flex;gap:16px;flex-wrap:wrap">%s</div>'
            '<p class="price-note" style="margin-top:20px">%s</p></div>'
            % (esc(p["sub"]), items, esc(p["note"])))
    # quote calculator (outcomes-based questionnaire)
    def _num(p):
        return int(p.replace("$", "").replace(",", ""))
    tiers = [{"name": t["name"], "price": _num(t["price"]), "commit": t["commit"],
              "outcome": d["calc_tier_outcomes"][i], "why": t["bestfor"]} for i, t in enumerate(d["cro"])]
    mkq = d["calc_q"][3]["opts"]
    mk_list = [{"mk": o.get("mk", 0), "name": o.get("mkname", ""), "out": o.get("mkout", "")} for o in mkq]
    labels = {"recommended": d["calc_recommended"], "outcome_h": d["calc_outcome_h"],
              "cost_h": d["calc_cost_h"], "prompt": d["calc_prompt"], "mo": d["calc_mo"],
              "sdr_outcome": d["calc_sdr_outcome"], "sdr_word1": d["calc_sdr_word1"], "sdr_wordN": d["calc_sdr_wordN"], "sdr_line": d["calc_sdr_line"], "book_url": "https://calendly.com/ksw/15min",
              "book": d["calc_book"], "quote_title": d["calc_quote_title"], "terms": d["calc_note"],
              "print": d["calc_print"], "lang": d["calc_lang"], "dir": d["calc_dir"],
              "brand": "TAL PAPERIN", "tagline": d["calc_tagline"], "site": "talpaperin.com",
              "result_note": d["calc_result_note"], "none": d["calc_none_label"]}
    if d.get("perf"):
        labels["perf_h"] = d["perf"]["h"]
        labels["perf_items"] = ["%s %s (%s)" % (a, of, who) for a, of, who in d["perf"]["items"]]
        labels["perf_note"] = d["perf"]["note"]
    labels["ppm_line"] = d.get("calc_ppm_line", "")
    labels["ppm_outcome"] = d.get("calc_ppm_outcome", "")
    labels["ppm_setup_label"] = d.get("calc_ppm_setup_label", "")
    labels["ppm_rec_name"] = d.get("calc_ppm_rec_name", "")
    qhtml = ""
    for q in d["calc_q"]:
        cls = " qc-q-reps" if q.get("reps") else ""
        chips = ""
        for o in q["opts"]:
            data = ""
            if "tier" in o:
                data += ' data-set="tier" data-tier="%d"' % o["tier"]
            if "sdr" in o:
                data += ' data-set="team" data-sdr="%d"' % o["sdr"]
            if "reps" in o:
                data += ' data-set="reps" data-reps="%d"' % o["reps"]
            if "mk" in o:
                data += ' data-set="mk" data-mk="%d" data-mkname="%s" data-mkout="%s"' % (o["mk"], esc(o["mkname"]), esc(o["mkout"]))
            if "ppm" in o:
                data += ' data-set="ppm" data-ppm="%d"' % o["ppm"]
            chips += '<button type="button" class="qc-chip"%s>%s</button>' % (data, esc(o["t"]))
        qhtml += '<div class="qc-q%s"><p class="qc-q-label">%s</p><div class="qc-chips">%s</div></div>' % (cls, esc(q["q"]), chips)
    cro_scale = '<div class="qc-scale">' + "".join('<span>%s</span>' % esc(t["name"]) for t in d["cro"]) + '</div>'
    sdr_scale = '<div class="qc-scale"><span>0</span><span>3</span><span>6</span></div>'
    mk_names = [d["calc_none_label"]] + [o.get("mkname", "") for o in mkq[1:]]
    mk_scale = '<div class="qc-scale">' + "".join('<span>%s</span>' % esc(n) for n in mk_names) + '</div>'
    sliders = ('<div class="qc-sliders" hidden><p class="qc-sub-h">%s</p>'
               '<div class="qc-slider"><label>%s: <span class="qc-cro-val"></span></label><input type="range" class="qc-cro-range" min="0" max="3" step="1" value="0" />%s</div>'
               '<div class="qc-slider"><label>%s: <span class="qc-sdr-val"></span></label><input type="range" class="qc-sdr-range" min="0" max="6" step="1" value="0" />%s</div>'
               '<div class="qc-slider"><label>%s: <span class="qc-mk-val"></span></label><input type="range" class="qc-mk-range" min="0" max="2" step="1" value="0" />%s</div></div>'
               ) % (esc(d["calc_sliders_h"]), esc(d["calc_slider_cro"]), cro_scale, esc(d["calc_slider_sdr"]), sdr_scale, esc(d["calc_slider_mk"]), mk_scale)
    out.append('      <h2 class="price-h2">%s</h2>' % esc(d["calc_h"]))
    out.append('      <div class="quote-calc" data-subject="%s" data-sdr-r1="6000" data-sdr-r2="11000" data-sdr-r3="5000" data-ppm-setup="2500" data-tiers="%s" data-labels="%s" data-marketing="%s">'
               '<p class="bestfor">%s</p>%s'
               '<div class="qc-result" aria-live="polite"><p class="qc-prompt">%s</p></div>'
               '%s'
               '<div class="qc-fields"><input class="qc-name" placeholder="%s" autocomplete="name" /><input class="qc-email" type="email" placeholder="%s" autocomplete="email" /><input class="qc-company" placeholder="%s" autocomplete="organization" /></div>'
               '<div class="qc-actions"><button type="button" class="btn btn-secondary qc-download">%s</button>'
               '<a class="btn btn-primary qc-email-btn" href="mailto:tal@ksw.solutions">%s</a>'
               '<a class="btn btn-secondary qc-book" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">%s</a></div>'
               '<p class="price-note">%s</p></div>'
               % (esc(d["calc_subject"]), esc(json.dumps(tiers, ensure_ascii=False)), esc(json.dumps(labels, ensure_ascii=False)), esc(json.dumps(mk_list, ensure_ascii=False)),
                  esc(d["calc_intro"]), qhtml, esc(d["calc_prompt"]), sliders,
                  esc(d["calc_name"]), esc(d["calc_email"]), esc(d["calc_company"]),
                  esc(d["calc_download"]), esc(d["calc_email_btn"]), esc(d["calc_book"]),
                  esc(d["calc_note"])))
    out.append('      <h2 class="price-h2">%s</h2>' % esc(d["faq_h"]))
    faq = "".join('<h3>%s</h3><p>%s</p>' % (esc(q), esc(a)) for q, a in d["faq"])
    out.append('      <div class="price-faq">%s</div>' % faq)
    out.append('      <script src="/quote.js" defer></script>')
    return out


def pricing_ldblock(url, he):
    d = PRICING_HE if he else PRICING_EN
    ents = ",".join('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                    % (_jsonesc(q), _jsonesc(a)) for q, a in d["faq"])
    offers = ([(t["name"], _price_num(t["price"])) for t in d["cro"]]
              + [(d["sdr_name"], _price_num(d["sdr_amount"]))]
              + [(t["name"], _price_num(t["price"])) for t in d["marketing"]])
    graph = graph_ld(he, offers=offers)
    page = ('{"@context":"https://schema.org","@type":"WebPage","@id":"%s#webpage",'
            '"url":"%s","name":"Pricing","isPartOf":{"@id":"%s"},'
            '"about":{"@id":"%s"}}') % (url, url, WEBSITE_ID, BUSINESS_ID)
    return ('%s\n'
            '  <script type="application/ld+json">%s</script>\n'
            '  <script type="application/ld+json">{"@context":"https://schema.org",'
            '"@type":"FAQPage","mainEntity":[%s]}</script>') % (graph, page, ents)


PRICING_TPL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pricing: Fractional CRO, SDR Teams and Marketing | Tal Paperin</title>
  <meta name="description" content="Straight monthly pricing for fractional CRO leadership, dedicated SDR teams and marketing leadership. Advisor to full CRO ownership. No long contracts, no exit fines." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/pricing" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/pricing" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/pricing" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/pricing" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/pricing" />
  <meta property="og:title" content="Pricing: Fractional CRO, SDR Teams and Marketing | Tal Paperin" />
  <meta property="og:description" content="Straight monthly pricing for fractional CRO leadership, SDR teams and marketing leadership. No long contracts." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Pricing | Tal Paperin" />
  <meta name="twitter:description" content="Straight monthly pricing for fractional CRO, SDR teams and marketing leadership." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/blog/blog.css" />

  {analytics}

  {ldblock}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="blog-head">
        <div class="glowline"></div>
        <p class="eyebrow">Pricing</p>
        <h1>Straight pricing. No proposals, no games.</h1>
        <p>Every engagement is built around one thing: a revenue number you can rely on. Whether I advise you a few hours a week or own the whole engine full-time, you are buying an outcome, not hours, and never a slide deck. <a href="/services/">See what each engagement includes</a>.</p>
        <p class="price-outcomes-h">What every engagement is built to deliver</p>
        <ul class="price-outcomes">
          <li>A repeatable go-to-market motion that creates demand instead of waiting for it</li>
          <li>A sales team that performs, hired, trained and managed to a standard</li>
          <li>A pipeline you can actually forecast, with a CRM and process behind it</li>
          <li>Revenue that compounds month over month, and a number someone finally owns</li>
        </ul>
        <p>Pick the level of ownership you need below. Monthly, no long contracts, no exit fines.</p>
        <p style="margin-top:22px"><a class="btn btn-secondary" href="/services/">See all services &rarr;</a></p>
      </div>
{body}
{cta}
      <div class="svc-related">See <a href="/services/">what each engagement includes</a>, the <a href="/fractional-cro-cost">cost breakdown</a>, or <a href="/case-studies">the results</a>.</div>
    </div>
  </main>

{footer}
</body>
</html>
"""

PRICING_TPL_HE = """<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>תמחור: סמנכ״ל מכירות, צוותי SDR ושיווק | טל פאפרין</title>
  <meta name="description" content="תמחור חודשי ברור להנהגת מכירות במיקור חוץ, צוותי SDR ייעודיים והובלת שיווק. מ-Advisor ועד בעלות CRO מלאה. בלי חוזים ארוכים, בלי קנסות יציאה." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/pricing" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/pricing" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/pricing" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/pricing" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/pricing" />
  <meta property="og:title" content="תמחור: סמנכ״ל מכירות, צוותי SDR ושיווק | טל פאפרין" />
  <meta property="og:description" content="תמחור חודשי ברור להנהגת מכירות, צוותי SDR והובלת שיווק. בלי חוזים ארוכים." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta property="og:locale" content="he_IL" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="תמחור | טל פאפרין" />
  <meta name="twitter:description" content="תמחור חודשי ברור להנהגת מכירות, צוותי SDR והובלת שיווק." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}

  {ldblock}
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="blog-head">
        <div class="glowline"></div>
        <p class="eyebrow">תמחור</p>
        <h1>תמחור ישר. בלי הצעות מחיר, בלי משחקים.</h1>
        <p>כל התקשרות נבנית סביב דבר אחד: מספר הכנסות שאפשר לסמוך עליו. בין אם אני מלווה אתכם כמה שעות בשבוע ובין אם אני מנהל את כל המנוע במשרה מלאה, אתם קונים תוצאה, לא שעות, ובטח לא מצגת. <a href="/he/services/">ראו מה כל שירות כולל</a>.</p>
        <p class="price-outcomes-h">מה כל התקשרות נבנית לספק</p>
        <ul class="price-outcomes">
          <li>מנוע Go-to-Market חוזר שמייצר ביקוש במקום לחכות לו</li>
          <li>צוות מכירות שמבצע, מגויס, מוכשר ומנוהל לפי סטנדרט</li>
          <li>פייפליין שאפשר באמת לחזות, עם CRM ותהליך מאחוריו</li>
          <li>הכנסה שגדלה מחודש לחודש, ומספר שמישהו סוף סוף אחראי עליו</li>
        </ul>
        <p>בחרו למטה את רמת הבעלות שאתם צריכים. חודשי, בלי חוזים ארוכים, בלי קנסות יציאה.</p>
        <p style="margin-top:22px"><a class="btn btn-secondary" href="/he/services/">לכל השירותים &larr;</a></p>
      </div>
{body}
{cta}
      <div class="svc-related">ראו <a href="/he/services/">מה כל שירות כולל</a>, את <a href="/he/case-studies">התוצאות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.</div>
    </div>
  </main>

{footer}
</body>
</html>
"""


def build():
    os.makedirs(SVC_DIR, exist_ok=True)
    he_dir = os.path.join(ROOT, "he", "services")
    os.makedirs(he_dir, exist_ok=True)

    # English service pages
    for svc in SERVICES:
        url = "%s/services/%s" % (SITE, svc["slug"])
        he_url = "%s/he/services/%s" % (SITE, svc["slug"])
        hreflang = ('  <link rel="alternate" hreflang="en" href="%s" />\n'
                    '  <link rel="alternate" hreflang="he" href="%s" />\n'
                    '  <link rel="alternate" hreflang="x-default" href="%s" />') % (url, he_url, url)
        ld = ('{"@context":"https://schema.org","@type":"Service",'
              '"name":"%s","description":"%s","serviceType":"%s",'
              '"provider":{"@id":"%s"},'
              '"areaServed":[{"@type":"Country","name":"United States"},{"@type":"Country","name":"Israel"}],'
              '"url":"%s","mainEntityOfPage":"%s"}'
              ) % (esc(svc["h1"]), esc(svc["desc"]), esc(svc["nav"]), BUSINESS_ID, url, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
                 '{"@type":"ListItem","position":2,"name":"Services","item":"%s/services/"},'
                 '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
                 ) % (SITE, SITE, esc(svc["h1"]), url)
        page = PAGE.format(graph=graph_ld(False),
            title=esc(svc["title"]), desc=esc(svc["desc"]), url=url, site=SITE,
            h1=esc(svc["h1"]), eyebrow=esc(svc["eyebrow"]), lead=esc(svc["lead"]),
            sections=render_sections(svc), related=render_related(svc["slug"]),
            case=render_case_callout(SERVICE_CASE_EN.get(svc["slug"]), "Case study", "Result", "See more case studies", "/case-studies"),
            faq=render_faq(SERVICE_FAQS_EN.get(svc["slug"]))[0],
            faqld=render_faq(SERVICE_FAQS_EN.get(svc["slug"]))[1],
            fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER, cta=CTA_BOX,
            ld=ld, crumb=crumb, hreflang=hreflang)
        with open(os.path.join(SVC_DIR, svc["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    cards = []
    for svc in SERVICES:
        cards.append(
            '        <a class="svc-card" href="/services/%s">\n'
            '          <h2>%s</h2>\n          <p>%s</p>\n'
            '          <span class="more">Learn more &rarr;</span>\n        </a>'
            % (svc["slug"], esc(svc["h1"]), esc(svc["card"])))
    with open(os.path.join(SVC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX.format(site=SITE, fonts=FONTS, analytics=ANALYTICS,
                             nav=NAV, footer=FOOTER, cards="\n".join(cards),
                             graph=graph_ld(False), gallery=render_gallery()))

    # Hebrew service pages
    for svc in HE_SERVICES:
        url = "%s/he/services/%s" % (SITE, svc["slug"])
        en = "%s/services/%s" % (SITE, svc["slug"])
        ld = ('{"@context":"https://schema.org","@type":"Service",'
              '"name":"%s","description":"%s","serviceType":"%s","inLanguage":"he",'
              '"provider":{"@id":"%s"},'
              '"areaServed":[{"@type":"Country","name":"United States"},{"@type":"Country","name":"Israel"}],'
              '"url":"%s","mainEntityOfPage":"%s"}'
              ) % (esc(svc["h1"]), esc(svc["desc"]), esc(svc["nav"]), BUSINESS_ID, url, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"בית","item":"%s/he/"},'
                 '{"@type":"ListItem","position":2,"name":"שירותים","item":"%s/he/services/"},'
                 '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
                 ) % (SITE, SITE, esc(svc["h1"]), url)
        page = HE_PAGE.format(graph=graph_ld(True),
            title=esc(svc["title"]), desc=esc(svc["desc"]), url=url, en=en, site=SITE,
            h1=esc(svc["h1"]), eyebrow=esc(svc["eyebrow"]), lead=esc(svc["lead"]),
            sections=render_sections(svc), related=render_he_related(svc["slug"]),
            case=render_case_callout(SERVICE_CASE_HE.get(svc["slug"]), "מקרה לקוח", "תוצאה", "לעוד מקרי מבחן", "/he/case-studies"),
            faq=render_faq(SERVICE_FAQS_HE.get(svc["slug"]), "שאלות נפוצות")[0],
            faqld=render_faq(SERVICE_FAQS_HE.get(svc["slug"]), "שאלות נפוצות")[1],
            fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER, cta=HE_CTA,
            ld=ld, crumb=crumb)
        with open(os.path.join(he_dir, svc["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    he_cards = []
    for svc in HE_SERVICES:
        he_cards.append(
            '        <a class="svc-card" href="/he/services/%s">\n'
            '          <h2>%s</h2>\n          <p>%s</p>\n'
            '          <span class="more">קרא עוד &larr;</span>\n        </a>'
            % (svc["slug"], esc(svc["h1"]), esc(svc["card"])))
    with open(os.path.join(he_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(HE_INDEX.format(site=SITE, fonts=HE_FONTS, analytics=ANALYTICS,
                                nav=HE_NAV, footer=HE_FOOTER, cards="\n".join(he_cards),
                                graph=graph_ld(True), gallery=render_gallery("טל פאפרין בשטח")))

    # Hebrew FAQ / challenges pillar page
    items_html = []
    faq_entities = []
    for q, ans in HE_FAQ["items"]:
        items_html.append("        <h2>%s</h2>" % esc(q))
        for a in ans:
            items_html.append("        <p>%s</p>" % a)
        atext = " ".join(re.sub(r"<[^>]+>", "", a) for a in ans)
        faq_entities.append('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                            % (_jsonesc(q), _jsonesc(atext)))
    faqld = '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % ",".join(faq_entities)
    with open(os.path.join(ROOT, "he", "challenges.html"), "w", encoding="utf-8") as f:
        f.write(HE_FAQPAGE.format(
            title=esc(HE_FAQ["title"]), desc=esc(HE_FAQ["desc"]), site=SITE,
            h1=esc(HE_FAQ["h1"]), eyebrow=esc(HE_FAQ["eyebrow"]), lead=esc(HE_FAQ["lead"]),
            items="\n".join(items_html), cta=HE_CTA, faqld=faqld,
            fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER))

    with open(os.path.join(ROOT, "contact.html"), "w", encoding="utf-8") as f:
        f.write(CONTACT_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER, graph=graph_ld(False), contactjs=CONTACT_JS_EN))
    with open(os.path.join(ROOT, "he", "contact.html"), "w", encoding="utf-8") as f:
        f.write(CONTACT_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER, graph=graph_ld(True), contactjs=CONTACT_JS_HE))

    with open(os.path.join(ROOT, "about.html"), "w", encoding="utf-8") as f:
        f.write(ABOUT_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                graph=graph_ld(False), gallery=render_gallery(), cta=CTA_BOX, career=IG_CAREER_EN))
    with open(os.path.join(ROOT, "he", "about.html"), "w", encoding="utf-8") as f:
        f.write(ABOUT_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                graph=graph_ld(True), gallery=render_gallery("טל פאפרין בשטח"), cta=HE_CTA, career=IG_CAREER_HE))

    with open(os.path.join(ROOT, "pricing.html"), "w", encoding="utf-8") as f:
        f.write(PRICING_TPL.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                cta=CTA_BOX, ldblock=pricing_ldblock(SITE + "/pricing", False),
                body="\n".join(render_pricing_body(PRICING_EN, "https://calendly.com/ksw/15min"))))
    with open(os.path.join(ROOT, "he", "pricing.html"), "w", encoding="utf-8") as f:
        f.write(PRICING_TPL_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                cta=HE_CTA, ldblock=pricing_ldblock(SITE + "/he/pricing", True),
                body="\n".join(render_pricing_body(PRICING_HE, "https://calendly.com/ksw/15min"))))

    # The case-studies marquee is a teaser: drop the longest outlier quotes so the
    # strip stays a sensible height. The full set lives on the recommendations page.
    cs_idx = [i for i, t in enumerate(TESTIMONIALS_EN) if len(t["q"]) <= 330]
    cs_en = [TESTIMONIALS_EN[i] for i in cs_idx]
    cs_he = [TESTIMONIALS_HE[i] for i in cs_idx]

    with open(os.path.join(ROOT, "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                  graph=graph_ld(False),
                                  cases=render_cases(CASE_STUDIES, "Result"),
                                  testimonials=render_testimonials(cs_en),
                                  gallery=render_gallery(), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                  graph=graph_ld(True),
                                  cases=render_cases(HE_CASES, "תוצאה"),
                                  testimonials=render_testimonials(cs_he, he=True),
                                  gallery=render_gallery("טל פאפרין בשטח"), cta=HE_CTA))

    with open(os.path.join(ROOT, "recommendations.html"), "w", encoding="utf-8") as f:
        f.write(REC_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                   graph=graph_ld(False),
                                   logos=render_logo_wall(LOGOS),
                                   quotes=render_quote_grid(TESTIMONIALS_EN), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "recommendations.html"), "w", encoding="utf-8") as f:
        f.write(REC_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                   graph=graph_ld(True),
                                   logos=render_logo_wall(LOGOS),
                                   quotes=render_quote_grid(TESTIMONIALS_HE, he=True), cta=HE_CTA))

    # Lead-focused SEO landing pages (root level, e.g. /fractional-cro-cost)
    for g in GUIDES:
        url = "%s/%s" % (SITE, g["slug"])
        he_url = "%s/he/%s" % (SITE, g["slug"])
        if g.get("en_only"):
            hreflang = ('  <link rel="alternate" hreflang="en" href="%s" />\n'
                        '  <link rel="alternate" hreflang="x-default" href="%s" />') % (url, url)
        else:
            hreflang = ('  <link rel="alternate" hreflang="en" href="%s" />\n'
                        '  <link rel="alternate" hreflang="he" href="%s" />\n'
                        '  <link rel="alternate" hreflang="x-default" href="%s" />') % (url, he_url, url)
        ld = guide_ld(g, url, he=False)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
                 '{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}'
                 ) % (SITE, esc(g["h1"]), url)
        faq_html, faq_ld = render_faq(g.get("faqs"))
        page = GUIDE_PAGE.format(graph=graph_ld(False),
            title=esc(g["title"]), desc=esc(g["desc"]), url=url, site=SITE,
            h1=esc(g["h1"]), eyebrow=esc(g["eyebrow"]), lead=esc(g["lead"]),
            sections=render_guide_sections(g), faq=faq_html, faqld=faq_ld,
            related=g["related"], fonts=FONTS, analytics=ANALYTICS, nav=NAV,
            footer=FOOTER, cta=CTA_BOX, ld=ld, crumb=crumb, hreflang=hreflang)
        with open(os.path.join(ROOT, g["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    # Hebrew lead pages (e.g. /he/fractional-cro-cost)
    for g in HE_GUIDES:
        url = "%s/he/%s" % (SITE, g["slug"])
        en_url = "%s/%s" % (SITE, g["slug"])
        hreflang = ('  <link rel="alternate" hreflang="he" href="%s" />\n'
                    '  <link rel="alternate" hreflang="en" href="%s" />\n'
                    '  <link rel="alternate" hreflang="x-default" href="%s" />') % (url, en_url, en_url)
        ld = guide_ld(g, url, he=True)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"בית","item":"%s/he/"},'
                 '{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}'
                 ) % (SITE, esc(g["h1"]), url)
        faq_html, faq_ld = render_faq(g.get("faqs"), "שאלות נפוצות")
        page = HE_GUIDE_PAGE.format(graph=graph_ld(True),
            title=esc(g["title"]), desc=esc(g["desc"]), url=url, site=SITE,
            h1=esc(g["h1"]), eyebrow=esc(g["eyebrow"]), lead=esc(g["lead"]),
            sections=render_guide_sections(g), faq=faq_html, faqld=faq_ld,
            related=g["related"], fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV,
            footer=HE_FOOTER, cta=HE_CTA, ld=ld, crumb=crumb, hreflang=hreflang)
        with open(os.path.join(ROOT, "he", g["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    # Guides hub (links all guides so they are not orphans)
    with open(os.path.join(ROOT, "guides.html"), "w", encoding="utf-8") as f:
        f.write(HUB_PAGE_EN.format(site=SITE, fonts=FONTS, analytics=ANALYTICS,
                                   nav=NAV, footer=FOOTER, groups=render_guides_hub(False)))
    with open(os.path.join(ROOT, "he", "guides.html"), "w", encoding="utf-8") as f:
        f.write(HUB_PAGE_HE.format(site=SITE, fonts=HE_FONTS, analytics=ANALYTICS,
                                   nav=HE_NAV, footer=HE_FOOTER, groups=render_guides_hub(True)))

    print("Built %d EN + %d HE service pages, HE index, HE FAQ, %d guides + %d HE guides"
          % (len(SERVICES), len(HE_SERVICES), len(GUIDES), len(HE_GUIDES)))


if __name__ == "__main__":
    build()
