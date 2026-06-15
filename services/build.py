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
        <a href="/case-studies">Case Studies</a>
        <a href="/recommendations">Recommendations</a>
        <a href="/blog/">Blog</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/he/" hreflang="he" aria-label="Switch to Hebrew">''' + FLAG_IL + '''</a>
        <a class="btn btn-solid" href="/contact">Let's Talk</a>
        <button class="navtoggle" aria-label="Menu" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 Tal Paperin. All rights reserved.</span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="Email Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="Call Tal Paperin"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="Tal Paperin on LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
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
    {"h":"Priced by how much of me you need","p":[
      "The job is identical at every level. The only thing that changes is how many hours a day I am in your business."],
     "ul":[
      "Starter, $6,000 a month: two hours a day, every working day",
      "Growth, $12,000 a month: half time, four hours a day. What most companies choose",
      "CRO Ownership, $22,000 a month: full time and exclusive, when I take this I take only you"]},
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
  "desc":"Break into new markets without the expensive mistakes. I have built and run sales, teams, subsidiaries and support across four continents, repeatedly and for multiple companies. Here is how I pick a market and build it.",
  "eyebrow":"Service",
  "lead":"Four continents. More than forty countries. Hundreds of cities, on the ground, not over email. Entering a new market is where companies burn the most money. I do not just enter a market, I help you choose the right one, then build and run it.",
  "card":"Pick the right market, then build and run the whole operation: sales, subsidiary, support and customer service. Built across four continents.",
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
      "This is not a one-time story. I have built, hired, trained and managed teams across these markets more than once, for more than one company, on four continents. Different products, different buyers, the same discipline. I also run B2G and complex public-sector deals across the globe."]},
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

 {"slug":"global-markets","nav":"Global Markets","h1":"Global Markets: Where I Build and Run Revenue",
  "title":"Global Markets: International Sales Expansion | Tal Paperin",
  "desc":"I have built, hired, trained and managed sales teams, opened subsidiaries and run support and customer service across four continents, repeatedly and for multiple companies. Here is how I pick a market and build it.",
  "eyebrow":"Global",
  "lead":"Four continents. More than forty countries. Hundreds of cities, on the ground, not over email. I do not just enter a market, I help you choose the right one, then build and run it.",
  "card":"Built revenue across four continents. I help you pick the right market, then build and run the whole operation there.",
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
      "This is not a one-time story. I have built, hired, trained and managed teams across these markets more than once, for more than one company, on four continents. Different products, different buyers, the same discipline."]},
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
      <h2 class="cases-recs-h">On the ground, on four continents</h2>
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
        <a href="/he/case-studies">מקרי מבחן</a>
        <a href="/he/recommendations">המלצות</a>
        <a href="/he/blog/">בלוג</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/" hreflang="en" aria-label="Switch to English">''' + FLAG_US + '''</a>
        <a class="btn btn-solid" href="/he/contact">בואו נדבר</a>
        <button class="navtoggle" aria-label="תפריט" aria-expanded="false">''' + HAMBURGER + '''</button>
      </div>
    </div>
  </nav>'''

HE_FOOTER = '''  <footer>
    <div class="wrap inner">
      <span>&copy; 2017-2026 טל פאפרין. כל הזכויות שמורות.</span>
      <span class="foot-contact"><a href="mailto:tal@ksw.solutions" aria-label="אימייל"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></a><a href="tel:+972545308119" aria-label="טלפון"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></a><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener" aria-label="לינקדאין"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14zM8.34 18.34V10.5H5.67v7.84h2.67zM7 9.34a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1zM18.34 18.34v-4.3c0-2.3-1.23-3.37-2.87-3.37a2.48 2.48 0 0 0-2.24 1.23v-1.06h-2.67v7.5h2.67v-4.15c0-1.1.2-2.16 1.56-2.16 1.34 0 1.36 1.25 1.36 2.23v4.08h2.9z"/></svg></a></span>
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
     "p":["בשבוע הראשון אני מאבחן איפה העסקאות נתקעות ודולפות. בשבוע השני יש לכם תוכנית ותחזית אמיתית. בשבוע השלישי אני כבר מריץ אותה. אתם מקבלים מנהל מנוסה שעשה את זה יותר מ-30 פעם בארבע יבשות, לא עוד מצגת אסטרטגיה שנשארת במגירה."]},
    {"h":"מתומחר לפי כמה ממני אתם צריכים",
     "p":["התפקיד זהה בכל רמה. הדבר היחיד שמשתנה הוא כמה שעות ביום אני בעסק שלכם."],
     "ul":["Starter, 6,000 דולר בחודש: שעתיים ביום, בכל יום עבודה","Growth, 12,000 דולר בחודש: חצי משרה, ארבע שעות ביום. מה שרוב החברות בוחרות","בעלות מלאה, 22,000 דולר בחודש: משרה מלאה ובלעדית, כשאני לוקח את זה אני לוקח רק אתכם"]},
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
  "desc":"לפרוץ לשווקים חדשים בלי הטעויות היקרות. בניתי וניהלתי מכירות, צוותים, חברות בנות ותמיכה בארבע יבשות, שוב ושוב ולמספר חברות. הנה איך אני בוחר שוק ובונה אותו.",
  "eyebrow":"שירות",
  "lead":"ארבע יבשות. יותר מארבעים מדינות. מאות ערים, בשטח, לא מהאימייל. כניסה לשוק חדש זה המקום שבו חברות שורפות הכי הרבה כסף. אני לא רק נכנס לשוק, אני עוזר לכם לבחור את הנכון, ואז בונה ומנהל אותו.",
  "card":"בוחרים את השוק הנכון, ואז בונים ומנהלים את כל המערך: מכירות, חברה בת, תמיכה ושירות לקוחות. נבנה בארבע יבשות.",
  "sections":[
    {"h":"קודם בוחרים שוק, אחר כך בונים אותו",
     "p":["הטעות היקרה ביותר בהתרחבות היא להיכנס מהר לשוק הלא נכון. אני מתחיל בלשפוט אם השוק בכלל שלכם, הכאב, הנגישות, הנכונות לשלם, התחרות, ואז בונה את המערך רק איפה שזה הגיוני. תכנון וביצוע, מאותו אדם שאחראי על התוצאות."]},
    {"h":"מה אני עושה",
     "ul":["אסטרטגיית חדירה ותוכנית לפי אבני דרך","הטריטוריות, הערוצים ומקבלי ההחלטות הנכונים","הובלת המשא ומתן וסגירת העסקאות הראשונות באופן אישי","בניית נוכחות מקומית, ישירה או דרך שותפים"]},
    {"h":"כל המערך, לא רק המכירה",
     "ul":["צוותי מכירות: SDR, AE והובלה, מגויסים, מוכשרים ומנוהלים","חברות בנות שנפתחות כשלקוחות או גיוס דורשים ישות מקומית","מערכי תמיכה טכנית ושירות לקוחות שמוקמים ומנוהלים","תמחור, מיצוב ו-Go-To-Market שנבנים לקונה המקומי","ה-CRM, הפייפליין, התחזית והאחריות על התוצאות"]},
    {"h":"נעשה שוב ושוב, למספר חברות",
     "p":["זה לא סיפור חד פעמי. בניתי, גייסתי, הכשרתי וניהלתי צוותים בשווקים האלה יותר מפעם אחת, למספר חברות, בארבע יבשות. מוצרים שונים, קונים שונים, אותה משמעת. אני גם מנהל עסקאות B2G ומורכבות מול המגזר הציבורי בכל העולם."]},
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

 {"slug":"global-markets","nav":"שווקים גלובליים","h1":"שווקים גלובליים: איפה אני בונה ומנהל הכנסות",
  "title":"שווקים גלובליים: התרחבות מכירות בינלאומית | טל פאפרין",
  "desc":"בניתי, גייסתי, הכשרתי וניהלתי צוותי מכירות, פתחתי חברות בנות וניהלתי תמיכה ושירות לקוחות בארבע יבשות, שוב ושוב ולמספר חברות. הנה איך אני בוחר שוק ובונה אותו.",
  "eyebrow":"גלובלי",
  "lead":"ארבע יבשות. יותר מארבעים מדינות. מאות ערים, בשטח, לא מהאימייל. אני לא רק נכנס לשוק, אני עוזר לכם לבחור את הנכון, ואז בונה ומנהל אותו.",
  "card":"בניתי הכנסות בארבע יבשות. אני עוזר לכם לבחור את השוק הנכון, ואז בונה ומנהל שם את כל המערך.",
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
      "זה לא סיפור חד פעמי. בניתי, גייסתי, הכשרתי וניהלתי צוותים בשווקים האלה יותר מפעם אחת, למספר חברות, בארבע יבשות. מוצרים שונים, קונים שונים, אותה משמעת."]},
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
_SVC_ORDER = ["fractional-cro", "outsourced-sales", "go-to-market-strategy", "market-entry",
              "sales-team-building", "distributor-channel-recruitment", "b2g-public-sector",
              "contract-negotiation"]


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
  <title>שירותים: סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, מכירות במיקור חוץ ו-GTM | טל פאפרין</title>
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
      <h2 class="cases-recs-h">בשטח, בארבע יבשות</h2>
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
 {"company":"KanduAI","id":"kanduai","meta":"AI SaaS startup, Fractional VP of Sales",
  "situation":"An early-stage AI startup with a product and no way to sell it. No pipeline, no process, no team, and nobody who had ever built a sales motion from zero. They did not need advice, they needed someone to take the revenue side off the founders' plate and build the engine, then keep it alive when the product pivoted out from under it. Twice.",
  "did":["Owned go-to-market end to end as fractional VP of Sales from day one","Defined and validated the ICP, positioning and messaging before a single rep dialed","Built the outbound playbook and the entire motion from zero","Hired, trained and managed the SDR team","Relaunched the whole go-to-market through the pivot, twice, without losing momentum"],
  "result":"An outbound engine that existed where there had been nothing, rebuilt from scratch through two pivots. The founders got a real motion and a trained team instead of guessing at sales between everything else they were carrying."},
 {"company":"LoneStar Tracking","id":"lonestar","meta":"Founder-led IoT business, Outsourced sales leadership",
  "situation":"Marketing was doing its job and generating real interest. The problem was everything that happened after the lead came in. Deals stalled and died because there was no sales engine to convert them and founders who had never sold for a living. They were paying to create demand and watching it leak straight out the bottom.",
  "did":["Built the entire sales strategy and motion from scratch","Selected and implemented the CRM and the full sales stack","Built the process, the playbook and the pipeline","Recruited, hired and trained the sales team","Ran the team and the motion day to day as outsourced sales leadership"],
  "result":"Full VP-level sales leadership at a fraction of the cost of a hire, with a real process catching the demand marketing was paying to create instead of letting it bleed away."},
 {"company":"Bacsoft","id":"bacsoft","meta":"Israeli industrial IoT, backed by Japan's SUN Corp, VP of Global Sales",
  "situation":"An Israeli industrial IoT company, backed by Japan's SUN Corp, that made existing equipment smart and connected for water and wastewater utilities, manufacturers and smart cities. The technology was real and the global demand was there, with projects from Peru to Holland to Australia. What was missing was the engine to actually sell complex industrial IoT across borders: a strategy, a distributor network across continents, and the patience to win public-sector deals with long RFI and RFQ cycles.",
  "did":["Owned the global sales strategy end to end","Recruited and managed distributors across continents, from Europe to South America to APAC","Ran direct B2B sales of SaaS, hardware and services into utilities, manufacturers and municipalities","Led B2G: RFIs, RFQs and complex government and utility projects across the globe","Represented the company at international industry shows and managed marketing and marcom"],
  "result":"A global channel and a live B2G pipeline for a small Israeli company selling complex industrial IoT, hardware, software and services, to utilities and governments on four continents."},
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
  "result":"רשת ערוצים גלובלית ופייפליין B2G חי, לחברה ישראלית קטנה שמוכרת IoT תעשייתי מורכב, חומרה, תוכנה ושירותים, לתאגידים ולממשלות בארבע יבשות."},
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


