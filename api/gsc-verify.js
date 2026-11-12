// Google Search Console ownership check (HTML file method).
// vercel.json rewrites /google708bc123c251c1a6.html to this function, so the exact URL Google
// asks for answers 200. A static file would be redirected to the extensionless path because
// cleanUrls is on, and Google's check does not reliably follow that redirect.
// Do not remove: Search Console re-checks this URL from time to time.

export default function handler(req, res) {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=3600");
  res.statusCode = 200;
  res.end("google-site-verification: google708bc123c251c1a6.html");
}
