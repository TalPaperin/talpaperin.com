# Explee reply-check playbook

The hourly and hourly+30 Explee reply-check routines read THIS file each run and
follow it. Keeping the full procedure here (instead of inline in the trigger
prompt) keeps the recurring prompt small. Never build or publish any dashboard.

## Setup each run
- cd /home/user/talpaperin.com ; git fetch origin main ; git reset --hard origin/main.
- API base https://api.explee.com/public/api/v1 , header "X-API-Key: $EXPLEE_API_KEY_TALPAPERIN". Use curl (urllib gets 403 through the proxy).
- Read ops/booked_leads.txt (skip every listed email entirely: no reply, no rebuttal, no nudge) and ops/explee_rules.md (apply its standing disqualifiers, campaign-coverage note, Shabbat pause, and the POUND follow-up policy). Follow CLAUDE.md voice everywhere.

## What to scan
- GET /autogtm/projects/{pid}/analytics for Talpaperin 49501 and HireMatch 51033; scan EVERY campaign that has replies, not a fixed list (dormant campaigns get resumed).
- For each campaign: GET /autogtm/campaigns/{cid}/inbox (results under "contacts", 50 per page, paginate with limit/offset following has_more/next_offset). For each contact with reply_count>0: GET /autogtm/campaigns/{cid}/inbox/{person_id}, order the "messages" array by ts, judge the TRUE last message. Do NOT trust latest_intent, and do NOT use latest_reply_at vs latest_sent_at as the signal.
- A thread needs attention ONLY if the last message by ts is a "reply" whose from_email is the PROSPECT. A reply whose from_email is any ksw.solutions OR hire-match.ai address is us/Tal replying: the thread is handled, skip it.
- Coverage (analytics omits paused/listening campaigns): always scan these inboxes directly regardless. Talpaperin: 252219, 252222, 252223, 252224. HireMatch: 263741, 263742, 263743, 263746, 280152.
- OPENER SPOT-CHECK (mostly solved as of 2026-10-27: the opener is now LOCKED via Explee "My copy", a fixed template we wrote, sent to ~90% of leads, with ~10% an anchored AI variant). So the old off-brief drift (an opener once offered "a few short ideas") can now only appear in the ~10% AI variant. A light glance each cycle is still worth it: in the inboxes you already pull, check the most recent OUTBOUND openers (first "sent" per thread) for the single 15-minute-call ask, NO link/URL, and a correct name. Only surface to Tal if the FIXED copy itself looks broken or a 10% AI variant is egregiously off (not minor wording variation, he said to ignore small drift). The opener source of truth is the Explee "My copy" box (project default, all 3 campaigns), not the `offer` brief.
- Do NOT judge a campaign by its single newest reply. Several inbounds can land between runs, the analytics count is only the net, and an engaged reply can sit UNDER a later out-of-office or decline (this is how a warm CDL-driver lead got missed once). Whenever a campaign shows any new inbound since the last run, scan ALL its contacts with reply_count>0 and judge each one's true last message, not just the most recent thread.

## Already-closing / already-booked guard
Calendly bookings are invisible to this API. Do NOT send another message when the prospect's last inbound is a positive acceptance or sign-off with no actual question ("sounds good", "I'll book", "I'll coordinate a meeting", "looking forward to it", "I'll grab a time"), above all after we already sent the Calendly link. Those threads are DONE. The only permitted re-contact is the safe follow-up defined by the POUND policy in ops/explee_rules.md. Classify as A (reply) only when the last inbound genuinely asks a question or requests a time/info we have not already provided.

## Classify by CONTENT (not Explee's intent label), then do ONE
- (A) REPLY: genuine engagement, a real question, a request for a time or info, or genuine confusion asking what you mean.
- (B) REBUTTAL (once per thread ever): a soft or reflexive decline ("not interested" with no reason, "we're fine right now", "all good right now", "too busy", "not using external help", or a pass that misreads what we do). Send ONE short, sharp, senior, non-desperate reframe plus a next step. If our last message in the thread was already a rebuttal, let it go.
- (C) SKIP (no reply, no rebuttal): hard decline / opt-out ("remove me", "unsubscribe", "stop", "do not contact"), hostile replies, clear competitors / peers / agencies / vendors pitching us, a fundamental not-a-fit (wrong market or business model), out-of-office autoresponders, bounces, left-company or email-changed notices, anyone who already declined more than once. Never reply to an autoresponder. When unsure whether a decline deserves a rebuttal, surface it to Tal instead of sending.

NEVER offer, promise or send written ideas, tips, advice, an audit or a plan, by email or as a hook. If a prospect says "yes, send the ideas", reply that generic written ideas are cheap and usually wrong for their specific company, that the useful version is a short 15-minute call, then give the Calendly link and the tal@ksw.solutions handoff line.

