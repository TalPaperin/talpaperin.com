// Vercel serverless function: a visitor submitted the sales cost calculator form.
// Emails the submission to Tal with the visitor's PDF attached.
//
// Sending goes through Tal's own Gmail over SMTP. Set these in Vercel (Project, Settings,
// Environment Variables), then redeploy:
//   GMAIL_USER          the Gmail / Google Workspace address that sends, e.g. the work mailbox
//   GMAIL_APP_PASSWORD  a Google "app password" for that account (needs 2-Step Verification)
//   LEAD_TO             optional, where the lead goes. Defaults to GMAIL_USER.
// Until those exist, the submission is forwarded to the Formspree form the contact page uses,
// without the attachment, so no lead is lost.
//
// No dependencies on purpose: the site has no package.json, so SMTP is spoken directly.

import tls from "node:tls";

const FORMSPREE = "https://formspree.io/f/xykbgowb";
const MAX_PDF_BYTES = 3 * 1024 * 1024;

const clean = (s, n) => String(s == null ? "" : s).replace(/[\r\n\t]+/g, " ").trim().slice(0, n);
const b64 = (s) => Buffer.from(String(s), "utf8").toString("base64");
const encWord = (s) => (/^[\x20-\x7e]*$/.test(s) ? s : "=?UTF-8?B?" + b64(s) + "?=");
const wrap76 = (s) => s.replace(/(.{76})/g, "$1\r\n");

// Minimal SMTP client. `connect` returns a duplex socket (tls.connect in production).
export function smtpSend({ connect, user, pass, from, to, raw }) {
  return new Promise((resolve, reject) => {
    const sock = connect();
    let buf = "";
    let step = 0;
    let done = false;
    const steps = [
      { expect: 220, send: "EHLO talpaperin.com" },
      { expect: 250, send: "AUTH LOGIN" },
      { expect: 334, send: b64(user) },
      { expect: 334, send: b64(pass) },
      { expect: 235, send: "MAIL FROM:<" + from + ">" },
      { expect: 250, send: "RCPT TO:<" + to + ">" },
      { expect: 250, send: "DATA" },
      { expect: 354, send: raw.replace(/\r\n\./g, "\r\n..") + "\r\n." },
      { expect: 250, send: "QUIT" },
    ];
    const fail = (e) => { if (!done) { done = true; try { sock.destroy(); } catch (_) {} reject(e); } };
    sock.setTimeout(15000, () => fail(new Error("SMTP timeout")));
    sock.on("error", fail);
    sock.on("close", () => { if (!done) fail(new Error("SMTP closed early at step " + step)); });
    sock.on("data", (d) => {
      buf += d.toString("utf8");
      // A reply is complete when its last line is "NNN text" (a space after the code).
      for (;;) {
        const m = buf.match(/^(?:\d{3}-[^\r\n]*\r?\n)*(\d{3}) [^\r\n]*\r?\n/);
        if (!m) return;
        buf = buf.slice(m[0].length);
        const code = parseInt(m[1], 10);
        if (step >= steps.length) return;
        const s = steps[step];
        if (code !== s.expect) return fail(new Error("SMTP " + code + " at step " + step));
        step += 1;
        sock.write(s.send + "\r\n");
        if (step === steps.length) { done = true; sock.end(); return resolve(true); }
      }
    });
  });
}

export function buildMessage({ from, to, replyTo, subject, text, pdf, filename }) {
  const boundary = "tp_" + Date.now().toString(36) + Math.random().toString(36).slice(2);
  const head = [
    "From: " + encWord("talpaperin.com calculator") + " <" + from + ">",
    "To: <" + to + ">",
    replyTo ? "Reply-To: <" + replyTo + ">" : null,
    "Subject: " + encWord(subject),
    "Date: " + new Date().toUTCString().replace("GMT", "+0000"),
    "Message-ID: <" + boundary + "@talpaperin.com>",
    "MIME-Version: 1.0",
    'Content-Type: multipart/mixed; boundary="' + boundary + '"',
  ].filter(Boolean);
  const parts = [
    "--" + boundary,
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
    "",
    wrap76(b64(text)),
  ];
  if (pdf) {
    parts.push(
      "--" + boundary,
      'Content-Type: application/pdf; name="' + filename + '"',
      "Content-Transfer-Encoding: base64",
      'Content-Disposition: attachment; filename="' + filename + '"',
      "",
      wrap76(pdf.toString("base64"))
    );
  }
  parts.push("--" + boundary + "--", "");
  return head.join("\r\n") + "\r\n\r\n" + parts.join("\r\n");
}

