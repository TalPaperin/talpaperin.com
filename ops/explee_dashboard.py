#!/usr/bin/env python3
# Generates the Explee outreach dashboard HTML from a snapshot JSON.
# Usage: python3 dashboard_gen.py <snapshot.json> <out.html>
import sys, json, html, datetime

snap = json.load(open(sys.argv[1]))
out = sys.argv[2]

bal = snap["balance"]["remain"] / 100.0
budget = snap["budget"]["daily_budget_usd"]
a = snap["analytics"]
leads = snap.get("hot_leads", {}).get("leads", [])

runway = (bal / budget) if budget else 0
sent = a["total_emails_sent"]
replies = a["total_replies"]
hot = a["total_hot_leads"]
spend = a["total_spend_usd"]
rate = (replies / sent * 100) if sent else 0.0

REBUILT = {252219, 252224}

def esc(s): return html.escape(str(s if s is not None else ""))

STATUS = {
 "outreach": ("live", "Sending"),
 "review": ("review", "Review"),
 "discovery": ("finding", "Finding leads"),
 "searching": ("finding", "Finding leads"),
 "starting": ("finding", "Starting"),
 "listening": ("paused", "Stopped"),
}

# sort: active (rebuilt / sending) first
def sortkey(c):
    order = {"outreach":0,"review":1,"searching":2,"discovery":2,"starting":2,"listening":9}
    return (0 if c["campaign_id"] in REBUILT else 1, order.get(c["status"],5), -c["emails_sent"])

rows = ""
for c in sorted(a["campaigns"], key=sortkey):
    cls, label = STATUS.get(c["status"], ("paused", c["status"].title()))
    crate = c["reply_rate_pct"]
    tag = '<span class="tag">rebuilt</span>' if c["campaign_id"] in REBUILT else ""
    pool = ""
    if c.get("leads_pool_total"):
        pool = f'{c["leads_pool_used"]}/{c["leads_pool_total"]}'
    rows += f"""
      <tr>
        <td class="cname"><span class="name">{esc(c['name'])}</span>{tag}</td>
        <td><span class="pill {cls}">{label}</span></td>
        <td class="num">{c['emails_sent']}</td>
        <td class="num">{c['total_replies']}</td>
        <td class="num">{crate:.1f}%</td>
        <td class="num">{c['hot_leads']}</td>
        <td class="num">${c['spend_usd']:.2f}</td>
        <td class="num dim">${c['daily_budget_usd']:.0f}</td>
        <td class="num dim">{pool}</td>
      </tr>"""

if leads:
    lead_items = ""
    for L in leads:
        why = (L.get("why_hot") or "").replace("\r"," ").replace("\n"," ").strip()
        why = why[:160] + ("..." if len(why) > 160 else "")
        li = L.get("linkedin_url")
        linked = f'<a href="{esc(li)}" target="_blank" rel="noopener">LinkedIn</a>' if li else ""
        em = esc(L.get("email") or "")
        lead_items += f"""
        <div class="lead">
          <div class="lead-head">
            <span class="lead-name">{esc(L.get('name') or 'Unknown')}</span>
            <span class="lead-meta">{esc(L.get('job_title') or '')}{' · ' if L.get('job_title') and L.get('company_name') else ''}{esc(L.get('company_name') or '')}</span>
          </div>
          <div class="lead-why">{esc(why)}</div>
          <div class="lead-foot"><span class="mono">{em}</span> {linked}</div>
        </div>"""
    leads_block = f'<div class="leads">{lead_items}</div>'
else:
    leads_block = '<div class="empty">No hot leads yet. They will appear here the moment someone replies with real interest.</div>'

updated = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y, %H:%M UTC")

def tile(label, value, sub="", tone=""):
    return f"""<div class="tile {tone}">
      <div class="t-label">{label}</div>
      <div class="t-value">{value}</div>
      <div class="t-sub">{sub}</div>
    </div>"""

tiles = "".join([
  tile("Balance", f"${bal:,.2f}", f"about {runway:.0f} days left at ${budget:.0f}/day", "good" if runway>7 else "warn"),
  tile("Daily budget", f"${budget:.0f}", "~$500 / month pace"),
  tile("Emails sent", f"{sent:,}", "all campaigns, lifetime"),
  tile("Replies", f"{replies:,}", f"{rate:.1f}% reply rate"),
  tile("Hot leads", f"{hot:,}", "flagged by Explee", "accentile" if hot else ""),
  tile("Spent", f"${spend:,.2f}", "lifetime"),
])

