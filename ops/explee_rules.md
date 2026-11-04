# Explee standing rules: disqualifiers + how qualification works

Rules learned from real outcomes. The reply-check and EOD-handoff routines read
this file each run and apply it. Add new lessons here (one short rule per bullet)
and commit. Keep everything short: prospects do NOT read long emails or long
meeting invites, so qualifying has to be built into the copy, not a wall of text.

## Sender identity: PERSONA model (Tal, 2026-11-04) -- SUPERSEDES the old "sender name is settled"

Tal flipped the Explee project (49501) sender name to "Mailbox names" (Automatic): every cold
email now goes out FROM the mailbox's own person (e.g. Finn Turner, Leo Brooks), not from
"Tal Paperin". The My-copy (project default, all 4 campaigns) was rewritten to open
"I'm {{sender_first_name}}. I work with Tal Paperin, a fractional CRO. He {helps|works with}
B2B companies {fix, build and run|rebuild and run} their {sales and marketing|sales} engine..."
and Explee auto-signs with the mailbox persona's name. This is deliberate: it (a) kills the old
body-says-Tal / signature-says-persona contradiction (the "Kristen/Tal", "Ofer Levy" confusion)
for good, (b) makes the ~10% AI-variant's random persona names coherent instead of a bug
(everyone is now "a person on Tal's team"), and (c) positions Tal as senior enough to have
people working on his behalf.
The OLD rule ("sender name is settled, it is Tal Paperin, persona names are a 10% bug to
ignore") is REVERSED and no longer applies. Do NOT revert the sender name to "Tal Paperin" and
do NOT re-flag persona names as a bug.
Copy constraints learned while deploying this (2026-11-04), keep them in mind for any My-copy edit:
- Explee's My-copy spam checker scans the TEMPLATE text, INCLUDING {{ai:}} instruction wording.
  Never put trigger words ("guarantee(s)", "promise(s)", money figures) inside an {{ai:}}
  instruction even as a negative ("no guarantees") -- it flags the literal word.
- A fixed ~80-word block identical across every send trips Gmail's repeated-passage filter.
  Break it with {a|b} spintax variants. No empty option and no parentheses inside the braces
  (e.g. use {sales and marketing|sales} engine, NOT {(and marketing) |}engine).
- A command telling the reader to "ask any AI how Tal can help your business" can trip the
  "manipulation" filter on some leads. Phrase it as a statement ("Any AI assistant can tell you
  about Tal Paperin"), not a command.

## Campaign review + ICP tightening (Tal, 2026-10-28)

Tal flagged "still no leads." Pulled project 49501 analytics + full inboxes. Diagnosis:
all-time 3,737 sent, 46 replies (1.2 pct), 18 flagged hot, but only 5 EVER booked (all in
252219 B2B SaaS); 252222 / 252223 / 252224 have 0 bookings. Reply volume fell from 13-15/day
(Oct 15-19) to ~2/day (Oct 27-28). Two leaks, not one: (1) volume (opener; the My-copy lock is
too new to judge), and (2) the bigger one, the replies we get are wrong-fit or tire-kickers, so
hot never becomes booked. Receipts: Yair Goldfinger/AppCard (150 emp, 10 yrs, we even used a
stale company name) hard "no interest"; Eran Elias/Spark Labs (an accelerator) "not at this
stage"; 252224 Industrial 23 replies / 0 books.

Decisions + actions taken:
- TIGHTENED ICP HARD (done via PATCH, targeting_editable=true). 252219 B2B SaaS: size now
  ~10-75 employees, seed-Series B, exclude >100 emp / >~8yr mature / accelerators-incubators-VCs-
  agencies. 252222 Bootstrapped: size ~5-50, B2B software/tech-enabled only (dropped generic "B2B
  services"), exclude mid-market+enterprise and accelerators/incubators/VCs/agencies. Do NOT
  re-broaden these size bands; the oversized/wrong-entity pulls were the core booking leak.
- 252224 Industrial: ARCHIVED (status=archived). Wrong vertical for Tal. Do not resume.
- Reply ask stays LINK-ONLY on warm replies (Tal's call): send positioning + soft Calendly link,
  do NOT propose specific call times.
  SUPERSEDED (Tal, 2026-11-01): LINK-ONLY is REVERSED for HIGH-INTENT replies. A two-week review
  found ~10 Oct 18-24 leads who said "yes, let's talk" / offered their own times / gave a phone
  number, and we bounced every one to a Calendly link; NONE booked (Allen Thrush, Shlomo Talitman,
  Moris Elkayam, Taylor Byington, John Wurch, Ori Yona, Oren Haimov, Kelly Franko). The link is the
  friction. NEW RULE: when a prospect offers times, asks us to send times, says "call me", or gives
  a phone number, do NOT send Calendly. Propose ONE concrete time (and offer to send a calendar
  invite on their yes), or offer to call the number they gave. Keep Calendly ONLY for lukewarm
  "maybe sometime" replies. If Explee returns reply_rate_limited for a contact (we already messaged
  them ~3x), send the re-engagement from tal@ksw.solutions via Gmail with a fresh subject instead
  (pound-policy bypass). Also: do NOT let a high-intent "yes" sit on one Calendly nudge and die;
  follow the POUND policy until they book, decline, or disqualify.

## NEVER outreach a CLIENT (Tal, 2026-11-02) -- HARD RULE, learned the hard way

The KSW re-engagement CSV (and any old CRM export) contains people who are now CLIENTS or
partners, not prospects. NEVER send a client a prospecting / re-engagement / "here is what I do
and what it costs" email. Before ANY re-engagement wave or prospect send, scrub the list against
known clients and drop them silently.
KNOWN CLIENTS / PARTNERS -- do NOT prospect, do NOT re-engage, do NOT pitch:
- noam@ai-recruitment.co (Noam) -- CLIENT. (Mistakenly sent a re-engagement 2026-11-02; do not repeat.)
- chris.latimer@vectorize.io (Chris Latimer, Vectorize) -- CLIENT (won deal). He appears in the
  re-engagement CSV at P4-NURTURE; NEVER email him as a prospect.
- Vectorize and HireMatch are active CLIENT accounts (we run their outbound). Anyone clearly at a
  client company is off-limits for KSW prospecting.
When in doubt whether a name is a client, ASK Tal before sending, do not guess.

## How to write a warm-reply / re-engagement (Tal, 2026-11-02, from the Raj Bhan post-mortem)

Dissected a weak email Claude sent. Rules, apply to every warm reply and re-engagement:
- OPEN WITH THEIR PAIN, not with Tal. Lead with the prospect's problem, tie it to what they do,
  THEN position Tal as the fix. Do NOT open with "I'm a fractional CRO and here's what I do" -- that
  is all about us and converts nobody.
- THE PAIN BANK (use talpaperin.com's own language -- Tal leads with these on the site; pick the ONE
  that fits the prospect and open on it, in their words):
    * "Your 4th VP of Sales hasn't delivered. Again." -- burned six figures on $30K/mo hires that did
      not move the number; another VP gone in 90 days.
    * Reps who can't close / hired reps but still no pipeline / team missing quota.
    * No team at all, and no time to build one.
    * A great product that just won't sell / no sales yet.
    * You're still closing every deal yourself (founder-led sales that won't scale).
    * No pipeline / the sales forecast is always wrong.
    * You want to sell globally (or into the US) and don't know where to start.
    * Need distributors / channel partners to reach new markets.
  Site hero framing to echo: "Your sales suck. You don't know why. I do. And I fix it, end to end."
  When unsure which pain fits, read the prospect's own reply/company and name the most likely one.
- PRICING: unless the prospect EXPLICITLY asks about price, do NOT quote any number. Just point them
  to talpaperin.com (pricing is on the site) and let the site do the reveal. This still satisfies the
  qualification gate (they see the price) without us dropping a scary figure.
- IF they ask price: the real tiers are $2,000/month, then $6,000/month, then $12,000/month,
  month-to-month. Lead with "$2k/month". NEVER say "$72,000/year" (it is WRONG and maximally scary).
  Frame per month, never annualized. Anchor against a full-time VP ($150-250K/yr) only if needed.
- Do NOT push or even volunteer TheDealMentor or a "downsell". Offering the cheap option
  before they object plants the objection, signals low conviction, and gives them permission to pass.
- Do NOT turn the call into an email price-gate. Never make a prospect "reply to confirm the price
  works" in writing, alone, before a call -- that is where they self-reject. Objections (e.g. "I
  thought it was revenue-share") are what the CALL is for. Get the call, handle it live.
- Keep the gate: they should have been pointed to the site (which shows pricing) before booking, and
  book only inside Tal's hours. But qualify by sending them to the site, not by pasting numbers.

## Meeting-qualification GATE + Tal's availability (Tal, 2026-11-02) -- HARD RULE

The point of all outreach is MEETINGS WITH QUALIFIED PROSPECTS, not meetings. A prospect is
NOT ready to book until they have visited talpaperin.com and seen (a) what Tal does and (b) what
he charges. This is how we stop wasting Tal's calls on people who did not know the model or price.
- SEQUENCE on any warm "let's talk" / "send me a time" / "send the invite" reply: FIRST point them
  to talpaperin.com (what Tal does) and talpaperin.com/pricing (what he charges), and state the
  model plainly in the reply: fractional CRO, month-to-month retainer, starts around $72,000/year,
  NOT commission-only, NOT a self-serve software tool. Ask them to take a look. ONLY AFTER they have the
  model/price and it is a fit do you lock a time. Make sure they have been sent to the site before
  any booking. Do NOT send a prospect a specific meeting time until this gate is passed.
- NO RANDOM TIME PROPOSALS. Never throw out a clock time just to fill the calendar.
- If the retainer is above their budget, route to the cheaper rungs instead of a call: Pay-Per-Meeting
  (done-for-you leads) or TheDealMentor.AI (DIY, tiered license fees). Do not burn a call slot on someone who
  cannot afford the service.
- TAL'S AVAILABILITY (Israel time, Asia/Jerusalem) -- NEVER propose/accept a time outside it:
  base windows 11:00-15:00 and 16:30-22:00, MINUS a STANDING DAILY MEETING that is always blocked.
  The meeting hour (Tal, 2026-11-02): RIGHT NOW it is 18:00-19:00 Israel. After the NEXT US time
  change it moves to 19:00-20:00 Israel (Tal will say when it shifts; do not infer the date yourself,
  I have gotten this wrong before). So:
    * NET BOOKABLE NOW: 11:00-15:00, 16:30-18:00, and 19:00-22:00 Israel.
    * NET BOOKABLE after the US change: 11:00-15:00, 16:30-19:00, and 20:00-22:00 Israel.
  (Plus the standing Shabbat pause: Fri 12:00 to Sat nightfall.)
  CONVERSION: do it case by case, do not rely on memorized PT/ET anchors (that is where errors crept
  in). Israel is UTC+2. Take the prospect's proposed time, convert to UTC, then +2 for Israel, and
  confirm it lands inside a bookable window AND not in the meeting block. If unsure of the prospect's
  current UTC offset (US DST vs standard), ask them to confirm their time zone rather than guessing.
  Propose ONE concrete time inside the net-bookable window and offer the calendar invite on their yes.
- Tal sends the actual calendar invite himself (direct invite + video link). Claude qualifies the
  prospect (site + pricing), proposes/confirms a time inside Tal's window, then hands to Tal to send
  the invite. Claude does NOT send calendar invites.

## Vectorize (Hindsight) reworked for enterprise meetings (Tal, 2026-10-28)

Vectorize sells Hindsight, the open-source standard for AI agent memory (teams at Nvidia, Groq,
EA build on it; large OSS dev base; paid product Hindsight Enterprise, 5-6 figure ACV; meetings
go to calendly.com/adam-hulkower-vectorize). It was the worst performer: 6,159 sent, 2 human
replies (0.03 pct), 0 hot, most "replies" auto-responders, highest spend. Cause: targeting
enterprise BY SIZE (2,000+/1,000+ employees) and cold-hitting VPs/CTOs who never answer cold.
Tal wants big-corporate meetings, so (his call 2026-10-28) I reworked the two live campaigns
(263613, 263612) via API, NOT down-market:
- Persona -> the technical CHAMPION who owns the agent in production (staff/principal AI eng,
  ML-platform/agent-infra eng), then multithread to their Head of AI. Not the CTO cold.
- Crowd -> LARGE COMPANIES ONLY (Tal's call 2026-10-28: he wants big-corporate deals): 263613
  roughly 2,000+ employees, 263612 roughly 1,000+ / $500M+ revenue, AND qualify on an active
  agent project / shipped agent feature (intent signal), not headcount alone. (An earlier pass
  briefly opened this to Series B-D scale-ups; Tal reverted it to large-only.) Edited in place,
  no new campaigns.
- Opener -> lead with the open-source standard + the Nvidia/Groq/EA proof and ONE specific
  question tied to the prospect's own live agent; link-free email 1 (already in the brief).
- LOOKALIKE by customer (Tal's idea 2026-10-28): EA builds on Hindsight, so 263613 now prioritizes
  gaming / interactive-entertainment peers (Activision Blizzard, Riot, Epic, Ubisoft, Take-Two,
  Roblox and similar), with a gaming-specific opener (peer proof "teams like EA build on Hindsight"
  + gaming memory use cases: persistent NPCs, player-support agents, moderation, live-ops copilots).
  TRUTH GUARD: the site lists EA among "teams building with Vectorize", so say "builds on Hindsight",
  NOT "paying customer". Same lookalike logic can later extend to Nvidia/Groq peers (AI infra/chips).
- FINANCE ICP added (Tal fwded Chris's CRM list, 2026-10-28): NEW dedicated campaign 311502
  "F: Investment firms (AI research agents)" in project 51016. ICP = investment firms (VC, PE,
  hedge funds, asset managers, investment platforms) building AI agents for investment research,
  memo/Q&A generation, deal tracking or institutional-knowledge memory. SIZE: qualify on AUM +
  active agent project + 5-6 figure budget, ANY headcount (Tal's call; these firms are small-
  headcount/big-budget, so the large-only floor does NOT apply here). Champion persona = Head of
  AI/Data/Eng or CTO at the fund, or the agent-strategy lead they are hiring (a live signal).
  Finance hook: own-cloud / data-never-leaves (compliance) + the open-source standard. CONFIDENTIALITY
  GUARD: the firms Chris named (Madrona, Serengeti, Arcole, DSV, Tudor) are PRIVATE CRM engagements,
  some on hold, NOT public reference customers. Use them ONLY to shape the ICP and use-case language;
  NEVER name them in outreach (unlike EA/Nvidia/Groq, which are public site logos). As of 2026-10-28
  311502 is in discovery (pool building); it needs Tal to approve/launch it in Explee to start sending.
Deferred (Tal: signals first): mining developers already using Hindsight inside big companies
(the warm-champion / PLG-to-enterprise path) and competitor-tool-user lists; both need GitHub/
usage or intent data Explee won't source itself. STILL OPEN as levers: lower volume + higher
relevance and deliverability (the total silence on 3,295 enterprise sends hints at spam-foldering)
- flag to Tal, do not change client budgets unprompted. Vectorize stays auto-reply-ON, we do NOT
send replies there (see reply bullet); this note is about the outbound targeting only.

## DealMentor campaign launched (Tal, 2026-10-28)

Tal added a DealMentor outreach as a NEW project 55881 (NOT inside 49501). 6 campaigns exist
but only THREE are relevant (Tal, 2026-10-28): 310570 Founder-led sales, 310571 Fast-growing
startups, 310572 B2B SaaS sales teams (the direct end-user buyers). The other three, 310573
Sales Training Firms, 310574 Outbound Agencies, 310575 Agency sales teams, are user-paused and
NOT relevant, do not monitor or re-tune them unless Tal resumes them. As of 2026-10-28 the live
three were discovery/review (0 sent, pools still building). target_url =
https://www.thedealmentor.ai/contact. Decisions: I handle DealMentor replies on a DM-specific
track (see reply_check_playbook.md: point to thedealmentor.ai, DIY framing (do not quote a flat price), NO Calendly,
NO fractional-CRO pitch), and I tightened the ICP + offers (done via PATCH): set target_role per
segment, capped company size to small (~1-50, a couple at ~1-75; dropped the old 1-500 band,
since the DealMentor buyer is the "can't afford senior help" small/early crowd), and rewrote each
offer to lead with what TheDealMentor.AI is (self-serve AI sales platform, see thedealmentor.ai for pricing) plus the segment benefit.
Do NOT re-broaden to mid-market/enterprise. Add 55881 to every reply-check cycle. Note: the
`keywords` field is read-only via the API (PATCH rejects it with extra_forbidden); strip it from
any PATCH body.

## Follow-up cadence: POUND warm non-bookers until they book (Tal, 2026-10-25)

This OVERRIDES the routine prompt's "one 48h nudge, once ever" limit. For any lead who showed
genuine buying intent but has NOT booked (said yes, asked for a time or a link, offered specific
times, "looking forward to the call", asked us to elaborate on the offer), keep following up until
they book, hard-decline, or dead-end. Not one nudge: as many as it takes, spaced about 2-3 days apart.
- VARY every touch. Never resend the same canned nudge. Change the angle and, where possible, the
  SUBJECT LINE. The Explee reply endpoint IGNORES a custom subject (it always threads "Re: <orig>",
  tested 2026-10-25), so to change the subject send the follow-up from tal@ksw.solutions via Gmail
  (mcp__Gmail__send_message, fresh subject, no replyThreadId so it starts a new thread) to the lead's
  real email (use the address they actually reply from). Bonus: this sends from Tal's own address, not
  the rotating campaign mailboxes that are landing in spam, which helps deliverability and trust.
- Remove booking friction. Offer "reply with a time and I will send a calendar invite to your inbox"
  alongside the Calendly link, especially for anyone who stalled on Calendly or offered their own times.
- STOP pounding when the lead books (add them to ops/booked_leads.txt), hard-declines / opts out, or is
  a disqualifier below. A soft "not now / not relevant" still gets just the ONE rebuttal; if they then
  re-engage, they become a pound target again.
- AUTO-DROP declines silently (Tal, 2026-10-26). When a lead hard-declines, opts out, or declines again
  AFTER we already sent our one rebuttal, drop them from the pound/watch list automatically and do NOT
  surface the decline to Tal. No "FYI they passed" note, no closing-the-loop line: just stop and stay
  quiet. Only surface a decline when it is genuinely ambiguous (unclear whether it deserves a rebuttal)
  or carries something Tal needs (a referral to someone else, a complaint, a deliverability signal).
- Booked leads (ops/booked_leads.txt) are NEVER pounded.
- These leads are all Explee-sourced even when the live conversation has moved into Tal's Gmail inbox;
  a Gmail-direct pound is correct and expected, it is not off-campaign outreach.

## An autoresponder is NOT a lead (Tal + client Adam, 2026-10-26)

A real client (Adam/Vectorize) rejected a handoff file because an out-of-office auto-reply was
labelled "engaged, needs human follow-up." It was a TAFW vacation auto-reply from ms@svb.com, the
reply landed 11 seconds after our send, and the name on the record ("Sindhu M") was the campaign's
bad personalization token, not the mailbox owner (Manoj Selvaraj, which Explee's own contact field
already had right). Lessons, apply everywhere (reply check AND SDR handoff):

- "ENGAGED" / "WARM" / "HOT" means a HUMAN replied on the merits: real interest, a real question, a
  request, or a genuine "not now, come back at <time>." Nothing less EVER gets that label. An
  autoresponder is NEVER hot/warm/engaged, full stop.
- You MAY harvest contact details from an autoresponder, but you MUST label the source (Tal, 2026-10-26).
  Out-of-office / vacation / TAFW / "automatic reply" notices and left-company / email-changed redirects
  often expose usable intel: the person's real name and return date, or an alternate/redirect contact's
  name, email and phone. Capture that into a clearly-labelled "REACH-OUT (from auto-reply, not engaged)"
  entry, LOW priority, and state in the Status/notes that it came from an auto-reply and the person has
  NOT engaged. Never imply interest. If an auto-reply exposes no usable new contact detail (just "I'm
  away"), skip it. Pure bounces / invalid-address / recipient-gone notices with no alternate contact are
  still dropped entirely.
- TIMING TELL: any "reply" that arrives within ~60 seconds of our send is an autoresponder by
  definition. Check the timestamps; a near-instant reply is never a human.
- NAME: use the person's real name from their signature or Explee's contact record, NOT the opener's
  personalization token (the token is often wrong, as with "Sindhu"). If the name cannot be verified,
  leave it blank; never guess.
- CONTACT DETAILS: a general switchboard number (e.g. a 1-800/1-888 main line) or a role/group mailbox
  is NOT a direct contact. Mark it "(general)" or leave it blank; never present it as the person's line.
- If a client has NO genuinely engaged human leads in the window, send "nothing new." An honest empty
  list beats a padded one.

## Disqualifiers (NOT a fit: do not auto-book, do not push Calendly, do not hand to an SDR; surface to Tal)

- COMMISSION-ONLY / SUCCESS-FEE-ONLY / REV-SHARE / EQUITY-ONLY. Tal works on a
  fractional retainer. He does NOT work for pure commission, a cut of the deals,
  pay-on-results or equity only. This already burned two booked calls that turned
  out to be commission-only time-wasters (Oren Haimov, and Mohan Sam / Spenego).
  If a prospect's reply hints they want a commission / rev-share / success-fee /
  equity setup, do NOT book a call: surface to Tal.

## How qualification works (the lesson from the wasted calls)

The wasted calls happened because people booked without understanding Tal charges
a retainer, and the long confirmation email / calendar invite did not fix it
because they do not read it. The fix lives at FIRST TOUCH, not in replies:

- OPENER IS NOW LOCKED via Explee "My copy" (Tal, 2026-10-27). The first email is a FIXED
  template we wrote (Explee project default, used by all 3 Talpaperin campaigns), NOT AI-generated
  from the brief. Explee sends our exact copy to ~90% of leads and an AI variant to ~10%. This
  replaced the AI-"Instructions" openers, which kept drifting off-brief (offering "a few short ideas",
  bloating the footer). The locked template is the short, direct winner that was converting (the
  Kevin Maag / IntegraTouch style): a one-line specific hook, "I'm Tal Paperin, a fractional CRO. I
  help B2B companies fix, build and run their sales (and marketing) engine: the plan, the team and the
  pipeline, without a full-time hire.", a one-line concrete payoff, then one short credibility line
  ("Why me? Just ask any AI how Tal Paperin can help your business."), then the single CTA "It's a
  15-minute intro call.", signed Tal Paperin. Subject: "Tal Paperin x {{company}}". The two personalization sentences are the only AI-filled lines. NO LINK / NO URL
  anywhere (hurts deliverability). The old long Google-me + $30M footer was dropped: it lengthened the
  email and suppressed replies. Source of truth for the opener is now the Explee "My copy" box, not the
  campaign `offer` brief. Keep replies link-free too unless a prospect explicitly asks for a URL.
- So in replies, do NOT add a separate "I work on a retainer" line and do NOT paste
  pricing. Just handle the reply normally (book the call via Calendly for genuine
  interest). The footer already set the frame.
- If a prospect still pushes commission-only terms after all that, stop: surface to
  Tal, do not keep booking.

## Campaign coverage (do NOT trust the analytics feed to list campaigns)

The GET /autogtm/projects/{pid}/analytics reply-count list is INCOMPLETE: it only
surfaces the currently-sending ("outreach") campaigns. Paused / "listening" campaigns
still receive inbound replies that the analytics list hides. A whole campaign of warm
leads was missed this way (252224 Industrial had 23 replied contacts, 252223 Services 3,
none visible in analytics).

So EVERY reply-check cycle, scan these inboxes DIRECTLY, by campaign id, regardless of
whether analytics lists them:
- Talpaperin (project 49501): 252219, 252222, 252223, 252224 (and any other 49501 campaign).
- HireMatch (project 51033): 263741, 263742, 263743, 263746, 280152.
GET /autogtm/campaigns/{cid}/inbox for each, page it, and process every contact with
reply_count>0. Treat a flat total_replies number as NOT proof that nothing changed; the
real signal is the per-campaign inbox contents.

## Shabbat pause (Tal keeps Shabbat, ALWAYS honor this)

Tal observes Shabbat, so NOTHING may go out in his name during it.
- Window: from Friday 12:00 until Saturday nightfall in Israel time (Asia/Jerusalem,
  UTC+3 in DST / UTC+2 in standard time). Use Saturday 20:30 Israel time as a safe
  year-round "Shabbat is over" cutoff; if unsure whether it has ended, wait.
- During the window the reply-check routine may still run its read-only scan, but it
  sends NOTHING: no reply, no rebuttal, no nudge, and no email to Tal. Stay completely
  quiet. Hold any hot lead or nudge until after the window; prospects can still self-book
  via the Calendly link already in their thread, so nothing is lost by waiting.
- A 48h nudge that comes due during Shabbat is sent AFTER the window, not during it.
- MOTZEI SHABBAT SUMMARY: the FIRST reply-check run after Saturday 20:30 Israel posts
  Tal ONE consolidated summary of everything that came in and everything held across
  Friday-Saturday, then processes the held backlog (send the held replies/nudges then).
  Only the hourly routine (not the +30 offset one) posts this summary, to avoid a
  duplicate; if a motzei-Shabbat summary was already posted since Shabbat ended, stay quiet.

## Friday review: Talpaperin quality fix + DealMentor VP-Sales pivot + Vectorize opener rewrite (Tal, 2026-10-30)

Tal: "Talpaperin performance significantly worse than last week. We waited Wed/Thu, now it's Fri, fix it."
Computed week-over-week genuine human replies (autoresponders stripped) on 252219+252222:
- Last wk (Oct16-22): 24 genuine. This wk (Oct23-30): 22 genuine. Prior (Oct9-15): 7. So raw reply
  volume is FLAT, not collapsed. What dropped is the MIX/quality, not the count.
- Last wk mix: ~5 clean "let's meet" + 1 booking (Sharon/gotrack, Shlomo, Moris, Taylor, Kevin).
- This wk mix: 2 clean meeting-intent (Allen/ContractorRush, John Wurch) + a pile of price-shoppers
  (Umesh "charging structure", Eyal "pay per meeting?", Liran "success-based", Karim) + more
  hostility (Ivan, Ron Peled, Yair/AppCard, Kahlil, Tomer declining).
ROOT CAUSE: the price/commission flood is concentrated in 252222 "Bootstrapped B2B" whose own ICP
selected for "cash-conscious growth / lightly funded" = people who want commission-only and cannot
fund a retainer. Fishing for retainer clients in a commission-only pond. NOT a geography problem
(gotrack, this period's booking cohort, is Israeli), it is an AFFORDABILITY/FIT problem.
FIXES (done via PATCH, targeting_editable=true):
- 252222 renamed "Funded small B2B SaaS", repointed OFF bootstrapped/cash-conscious -> funded OR
  revenue-scaled small B2B SaaS (15-75 emp) that can actually fund senior help. Offer reworded
  "funded and growing" (was "bootstrapped and small"). Do NOT re-add "bootstrapped/cash-conscious".
- BOTH 252219 and 252222 negative_criteria now exclude "Wants commission-only / pay-on-success /
  percentage-of-sales" and "Pre-revenue or so cash-constrained there is no budget for senior help".
- Did NOT touch geo (Israel includes real wins) and did NOT touch the locked My-copy opener.
- Give it runtime: the ICP change takes a few days to flow into sends then replies before judging.

DealMentor VP-Sales pivot (Tal, 2026-10-30): "need VP Sales or sales directors in SMALL companies,
NOT tech. 3 demos yesterday but looks like curiosity." The old 3 campaigns targeted founders/CEOs at
small TECH/SaaS = curiosity tire-kickers on a DIY tool. Repointed all 3 (310570/310571/310572) via
PATCH to: ROLE = VP Sales / Sales Director / Head of Sales who owns the number and manages a team
(NOT founder/CEO, NOT a lone rep); SIZE = small NON-TECH companies ~10-100 emp with a real sales team
and a sales leader; split by non-tech vertical: 310570 manufacturing/industrial, 310571 distribution/
wholesale/logistics, 310572 B2B services (staffing/agencies/commercial/professional/construction).
Offer + customer_problem reworded for a sales LEADER (team visibility, next-step per rep, deal reviews,
prospect research + scripts for the whole team) not a founder. MY-COPY: use the "team managers" version
(Version B) across all 3 now; the "founders" version (A) no longer matches the audience.

Vectorize opener rewrite (Tal, 2026-10-30): across ~3,970 contacts, 100% autoresponders, 0 human
replies = COPY problem, not volume or ICP (the OOO/left-company bounces prove the addresses are real
and senior). Rewrote the offer brief on 263613 + 263612 via PATCH: write as Adam, a real ENGINEER,
peer-to-peer, short (4-6 sentences), lowercase-casual; OPEN with a specific observation about THEIR
agent/AI work; ONE line = what Hindsight is + Nvidia/Groq/EA + open-source proof; ASK = low-friction
TECHNICAL ("want me to send the repo / a short writeup?" or swap notes with the engineers who built
it), NOT a demo/calendar link, because engineers reply to a repo offer far sooner than a sales call.
FORBIDDEN: buzzwords, feature lists, invented metrics. Fixed-opener (My-copy) draft handed to Tal.

## Copy capitalization: NEVER write openers in all-lowercase (Tal, 2026-11-01)

I handed Tal a Vectorize opener written entirely in lowercase ("engineer-casual"); he had to
make ~13 fixes, almost all capitalization, including the brand (Hindsight, Vectorize), proof names
(NVIDIA, Groq) and the sender's own name (Adam). Lowercasing proper nouns is a defect, not a style.
RULE: all opener/reply copy uses normal capitalization, capital sentence starts and every proper
noun (company, product, partner, person) capitalized. Never all-lowercase. The Vectorize offer
briefs (263613/263612) were fixed to require this for the AI-variant too.

## Volume + follow-ups + new segment (Tal, 2026-11-01)

Benchmark: Tal's old outbound agency (BEC) ran 500 mailboxes, ~5,000 emails/day, got 166 leads +
dozens of meetings + 2 closed for $11K. Our Explee engine is ~6x cheaper per lead ($10.62 vs ~$66)
and ~3x more efficient per email, but was volume-starved: ~305 emails/day and ZERO follow-ups.
Root issue vs the agency = VOLUME and FOLLOW-UPS, not targeting/copy. Decisions:
- Tal raised the project daily budget to $36/day.
- Tal turned FOLLOW-UPS ON (was single-touch, 0 follow-ups; most replies come from touches 2-4).
- Replies: handled by the reply-check routines (conversion leak already fixed 2026-11-01).
- NEW SEGMENT added (campaign 347642 "Scaling B2B (Series B+, US, 50-200)", project 49501):
  later-stage / bigger buyer to add volume AND chase bigger deals. ICP = US B2B tech/tech-enabled,
  ~50-200 emp, Series B+ or real revenue scale, scaling past founder-led sales, no seasoned CRO yet;
  CEO/revenue-owner. Excludes commission-only/no-budget, established CRO, enterprise >500, tiny/pre-rev.
  Inherits the project Calendly + locked "My copy" opener. Cap ~$10/day (12+13+10 under the $36).
  Created in "discovery" status; if it does not auto-advance to outreach, Tal approves/launches in UI.
  CONFIRM follow-ups are ON for this new lane too (may be per-campaign).
Now three active Talpaperin lanes (252219, 252222, 347642) + follow-ups + fixed conversion = the
volume/sequencing/conversion stack we were missing vs the agency, at a fraction of the cost.

## Add a marketing / lead-gen line to warm replies (Tal, 2026-11-01)

Shlomi Kakon (CEO, Box.co.il) asked "how can you help?", I answered with the sales-engine pitch
only, and he passed. Lesson: many prospects' real pain is PIPELINE/LEADS, not sales management, so
leading only with "I build and run your sales team" misses them. RULE: in warm Talpaperin replies,
and especially in "what do you do / how can you help" answers, include ONE short line that KSW also
drives the MARKETING side, getting them leads and booked meetings, not just running the sales team.
Two levers to name (match to their hint): the in-house fractional CMO / demand-gen capability, and
Pay-Per-Meeting (done-for-you qualified meetings on their calendar, https://talpaperin.com/services/pay-per-meeting).
Keep it to one line, do not turn the reply into a feature list. Stays consistent with positioning.md
(fractional CRO owns the number; full marketing capability via an in-house fractional CMO).
