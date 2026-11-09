# Permissions / autonomous sending (do not re-litigate this)

This was figured out, lost, and re-figured out twice (week of 2026-11-02 and
again 2026-11-09). Writing it down so it stops recurring.

## The settled answer
- **Keep the cloud session on AUTO mode** (the mode dropdown next to the prompt
  box: Auto = "Claude handles permission decisions"). In Auto, Claude runs the
  Explee API calls (curl) and the Gmail sends WITHOUT a permission pop-up. This
  is what makes the overnight routines (reply-check, SDR handoff, blog drip) send
  hands-off.
- **Do NOT switch to Default** (it prompts on every send, so an overnight send
  sits unanswered for hours) and **do NOT switch to "Accept edits"** (that only
  auto-accepts file edits, not sends; sends would still prompt).

## Myths to stop repeating
- "Auto denies email sends / real-world transactions" — FALSE as observed
  2026-11-09: in Auto, the Explee reply curl and mcp__Gmail__send_message both
  go through automatically (e.g. the Paul Walker / EtherAI close went out with no
  tap). The old note claiming Auto auto-denies sends was wrong; do not act on it
  and do not tell Tal to leave Auto because of it.
- The real overnight blocker was (a) the session being in a prompting mode, and
  (b) container/worker restarts interrupting a turn mid-send. (b) is infra, not
  permissions; the routine just completes on its next fire.

## Optional hardening (Claude CANNOT do this; only Tal can)
Cloud sessions ignore `bypassPermissions`/`dontAsk` in settings. The only
file-based lever is `permissions.allow` in a committed `.claude/settings.json`
(a one-repo session reads it). Claude is HARD-BLOCKED from creating or editing
that file ("Self-Modification" denial) even with Tal approving in chat, so if we
ever want it, TAL adds it from a desktop editor. It is NOT required while the
session stays on Auto. Suggested contents if ever wanted:

    {
      "permissions": {
        "allow": [
          "Bash(curl:*)",
          "Bash(python3:*)",
          "Bash(git add:*)",
          "Bash(git commit:*)",
          "Bash(git push:*)",
          "Bash(git fetch:*)",
          "Bash(git reset:*)",
          "mcp__Gmail__send_message",
          "mcp__Gmail__search_threads",
          "mcp__Gmail__get_thread"
        ]
      }
    }
