#!/usr/bin/env python3
"""
Static service-page generator for talpaperin.com.

Generates /services/index.html and one SEO-optimized page per service,
reusing the blog's dark-theme stylesheet (/blog/blog.css). Run:

  python3 services/build.py

Service URLs are also pulled into sitemap.xml and llms.txt by blog/build.py,
so run this first, then blog/build.py.
"""

import os
import re
import html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVC_DIR = os.path.join(ROOT, "services")
SITE = "https://talpaperin.com"

ANALYTICS = ('<script src="https://analytics.ahrefs.com/analytics.js" '
             'data-key="yw4L2JvlOTPBX9ieFq8jZg" async></script>')
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Anton&'
         'family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />')

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

NAV = '''  <nav class="site">
    <div class="inner">
      <a class="brand" href="/">TAL PAPERIN</a>
      <div class="navlinks">
        <a href="/">Home</a>
        <a href="/services/">Services</a>
        <a href="/case-studies">Case Studies</a>
        <a href="/blog/">Blog</a>
        <a href="/contact">Contact</a>
      </div>
      <div class="nav-right">
        <a class="btn btn-solid" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">Book a Call</a>
        <button class="navtoggle" aria-label="Menu" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 Tal Paperin. All rights reserved.</span>
      <span>Fractional CRO &middot; US market focus &middot; US business hours</span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
  </script>'''

CTA_BOX = '''      <div class="cta-box">
        <h3>Tell me where revenue stalled. I'll tell you why.</h3>
        <p>A 15-minute call, no pitch. You will leave with at least one concrete thing to fix, whether or not we work together.</p>
        <a class="btn btn-solid" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">Book a 15-Minute Call</a>
      </div>'''


# --- Service content -------------------------------------------------------

SERVICES = [
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
      "Week one I diagnose where deals stall and leak. Week two you have a plan and a real forecast. Week three I am running it. You get a senior operator who has done this 30-plus times on four continents, not a strategy deck that sits in a drawer."]},
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
  ]},

 {"slug":"go-to-market-strategy","nav":"Go-To-Market Strategy","h1":"Go-To-Market Strategy",
  "title":"Go-To-Market Strategy Consultant | Tal Paperin",
  "desc":"A go-to-market strategy you can actually execute. ICP, positioning, channels, playbook and a real forecast, then I help you run it.",
  "eyebrow":"Service",
  "lead":"Most GTM decks die in a drawer. I build a plan with targets and timelines, then lead the execution with you.",
  "card":"ICP, positioning, channels, playbook and a real forecast, then I lead the execution, not just the slides.",
  "sections":[
    {"h":"What a real GTM plan includes","ul":[
      "A validated ICP, positioning and messaging, not a guess you wrote down once",
      "The right markets and channels for your stage",
      "An executable playbook: talk tracks, decision criteria, the outbound motion",
      "A real forecast with milestones, not a hope"]},
    {"h":"Strategy is not enough","p":[
      "I do not stop at the slide deck. I build the plan, then lead the execution with you, until you have pipeline, partners and first sales. From the high-level plan to the work in the field, I am there."]},
    {"h":"Across markets","p":[
      "North America, the EU, Eastern and Central Europe, and APAC. I have opened markets others wrote off, and I know the expensive mistakes before you make them."]},
  ]},

 {"slug":"sales-team-building","nav":"Team Building","h1":"Sales Team Building and Training",
  "title":"Sales Team Building and Training | Tal Paperin",
  "desc":"Build a sales team that actually closes. I hire, train and manage SDRs, AEs and BDs, and replace who can't.",
  "eyebrow":"Service",
  "lead":"Reps who can't close are not a people problem. They are a system problem. I build the team and the system that makes them hit quota.",
  "card":"Hire, train and manage SDRs, AEs and BDs on a playbook that makes them hit quota. Replace who can't, fast.",
  "sections":[
    {"h":"What I do","ul":[
      "Recruit and hire SDRs, AEs, BDs, post-sales and tech support",
      "Build a training plan tailored to your ICP and your GTM",
      "Manage the team day to day until they hit quota",
      "Replace who can't, fast, before they burn a year"]},
    {"h":"In-house or outsourced","p":[
      "I build it inside your company, or bring a ready team through KSW Solutions. Either way you get a sales org that runs on a playbook, not on hope."]},
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
      "I have signed two of the largest DIY retail chains in a region a global manufacturer had written off, and built distributor networks across the FSU, the EU and APAC. Partners are not a logo on a slide. They are revenue, if you pick and manage them right."]},
  ]},

 {"slug":"market-entry","nav":"Market Entry","h1":"International Market Entry",
  "title":"International Market Entry Consultant | Tal Paperin",
  "desc":"Break into new markets without the expensive mistakes. Market-entry strategy and execution across the US, EU, Eastern Europe and APAC.",
  "eyebrow":"Service",
  "lead":"Entering a new market is where companies burn the most money. I have done it across four continents, and I know the mistakes before you make them.",
  "card":"Market-entry strategy and execution across North America, the EU, Eastern Europe and APAC. Including B2G and complex deals.",
  "sections":[
    {"h":"What I do","ul":[
      "Market-entry strategy and a milestone-by-milestone plan",
      "The right territories, channels and decision-makers",
      "Lead the negotiations and close the first deals personally",
      "Build the local presence, direct or through partners"]},
    {"h":"Markets I know","p":[
      "North America, the EU, Eastern and Central Europe, and APAC. I proved there was real money in Eastern Europe for a company convinced there was none, and put product on shelves in a market they had abandoned."]},
    {"h":"B2G and complex deals","p":[
      "I also run B2G and complex public-sector deals, RFIs, RFQs and government projects, across the globe."]},
  ]},
]


