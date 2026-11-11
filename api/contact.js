// Vercel serverless function: the contact page form.
// Emails the message to Tal through his own Gmail (same sender and environment variables as
// api/calc-lead.js: GMAIL_USER, GMAIL_APP_PASSWORD, optional LEAD_TO). Reply-To is the visitor.
// If Gmail is not configured or refuses the send, the message is forwarded to the Formspree
// form the page used before, so nothing is lost.

import tls from "node:tls";
import { smtpSend, buildMessage } from "./calc-lead.js";

const FORMSPREE = "https://formspree.io/f/xykbgowb";
const line = (s, n) => String(s == null ? "" : s).replace(/[\r\n\t]+/g, " ").trim().slice(0, n);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }
  let body = {};
  try {
    body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
  } catch (_) { /* ignore */ }

  if (body._gotcha) { res.status(200).json({ ok: true }); return; } // honeypot: pretend it worked
  const name = line(body.name, 120);
  const email = line(body.email, 200);
  const page = line(body.page, 120);
  const message = String(body.message == null ? "" : body.message).replace(/\r\n?/g, "\n").trim().slice(0, 6000);
  if (!email || !/^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$/.test(email)) {
    res.status(400).json({ ok: false, error: "Invalid email" });
    return;
  }
  if (!message) {
    res.status(400).json({ ok: false, error: "Empty message" });
    return;
  }
  const subject = "Contact form: " + (name || email);
  const text = [
    "New message from the contact form on talpaperin.com",
    "",
    "Name: " + (name || "(not given)"),
    "Email: " + email,
    page ? "Page: " + page : null,
    "",
    message,
    "",
    "Reply to this email to answer them directly.",
  ].filter((x) => x !== null).join("\n");

  const user = process.env.GMAIL_USER;
  const pass = (process.env.GMAIL_APP_PASSWORD || "").replace(/\s+/g, "");
  if (user && pass) {
    const to = process.env.LEAD_TO || user;
    try {
      const raw = buildMessage({ from: user, to, replyTo: email, subject, text, pdf: null, filename: "" })
        .replace("talpaperin.com calculator", "talpaperin.com contact form");
      await smtpSend({
        connect: () => tls.connect({ host: "smtp.gmail.com", port: 465, servername: "smtp.gmail.com" }),
        user, pass, from: user, to, raw,
      });
      res.status(200).json({ ok: true, via: "gmail" });
      return;
    } catch (e) {
      console.error("contact gmail send failed:", e && e.message);
    }
  }

  try {
    const r = await fetch(FORMSPREE, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ name, email, message }),
    });
    if (r.ok) { res.status(200).json({ ok: true, via: "form" }); return; }
    res.status(502).json({ ok: false, error: "Delivery failed" });
  } catch (_) {
    res.status(500).json({ ok: false, error: "Server error" });
  }
}
