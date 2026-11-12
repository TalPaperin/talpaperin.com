# talpaperin.com — working notes for Claude

Static site (HTML on Vercel) for Tal Paperin, Fractional CRO / B2B sales consultant.
Bilingual EN + HE (RTL). The brand on this site is Tal Paperin only (see "Identity" below).

## Voice / style (ALWAYS)
- **Never use em dashes (—) or en dashes (–).** Use commas, periods, or restructure. This applies to blog posts, page copy, emails, everything.
- Write in Tal's voice: direct, senior operator, honest, controversial when warranted, aimed at founders/CEOs.
- Reply to the user in English.

## Writing craft (ALWAYS, for blog posts and all copy)
Adopted from the LinkedIn writing field guide Tal reviewed. Goal: read like a senior operator wrote it, not an AI. Apply on top of the Voice/style rules above.

- **De-slop.** Cut the AI-tell vocabulary. Never use: delve, leverage, robust, seamless, elevate, unlock, unleash, harness, foster, navigate (figurative), landscape (figurative), realm, tapestry, testament, pivotal, crucial, vital, game-changer, cutting-edge, supercharge, turbocharge, "in today's fast-paced world," "let that sink in," "the bottom line is," "at the end of the day," "needle-mover," "low-hanging fruit," "move the needle," "deep dive," "circle back." Prefer plain, concrete words.
- **No AI punctuation.** Already banned: em/en dashes. Also: no curly/smart quotes (use straight `'` and `"`), and no ellipsis character — type three dots `...` when you need them.
- **Kill the AI sentence patterns:**
  - No "It's not just X, it's Y" (and its cousins "It isn't about X. It's about Y").
  - No rule-of-three padding ("faster, cheaper, better"). Use one sharp point or an honest list, not a rhythmic triple.
  - No one-word rhetorical questions as transitions ("The result?", "The problem?", "The kicker?").
  - No engagement bait ("Thoughts?", "Agree?", "Who else?"), no hashtag walls, no emoji openers.
- **Burstiness.** Vary sentence length on purpose. Mix short punchy lines with longer ones. If every sentence is the same length, rewrite.
- **Specificity over abstraction.** Use real numbers, real names, real timeframes, concrete detail. Abstract nouns ("solutions," "outcomes," "value") are a smell.
- **Never invent numbers, clients, or results.** Only use figures that are verified or that Tal supplied. If a number would strengthen the point but you don't have a real one, leave it out or ask, never fabricate. Do not fabricate backdated post histories.
- **Open with a real hook, not a windup.** First line earns the second. Useful angles: contrarian take, a number reveal, a mistake confession, before/after, a myth bust, a specific receipt/example, a warning, a time anchor. Pick one, lead with it, drop the preamble.
- One idea per post, one clear close. The template adds the CTAs, so end on the argument.

## Blog posts (ALWAYS create a Hebrew twin)
Every new English post gets a Hebrew translation, no exceptions.
- EN source: `blog/posts/YYYY-MM-DD-<slug>.md`
- HE twin:  `blog/posts-he/YYYY-MM-DD-<slug>.md` — **same slug** (build auto-pairs by slug and emits hreflang). Set `alt: <slug>` in the HE front-matter too.
- Front-matter fields: `title`, `seotitle` (SEO <title>, distinct from H1), `description` (<=160 chars), `date`, `tags` (comma-separated), `image` (default `/og-image.jpg`), optional `alt`.
- Body is Markdown. The template auto-inserts a mid-article CTA and a bottom Book-a-call CTA, so do not add your own.
- Add internal links where natural (to service/guide pages and related posts) to build SEO connective tissue. HE posts link to `/he/...` equivalents.
- A post with no HE twin emits no hreflang (safe), but the standing rule is: always make the twin.

## Build & deploy workflow
1. Run `services/build.py` first (services, guides, about, contact, pricing, case-studies, recommendations), THEN `blog/build.py` (posts, blog index, RSS, sitemap.xml, llms.txt).
2. `blog/build.py` needs the `markdown` package. Install it with `python3 -m pip install markdown`, NOT bare `pip install markdown`: on recycled containers `pip` can point at a different Python than `python3` (seen: `pip` on 3.13, `python3` on 3.11), so a bare `pip install` reports success while `python3` still raises `ModuleNotFoundError`. Not persistent across recycled containers, so reinstall when it is missing.
3. The `.py` templates are the source of truth and must stay in sync with the live HTML. Edit templates, then rebuild; a rebuild of unchanged pages should produce a zero diff.
4. **All development goes straight to `main`** (per Tal). Recycled containers often start on the stale `claude/determined-brahmagupta-rkvaL` branch, which can be behind `main` — always `git fetch origin main` and reconcile to `origin/main` before building/committing so nothing is lost.