def esc(s):
    return html.escape(s, quote=True)


def render_sections(svc):
    out = []
    for sec in svc["sections"]:
        out.append("        <h2>%s</h2>" % esc(sec["h"]))
        for p in sec.get("p", []):
            out.append("        <p>%s</p>" % esc(p))
        if sec.get("ul"):
            out.append("        <ul>")
            for li in sec["ul"]:
                out.append("          <li>%s</li>" % esc(li))
            out.append("        </ul>")
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

  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/services/">Services</a></p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
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
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Services</p>
        <h1>What I do.</h1>
        <p class="lead">Six ways I fix and run revenue. Pick the one that matches your problem, or just tell me where it hurts and I will point you to the right one.</p>
      </div>
      <div class="svc-grid">
{cards}
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


# --- Hebrew (RTL) ----------------------------------------------------------

HE_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            '  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800;900&'
            'family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet" />')

HE_NAV = '''  <nav class="site">
    <div class="inner">
      <a class="brand" href="/he/">טל פאפרין</a>
      <div class="navlinks">
        <a href="/he/">בית</a>
        <a href="/he/services/">שירותים</a>
        <a href="/he/case-studies">מקרי מבחן</a>
        <a href="/blog/">בלוג</a>
        <a href="/he/contact">צור קשר</a>
      </div>
      <div class="nav-right">
        <a class="btn btn-solid" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">תיאום שיחה</a>
        <button class="navtoggle" aria-label="תפריט" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

HE_FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 טל פאפרין. כל הזכויות שמורות.</span>
      <span>Fractional CRO &middot; התמחות בשוק האמריקאי &middot; עבודה בשעות פעילות ארה״ב</span>
    </div>
  </footer>

  <a class="wa-float" href="https://wa.me/972545308119" target="_blank" rel="noopener" aria-label="שיחה בוואטסאפ">''' + WA_SVG + '''</a>

  <script>
    var nt=document.querySelector('.navtoggle');
    if(nt){nt.addEventListener('click',function(){var n=document.querySelector('nav.site');var o=n.classList.toggle('open');nt.setAttribute('aria-expanded',o);});
    document.querySelectorAll('.navlinks a').forEach(function(a){a.addEventListener('click',function(){document.querySelector('nav.site').classList.remove('open');});});}
  </script>'''

HE_CTA = '''      <div class="cta-box">
        <h3>ספרו לי איפה המכירות נתקעו. אני אגיד לכם למה.</h3>
        <p>שיחה של 15 דקות, בלי ניסיונות מכירה. תצאו ממנה עם לפחות דבר אחד פרקטי לתקן, בין אם נעבוד יחד ובין אם לא.</p>
        <a class="btn btn-solid" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">תיאום שיחה של 15 דקות</a>
      </div>'''

