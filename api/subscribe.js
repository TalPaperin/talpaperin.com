// Vercel serverless function: subscribe an email to the beehiiv list.
// Reads the secret API key from the environment (set BEEHIIV_API_KEY in Vercel).
// The publication ID is public (used in embeds), so it is fine in code.

const PUBLICATION_ID = process.env.BEEHIIV_PUBLICATION_ID || "pub_a72f0c0a-48d5-4f9b-834e-6c7ca597ede4";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  let email = "";
  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    email = (body.email || "").trim();
  } catch (_) { /* ignore */ }

  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    res.status(400).json({ ok: false, error: "Invalid email" });
    return;
  }

  const key = process.env.BEEHIIV_API_KEY;
  if (!key) {
    res.status(500).json({ ok: false, error: "Not configured" });
    return;
  }

  try {
    const r = await fetch(
      `https://api.beehiiv.com/v2/publications/${PUBLICATION_ID}/subscriptions`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${key}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          reactivate_existing: true,
          send_welcome_email: true,
          utm_source: "talpaperin.com",
        }),
      }
    );
    if (r.ok) {
      res.status(200).json({ ok: true });
    } else {
      res.status(502).json({ ok: false, error: "Subscription service error" });
    }
  } catch (_) {
    res.status(500).json({ ok: false, error: "Server error" });
  }
}
