# Command Module — Plugin Inventory

## Agents

### Design

| Agent | Purpose |
|---|---|
| `design-implementation-reviewer` | Compare live UI against Figma designs, provide detailed feedback on discrepancies |
| `design-iterator` | Iterative screenshot-analyze-improve cycles — takes a screenshot, analyzes what's off, implements fixes, repeats N times |
| `figma-design-sync` | Auto-detect and fix visual differences between a web implementation and its Figma design |

### Document Review

| Agent | Purpose |
|---|---|
| `adversarial-document-reviewer` | Challenge premises, surface unstated assumptions, stress-test decisions in planning docs |
| `coherence-reviewer` | Check internal consistency, contradictions, and terminology drift |
| `design-lens-reviewer` | Flag missing design decisions, interaction states, and AI slop risk |
| `feasibility-reviewer` | Reality-check whether proposed technical approaches will survive contact with production |
| `product-lens-reviewer` | Challenge problem framing and scope decisions from a product perspective |
| `scope-guardian-reviewer` | Guard against unjustified complexity and scope creep |
| `security-lens-reviewer` | Evaluate planning documents for security gaps at the plan level |

### Research

| Agent | Purpose |
|---|---|
| `best-practices-researcher` | Synthesize external best practices, documentation, and examples for any technology or framework |
| `framework-docs-researcher` | Gather comprehensive documentation for frameworks and libraries in your project |
| `git-history-analyzer` | Archaeological analysis of git history — trace code evolution, identify contributors and patterns |
| `issue-intelligence-analyst` | Fetch and analyze GitHub issues to surface recurring themes and pain patterns |
| `learnings-researcher` | Search `docs/solutions/` for relevant past solutions filtered by frontmatter metadata |
| `repo-research-analyst` | Research repository structure, conventions, issue patterns, and contribution guidelines |

### Review

| Agent | Purpose |
|---|---|
| `adversarial-reviewer` | Construct failure scenarios to break implementations across component boundaries |
| `api-contract-reviewer` | Detect breaking API contract changes and versioning issues |
| `architecture-strategist` | Analyze code changes for architectural pattern compliance and system design alignment |
| `cli-agent-readiness-reviewer` | Review CLI source code for AI agent readiness using a severity-based rubric |
| `code-simplicity-reviewer` | Final review pass for YAGNI enforcement — ruthlessly simplify while maintaining functionality |
| `correctness-reviewer` | Find logic errors, edge cases, state management bugs, and intent mismatches |
| `data-migrations-reviewer` | Review schema changes and data transformations for integrity and migration safety |
| `maintainability-reviewer` | Spot premature abstraction, dead code, coupling, and unclear naming |
| `pattern-recognition-specialist` | Identify design patterns, anti-patterns, naming conventions, and code duplication |
| `performance-reviewer` | Review database queries, loops, caching, and I/O-intensive paths for performance issues |
| `project-standards-reviewer` | Audit changes against the project's own CLAUDE.md and AGENTS.md standards |
| `reliability-reviewer` | Review error handling, retries, circuit breakers, and failure modes |
| `schema-drift-detector` | Detect unrelated schema changes sneaking into PRs |
| `security-reviewer` | Find exploitable vulnerabilities — injection, auth/authz bypasses, exposed secrets |
| `testing-reviewer` | Identify test coverage gaps, weak assertions, and brittle tests |

### Workflow

| Agent | Purpose |
|---|---|
| `bug-reproduction-validator` | Systematically reproduce and validate bug reports step by step |
| `pr-comment-resolver` | Evaluate and resolve a single PR review thread — reads the comment, implements the fix, reports back |
| `spec-flow-analyzer` | Analyze specifications and plans for user flow completeness and missing edge cases |

---

## Skills

### Core Workflow

| Skill | Invoke | What it does |
|---|---|---|
| **Brainstorm** | `/brainstorm` | Collaborative dialogue to explore requirements and approaches before committing to a plan. Produces a requirements document. Use when the request is vague, ambitious, or has multiple valid interpretations. |
| **Implementation Plan** | `/implementation-plan` | Transform a feature description or requirements doc into a structured implementation plan grounded in repo patterns and research. Captures approach, boundaries, files, dependencies, risks — not code. |
| **Work** | `/work` | Execute a plan efficiently. Picks up where planning left off, writes code, runs tests, and finishes features. |
| **Work (Beta)** | `/work-beta` | Same as /work but with experimental Codex delegation mode for token-conserving code implementation. |
| **Code Review** | `/code-review` | Multi-agent code review using tiered persona agents with confidence gating and merge/dedup. Run before creating a PR. |
| **Compound** | `/compound` | Document a recently solved problem as a categorized learning in `docs/solutions/` so future sessions can find it. |
| **Compound Refresh** | `/compound-refresh` | Audit and refresh stale learnings in `docs/solutions/`. Use after refactors, migrations, or when a retrieved learning feels outdated. |
| **Ideate** | `/ideate` | Generate and critically evaluate grounded improvement ideas for the current project. Good for "what should I work on next?" moments. |
| **LFG** | `/lfg` | Full autonomous engineering workflow — end-to-end from understanding to implementation. |
| **SLFG** | `/slfg` | Same as LFG but uses swarm mode for parallel agent execution. |