HE_SERVICES = [
 {"slug":"fractional-cro","nav":"Fractional CRO","h1":"Fractional CRO",
  "title":"Fractional CRO, מנהל הכנסות במיקור חוץ | טל פאפרין",
  "desc":"מנהל הכנסות (CRO) במיקור חוץ שיושב על הכיסא ולוקח בעלות על המספר. אסטרטגיה, צוות, פייפליין ותחזית, בלי גיוס יקר של משרה מלאה.",
  "eyebrow":"שירות",
  "lead":"מנהיגות הכנסות בכירה, על הכיסא, שלוקחת אחריות על המספר. בלי משכורת של רבע מיליון דולר ובלי התחייבות ארוכת טווח.",
  "card":"אני יושב על הכיסא, מנהל את ההכנסות ולוקח אחריות על המספר. שלב הביניים שרוב החברות בוחרות בו.",
  "sections":[
    {"h":"מתי צריך Fractional CRO?",
     "p":["אתם צריכים שיקול דעת ברמת CRO, אבל הנפח עדיין לא מצדיק משרה מלאה. או שאתם צריכים תוצאות עכשיו ולא יכולים לחכות שני רבעונים שמישהו חדש יתחמם. בדיוק לפער הזה נכנס Fractional CRO."],
     "ul":["המכירות נתקעו ואף אחד לא באמת אחראי על המספר","אתם בצמיחה וצריכים מנהיג עוד לפני שאפשר להצדיק CRO במשרה מלאה","CRO שכיר עולה רבע מיליון דולר ומעלה בשנה, עם חודשים של גיוס וחימום וסיכוני פיצויים"]},
    {"h":"על מה אני לוקח בעלות",
     "ul":["אסטרטגיית ההכנסות, התחזית והאחריות, מקצה לקצה","תנועת ה-Go-to-Market, הפייפליין והצוות שמריץ אותם","שיווק שבאמת מזין את הפייפליין, לא רק מייצר פעילות","ההחלטות הקשות: את מי לגייס, את מי להכשיר ואת מי להחליף"]},
    {"h":"איך זה עובד",
     "p":["בשבוע הראשון אני מאבחן איפה העסקאות נתקעות ודולפות. בשבוע השני יש לכם תוכנית ותחזית אמיתית. בשבוע השלישי אני כבר מריץ אותה. אתם מקבלים מנהל מנוסה שעשה את זה יותר מ-30 פעם בארבע יבשות, לא עוד מצגת אסטרטגיה שנשארת במגירה."]},
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
  ]},

 {"slug":"go-to-market-strategy","nav":"אסטרטגיית GTM","h1":"אסטרטגיית Go-To-Market",
  "title":"אסטרטגיית Go-To-Market ותוכנית שיווק בינלאומית | טל פאפרין",
  "desc":"אסטרטגיית Go-To-Market שאפשר באמת לבצע. ICP, מיצוב, ערוצים, Playbook ותחזית אמיתית, ואז אני מוביל איתכם את הביצוע.",
  "eyebrow":"שירות",
  "lead":"רוב מצגות ה-GTM מתות במגירה. אני בונה תוכנית עם יעדים ולוחות זמנים, ואז מוביל איתכם את הביצוע.",
  "card":"ICP, מיצוב, ערוצים, Playbook ותחזית אמיתית, ואז אני מוביל את הביצוע, לא רק את השקפים.",
  "sections":[
    {"h":"מה כוללת תוכנית GTM אמיתית",
     "ul":["ICP מתוקף, מיצוב ומסרים, לא ניחוש שרשמתם פעם אחת","השווקים והערוצים הנכונים לשלב שלכם","Playbook בר-ביצוע: תסריטי שיחה, קריטריונים להחלטה ותנועת אאוטבאונד","תחזית אמיתית עם אבני דרך, לא תקווה"]},
    {"h":"אסטרטגיה זה לא מספיק",
     "p":["אני לא עוצר במצגת. אני בונה את התוכנית, ואז מוביל איתכם את הביצוע, עד שיש פייפליין, שותפים ומכירות ראשונות. מהתכנון הגבוה ועד העבודה בשטח, אני שם."]},
    {"h":"לרוחב השווקים",
     "p":["צפון אמריקה, האיחוד האירופי, מזרח ומרכז אירופה ו-APAC. פתחתי שווקים שאחרים מחקו, ואני מכיר את הטעויות היקרות לפני שאתם עושים אותן."]},
  ]},

 {"slug":"sales-team-building","nav":"בניית צוות","h1":"בניית והכשרת צוות מכירות",
  "title":"בניית והכשרת צוות מכירות | טל פאפרין",
  "desc":"לבנות צוות מכירות שבאמת סוגר. אני מגייס, מכשיר ומנהל SDRs, AEs ו-BDs, ומחליף את מי שלא מתאים.",
  "eyebrow":"שירות",
  "lead":"אנשי מכירות שלא סוגרים זו לא בעיה של אנשים. זו בעיה של שיטה. אני בונה את הצוות ואת השיטה שגורמים להם לפגוע ביעד.",
  "card":"גיוס, הכשרה וניהול של SDRs, AEs ו-BDs על Playbook שמביא אותם ליעד. החלפה מהירה של מי שלא מתאים.",
  "sections":[
    {"h":"מה אני עושה",
     "ul":["גיוס והשמה של SDRs, AEs, BDs, שירות שלאחר מכירה ותמיכה טכנית","בניית תוכנית הכשרה מותאמת ל-ICP ול-GTM שלכם","ניהול הצוות יום-יום עד שהוא פוגע ביעד","החלפה מהירה של מי שלא מתאים, לפני שהוא שורף שנה"]},
    {"h":"בתוך החברה או במיקור חוץ",
     "p":["אני בונה את זה בתוך החברה שלכם, או מביא צוות מוכן דרך KSW Solutions. כך או כך אתם מקבלים מערך מכירות שרץ על Playbook, לא על תקווה."]},
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
     "p":["החתמתי שתיים מרשתות ה-DIY הגדולות באזור שיצרן גלובלי כבר מחק, ובניתי רשתות מפיצים ב-FSU, באיחוד האירופי וב-APAC. שותפים הם לא לוגו על שקף. הם הכנסות, אם בוחרים ומנהלים אותם נכון."]},
  ]},

 {"slug":"market-entry","nav":"חדירה לשווקים","h1":"חדירה לשווקים בינלאומיים",
  "title":"חדירה לשווקים בינלאומיים | טל פאפרין",
  "desc":"לפרוץ לשווקים חדשים בלי הטעויות היקרות. אסטרטגיית חדירה וביצוע בארה״ב, באיחוד האירופי, במזרח אירופה ו-APAC.",
  "eyebrow":"שירות",
  "lead":"כניסה לשוק חדש זה המקום שבו חברות שורפות הכי הרבה כסף. עשיתי את זה בארבע יבשות, ואני מכיר את הטעויות לפני שאתם עושים אותן.",
  "card":"אסטרטגיית חדירה וביצוע בצפון אמריקה, באיחוד האירופי, במזרח אירופה ו-APAC. כולל B2G ועסקאות מורכבות.",
  "sections":[
    {"h":"מה אני עושה",
     "ul":["אסטרטגיית חדירה ותוכנית לפי אבני דרך","הטריטוריות, הערוצים ומקבלי ההחלטות הנכונים","הובלת המשא ומתן וסגירת העסקאות הראשונות באופן אישי","בניית נוכחות מקומית, ישירה או דרך שותפים"]},
    {"h":"השווקים שאני מכיר",
     "p":["צפון אמריקה, האיחוד האירופי, מזרח ומרכז אירופה ו-APAC. הוכחתי שיש כסף אמיתי במזרח אירופה לחברה שהייתה בטוחה שאין, והבאתי מוצר למדפים בשוק שהיא כבר נטשה."]},
    {"h":"B2G ועסקאות מורכבות",
     "p":["אני גם מנהל עסקאות B2G ועסקאות מורכבות מול המגזר הציבורי, מכרזים, RFIs, RFQs ופרויקטים ממשלתיים, בכל העולם."]},
  ]},
]

