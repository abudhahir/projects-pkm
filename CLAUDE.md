# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A personal knowledge-management repository for Claude Code plugin skills, handbooks, and the `ecc-universal` npm package (`packages/everything-claude-code/`). The primary content is a curated collection of reusable SKILL.md files, agents, hooks, and commands.

## Commands (packages/everything-claude-code)

```bash
# Run all tests
node tests/run-all.js

# Run individual test files
node tests/run-all.js
node tests/lib/utils.test.js
node tests/lib/package-manager.test.js
node tests/hooks/hooks.test.js

# Lint (ESLint + markdownlint)
npm run lint

# Full validation suite (agents, commands, rules, skills, hooks, manifests, paths, catalog)
npm test

# Coverage (80% minimum, all scripts)
npm run coverage
```

Node >=18 required.

## Architecture

### skills-src/ — Grouped personal skill library

Each skill now lives in a grouped source tree and follows this layout:

```
skills-src/group-name/
└── skills/
    └── skill-name/
        ├── SKILL.md          # Required. YAML frontmatter + lean body (1500-2000 words max)
        ├── references/       # Detailed docs loaded by Claude on demand
        ├── examples/         # Working, copy-ready code samples
        ├── scripts/          # Executable utilities (bash/python)
        └── assets/           # Template files used in output (not loaded into context)
```

`SKILLS/index.md` remains as a compatibility index into the grouped `skills-src/` tree.

**SKILL.md frontmatter** controls auto-selection — the `description` must use third-person with concrete trigger phrases:
```yaml
---
name: skill-name
description: This skill should be used when the user asks to "create X", "configure Y"...
version: 0.1.0
---
```

**Body writing style**: imperative/infinitive form only (`Configure the server.`, not `You should configure...`). Detailed content belongs in `references/`, not the body — keep the body lean so context load stays small.

### packages/everything-claude-code — Published npm package (`ecc-universal`)

Production-ready Claude Code configs distributed via npm. Key subdirectories:

- `agents/` — Subagent `.md` files with YAML frontmatter (`name`, `description`, `model`, `color`, `tools`)
- `skills/` — Workflow skills consumed by Claude Code
- `commands/` — Slash commands invoked as `/command-name`
- `hooks/hooks.json` — Event-driven automations (PreToolUse, PostToolUse, Stop, SessionStart, etc.)
- `rules/` — Always-applied coding standards and security guidelines
- `mcp-configs/` — MCP server connection configs
- `scripts/` — Node.js utilities for install, validation, hooks, and orchestration
- `tests/` — Test suite for scripts and utilities

**Agent format**: Markdown with YAML frontmatter. `description` field drives triggering — include 2-4 `<example>` blocks. `model: inherit` unless a specific capability is required. Restrict `tools` to minimum needed.

**Command format**: Markdown files that become Claude's instructions when invoked. Use `$ARGUMENTS`, `$1`/`$2` for positional args, `@file` for file injection, `!`backtick`` for inline bash, and `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths.

**Hook format** in `hooks/hooks.json` wraps events:
```json
{ "hooks": { "PreToolUse": [...], "Stop": [...] } }
```
Two hook types: `"type": "prompt"` (LLM-driven, context-aware) and `"type": "command"` (deterministic bash).

### skills-src/ domain coverage

The skill library spans: Java/Spring Boot, Kotlin, architecture diagramming (Mermaid, draw.io, C4, Excalidraw), MCP integration, agent/command/hook/skill development, TDD, AWS/Azure integration, API documentation, and visual explanation workflows.

## Key Conventions

- File naming: lowercase with hyphens (`python-reviewer.md`, `tdd-workflow.md`)
- Skill descriptions use third-person; agent system prompts use second-person (`You are...`)
- Progressive disclosure: SKILL.md ≤ 5k words; push detail to `references/`
- `packages/everything-claude-code/` has its own CLAUDE.md with additional package-specific notes
