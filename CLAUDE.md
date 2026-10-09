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

## Structured data (JSON-LD)
One canonical entity `@graph` (ProfessionalService + Person + WebSite), referenced by `@id`, is injected sitewide via `graph_ld()` in `services/build.py`. Service-offering pages use `Service`; genuine explainers/comparisons stay `Article` (see `ARTICLE_GUIDES`). Keep new pages consistent with this.