export function readSubmission(body) {
  const name = clean(body.name, 120);
  const email = clean(body.email, 200);
  const company = clean(body.company, 160);
  const lang = body.lang === "he" ? "he" : "en";
  const total = clean(body.total, 40);
  const page = clean(body.page, 120);
  const rows = (v, n) => (Array.isArray(v) ? v : []).slice(0, n)
    .map((r) => [clean(r && r[0], 120), clean(r && r[1], 60)]).filter((r) => r[0]);
  const lines = rows(body.lines, 10);
  const inputs = rows(body.inputs, 30);
  let pdf = null;
  if (typeof body.pdf === "string" && body.pdf.length < MAX_PDF_BYTES * 1.4) {
    const raw = Buffer.from(body.pdf.replace(/^data:application\/pdf;[^,]*,/, ""), "base64");
    if (raw.length <= MAX_PDF_BYTES && raw.slice(0, 5).toString("latin1") === "%PDF-") pdf = raw;
  }
  const who = [name, company].filter(Boolean).join(", ") || email;
  const text = [
    "New sales cost calculator submission from talpaperin.com",
    "",
    "Name: " + (name || "(not given)"),
    "Email: " + email,
    "Company: " + (company || "(not given)"),
    "Language: " + (lang === "he" ? "Hebrew" : "English") + (page ? "  Page: " + page : ""),
    "",
    "Lost every year: " + total,
    ...lines.map((r) => r[0] + ": " + r[1]),
    "",
    "What they entered:",
    ...inputs.map((r) => r[0] + ": " + r[1]),
    "",
    pdf ? "The PDF they received is attached. Reply to this email to answer them directly."
        : "No PDF was attached to this submission. Reply to this email to answer them directly.",
  ].join("\n");
  return { name, email, company, total, text, pdf, who };
}

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
  const sub = readSubmission(body);
  if (!sub.email || !/^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$/.test(sub.email)) {
    res.status(400).json({ ok: false, error: "Invalid email" });
    return;
  }
  const subject = "Sales cost calculator: " + sub.who + (sub.total ? " (" + sub.total + " a year)" : "");

  const user = process.env.GMAIL_USER;
  const pass = (process.env.GMAIL_APP_PASSWORD || "").replace(/\s+/g, "");
  if (user && pass) {
    const to = process.env.LEAD_TO || user;
    try {
      const raw = buildMessage({
        from: user, to, replyTo: sub.email, subject, text: sub.text,
        pdf: sub.pdf, filename: "sales-cost-calculator.pdf",
      });
      await smtpSend({
        connect: () => tls.connect({ host: "smtp.gmail.com", port: 465, servername: "smtp.gmail.com" }),
        user, pass, from: user, to, raw,
      });
      res.status(200).json({ ok: true, via: "gmail", attached: !!sub.pdf });
      return;
    } catch (e) {
      console.error("calc-lead gmail send failed:", e && e.message);
      // fall through to the form service so the lead still arrives
    }
  }

  try {
    const r = await fetch(FORMSPREE, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ name: sub.name, email: sub.email, company: sub.company, _subject: subject, message: sub.text }),
    });
    if (r.ok) { res.status(200).json({ ok: true, via: "form", attached: false }); return; }
    res.status(502).json({ ok: false, error: "Delivery failed" });
  } catch (_) {
    res.status(500).json({ ok: false, error: "Server error" });
  }
}
