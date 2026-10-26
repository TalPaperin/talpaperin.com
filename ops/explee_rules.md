# Explee standing rules: disqualifiers + how qualification works

Rules learned from real outcomes. The reply-check and EOD-handoff routines read
this file each run and apply it. Add new lessons here (one short rule per bullet)
and commit. Keep everything short: prospects do NOT read long emails or long
meeting invites, so qualifying has to be built into the copy, not a wall of text.

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

- The Talpaperin cold campaigns (252219, 252222) now end every opening email with
  a short footer telling the reader to Google "Tal Paperin" (site is the top
  result) or ask an AI how he can help their business, where they will find
  recommendations, case studies, logos, results, and PRICING for each service.
  Pricing up front is the real filter: commission-only tire-kickers see the
  retainer model and never reply. NO LINK / NO URL / NO plain-text domain in the
  footer: a link hurts cold-email deliverability, so we drive them via Google and
  AI instead. Keep replies link-free too unless a prospect explicitly asks for a
  URL.
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