HE_FAQ = {
 "slug": "challenges",
 "title": "אתגרי השיווק והמכירות הבינלאומיים, המדריך | טל פאפרין",
 "desc": "המדריך הישיר לחדירה לשווקים בינלאומיים: מוכנות, לקוחות ראשונים, מפיצים, Fractional CRO מול VP במשרה מלאה, ותחרות מול הענקים.",
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
    'עד שמנוע המכירות עובד ומזין לידים, <a href="/he/services/fractional-cro">Fractional CRO</a> או מנהל מכירות במיקור חוץ נותן לכם את אותה מנהיגות בכירה בשבריר מהעלות: בלי משכורת, בלי תנאים סוציאליים ובלי סיכון פיצויים. כשהמשפך מתמלא, אז שוכרים משרה מלאה.']),
  ('איך מאתרים ובוחרים את המפיצים הנכונים?',
   ['המפיץ הראשון שפנה אליכם הוא כמעט אף פעם לא הנכון. חתימה על הסכם עם מי שמזדמן זה מתכון לחודשים של שקט מצדו ותירוצים מצדכם.',
    'קודם מגדירים אילו פונקציות המפיץ צריך למלא, בונים פרופיל של מפיץ אידיאלי, ורק אז מאתרים. מפיץ טוב גם בודק אתכם, ואם תשתית השיווק והמכירות שלכם חלשה הוא לא יתחבר. אני <a href="/he/services/distributor-channel-recruitment">בונה את התשתית ומנהל את התהליך</a> נכון.']),
  ('איך מתחרים בענקים הגלובליים עם כל המשאבים?',
   ['לא מנצחים אותם בתקציב. מנצחים אותם במיקוד. הענקים לא רוצים או לא יכולים לתפור פתרון לנישה ספציפית, ושם בדיוק יש לכם יתרון.',
    'מזהים קבוצת לקוחות עם כאב משותף שאתם פותרים טוב מכולם, מנסחים USP חד, ונלחמים על הלקוח האסטרטגי הראשון, גם אם מתפשרים על המחיר. אחריו באים האחרים.']),
  ('כמה זמן לוקח לראות תוצאות?',
   ['אצלי, מהר. אבחון בשבוע הראשון, תוכנית בשבוע השני, ביצוע מהשבוע השלישי. אני לא מוכר מצגת, אני לוקח בעלות על המספר.']),
  ('מה ההבדל בינך לבין יועץ שיווק?',
   ['יועץ נותן לכם המלצות והולך. אני נכנס, בונה את מערך המכירות, מגייס ומנהל את הצוות, סוגר עסקאות בעצמי ולוקח אחריות על התוצאה. <a href="/he/services/">Fractional CRO, לא יועץ מהצד</a>.']),
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

  <script type="application/ld+json">{ld}</script>
  <script type="application/ld+json">{crumb}</script>
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <p class="breadcrumb"><a href="/he/">בית</a> / <a href="/he/services/">שירותים</a></p>
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{sections}
{cta}
        <div class="svc-related">שירותים נוספים: {related} &middot; <a href="/blog/">לבלוג</a></div>
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
  <title>שירותים: Fractional CRO, מכירות במיקור חוץ ו-GTM | טל פאפרין</title>
  <meta name="description" content="איך אני מתקן ומריץ מכירות: Fractional CRO, מכירות במיקור חוץ, אסטרטגיית Go-To-Market, בניית צוות מכירות, גיוס מפיצים וחדירה לשווקים בינלאומיים." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{site}/he/services/" />
  <link rel="alternate" hreflang="en" href="{site}/services/" />
  <link rel="alternate" hreflang="he" href="{site}/he/services/" />
  <link rel="alternate" hreflang="x-default" href="{site}/services/" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="{site}/he/services/" />
  <meta property="og:title" content="שירותים | טל פאפרין" />
  <meta property="og:description" content="Fractional CRO, מכירות במיקור חוץ, GTM, בניית צוות, גיוס מפיצים וחדירה לשווקים." />
  <meta property="og:image" content="{site}/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">שירותים</p>
        <h1>מה אני עושה.</h1>
        <p class="lead">שש דרכים שבהן אני מתקן ומריץ מכירות. בחרו את זו שמתאימה לבעיה שלכם, או <a href="/he/challenges">קראו את המדריך</a> ותגלו איפה כואב.</p>
      </div>
      <div class="svc-grid">
{cards}
      </div>
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

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{items}
{cta}
        <div class="svc-related">קראו עוד: <a href="/he/services/">השירותים שלי</a> &middot; <a href="/blog/">הבלוג</a></div>
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
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Contact</p>
        <h1>Let's talk.</h1>
        <p class="lead">Tell me where revenue stalled. Book a call, send a message, or reach me directly. I read everything.</p>

        <div class="contact-buttons">
          <a class="btn btn-outline" href="mailto:tal@ksw.solutions">Email</a>
          <a class="btn btn-outline" href="tel:+972545308119">Call</a>
          <a class="btn btn-outline" href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">LinkedIn</a>
        </div>

        <div class="contact-grid">
          <div>
            <h2>Send a message</h2>
            <form action="https://api.web3forms.com/submit" method="POST" class="contact-form">
              <input type="hidden" name="access_key" value="REPLACE_WITH_ACCESS_KEY" />
              <input type="hidden" name="subject" value="New message from talpaperin.com" />
              <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off" />
              <input type="text" name="name" placeholder="Name" required />
              <input type="email" name="email" placeholder="Email" required />
              <input type="text" name="company" placeholder="Company (optional)" />
              <textarea name="message" placeholder="Where did revenue stall?" required></textarea>
              <button class="btn btn-solid" type="submit">Send message</button>
            </form>
          </div>
          <div>
            <h2>Or book a 15-minute call</h2>
            <div class="calendly-inline-widget cal-embed" data-url="https://calendly.com/ksw/15min"></div>
          </div>
        </div>
      </div>
    </div>
  </main>

