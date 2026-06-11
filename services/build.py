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
      </div>
      <div class="nav-right">
        <a class="btn btn-solid" href="/contact">Let's Talk</a>
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
      "I have signed multiple distributors and retail chains across a region a global manufacturer had written off, and built distributor networks across the FSU, the EU and APAC. Partners are not a logo on a slide. They are revenue, if you pick and manage them right."]},
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
    {"h":"How it works","p":["I step into the live deal, get the full picture fast, and lead it to signature. Twenty years of closing complex B2B and B2G agreements across four continents means I have seen the tactics before they are used on you."]},
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
{case}
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
      </div>
      <div class="nav-right">
        <a class="btn btn-solid" href="/he/contact">בואו נדבר</a>
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
     "p":["החתמתי מספר מפיצים ורשתות קמעונאות באזור שיצרן גלובלי כבר מחק, ובניתי רשתות מפיצים ב-FSU, באיחוד האירופי וב-APAC. שותפים הם לא לוגו על שקף. הם הכנסות, אם בוחרים ומנהלים אותם נכון."]},
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
  ]},

 {"slug":"contract-negotiation","nav":"משא ומתן","h1":"ניהול משא ומתן על חוזים",
  "title":"ניהול משא ומתן על חוזים B2B | טל פאפרין",
  "desc":"לקחת פיקוד על המשא ומתן ולסגור את ההסכמים המורכבים והגדולים. אני מוביל את העסקאות שמזיזות את המספר.",
  "eyebrow":"שירות",
  "lead":"עסקאות גדולות מתמסמסות במשא ומתן. אני לוקח פיקוד על המשא ומתן וסוגר את ההסכמים המורכבים והרווחיים.",
  "card":"אני לוקח פיקוד על המשא ומתן וסוגר את העסקאות המורכבות והגדולות שמזיזות את המספר.",
  "sections":[
    {"h":"מתי צריך את זה","p":["העסקאות הכי גדולות שלכם הן אלה שאתם הכי לא יכולים להרשות לעצמכם להפסיד, ואלה שהכי נוטות להיתקע במשא ומתן: מחיר, תנאים, משפטי, רכש, וקונה שמריח היסוס."],
     "ul":["עסקאות גדולות נתקעות שוב ושוב בשלב המשא ומתן","הצוות שלכם חזק במכירה אבל לא בסגירת התנאים הקשים","אתם צריכים יד יציבה על העסקאות הכי חשובות"]},
    {"h":"מה אני עושה","ul":["לקיחת פיקוד על המשא ומתן בעסקאות המורכבות והגדולות שלכם","החזקת מחיר ותנאים בלי לאבד את העסקה","ניהול הרכש, המשפטי ומקבלי ההחלטות","סגירת ההסכמים שבאמת מזיזים את המספר"]},
    {"h":"איך זה עובד","p":["אני נכנס לעסקה החיה, קולט את התמונה המלאה מהר, ומוביל אותה עד החתימה. 20 שנה של סגירת הסכמים מורכבים B2B ו-B2G בארבע יבשות, אני מכיר את הטקטיקות עוד לפני שמפעילים אותן עליכם."]},
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
{case}
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

        <div class="contact-cols">
          <div class="contact-card">
            <h2>Send a message</h2>
            <p class="contact-sub">We read every one. Replies within one business day.</p>
            <form class="cf-form" onsubmit="return submitForm(event)">
              <input type="text" id="cf-hp" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0" />
              <input type="hidden" id="cf-loaded" value="" />
              <label for="cf-name">Your name</label>
              <input id="cf-name" type="text" name="name" required />
              <label for="cf-email">Email</label>
              <input id="cf-email" type="email" name="email" required autocomplete="email" />
              <label for="cf-message">Message</label>
              <textarea id="cf-message" name="message" required></textarea>
              <button class="btn btn-solid" type="submit">Send Message &rarr;</button>
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

        <div class="contact-cols">
          <div class="contact-card">
            <h2>שליחת הודעה</h2>
            <p class="contact-sub">אנחנו קוראים כל אחת. מענה תוך יום עסקים אחד.</p>
            <form class="cf-form" onsubmit="return submitForm(event)">
              <input type="text" id="cf-hp" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0" />
              <input type="hidden" id="cf-loaded" value="" />
              <label for="cf-name">שם</label>
              <input id="cf-name" type="text" name="name" required />
              <label for="cf-email">אימייל</label>
              <input id="cf-email" type="email" name="email" required autocomplete="email" />
              <label for="cf-message">הודעה</label>
              <textarea id="cf-message" name="message" required></textarea>
              <button class="btn btn-solid" type="submit">שליחת הודעה &larr;</button>
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
    function openCal(){if(window.Calendly){Calendly.initPopupWidget({url:'https://calendly.com/ksw/15min'});return false;}return true;}
    function cfDone(f,m){var els=f.querySelectorAll('input,textarea,button,label');for(var i=0;i<els.length;i++){els[i].style.display='none';}m.hidden=false;m.style.color='var(--blue)';m.textContent='Thanks. Your message is on its way, I will reply within one business day.';}
    function submitForm(e){e.preventDefault();var f=e.target,m=f.querySelector('.cf-msg'),b=f.querySelector('button');
      if(f.querySelector('#cf-hp').value){cfDone(f,m);return false;}
      var loaded=parseInt(f.querySelector('#cf-loaded').value||'0',10);
      if(loaded&&Date.now()-loaded<3000){cfDone(f,m);return false;}
      var n=f.querySelector('[name=name]').value,em=f.querySelector('[name=email]').value,msg=f.querySelector('[name=message]').value;
      b.disabled=true;b.textContent='Sending...';
      fetch('https://formspree.io/f/xykbgowb',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({name:n,email:em,message:msg})})
        .then(function(r){if(r.ok){cfDone(f,m);}else{b.disabled=false;b.textContent='Send Message';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please email tal@ksw.solutions.';}})
        .catch(function(){b.disabled=false;b.textContent='Send Message';m.hidden=false;m.style.color='#ff9a9a';m.textContent='Something went wrong. Please email tal@ksw.solutions.';});
      return false;}
  </script>'''

CONTACT_JS_HE = '''  <link rel="stylesheet" href="https://assets.calendly.com/assets/external/widget.css" />
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
  <script>
    (function(){var cl=document.getElementById('cf-loaded');if(cl)cl.value=String(Date.now());})();
    function openCal(){if(window.Calendly){Calendly.initPopupWidget({url:'https://calendly.com/ksw/15min'});return false;}return true;}
    function cfDone(f,m){var els=f.querySelectorAll('input,textarea,button,label');for(var i=0;i<els.length;i++){els[i].style.display='none';}m.hidden=false;m.style.color='var(--blue)';m.textContent='תודה. ההודעה שלך בדרך, אענה תוך יום עסקים אחד.';}
    function submitForm(e){e.preventDefault();var f=e.target,m=f.querySelector('.cf-msg'),b=f.querySelector('button');
      if(f.querySelector('#cf-hp').value){cfDone(f,m);return false;}
      var loaded=parseInt(f.querySelector('#cf-loaded').value||'0',10);
      if(loaded&&Date.now()-loaded<3000){cfDone(f,m);return false;}
      var n=f.querySelector('[name=name]').value,em=f.querySelector('[name=email]').value,msg=f.querySelector('[name=message]').value;
      b.disabled=true;b.textContent='שולח...';
      fetch('https://formspree.io/f/xykbgowb',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({name:n,email:em,message:msg})})
        .then(function(r){if(r.ok){cfDone(f,m);}else{b.disabled=false;b.textContent='שליחת הודעה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. אפשר לכתוב ל-tal@ksw.solutions.';}})
        .catch(function(){b.disabled=false;b.textContent='שליחת הודעה';m.hidden=false;m.style.color='#ff9a9a';m.textContent='משהו השתבש. אפשר לכתוב ל-tal@ksw.solutions.';});
      return false;}
  </script>'''


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
  "did":["Built the market-entry strategy and milestone plan","Mapped the channel and the real decision-makers on the ground","Led every negotiation personally","Signed multiple distributors and retail chains across the region"],
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
  "did":["בניתי את אסטרטגיית החדירה ותוכנית אבני הדרך","מיפיתי את הערוץ ואת מקבלי ההחלטות האמיתיים בשטח","ניהלתי כל משא ומתן באופן אישי","החתמתי מספר מפיצים ורשתות קמעונאות באזור"],
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


LOGO_MAP = {"KanduAI":"kanduai","LoneStar Tracking":"lonestar","Bacsoft":"bacsoft",
            "Palram":"palram","BT9":"bt9","SOURCE Vagabond":"source"}


def render_cases(cases, rlabel):
    out = []
    for c in cases:
        logo = LOGO_MAP.get(c["company"], "")
        img = ('<img class="cs-logo" src="/logos/%s.jpg" alt="%s" loading="lazy" />\n        '
               % (logo, esc(c["company"]))) if logo else ""
        lis = "".join("<li>%s</li>" % esc(x) for x in c["did"])
        out.append('      <div class="case-study">\n        %s'
                    '<h2>%s</h2>\n        <div class="meta">%s</div>\n'
                    '        <p class="situation">%s</p>\n        <ul>%s</ul>\n'
                    '        <div class="result"><span>%s</span>%s</div>\n      </div>'
                    % (img, esc(c["company"]), esc(c["meta"]), esc(c["situation"]), lis,
                       esc(rlabel), esc(c["result"])))
    return "\n".join(out)


def _initials(name):
    parts = [p for p in re.split(r"[\s.,\"']+", name) if p and p[0].isalpha()]
    a = parts[0][0] if parts else "?"
    b = parts[1][0] if len(parts) > 1 else ""
    return (a + b).upper()


def render_testimonials(quotes):
    cards = []
    for txt, name, who in quotes:
        wholine = (", " + esc(who)) if who else ""
        cards.append('<div class="quote"><p>"%s"</p><div class="who">'
                     '<span class="qavatar">%s</span>'
                     '<span class="qwho"><strong>%s</strong>%s</span></div></div>'
                     % (esc(txt), esc(_initials(name)), esc(name), wholine))
    inner = "".join(cards)
    return ('<div class="marquee tmarquee"><div class="marquee-track">%s%s</div></div>'
            % (inner, inner))


TESTIMONIALS_EN = [
 ("We brought in Tal Paperin as our fractional VP of Sales from day one at KanduAi. He wasn't just a consultant, he acted as a true VP of Sales. He defined our Ideal Customer Profile, built our outbound playbook, hired and trained SDRs, and launched our outbound motion twice. If you're a founder trying to launch or relaunch sales from zero, Tal is who you want in your corner.","Ariel Shemesh","Co-Founder & CEO at KanduAI"),
 ("Tal has been a pleasure to work with. I own and operate a small business in the IoT sector, and have very little experience in sales and marketing. Tal was able to quickly develop a strategy for us, implement a CRM, and start building and training our sales team. If you are a small (or large) business needing to get your sales and marketing straightened out, Tal is your guy.","Tommy Remmert","Co-Founder and CTO of LoneStar Tracking"),
 ("If you are looking for someone who understands sales, Tal is your address. His grasp on the overall sales process, how to move a prospect forward and his on point grasp of how to move your business forward is invaluable. Follow him. Listen to him. Take his advice. Grow your business as a result.","Helen Gottstein","Public Speaking, Executive Communications & Strategy"),
 ("Tal is a hard-working and trustworthy person. I have experience as a client, a partner and working for him directly. He is a man of his word, delivers on what he promises. A competent salesperson and strategist I would recommend him to any company wanting a fractional sales leader, channel manager or strategist.","Steve Burton","CRO, The Point Company"),
 ("Working with Tal has been impactful. He helped us understand where the issues were in our sales process and provided us a roadmap to increase sales by creating custom SOPs and demonstrating every step very clearly. He is very responsive and communicates well. Highly recommended.","Amitay Stern","CEO at TypoDuctions and DRIFT"),
 ("Tal is a sharp and smart marketer. In a short conversation, he was able to understand and analyze complex problems of understanding the market, customer analysis, and consumer mapping. He brought us quick and good solutions that do the job.","David Gallula, Ph.D.","Head at UED Research Institute, CEO at ProUX"),
 ("With just an initial 15 minute consulting call with Tal, I was able to identify new approaches that I am confident will lead to a significant increase in successful prospect meetings. Tal was friendly, gracious with his time, and a good listener. This session was one of the most helpful resources I have encountered.","Michael Teichberg","Founder, InventivHR"),
 ("Tal provided me with wise advice. He listened to me and asked great questions that showed an advanced level of understanding and attention, and then gave very helpful advice and shared his ways of thinking on the matter. I was most impressed by his methodical way of thinking and experimenting in sales.","Neriya Rosner","Founder and CEO of SpecBite"),
 ("Tal is a real professional! I've asked him to provide an opinion on commercialization of a medical device product. What I received is a deep dive into entire world of terms, key players and possibilities and, on the other hand, a clear recommendation and a guidance for proper planning of my next steps.","Yakov Nedlin","Founder at LIBACCORD"),
 ("I had a great experience working with Tal Paperin. He gave me some great insight and ideas about how to take my business to the next dimension. He provides an array of services to help businesses make more money from domestic or international expansion. I would recommend using them for sure.","Sherman Barnes II","Head of Sales & Marketing, Trio Trucking Inc"),
 ("KSW is an incredible resource, but more importantly, there are very few people as talented as Tal when it comes to sales strategy. He helped close a publicly traded company for my startup.","Huw Nierenberg","Co-Founder, ePropertyCare"),
 ("I had the pleasure to work with Tal. I can tell that Tal is a great team player, very energetic and enthusiastic to get things done. He was always willing to help and share his experience in international sales and project management. He is practical, analytic with solving skills and nice to have around!","Luisa Arroyave","Senior Manager, Walmart Global Sourcing"),
 ("Tal Paperin has everything you want and need in a solutions consulting company: years of experience in both pre and post sales, connections in all the BRIC countries, knowledge in how to standout in many different types of markets, and more ways to increase your company's profitability.","Gabriel Heifets","HW Lead Engineer, Annapurna Labs (Amazon)"),
 ("Tal has the knowledge and deep understanding to analyze and map the market competition in order to promote the comparative advantage for any category of products. Tal is the one you would like to have as your team leader.","Barak Kav","CEO at TAG Dental LTD (Global)"),
 ("Tal is extremely enthusiastic about his job, smart, professional and thorough, and was a pleasure to work with.","Daniel Weiser","Sr. Director BD & Sales, Americas at Silicom Ltd."),
 ("Tal has great negotiating skills and secured several big deals for the company. He is incredibly capable and is a huge asset to any company that he works for.","Laura Gillman","Meshi Pharm"),
 ("I had the pleasure of meeting Tal to discuss strategies and ideas for developing my business and improving sales. Tal had excellent ideas and opinions that I will be putting to use in the coming months. I highly recommend Tal for your business.","Daniel Tarlow","GK8 by Galaxy (Nasdaq: GLXY)"),
 ("After great achievements in a rapidly growing company (Mobileye, an Intel Company), Tal listened carefully and gave concise, precise advice of great value, on negotiating projects by added value and expanding global markets through more personalised channels. He has a rare talent for thinking in-depth and forward.","Judith Rozen-Romano","Founder & CEO, Divine Italy"),
 ("Having Tal as a contact is valuable. Having him in your corner is priceless. He is always prepared with insights and market focus, so every minute with him is energised and filled with possibility. He extracts the essence of any business idea and distils it into action and a roadmap to your goal.","Daniel Zatman","Co-Founder, Qii78"),
 ("I worked alongside Tal on the BizDev and Sales team at TAG Dental. I was always impressed by his professionalism and personal qualities. Tal brings creative problem-solving, wide cross-discipline knowledge and a willingness to do whatever it takes to get a productive result.","Bar Libach","Global Head of Sales & BD, MIS Implants Technologies"),
 ("I needed sound, no-bs advice on sales and marketing for a new business. Tal didn't hesitate to help, and his advice really put things into perspective. It became obvious that Tal is not only an expert in his field, but also a gracious person willing to help others.","Hans Bronkhorst","IT Manager, Bauwatch Group"),
 ("I had the honor of working with Tal for over a year. He proved himself professional, dedicated and a valuable asset. Tal is methodical with great attention to detail, combined with the ability to see the big picture and excellent people skills, which made him a pivotal figure in every project.","Yair Rosenzweig","VP Sales & Services, Galcon"),
]

TESTIMONIALS_HE = [
 ('הבאנו את טל פאפרין כ-VP Sales במיקור חוץ מהיום הראשון שלנו ב-KanduAi. הוא לא היה סתם יועץ, הוא תפקד כ-VP Sales אמיתי לכל דבר. הוא הגדיר את פרופיל הלקוח האידיאלי שלנו, בנה את ה-playbook לאאוטבאונד, גייס והכשיר אנשי SDR, והניע את תהליך האאוטבאונד שלנו פעמיים מאפס. אם אתם מייסדים שמנסים להניע או להניע מחדש מערך מכירות מאפס, טל הוא האיש שאתם רוצים לצידכם.','אריאל שמש','שותף מייסד ומנכ"ל, KanduAI'),
 ('העבודה עם טל היא תענוג צרוף. אני הבעלים והמנהל של עסק קטן בתחום ה-IoT, ויש לי מעט מאוד ניסיון במכירות ובשיווק. טל ידע לפתח עבורנו אסטרטגיה במהירות, להטמיע CRM, ולהתחיל לבנות ולהכשיר את צוות המכירות שלנו. אם אתם עסק קטן (או גדול) שצריך לעשות סדר ולקחת את המכירות והשיווק בידיים, טל הוא האיש שלכם.','תומאס רמרט','שותף מייסד ו-CTO, LoneStar Tracking'),
 ('אם אתם מחפשים מישהו שבאמת מבין מכירות, טל הוא הכתובת שלכם. התפיסה שלו לגבי תהליך המכירה הכולל, היכולת שלו להניע לקוח פוטנציאלי קדימה, וההבנה המדויקת שלו איך לדחוף את העסק שלכם להצלחה, הן פשוט נכס שאין לו מחיר. תעקבו אחריו. תקשיבו לו. קחו את העצות שלו, ותראו איך העסק שלכם צומח.','הלן גוטשטיין','דוברות, תקשורת ואסטרטגיה ניהולית'),
 ('טל הוא אדם חרוץ ואיש סוד שניתן לסמוך עליו בעיניים עצומות. יש לי ניסיון איתו כלקוח, כשותף וגם כמי שעבד תחתיו באופן ישיר. הוא איש של מילה, ומספק בדיוק את מה שהוא מבטיח. כאיש מכירות ואסטרטג בחסד, אני ממליץ עליו בחום לכל חברה שמחפשת מנהל מכירות במיקור חוץ, מנהל ערוצי הפצה או אסטרטג עסקי.','סטיב ברטון','CRO, The Point Company'),
 ('העבודה עם טל השפיעה עלינו בצורה מטורפת. הוא עזר לנו להבין בדיוק איפה היו הבעיות בתהליך המכירה שלנו, וסיפק לנו מפת דרכים ברורה להגדלת המכירות על ידי יצירת נהלי עבודה (SOPs) מותאמים אישית והדגמה חיונית של כל שלב ושלב. הוא זמין מאוד ותקשורתי ברמות הגבוהות ביותר. מומלץ בחום.','אמיתי שטרן','מנכ"ל, TypoDuctions ו-DRIFT'),
 ('טל הוא איש שיווק חד וחכם בצורה יוצאת דופן. בשיחה קצרה אחת, הוא הצליח להבין ולנתח בעיות מורכבות של הבנת שוק, ניתוח לקוחות ומיפוי צרכנים. הוא הביא לנו פתרונות מהירים ומעולים שעושים את העבודה בשטח.','ד"ר דיוויד גלולה','מנהל מכון המחקר UED, מנכ"ל ProUX'),
 ('כבר בשיחת ייעוץ ראשונית של 15 דקות בלבד עם טל, הצלחתי לזהות גישות חדשות שאני בטוח שיובילו לעלייה משמעותית בפגישות מוצלחות עם לקוחות פוטנציאליים. טל היה חברותי, נדיב בזמנו וקשוב מאוד. השיחה הזו הייתה אחד הכלים הכי יעילים ומועילים שנתקלתי בהם.','מייקל טייכברג','מייסד, InventivHR'),
 ('טל נתן לי עצות חכמות ומדויקות. הוא הקשיב לי, שאל שאלות מצוינות שהראו רמת הבנה ותשומת לב גבוהה, ואז נתן עצות מועילות במיוחד ושיתף את דרכי החשיבה שלו בנושא. מה שהכי הרשים אותי זו הדרך המתודית שבה הוא חושב ומנווט בעולם המכירות.','נריה רוזנר','מייסדת ומנכ"לית, SpecBite'),
 ('טל הוא מקצוען אמיתי! ביקשתי ממנו חוות דעת על מסחור של מוצר בתחום המכשור הרפואי. מה שקיבלתי היה צלילת עומק מטורפת לכל עולם המושגים, שחקני המפתח והאפשרויות, ומצד שני, המלצה ברורה והכוונה מדויקת לתכנון השלבים הבאים שלי.','יעקב נדלין','מייסד, LIBACCORD'),
 ('הייתה לי חוויה מדהימה בעבודה עם טל פאפרין. הוא נתן לי תובנות ורעיונות מעולים איך לקחת את העסק שלי לשלב הבא. הוא מציע מגוון רחב של שירותים שעוזרים לעסקים להרוויח יותר כסף מהתרחבות מקומית או בינלאומית. אני ממליץ לעבוד איתו ללא ספק.','שרמן בארנס השני','מנהל מכירות ושיווק, Trio Trucking'),
 ('KSW היא משאב מדהים, אבל חשוב מכך, יש מעט מאוד אנשים מוכשרים כמו טל כשזה מגיע לאסטרטגיית מכירות. הוא עזר לסטארטאפ שלי לסגור עסקה עם חברה הנסחרת בבורסה.','היו ניירנברג','שותף מייסד, ePropertyCare'),
 ('היה לי העונג לעבוד עם טל. אני יכולה להגיד שטל הוא שחקן צוות מדהים, מלא באנרגיה ורעב להשיג תוצאות. הוא תמיד שמח לעזור ולשתף מהניסיון שלו במכירות בינלאומיות ובניהול פרויקטים. הוא מעשי, אנליטי, בעל יכולת פתרון בעיות גבוהה, ופשוט אדם שכיף לעבוד לצידו!','לואיזה ארויאבה','מנהלת בכירה, Walmart Global Sourcing'),
 ('לטל פאפרין יש כל מה שאתם רוצים וצריכים מחברת ייעוץ פתרונות: שנים של ניסיון ב-Pre-sales וב-Post-sales, קשרים ענפים בכל מדינות ה-BRIC, ידע מעשי איך להבליט את העסק שלכם בסוגים שונים של שווקים, והמון דרכים להגדיל את הרווחיות של החברה שלכם.','גבריאל הייפץ','מהנדס חומרה מוביל, Annapurna Labs (Amazon)'),
 ('לטל יש את הידע וההבנה העמוקה הדרושים כדי לנתח ולמפות את תחרות השוק, במטרה לקדם את היתרון היחסי של כל קטגוריית מוצרים. טל הוא בדיוק האדם שאתם רוצים שיוביל את הצוות שלכם.','ברק קב','מנכ"ל, TAG Dental LTD (Global)'),
 ('טל מלא בתשוקה ואנרגיה לעבודה שלו, הוא חכם, מקצועי ויסודי בצורה בלתי רגילה, והיה פשוט תענוג לעבוד איתו.','דניאל וייזר','מנהל בכיר BD ומכירות, אמריקה, Silicom Ltd.'),
 ('לטל יש יכולות ניהול משא ומתן פנומנליות, והוא סגר כמה עסקאות ענק עבור החברה. הוא מוכשר ברמות הגבוהות ביותר ומהווה נכס אדיר לכל חברה שהוא עובד איתה.','לורה גילמן','Meshi Pharm'),
 ('היה לי העונג להיפגש עם טל ולדבר על אסטרטגיות ורעיונות לפיתוח העסק ולשיפור המכירות. לטל היו רעיונות ודעות מעולים שאני איישם בחודשים הקרובים. אני ממליץ בחום על טל לעסק שלכם.','דניאל תרלו','GK8 by Galaxy (Nasdaq: GLXY)'),
 ('אחרי הישגים גדולים בחברה שצמחה במהירות (Mobileye, חברת אינטל), טל הקשיב בקפידה ונתן עצות תמציתיות ומדויקות בעלות ערך רב, על ניהול פרויקטים לפי ערך מוסף והרחבת שווקים גלובליים דרך ערוצים מותאמים אישית. יש לו כישרון נדיר לחשוב לעומק וקדימה.','ג׳ודית רוזן-רומנו','מייסדת ומנכ״לית, Divine Italy'),
 ('טל כאיש קשר הוא נכס. טל לצידך לא יסולא בפז. הוא תמיד מגיע עם תובנות ומיקוד שוק, וכל דקה איתו מלאת אנרגיה ואפשרויות. הוא מזקק את המהות של כל רעיון עסקי והופך אותו לפעולה ולמפת דרכים ליעד שלך.','דניאל זטמן','שותף מייסד, Qii78'),
 ('עבדתי לצד טל בצוות ה-BizDev והמכירות ב-TAG Dental. תמיד התרשמתי מהמקצועיות ומהתכונות האישיות שלו. טל מביא פתרון בעיות יצירתי, ידע רחב בין-תחומי ונכונות לעשות מה שצריך כדי להגיע לתוצאה.','בר ליבך','ראש מכירות ופיתוח עסקי גלובלי, MIS Implants'),
 ('הייתי צריך עצה כנה ובלי בולשיט על מכירות ושיווק לעסק חדש. טל לא היסס לעזור, והעצה שלו באמת סידרה לי את הראש. התברר שטל הוא לא רק מומחה בתחומו אלא גם אדם נדיב שמוכן לעזור לאחרים.','הנס ברונקהורסט','מנהל IT, Bauwatch Group'),
 ('היה לי הכבוד לעבוד עם טל במשך יותר משנה. הוא הוכיח את עצמו כמקצוען, מסור ונכס יקר. טל מתודי עם תשומת לב יוצאת דופן לפרטים, יחד עם יכולת לראות את התמונה הגדולה וכישורי אנשים מעולים, מה שהפך אותו לדמות מרכזית בכל פרויקט.','יאיר רוזנצוויג','סמנכ״ל מכירות ושירות, Galcon'),
]


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
        <h2 class="cases-recs-h">What clients say</h2>
{testimonials}
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
        <h2 class="cases-recs-h">מה הלקוחות אומרים</h2>
{testimonials}
{cta}
        <div class="svc-related">ראו את <a href="/he/services/">השירותים</a> שמאחורי אלה, או <a href="/blog/">קראו את הבלוג</a>.</div>
      </div>
    </div>
  </main>

{footer}
</body>
</html>
'''


SERVICE_CASE_EN = {
 "fractional-cro":{"company":"KanduAI","line":"Brought in as fractional VP of Sales from day one. I owned go-to-market end to end and rebuilt the entire engine through a full product pivot.","result":"A working outbound engine, rebuilt from scratch through a pivot, with speed and precision."},
 "outsourced-sales":{"company":"LoneStar Tracking","line":"Strong marketing, a sales engine that was not converting, and founders with little sales experience. I built and ran the entire sales side.","result":"Full VP-level sales leadership at a fraction of the cost of a hire."},
 "go-to-market-strategy":{"company":"Bacsoft","line":"An Israeli IIoT company that needed a global go-to-market: strategy, a channel and complex public-sector deals. I owned all of it.","result":"A global channel and a B2G pipeline, built for complex IIoT sold worldwide."},
 "sales-team-building":{"company":"KanduAI","line":"I hired, trained and managed the SDR team, and rebuilt the motion through a product pivot.","result":"A trained team running a real outbound playbook, not improvising every call."},
 "distributor-channel-recruitment":{"company":"Palram","line":"A global manufacturer convinced there was no money in Eastern Europe. I mapped the channel and the real decision-makers, and signed the partners on the ground.","result":"Multiple distributors and retail chains signed in a market they had written off."},
 "market-entry":{"company":"BT9","line":"A company that needed an entire international sales operation built from the ground up, across the FSU, the EU and APAC.","result":"A working international sales engine across three regions, built from scratch."},
 "b2g-public-sector":{"company":"Bacsoft","line":"Led B2G for an Israeli IIoT company backed by Japan's SUN Corp: RFIs, RFQs and complex government projects across the globe.","result":"A B2G pipeline built for complex public-sector deals worldwide."},
 "contract-negotiation":{"company":"Palram","line":"Led every negotiation personally to open a market a global manufacturer had abandoned.","result":"Signed the distributors and chains that put product on the shelves."},
 "saas-sales":{"company":"Synergix","line":"Sold scientific SaaS to a hard, technical US buyer: universities, research labs and pharma companies.","result":"SaaS sold into US academia and pharma, a long, technical, high-trust sale."},
}

SERVICE_CASE_HE = {
 "fractional-cro":{"company":"KanduAI","line":"נכנסתי כ-VP מכירות במיקור חוץ מהיום הראשון. לקחתי בעלות מלאה על ה-GTM ובניתי מחדש את כל המנוע דרך פיבוט מלא במוצר.","result":"מנוע אאוטבאונד עובד, שנבנה מחדש מאפס דרך פיבוט, במהירות ובדיוק."},
 "outsourced-sales":{"company":"LoneStar Tracking","line":"שיווק חזק, מנוע מכירות שלא המיר, ומייסדים עם מעט ניסיון במכירות. בניתי והרצתי את כל צד המכירות.","result":"הובלת מכירות מלאה ברמת VP בשבריר מעלות של גיוס."},
 "go-to-market-strategy":{"company":"Bacsoft","line":"חברת IIoT ישראלית שהייתה צריכה Go-to-Market גלובלי: אסטרטגיה, ערוץ ועסקאות מורכבות מול המגזר הציבורי. לקחתי בעלות על הכל.","result":"רשת ערוצים גלובלית ופייפליין B2G, שנבנו ל-IIoT מורכב שנמכר בעולם."},
 "sales-team-building":{"company":"KanduAI","line":"גייסתי, הכשרתי וניהלתי את צוות ה-SDR, ובניתי מחדש את התנועה דרך פיבוט במוצר.","result":"צוות מיומן שמריץ Playbook אאוטבאונד אמיתי, לא מאלתר כל שיחה."},
 "distributor-channel-recruitment":{"company":"Palram","line":"יצרן גלובלי שהיה בטוח שאין כסף במזרח אירופה. מיפיתי את הערוץ ואת מקבלי ההחלטות האמיתיים, והחתמתי את השותפים בשטח.","result":"מספר מפיצים ורשתות קמעונאות שהוחתמו בשוק שהחברה כבר מחקה."},
 "market-entry":{"company":"BT9","line":"חברה שהייתה צריכה מערך מכירות בינלאומי שלם שייבנה מאפס, ב-FSU, באיחוד האירופי וב-APAC.","result":"מנוע מכירות בינלאומי עובד בשלוש טריטוריות, שנבנה מאפס."},
 "b2g-public-sector":{"company":"Bacsoft","line":"הובלתי B2G לחברת IIoT ישראלית בגיבוי SUN Corp מיפן: מכרזים, RFIs, RFQs ופרויקטים ממשלתיים מורכבים בכל העולם.","result":"פייפליין B2G שנבנה לעסקאות מורכבות מול המגזר הציבורי בעולם."},
 "contract-negotiation":{"company":"Palram","line":"ניהלתי כל משא ומתן באופן אישי כדי לפתוח שוק שיצרן גלובלי כבר נטש.","result":"החתמתי את המפיצים והרשתות שהביאו את המוצר למדפים."},
 "saas-sales":{"company":"Synergix","line":"מכרתי SaaS מדעי לקונה אמריקאי קשה וטכני: אוניברסיטאות, מעבדות מחקר וחברות פארמה.","result":"SaaS שנמכר לאקדמיה ולפארמה בארה״ב, מכירה ארוכה, טכנית ועתירת אמון."},
}


def render_case_callout(case, label, rlabel, more, url):
    if not case:
        return ""
    return ('      <div class="svc-case">\n'
            '        <span class="svc-case-label">%s</span>\n'
            '        <h3>%s</h3>\n        <p>%s</p>\n'
            '        <p class="svc-case-result"><strong>%s:</strong> %s</p>\n'
            '        <a class="svc-case-link" href="%s">%s</a>\n      </div>'
            % (esc(label), esc(case["company"]), esc(case["line"]),
               esc(rlabel), esc(case["result"]), url, esc(more)))


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
            case=render_case_callout(SERVICE_CASE_EN.get(svc["slug"]), "Case study", "Result", "See more case studies", "/case-studies"),
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
            case=render_case_callout(SERVICE_CASE_HE.get(svc["slug"]), "מקרה לקוח", "תוצאה", "לעוד מקרי מבחן", "/he/case-studies"),
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
        f.write(CONTACT_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER, contactjs=CONTACT_JS_EN))
    with open(os.path.join(ROOT, "he", "contact.html"), "w", encoding="utf-8") as f:
        f.write(CONTACT_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER, contactjs=CONTACT_JS_HE))

    with open(os.path.join(ROOT, "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                  cases=render_cases(CASE_STUDIES, "Result"),
                                  testimonials=render_testimonials(TESTIMONIALS_EN), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                  cases=render_cases(HE_CASES, "תוצאה"),
                                  testimonials=render_testimonials(TESTIMONIALS_HE), cta=HE_CTA))

    print("Built %d EN + %d HE service pages, HE index and HE FAQ"
          % (len(SERVICES), len(HE_SERVICES)))


if __name__ == "__main__":
    build()
