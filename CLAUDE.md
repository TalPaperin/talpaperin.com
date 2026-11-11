# talpaperin.com — working notes for Claude

Static site (HTML on Vercel) for Tal Paperin, Fractional CRO / B2B sales consultant.
Bilingual EN + HE (RTL). Serves as a backup to the KSW website.

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
- `site.js` and `site.css` are browser-cached for an hour, so they are loaded with a version query (`/site.js?v=11`, `/site.css?v=11`). BUMP the number in all three places whenever either file changes, or returning visitors keep the old behaviour.
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
- Sales cost calculator (Tal, 2026-11-11): a real form (name, work email, company). On submit the browser builds a PDF with `/vendor/html2pdf.bundle.min.js`, downloads it for the prospect, and posts the form plus the PDF to `/api/calc-lead`, which emails Tal with the PDF attached through his own Gmail (Vercel env `GMAIL_USER`, `GMAIL_APP_PASSWORD`, optional `LEAD_TO`). Without those variables the function forwards to the Formspree form, no attachment. The contact page form uses Formspree, which delivers to Tal's DealMentor mailbox.
- Contact page: no strip above the channel list. Blog mid-article box says "Let's Talk" and goes to the contact page.
- Each service page carries one matching recommendation (`SERVICE_PROOF` in `services/build.py`). The services index leads with Fractional CRO, Outsourced Sales Teams and Pay-Per-Meeting (`LEAD_SERVICES`).
- The trade-show photo gallery was removed from every page and must NOT come back. The homepage testimonials stay a scrolling strip, with "Show more" on cut-off quotes.
- Headline rule: page titles (h1) are mixed case, section headlines are capitals. The homepage hero stays in capitals as a display block.
- Not wanted, do not build or re-propose: marking GA4 key events, session recording, a Search Console review, a single "how it works" page, email signup outside the blog, a cutout photo, podcast embed changes.
- Cookie consent: Google Consent Mode defaults sit in the head snippet (analytics denied for EEA, UK, CH until accepted). `site.js` shows the banner only to visitors on a European time zone and stores the choice in localStorage `tp_consent`. `/terms` and `/he/terms` are generated from `TERMS_EN` / `TERMS_HE`. Neither page has had a lawyer's read.
- LinkedIn Insight Tag: the hook is in `site.js` (`LI_PARTNER_ID`, empty = off). It needs the PARTNER ID from Campaign Manager, not an ad account ID. When it is switched on, add LinkedIn to the privacy page.
- No trailing slashes: `vercel.json` has `trailingSlash: false`. Link to `/blog`, `/services`, `/he`, `/he/blog`, `/he/services`, never with a slash at the end.
- Fonts are self-hosted in `/fonts` and inlined through `FONT_FACES_EN` / `FONT_FACES_HE`. Do not add Google Fonts links back.
- Images: after adding a logo, testimonial photo or page photo run `python3 ops/optimize_images.py` (needs Pillow). It writes the WebP copy and `img/dims.json`; both builds then link the WebP and write width and height into the tag.

## Blog build extras (added 2026-11-11)
- Length: new posts are 900 words or more (Tal: "significantly longer"). Nothing under 700.
- `noindex: true` in front matter keeps a post readable and linked but out of search, the sitemap and llms.txt. It is on the posts under 200 words. Remove it only after the post is expanded.
- Listing pages: 20 posts per page (`/blog/page-N`), plus topic pages (`/blog/topic-<slug>`) built from the tags by the `TOPICS` map in `blog/build.py`. Add a new tag to that map or it lands in no topic.
- Social cards: `blog/og_cards.py` draws `/img/og/<slug>.jpg` (headline on the brand background) for every post that still has `image: /og-image.jpg`. Needs Pillow; without it the build keeps the default image. Commit the new card with the post.
- The frum city posts were merged on 2026-11-11 into four posts plus the `/frum-business-consultant` guide, with 301 redirects in `vercel.json`. Do not create per-city pages again.

## Structured data (JSON-LD)
One canonical entity `@graph` (ProfessionalService + Person + WebSite), referenced by `@id`, is injected sitewide via `graph_ld()` in `services/build.py`. Service-offering pages use `Service`; genuine explainers/comparisons stay `Article` (see `ARTICLE_GUIDES`). Keep new pages consistent with this.
