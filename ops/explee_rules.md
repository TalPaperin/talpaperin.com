# Explee standing rules: disqualifiers + how qualification works

Rules learned from real outcomes. The reply-check and EOD-handoff routines read
this file each run and apply it. Add new lessons here (one short rule per bullet)
and commit. Keep everything short: prospects do NOT read long emails or long
meeting invites, so qualifying has to be built into the copy, not a wall of text.

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

## DealMentor campaign launched (Tal, 2026-10-28)

Tal added a DealMentor outreach as a NEW project 55881 (NOT inside 49501). 6 campaigns:
310570 Founder-led sales, 310571 Fast-growing startups, 310572 B2B SaaS sales teams,
310573 Sales Training Firms, 310574 Outbound Agencies, 310575 Agency sales teams. As of
2026-10-28 all were discovery/listening (0 sent, pools still building). target_url =
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