{footer}
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
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
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">צור קשר</p>
        <h1>בואו נדבר.</h1>
        <p class="lead">ספרו לי איפה המכירות נתקעו. תאמו שיחה, שלחו הודעה, או צרו קשר ישיר. אני קורא הכל.</p>

        <div class="contact-buttons">
          <a class="btn btn-outline" href="mailto:tal@ksw.solutions">מייל</a>
          <a class="btn btn-outline" href="tel:+972545308119">טלפון</a>
          <a class="btn btn-outline" href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">לינקדאין</a>
        </div>

        <div class="contact-grid">
          <div>
            <h2>שליחת הודעה</h2>
            <form action="https://api.web3forms.com/submit" method="POST" class="contact-form">
              <input type="hidden" name="access_key" value="REPLACE_WITH_ACCESS_KEY" />
              <input type="hidden" name="subject" value="הודעה חדשה מ-talpaperin.com" />
              <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off" />
              <input type="text" name="name" placeholder="שם" required />
              <input type="email" name="email" placeholder="אימייל" required />
              <input type="text" name="company" placeholder="חברה (אופציונלי)" />
              <textarea name="message" placeholder="איפה המכירות נתקעו?" required></textarea>
              <button class="btn btn-solid" type="submit">שליחת הודעה</button>
            </form>
          </div>
          <div>
            <h2>או תיאום שיחה של 15 דקות</h2>
            <div class="calendly-inline-widget cal-embed" data-url="https://calendly.com/ksw/15min"></div>
          </div>
        </div>
      </div>
    </div>
  </main>

