---
title: Preserve late-running clocks with report-only checks
date: 2026-11-09
category: integrations
---

# Preserve late-running clocks with report-only checks

## Cause

The manually created /ci clock had a valid start but omitted opened_at.
The installed 20:00 sweep classified it as legacy and removed it without a
timesheet row. The sweep also processed active conversations without checking
whether their work had ended, so format repair alone did not support late work.

## Change

- Retire fixed-time closure. The new com.esther.clock-check LaunchAgent runs at
  20:00 and writes reports/clock-check/latest.md and latest.json in Mission Control.
- Preserve every clock and all time records. Missing activity means unknown
  completion, not permission to close, infer time, or delete a record.
- The old label is disabled and unloaded. Both installed auto-close entry points
  and the old plist now point to report-only behavior.
- The compatibility installer backs up replaced files, rejects older destructive
  hook-source directories, generates a safe shim, and enables the report service
  before bootstrap so reinstalling a previously disabled job works.
- /ci uses a stable installed copy of scripts/clock-in.py, independent of the
  active source checkout branch: atomic exclusive publication, complete lifecycle
  fields, local-naive timestamps, and no overwrite of existing clocks.
- /co normalizes aware timestamps into local time before arithmetic.
- Installed Claude and Codex skill copies were explicitly synchronized. The newer
  live shared clock engines were not replaced with older staged copies.

Reports are saved locally; they do not themselves notify the user. Inspect the
report during reconciliation, and finish a session with its own /co or wrap-up.
Normal session hooks and wrap-up remain independent from the daily check.

## Verification

- 17 isolated standard-library tests passed under /usr/bin/python3 3.9.6.
  Coverage includes malformed and stale clocks, activity ordering, future dates,
  accrued-work anomalies, directory/read errors, offset/Z/DST conversion,
  concurrent creation, exact file preservation, repeat installation, and override
  rejection. Scheduling commands were mocked in installer tests.
- 499 Bun tests passed.
- New clocks passed in-memory legacy/heartbeat/span/finalization checks against
  both installed shared engines; no live finalizer was invoked.
- Real installed LaunchAgent ran once with exit code 0. Seven existing clocks and
  the existing timesheet were byte-identical before and after deployment/check.
- release:validate reports existing drift in four plugin/marketplace metadata
  files. The unchanged HEAD baseline reproduced the same failure and inventory;
  release-owned metadata was left untouched.
- No historical time entry was created, and no prior duration was inferred.

## Recovery and rollback

Deployment backups live under ~/Library/Application Support/ClockCheck/backups.
The original 20:00 job remains disabled. Stopping the report job is reversible
with launchctl disable and bootout for com.esther.clock-check. Restoring old
scripts/plists would restore destructive behavior and needs deliberate review.
The installer does not alter unrelated launch jobs or cron entries.
