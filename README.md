# talpaperin.com

Single-page personal-brand site for Tal Paperin, fractional CRO and B2B sales
leader. Static HTML, no framework, no build step. Ships in English and Hebrew.

## Structure

```
index.html      English page (lang=en, LTR)
he/index.html   Hebrew page (lang=he, RTL), full translation of the same content
```

A flag button in the nav links between the two languages (Israeli flag on the
English page, US flag on the Hebrew page). The pages cross-reference each other
with `hreflang` alternate tags for SEO.

- Fonts: Fraunces + Inter Tight (English), Frank Ruhl Libre + Heebo (Hebrew),
  loaded from Google Fonts with `preconnect` hints.
- The only JavaScript is an `IntersectionObserver` that reveals sections on
  scroll. No `localStorage`, no `sessionStorage`, no tracking.
- All booking CTAs point to `https://calendly.com/ksw/15min`.
- SEO: title, meta description, canonical, Open Graph and Twitter tags, plus
  JSON-LD for `Person`, `ProfessionalService` (three priced offers), and
  `FAQPage` matching the visible FAQ.

## Deploy

Static hosting. Serve `index.html` at the root and `he/index.html` at `/he/`.
Any static host works (the site was scoped for a simple static deploy).

## To do before launch (must be supplied by Tal)

1. **Hero portrait and og:image, hosted on talpaperin.com.**
   Both pages reference:
   - `https://talpaperin.com/tal-paperin.jpg` (hero portrait, 4:5, around 600x750)
   - `https://talpaperin.com/og-image.jpg` (social share image, 1200x630)
   These files do not exist yet and must be uploaded to the site's own server.
   Do not reuse the KSW headshot URL, it is hotlink-protected and will not load
   cross-domain. Host the images locally here.

2. **Sign off on the paraphrased wording.**
   The testimonials and the two case studies were condensed and paraphrased from
   the originals. Review both the English and Hebrew copy for accuracy before the
   site goes live.

## Editing notes

- House style: no em dashes and no en dashes anywhere in the copy. Use commas,
  periods, or a plain hyphen.
- Keep exactly one `<h1>` per page.
- If you change a FAQ answer, update the matching `FAQPage` JSON-LD in the same
  file so the structured data stays in sync with what is visible.
