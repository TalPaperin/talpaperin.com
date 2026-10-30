# Explee standing rules: disqualifiers + how qualification works

Rules learned from real outcomes. The reply-check and EOD-handoff routines read
this file each run and apply it. Add new lessons here (one short rule per bullet)
and commit. Keep everything short: prospects do NOT read long emails or long
meeting invites, so qualifying has to be built into the copy, not a wall of text.

## Sender name is SETTLED, do NOT raise it again (Tal, 2026-10-29)

There is ONE global sender-name field in Explee. It is already set to "Tal Paperin".
It CANNOT be set per mailbox, there are HUNDREDS of rotating mailboxes. So there is
NOTHING to do and nothing to "fix" about the sender name / signature. Emails that sign
with a persona first name (Willis, Katherine, Gavin, Rhiannon, etc.) are the ~10% AI-variant
sends (Explee sends your My-copy to 90% of leads and its own AI email to 10%); the AI 10% does
not honor the global sender name. That is expected and out of Tal's control. Likewise the
occasional "can I send you a few short ideas" opener is that same 10% AI variant, NOT the
locked My-copy (which is the correct 15-min-call opener on all 3 campaigns, project default).
DO NOT tell Tal to set the sender name per mailbox, DO NOT re-flag the Tal/persona signature as
a bug to fix, DO NOT claim a campaign's main opener is the "ideas" one. The 90% My-copy is clean.

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
track (see reply_check_playbook.md: point to thedealmentor.ai, $149/mo DIY framing, NO Calendly,
NO fractional-CRO pitch), and I tightened the ICP + offers (done via PATCH): set target_role per
segment, capped company size to small (~1-50, a couple at ~1-75; dropped the old 1-500 band,
since the DealMentor buyer is the "can't afford senior help" small/early crowd), and rewrote each
offer to lead with what TheDealMentor.AI is ($149/mo AI sales platform) plus the segment benefit.
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
small TECH/SaaS = curiosity tire-kickers on a $149 tool. Repointed all 3 (310570/310571/310572) via
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
