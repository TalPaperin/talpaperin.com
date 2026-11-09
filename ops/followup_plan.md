# Re-engagement follow-up plan (Tal approved 2026-11-03)

For every lead we contacted that has NOT replied. Source of truth = the KSW Lead Tracker artifact
(https://claude.ai/artifact/XFXSMiu9bwe2rtkzJUyk1a), `leads` collection, managed via ArtifactData.

## The 4-touch sequence (pain-first, from tal@ksw.solutions via Gmail, fresh subject each time)
Touch dates are measured from the lead's `date_contacted` (touch 1):
- Touch 1: the re-engagement (already sent).
- Touch 2: +3 days. ONE short line naming THEIR pain (not what Tal does).
  MATCH THE PAIN TO THE SPECIFIC LEAD (Tal, 2026-11-03) - this is the whole point:
  before writing, read the lead's `context` (their own prior words) and what their company actually
  does, then name the pain THEY have, in their language. If their prior reply already revealed it
  ("what is the cost", "curious how it works", "quick convo", "depends on terms"), speak to that
  exact thing. Use the pain bank only as a starting point and pick the ONE that genuinely fits this
  lead's business and stage; never paste a generic pain. A mismatched pain is worse than no email.
- Touch 3: +7 days. A different pain angle OR one concrete receipt (a real KSW outcome, never invented).
- Touch 4: +14 days. The breakup: "should I close your file?" Short. These pull the most replies.
Every touch: lead with pain, straight quotes, no em dashes, no "here's what I do" opener, vary the
subject line, point to talpaperin.com only if useful (pricing self-qualifies). NEVER quote a flat
price unless asked; DealMentor is never pushed.

## Tiers (field `tier` on each lead)
- `pound`: genuinely hot before (said yes / offered a time / "call me"). Keep going UNLIMITED
  (Tal, 2026-11-09), spacing out (~every 4-5 days), until they BOOK, hard-decline, or disqualify.
- `sequence`: vaguer prior interest ("happy to chat") or unknown. STOP AFTER TOUCH 3 (Tal, 2026-11-09,
  tightened from the old "4 touches then NURTURE"). Touch 3 IS the breakup ("should I close your
  file?", the highest-reply touch), so sequence leads get touches 1, 2, then a breakup as touch 3.
  If still silent after touch 3 -> status DROPPED (not NURTURE). Do not keep emailing low-signal
  warm-CRM leads past a breakup.

## Triage / status moves (update the tracker every time)
- Any genuine reply -> status REPLIED; work it through the qualification gate (site + pricing before
  proposing a time; price tiers are $2k/$6k/$12k per month, lead with $2k if asked).
- Hard no / opt-out -> status DECLINED, mirror email to booked_leads.txt, stop.
- `sequence` lead with no reply after touch 3 (the breakup) -> status DROPPED (Tal, 2026-11-09).
  Stop. (This replaces the old "touch 4 then NURTURE" rule for sequence leads.)
- CASE-STUDY / reference clients are NOT cold re-engage targets. Kanduai (ariel@kanduai.com) is a KSW
  case study: do NOT send it the re-engage sequence; left for Tal to confirm (flagged 2026-11-09).
- Booked -> status BOOKED + booked_leads.txt.
- CLIENT -> never contact.

## Daily mechanics (run inside the daily re-engagement wave trigger)
1. Query the tracker for leads due today: status AWAITING (or NURTURE whose monthly touch is due) and
   next_touch_due <= today.
2. For each, compose the right touch (by touch_count and tier), send from tal@ksw.solutions (cc tal),
   then update the tracker: touch_count += 1, next_touch_due = date_contacted + next gap (or +30d for
   nurture), last_action/updated.
3. THEN send new leads from the re-engagement CSV, up to a combined daily cap of ~15-20 sends to
   protect ksw.solutions deliverability. Overdue follow-ups take priority over new names.
4. Addresses stored "(verify)" (Tier1 shorthand) must be confirmed from Gmail Sent before re-sending.