### Reply / rebuttal craft (Tal, 2026-10-26: write like a senior operator, not an apologizer)
Short, confident, specific. Structure: ONE sharp reframe tied to what they actually said + ONE clean ask. Then stop.
- Do NOT stack softeners. One acknowledgement is plenty. Never pile "both are fair" + "no worries at all" + "if it's genuinely not a priority, no worries" into one reply; three apologies read as permission-seeking and kill the close. At most one brief "fair enough".
- Weave the handoff into the close, do not bolt it on. A standalone last line like "You can reach me directly at tal@ksw.solutions" after a soft sign-off reads detached. Fold the direct email into the same sentence as the ask (e.g. "15 minutes, no pitch: <calendly>, and it comes straight to my inbox at tal@ksw.solutions.").
- End on the ask or the argument, not an apology. "If it's not a priority I won't chase it" is a fine confident out; do not follow it with more hedging or a tacked-on line.

## Sending (auto-reply is OFF; I send)
Send via POST /autogtm/campaigns/{cid}/inbox/{person_id}/reply with {"body_text": "...", "cc_emails": ["tal@ksw.solutions"]} on EVERY reply, rebuttal and nudge. Explee's own links are clean (not routed through Gmail), so do not worry about link mangling on the prospect side.

- Talpaperin (project 49501: 252219 B2B SaaS, 252224 Industrial, 252223 Services, 252222 Bootstrapped B2B, plus any other 49501 campaign): reply in Tal's voice per CLAUDE.md (no em/en dashes, straight quotes, short, varied). The only ask is a short call via https://calendly.com/ksw/15min ; when it fits, point to talpaperin.com (services, recommendations, case studies, pricing). POSITIONING: Tal builds and runs the client's own sales (usually US): the go-to-market plan or executing the existing one, hiring/training/managing the team (SDRs, AEs, reps), owning the number. Do NOT frame him as export or international-only. MORE INFO asks: one short line on what Tal does + talpaperin.com + suggest they ask any AI "who is Tal Paperin and how can he help my business" (no long bio or client list). HANDOFF: whenever a reply includes the Calendly link, add one line that they can reach Tal directly at tal@ksw.solutions and that the meeting invite comes from that address. If a reply needs Tal's judgment (pricing, legal, NDA, ambiguous scope), do NOT send; surface to Tal.
- HireMatch (263741, 263742, 263743, 263746): reply AS Tanice Parkes at HireMatch (AI recruiting: resume screening and matching, AI interviews, assessments). English only, short, friendly, senior recruiting-tech voice, no hype, no dashes, straight quotes. NO Calendly / booking link, NO demo. On genuine interest or a worthwhile rebuttal: thank or reframe, ask ONE qualifying question (roughly how much hiring they do, and whether resume screening or first-round interviews is the bottleneck), propose a short intro call with the HireMatch team, then surface the lead to Tal.
- Vectorize (project 51016): auto-reply is ON (Explee sends it). Do NOT send replies. Just spot-check that a recent auto-reply did not include a link it should not, and surface any genuinely hot lead.

## Nudge and POUND sweep (run every cycle)
Run this independently of new inbound (candidates' last message is OURS, so a new-reply delta scan never catches them). Follow the POUND policy in ops/explee_rules.md: keep following up on warm non-bookers until they book, hard-decline, or disqualify; vary every touch; change the subject by sending the follow-up from tal@ksw.solutions via Gmail (the Explee reply endpoint ignores a custom subject); offer to send a direct calendar invite to remove Calendly friction. Skip anyone in ops/booked_leads.txt and anyone who named a future time. The old "one 48-hour nudge, once ever" limit is SUPERSEDED by that pound policy.

## Guaranteed copy to Tal (EVERY send, no exceptions)
Explee's cc_emails is unreliable (rotating mailboxes drop it), so after EACH successful send, load the Gmail tool and send a copy to tal@ksw.solutions with mcp__Gmail__send_message. Subject: "[Explee sent] <campaign name> - <lead name> (<reply|rebuttal|nudge>)". Use htmlBody, NOT the plain body field (Gmail mangles bare URLs into google.com/url redirects); build simple HTML with <br> for line breaks and render EVERY URL as an anchor. Header block: Campaign, Lead name, Company, Lead email, Lead phone if in signature, Classification, and the prospect's last inbound line being answered; then a line "--- Message sent ---" and the EXACT text sent (links as anchors). Keep cc_emails on the Explee reply too.

Note: a follow-up sent FROM tal@ksw.solutions via Gmail (e.g. a pound with a fresh subject) is already in Tal's Sent, so it needs no separate copy; the guaranteed copy is for Explee-channel sends.

## Report
Report only new replies, rebuttals or nudges sent, or anything genuinely needing Tal (a real lead, an ambiguous thread, a problem). Otherwise stay completely quiet. Hard declines, opt-outs, and leads who decline again AFTER our one rebuttal are dropped from the pound/watch list automatically and NOT reported: no "FYI they passed", no closing-the-loop line (Tal, 2026-10-26). Surface a decline only when it is genuinely ambiguous or carries something Tal needs (a referral, a complaint, a deliverability signal).
