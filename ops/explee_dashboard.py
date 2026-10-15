#!/usr/bin/env python3
# Self-contained Explee reply dashboard: pulls live data and renders the HTML.
# Shows what matters: every real human reply (out-of-office filtered), plus
# four headline numbers. Pulls via curl (works through the session proxy).
#
# Usage: python3 explee_dashboard.py <out.html> [--key KEY]
#   Key: --key arg, else env EXPLEE_API_KEY_TALPAPERIN.
import sys, os, re, json, html, subprocess, datetime

BASE = "https://api.explee.com"
PROJECT = 49501

def get_key():
    if "--key" in sys.argv:
        return sys.argv[sys.argv.index("--key") + 1]
    return os.environ.get("EXPLEE_API_KEY_TALPAPERIN", "")

def api(path, key):
    r = subprocess.run(["curl", "-sS", "--max-time", "30", "-H", f"X-API-Key: {key}", BASE + path],
                       capture_output=True, text=True, timeout=40)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}

QUOTE = re.compile(
    r"(?:\r?\n)+\s*(?:From:\s|On .*wrote:|-{3,}\s*Original|_{5,}|בתאריך .*?(?:כתב|מאת)|Sent from my|מאת:\s|ביום .*?בשעה)",
    re.I | re.S)
OOO = re.compile(r"out of office|will be away|away from|on vacation|annual leave|parental leave|"
                 r"be back|upon my return|auto[- ]?reply|מחוץ למשרד|אהיה מחוץ|בחופש", re.I)
POS = re.compile(r"\b(sure|yes|yeah|sounds good|interested|please send|go ahead|let'?s|happy to)\b", re.I)
Q = re.compile(r"\?|not sure|didn'?t understand|what (do|exactly)|לא בטוח|לא הבנתי|מה בדיוק")

SIG = re.compile(r"^\s*(--\s*$|best\b|regards\b|thanks\b|thank you\b|sincerely\b|cheers\b|"
                 r"warm regards|kind regards|sent from|get outlook|בברכה|כל טוב|תודה|"
                 r"your audience|בכבוד)", re.I)

def clean(body):
    body = (body or "").replace("\r", "\n")
    m = QUOTE.search(body)
    if m:
        body = body[:m.start()]
    # drop the signature block (everything from the first sign-off line)
    kept = []
    for ln in body.split("\n"):
        if SIG.match(ln):
            break
        kept.append(ln)
    body = "\n".join(kept)
    # strip links, emails, phone numbers, markdown bold
    body = re.sub(r"https?://\S+", "", body)
    body = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w{2,}\b", "", body)
    body = re.sub(r"[\+\(]?\d[\d\-\s\(\)]{6,}\d", "", body)
    body = body.replace("*", "")
    return re.sub(r"\s+", " ", body).strip()

def classify(text):
    if POS.search(text) and not Q.search(text):
        return ("Interested", "good")
    if Q.search(text):
        return ("Question", "warn")
    return ("Replied", "neutral")

def build(key):
    bal = api("/public/api/v1/billing/balance", key).get("remain", 0) / 100.0
    budget = api(f"/public/api/v1/autogtm/projects/{PROJECT}/budget", key).get("daily_budget_usd", 0)
    ana = api(f"/public/api/v1/autogtm/projects/{PROJECT}/analytics", key)
    reached = ana.get("total_emails_sent", 0)
    replies = []
    for c in ana.get("campaigns", []):
        if c.get("total_replies", 0) <= 0:
            continue
        inbox = api(f"/public/api/v1/autogtm/campaigns/{c['campaign_id']}/inbox", key)
        for ct in inbox.get("contacts", []):
            if ct.get("reply_count", 0) <= 0:
                continue
            th = api(f"/public/api/v1/autogtm/campaigns/{c['campaign_id']}/inbox/{ct['person_id']}", key)
            L = th.get("lead", {})
            rmsgs = [m for m in th.get("messages", []) if m.get("type") == "reply"]
            if not rmsgs:
                continue
            raw = rmsgs[-1].get("body_text", "")
            if OOO.search(raw or ""):
                continue
            txt = clean(raw)
            if not txt:
                continue
            replies.append({
                "name": L.get("name") or ct.get("name") or "Unknown",
                "title": L.get("job_title") or "",
                "company": L.get("company_name") or "",
                "email": L.get("email") or ct.get("email") or "",
                "linkedin": L.get("linkedin_url") or "",
                "msg": txt[:400],
                "ts": rmsgs[-1].get("ts", ""),
            })
    replies.sort(key=lambda r: r["ts"], reverse=True)
    return bal, budget, reached, replies

