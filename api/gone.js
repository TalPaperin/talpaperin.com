// Vercel serverless function: returns HTTP 410 Gone.
// Used for legacy WordPress paths (/wp-admin, /wp-content, /wp-includes and
// common probe files) that no longer exist after the move to a static site.
// A 410 tells search engines the content is permanently removed, which purges
// it from the index faster and cleaner than redirecting an old asset to the
// homepage (that reads as a soft 404). No imports, so there is no cold-start
// path that could ever return a 5xx.
export default function handler(req, res) {
  res.statusCode = 410;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=86400");
  res.end(
    '<!doctype html><meta charset="utf-8"><title>410 Gone</title>' +
    '<h1>410 Gone</h1><p>This page no longer exists. ' +
    'Visit <a href="https://talpaperin.com/">talpaperin.com</a>.</p>'
  );
}
