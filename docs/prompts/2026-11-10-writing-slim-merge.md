# Merge: slim command-module branch

## What to do

Land the slimmed plugin. The branch `feat/writing-foundations-slim` (worktree at `/Users/esther/prog/command-module-writing-slim`) is rebased and tested but not merged or pushed. First ask Esther how to land it: merge locally, push, or open a PR. Then do that and remove the extra worktree.

## Key context

- The branch has two commits on top of `codex/safe-clock-reporting`. One gives `writing-foundations` a condensed drafting card that loads about 5k words instead of 13–20k. The other (`refactor!`, a breaking change) moves 12 unused skills and 3 agents into `attic/`, so the plugin goes from 36 agents and 53 skills to 33 and 41.
- `codex/safe-clock-reporting` (two clock fixes, pushed to origin) is not on main yet. Merging the slim branch into main also brings those fixes in, so land `codex/safe-clock-reporting` first or together.
- A safety copy of the pre-rebase branch is kept as `backup/writing-foundations-slim-pre-rebase`. Delete it after the merge.
- Tests on the rebased branch: `bun test` 482 pass, plugin hook tests 74 pass. `bun run release:validate` reports count drift in the manifests, which already existed before the rebase. Release automation owns those counts, so don't hand-bump them.
- After the merge, the PostToolUse sync hook rsyncs `/Users/esther/prog/command-module/plugins/command-module/` with `--delete` into the installed plugin cache, so the parked skills disappear from new sessions.
- Separate from this repo: a new auto-handoff hook in `~/.claude/hooks` (`handoff-timer.py`, tests in `test_handoff_timer.py`) writes a handoff after 50 quiet minutes, and the auto-wrap now runs at 55 (`IDLE_WRAP_MINUTES`). It is live and fired correctly in its first real run. No follow-up is needed unless it misbehaves.

## Out of scope

- Restoring any parked component, and changing release-owned versions or counts.
