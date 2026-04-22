# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Repository Purpose

This repository is a personal knowledge-management workspace focused on reusable skills, handbooks, prompts, and the published `ecc-universal` package in `packages/everything-claude-code/`.

Treat the repo as two related surfaces:
- `skills-src/` is the grouped skill source tree and `SKILLS/` keeps the compatibility index and helper files
- `packages/everything-claude-code/` is the distributable package with its own tests, manifests, and package-specific guidance

## Working Style

- Prefer concise, incremental edits over large rewrites
- Preserve existing structure and naming conventions
- Update the closest relevant documentation when behavior, workflows, or packaged assets change
- Avoid creating new top-level files unless the current structure has no suitable home
- For non-trivial changes, plan first; for repo-content changes, keep the plan proportional to the scope

## Primary Sources of Truth

Read the nearest applicable guidance before editing:
- Root `CLAUDE.md` for repo-wide context
- Package-local guidance inside `packages/everything-claude-code/` when working there
- Existing `SKILL.md`, `README.md`, command, hook, or rule examples before creating new ones

If guidance differs by scope, prefer the more local file.

## Repository Structure

### `skills-src/`
Grouped skill source tree. Skills now follow this shape:

```text
skills-src/group-name/
└── skills/
    └── skill-name/
        ├── SKILL.md
        ├── references/
        ├── examples/
        ├── scripts/
        └── assets/
```

Use this area for reusable instructions and supporting references. `SKILLS/index.md` remains as a compatibility index into this grouped structure.

### `packages/everything-claude-code/`
Published npm package for Everything Claude Code / ECC assets.

Typical contents include:
- `agents/` for agent definitions
- `skills/` for packaged workflow skills
- `commands/` for slash-command content
- `hooks/` for automation config
- `rules/` for always-applied guidance
- `scripts/` for validation and install utilities
- `tests/` for package verification

## Editing Conventions

### Skills

When creating or updating a skill:
- Keep `SKILL.md` lean; put deep detail in `references/`
- Use clear trigger-oriented descriptions in frontmatter
- Prefer imperative instructions over explanatory prose
- Reuse existing folder patterns instead of inventing new layouts
- Add examples or assets only when they materially improve reuse

### Docs and Handbooks

- Keep docs practical and scannable
- Prefer updating an existing handbook or README over duplicating content
- Cross-link related resources when it improves discovery
- Preserve the repo's mixed knowledge-base style rather than forcing product-doc structure

### Package Content

When editing `packages/everything-claude-code/`:
- Check for package-local conventions first
- Keep public package assets consistent with existing formats
- Avoid breaking manifest paths, generated indexes, or validation assumptions
- Update tests or fixtures when package behavior changes

## Validation

Choose verification based on the surface you changed.

### Docs-only or knowledge-only changes

Usually verify by:
- Checking formatting and internal consistency
- Confirming links, paths, and referenced files exist
- Reviewing neighboring examples for consistency

### Package changes

Run relevant commands from the repo guidance, especially in `packages/everything-claude-code/`:

```bash
node tests/run-all.js
npm run lint
npm test
npm run coverage
```

Run the smallest sufficient set first, then broader validation if the change affects shared behavior.

## Change Heuristics

Use a balanced workflow for this repository:
- Simple doc or metadata edits do not need heavy process
- Multi-file content changes should start with a brief plan
- Behavioral or script changes should include validation
- Changes to reusable skills should consider downstream users and examples
- Package changes should leave the repo in a releasable state

## Content Placement

Put new information in the most specific existing location:
- Skill implementation guidance near the relevant skill
- Package behavior and maintenance notes near the package
- General repo guidance in root docs
- Temporary notes should not become permanent top-level documentation

If a change affects both the knowledge base and the package, update both sides explicitly instead of leaving one stale.

## Practical Defaults

- Prefer small, reviewable diffs
- Keep filenames lowercase with hyphens when introducing new content
- Preserve ASCII unless a file already requires Unicode
- Do not remove or overwrite user-authored material without clear need
- When unsure where content belongs, prefer the nearest existing directory with the same pattern

## Success Criteria

A good change in this repository:
- fits the current information architecture
- keeps skills and docs easy to discover
- preserves package consistency
- includes verification appropriate to the scope
- leaves clearer guidance for the next agent
