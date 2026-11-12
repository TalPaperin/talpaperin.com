// Google Search Console ownership check (HTML file method).
// cleanUrls is on, so Vercel answers /google708bc123c251c1a6.html with a 308 to the same path
// without .html, on the same domain. vercel.json rewrites that path (and the .html one) to this
// function, which returns the exact text Google expects.
// Do not remove: Search Console re-checks this URL from time to time.

export default function handler(req, res) {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=3600");
  res.statusCode = 200;
  res.end("google-site-verification: google708bc123c251c1a6.html");
}