## Shared conversion layer (added 2026-11-11)
- `/site.js` (loaded with `defer` on every page via the `ANALYTICS` constant) owns booking and tracking: EVERY `calendly.com` link opens the Calendly POPUP in place, never a new tab (Tal, 2026-11-11), with the widget loaded on demand, and fires GA4 `book_a_call`; a completed booking fires `calendly_booked` + `generate_lead`. WhatsApp, email, phone and newsletter clicks are tracked too. Do NOT add inline `openCal()` handlers or the Calendly widget tags to pages.
- `/site.css` (loaded via the `FONTS` / `HE_FONTS` constants) holds the shared components: footer grid, `.cta-strip`, `.proof-quote`, `.price-jump`, homepage `.next-steps` and `.home-faq`. It uses logical properties, so the same rules serve RTL.
- The header "Let's Talk" button and the homepage closing button go to the CONTACT PAGE (`/contact`, `/he/contact`). Never point them at Calendly: that bypasses the contact page (Tal, 2026-11-11). Calendly is reached from the booking buttons, as a popup.
- Ask level (Tal, 2026-11-11): the default button is "Let's Talk" to the contact page (header, footer, the `.cta-strip` on service, guide, about, recommendations and case-study pages). A direct booking button is used only where the visitor is already deciding: homepage hero, the homepage "what happens after you book" section, the pricing strip and quote builder, the calculator result, the contact page, and the bottom `cta-box`. Do not add more booking buttons without asking.
- WhatsApp float (Tal, 2026-11-11): the green bubble must be visible from the FIRST screen on every device, full size, never hidden on scroll or shrunk (Tal rejected hiding it on the mobile hero). `site.js` prefills the message with a READABLE page name, never a raw path, and nothing extra on the homepage (Tal rejected "(Page: /)"), and shows a dismissible label "Message Tal on WhatsApp" with a status line: it stays on desktop; on phones it shows once per visit and folds away after 8 seconds. Tal is on WhatsApp about 19 hours a day, so there is NO hours limit and no night state: "I'm on WhatsApp most of the day and reply personally." The only offline window is Friday 15:00 to Saturday 21:00 Israel time ("offline until Saturday night"). No reply-time number (none supplied). No live-chat widget, no pulsing.
- `site.js` and `site.css` are browser-cached for an hour, so they are loaded with a version query (`/site.js?v=14`, `/site.css?v=14`). BUMP the number in all three places whenever either file changes, or returning visitors keep the old behaviour.
- Homepage (Tal, 2026-11-11): two blocks were removed as useless and must NOT come back: the four-commitments bar under the hero ("No lock-in / Week 1 / In the seat / Straight talk") and the "Not sure you need a fractional CRO?" box.
- Footer (Tal, 2026-11-11): the name + tagline + "Let's Talk" block was removed from the footer on EVERY page. The footer is four link columns plus the copyright row, with NO button. Pages already end with calls to action; do not add another one to the footer.
- NAV, FOOTER and the head assets exist in THREE places that must stay in sync: `services/build.py`, `blog/build.py`, and the five hand-maintained pages (`index.html`, `he/index.html`, `404.html`, `sales-cost-calculator.html`, `he/sales-cost-calculator.html`).
- `/privacy` and `/he/privacy` are generated by `services/build.py` (`PRIVACY_EN` / `PRIVACY_HE`). Update them when a new tool that touches visitor data is added.
- Pricing: `/pricing` is the single source of truth for tiers and the performance share. Growth ($12,000) is the most chosen tier and the one to promote (Tal, 2026-11-11): it carries the "Most common" badge on `/pricing` and on the homepage. Never feature the $6,000 tier ahead of it.
- Fees are MONTHLY and are only ever shown per month (Tal, 2026-11-11). Never multiply a fee into a yearly total and never show a per-year comparison such as "$144,000 a year": the full-time CRO comparison block was removed from `/pricing` for that reason and must NOT come back.