### Git

| Skill | Invoke | What it does |
|---|---|---|
| **Commit** | `/git-commit` | Create a well-structured commit message that follows repo conventions. Handles staging and message formatting. |
| **Commit + Push + PR** | `/git-commit-push-pr` | Go from working changes to an open pull request in one step. Produces PR descriptions that scale in depth with complexity. Can also refresh an existing PR description. |
| **Clean Gone Branches** | `/git-clean-gone-branches` | Delete local branches whose remote tracking branch no longer exists. Also cleans up associated worktrees. |
| **Worktree** | `/git-worktree` | Manage Git worktrees for isolated parallel development — create, list, switch, and clean up. |

### Bug & PR Resolution

| Skill | Invoke | What it does |
|---|---|---|
| **Reproduce Bug** | `/reproduce-bug` | Systematically reproduce and investigate a bug from a GitHub issue. Uses logs, console inspection, and browser screenshots. |
| **Resolve PR Feedback** | `/resolve-pr-feedback` | Evaluate PR review comments for validity, then fix issues in parallel. |
| **Todo Create** | `/todo-create` | Create durable work items in the file-based todo system (`todos/` directory). |
| **Todo Resolve** | `/todo-resolve` | Batch-resolve approved todos using parallel processing. |
| **Todo Triage** | `/todo-triage` | Interactively review, prioritize, and categorize pending todos. |

### Frontend & Design

| Skill | Invoke | What it does |
|---|---|---|
| **Frontend Design** | `/frontend-design` | Build web interfaces with genuine design quality — not generic AI aesthetics. Covers composition, typography, color, motion, and copy. Detects existing design systems and respects them. Verifies results via screenshots. |
| **Gemini Image Gen** | `/gemini-imagegen` | Generate and edit images using Google's Gemini API. Text-to-image, style transfers, logos with text, stickers, product mockups, multi-turn refinement. |

### Browser & Automation

| Skill | Invoke | What it does |
|---|---|---|
| **Agent Browser** | `/agent-browser` | CLI-based browser automation using Vercel's agent-browser. Navigate pages, fill forms, click buttons, take screenshots, scrape data, test web apps — all from the terminal. Alternative to Playwright that's designed for agent use. |
| **Test Browser** | `/test-browser` | Run browser tests on pages affected by the current PR or branch. |
| **Test Xcode** | `/test-xcode` | Build and test iOS apps on simulator using XcodeBuildMCP. |

### Agent & Skill Development

| Skill | Invoke | What it does |
|---|---|---|
| **Agent-Native Architecture** | `/agent-native-architecture` | Design applications where agents are first-class citizens — MCP tools, self-modifying systems, agent-in-the-loop patterns. |
| **Agent-Native Audit** | `/agent-native-audit` | Run a scored audit of how well an app supports agent operation. |
| **Orchestrating Swarms** | `/orchestrating-swarms` | Guide for coordinating multi-agent swarms — parallel reviews, pipeline workflows, task queues, divide-and-conquer patterns. |

### Utilities

| Skill | Invoke | What it does |
|---|---|---|
| **Changelog** | `/changelog` | Generate an engaging changelog from recent merges to main. |
| **Deploy Docs** | `/deploy-docs` | Validate and prepare documentation for GitHub Pages deployment. |
| **Feature Video** | `/feature-video` | Record a video walkthrough of a feature and embed it in a PR description. |
| **Onboarding** | `/onboarding` | Generate `ONBOARDING.md` to help new contributors understand the codebase. |
| **Claude Permissions Optimizer** | `/claude-permissions-optimizer` | Reduce permission prompt fatigue by analyzing session history and auto-allowlisting safe commands. |
| **Rclone** | `/rclone` | Upload and sync files to S3, Cloudflare R2, Backblaze B2, Google Drive, Dropbox, or any S3-compatible storage. |
| **Document Review** | `/document-review` | Review a requirements or plan document using parallel persona agents that surface role-specific issues. |
| **Setup** | `/setup` | Placeholder for future project-level workflow configuration. |

---

## MCP Servers

| Server | Type | What it does |
|---|---|---|
| **Context7** | HTTP | Look up framework and library documentation on demand. Covers 100+ frameworks (React, Next.js, Tailwind, Django, FastAPI, Express, etc.). |
