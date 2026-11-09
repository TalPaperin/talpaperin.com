# Lead tracker: OPEN / pending pipeline

Purpose: every lead we have CONTACTED and not yet closed, so none get dropped.
- `ops/booked_leads.txt` = CLOSED leads (booked / declined / dead). This file = OPEN pipeline.
- Update this on every reply-check and re-engagement wave: move a lead to the right status, and
  when it closes (books/declines/dead) add it to booked_leads.txt and mark it CLOSED here.

## SOURCE OF TRUTH: the live tracker Artifact (Tal, 2026-11-03)
All leads are managed in the claude.ai Artifact "KSW Lead Tracker":
  https://claude.ai/artifact/XFXSMiu9bwe2rtkzJUyk1a
It is a published page backed by a shared database (the `leads` collection), private to Tal, NOT in
this repo (so the uploaded-CRM PII guardrail is a non-issue). Manage it with the ArtifactData tool
(get/list/query/set/update/batch) against that url.
MAINTENANCE RULE - do this every reply-check and every re-engagement wave:
- NEW contacted lead -> `set` a `leads` doc (id = email). Fields: name, company, email, source,
  status, context, last_action, next_step, date_contacted, updated.
- A lead REPLIES or advances -> `update` its status/last_action/next_step (+ updated date). Statuses:
  AWAITING, REPLIED, MET, BOOKED, DECLINED, DROPPED, CLIENT.
- A lead CLOSES (books/declines/dead) -> set status BOOKED/DECLINED/DROPPED here AND mirror to
  booked_leads.txt (the scan/handoff skip-list). Keep both in sync.
Seeded 2026-11-03 with 42 leads (33 re-engagements + Explee warm/closed). The uploaded-CRM contacts
live only here and in the delivered master CSV, never committed to the repo.
The table below is a lightweight mirror for Explee-sourced open leads; the Artifact is authoritative.

## Reply log (every reply, audit trail) -- `reply_log` collection in the SAME Artifact (Tal, 2026-11-09)
After Tal asked "are you logging ALL those replies", the raw every-reply log lives in the tracker
Artifact's `reply_log` collection (NOT the public repo: it holds prospect PII and the repo is public).
- One document per campaign, id `<Project>-<campaignId>` (e.g. `DealMentor-359966`), fields: project,
  campaign, count, by_class, and `replies` (array). Each reply: name, email, latest_reply_at,
  classification (engaged / decline / autoresponder / reply-other / vectorize-human), answered_by_us,
  body_excerpt. Backfilled 2026-11-09 with 434 replies across 20 campaigns (the full history).
- MAINTENANCE: every reply-check cycle, append any NEW human reply (not already in that campaign's
  doc) to the matching `reply_log/<Project>-<campaignId>` doc. Rebuild the full backfill with
  scratchpad `log_replies.py` (discovers all campaigns live, same classifier as scan.py).

## Explee-sourced open leads (committable here)
| Date | Source | Name | Company | Email | Status | Last action | Next step |
|---|---|---|---|---|---|---|---|
| 2026-11-03 | Explee TP 252219 | Allen Thrush | ContractorRush | allen@contractorrush.com | MET (showed on Zoom) | Joined the 11am ET call | Tal: log call outcome; book follow-up or close |
| 2026-11-02 | Explee TP 252222 | Jason McGinn | 4Infiniti (AI agency) | jason@4infiniti.agency | REPLIED - low intent | Sent positioning + call offer | Watch for reply; low priority (agency), do not chase hard |

## Explee Oct warm-never-booked, re-engaged (emails to pull from Explee if we want them row-by-row)
Shlomo Talitman, Moris Elkayam, Taylor Byington, John Wurch, Ori Yona, Oren Haimov.
These were re-engaged after the two-week review; none booked. Status: AWAITING / stale. If Tal wants
each tracked individually, pull their exact emails from the Explee threads and add rows above.
(Allen Thrush and Kelly Franko were from this same batch: Allen MET above; Kelly DECLINED in booked_leads.)