doc = f"""<meta name="claude:viewport-fit-sides" content="cover">
<title>Tal Paperin Outreach</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
  /* Layout: ops console — summary tiles on top, campaign table, hot-lead feed. */
  :root {{
    --bg:#f4f5f7; --panel:#ffffff; --ink:#15181f; --muted:#5b6472; --faint:#8a93a3;
    --line:#e5e8ee; --accent:#2563eb; --good:#1f9d57; --warn:#c77700; --crit:#d23b3b;
    --pill-bg:#eef1f6;
    --f-head:'Archivo',system-ui,sans-serif; --f-mono:'IBM Plex Mono',ui-monospace,monospace;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --bg:#0d1016; --panel:#151a22; --ink:#e9edf3; --muted:#9aa4b2; --faint:#6b7483;
    --line:#242b36; --accent:#5b9bff; --good:#35c377; --warn:#e3a13a; --crit:#ff6b6b;
    --pill-bg:#1e2530; color-scheme:dark;
  }} }}
  :root[data-theme="dark"] {{
    --bg:#0d1016; --panel:#151a22; --ink:#e9edf3; --muted:#9aa4b2; --faint:#6b7483;
    --line:#242b36; --accent:#5b9bff; --good:#35c377; --warn:#e3a13a; --crit:#ff6b6b;
    --pill-bg:#1e2530; color-scheme:dark;
  }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--ink); font-family:var(--f-head); line-height:1.45;
         font-variant-numeric:tabular-nums; }}
  .wrap {{ max-width:960px; margin:0 auto;
           padding-left:max(16px,env(safe-area-inset-left,0px));
           padding-right:max(16px,env(safe-area-inset-right,0px));
           padding-block:28px 48px; }}
  header {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 14px; margin-bottom:22px; }}
  h1 {{ font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-.01em; }}
  .sub {{ color:var(--muted); font-size:.9rem; }}
  .updated {{ margin-left:auto; color:var(--faint); font-size:.78rem; font-family:var(--f-mono); }}

  .tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:26px; }}
  .tile {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px 16px; min-width:0; }}
  .t-label {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); }}
  .t-value {{ font-family:var(--f-mono); font-weight:600; font-size:1.55rem; margin-top:4px; letter-spacing:-.01em; }}
  .t-sub {{ font-size:.76rem; color:var(--faint); margin-top:3px; }}
  .tile.good .t-value {{ color:var(--good); }}
  .tile.warn .t-value {{ color:var(--warn); }}
  .tile.accentile {{ border-color:var(--accent); }}
  .tile.accentile .t-value {{ color:var(--accent); }}

  .section-h {{ font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted);
               margin:0 0 10px; font-weight:600; }}
  .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; overflow:hidden; margin-bottom:26px; }}
  .tbl-scroll {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:.86rem; min-width:620px; }}
  th,td {{ text-align:left; padding:11px 14px; border-bottom:1px solid var(--line); white-space:nowrap; }}
  th {{ font-size:.68rem; text-transform:uppercase; letter-spacing:.06em; color:var(--faint); font-weight:600; }}
  tr:last-child td {{ border-bottom:none; }}
  td.num {{ text-align:right; font-family:var(--f-mono); }}
  td.dim {{ color:var(--faint); }}
  .cname .name {{ font-weight:600; }}
  .tag {{ font-size:.64rem; text-transform:uppercase; letter-spacing:.05em; color:var(--accent);
          border:1px solid var(--accent); border-radius:5px; padding:1px 5px; margin-left:8px; vertical-align:middle; }}
  .pill {{ font-size:.72rem; font-weight:600; padding:3px 9px; border-radius:999px; background:var(--pill-bg); color:var(--muted); white-space:nowrap; }}
  .pill.live {{ background:color-mix(in srgb,var(--good) 18%,transparent); color:var(--good); }}
  .pill.review {{ background:color-mix(in srgb,var(--warn) 18%,transparent); color:var(--warn); }}
  .pill.finding {{ background:color-mix(in srgb,var(--accent) 16%,transparent); color:var(--accent); }}
  .pill.paused {{ background:var(--pill-bg); color:var(--faint); }}

  .leads {{ display:flex; flex-direction:column; gap:12px; }}
  .lead {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px 16px; }}
  .lead-head {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 10px; }}
  .lead-name {{ font-weight:700; }}
  .lead-meta {{ color:var(--muted); font-size:.84rem; }}
  .lead-why {{ margin-top:7px; color:var(--ink); font-size:.9rem; border-left:3px solid var(--line); padding-left:10px; }}
  .lead-foot {{ margin-top:8px; font-size:.8rem; color:var(--faint); display:flex; gap:14px; flex-wrap:wrap; }}
  .lead-foot a {{ color:var(--accent); text-decoration:none; }}
  .mono {{ font-family:var(--f-mono); }}
  .empty {{ background:var(--panel); border:1px dashed var(--line); border-radius:14px; padding:22px 18px;
            color:var(--muted); font-size:.9rem; text-align:center; }}
  .foot {{ color:var(--faint); font-size:.76rem; margin-top:6px; line-height:1.6; }}
  a {{ color:var(--accent); }}
</style>

<div class="wrap">
  <header>
    <h1>Outreach</h1>
    <span class="sub">Tal Paperin &middot; Explee cold-email engine</span>
    <span class="updated">Updated {updated}</span>
  </header>

  <div class="tiles">{tiles}</div>

  <h2 class="section-h">Campaigns</h2>
  <div class="panel"><div class="tbl-scroll"><table>
    <thead><tr>
      <th>Campaign</th><th>Status</th><th>Sent</th><th>Replies</th><th>Rate</th>
      <th>Hot</th><th>Spent</th><th>Budget/d</th><th>Lead pool</th>
    </tr></thead>
    <tbody>{rows}
    </tbody>
  </table></div></div>

  <h2 class="section-h">Hot leads</h2>
  {leads_block}

  <p class="foot">Snapshot, refreshed hourly. Two campaigns rebuilt and relaunched (SaaS founders, Industrial &amp; export); the four earlier overlapping campaigns are stopped. Auto-reply is off, so replies route to you for a human response. Spend and reply totals are lifetime and include the earlier campaigns.</p>
</div>
"""
open(out, "w").write(doc)
print("wrote", out, len(doc), "bytes")
