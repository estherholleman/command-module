---
title: "launchd replaces cron for sleep-aware periodic jobs on macOS"
date: 2026-04-25
problem_type: developer_experience
category: developer-experience
component: scheduling
root_cause: cron_silent_skip_on_sleep
resolution_type: tool_replacement
severity: high
tags:
  - macos
  - launchd
  - cron
  - scheduling
  - per-session-clocks
  - time-tracking
symptoms:
  - "Periodic job scheduled via cron at 20:00 silently skipped on days when the Mac was asleep at 20:00"
  - "Stale state from missed run blocked the next day's automation across multiple Claude conversations"
  - "Tracking for an entire working day was lost because cron never caught up"
root_cause_detail: "cron's `0 20 * * * cmd` semantics: if the system is asleep, off, or otherwise unavailable when the time arrives, the job is skipped. cron does not catch up on wake. macOS sleeps frequently — closing the lid, idle sleep, or a downed display — making cron the wrong tool for daily personal-Mac jobs."
solution_summary: "Use a launchd LaunchAgent with `StartCalendarInterval { Hour=20, Minute=0 }`. Per Apple's `launchd.plist(5)` man page: 'Unlike cron which skips job invocations when the computer is asleep, launchd will start the job the next time the computer wakes up.' Multiple missed intervals coalesce into one run on wake — fine for idempotent sweeps. Install via modern launchctl commands (`bootstrap`/`bootout`/`enable`); the older `load`/`unload` are deprecated since macOS 10.11."
key_insight: "Cron's quiet skip is the primary failure mode for daily jobs on a Mac that sleeps. Even if the job is idempotent and the data window is recoverable, the silent failure trains the user to distrust the automation and gives no signal that anything went wrong. Replacing the trigger with launchd flips the failure mode from 'silent skip' to 'next-wake catch-up' without changing the job logic."

files_changed:
  - "~/.claude/hooks/auto-close-clock.py (multi-file iterator)"
  - "~/Library/LaunchAgents/com.esther.auto-close-clock.plist (new)"
  - "plugins/command-module/scripts/install-auto-close-launchagent.sh (new)"
  - "crontab (legacy auto-close-clock.py entry removed; claude-configs/sync.sh entry preserved)"
---

## The failure

20:00 cron job to sweep stale time-tracking clocks. On 2026-04-23, the Mac was asleep at 20:00; the job was silently skipped. The next morning's auto-clock-in saw a stale clock from the previous evening and exited early on every Claude Code conversation that day. Result: an entire day of `portfoliostrategyframework` work went unrecorded.

## Why cron is wrong for personal Macs

`cron` runs jobs at exact wall-clock times. If the system isn't running at that instant — sleep, hibernate, off, lid closed, machine in another timezone — the job is skipped. There's no notification, no log, no retry on wake. For long-running servers this is fine; for laptops that sleep many hours per day, it's a quiet correctness hole.

## What launchd gives you

A LaunchAgent with `StartCalendarInterval` honors the next-wake guarantee:

```xml
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key><integer>20</integer>
  <key>Minute</key><integer>0</integer>
</dict>
```

Apple's `launchd.plist(5)` (verified 2026-04-25):

> Unlike cron which skips job invocations when the computer is asleep, launchd will start the job the next time the computer wakes up. If multiple intervals transpire before the computer is woken, those events will be coalesced into one event upon wake from sleep.

Coalesced firings matter: if the laptop was off for three days, launchd runs the job once on wake, not three times. For idempotent sweeps that reconstruct end-times from each item's own timestamp, one catch-up run is the right amount.

## The install pattern

1. Write the plist to `~/Library/LaunchAgents/<reverse-dns-label>.plist`. Owner stays as the user. `chmod 644`. Use absolute paths in `ProgramArguments` — relative paths silently fail.
2. Use the modern launchctl verbs: `launchctl bootstrap gui/$(id -u) <plist>` and `launchctl enable gui/$(id -u)/<label>`. `load`/`unload` have been deprecated since macOS 10.11 but still work; `bootstrap`/`bootout` is the documented current API.
3. After installing, `launchctl print gui/$(id -u)/<label>` shows state, next-firing time, and the live program arguments. Use this to verify the install — not just `launchctl list`.

## Top three silent-failure pitfalls

| Symptom | Cause |
|---|---|
| `bootstrap` succeeds but agent never fires | System Settings → General → Login Items & Extensions → "Allow in the Background" toggled off (Sonoma+). The toggle is per-app/per-shell and silently overrides launchctl's enable state. |
| `bootstrap` succeeds but program path errors at runtime | `ProgramArguments` contained a relative path or `~`. launchd does not expand `~`; specify `/usr/bin/python3` and the absolute hook path. |
| In-place plist edit had no effect | Editing a plist while the agent is loaded does nothing. Always `bootout` then `bootstrap` after edits. The install script idempotently does this on every run. |

## When NOT to switch from cron

- Server-grade always-on hardware where cron's wall-clock semantics are a feature.
- Jobs that need to fire exactly at the named time and skip otherwise (regulatory or coordination jobs where a delayed run is wrong).
- System-wide services across multiple users — those want LaunchDaemons, not LaunchAgents.

## Installation entry point

`plugins/command-module/scripts/install-auto-close-launchagent.sh`. Idempotent. Prompts before editing crontab. Prints next-firing timestamp on success.

## Sources

- Apple `launchd.plist(5)` — "If multiple intervals transpire before the computer is woken, those events will be coalesced into one event upon wake from sleep."
- Apple `launchctl(1)` — `bootstrap`/`bootout` documented as the current API; `load`/`unload` flagged as deprecated since 10.11.
- Apple Developer documentation on `Login Items and Background Tasks` for the Sonoma+ user-toggle issue.