## Decisions from the open-items review (Tal, 2026-11-11)
- Case studies carry NO figures: client numbers are under NDA. The page says so and invites the visitor to ask on a call. Never add a number to a case study.
- There is no paid diagnostic or other offer below Advisor ($2,000). Do not invent one.
- Homepage wording: "Three part-time levels, plus full-time."
- Performance share: one plain line inside each price card ("plus 3% of net new ARR"), never a star or footnote.
- Capacity line (pricing + homepage): two Growth clients at a time, or one full-time, three to four at Starter, or about ten Advisors. Do not turn it into "X places left".
- Sales cost calculator (Tal, 2026-11-11): a real form (name, work email, company). On submit the browser builds a PDF with `/vendor/html2pdf.bundle.min.js`, downloads it for the prospect, and posts the form plus the PDF to `/api/calc-lead`, which emails Tal with the PDF attached through his own Gmail (Vercel env `GMAIL_USER`, `GMAIL_APP_PASSWORD`, optional `LEAD_TO`). Without those variables the function forwards to the Formspree form, no attachment. The contact page form posts to `/api/contact`, which sends through the same Gmail route to the KSW mailbox (Tal, 2026-11-11), with Formspree only as the fallback.
- Contact page: no strip above the channel list. Blog mid-article box says "Let's Talk" and goes to the contact page.
- Each service page carries one matching recommendation (`SERVICE_PROOF` in `services/build.py`). The services index leads with Fractional CRO, Outsourced Sales Teams and Pay-Per-Meeting (`LEAD_SERVICES`).
- The trade-show photo gallery was removed from every page and must NOT come back. The homepage testimonials stay a scrolling strip, with "Show more" on cut-off quotes.
- Headline rule: page titles (h1) are mixed case, section headlines are capitals. The homepage hero stays in capitals as a display block.
- Not wanted, do not build or re-propose: marking GA4 key events, session recording, a Search Console review, a single "how it works" page, email signup outside the blog, a cutout photo, podcast embed changes.
- Cookie consent: Google Consent Mode defaults sit in the head snippet (analytics denied for EEA, UK, CH until accepted). `site.js` shows the banner only to visitors on a European time zone and stores the choice in localStorage `tp_consent`. `/terms` and `/he/terms` are generated from `TERMS_EN` / `TERMS_HE`. Neither page has had a lawyer's read.
- LinkedIn Insight Tag: the hook is in `site.js` (`LI_PARTNER_ID`, empty = off). It needs the PARTNER ID from Campaign Manager, not an ad account ID. When it is switched on, add LinkedIn to the privacy page.
- Google Search Console verification (Sam, 2026-11-12): `/google708bc123c251c1a6.html` is answered by `api/gsc-verify.js` through two rewrites in `vercel.json` (with and without `.html`, because `cleanUrls` redirects the `.html` address). Do NOT remove either: Search Console re-checks it and access is lost if it disappears.
- No trailing slashes: `vercel.json` has `trailingSlash: false`. Link to `/blog`, `/services`, `/he`, `/he/blog`, `/he/services`, never with a slash at the end.
- Fonts are self-hosted in `/fonts` and inlined through `FONT_FACES_EN` / `FONT_FACES_HE`. Do not add Google Fonts links back.
- Images: after adding a logo, testimonial photo or page photo run `python3 ops/optimize_images.py` (needs Pillow). It writes the WebP copy and `img/dims.json`; both builds then link the WebP and write width and height into the tag.

