# Build: /whats-next skill

Run `/work` on the implementation plan for the /whats-next skill.

The plan is at `docs/plans/2026-04-07-003-feat-whats-next-skill-plan.md` — read it fully before starting.

No feature branch needed — this is a new skill in a new directory, no risk to existing functionality. Work directly on main.

## Key context

- This is the third skill in the strategy toolkit, alongside `/concept` and `/strategy` which are already built
- The primary references for conventions are `plugins/command-module/skills/concept/SKILL.md` and `plugins/command-module/skills/strategy/SKILL.md` — match their structure closely
- `/capture` is a project-level command (`.claude/commands/capture.md`), not a plugin skill — treat as an external dependency
- Run `bun test tests/frontmatter.test.ts` after creating the SKILL.md to validate frontmatter
- Run `bun run release:validate` after updating README.md to verify plugin metadata consistency
