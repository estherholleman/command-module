# Compounding Engineering Plugin

AI-powered development tools that get smarter with every use. Make each unit of engineering work easier than the last.

## Components

| Component | Count |
|-----------|-------|
| Agents | 36 |
| Skills | 45 |
| MCP Servers | 1 |

## Skills

### Core Workflow

The primary entry points for engineering work, invoked as slash commands:

| Skill | Description |
|-------|-------------|
| `/ideate` | Discover high-impact project improvements through divergent ideation and adversarial filtering |
| `/brainstorm` | Explore requirements and approaches before planning |
| `/implementation-plan` | Transform features into structured implementation plans grounded in repo patterns, with automatic confidence checking |
| `/code-review` | Structured code review with tiered persona agents, confidence gating, and dedup pipeline |
| `/work` | Execute work items systematically |
| `/distill` | Document solved problems to distill team knowledge |
| `/distill-refresh` | Refresh stale or drifting learnings and decide whether to keep, update, replace, or archive them |

### Git Workflow

| Skill | Description |
|-------|-------------|
| `git-clean-gone-branches` | Clean up local branches whose remote tracking branch is gone |
| `git-commit` | Create a git commit with a value-communicating message |
| `git-commit-push-pr` | Commit, push, and open a PR with an adaptive description; also update an existing PR description |
| `git-worktree` | Manage Git worktrees for parallel development |

### Workflow Utilities

| Skill | Description |
|-------|-------------|
| `/changelog` | Create engaging changelogs for recent merges |
| `/feature-video` | Record video walkthroughs and add to PR description |
| `/handoff` | Generate a self-contained starter prompt for a fresh conversation at workflow transition points |
| `/here-or-there` | Decide whether to continue inline or hand off; auto-routes to /handoff when a fresh conversation will help |
| `/reproduce-bug` | Reproduce bugs using logs and console |
| `/report-bug-ce` | Report a bug in the command-module plugin |
| `/resolve-pr-feedback` | Resolve PR review feedback in parallel |
| `/sync` | Sync Claude Code config across machines |
| `/test-browser` | Run browser tests on PR-affected pages |
| `/test-xcode` | Build and test iOS apps on simulator |
| `/onboarding` | Generate `ONBOARDING.md` to help new contributors understand the codebase |
| `/explain-pipeline` | Generate a grounded Markdown draft explaining how a data pipeline behaves (entry points, branches, fallbacks, gates), with file:line citations |
| `/todo-resolve` | Resolve todos in parallel |
| `/todo-triage` | Triage and prioritize pending todos |
| `/export-docx` | Convert markdown to DOCX with proofing reminder, discovers repo-specific conversion scripts |
| `todo-create` | File-based todo tracking system |

### Development Frameworks

| Skill | Description |
|-------|-------------|
| `agent-native-architecture` | Build AI agents using prompt-native architecture |
| `andrew-kane-gem-writer` | Write Ruby gems following Andrew Kane's patterns |
| `dhh-rails-style` | Write Ruby/Rails code in DHH's 37signals style |
| `dspy-ruby` | Build type-safe LLM applications with DSPy.rb |
| `frontend-design` | Create production-grade frontend interfaces |

### Review & Quality

| Skill | Description |
|-------|-------------|
| `claude-permissions-optimizer` | Optimize Claude Code permissions from session history |
| `document-review` | Review documents using parallel persona agents for role-specific feedback |
| `setup` | Reserved for future project-level workflow configuration; code review agent selection is automatic |

### Style

| Skill | Description |
|-------|-------------|
| `design-foundations` | Graphic design fundamentals (typography, color, composition, hierarchy) -- medium-agnostic visual knowledge base and critic |
| `writing-foundations` | Writing craft fundamentals (clarity, structure, voice, persuasion, audience) -- medium-agnostic writing knowledge base and critic |
| `/proof` | Review and edit prose for natural writing style, removing AI-typical patterns (English and Dutch) |

### Strategy

| Skill | Description |
|-------|-------------|
| `/concept` | Conceptual thinking partner using the reframe-react-sharpen pattern for sharpening ideas and strategic concepts |
| `/strategy` | Strategic PM for portfolio review, tension analysis, context curation, and thinking direction |
| `/whats-next` | Strategic execution advisor that translates concepts and decisions into task recommendations and prompt files |

### Automation & Tools

| Skill | Description |
|-------|-------------|
| `agent-browser` | CLI-based browser automation using Vercel's agent-browser |
| `gemini-imagegen` | Generate and edit images using Google's Gemini API |
| `orchestrating-swarms` | Comprehensive guide to multi-agent swarm orchestration |
| `rclone` | Upload files to S3, Cloudflare R2, Backblaze B2, and cloud storage |

### Beta / Experimental

| Skill | Description |
|-------|-------------|
| `/lfg` | Full autonomous engineering workflow |
| `/slfg` | Full autonomous workflow with swarm mode for parallel execution |

## Agents

Agents are specialized subagents invoked by skills — you typically don't call these directly.

### Review

