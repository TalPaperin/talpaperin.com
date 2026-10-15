#!/usr/bin/env python3
# Generates Tal's lead-focused outreach dashboard HTML from an Explee snapshot JSON.
# Shows only what matters: the leads, and whether the spend is working.
# Usage: python3 explee_dashboard.py <snapshot.json> <out.html>
import sys, json, html, datetime

snap = json.load(open(sys.argv[1]))
out = sys.argv[2]

bal = snap["balance"]["remain"] / 100.0
budget = snap["budget"]["daily_budget_usd"]
a = snap["analytics"]
leads = snap.get("hot_leads", {}).get("leads", [])

reached = a["total_emails_sent"]
replies = a["total_replies"]
hot = a["total_hot_leads"]
spend = a["total_spend_usd"]
runway = (bal / budget) if budget else 0
rate = (replies / reached * 100) if reached else 0.0

def esc(s): return html.escape(str(s if s is not None else ""))

def metric(value, label, tone=""):
    return f'<div class="m {tone}"><div class="m-val">{value}</div><div class="m-lbl">{label}</div></div>'

metrics = "".join([
    metric(f"{hot:,}", "Hot leads", "hero"),
    metric(f"{replies:,}", "Replies"),
    metric(f"{reached:,}", "People reached"),
    metric(f"{runway:.0f} days", f"Budget left (${bal:,.0f})", "money"),
])

if leads:
    cards = ""
    for L in leads:
        why = (L.get("why_hot") or "").replace("\r", " ").replace("\n", " ").strip()
        why = why[:220] + ("..." if len(why) > 220 else "")
        meta = " · ".join([x for x in [esc(L.get("job_title")), esc(L.get("company_name"))] if x])
        email = esc(L.get("email") or "")
        li = L.get("linkedin_url")
        links = ""
        if email: links += f'<span class="mono">{email}</span>'
        if li: links += f'<a href="{esc(li)}" target="_blank" rel="noopener">LinkedIn</a>'
        cards += f"""
      <article class="lead">
        <div class="lead-top">
          <h3>{esc(L.get('name') or 'Unknown')}</h3>
          <div class="lead-meta">{meta}</div>
        </div>
        <p class="lead-msg">{esc(why)}</p>
        <div class="lead-links">{links}</div>
      </article>"""
    body = f'<div class="leads">{cards}</div>'
else:
    body = """
      <div class="empty">
        <div class="empty-dot"></div>
        <h3>No leads yet</h3>
        <p>Emails are going out now. The moment someone replies with real interest, they land here, and your phone buzzes with a ready response.</p>
      </div>"""

updated = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b, %H:%M UTC")

doc = f"""<meta name="claude:viewport-fit-sides" content="cover">
<title>Tal Paperin Leads</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter+Tight:wght@400;500;600&display=swap">
<style>
  /* Lead board: a tight metrics bar, then the leads themselves as the whole page. */
  :root {{
    --bg:#f6f6f4; --panel:#ffffff; --ink:#17191c; --muted:#5d636d; --faint:#949aa4;
    --line:#e7e8e5; --accent:#1f6feb; --money:#1f9d57;
    --f-display:'Fraunces',Georgia,serif; --f-body:'Inter Tight',system-ui,sans-serif;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --bg:#101214; --panel:#191c20; --ink:#eef0f2; --muted:#9aa1ab; --faint:#6a717b;
    --line:#282c31; --accent:#5b9bff; --money:#35c377; color-scheme:dark;
  }} }}
  :root[data-theme="dark"] {{
    --bg:#101214; --panel:#191c20; --ink:#eef0f2; --muted:#9aa1ab; --faint:#6a717b;
    --line:#282c31; --accent:#5b9bff; --money:#35c377; color-scheme:dark;
  }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); font-family:var(--f-body); line-height:1.5; }}
  .wrap {{ max-width:720px; margin:0 auto;
           padding-left:max(18px,env(safe-area-inset-left,0px));
           padding-right:max(18px,env(safe-area-inset-right,0px));
           padding-block:32px 56px; }}
  .eyebrow {{ font-size:.74rem; text-transform:uppercase; letter-spacing:.12em; color:var(--faint); }}
  h1 {{ font-family:var(--f-display); font-weight:700; font-size:2rem; margin:4px 0 24px; letter-spacing:-.01em; }}

  .bar {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--line);
          border:1px solid var(--line); border-radius:16px; overflow:hidden; margin-bottom:34px; }}
  .m {{ background:var(--panel); padding:16px 14px; min-width:0; }}
  .m-val {{ font-family:var(--f-display); font-weight:700; font-size:1.7rem; letter-spacing:-.01em;
            font-variant-numeric:tabular-nums; }}
  .m-lbl {{ font-size:.75rem; color:var(--muted); margin-top:3px; }}
  .m.hero .m-val {{ color:var(--accent); }}
  .m.money .m-val {{ color:var(--money); font-size:1.4rem; }}
  @media (max-width:520px) {{ .bar {{ grid-template-columns:repeat(2,1fr); }} }}

  .section-h {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.1em; color:var(--muted);
               margin:0 0 14px; }}
  .leads {{ display:flex; flex-direction:column; gap:14px; }}
  .lead {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:18px 20px; min-width:0; }}
  .lead-top {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 12px; }}
  .lead h3 {{ font-family:var(--f-display); font-weight:600; font-size:1.2rem; margin:0; }}
  .lead-meta {{ color:var(--muted); font-size:.9rem; }}
  .lead-msg {{ margin:11px 0 0; color:var(--ink); border-left:3px solid var(--accent); padding-left:13px;
               font-size:.96rem; }}
  .lead-links {{ margin-top:13px; display:flex; flex-wrap:wrap; gap:16px; font-size:.86rem; }}
  .lead-links a {{ color:var(--accent); text-decoration:none; }}
  .mono {{ font-family:ui-monospace,Menlo,monospace; color:var(--faint); }}

  .empty {{ background:var(--panel); border:1px solid var(--line); border-radius:18px;
            padding:44px 26px; text-align:center; }}
  .empty-dot {{ width:12px; height:12px; border-radius:50%; background:var(--accent); margin:0 auto 16px;
                box-shadow:0 0 0 6px color-mix(in srgb,var(--accent) 18%,transparent); }}
  .empty h3 {{ font-family:var(--f-display); font-weight:600; font-size:1.3rem; margin:0 0 8px; }}
  .empty p {{ color:var(--muted); margin:0 auto; max-width:40ch; font-size:.95rem; }}

  .foot {{ color:var(--faint); font-size:.78rem; margin-top:28px; }}
  a {{ color:var(--accent); }}
</style>

<div class="wrap">
  <div class="eyebrow">Live outreach</div>
  <h1>Your leads</h1>

  <div class="bar">{metrics}</div>

  <h2 class="section-h">Interested replies</h2>
  {body}

  <p class="foot">Updated {updated}, refreshes hourly. Auto-reply is off, so every reply reaches you with a ready response. Add budget before "days left" runs down.</p>
</div>
"""
open(out, "w").write(doc)
print("wrote", out, len(doc), "bytes")
