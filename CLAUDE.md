# talpaperin.com — working notes for Claude

Static site (HTML on Vercel) for Tal Paperin, Fractional CRO / B2B sales consultant.
Bilingual EN + HE (RTL). Serves as a backup to the KSW website.

## Voice / style (ALWAYS)
- **Never use em dashes (—) or en dashes (–).** Use commas, periods, or restructure. This applies to blog posts, page copy, emails, everything.
- Write in Tal's voice: direct, senior operator, honest, controversial when warranted, aimed at founders/CEOs.
- Reply to the user in English.

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
2. `blog/build.py` needs the `markdown` package: `pip install markdown` (NOT persistent across recycled containers — reinstall if `ModuleNotFoundError`).
3. The `.py` templates are the source of truth and must stay in sync with the live HTML. Edit templates, then rebuild; a rebuild of unchanged pages should produce a zero diff.
4. **All development goes straight to `main`** (per Tal). Recycled containers often start on the stale `claude/determined-brahmagupta-rkvaL` branch, which can be behind `main` — always `git fetch origin main` and reconcile to `origin/main` before building/committing so nothing is lost.

## Structured data (JSON-LD)
One canonical entity `@graph` (ProfessionalService + Person + WebSite), referenced by `@id`, is injected sitewide via `graph_ld()` in `services/build.py`. Service-offering pages use `Service`; genuine explainers/comparisons stay `Article` (see `ARTICLE_GUIDES`). Keep new pages consistent with this.
