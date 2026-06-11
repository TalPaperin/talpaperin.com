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
SITE = "https://talpaperin.com"

# Service pages are defined in services/build.py; pull them in for sitemap + llms.
_svc_spec = importlib.util.spec_from_file_location(
    "svcbuild", os.path.join(ROOT, "services", "build.py"))
_svc_mod = importlib.util.module_from_spec(_svc_spec)
_svc_spec.loader.exec_module(_svc_mod)
SERVICES = _svc_mod.SERVICES

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
RFC822_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
RFC822_MONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]

ANALYTICS = ('<script src="https://analytics.ahrefs.com/analytics.js" '
             'data-key="yw4L2JvlOTPBX9ieFq8jZg" async></script>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Anton&'
         'family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />')

FLAG_SVG = ('<svg width="31" height="21" viewBox="0 0 22 15" aria-hidden="true">'
            '<rect width="22" height="15" fill="#fff"/>'
            '<rect width="22" height="1.7" y="2.3" fill="#0038b8"/>'
            '<rect width="22" height="1.7" y="11" fill="#0038b8"/>'
            '<path d="M11 4.5 L8.4 9 L13.6 9 Z" fill="none" stroke="#0038b8" stroke-width=".7"/>'
            '<path d="M11 10.5 L8.4 6 L13.6 6 Z" fill="none" stroke="#0038b8" stroke-width=".7"/></svg>')

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
        <a href="/blog/">Blog</a>
        <a href="/#work">Work With Me</a>
        <a href="/contact">Contact</a>
      </div>
      <div class="nav-right">
        <a class="flag-btn" href="/he/" hreflang="he" aria-label="Switch to Hebrew">''' + FLAG_SVG + '''</a>
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
        <h3>Your sales suck. You don't know why. I do.</h3>
        <p>A 15-minute call, no pitch. You will leave with at least one concrete thing to fix, whether or not we work together.</p>
        <a class="btn btn-solid" href="https://calendly.com/ksw/15min" target="_blank" rel="noopener">Book a 15-Minute Call</a>
      </div>'''

SUBSCRIBE = '''      <div class="subscribe-box">
        <h3>Get these in your inbox</h3>
        <p>No fluff. Sales, revenue and go-to-market, straight from the field.</p>
        <a class="btn btn-solid" href="https://talpaperin.beehiiv.com/subscribe" target="_blank" rel="noopener">Subscribe</a>
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
            meta[k.strip().lower()] = v.strip()
    return meta, parts[2].strip()


def parse_date(s):
    return datetime.date(*[int(x) for x in s.split("-")])


def human_date(d):
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def rfc822(d):
    wd = RFC822_DAYS[d.weekday()]
    return "%s, %02d %s %d 00:00:00 +0000" % (wd, d.day, RFC822_MONS[d.month - 1], d.year)


def reading_time(text):
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 200))


def esc(s):
    return html.escape(s, quote=True)


