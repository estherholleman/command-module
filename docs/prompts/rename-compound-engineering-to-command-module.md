# Refactor: rename plugins/compound-engineering references to plugins/command-module

The plugin directory was renamed from `plugins/compound-engineering/` to `plugins/command-module/` at some point, but ~95 references across the codebase still point to the old path. This breaks `bun run release:validate` and leaves stale paths in docs, tests, and CI.

## What to do

Replace all filesystem path references from `plugins/compound-engineering` to `plugins/command-module` across the repo.

**Important distinctions:**
- `plugins/compound-engineering` as a **filesystem path** -> change to `plugins/command-module`
- `compound-engineering` as a **release component name** in types, display strings, and release-please config -> keep as-is (it's the logical release identity, not the directory name)
- The `.github/release-please-config.json` and `.github/.release-please-manifest.json` use `plugins/compound-engineering` as a **package path key** -> these must change to `plugins/command-module` since release-please uses them to match filesystem paths

## Files that need changes

### Runtime source (breaks release:validate)
- `src/release/metadata.ts` -- lines 106, 133, 134 hardcode `plugins/compound-engineering`
- `src/release/components.ts` -- lines 26, 185 hardcode the old path

### Release config
- `.github/release-please-config.json` -- package key `plugins/compound-engineering`
- `.github/.release-please-manifest.json` -- version key `plugins/compound-engineering`

### Tests (will fail with old paths)
- `tests/extract-commands-normalize.test.ts` -- import path
- `tests/release-components.test.ts` -- test fixture paths
- `tests/release-preview.test.ts` -- test fixture path
- `tests/release-config.test.ts` -- test fixture paths
- `tests/review-skill-contract.test.ts` -- many readRepoFile paths
- `tests/frontmatter.test.ts` -- plugin path

### CI
- `.github/workflows/deploy-docs.yml` -- path filter and checkout path

### Docs (AGENTS.md, README.md, solutions, plans)
- `AGENTS.md` -- plugin path references
- `README.md` -- install examples, alias examples, link to plugin README
- `PRIVACY.md` -- path reference
- Multiple files under `docs/solutions/` and `docs/plans/` -- path references in historical docs

## Verification

After making changes:
1. `bun test` -- all tests should pass
2. `bun run release:validate` -- should no longer crash with ENOENT
3. `grep -r 'plugins/compound-engineering' --include='*.ts' --include='*.json' --include='*.yml'` -- should return nothing (docs may still have historical references, that's fine)

## Key context

- `bun` needs to be run via `npx --yes bun` in this environment
- Run `npx --yes bun install` first if dependencies aren't installed
- The plugin's internal name is still "compound-engineering" (in plugin.json `name` field, release component types, etc.) -- only the filesystem *directory path* changed