def esc(s): return html.escape(str(s if s is not None else ""))

def render(bal, budget, reached, replies, out):
    n = len(replies)
    runway = (bal / budget) if budget else 0
    rate = (n / reached * 100) if reached else 0.0

    def metric(val, lbl, tone=""):
        return f'<div class="m {tone}"><div class="m-val">{val}</div><div class="m-lbl">{lbl}</div></div>'
    metrics = "".join([
        metric(f"{n}", "Real replies", "hero"),
        metric(f"{reached:,}", "People reached"),
        metric(f"{rate:.1f}%", "Reply rate"),
        metric(f"{runway:.0f}d", f"Budget left · ${bal:,.0f}", "money"),
    ])

    if replies:
        cards = ""
        for r in replies:
            label, tone = classify(r["msg"])
            meta = " · ".join([x for x in [esc(r["title"]), esc(r["company"])] if x])
            links = ""
            if r["email"]:
                links += f'<span class="mono">{esc(r["email"])}</span>'
            if r["linkedin"]:
                links += f'<a href="{esc(r["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>'
            cards += f"""
      <article class="r">
        <div class="r-top">
          <h3>{esc(r['name'])}</h3>
          <span class="chip {tone}">{label}</span>
        </div>
        <div class="r-meta">{meta}</div>
        <p class="r-msg">{esc(r['msg'])}</p>
        <div class="r-links">{links}</div>
      </article>"""
        body = f'<div class="list">{cards}</div>'
    else:
        body = """
      <div class="empty">
        <div class="dot"></div>
        <h3>No replies yet</h3>
        <p>Emails are going out now. The moment someone replies, they appear here and your phone buzzes.</p>
      </div>"""

    updated = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b, %H:%M UTC")
    doc = f"""<meta name="claude:viewport-fit-sides" content="cover">
<title>Tal Paperin Replies</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
  /* Reply board: four headline numbers, then every real reply as a card. */
  :root {{
    --bg:#f5f6f8; --panel:#ffffff; --ink:#15181d; --muted:#596173; --faint:#9aa1ae;
    --line:#e6e9ee; --accent:#2f6bff; --good:#17935a; --warn:#b5730a; --neutral:#7b8394;
    --f:'IBM Plex Sans',system-ui,sans-serif; --mono:'IBM Plex Mono',ui-monospace,monospace;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --bg:#0c0e12; --panel:#161a21; --ink:#eceef2; --muted:#98a1b2; --faint:#646d7d;
    --line:#242a34; --accent:#5e93ff; --good:#38c47f; --warn:#e0a53c; --neutral:#8691a3; color-scheme:dark;
  }} }}
  :root[data-theme="dark"] {{
    --bg:#0c0e12; --panel:#161a21; --ink:#eceef2; --muted:#98a1b2; --faint:#646d7d;
    --line:#242a34; --accent:#5e93ff; --good:#38c47f; --warn:#e0a53c; --neutral:#8691a3; color-scheme:dark;
  }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); font-family:var(--f); line-height:1.5; }}
  .wrap {{ max-width:680px; margin:0 auto;
           padding-left:max(18px,env(safe-area-inset-left,0px));
           padding-right:max(18px,env(safe-area-inset-right,0px)); padding-block:34px 56px; }}
  .eyebrow {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.14em; color:var(--faint); font-weight:600; }}
  h1 {{ font-size:1.9rem; font-weight:700; margin:5px 0 26px; letter-spacing:-.02em; }}
  .bar {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:34px; }}
  .m {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:15px 14px; min-width:0; }}
  .m-val {{ font-family:var(--mono); font-weight:600; font-size:1.55rem; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
  .m-lbl {{ font-size:.73rem; color:var(--muted); margin-top:4px; }}
  .m.hero {{ border-color:color-mix(in srgb,var(--accent) 45%,var(--line)); }}
  .m.hero .m-val {{ color:var(--accent); }}
  .m.money .m-val {{ color:var(--good); font-size:1.2rem; }}
  @media (max-width:540px) {{ .bar {{ grid-template-columns:repeat(2,1fr); }} }}

  .sec {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin:0 0 14px; font-weight:600; }}
  .list {{ display:flex; flex-direction:column; gap:12px; }}
  .r {{ background:var(--panel); border:1px solid var(--line); border-radius:15px; padding:17px 19px; min-width:0; }}
  .r-top {{ display:flex; align-items:center; gap:10px; }}
  .r h3 {{ font-size:1.12rem; font-weight:600; margin:0; flex:1; min-width:0; }}
  .r-meta {{ color:var(--muted); font-size:.87rem; margin-top:2px; }}
  .r-msg {{ margin:11px 0 0; border-left:3px solid var(--accent); padding-left:13px; font-size:.95rem; }}
  .r-links {{ margin-top:13px; display:flex; flex-wrap:wrap; gap:16px; font-size:.84rem; align-items:center; }}
  .r-links a {{ color:var(--accent); text-decoration:none; }}
  .mono {{ font-family:var(--mono); color:var(--faint); font-size:.8rem; }}
  .chip {{ font-size:.68rem; font-weight:600; text-transform:uppercase; letter-spacing:.04em;
           padding:3px 9px; border-radius:999px; white-space:nowrap; }}
  .chip.good {{ background:color-mix(in srgb,var(--good) 16%,transparent); color:var(--good); }}
  .chip.warn {{ background:color-mix(in srgb,var(--warn) 16%,transparent); color:var(--warn); }}
  .chip.neutral {{ background:color-mix(in srgb,var(--neutral) 16%,transparent); color:var(--neutral); }}

  .empty {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:46px 24px; text-align:center; }}
  .dot {{ width:11px; height:11px; border-radius:50%; background:var(--accent); margin:0 auto 16px;
          box-shadow:0 0 0 6px color-mix(in srgb,var(--accent) 16%,transparent); }}
  .empty h3 {{ font-size:1.25rem; margin:0 0 8px; }}
  .empty p {{ color:var(--muted); margin:0 auto; max-width:40ch; font-size:.93rem; }}
  .foot {{ color:var(--faint); font-size:.78rem; margin-top:26px; }}
</style>

<div class="wrap">
  <div class="eyebrow">Live outreach</div>
  <h1>Replies</h1>
  <div class="bar">{metrics}</div>
  <h2 class="sec">Who replied</h2>
  {body}
  <p class="foot">Updated {updated}, refreshes hourly. Out-of-office auto-replies are filtered out. Auto-reply is off, so each of these reaches you with a ready response. Top up before the budget runs down.</p>
</div>
"""
    open(out, "w").write(doc)
    return n

if __name__ == "__main__":
    out = sys.argv[1]
    key = get_key()
    if not key:
        sys.stderr.write("No API key (EXPLEE_API_KEY_TALPAPERIN or --key)\n"); sys.exit(2)
    bal, budget, reached, replies = build(key)
    n = render(bal, budget, reached, replies, out)
    print(f"wrote {out}: {n} real replies, reached {reached}, balance ${bal:.2f}")