def load_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for fn in os.listdir(POSTS_DIR):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(POSTS_DIR, fn), encoding="utf-8") as f:
            raw = f.read()
        meta, body_md = parse_front_matter(raw)
        slug = meta.get("slug") or re.sub(r"\.md$", "", fn)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
        date = parse_date(meta["date"])
        updated = parse_date(meta["updated"]) if meta.get("updated") else date
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        md = markdown.Markdown(extensions=["extra", "sane_lists", "toc"])
        body_html = md.convert(body_md)
        posts.append({
            "slug": slug,
            "title": meta["title"],
            "description": meta["description"],
            "date": date,
            "updated": updated,
            "tags": tags,
            "image": meta.get("image", "/og-image.jpg"),
            "body_html": body_html,
            "read": reading_time(body_md),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def render_post(p):
    url = "%s/blog/%s" % (SITE, p["slug"])
    img = p["image"] if p["image"].startswith("http") else SITE + p["image"]
    tags_meta = "\n".join(
        '  <meta property="article:tag" content="%s" />' % esc(t) for t in p["tags"])
    keywords = ", ".join(p["tags"])
    tagrow = ""
    if p["tags"]:
        tagrow = '<div class="tagrow">' + "".join(
            '<span class="tag">%s</span>' % esc(t) for t in p["tags"]) + "</div>"

    ld = (
        '{"@context":"https://schema.org","@type":"BlogPosting",'
        '"mainEntityOfPage":{"@type":"WebPage","@id":"%s"},'
        '"headline":"%s","description":"%s","image":"%s",'
        '"datePublished":"%s","dateModified":"%s",'
        '"author":{"@type":"Person","name":"Tal Paperin","url":"%s/"},'
        '"publisher":{"@type":"Organization","name":"Tal Paperin",'
        '"logo":{"@type":"ImageObject","url":"%s/og-image.jpg"}},'
        '"keywords":"%s"}'
    ) % (url, esc(p["title"]), esc(p["description"]), img,
         p["date"].isoformat(), p["updated"].isoformat(), SITE, SITE, esc(keywords))

    crumb = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
        '{"@type":"ListItem","position":2,"name":"Blog","item":"%s/blog/"},'
        '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
    ) % (SITE, SITE, esc(p["title"]), url)

    return TEMPLATE_POST \
        .replace("{{TITLE}}", esc(p["title"])) \
        .replace("{{DESC}}", esc(p["description"])) \
        .replace("{{URL}}", url) \
        .replace("{{IMG}}", img) \
        .replace("{{KEYWORDS}}", esc(keywords)) \
        .replace("{{PUBLISHED}}", p["date"].isoformat()) \
        .replace("{{MODIFIED}}", p["updated"].isoformat()) \
        .replace("{{ARTICLE_TAGS}}", tags_meta) \
        .replace("{{LD}}", ld) \
        .replace("{{CRUMB}}", crumb) \
        .replace("{{HUMAN_DATE}}", human_date(p["date"])) \
        .replace("{{READ}}", str(p["read"])) \
        .replace("{{TAGROW}}", tagrow) \
        .replace("{{BODY}}", p["body_html"]) \
        .replace("{{NAV}}", NAV) \
        .replace("{{FOOTER}}", FOOTER) \
        .replace("{{SUBSCRIBE}}", SUBSCRIBE) \
        .replace("{{CTA}}", CTA_BOX) \
        .replace("{{FONTS}}", FONTS) \
        .replace("{{ANALYTICS}}", ANALYTICS)


def render_index(posts):
    cards = []
    for p in posts:
        url = "/blog/%s" % p["slug"]
        tagrow = ""
        if p["tags"]:
            tagrow = '<div class="tagrow">' + "".join(
                '<span class="tag">%s</span>' % esc(t) for t in p["tags"]) + "</div>"
        cards.append(
            '      <a class="post-card" href="%s">\n'
            '        <span class="meta">%s &middot; %s min read</span>\n'
            '        <h2>%s</h2>\n'
            '        <p>%s</p>\n'
            '        %s\n'
            '        <span class="more">Read the post &rarr;</span>\n'
            '      </a>' % (url, human_date(p["date"]), p["read"],
                           esc(p["title"]), esc(p["description"]), tagrow))
    listing = "\n".join(cards) if cards else \
        '      <p style="color:var(--soft)">First posts coming soon.</p>'

    ld = (
        '{"@context":"https://schema.org","@type":"Blog","@id":"%s/blog/",'
        '"name":"Tal Paperin Insights","url":"%s/blog/",'
        '"description":"Field notes on B2B sales, fractional CRO leadership, '
        'go-to-market and fixing broken revenue.",'
        '"publisher":{"@type":"Organization","name":"Tal Paperin"}}'
    ) % (SITE, SITE)

    return TEMPLATE_INDEX \
        .replace("{{LISTING}}", listing) \
        .replace("{{LD}}", ld) \
        .replace("{{NAV}}", NAV) \
        .replace("{{FOOTER}}", FOOTER) \
        .replace("{{FONTS}}", FONTS) \
        .replace("{{ANALYTICS}}", ANALYTICS)


def render_rss(posts):
    items = []
    for p in posts[:30]:
        url = "%s/blog/%s" % (SITE, p["slug"])
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
    return TEMPLATE_RSS \
        .replace("{{BUILD_DATE}}", build_date) \
        .replace("{{ITEMS}}", "\n".join(items))


def render_sitemap(posts):
    today = datetime.date.today().isoformat()
    urls = [
        ('%s/' % SITE, '1.0', today),
        ('%s/he/' % SITE, '0.9', today),
        ('%s/blog/' % SITE, '0.8', today),
        ('%s/services/' % SITE, '0.8', today),
        ('%s/contact' % SITE, '0.7', today),
    ]
    for s in SERVICES:
        urls.append(('%s/services/%s' % (SITE, s["slug"]), '0.7', today))
    urls.append(('%s/he/services/' % SITE, '0.7', today))
    for s in SERVICES:
        urls.append(('%s/he/services/%s' % (SITE, s["slug"]), '0.6', today))
    urls.append(('%s/he/challenges' % SITE, '0.6', today))
    urls.append(('%s/he/contact' % SITE, '0.6', today))
    for p in posts:
        urls.append(('%s/blog/%s' % (SITE, p["slug"]), '0.7', p["updated"].isoformat()))
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
        "> Fractional CRO and B2B sales consultant. I rebuild revenue functions and "
        "fix broken sales, fast. 30-plus B2B companies rebuilt, $20M ARR managed. Work "
        "with me three ways: fractional CRO (me, personally), fully outsourced sales via "
        "KSW Solutions, or TheDealMentor.AI for founders who want to run the motion themselves.",
        "",
        "## Key pages",
        "- [Tal Paperin, Fractional CRO (home)](%s/): services, what I fix, case studies, "
        "engagements and pricing, contact." % SITE,
        "- [Hebrew site](%s/he/): Hebrew version of the homepage." % SITE,
        "- [Blog](%s/blog/): field notes on B2B sales, fractional CRO leadership, "
        "go-to-market and fixing broken revenue." % SITE,
        "- [Contact](%s/contact): email, phone, WhatsApp, a 15-minute booking link and a contact form." % SITE,
        "",
        "## Services",
    ]
    for s in SERVICES:
        lines.append("- [%s](%s/services/%s): %s" % (s["h1"], SITE, s["slug"], s["desc"]))
    lines += ["", "## Hebrew (עברית)",
              "- [Services in Hebrew](%s/he/services/): Fractional CRO, outsourced sales, GTM, team building, distributors and market entry, in Hebrew." % SITE,
              "- [International B2B sales guide (Hebrew)](%s/he/challenges): the bold guide to selling B2B internationally from Israel." % SITE,
              "", "## Blog posts"]
    for p in posts:
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
  <title>{{TITLE}} | Tal Paperin</title>
  <meta name="description" content="{{DESC}}" />
  <meta name="keywords" content="{{KEYWORDS}}" />
  <meta name="author" content="Tal Paperin" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{{URL}}" />

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

  <main class="page">
    <div class="wrap">
      <article class="article">
        <p class="breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a></p>
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
        <a class="backlink" href="/blog/">&larr; All posts</a>
      </article>
    </div>
  </main>