LOGO_MAP = {"KanduAI":"kanduai","LoneStar Tracking":"lonestar","Bacsoft":"bacsoft",
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
 {"q": "We brought in Tal Paperin as our fractional VP of Sales from day one at KanduAi. He wasn't just a consultant, he acted as a true VP of Sales. He defined our Ideal Customer Profile, built our outbound playbook, hired and trained SDRs, and launched our outbound motion twice. If you're a founder trying to launch or relaunch sales from zero, Tal is who you want in your corner.", "name": "Ariel Shemesh", "role": "Co-Founder & CEO", "company": "KanduAI", "tag": "fractional-cro", "photo": "/img/testimonials/ariel-shemesh.jpg"},
 {"q": "Tal has been a pleasure to work with. I own and operate a small business in the IoT sector, and have very little experience in sales and marketing. Tal was able to quickly develop a strategy for us, implement a CRM, and start building and training our sales team. If you are a small (or large) business needing to get your sales and marketing straightened out, Tal is your guy.", "name": "Tommy Remmert", "role": "Co-Founder & CTO", "company": "LoneStar Tracking", "tag": "outsourced-sales", "photo": "/img/testimonials/tommy-remmert.jpg"},
 {"q": "If you are looking for someone who understands sales, Tal is your address. His grasp on the overall sales process, how to move a prospect forward and his on point grasp of how to move your business forward is invaluable. Follow him. Listen to him. Take his advice. Grow your business as a result.", "name": "Helen Gottstein", "role": "Public Speaking & Executive Communications", "company": "", "tag": "go-to-market-strategy", "photo": ""},
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
 {"q": "Tal is detail-oriented with a professional, easy-going attitude. He is very responsive and easy to work with. He quickly establishes credibility and confidence, and his straightforward manner makes him fun to work with.", "name": "Kasia Wenker", "role": "VP of Solutions Engineering", "company": "ITS Logistics", "tag": "fractional-cro", "photo": ""},
 {"q": "Tal is our sales rep for SOURCE. He has been very helpful and very persistent about getting information to me in the format I requested. He has gone above and beyond for me. I highly recommend him.", "name": "Bonnie Meyers", "role": "Business Owner", "company": "Unstoppable Learning", "tag": "outsourced-sales", "photo": ""},
 {"q": "Tal is great to work with. He is very professional and highly motivated, and a great source of advice and guidance for moving your business forward.", "name": "Dovid Shaw", "role": "Director", "company": "WoW Discoveries", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-shaw.jpg"},
 {"q": "Tal is a take-charge person who presents creative ideas and communicates their benefits. He successfully developed several marketing plans for our company. Beyond being an asset to our sales efforts, he wrote effective script modules for our sales representatives and took a leadership role in sales meetings, inspiring and motivating other employees. I highly recommend Tal for any organization.", "name": "Ouri Fischel", "role": "VP Business Development", "company": "agrematch", "tag": "sales-team-building", "photo": "/img/testimonials/ouri-fischel.jpg"},
]

TESTIMONIALS_HE = [
 {"q": "הבאנו את טל פאפרין כ-VP Sales במיקור חוץ מהיום הראשון שלנו ב-KanduAi. הוא לא היה סתם יועץ, הוא תפקד כ-VP Sales אמיתי לכל דבר. הוא הגדיר את פרופיל הלקוח האידיאלי שלנו, בנה את ה-playbook לאאוטבאונד, גייס והכשיר אנשי SDR, והניע את תהליך האאוטבאונד שלנו פעמיים מאפס. אם אתם מייסדים שמנסים להניע או להניע מחדש מערך מכירות מאפס, טל הוא האיש שאתם רוצים לצידכם.", "name": "אריאל שמש", "role": "שותף מייסד ומנכ\"ל", "company": "KanduAI", "tag": "fractional-cro", "photo": "/img/testimonials/ariel-shemesh.jpg"},
 {"q": "העבודה עם טל היא תענוג צרוף. אני הבעלים והמנהל של עסק קטן בתחום ה-IoT, ויש לי מעט מאוד ניסיון במכירות ובשיווק. טל ידע לפתח עבורנו אסטרטגיה במהירות, להטמיע CRM, ולהתחיל לבנות ולהכשיר את צוות המכירות שלנו. אם אתם עסק קטן (או גדול) שצריך לעשות סדר ולקחת את המכירות והשיווק בידיים, טל הוא האיש שלכם.", "name": "תומאס רמרט", "role": "שותף מייסד ו-CTO", "company": "LoneStar Tracking", "tag": "outsourced-sales", "photo": "/img/testimonials/tommy-remmert.jpg"},
 {"q": "אם אתם מחפשים מישהו שבאמת מבין מכירות, טל הוא הכתובת שלכם. התפיסה שלו לגבי תהליך המכירה הכולל, היכולת שלו להניע לקוח פוטנציאלי קדימה, וההבנה המדויקת שלו איך לדחוף את העסק שלכם להצלחה, הן פשוט נכס שאין לו מחיר. תעקבו אחריו. תקשיבו לו. קחו את העצות שלו, ותראו איך העסק שלכם צומח.", "name": "הלן גוטשטיין", "role": "דוברות ותקשורת ניהולית", "company": "", "tag": "go-to-market-strategy", "photo": ""},
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
 {"q": "טל הוא איש פרטים עם גישה מקצועית ונעימה. הוא מאוד זמין וקל לעבודה. הוא מבסס במהירות אמינות וביטחון, והישירות שלו הופכת את העבודה איתו לכיף.", "name": "קסיה ונקר", "role": "סמנכ\"לית הנדסת פתרונות", "company": "ITS Logistics", "tag": "fractional-cro", "photo": ""},
 {"q": "טל הוא איש המכירות שלנו ב-SOURCE. הוא היה מאוד מועיל ומאוד עקבי בלהביא לי את המידע בדיוק בפורמט שביקשתי. הוא עשה למעני הרבה מעבר למצופה. אני ממליצה עליו בחום.", "name": "בוני מאיירס", "role": "בעלת עסק", "company": "Unstoppable Learning", "tag": "outsourced-sales", "photo": ""},
 {"q": "טל הוא תענוג לעבוד איתו. הוא מאוד מקצועי ובעל מוטיבציה גבוהה, ומקור מצוין לעצה והכוונה בקידום העסק שלכם.", "name": "דוד שו", "role": "מנהל", "company": "WoW Discoveries", "tag": "go-to-market-strategy", "photo": "/img/testimonials/dovid-shaw.jpg"},
 {"q": "טל הוא אדם שלוקח אחריות, מציג רעיונות יצירתיים ויודע להעביר את הערך שבהם. הוא פיתח עבורנו בהצלחה כמה תוכניות שיווק. מעבר לזה שהיה נכס למאמצי המכירות שלנו, הוא כתב מודולי תסריטים אפקטיביים לנציגי המכירות ולקח תפקיד מוביל בישיבות מכירות, כשהוא מעורר השראה ומניע עובדים אחרים. אני ממליץ בחום על טל לכל ארגון.", "name": "אורי פישל", "role": "סמנכ\"ל פיתוח עסקי", "company": "agrematch", "tag": "sales-team-building", "photo": "/img/testimonials/ouri-fischel.jpg"},
]


LOGOS = [
 ("pepsico","PepsiCo"),("mars","Mars"),("mehadrin","Mehadrin"),
 ("saskatchewan","University of Saskatchewan"),("palram","Palram Applications"),
 ("motorad","MotoRad"),("source","Source"),("bt9","BT9"),
 ("limat","Limat Group"),
 ("lonestar","LoneStar Tracking"),("supra","Supra National Express"),
 ("bacsoft","Bacsoft"),("ofekpoint","OfekPoint"),("headcount","Headcount"),
 ("structshare","StructShare"),("hiarc","HiArc"),("cornsys","Cornsys"),
 ("epropertycare","ePropertyCare"),("chabad","Chabad on Campus"),
 ("kanduai","KanduAI"),("clinicmind","ClinicMind"),("plasticplace","PlasticPlace"),
]


def render_logo_wall(logos):
    imgs = "".join(
        '<img src="/logos/%s.jpg" alt="%s" loading="lazy" />' % (slug, esc(name))
        for slug, name in logos)
    return '<div class="proof-logos">%s</div>' % imgs


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
  <meta name="description" content="What founders and executives say about working with Tal Paperin, and the companies he has built sales for, from multinationals to startups, on four continents." />
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
  <meta name="description" content="מה מייסדים ומנהלים אומרים על עבודה עם טל פאפרין, והחברות שבנה להן מכירות, מתאגידים רב-לאומיים ועד סטארטאפים, בארבע יבשות." />
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

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">Case Studies</p>
        <h1>Brought in to build the engine, not just advise on it.</h1>
        <p class="lead">Real companies, real problems, real ownership. Here is what I have built and fixed, across startups, IoT, manufacturing, medical devices, retail and SaaS, on four continents.</p>
        <div class="cases-list">
{cases}
        </div>
        <h2 class="cases-recs-h">What clients say</h2>
{testimonials}
        <h2 class="cases-recs-h">On the ground, on four continents</h2>
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
  <meta name="description" content="תוצאות אמיתיות: בניית מנועי מכירות, פתיחת שווקים וסגירת עסקאות מורכבות לחברות B2B, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי ו-SaaS, בארבע יבשות." />
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
</head>
<body>
{nav}

  <main class="page" id="main">
    <div class="wrap">
      <div class="svc">
        <div class="glowline"></div>
        <p class="eyebrow">מקרי מבחן</p>
        <h1>הגעתי כדי לבנות את המנוע, לא רק לייעץ עליו.</h1>
        <p class="lead">חברות אמיתיות, בעיות אמיתיות, אחריות אמיתית. הנה מה שבניתי ותיקנתי, מסטארטאפים ועד יצרנים, IoT, מכשור רפואי, קמעונאות ו-SaaS, בארבע יבשות.</p>
        <div class="cases-list">
{cases}
        </div>
        <h2 class="cases-recs-h">מה הלקוחות אומרים</h2>
{testimonials}
        <h2 class="cases-recs-h">בשטח, בארבע יבשות</h2>
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
 "fractional-cro":{"company":"KanduAI","anchor":"kanduai","line":"An early-stage AI startup with a product and no way to sell it: no pipeline, no process, no team. I came in as fractional VP of Sales and owned the revenue side end to end.","bullets":["Defined the ICP, positioning and messaging, then built the outbound motion from zero","Hired, trained and managed the SDR team","Relaunched the entire go-to-market through two product pivots without losing momentum"],"result":"A working outbound engine, rebuilt from scratch through a pivot, with speed and precision."},
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
 "fractional-cro":[
  {"q":"What is a fractional CRO?","a":"A senior revenue leader who owns your strategy, team, pipeline, forecast and the number, part time, without a full-time CRO salary or a long-term lock-in."},
  {"q":"How is a fractional CRO different from a consultant?","a":"A consultant hands you a deck and leaves. I do the work, in the pipeline and the deals, and answer for the result."},
  {"q":"How much does a fractional CRO cost?","a":"$6,000 to $22,000 a month depending on how many hours a day you need, versus $250,000-plus for a full-time CRO, billed monthly with no contract."}],
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
  {"q":"What kind of deals have you closed?","a":"Complex, high-value B2B and B2G agreements across four continents, twenty-plus years of holding price and terms without losing the deal."}],
}

SERVICE_FAQS_HE = {
 "fractional-cro":[
  {"q":"מה זה סמנכ\"ל מכירות ופיתוח עסקי במיקור חוץ?","a":"מנהיג הכנסות בכיר שלוקח אחריות על האסטרטגיה, הצוות, הפייפליין, התחזית והתוצאות, במשרה חלקית, בלי שכר של משרה מלאה ובלי התחייבות ארוכת טווח."},
  {"q":"במה זה שונה מיועץ?","a":"יועץ מגיש מצגת והולך. אני עושה את העבודה, בתוך הפייפליין ובתוך העסקאות, ואחראי על התוצאה."},
  {"q":"כמה זה עולה?","a":"בין 6,000 ל-22,000 דולר בחודש לפי כמה שעות ביום אתם צריכים, מול 250 אלף דולר ומעלה למשרה מלאה, בתשלום חודשי בלי חוזה."}],
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
  {"q":"אילו עסקאות סגרת?","a":"הסכמי B2B ו-B2G מורכבים ובעלי ערך גבוה בארבע יבשות, מעל עשרים שנה של החזקת מחיר ותנאים בלי לאבד את העסקה."}],
}