| Agent | Description |
|-------|-------------|
| `agent-native-reviewer` | Verify features are agent-native (action + context parity) |
| `api-contract-reviewer` | Detect breaking API contract changes |
| `cli-agent-readiness-reviewer` | Evaluate CLI agent-friendliness against 7 core principles |
| `architecture-strategist` | Analyze architectural decisions and compliance |
| `code-simplicity-reviewer` | Final pass for simplicity and minimalism |
| `correctness-reviewer` | Logic errors, edge cases, state bugs |
| `data-integrity-guardian` | Database migrations and data integrity |
| `data-migration-expert` | Validate ID mappings match production, check for swapped values |
| `data-migrations-reviewer` | Migration safety with confidence calibration |
| `deployment-verification-agent` | Create Go/No-Go deployment checklists for risky data changes |
| `dhh-rails-reviewer` | Rails review from DHH's perspective |
| `julik-frontend-races-reviewer` | Review JavaScript/Stimulus code for race conditions |
| `kieran-rails-reviewer` | Rails code review with strict conventions |
| `kieran-python-reviewer` | Python code review with strict conventions |
| `kieran-typescript-reviewer` | TypeScript code review with strict conventions |
| `maintainability-reviewer` | Coupling, complexity, naming, dead code |
| `pattern-recognition-specialist` | Analyze code for patterns and anti-patterns |
| `performance-oracle` | Performance analysis and optimization |
| `performance-reviewer` | Runtime performance with confidence calibration |
| `reliability-reviewer` | Production reliability and failure modes |
| `schema-drift-detector` | Detect unrelated schema.rb changes in PRs |
| `security-reviewer` | Exploitable vulnerabilities with confidence calibration |
| `security-sentinel` | Security audits and vulnerability assessments |
| `testing-reviewer` | Test coverage gaps, weak assertions |
| `project-standards-reviewer` | CLAUDE.md and AGENTS.md compliance |
| `adversarial-reviewer` | Construct failure scenarios to break implementations across component boundaries |

### Document Review

| Agent | Description |
|-------|-------------|
| `coherence-reviewer` | Review documents for internal consistency, contradictions, and terminology drift |
| `design-lens-reviewer` | Review plans for missing design decisions, interaction states, and AI slop risk |
| `feasibility-reviewer` | Evaluate whether proposed technical approaches will survive contact with reality |
| `grounding-check` | Mechanically verify code-level claims in plans (file paths, function names, libraries) against the actual repo |
| `product-lens-reviewer` | Challenge problem framing, evaluate scope decisions, surface goal misalignment |
| `scope-guardian-reviewer` | Challenge unjustified complexity, scope creep, and premature abstractions |
| `security-lens-reviewer` | Evaluate plans for security gaps at the plan level (auth, data, APIs) |
| `adversarial-document-reviewer` | Challenge premises, surface unstated assumptions, and stress-test decisions |

### Research

| Agent | Description |
|-------|-------------|
| `best-practices-researcher` | Gather external best practices and examples |
| `framework-docs-researcher` | Research framework documentation and best practices |
| `git-history-analyzer` | Analyze git history and code evolution |
| `issue-intelligence-analyst` | Analyze GitHub issues to surface recurring themes and pain patterns |
| `learnings-researcher` | Search institutional learnings for relevant past solutions |
| `repo-research-analyst` | Research repository structure and conventions |

### Design

| Agent | Description |
|-------|-------------|
| `design-implementation-reviewer` | Verify UI implementations match Figma designs |
| `design-iterator` | Iteratively refine UI through systematic design iterations |
| `figma-design-sync` | Synchronize web implementations with Figma designs |

### Workflow

| Agent | Description |
|-------|-------------|
| `bug-reproduction-validator` | Systematically reproduce and validate bug reports |
| `lint` | Run linting and code quality checks on Ruby and ERB files |
| `pr-comment-resolver` | Address PR comments and implement fixes |
| `spec-flow-analyzer` | Analyze user flows and identify gaps in specifications |

### Docs

| Agent | Description |
|-------|-------------|
| `ankane-readme-writer` | Create READMEs following Ankane-style template for Ruby gems |
| `writing-style-editor` | Edit prose to remove AI-typical writing patterns and improve naturalness (English and Dutch) |

## MCP Servers

| Server | Description |
|--------|-------------|
| `context7` | Framework documentation lookup via Context7 |

### Context7

**Tools provided:**
- `resolve-library-id` - Find library ID for a framework/package
- `get-library-docs` - Get documentation for a specific library

Supports 100+ frameworks including Rails, React, Next.js, Vue, Django, Laravel, and more.

MCP servers start automatically when the plugin is enabled.

**Authentication:** To avoid anonymous rate limits, set the `CONTEXT7_API_KEY` environment variable with your Context7 API key. The plugin passes this automatically via the `x-api-key` header. Without it, requests go unauthenticated and will quickly hit the anonymous quota limit.

## Browser Automation

This plugin uses **agent-browser CLI** for browser automation tasks. Install it globally:

```bash
npm install -g agent-browser
agent-browser install  # Downloads Chromium
```

The `agent-browser` skill provides comprehensive documentation on usage.

## Installation

```bash
claude /plugin install command-module
```

## Known Issues

### MCP Servers Not Auto-Loading

**Issue:** The bundled Context7 MCP server may not load automatically when the plugin is installed.

**Workaround:** Manually add it to your project's `.claude/settings.json`:

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "x-api-key": "${CONTEXT7_API_KEY:-}"
      }
    }
  }
}
```

Set `CONTEXT7_API_KEY` in your environment to authenticate. Or add it globally in `~/.claude/settings.json` for all projects.

## Version History

See the repo root [CHANGELOG.md](../../CHANGELOG.md) for canonical release history.

## License

MIT