{{FOOTER}}
</body>
</html>
'''

TEMPLATE_INDEX = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Insights on B2B Sales &amp; Fractional CRO Leadership | Tal Paperin</title>
  <meta name="description" content="Field notes from Tal Paperin on B2B sales, fractional CRO leadership, go-to-market strategy and fixing broken revenue functions." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://talpaperin.com/blog/" />

  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://talpaperin.com/blog/" />
  <meta property="og:title" content="Insights on B2B Sales &amp; Fractional CRO Leadership | Tal Paperin" />
  <meta property="og:description" content="Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue." />
  <meta property="og:image" content="https://talpaperin.com/og-image.jpg" />
  <meta property="og:site_name" content="Tal Paperin" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Insights on B2B Sales &amp; Fractional CRO Leadership | Tal Paperin" />
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

  <main class="page">
    <div class="wrap">
      <div class="blog-head">
        <div class="glowline"></div>
        <p class="eyebrow">Blog</p>
        <h1>Notes on selling, scaling and fixing revenue.</h1>
        <p>Practical takes on B2B sales, fractional CRO leadership and go-to-market, from 20-plus years carrying the number on four continents.</p>
      </div>
      <div class="post-list">
{{LISTING}}
      </div>
    </div>
  </main>

{{FOOTER}}
</body>
</html>
'''

TEMPLATE_RSS = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Tal Paperin Insights</title>
    <link>https://talpaperin.com/blog/</link>
    <atom:link href="https://talpaperin.com/blog/rss.xml" rel="self" type="application/rss+xml" />
    <description>Field notes on B2B sales, fractional CRO leadership, go-to-market and fixing broken revenue.</description>
    <language>en-us</language>
    <lastBuildDate>{{BUILD_DATE}}</lastBuildDate>
{{ITEMS}}
  </channel>
</rss>
'''


def main():
    posts = load_posts()
    for p in posts:
        out = os.path.join(BLOG_DIR, p["slug"] + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(render_post(p))
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(posts))
    with open(os.path.join(BLOG_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(render_rss(posts))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(render_sitemap(posts))
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(render_llms(posts))
    print("Built %d post(s): %s" % (len(posts), ", ".join(p["slug"] for p in posts)))


if __name__ == "__main__":
    main()
