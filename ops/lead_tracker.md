# Lead tracker: OPEN / pending pipeline

Purpose: every lead we have CONTACTED and not yet closed, so none get dropped.
- `ops/booked_leads.txt` = CLOSED leads (booked / declined / dead). This file = OPEN pipeline.
- Update this on every reply-check and re-engagement wave: move a lead to the right status, and
  when it closes (books/declines/dead) add it to booked_leads.txt and mark it CLOSED here.

## STORAGE NOTE (why this file is only part of the picture)
The big re-engagement batches (18 Gmail Tier-1 on 2026-11-01 + 15 wave-1 on 2026-11-02) are from
Tal's UPLOADED CRM list. Committing those contacts' PII to this public GitHub repo is blocked by a
safety guardrail, so they are NOT in this committed file. They live in the delivered master CSV
(lead_tracker_master_<date>.csv, sent to Tal) and are rebuilt from the uploaded CSV. RECOMMENDED FIX:
move the whole tracker to a Google Sheet (durable, Tal-owned, not in the repo, survives container
recycles, updatable by Claude). Ask Tal to green-light that and it becomes the single source of truth.

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