{footer}
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
</body>
</html>
'''


CASE_STUDIES = [
 {"company":"KanduAI","meta":"AI SaaS startup, Fractional VP of Sales",
  "situation":"An early-stage AI startup with no sales engine. They needed someone to build it from day one, then it survived a full product pivot.",
  "did":["Owned go-to-market end to end as fractional VP of Sales from day one","Defined and validated the ICP, positioning and messaging","Built the outbound playbook and motion from zero","Hired, trained and managed the SDR team","Relaunched the entire go-to-market through the pivot, twice"],
  "result":"A working outbound engine, rebuilt from scratch through a pivot, with speed and precision."},
 {"company":"LoneStar Tracking","meta":"Founder-led IoT business, Outsourced sales leadership",
  "situation":"Strong marketing, but a sales engine that was not converting, and founders with little sales experience.",
  "did":["Built the entire sales strategy and motion from scratch","Selected and implemented the CRM and the sales stack","Built the process, the playbook and the pipeline","Recruited, hired and trained the sales team","Ran the team and the motion day to day"],
  "result":"Full VP-level sales leadership at a fraction of the cost of a hire."},
 {"company":"Bacsoft","meta":"Israeli IIoT, backed by Japan's SUN Corp, VP of Global Sales",
  "situation":"An IIoT company that needed a global sales strategy, a channel network, and the ability to win complex public-sector deals.",
  "did":["Owned the global sales strategy","Recruited and managed distributors worldwide","Ran direct B2B sales of SaaS, hardware and services","Led B2G: RFIs, RFQs and complex government projects across the globe","Managed marketing and marcom"],
  "result":"A global channel and a B2G pipeline built for a company selling complex IIoT internationally."},
 {"company":"Palram","meta":"Global manufacturer, Eastern Europe market entry",
  "situation":"A global manufacturer convinced there was no money in Eastern Europe, so they stayed out.",
  "did":["Built the market-entry strategy and milestone plan","Mapped the channel and the real decision-makers on the ground","Led every negotiation personally","Signed two of the region's largest DIY retail chains"],
  "result":"Product on shelves in a market the company had written off, proving there was real money in Eastern Europe."},
 {"company":"BT9","meta":"IoT and SaaS, International sales across FSU, EU and APAC",
  "situation":"A company that needed an entire international sales operation built from the ground up.",
  "did":["Built an international sales operation from zero across the FSU, the EU and APAC","Ran direct sales of SaaS, hardware and services","Recruited and managed the distributor network","Hired, trained and ran the team day to day: SDRs, post-sales and tech support"],
  "result":"A working international sales engine across three regions, built from scratch."},
 {"company":"TAG Medical","meta":"Medical devices, International sales and marketing, EU",
  "situation":"A medical device manufacturer expanding into the EU that needed both a sales motion and a marketing function.",
  "did":["Ran international sales across the EU","Drove direct B2B sales of medical equipment","Recruited and managed distributors","Built and ran the entire marketing department, online and offline"],
  "result":"A sales and marketing engine for medical devices across European markets."},
 {"company":"SOURCE Vagabond","meta":"Consumer products, North American retail",
  "situation":"An Israeli brand that needed to crack large US retailers and big-box chains.",
  "did":["Sold direct to large retailers and big-box stores across North America","Recruited and managed distributors"],
  "result":"Product into major North American retail, from an unknown overseas brand."},
 {"company":"Synergix","meta":"Scientific SaaS, North America",
  "situation":"A scientific SaaS company selling to a hard, technical US buyer: universities, research labs and pharma.",
  "did":["Drove direct B2B SaaS sales to universities, research facilities and pharma companies","Wrote the sales scripts and the playbook the reps used","Led and motivated the sales effort"],
  "result":"SaaS sold into US academia and pharma, a long, technical, high-trust sale."},
]

HE_CASES = [
 {"company":"KanduAI","meta":"סטארטאפ AI SaaS, VP מכירות במיקור חוץ",
  "situation":"סטארטאפ AI בתחילת הדרך בלי מנוע מכירות. היו צריכים מישהו שיבנה אותו מהיום הראשון, ואז המוצר עבר פיבוט מלא.",
  "did":["לקחתי בעלות מלאה על ה-GTM כ-VP מכירות במיקור חוץ מהיום הראשון","הגדרתי ותיקפתי את ה-ICP, המיצוב והמסרים","בניתי את ה-Playbook ותנועת האאוטבאונד מאפס","גייסתי, הכשרתי וניהלתי את צוות ה-SDR","השקתי מחדש את כל ה-GTM דרך הפיבוט, פעמיים"],
  "result":"מנוע אאוטבאונד עובד, שנבנה מחדש מאפס דרך פיבוט, במהירות ובדיוק."},
 {"company":"LoneStar Tracking","meta":"עסק IoT בהובלת מייסדים, הובלת מכירות במיקור חוץ",
  "situation":"שיווק חזק, אבל מנוע מכירות שלא המיר, ומייסדים עם מעט ניסיון במכירות.",
  "did":["בניתי את כל אסטרטגיית ותהליכי המכירה מאפס","בחרתי והטמעתי CRM ומערך כלי מכירה","בניתי תהליך, Playbook ופייפליין","גייסתי, הכשרתי ובניתי את צוות המכירות","ניהלתי את הצוות ואת התנועה יום-יום"],
  "result":"הובלת מכירות מלאה ברמת VP בשבריר מעלות של גיוס."},
 {"company":"Bacsoft","meta":"חברת IIoT ישראלית בגיבוי SUN Corp מיפן, VP מכירות גלובלי",
  "situation":"חברת IIoT שהייתה צריכה אסטרטגיית מכירות גלובלית, רשת מפיצים ויכולת לזכות בעסקאות מורכבות מול המגזר הציבורי.",
  "did":["לקחתי בעלות על אסטרטגיית המכירות הגלובלית","גייסתי וניהלתי מפיצים בכל העולם","הרצתי מכירה ישירה B2B של SaaS, חומרה ושירותים","הובלתי B2G: מכרזים, RFIs, RFQs ופרויקטים ממשלתיים מורכבים בכל העולם","ניהלתי את השיווק וה-Marcom"],
  "result":"רשת ערוצים גלובלית ופייפליין B2G שנבנו לחברה שמוכרת IIoT מורכב בעולם."},
 {"company":"Palram","meta":"יצרן גלובלי, חדירה לשוק במזרח אירופה",
  "situation":"יצרן גלובלי שהיה בטוח שאין כסף במזרח אירופה, ולכן נמנע מלהיכנס.",
  "did":["בניתי את אסטרטגיית החדירה ותוכנית אבני הדרך","מיפיתי את הערוץ ואת מקבלי ההחלטות האמיתיים בשטח","ניהלתי כל משא ומתן באופן אישי","חתמתי על שתיים מרשתות ה-DIY הגדולות באזור"],
  "result":"מוצר על המדפים בשוק שהחברה כבר מחקה, והוכחה שיש שם כסף אמיתי."},
 {"company":"BT9","meta":"IoT ו-SaaS, מכירות בינלאומיות ב-FSU, באיחוד האירופי וב-APAC",
  "situation":"חברה שהייתה צריכה מערך מכירות בינלאומי שלם שייבנה מאפס.",
  "did":["בניתי מערך מכירות בינלאומי מאפס ב-FSU, באיחוד האירופי וב-APAC","הרצתי מכירה ישירה של SaaS, חומרה ושירותים","גייסתי וניהלתי את רשת המפיצים","גייסתי, הכשרתי וניהלתי את הצוות יום-יום: SDR, פוסט-סייל ותמיכה טכנית"],
  "result":"מנוע מכירות בינלאומי עובד בשלוש טריטוריות, שנבנה מאפס."},
 {"company":"TAG Medical","meta":"מכשור רפואי, מכירות ושיווק בינלאומיים באיחוד האירופי",
  "situation":"יצרן מכשור רפואי שהתרחב לאיחוד האירופי וצריך גם מערך מכירות וגם מחלקת שיווק.",
  "did":["ניהלתי מכירות בינלאומיות בכל האיחוד האירופי","הובלתי מכירה ישירה B2B של ציוד רפואי","גייסתי וניהלתי מפיצים","בניתי וניהלתי את כל מחלקת השיווק, אונליין ואופליין"],
  "result":"מערך מכירות ושיווק למכשור רפואי בשווקים האירופיים."},
 {"company":"SOURCE Vagabond","meta":"מוצרי צריכה, קמעונאות בצפון אמריקה",
  "situation":"מותג ישראלי שהיה צריך לפרוץ לקמעונאים הגדולים ולרשתות ה-Big Box בארה״ב.",
  "did":["מכרתי ישירות לקמעונאים גדולים ולרשתות Big Box בכל צפון אמריקה","גייסתי וניהלתי מפיצים"],
  "result":"מוצר לתוך הקמעונאות הגדולה בצפון אמריקה, ממותג זר לא מוכר."},
 {"company":"Synergix","meta":"SaaS מדעי, צפון אמריקה",
  "situation":"חברת SaaS מדעית שמכרה ללקוח אמריקאי קשה וטכני: אוניברסיטאות, מעבדות מחקר וחברות פארמה.",
  "did":["הובלתי מכירה ישירה B2B של SaaS לאוניברסיטאות, מוסדות מחקר וחברות פארמה","כתבתי את תסריטי המכירה ואת ה-Playbook שהנציגים השתמשו בהם","הובלתי והנעתי את צוות המכירות"],
  "result":"SaaS שנמכר לאקדמיה ולפארמה בארה״ב, מכירה ארוכה, טכנית ועתירת אמון."},
]


def render_cases(cases, rlabel):
    out = []
    for c in cases:
        lis = "".join("<li>%s</li>" % esc(x) for x in c["did"])
        out.append('      <div class="case-study">\n'
                    '        <h2>%s</h2>\n        <div class="meta">%s</div>\n'
                    '        <p class="situation">%s</p>\n        <ul>%s</ul>\n'
                    '        <div class="result"><span>%s</span>%s</div>\n      </div>'
                    % (esc(c["company"]), esc(c["meta"]), esc(c["situation"]), lis,
                       esc(rlabel), esc(c["result"])))
    return "\n".join(out)


CS_PAGE_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Case Studies | Tal Paperin, Fractional CRO</title>
  <meta name="description" content="Real results from a fractional CRO: building sales engines, opening markets and closing complex deals for B2B companies across startups, IoT, manufacturing, medical and SaaS, on four continents." />
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
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Case Studies</p>
        <h1>Brought in to build the engine, not advise on it.</h1>
        <p class="lead">Real companies, real problems, real ownership. Here is what I have built and fixed, across startups, IoT, manufacturing, medical devices, retail and SaaS, on four continents.</p>
        <div class="cases-list">
{cases}
        </div>
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
  <title>מקרי מבחן | טל פאפרין, Fractional CRO</title>
  <meta name="description" content="תוצאות אמיתיות: בניית מנועי מכירות, פתיחת שווקים וסגירת עסקאות מורכבות לחברות B2B, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי ו-SaaS, בארבע יבשות." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/case-studies" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/case-studies" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/case-studies" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/case-studies" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/he/case-studies" />
  <meta property="og:title" content="מקרי מבחן | טל פאפרין" />
  <meta property="og:description" content="חברות אמיתיות, בעיות אמיתיות, בעלות אמיתית. מנועי מכירות שנבנו, שווקים שנפתחו, עסקאות מורכבות שנסגרו." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="טל פאפרין" />
  <meta property="og:locale" content="he_IL" />

  {fonts}
  <link rel="stylesheet" href="/he/he-pages.css" />

  {analytics}
</head>
<body>
{nav}

  <main class="page">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">מקרי מבחן</p>
        <h1>הגעתי כדי לבנות את המנוע, לא לייעץ עליו.</h1>
        <p class="lead">חברות אמיתיות, בעיות אמיתיות, בעלות אמיתית. הנה מה שבניתי ותיקנתי, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי, קמעונאות ו-SaaS, בארבע יבשות.</p>
        <div class="cases-list">
{cases}
        </div>
{cta}
        <div class="svc-related">ראו את <a href="/he/services/">השירותים</a> שמאחורי אלה, או <a href="/blog/">קראו את הבלוג</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


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
              '"provider":{"@type":"Person","name":"Tal Paperin","url":"%s/"},'
              '"areaServed":"Worldwide","url":"%s"}'
              ) % (esc(svc["h1"]), esc(svc["desc"]), esc(svc["nav"]), SITE, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
                 '{"@type":"ListItem","position":2,"name":"Services","item":"%s/services/"},'
                 '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
                 ) % (SITE, SITE, esc(svc["h1"]), url)
        page = PAGE.format(
            title=esc(svc["title"]), desc=esc(svc["desc"]), url=url, site=SITE,
            h1=esc(svc["h1"]), eyebrow=esc(svc["eyebrow"]), lead=esc(svc["lead"]),
            sections=render_sections(svc), related=render_related(svc["slug"]),
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
                             nav=NAV, footer=FOOTER, cards="\n".join(cards)))

    # Hebrew service pages
    for svc in HE_SERVICES:
        url = "%s/he/services/%s" % (SITE, svc["slug"])
        en = "%s/services/%s" % (SITE, svc["slug"])
        ld = ('{"@context":"https://schema.org","@type":"Service",'
              '"name":"%s","description":"%s","serviceType":"%s",'
              '"provider":{"@type":"Person","name":"טל פאפרין","url":"%s/he/"},'
              '"areaServed":"Worldwide","url":"%s"}'
              ) % (esc(svc["h1"]), esc(svc["desc"]), esc(svc["nav"]), SITE, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"בית","item":"%s/he/"},'
                 '{"@type":"ListItem","position":2,"name":"שירותים","item":"%s/he/services/"},'
                 '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
                 ) % (SITE, SITE, esc(svc["h1"]), url)
        page = HE_PAGE.format(
            title=esc(svc["title"]), desc=esc(svc["desc"]), url=url, en=en, site=SITE,
            h1=esc(svc["h1"]), eyebrow=esc(svc["eyebrow"]), lead=esc(svc["lead"]),
            sections=render_sections(svc), related=render_he_related(svc["slug"]),
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
                                nav=HE_NAV, footer=HE_FOOTER, cards="\n".join(he_cards)))

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
        f.write(CONTACT_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER))
    with open(os.path.join(ROOT, "he", "contact.html"), "w", encoding="utf-8") as f:
        f.write(CONTACT_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER))

    with open(os.path.join(ROOT, "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                  cases=render_cases(CASE_STUDIES, "Result"), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                  cases=render_cases(HE_CASES, "תוצאה"), cta=HE_CTA))

    print("Built %d EN + %d HE service pages, HE index and HE FAQ"
          % (len(SERVICES), len(HE_SERVICES)))


if __name__ == "__main__":
    build()