## Identity and the AI-visibility brief (Tal, 2026-11-12)
Tal handed over an implementation brief ("get Tal Paperin recommended by AI assistants and Google") and said to implement it. Standing results:
- **KSW Solutions is the legal company behind the Tal Paperin brand, and the two are ONE business** (Tal's correction, 2026-11-12, which replaces the brief's "remove KSW" rule). Search engines and AI assistants should read talpaperin.com and KSW Solutions as the same fractional CRO practice. Do NOT remove KSW again.
- Where KSW appears: the footer line on every page ("Tal Paperin operates through his company, KSW Solutions", linked to `https://ksw.solutions`, in all three footer copies, EN and HE), a first-person version on `/about` and `/he/about` ("I work through KSW Solutions..."), the About timeline ("2017, Founded KSW Solutions"; Tal confirmed 2017, the earlier 2019 was wrong), the ePropertyCare quote word for word, the "who is responsible" line on privacy and terms, `legalName` plus `https://ksw.solutions` in `sameAs` on the `#business` node (`LEGAL_NAME` / `LEGAL_URL` in `services/build.py`), and the "Legal entity" block in llms.txt.
- Tal FOUNDED KSW Solutions himself (Tal, 2026-11-12: "No need to say co founded. I founded it myself. Sam works with me and for me."). Never write "co-founded", "co-lead" or "the firm I co-lead", and never present Sam as a co-founder or partner.
- Tal Paperin is a PERSON, KSW Solutions is his company. Never write that Tal "is the practice of" KSW or that the two "are the same practice" (Tal, 2026-11-12: "Tal Paperin is me. I'm a person."). Say he operates or works through it.
- `LEGAL_NAME` is "KSW Solutions": Tal, 2026-11-12, "KSW Solutions is the legal name of my company in Israel." Do not add "Ltd." or another suffix unless he supplies it.
- Service, pricing and guide copy still describes the work as Tal's and his teams' ("via KSW" and "Run by KSW Solutions" were not put back, they read as a second company). Page titles end in "| Tal Paperin". Ask before changing either.
- The contact strings `tal@ksw.solutions` and `calendly.com/ksw/15min` stay (footer, `/contact`, schema, llms.txt).
- Never edit a client's words. The `"hide": True` flag on a testimonial keeps it in the list but off every page; nothing is hidden today.
- Schema: `graph_ld()` is emitted once per page, blog pages included. Person `jobTitle` is "Fractional CRO", `worksFor` points at `#business`, `sameAs` is the `SAME_AS` list (LinkedIn, about.me, MentorCruise, Clutch). Articles and posts reference `author` / `publisher` by `@id` only. No Review or AggregateRating, ever.
- Facts to use everywhere: fractional CRO (also fractional VP of Sales), 30-plus B2B companies rebuilt, $20M ARR managed last year, five continents, 40-plus countries, 300-plus founders, **1,000+ salespeople trained** (Tal confirmed; never 2,000), $2,000 to $22,000 a month plus the performance share.
- First paragraph rule: the first `<p>` inside `<main>` is the direct answer. Breadcrumbs are `<nav class="breadcrumb">` and eyebrows are `<div class="eyebrow">`, never `<p>`. Keep it that way in new templates.
- Titles are under 60 characters and meta descriptions under 155. The brief wrote titles with a dash; this site uses `|` (no en dashes).
- Author bio: `BIO_EN` / `BIO_HE` in `services/build.py` sit above the footer on every page except privacy, terms, 404 and the calculator (Tal asked for home, about, contact and /he on 2026-11-12). The two homepages carry a hand-synced copy of the block. Its links are text links to About and the contact page, NOT a booking button (the ask-level rule above still wins over the brief's "Book a 15-minute call").
- Hub pages carry a BreadcrumbList through `hub_crumb()`. Guides are Home > Guides > page. `/he` has a hand-written one. The homepage links to the founder-led, VP-hire and outsourced-vs-in-house guides through the `.home-reads` line under "What I Fix".
- Buyer-question pages: `/fractional-vp-sales-vs-full-time-vp-sales` and `/outsourced-sales-team-vs-in-house` are new (EN + HE twins in `HE_GUIDES`), `/fractional-cro-for-saas` is the canonical B2B SaaS page. Convenience slugs 301 in `vercel.json`: `/fractional-cro`, `/fractional-cro-for-b2b-saas`, `/founder-led-sales-stuck`, `/why-vp-sales-hires-fail`, `/us-market-entry-b2b-sales`. Do not create duplicate pages at those slugs.
- Case studies: every entry in `CASE_STUDIES` gets its own page at `/case-studies/<slug>` (and `/he/case-studies/<slug>`), built from the same data plus `CASE_PAGES_EN`. Still NO figures. There is deliberately no page for The Point Company: the only source is Steve Burton's recommendation, which does not describe an engagement, and a case study would mean inventing one.
- The outsourced-sales service keeps the H1 "Outsourced Sales Teams" (Tal pitches the teams), not the brief's "Outsourced sales leadership". Never write "not an agency" about Tal, on the site either.
- `http://` already answers 308 to HTTPS on Vercel (checked 2026-11-12). The 500 in the brief was a crawl artifact.

## Who the site is for (Tal, 2026-11-12, conversion review)
The site's main job is to turn ONE visitor into a conversation: a founder or CEO of a US-based B2B SaaS company (5 to 50 people) that is struggling with sales. Keep Tal's voice: first person, short, blunt, anti-consultant.
- English homepage leads with SaaS: title "Fractional CRO for B2B SaaS and Tech", the hero client line names KanduAI before PepsiCo, Mars and Teva, and the case cards run KanduAI, Synergix, LoneStar, BT9 (phones show the first two). Palram and the distributor pain card are off the homepage but still on `/case-studies` and `/services`. Do not put non-SaaS proof back above the SaaS stories.
- "What I Fix" opens with the founder-led card ("Every deal still needs you on the call"), then VP gone, reps who cannot close, product will not sell, no team, sell globally.
- The Hebrew homepage was deliberately NOT refocused: its visitor is an Israeli company going abroad, so market entry and distributors stay prominent there.
- Phone hero: the photo is 30vh (was 42vh) so "Book a Call" is visible without scrolling on a 390x844 screen. Do not make the photo taller again without checking the button still shows. The hero image `sizes` starts with `(max-width:680px) 70vw` so phones load the 960 file.
- SaaS result: there is still NO published SaaS outcome. The slot exists: `"outcome"` on `CASE_PAGES_EN["kanduai"]` (empty) and the `<!-- result-slot -->` marker in the KanduAI card on `index.html`. Fill both only with a sentence Tal supplies and the client approved. Never invent one.
- Contact page: three fields only (name, work email, "Where is revenue stuck?"), the reply promise is "within one business day" (Tal confirmed it on 2026-11-12), the lead says what the visitor gets, WhatsApp is the second channel and is offered again under the form, and on phones the photo sits BELOW the form. Still no strip above the channel list.
- Tal said to ignore the other three asks from that review (a published SaaS result, putting Palram or the distributor card back on the homepage, a US phone number). Do not raise them again unless he does.
- Measured 2026-11-12 on a throttled phone profile: homepage LCP about 3.1s (the hero image), contact 1.5s, no layout shift. The largest file on every page is Google's own analytics script.

## Site audit fixes (Tal, 2026-11-13)
Tal pasted a six-area audit (overall 86 of 100, no blocking issues). Acted on:
- Homepage testimonials are STATIC HTML inside `#quotetrack` on `index.html` and `he/index.html` (36 quotes each), so crawlers that do not run JavaScript can read them. The script only clones them for the loop and adds "Show more". To add, remove or edit a quote, edit the HTML, there is no JS array any more. The logo strip is still built by JS.
- The Google tag library loads after the page `load` event or on the first interaction, through the small loader inside the `ANALYTICS` snippet (three places). The consent defaults and `gtag('config')` still run inline first. Do not put the `async` script tag back in the head.
- The contact photo is no longer lazy-loaded and is preloaded on desktop only (`media="(min-width:901px)"`), because it is the largest element there.
Not acted on: outcome numbers on case studies (NDA, Tal said to drop it), a US contact number (dropped), thin industry pages, Article dates and Offer schema, and the 13 smaller items the audit counted but did not list.

## Blog build extras (added 2026-11-11)
- Length: new posts are 900 words or more (Tal: "significantly longer"). Nothing under 700.
- `noindex: true` in front matter keeps a post readable and linked but out of search, the sitemap and llms.txt. It is on the posts under 200 words. Remove it only after the post is expanded.
- Listing pages: 20 posts per page (`/blog/page-N`), plus topic pages (`/blog/topic-<slug>`) built from the tags by the `TOPICS` map in `blog/build.py`. Add a new tag to that map or it lands in no topic.
- Social cards: `blog/og_cards.py` draws `/img/og/<slug>.jpg` (headline on the brand background) for every post that still has `image: /og-image.jpg`. Needs Pillow; without it the build keeps the default image. Commit the new card with the post.
- The frum city posts were merged on 2026-11-11 into four posts plus the `/frum-business-consultant` guide, with 301 redirects in `vercel.json`. Do not create per-city pages again.

## Structured data (JSON-LD)
One canonical entity `@graph` (ProfessionalService + Person + WebSite), referenced by `@id`, is injected sitewide via `graph_ld()` in `services/build.py`. Service-offering pages use `Service`; genuine explainers/comparisons stay `Article` (see `ARTICLE_GUIDES`). Keep new pages consistent with this.