GUIDES = [
 {"slug":"fractional-cro-cost",
  "title":"How Much Does a Fractional CRO Cost? | Tal Paperin",
  "desc":"A straight answer on fractional CRO pricing: what it costs per month, how that compares to a $250K full-time CRO, what is included, and when each level is worth it.",
  "h1":"What a Fractional CRO Actually Costs","eyebrow":"Guide",
  "lead":"Most consultants hide the number, hand you a deck, and disappear. I am an operator who still sells, I bill monthly with no contract, and here is exactly what a fractional CRO costs, in plain figures.",
  "sections":[
    {"h":"The short answer","p":[
      "A full-time CRO runs $250,000 and up all in, once you add base, equity, bonus, severance risk and a months-long hiring cycle. A fractional CRO gives you the same senior ownership for a monthly fee. The role is identical at every level. The only thing that changes is how many hours a day I am in your business."]},
    {"h":"The three levels, priced by how much of me","tiers":[
      "Starter, $6,000 a month. Me as your CRO embedded two hours a day, every working day. I own the strategy, the system and the standards, and your team carries more of the daily execution.",
      "Growth, $12,000 a month. Half time, four hours a day. Not just steering, driving: I run the motion week to week, manage the team hands-on, and carry the number with you. What most companies choose.",
      "CRO Ownership, $22,000 a month. Full time and exclusive. All of me on your revenue across sales, marketing and go-to-market, and while I own your number I take no other clients. Subject to availability."]},
    {"h":"Why it is cheaper than a full-time hire","ul":[
      "No $250K base, equity, bonus or severance risk",
      "No three-month hiring search and no two-quarter ramp",
      "Monthly billing, no contract, no lock-in, no exit fines: do not like it, we are done at the end of the month",
      "Results in week one, not month six"]},
    {"h":"You are hiring an operator, not an advisor","p":[
      "Most consultants hand you a deck and disappear. They have never carried a number. I am an ex VP of Global Sales and CRO, and I still do the selling myself, in the pipeline and in the deals. And I bill monthly with no contract, so I keep the work by being good at it, not by trapping you in one."]},
    {"h":"When a fractional CRO is the wrong call","p":[
      "If your sales motion is already proven and the work is genuinely a full week every week, hire full-time. Fractional wins when the motion is not yet proven, the volume is not yet a full week, or you need results before committing to a permanent hire."]},
  ],
  "faqs":[
    {"q":"How much does a fractional CRO cost?","a":"My engagements run $6,000 to $22,000 a month depending on the level of involvement, versus $250,000 and up for a full-time CRO once you include equity, bonus and severance."},
    {"q":"Is a fractional CRO cheaper than a full-time CRO?","a":"Yes. You get the same senior ownership without the base salary, equity, bonus, severance risk, hiring cycle or long ramp, and without a long-term lock-in."},
    {"q":"What is included?","a":"The same at every tier: a revenue diagnosis, a sales strategy and forecast, a playbook, CRM and pipeline structure, team training, hands-on management of the motion, hiring and performance, and full CRO-level ownership across sales, marketing and go-to-market. What changes between tiers is how many hours a day I am in your business: two hours, four hours, or full time."},
    {"q":"How long are fractional CRO engagements?","a":"There is no long-term lock-in. You scale the involvement up as you grow, or hand the function off once it is built."},
    {"q":"Do I have to sign a long contract?","a":"No. I bill monthly with no contract and no exit fines. If you do not like what I deliver, we are done at the end of the month and you owe nothing more."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO service</a>, <a href="/case-studies">case studies</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"fractional-cro-vs-outsourced-sales",
  "title":"Fractional CRO vs Outsourced Sales: Which Do You Need? | Tal Paperin",
  "desc":"Fractional CRO, fully outsourced sales, or a do-it-yourself system? A straight breakdown of which fits your stage, and how to choose.",
  "h1":"Fractional CRO vs Outsourced Sales","eyebrow":"Guide",
  "lead":"Three ways to fix revenue, one decision. Whichever you pick, you get an operator who still sells, billed monthly with no contract and no lock-in. Here is which one fits your stage, and which one wastes your money.",
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
    {"q":"How much does a fractional CRO in Israel cost?","a":"Engagements run $6,000 to $22,000 a month depending on involvement, far below a $250,000-plus full-time CRO hire."}],
  "related":'See the <a href="/services/market-entry">market entry</a> and <a href="/services/fractional-cro">fractional CRO</a> services, or <a href="/he/">the Hebrew site</a>.'},

 {"slug":"fractional-cro-vs-vp-of-sales",
  "title":"Fractional CRO vs Hiring a VP of Sales | Tal Paperin",
  "desc":"Tired of $30K-a-month VP of Sales hires you fire in 90 days? A fractional CRO gives you proven revenue leadership with no hiring gamble, no severance, and no lock-in.",
  "h1":"Fractional CRO vs Hiring a VP of Sales","eyebrow":"Guide",
  "lead":"You have done this before. Hire a VP of Sales at thirty grand a month, wait, watch nothing move, fire them at month three, eat the severance, start over. Here is the alternative.",
  "sections":[
    {"h":"The VP of Sales graveyard","p":[
      "A VP of Sales runs $30,000 a month or more, all in. The search takes months. The ramp takes a quarter. And if the fit is wrong, and it often is, you fire them at month two, three or four, eat the severance, and start the whole cycle again. I have watched founders burn hundreds of thousands of dollars this way, with nothing to show for it but lost time.",
      "The hire is a gamble. You are betting six figures on a resume and three interviews."]},
    {"h":"A fractional CRO is not a gamble","ul":[
      "I have built and run revenue for 30-plus B2B companies on four continents. You are not betting on whether I can do it. I have already done it.",
      "No recruiter fees, no equity, no severance risk, no months-long search",
      "Results in week one: I diagnose where deals leak, then I run the fix. No ramp, no learning curve"]},
    {"h":"I still sell. Myself. Hands on.","p":[
      "Most consultants hand you a deck and disappear. They have never carried a number. I am an ex VP of Global Sales and CRO, and I still do the selling myself, on the phone, in the room, in the deal. You are hiring an operator, not an advisor."]},
    {"h":"Monthly. No contract. No hostages.","p":[
      "I bill monthly. No long contract, no lock-in, no exit fines. You do not like what I deliver, we are done at the end of the month, and you owe nothing more. I keep the engagement because the work is good, not because a contract traps you. That is the opposite of a VP hire you cannot easily undo."]},
  ],
  "faqs":[
    {"q":"Is a fractional CRO better than hiring a VP of Sales?","a":"If your sales motion is not yet proven, yes. A VP hire is a six-figure gamble with months of search, a quarter of ramp and real severance risk. A fractional CRO who has done it 30-plus times delivers from week one, with no hiring risk and no lock-in."},
    {"q":"How much does a fractional CRO cost vs a VP of Sales?","a":"A VP of Sales runs $30,000 a month or more all in, plus recruiter fees, equity and severance. My fractional engagements run $6,000 to $22,000 a month, billed monthly with no contract."},
    {"q":"What if it is not working out?","a":"I bill monthly with no contract and no exit fines. If you do not like what I deliver, we are done at the end of the month and you owe nothing more."},
    {"q":"Do you actually do the selling, or just advise?","a":"I do the selling. I am an ex VP of Global Sales and CRO and I still work hands-on in the pipeline and the deals, not just in strategy decks."}],
  "related":'Compare the <a href="/fractional-cro-cost">cost</a>, see <a href="/fractional-cro-vs-outsourced-sales">fractional CRO vs outsourced sales</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"frum-business-consultant","en_only":True,
  "title":"Frum Business Consultant and Sales Leader | Tal Paperin",
  "desc":"A frum, shomer Shabbos business consultant and fractional sales leader from Eretz Yisrael, who knows the heimishe, Yiddish-speaking business world and helps frum business owners grow.",
  "h1":"A Frum Business Consultant Who Gets the Heimishe World","eyebrow":"For Frum Businesses",
  "lead":"I am a frum, shomer Shabbos Yid from Eretz Yisrael who has built and run sales for businesses on four continents. If you are a frum business owner who wants a sales leader who shares your values and understands your world, not just your spreadsheet, this is for you.",
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
      "At KanduAI I came in as fractional VP of Sales from day one, defined the ICP, built the outbound motion from zero and rebuilt it through two pivots. For Synergix I sold scientific SaaS into universities, research labs and pharma, writing the scripts and playbook the reps actually ran. Different products, same discipline."]},
  ],
  "faqs":[
    {"q":"What does a fractional CRO do for a SaaS company?","a":"Owns the revenue motion end to end: ICP and pricing, the outbound and inbound playbook, the CRM and pipeline, hiring and managing the reps, and the forecast, all without a full-time CRO salary."},
    {"q":"Do you sell technical or scientific SaaS?","a":"Yes. I have sold SaaS into universities, research labs and pharma, and built the motion for AI SaaS startups from zero. Technical, skeptical buyers are exactly where most reps stall and where a real playbook wins."},
    {"q":"How much does a fractional CRO for SaaS cost?","a":"Engagements run $6,000 to $22,000 a month depending on how many hours a day you need, far below a $250,000-plus full-time CRO hire, billed monthly with no lock-in."}],
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
    {"q":"Can you build and manage a distributor network for hardware?","a":"Yes. Recruiting, signing and managing distributors and resellers across markets is a core part of how I sell IoT and hardware, alongside direct sales."},
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
  "desc":"A fractional CRO for manufacturers: open new territories and channels, sign distributors and retail chains, and get product onto shelves in markets you wrote off.",
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
    {"q":"How much does a fractional CRO for manufacturers cost?","a":"Engagements run $6,000 to $22,000 a month depending on involvement, billed monthly with no long-term lock-in, far below a full-time hire."}],
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
    {"h":"What it costs","p":["A fractional CRO is priced by how much of the week you need, not by a full salary. Expect roughly $6,000 a month for a couple of hours a day, up to around $22,000 for full-time and exclusive, billed monthly. Compare that to $250,000-plus all in for a full-time CRO once you add equity, bonus, severance risk and a long hiring cycle."]},
  ],
  "faqs":[
    {"q":"How much does it cost to hire a fractional CRO?","a":"Typically $6,000 to $22,000 a month depending on how many hours a day you need, billed monthly with no long-term lock-in, far below a $250,000-plus full-time CRO."},
    {"q":"How fast can a fractional CRO start?","a":"Quickly. A good one diagnoses in week one, gives you a plan and a real forecast in week two, and is running the motion by week three, instead of the months a full-time hire takes to find and ramp."},
    {"q":"Fractional CRO or full-time CRO?","a":"Hire fractional when the work is not yet a full week or you need results now without the cost and risk of a full-time hire. Move to full-time when the function is big enough to justify a senior salary all year."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service, compare <a href="/fractional-cro-vs-vp-of-sales">CRO vs VP of Sales</a> and <a href="/fractional-cro-cost">the cost</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"when-do-you-need-a-fractional-cro",
  "title":"When Do You Need a Fractional CRO? The Signs | Tal Paperin",
  "desc":"The clear signs you need a fractional CRO: stalled revenue, no owner of the number, churned VPs, a great product that will not sell.",
  "h1":"When Do You Need a Fractional CRO?","eyebrow":"Guide",
  "lead":"Most companies wait too long. Here are the signs you need a fractional CRO now, not after another lost quarter.",
  "sections":[
    {"h":"The signs","ul":["Revenue has stalled and nobody actually owns the number","You are scaling and need senior leadership before you can justify a full-time CRO","You have churned through VPs of Sales who did not move the number","You have a great product that just will not sell at scale","Your pipeline and forecast are guesses, not a system","Founders are still the only ones who can close","You want to enter a new market and do not know where to start"]},
    {"h":"What changes when someone owns the number","p":["A fractional CRO takes the strategy, the team, the pipeline, the forecast and the accountability off your plate and onto theirs. Week one is diagnosis, week two is a plan and a real forecast, then they run it, hiring where needed, training the team you have and replacing who cannot. You stop guessing and start operating."]},
    {"h":"What waiting costs","p":["The cost of waiting is a wrong VP hire, a year lost, and six figures spent learning what a senior operator would have told you in week one. Stalled revenue rarely fixes itself, and the longer the motion stays broken, the more it costs to rebuild."]},
  ],
  "faqs":[
    {"q":"What is the difference between a fractional CRO and a consultant?","a":"A consultant hands you a deck and leaves. A fractional CRO owns the work, the pipeline, the deals and the number, and answers for the result."},
    {"q":"Is my company too small for a fractional CRO?","a":"If you have a product and some revenue but no repeatable motion or senior owner of the number, you are the right size. Fractional exists so you get CRO-level leadership without a full-time salary."},
    {"q":"How quickly will I see results?","a":"You get a diagnosis in week one and a plan and forecast in week two. Pipeline and process improvements follow as the motion gets built and run."}],
  "related":'See <a href="/how-to-hire-a-fractional-cro">how to hire a fractional CRO</a>, the <a href="/services/fractional-cro">service</a>, or <a href="/contact">tell me where revenue stalled</a>.'},

 {"slug":"fractional-cro-for-startups",
  "title":"Fractional CRO for Startups | Tal Paperin",
  "desc":"A fractional CRO for startups: senior revenue leadership from first revenue to Series B without a full-time hire. The motion, the team and the number.",
  "h1":"Fractional CRO for Startups","eyebrow":"For Startups",
  "lead":"Startups need senior revenue leadership before they can afford it. That gap is what a fractional CRO fills: I build the motion, hire the team and own the number, without a full-time salary.",
  "sections":[
    {"h":"Why startups stall on revenue","p":["Most startups get the first deals from the founders and the network, then stall because there is no repeatable motion and nobody senior owns the number. Hiring a $250,000 CRO too early burns runway; hiring junior reps with no leader burns time. A fractional CRO gives you the senior owner now and builds the engine the reps will run."]},
    {"h":"What I build for a startup","ul":["A validated ICP, positioning and pricing for how you actually get bought","The outbound and inbound motion, the playbook, the CRM and the pipeline","The first sales hires, trained and managed, and the ones to replace","A real forecast the board can trust","The founders out of every deal and into the right ones"]},
    {"h":"Built for real startups","p":["I have come in as fractional VP of Sales from day one, defined the ICP, built the outbound motion from zero and rebuilt it through pivots. Same discipline whether you are pre-seed or Series B: own the number, build the motion, make the team hit quota."]},
  ],
  "faqs":[
    {"q":"When should a startup hire a fractional CRO?","a":"When the founders are still the only ones closing, or you need a repeatable motion and a forecast before you can justify a full-time CRO. Usually from first revenue through Series B."},
    {"q":"Is a fractional CRO affordable for a startup?","a":"Yes, that is the point. You get senior revenue leadership for $6,000 to $22,000 a month, billed monthly, instead of a $250,000-plus full-time salary plus equity."},
    {"q":"Will you actually sell or just advise?","a":"I sell and build. I get in the pipeline and the deals, hire and manage the reps, and own the forecast, not a slide deck."}],
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
  "desc":"A fractional VP of Sales who builds and runs your sales team, the playbook and the pipeline, hands-on, without a full-time hire.",
  "h1":"Fractional VP of Sales","eyebrow":"Guide",
  "lead":"Need someone to build the team and run the sales floor, not just set strategy? That is a fractional VP of Sales. I hire, train and manage the reps and own the pipeline, part-time.",
  "sections":[
    {"h":"Fractional VP of Sales vs fractional CRO","p":["A VP of Sales runs the sales team and the pipeline day to day. A CRO owns all of revenue, sales, marketing and go-to-market, and the number itself. I do both; the right title depends on whether you need the sales floor run or the whole revenue function owned. Many companies start with a fractional VP of Sales and grow the scope into CRO."]},
    {"h":"What I own as fractional VP of Sales","ul":["Hiring, training and managing SDRs, AEs and BDs","The playbook, the talk tracks and the sales process","The CRM, the pipeline and the forecast","Coaching reps to quota and replacing who cannot","Day-to-day management of the sales floor"]},
    {"h":"Built the team before, many times","p":["I have recruited, trained and managed sales teams across four continents and 40-plus countries, from first reps to full floors with SDRs, AEs, post-sales and tech support. I make the team you have hit quota and build the team you do not have yet."]},
  ],
  "faqs":[
    {"q":"What does a fractional VP of Sales do?","a":"Builds and runs your sales team and pipeline part-time: hiring, training and managing reps, owning the playbook, the CRM and the forecast, and coaching the team to quota."},
    {"q":"Fractional VP of Sales or fractional CRO?","a":"Choose a VP of Sales to run the sales team and pipeline. Choose a CRO to own all of revenue including marketing and go-to-market. I do both and can grow the scope as you do."},
    {"q":"How much does a fractional VP of Sales cost?","a":"Typically $6,000 to $22,000 a month depending on hours, billed monthly with no lock-in, far below a full-time VP salary."}],
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
    {"q":"What does it cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> service or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-roi",
  "title":"Is a Fractional CRO Worth It? The ROI | Tal Paperin",
  "desc":"The business case for a fractional CRO: what it costs, what it returns, and how it compares to a full-time hire or doing nothing.",
  "h1":"Is a Fractional CRO Worth It?","eyebrow":"Guide",
  "lead":"A fractional CRO is not a cost, it is a bet on the number. Here is the honest business case: what you pay, what it returns, and what doing nothing costs.",
  "sections":[
    {"h":"What you pay","p":["Roughly $6,000 to $22,000 a month depending on how much of the week you need, billed monthly with no long-term contract. No equity, no bonus, no severance risk, no recruiting fee, no ramp."]},
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
    {"h":"Run by people who have built floors","p":["This is not a call center. The SDR team sits under senior sales leadership that has recruited, trained and managed reps across four continents, on a playbook that actually books meetings."]},
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
    {"q":"What does a fractional CRO for cybersecurity cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time CRO."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a>, <a href="/services/go-to-market-strategy">go-to-market</a> and <a href="/services/distributor-channel-recruitment">channel</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-fintech","en_only":True,
  "title":"Fractional CRO for Fintech Companies | Tal Paperin",
  "desc":"A fractional CRO for fintech: long, compliance-heavy B2B cycles into banks and enterprises, owned end to end without a full-time hire.",
  "h1":"Fractional CRO for Fintech","eyebrow":"Industry",
  "lead":"Fintech sells into cautious, regulated buyers through long cycles and heavy diligence. I build and own the revenue motion that closes those deals, without a full-time CRO salary.",
  "sections":[
    {"h":"Why fintech sales are hard","p":["Selling fintech B2B means long cycles, security and compliance reviews, procurement, and risk-averse buyers at banks, insurers and enterprises. Founders often get early traction then stall when deals get bigger and the buying process gets heavier. The fix is a motion built for that reality and someone senior owning the pipeline and the forecast."]},
    {"h":"What I build","ul":["An ICP and message for regulated, risk-averse buyers","A sales motion that survives compliance, security and procurement reviews","Reps who can run a long, multi-stakeholder enterprise sale","Partnerships and channels where they shorten the path","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for long, complex B2B sales","p":["I have run complex, high-value B2B and B2G deals across four continents, the kind with many stakeholders, formal procurement and a long road to signature. That is exactly the shape of a serious fintech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into regulated, enterprise buyers?","a":"Yes. I have run complex, high-value B2B and B2G deals with formal procurement and many stakeholders across four continents, the same shape as enterprise fintech sales."},
    {"q":"Can you handle long, compliance-heavy cycles?","a":"That is the job. I build a motion that survives security, compliance and procurement reviews and keeps multi-stakeholder deals moving to signature."},
    {"q":"What does a fractional CRO for fintech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/contract-negotiation">contract negotiation</a> services, or <a href="/contact">get in touch</a>.'},

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
    {"q":"What does a fractional CRO for defense tech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/b2g-public-sector">B2G and public-sector</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-ai-companies","en_only":True,
  "title":"Fractional CRO for AI Companies | Tal Paperin",
  "desc":"A fractional CRO for AI and deep-tech startups: turning a powerful product into a repeatable B2B sales motion, owned end to end.",
  "h1":"Fractional CRO for AI Companies","eyebrow":"Industry",
  "lead":"AI startups have powerful products and no repeatable way to sell them. I turn the technology into a motion: ICP, pricing, pipeline, team and the number, without a full-time CRO.",
  "sections":[
    {"h":"Why AI companies stall on revenue","p":["AI and deep-tech teams are brilliant at the product and improvise the sales. The result is a few design-partner deals and no repeatable motion, unclear pricing, and buyers who are curious but not sure what they are buying. The fix is a sharp ICP, pricing and a motion built for a technical, skeptical buyer, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and a value proposition a buyer understands, not a demo","Pricing and packaging for an AI product that is still evolving","The outbound and inbound motion, the playbook and the pipeline","Reps who can sell a technical product to skeptical buyers","The forecast and the number, owned end to end"]},
    {"h":"Built selling hard technical products","p":["I came in as fractional VP of Sales at an AI startup from day one, defined the ICP, built the outbound motion from zero and rebuilt it through pivots, and I have sold scientific and technical software into universities, labs and pharma. AI buyers are skeptical and technical, exactly where a real motion beats a great demo."]},
  ],
  "faqs":[
    {"q":"Can you sell a technical AI product?","a":"Yes. I have built the sales motion for an AI startup from zero and sold scientific and technical software into skeptical, technical buyers. The win comes from a real motion, not just a demo."},
    {"q":"How do you price an AI product that keeps changing?","a":"With packaging and pricing built for where the product is now and able to evolve, tied to the value the buyer actually gets, not to model costs."},
    {"q":"What does a fractional CRO for AI companies cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for digital health cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for climate tech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"Do you handle international foodtech expansion?","a":"Yes. Market entry across four continents, including building the local channel, is one of the things I do."},
    {"q":"What does a fractional CRO for foodtech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/distributor-channel-recruitment">channel</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-agritech","en_only":True,
  "title":"Fractional CRO for Agritech Companies | Tal Paperin",
  "desc":"A fractional CRO for agritech: selling into growers, cooperatives, distributors and agribusiness, channel and direct, across borders.",
  "h1":"Fractional CRO for Agritech","eyebrow":"Industry",
  "lead":"Agritech sells into growers, cooperatives, distributors and agribusiness, often a hardware, software and services mix across borders. I build and own the motion that wins those deals.",
  "sections":[
    {"h":"Why agritech sales are hard","p":["Your buyers are growers, cooperatives, distributors and large agribusinesses, spread across regions and slow to change, and your product is often a mix of hardware, software and services. It is a channel-heavy, international, long-cycle sale that most teams are not built to run. The fix is a real channel strategy plus direct selling, owned by someone senior."]},
    {"h":"What I build","ul":["A channel of distributors and partners that reach growers and agribusiness","Direct sales into large agribusinesses and cooperatives","Market entry where the opportunity is across borders","An ICP, pricing and message for a practical, ROI-driven buyer","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for channel and cross-border sales","p":["I have built distributor networks and run international market entry for IoT, hardware and manufacturing companies, selling devices, software and services through channel and direct across four continents. Agritech sits squarely in that world."]},
  ],
  "faqs":[
    {"q":"Can you build our agritech channel?","a":"Yes. Reaching growers and agribusiness usually runs through distributors and partners, and building and managing that channel is part of the work, alongside direct sales into large accounts."},
    {"q":"Do you handle international expansion for agritech?","a":"Yes. I run market entry across four continents, including building the local channel and team."},
    {"q":"What does a fractional CRO for agritech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for robotics cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for semiconductors cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guide and the <a href="/services/market-entry">market entry</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-logistics","en_only":True,
  "title":"Fractional CRO for Logistics and Supply Chain Companies | Tal Paperin",
  "desc":"A fractional CRO for logistics, supply chain and mobility tech: enterprise and operations buyers, long cycles, channel and direct.",
  "h1":"Fractional CRO for Logistics and Supply Chain","eyebrow":"Industry",
  "lead":"Logistics and supply-chain tech sells into operations-heavy enterprises through long, ROI-driven cycles. I build and own the revenue motion that wins those accounts.",
  "sections":[
    {"h":"Why logistics sales are hard","p":["You sell into operations, procurement and IT at enterprises that run on thin margins and do not change vendors lightly, through long cycles and hard ROI scrutiny, often internationally. Early traction stalls when deals get bigger and the buying committee grows. The fix is a motion built for that buyer and someone senior owning the pipeline and forecast."]},
    {"h":"What I build","ul":["An ICP and ROI-driven message for operations and procurement buyers","A motion that handles long cycles and multi-stakeholder committees","Direct sales into large enterprise and operations accounts","Channels and partnerships where they shorten the path","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for complex, international B2B","p":["I have built and run complex B2B sales into large enterprise and industrial accounts across four continents, including the operations-heavy, ROI-driven buyers that logistics and supply-chain tech sell to."]},
  ],
  "faqs":[
    {"q":"Have you sold into enterprise operations buyers?","a":"Yes. I have run complex B2B sales into large enterprise and industrial accounts internationally, the same operations-heavy, ROI-driven buyers logistics tech sells to."},
    {"q":"Can you handle long, multi-stakeholder cycles?","a":"Yes. I build a motion that keeps long, committee-driven deals moving to signature and a forecast you can trust."},
    {"q":"What does a fractional CRO for logistics cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/market-entry">market entry</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"us-market-entry-for-israeli-startups","en_only":True,
  "title":"US Market Entry for Israeli Startups | Tal Paperin",
  "desc":"Break into the US market the right way. An operator who has built US and global sales for Israeli and international companies, on the ground.",
  "h1":"US Market Entry for Israeli Startups","eyebrow":"Market Entry",
  "lead":"The US is where Israeli startups win or burn their runway. I help you enter it the right way: pick the beachhead, build the motion and the team, and sell, on US hours, on the ground.",
  "sections":[
    {"h":"Why Israeli startups stumble in the US","p":["Great Israeli tech often stalls in the US because the sale is run from Israel on Israeli assumptions: the wrong ICP, a message that does not land, no US presence, and founders trying to close a market they do not yet understand. The US rewards focus and presence, not a part-time experiment from eight time zones away."]},
    {"h":"What I do","ul":["Pick the right beachhead segment instead of spreading thin","Adapt the ICP, positioning and pricing for the US buyer","Build the motion, hire the first US reps and manage them","Open the first accounts and lead the key deals personally","Stand up the US presence, direct or through partners"]},
    {"h":"Built for this exact move","p":["I am based in Israel and work US hours, and I have built and run sales in the US and across four continents for Israeli and international companies. I know the expensive mistakes before you make them, and I have opened markets others wrote off."]},
  ],
  "faqs":[
    {"q":"Can you help an Israeli startup enter the US market?","a":"Yes. I help pick the beachhead, adapt the ICP, positioning and pricing for the US buyer, build the motion and the first US team, and open the first accounts, working US hours."},
    {"q":"Do I need a US entity and US reps?","a":"Often eventually, but not always on day one. I help you sequence it: prove the motion, then stand up the presence and team, direct or through partners, when it is justified."},
    {"q":"What does this cost?","a":"Fractional engagements run $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time US sales leader."}],
  "related":'See the <a href="/services/market-entry">market entry</a> service and the <a href="/fractional-cro-israel">fractional CRO in Israel</a> guide, or <a href="/contact">get in touch</a>.'},

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
    {"q":"What does an outsourced CRO cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time CRO."}],
  "related":'See <a href="/how-to-hire-a-fractional-cro">how to hire one</a> and the <a href="/services/fractional-cro">fractional CRO</a> service, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-insurtech","en_only":True,
  "title":"Fractional CRO for Insurtech Companies | Tal Paperin",
  "desc":"A fractional CRO for insurtech: selling to carriers, brokers and a regulated, conservative industry through long cycles, owned end to end.",
  "h1":"Fractional CRO for Insurtech","eyebrow":"Industry",
  "lead":"Insurtech sells into carriers, brokers and a cautious, regulated industry through long cycles and partnerships. I build and own the revenue motion that wins those deals.",
  "sections":[
    {"h":"Why insurtech sales are hard","p":["You sell into carriers, MGAs and brokers: conservative, regulated buyers with committees, compliance and procurement, and a strong preference for partners over newcomers. Distribution often runs through the incumbents you are trying to disrupt. It takes a motion built for long, relationship-heavy, regulated sales and someone senior owning the pipeline."]},
    {"h":"What I build","ul":["An ICP and message for carriers, MGAs and brokers","A motion that survives compliance, procurement and committees","Carrier and broker partnerships that become distribution","Reps who can run a long, multi-stakeholder regulated sale","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for regulated, partnership-driven sales","p":["I have run complex, high-value B2B and B2G deals with formal procurement and many stakeholders across four continents, and built channel and partner networks that became real distribution. That is the shape of an insurtech sale."]},
  ],
  "faqs":[
    {"q":"Have you sold into regulated, conservative industries?","a":"Yes. I have run complex, multi-stakeholder regulated deals with formal procurement across four continents, the same dynamics as selling to carriers and brokers."},
    {"q":"Can you build carrier and broker partnerships?","a":"Yes. Insurtech distribution often runs through carriers and brokers, and building and managing those partnerships is part of the work."},
    {"q":"What does a fractional CRO for insurtech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/distributor-channel-recruitment">channel</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-proptech","en_only":True,
  "title":"Fractional CRO for Proptech Companies | Tal Paperin",
  "desc":"A fractional CRO for proptech and real-estate tech: selling to owners, operators and brokerages in a slow-moving industry, owned end to end.",
  "h1":"Fractional CRO for Proptech","eyebrow":"Industry",
  "lead":"Proptech sells into owners, operators and brokerages, a relationship-driven, slow-to-change industry. I build and own the revenue motion that gets you adopted at scale.",
  "sections":[
    {"h":"Why proptech sales are hard","p":["Real estate owners, operators and brokerages are relationship-driven, fragmented and slow to adopt new tools, and a pilot in one building rarely rolls out on its own. You need a motion that lands the first accounts, proves ROI on the ground, and turns pilots into portfolio-wide deals, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and ROI-driven message for owners, operators and brokerages","A motion that turns single-site pilots into portfolio rollouts","Direct sales into large owners and operators","Partnerships and channels that reach a fragmented market","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for relationship-driven, on-the-ground sales","p":["I have opened markets on the ground across four continents, sold direct into large accounts and built the channel to reach fragmented buyers. Proptech rewards exactly that mix of direct selling and a real channel."]},
  ],
  "faqs":[
    {"q":"Can you turn proptech pilots into bigger deals?","a":"Yes. The job is building a motion that proves ROI in the first sites and expands pilots into portfolio-wide rollouts, not leaving them stuck as one-offs."},
    {"q":"Do you sell direct or through channel?","a":"Both. Proptech usually needs direct sales into large owners and operators plus partnerships to reach a fragmented market."},
    {"q":"What does a fractional CRO for proptech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-legaltech","en_only":True,
  "title":"Fractional CRO for Legaltech Companies | Tal Paperin",
  "desc":"A fractional CRO for legaltech: selling to law firms and general counsel, conservative buyers and procurement, owned end to end.",
  "h1":"Fractional CRO for Legaltech","eyebrow":"Industry",
  "lead":"Legaltech sells into law firms and general counsel, conservative buyers who move slowly and buy by committee. I build and own the revenue motion that wins those accounts.",
  "sections":[
    {"h":"Why legaltech sales are hard","p":["Law firms and in-house legal teams are risk-averse, consensus-driven and slow to change tools, with partners, committees and procurement all in the path. Adoption stalls without a clear ROI case and a motion built for cautious, multi-stakeholder buyers, owned by someone senior."]},
    {"h":"What I build","ul":["An ICP and message for law firms and general counsel","A motion that handles committees, partners and procurement","A clear ROI and risk case the buyer can defend internally","Reps who can run a long, consensus-driven sale","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for conservative, multi-stakeholder buyers","p":["I have run complex, high-value B2B deals with many stakeholders and formal procurement across four continents. The careful, consensus-driven legal buyer is exactly that kind of sale."]},
  ],
  "faqs":[
    {"q":"Have you sold to conservative, committee-driven buyers?","a":"Yes. Complex, multi-stakeholder deals with procurement and a long road to consensus are the deals I have run for years, the same shape as selling to law firms."},
    {"q":"How do you speed up a slow legal sale?","a":"With a clear ROI and risk case the buyer can defend internally, and a motion that keeps every stakeholder moving instead of letting the deal stall."},
    {"q":"What does a fractional CRO for legaltech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/contract-negotiation">contract negotiation</a> services, or <a href="/contact">get in touch</a>.'},

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
    {"q":"What does a fractional CRO for HR tech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for edtech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for developer tools cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for biotech cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-medical-devices">medical devices</a> and <a href="/fractional-cro-for-digital-health">digital health</a> guides, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-telecom","en_only":True,
  "title":"Fractional CRO for Telecom Companies | Tal Paperin",
  "desc":"A fractional CRO for telecom and connectivity: selling to carriers and operators through RFPs, long procurement and channel, owned end to end.",
  "h1":"Fractional CRO for Telecom","eyebrow":"Industry",
  "lead":"Telecom sells into carriers and operators through RFPs, long procurement and a global channel. I build and own the revenue motion that wins those deals.",
  "sections":[
    {"h":"Why telecom sales are hard","p":["Carriers and operators are large, bureaucratic and slow, buying through RFPs, long procurement and entrenched vendor relationships, often across borders. It is one of the hardest enterprise sales there is, and it needs someone who has run formal, multi-stakeholder, international deals owning the pipeline."]},
    {"h":"What I build","ul":["An ICP and message for carriers, operators and large enterprises","A motion built for RFPs, procurement and long cycles","The channel: integrators, resellers and partners that carry telecom","Direct relationships with key carrier and operator accounts","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for formal, international, channel sales","p":["I have run B2G and complex public-sector deals with RFIs and RFQs, built international distributor and channel networks, and managed long, formal procurement across four continents. Telecom sits squarely in that world."]},
  ],
  "faqs":[
    {"q":"Can you run RFP and procurement-driven deals?","a":"Yes. Formal RFIs, RFQs, RFPs and long procurement with many stakeholders are deals I have run internationally for years."},
    {"q":"Can you build the telecom channel?","a":"Yes. Telecom often sells through integrators and partners, and building and managing international channel networks is core to what I do."},
    {"q":"What does a fractional CRO for telecom cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
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
    {"q":"What does a fractional CRO for energy cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/fractional-cro-for-climate-tech">climate tech</a> and <a href="/fractional-cro-for-iot-hardware">IoT and hardware</a> guides, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-professional-services","en_only":True,
  "title":"Fractional CRO for Professional Services Firms | Tal Paperin",
  "desc":"A fractional CRO for agencies, consultancies and professional-services firms: building real business development beyond founder-led referrals.",
  "h1":"Fractional CRO for Professional Services","eyebrow":"Industry",
  "lead":"Agencies and consultancies live on referrals and the founder's network, then plateau. I build the business-development engine that grows revenue beyond who you already know.",
  "sections":[
    {"h":"Why professional-services firms plateau","p":["Agencies, consultancies and services firms grow on referrals and the founders' relationships, then hit a ceiling when those run out. Most have never built real business development: a defined ICP, an outbound motion, a pipeline and someone who owns the number instead of waiting for the phone to ring."]},
    {"h":"What I build","ul":["A defined ICP and positioning beyond word of mouth","A real business-development motion and pipeline","The first business-development hires, trained and managed","The founders out of every pitch and into the right ones","The pipeline, the forecast and the number, owned end to end"]},
    {"h":"Built for relationship and services selling","p":["I have built go-to-market from zero and run the kind of relationship-driven, trust-based selling that services firms depend on, across four continents. The same discipline turns a referral business into one with a real pipeline."]},
  ],
  "faqs":[
    {"q":"Can you grow a referral-based services firm?","a":"Yes. The job is building real business development on top of referrals: an ICP, an outbound motion, a pipeline and someone owning the number, so growth does not depend on who you already know."},
    {"q":"Will the founders still need to sell?","a":"Less, and on the right deals. I build the motion and the team so the founders are not the only ones who can win business."},
    {"q":"What does a fractional CRO for professional services cost?","a":"Typically $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in."}],
  "related":'See the <a href="/services/fractional-cro">fractional CRO</a> and <a href="/services/go-to-market-strategy">go-to-market</a> services, or <a href="/contact">get in touch</a>.'},

 {"slug":"fractional-cro-for-the-us-market","en_only":True,
  "title":"Fractional CRO for the US Market | Tal Paperin",
  "desc":"A fractional CRO to take a foreign or global company into the US market: pick the beachhead, build the motion and the team, and sell, on US hours.",
  "h1":"Fractional CRO for the US Market","eyebrow":"Market Entry",
  "lead":"The US is the prize and the place most foreign companies burn cash. I help you enter it the right way: pick the beachhead, build the motion and the team, and open the first accounts, on US hours.",
  "sections":[
    {"h":"Why foreign companies stall in the US","p":["Companies from Europe, Israel, APAC and beyond bring a product that works at home and run the US sale on home assumptions: the wrong ICP, a message that does not land, no US presence and leadership eight time zones away. The US rewards focus and presence, and punishes a part-time experiment run from abroad."]},
    {"h":"What I do","ul":["Pick the right beachhead segment instead of spreading thin","Adapt the ICP, positioning and pricing for the US buyer","Build the motion, hire the first US reps and manage them","Open the first accounts and lead the key deals personally","Stand up the US presence, direct or through partners"]},
    {"h":"Built for cross-border entry into the US","p":["I am based in Israel and work US hours, and I have built and run sales in the US and across four continents and 40-plus countries for foreign and global companies. I know the expensive mistakes before you make them, and I have opened markets others wrote off."]},
  ],
  "faqs":[
    {"q":"Can you take a foreign company into the US market?","a":"Yes. I help pick the beachhead, adapt the ICP, positioning and pricing for the US buyer, build the motion and the first US team, and open the first accounts, working US hours."},
    {"q":"Do I need a US entity and US team on day one?","a":"Not always. I help you sequence it: prove the motion first, then stand up the presence and team, direct or through partners, when it is justified."},
    {"q":"What does this cost?","a":"Fractional engagements run $6,000 to $22,000 a month depending on involvement, billed monthly with no lock-in, far below a full-time US sales leader."}],
  "related":'See the <a href="/services/market-entry">market entry</a> service and the <a href="/us-market-entry-for-israeli-startups">US entry for Israeli startups</a> guide, or <a href="/contact">get in touch</a>.'},
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
 {"slug":"fractional-cro-cost",
  "title":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ? | טל פאפרין",
  "desc":"תשובה ישירה על תמחור סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ: כמה זה עולה בחודש, איך זה משתווה לסמנכ״ל מכירות ופיתוח עסקי במשרה מלאה של 250 אלף דולר, מה כלול, ומתי כל רמה שווה את זה.",
  "h1":"כמה באמת עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ","eyebrow":"מדריך",
  "lead":"רוב היועצים מסתירים את המחיר, מגישים לכם מצגת, ונעלמים. אני מפעיל שעדיין מוכר בעצמו, מחייב חודשית בלי חוזה, והנה בדיוק כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, במספרים ברורים.",
  "sections":[
    {"h":"התשובה הקצרה","p":[
      "סמנכ״ל מכירות ופיתוח עסקי במשרה מלאה עולה 250 אלף דולר ומעלה בסך הכל, אחרי שמוסיפים בסיס, אקוויטי, בונוס, סיכון פיצויי פיטורין ומחזור גיוס של חודשים. סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ נותן לכם את אותה מנהיגות בכירה בתשלום חודשי. התפקיד זהה בכל רמה. הדבר היחיד שמשתנה הוא כמה שעות ביום אני בעסק שלכם."]},
    {"h":"שלוש הרמות, לפי כמה ממני אתם צריכים","tiers":[
      "Starter, 6,000 דולר בחודש. אני, סמנכ״ל המכירות ופיתוח העסקי שלכם, בתוך העסק שעתיים ביום, בכל יום עבודה. אני מחזיק את האסטרטגיה, השיטה והסטנדרטים, והצוות שלכם מבצע את רוב היומיום.",
      "Growth, 12,000 דולר בחודש. חצי משרה, ארבע שעות ביום. כבר לא רק מכוון, מניע: אני מריץ את המוטור שבוע אחר שבוע, מנהל את הצוות בידיים, ונושא איתכם במספר. מה שרוב החברות בוחרות.",
      "בעלות מלאה, 22,000 דולר בחודש. משרה מלאה ובלעדית. כולי על ההכנסות שלכם, על פני מכירות, שיווק ו-Go-to-Market, וכל עוד אני אחראי על התוצאות שלכם אני לא לוקח אף לקוח אחר. בכפוף לזמינות."]},
    {"h":"למה זה זול יותר מגיוס במשרה מלאה","ul":[
      "בלי בסיס של 250 אלף דולר, אקוויטי, בונוס או סיכון פיצויים",
      "בלי חיפוש גיוס של שלושה חודשים ובלי התברגות של שני רבעונים",
      "חיוב חודשי, בלי חוזה, בלי נעילה, בלי קנסות יציאה: לא אהבתם, סיימנו בסוף החודש",
      "תוצאות בשבוע הראשון, לא בחודש השישי"]},
    {"h":"אתם שוכרים מפעיל, לא יועץ","p":[
      "רוב היועצים מגישים לכם מצגת ונעלמים. הם מעולם לא נשאו אחריות על מספר. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר, ואני עדיין עושה את המכירה בעצמי, בפייפליין ובעסקאות. ואני מחייב חודשית בלי חוזה, אז אני שומר על העבודה בזכות זה שאני טוב בה, לא בזכות חוזה שכולא אתכם."]},
  ],
  "faqs":[
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ?","a":"הפרויקטים שלי נעים בין 6,000 ל-22,000 דולר בחודש לפי רמת המעורבות, לעומת 250 אלף דולר ומעלה לסמנכ״ל מכירות ופיתוח עסקי במשרה מלאה אחרי אקוויטי, בונוס ופיצויים."},
    {"q":"האם סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ זול יותר מסמנכ״ל מכירות ופיתוח עסקי במשרה מלאה?","a":"כן. אתם מקבלים את אותה מנהיגות בכירה בלי המשכורת, האקוויטי, הבונוס, סיכון הפיצויים, מחזור הגיוס או ההתברגות הארוכה, ובלי נעילה לטווח ארוך."},
    {"q":"מה כלול?","a":"אותו דבר בכל רמה: אבחון הכנסות, אסטרטגיית מכירות ותחזית, Playbook, מבנה CRM ופייפליין, הכשרת צוות, ניהול מעשי של התנועה, החלטות גיוס וביצועים, ואחריות מלאה על מכירות, שיווק ו-Go-to-Market. מה שמשתנה בין הרמות הוא כמה שעות ביום אני בעסק שלכם: שעתיים, ארבע שעות, או משרה מלאה."},
    {"q":"כמה זמן נמשך פרויקט סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ?","a":"אין נעילה לטווח ארוך. אתם מגדילים את המעורבות ככל שאתם גדלים, או מעבירים את הפונקציה הלאה כשהיא בנויה."},
    {"q":"האם אני צריך לחתום על חוזה ארוך?","a":"לא. אני מחייב חודשית בלי חוזה ובלי קנסות יציאה. אם לא אהבתם מה שאני מספק, סיימנו בסוף החודש ואתם לא חייבים עוד כלום."}],
  "related":'ראו את <a href="/he/services/fractional-cro">שירות הסמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a>, <a href="/he/case-studies">מקרי מבחן</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>. מהבלוג: <a href="/he/blog/fractional-cro-explained">סמנכ״ל מכירות ופיתוח עסקי במשרה חלקית, מה זה</a>, <a href="/he/blog/cost-of-bad-vp-sales-hire">כמה עולה גיוס כושל של סמנכ״ל מכירות</a>.'},

 {"slug":"fractional-cro-vs-outsourced-sales",
  "title":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול מכירות במיקור חוץ: מה אתם צריכים? | טל פאפרין",
  "desc":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ, מכירות במיקור חוץ מלא, או מערכת שאתם מריצים לבד? פירוק ישיר של מה מתאים לשלב שלכם, ואיך לבחור.",
  "h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול מכירות במיקור חוץ","eyebrow":"מדריך",
  "lead":"שלוש דרכים לתקן הכנסות, החלטה אחת. בכל אחת אתם מקבלים מפעיל שעדיין מוכר בעצמו, בחיוב חודשי בלי חוזה ובלי נעילה. הנה איזו מהן מתאימה לשלב שלכם, ואיזו מבזבזת לכם כסף.",
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
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ בישראל?","a":"הפרויקטים נעים בין 6,000 ל-22,000 דולר בחודש לפי רמת המעורבות, הרבה מתחת לגיוס סמנכ״ל מכירות ופיתוח עסקי במשרה מלאה של 250 אלף דולר ומעלה."}],
  "related":'ראו את שירותי <a href="/he/services/market-entry">כניסה לשוק</a> ו-<a href="/he/services/fractional-cro">סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ</a>, או <a href="/fractional-cro-israel">הגרסה באנגלית</a>. מהבלוג: <a href="/he/blog/entering-the-us-market">כניסה לשוק האמריקאי</a>, <a href="/he/blog/why-israeli-startups-fail-at-sales">למה סטארטאפים ישראלים נכשלים במכירות בחו״ל</a>.'},

 {"slug":"fractional-cro-vs-vp-of-sales",
  "title":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול גיוס VP מכירות | טל פאפרין",
  "desc":"נמאס לכם מגיוסי VP מכירות של 30 אלף דולר בחודש שאתם מפטרים תוך 90 יום? סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ נותן מנהיגות הכנסות מוכחת בלי הימור גיוס, בלי פיצויים ובלי נעילה.",
  "h1":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול גיוס VP מכירות","eyebrow":"מדריך",
  "lead":"כבר עשיתם את זה. שכרתם VP מכירות בשלושים אלף בחודש, חיכיתם, ראיתם שכלום לא זז, פיטרתם בחודש השלישי, אכלתם את הפיצויים, התחלתם מחדש. הנה האלטרנטיבה.",
  "sections":[
    {"h":"בית הקברות של ה-VP מכירות","p":[
      "VP מכירות עולה 30,000 דולר בחודש או יותר, בסך הכל. החיפוש לוקח חודשים. ההתברגות לוקחת רבעון. ואם ההתאמה שגויה, וזה קורה הרבה, אתם מפטרים בחודש השני, השלישי או הרביעי, אוכלים את הפיצויים, ומתחילים את כל המחזור מחדש. ראיתי מייסדים שורפים מאות אלפי דולרים ככה, בלי שום דבר להראות מלבד זמן אבוד.",
      "הגיוס הוא הימור. אתם מהמרים שש ספרות על קורות חיים ושלושה ראיונות."]},
    {"h":"סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ הוא לא הימור","ul":[
      "בניתי והרצתי הכנסות ל-30 ומעלה חברות B2B בארבע יבשות. אתם לא מהמרים אם אני יכול לעשות את זה. כבר עשיתי",
      "בלי דמי מגייסים, בלי אקוויטי, בלי סיכון פיצויים, בלי חיפוש של חודשים",
      "תוצאות בשבוע הראשון: אני מאבחן איפה העסקאות דולפות, ואז מריץ את התיקון. בלי התברגות, בלי עקומת למידה"]},
    {"h":"אני עדיין מוכר. בעצמי. ידיים בבוץ.","p":[
      "רוב היועצים מגישים לכם מצגת ונעלמים. הם מעולם לא נשאו אחריות על מספר. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר, ואני עדיין עושה את המכירה בעצמי, בטלפון, בחדר, בעסקה. אתם שוכרים מפעיל, לא יועץ."]},
    {"h":"חודשי. בלי חוזה. בלי בני ערובה.","p":[
      "אני מחייב חודשית. בלי חוזה ארוך, בלי נעילה, בלי קנסות יציאה. לא אהבתם מה שאני מספק, סיימנו בסוף החודש, ואתם לא חייבים עוד כלום. אני שומר על העבודה כי היא טובה, לא כי חוזה כולא אתכם. זה ההפך מגיוס VP שאי אפשר לבטל בקלות."]},
  ],
  "faqs":[
    {"q":"האם סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ עדיף על גיוס VP מכירות?","a":"אם תנועת המכירות שלכם עוד לא מוכחת, כן. גיוס VP הוא הימור של שש ספרות עם חודשי חיפוש, רבעון התברגות וסיכון פיצויים אמיתי. סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ שעשה את זה 30 פעמים ומעלה מספק מהשבוע הראשון, בלי סיכון גיוס ובלי נעילה."},
    {"q":"כמה עולה סמנכ״ל מכירות ופיתוח עסקי במיקור חוץ מול VP מכירות?","a":"VP מכירות עולה 30,000 דולר בחודש או יותר בסך הכל, פלוס דמי מגייסים, אקוויטי ופיצויים. הפרויקטים שלי במיקור חוץ נעים בין 6,000 ל-22,000 דולר בחודש, בחיוב חודשי בלי חוזה."},
    {"q":"ומה אם זה לא עובד?","a":"אני מחייב חודשית בלי חוזה ובלי קנסות יציאה. אם לא אהבתם מה שאני מספק, סיימנו בסוף החודש ואתם לא חייבים עוד כלום."},
    {"q":"אתה באמת עושה את המכירה, או רק מייעץ?","a":"אני עושה את המכירה. אני VP מכירות גלובלי וסמנכ״ל מכירות ופיתוח עסקי לשעבר ואני עדיין עובד ידיים בבוץ בפייפליין ובעסקאות, לא רק במצגות אסטרטגיה."}],
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
    {"h":"כמה זה עולה","p":["סמנכ״ל הכנסות במיקור חוץ מתומחר לפי כמה מהשבוע אתם צריכים, לא לפי משכורת מלאה. צפו לכ-6,000 דולר בחודש לכמה שעות ביום, ועד כ-22,000 למשרה מלאה ובלעדית, בחיוב חודשי. השוו את זה ל-250,000 דולר ומעלה בסך הכל ל-CRO במשרה מלאה ברגע שמוסיפים אקוויטי, בונוס, סיכון פיצויים ומחזור גיוס ארוך."]},
  ],
  "faqs":[
    {"q":"כמה עולה לשכור Fractional CRO?","a":"בדרך כלל 6,000 עד 22,000 דולר בחודש לפי כמה שעות ביום אתם צריכים, בחיוב חודשי בלי נעילה, הרבה מתחת ל-CRO במשרה מלאה של 250,000 דולר ומעלה."},
    {"q":"כמה מהר אפשר להתחיל?","a":"מהר. טוב מאבחן בשבוע הראשון, נותן תוכנית ותחזית אמיתית בשבוע השני, ומריץ את התהליך מהשבוע השלישי, במקום החודשים שלוקח לגייס ולהתברג למשרה מלאה."},
    {"q":"Fractional CRO או CRO במשרה מלאה?","a":"שכרו במיקור חוץ כשהעבודה עוד לא שבוע מלא או כשאתם צריכים תוצאות עכשיו בלי העלות והסיכון של משרה מלאה. עברו למשרה מלאה כשהפונקציה גדולה מספיק כדי להצדיק משכורת בכירה כל השנה."}],
  "related":'ראו את שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a>, השוו <a href="/he/fractional-cro-vs-vp-of-sales">CRO מול VP מכירות</a> ו<a href="/he/fractional-cro-cost">העלות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

 {"slug":"when-do-you-need-a-fractional-cro",
  "title":"מתי צריך Fractional CRO? הסימנים | טל פאפרין",
  "desc":"הסימנים הברורים שאתם צריכים סמנכ״ל הכנסות במיקור חוץ: הכנסות תקועות, אין בעלים לתוצאות, VP-ים שהתחלפו, מוצר מצוין שלא נמכר.",
  "h1":"מתי צריך Fractional CRO?","eyebrow":"מדריך",
  "lead":"רוב החברות מחכות יותר מדי. הנה הסימנים שאתם צריכים סמנכ״ל הכנסות במיקור חוץ עכשיו, לא אחרי עוד רבעון אבוד.",
  "sections":[
    {"h":"הסימנים","ul":["ההכנסות נתקעו ואף אחד באמת לא אחראי על התוצאות","אתם בצמיחה וצריכים הנהגה בכירה לפני שאפשר להצדיק משרה מלאה","התחלפתם בכמה VP מכירות שלא הזיזו את התוצאות","יש לכם מוצר מצוין שפשוט לא נמכר בקנה מידה","הפייפליין והתחזית שלכם הם ניחושים, לא מערכת","המייסדים עדיין היחידים שיכולים לסגור","אתם רוצים להיכנס לשוק חדש ולא יודעים מאיפה להתחיל"]},
    {"h":"מה משתנה כשמישהו אחראי על התוצאות","p":["סמנכ״ל הכנסות במיקור חוץ לוקח את האסטרטגיה, הצוות, הפייפליין, התחזית והאחריות מהצלחת שלכם אל שלו. שבוע ראשון זה אבחון, שבוע שני זה תוכנית ותחזית אמיתית, ואז הוא מריץ את זה, מגייס איפה שצריך, מכשיר את הצוות שיש לכם ומחליף את מי שלא יכול. אתם מפסיקים לנחש ומתחילים לתפעל."]},
    {"h":"מה עולה לחכות","p":["המחיר של ההמתנה הוא גיוס VP שגוי, שנה שאבדה, ושש ספרות שהוצאו כדי ללמוד מה שאיש ביצוע בכיר היה אומר לכם בשבוע הראשון. הכנסות תקועות כמעט אף פעם לא מתקנות את עצמן, וככל שהתהליך נשאר שבור יותר זמן, כך עולה יותר לבנות אותו מחדש."]},
  ],
  "faqs":[
    {"q":"מה ההבדל בין Fractional CRO ליועץ?","a":"יועץ מגיש מצגת והולך. סמנכ״ל הכנסות במיקור חוץ לוקח אחריות על העבודה, על הפייפליין, על העסקאות ועל התוצאות, ועונה על התוצאה."},
    {"q":"החברה שלי קטנה מדי ל-Fractional CRO?","a":"אם יש לכם מוצר וקצת הכנסות אבל אין תהליך חוזר או בעלים בכיר לתוצאות, אתם בדיוק הגודל הנכון. מיקור חוץ קיים כדי שתקבלו הנהגה ברמת CRO בלי משכורת מלאה."},
    {"q":"כמה מהר אראה תוצאות?","a":"אתם מקבלים אבחון בשבוע הראשון ותוכנית ותחזית בשבוע השני. שיפורים בפייפליין ובתהליך מגיעים ככל שהתהליך נבנה ורץ."}],
  "related":'ראו <a href="/he/how-to-hire-a-fractional-cro">איך לשכור</a> ואת <a href="/he/services/fractional-cro">השירות</a>, או <a href="/he/contact">ספרו לי איפה ההכנסות נתקעו</a>.'},

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
    {"q":"זה אפשרי כלכלית לסטארטאפ?","a":"כן, זו כל הנקודה. אתם מקבלים הנהגת הכנסות בכירה ב-6,000 עד 22,000 דולר בחודש, בחיוב חודשי, במקום משכורת מלאה של 250,000 דולר ומעלה פלוס אקוויטי."},
    {"q":"אתה באמת תמכור או רק תייעץ?","a":"אני מוכר ובונה. אני נכנס לפייפליין ולעסקאות, מגייס ומנהל את הנציגים, ולוקח אחריות על התחזית, לא על מצגת."}],
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
    {"h":"בניתי את הצוות, הרבה פעמים","p":["גייסתי, הכשרתי וניהלתי צוותי מכירות בארבע יבשות וביותר מ-40 מדינות, מנציגים ראשונים ועד רצפות מלאות עם SDR, AE, פוסט-סייל ותמיכה טכנית. אני גורם לצוות שיש לכם לעמוד ביעד ובונה את הצוות שעוד אין לכם."]},
  ],
  "faqs":[
    {"q":"מה עושה VP מכירות במיקור חוץ?","a":"בונה ומריץ את צוות המכירות והפייפליין במשרה חלקית: גיוס, הכשרה וניהול נציגים, אחריות על ה-playbook, ה-CRM והתחזית, ואימון הצוות ליעד."},
    {"q":"VP מכירות במיקור חוץ או Fractional CRO?","a":"בחרו VP מכירות כדי להריץ את צוות המכירות והפייפליין. בחרו CRO כדי לקחת אחריות על כל ההכנסות כולל שיווק ו-Go-To-Market. אני עושה את שניהם ויכול להגדיל את ההיקף ככל שאתם גדלים."},
    {"q":"כמה עולה VP מכירות במיקור חוץ?","a":"בדרך כלל 6,000 עד 22,000 דולר בחודש לפי שעות, בחיוב חודשי בלי נעילה, הרבה מתחת למשכורת VP מלאה."}],
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
    {"q":"כמה זה עולה?","a":"בדרך כלל 6,000 עד 22,000 דולר בחודש לפי מעורבות, בחיוב חודשי בלי נעילה."}],
  "related":'ראו את שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות במיקור חוץ</a> או <a href="/he/contact">צרו קשר</a>.'},

 {"slug":"fractional-cro-roi",
  "title":"האם Fractional CRO שווה את זה? ה-ROI | טל פאפרין",
  "desc":"התיק העסקי לסמנכ״ל הכנסות במיקור חוץ: כמה זה עולה, מה זה מחזיר, ואיך זה מול גיוס מלא או לא לעשות כלום.",
  "h1":"האם Fractional CRO שווה את זה?","eyebrow":"מדריך",
  "lead":"סמנכ״ל הכנסות במיקור חוץ הוא לא עלות, הוא הימור על התוצאות. הנה התיק העסקי הכן: כמה אתם משלמים, מה זה מחזיר, ומה עולה לא לעשות כלום.",
  "sections":[
    {"h":"כמה אתם משלמים","p":["בערך 6,000 עד 22,000 דולר בחודש לפי כמה מהשבוע אתם צריכים, בחיוב חודשי בלי חוזה ארוך. בלי אקוויטי, בלי בונוס, בלי סיכון פיצויים, בלי דמי גיוס, בלי התברגות."]},
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
    {"q":"כמה עולה סמנכ״ל הכנסות במיקור חוץ?","a":"בדרך כלל 6,000 עד 22,000 דולר בחודש לפי מעורבות, בחיוב חודשי בלי נעילה, הרבה מתחת ל-CRO מלא."}],
  "related":'ראו <a href="/he/how-to-hire-a-fractional-cro">איך לשכור אחד</a> ואת שירות <a href="/he/services/fractional-cro">סמנכ״ל ההכנסות</a>, או <a href="/he/contact">צרו קשר</a>.'},
]



ABOUT_EN = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>About Tal Paperin | Fractional CRO and B2B Sales Leader</title>
  <meta name="description" content="Tal Paperin is a fractional CRO and B2B sales leader with 20-plus years building and scaling revenue engines across four continents. Operator, not advisor." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/about" />

  <meta property="og:type" content="profile" />
  <meta property="og:url" content="https://talpaperin.com/about" />
  <meta property="og:title" content="About Tal Paperin | Fractional CRO" />
  <meta property="og:description" content="Twenty years carrying the number on four continents. Operator, not advisor." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="About Tal Paperin | Fractional CRO" />
  <meta name="twitter:description" content="Twenty years carrying the number on four continents. Operator, not advisor." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

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
        <p class="eyebrow">About</p>
        <h1>About Tal Paperin</h1>
        <p class="lead">Operator, not advisor. I do the selling, the building, the management and the closing, and I answer for the number. Twenty years of it, on four continents.</p>

        <figure class="svc-photo portrait"><img src="/img/site/fractional-cro-portrait.jpg" alt="Tal Paperin, fractional CRO" width="800" height="1200" loading="lazy" /><figcaption>Senior revenue leadership, in the seat.</figcaption></figure>

        <h2>Twenty years carrying the number</h2>
        <p>I am a veteran international sales operator, fractional CRO and business strategist with more than 20 years building and scaling B2B sales engines. I started in the mud, hands-on, as an SDR, moved up to Account Executive and Team Leader, then served as VP of Global Sales and Business Development for multinationals and venture-backed startups. I build and run revenue functions from zero, across North America, Europe, APAC and the Middle East.</p>
        <p>Along the way I have managed international distributor networks, owned CRM architecture and the sales stack, and run market-entry strategies, including putting written-off products back onto retail shelves across Eastern Europe, EMEA and APAC. Different products, different buyers, the same discipline: own the number, do the work.</p>

        <h2>KSW Solutions</h2>
        <p><a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>, the firm I co-lead with Samantha Paperin, is an entire sales and marketing department for hire. Not advisors on the side, the whole function under one roof: the people and the senior leadership both. SDRs, AEs, BDs and marketing, plus the VP and CRO-level management that runs them, hired, trained, managed and accountable. A company can outsource the entire revenue engine to us instead of building it.</p>
        <p>We deliver field-ready operations, not slideware, across SaaS, IoT and hardware, medical devices, manufacturing and consumer brands.</p>

        <h2>TheDealMentor.AI</h2>
        <p>Early-stage founders and lean teams rarely have access to senior sales leadership. So I built <a href="https://thedealmentor.ai" target="_blank" rel="noopener">TheDealMentor.AI</a>, a virtual CRO companion that automates the playbooks and structures complex deal-handling without the overhead of an executive retainer.</p>

        <h2>Background and credentials</h2>
        <ul>
          <li>20-plus years in B2B sales, from SDR to VP of Global Sales and Business Development</li>
          <li>Built and rebuilt revenue for 30-plus B2B companies, from startups to multinationals</li>
          <li>Worked across four continents and more than forty countries</li>
          <li>Served in the Israeli Air Force</li>
          <li>Dual B.A. from the Hebrew University of Jerusalem, in International Relations and Chinese and East Asian Studies</li>
          <li>Speaks English, Hebrew, Russian and Chinese</li>
        </ul>

        <h2>The short personal version</h2>
        <p>Born in the USSR in 1981, in Israel since 1990. Married to Samantha, an American-born marketing executive, and a father of five. Off the clock I collect mechanical tool watches, read science fiction and post-apocalyptic novels, and keep a structured strength-training habit.</p>

        <p><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">View my full background on LinkedIn &rarr;</a></p>

        <h2 class="cases-recs-h">On the ground, on four continents</h2>
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
  <title>אודות טל פאפרין | סמנכ״ל מכירות ומוביל מכירות B2B</title>
  <meta name="description" content="טל פאפרין הוא סמנכ״ל מכירות במיקור חוץ ומוביל מכירות B2B עם מעל 20 שנה של בנייה והרחבת מנועי מכירות בארבע יבשות. איש ביצוע, לא יועץ." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="en" href="https://talpaperin.com/about" />
  <link rel="alternate" hreflang="he" href="https://talpaperin.com/he/about" />
  <link rel="alternate" hreflang="x-default" href="https://talpaperin.com/about" />

  <meta property="og:type" content="profile" />
  <meta property="og:url" content="https://talpaperin.com/he/about" />
  <meta property="og:title" content="אודות טל פאפרין | סמנכ״ל מכירות" />
  <meta property="og:description" content="עשרים שנה של אחריות על התוצאות, בארבע יבשות. איש ביצוע, לא יועץ." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="אודות טל פאפרין | סמנכ״ל מכירות" />
  <meta name="twitter:description" content="עשרים שנה של אחריות על התוצאות, בארבע יבשות. איש ביצוע, לא יועץ." />
  <meta name="twitter:image" content="https://talpaperin.com/og-image.jpg" />

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
        <p class="eyebrow">אודות</p>
        <h1>אודות טל פאפרין</h1>
        <p class="lead">איש ביצוע, לא יועץ. אני עושה את המכירה, הבנייה, הניהול והסגירה, ואני אחראי על התוצאות. עשרים שנה, בארבע יבשות.</p>

        <figure class="svc-photo portrait"><img src="/img/site/fractional-cro-portrait.jpg" alt="טל פאפרין" width="800" height="1200" loading="lazy" /><figcaption>הנהגת הכנסות בכירה, בכיסא.</figcaption></figure>

        <h2>עשרים שנה של אחריות על התוצאות</h2>
        <p>אני איש מכירות בינלאומי ותיק, סמנכ״ל מכירות במיקור חוץ ואסטרטג עסקי עם מעל 20 שנה של בנייה והרחבת מנועי מכירות B2B. התחלתי בבוץ, ידיים, כאיש SDR, עליתי ל-Account Executive וראש צוות, ובהמשך כיהנתי כ-VP of Global Sales and Business Development בתאגידים רב-לאומיים ובסטארטאפים מגובי הון סיכון. אני בונה ומנהל מחלקות הכנסה מאפס, בצפון אמריקה, אירופה, APAC והמזרח התיכון.</p>
        <p>בדרך ניהלתי רשתות מפיצים בינלאומיות, הייתי אחראי על ארכיטקטורת ה-CRM ומערך המכירות, והרצתי אסטרטגיות חדירה לשווקים, כולל החזרת מוצרים שנמחקו אל מדפי הקמעונאות במזרח אירופה, EMEA ו-APAC. מוצרים שונים, קונים שונים, אותה משמעת: לקחת אחריות על התוצאות, ולעשות את העבודה.</p>

        <h2>KSW Solutions</h2>
        <p><a href="https://ksw.solutions" target="_blank" rel="noopener">KSW Solutions</a>, החברה שאני מוביל יחד עם סמנתה פאפרין, היא מחלקת מכירות ושיווק שלמה להשכרה. לא יועצים מהצד, אלא כל הפונקציה תחת קורת גג אחת: גם האנשים וגם ההנהגה הבכירה. אנשי SDR, AE, BD ושיווק, יחד עם ההנהלה ברמת VP ו-CRO שמנהלת אותם, מגויסים, מוכשרים, מנוהלים ואחראים. חברה יכולה להוציא אלינו את כל מנוע ההכנסות למיקור חוץ במקום לבנות אותו.</p>
        <p>אנחנו מספקים מערכים מוכנים לשטח, לא מצגות, ב-SaaS, IoT וחומרה, מכשור רפואי, תעשייה ומותגי צריכה.</p>

        <h2>TheDealMentor.AI</h2>
        <p>למייסדים בשלבים מוקדמים ולצוותים רזים כמעט אף פעם אין גישה להנהגת מכירות בכירה. אז בניתי את <a href="https://thedealmentor.ai" target="_blank" rel="noopener">TheDealMentor.AI</a>, מלווה CRO וירטואלי שמכניס ל-playbooks אוטומציה ומבנה לטיפול בעסקאות מורכבות, בלי העלות של ריטיינר למנהל בכיר.</p>

        <h2>רקע והסמכות</h2>
        <ul>
          <li>מעל 20 שנה במכירות B2B, מ-SDR ועד VP of Global Sales and Business Development</li>
          <li>בניתי ובניתי מחדש הכנסות ל-30 ומעלה חברות B2B, מסטארטאפים ועד רב-לאומיות</li>
          <li>עבדתי בארבע יבשות ובמעל ארבעים מדינות</li>
          <li>שירתתי בחיל האוויר הישראלי</li>
          <li>תואר ראשון כפול מהאוניברסיטה העברית בירושלים, ביחסים בינלאומיים ובלימודי סין ומזרח אסיה</li>
          <li>דובר אנגלית, עברית, רוסית וסינית</li>
        </ul>

        <h2>הגרסה האישית הקצרה</h2>
        <p>נולדתי בברית המועצות ב-1981, בישראל מ-1990. נשוי לסמנתה, מנהלת שיווק ילידת ארה"ב, ואב לחמישה. בשעות הפנאי אני אוסף שעוני כלי מכניים, קורא מדע בדיוני ורומנים פוסט-אפוקליפטיים, ושומר על שגרת אימוני כוח מסודרת.</p>

        <p><a href="https://www.linkedin.com/in/talpaperin/" target="_blank" rel="noopener">לרקע המלא שלי בלינקדאין &larr;</a></p>

        <h2 class="cases-recs-h">בשטח, בארבע יבשות</h2>
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
                             gallery=render_gallery()))

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
                                gallery=render_gallery("טל פאפרין בשטח")))

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

    with open(os.path.join(ROOT, "about.html"), "w", encoding="utf-8") as f:
        f.write(ABOUT_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                gallery=render_gallery(), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "about.html"), "w", encoding="utf-8") as f:
        f.write(ABOUT_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                gallery=render_gallery("טל פאפרין בשטח"), cta=HE_CTA))

    # The case-studies marquee is a teaser: drop the longest outlier quotes so the
    # strip stays a sensible height. The full set lives on the recommendations page.
    cs_idx = [i for i, t in enumerate(TESTIMONIALS_EN) if len(t["q"]) <= 330]
    cs_en = [TESTIMONIALS_EN[i] for i in cs_idx]
    cs_he = [TESTIMONIALS_HE[i] for i in cs_idx]

    with open(os.path.join(ROOT, "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                  cases=render_cases(CASE_STUDIES, "Result"),
                                  testimonials=render_testimonials(cs_en),
                                  gallery=render_gallery(), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "case-studies.html"), "w", encoding="utf-8") as f:
        f.write(CS_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
                                  cases=render_cases(HE_CASES, "תוצאה"),
                                  testimonials=render_testimonials(cs_he, he=True),
                                  gallery=render_gallery("טל פאפרין בשטח"), cta=HE_CTA))

    with open(os.path.join(ROOT, "recommendations.html"), "w", encoding="utf-8") as f:
        f.write(REC_PAGE_EN.format(fonts=FONTS, analytics=ANALYTICS, nav=NAV, footer=FOOTER,
                                   logos=render_logo_wall(LOGOS),
                                   quotes=render_quote_grid(TESTIMONIALS_EN), cta=CTA_BOX))
    with open(os.path.join(ROOT, "he", "recommendations.html"), "w", encoding="utf-8") as f:
        f.write(REC_PAGE_HE.format(fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV, footer=HE_FOOTER,
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
        ld = ('{"@context":"https://schema.org","@type":"Article",'
              '"headline":"%s","description":"%s",'
              '"author":{"@type":"Person","name":"Tal Paperin","url":"%s/"},'
              '"publisher":{"@type":"Organization","name":"Tal Paperin"},'
              '"mainEntityOfPage":"%s"}'
              ) % (esc(g["h1"]), esc(g["desc"]), SITE, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
                 '{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}'
                 ) % (SITE, esc(g["h1"]), url)
        faq_html, faq_ld = render_faq(g.get("faqs"))
        page = GUIDE_PAGE.format(
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
        ld = ('{"@context":"https://schema.org","@type":"Article",'
              '"headline":"%s","description":"%s","inLanguage":"he",'
              '"author":{"@type":"Person","name":"טל פאפרין","url":"%s/he/"},'
              '"publisher":{"@type":"Organization","name":"Tal Paperin"},'
              '"mainEntityOfPage":"%s"}'
              ) % (esc(g["h1"]), esc(g["desc"]), SITE, url)
        crumb = ('{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
                 '{"@type":"ListItem","position":1,"name":"בית","item":"%s/he/"},'
                 '{"@type":"ListItem","position":2,"name":"%s","item":"%s"}]}'
                 ) % (SITE, esc(g["h1"]), url)
        faq_html, faq_ld = render_faq(g.get("faqs"), "שאלות נפוצות")
        page = HE_GUIDE_PAGE.format(
            title=esc(g["title"]), desc=esc(g["desc"]), url=url, site=SITE,
            h1=esc(g["h1"]), eyebrow=esc(g["eyebrow"]), lead=esc(g["lead"]),
            sections=render_guide_sections(g), faq=faq_html, faqld=faq_ld,
            related=g["related"], fonts=HE_FONTS, analytics=ANALYTICS, nav=HE_NAV,
            footer=HE_FOOTER, cta=HE_CTA, ld=ld, crumb=crumb, hreflang=hreflang)
        with open(os.path.join(ROOT, "he", g["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    print("Built %d EN + %d HE service pages, HE index, HE FAQ, %d guides + %d HE guides"
          % (len(SERVICES), len(HE_SERVICES), len(GUIDES), len(HE_GUIDES)))


if __name__ == "__main__":
    build()
