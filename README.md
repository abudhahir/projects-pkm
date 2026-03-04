# project-pkm

A personal knowledge-management repository centered on **Claude Code plugin skills** and handbooks.

Most of the content lives under `NewAsus/`, which appears to be an Obsidian vault plus a curated set of skill packs for building and operating Claude Code extensions (agents, commands, hooks, MCP integrations, and related workflows).

## What this repository contains

- Skill authoring guidance (`skill-development`)
- Agent design guidance (`agent-development`)
- Slash command design guidance (`command-development`)
- Hook design and validation scripts (`hook-development`)
- MCP server integration guidance (`mcp-integration`)
- Handbook-style plugin packs (`handbook-*`)
- Additional markdown references and examples for each area

## Directory overview

```text
project-pkm/
+- .gitignore
+- NewAsus/
   +- HOME.base
   +- llms.txt/
   ¦  +- GitHub Copilot SDK.md
   +- .obsidian/
   +- SKILLS/
      +- agent-development/
      +- command-development/
      +- front-end/
      +- handbook-extras/
      +- handbook-git-worktree/
      +- handbook-glab/
      +- handbook-qa/
      +- handbook-structured-plan-mode/
      +- hook-development/
      +- mcp-integration/
      +- skill-development/
```

## Notes from analysis

- The repository is documentation-heavy: mainly `SKILL.md`, `README.md`, references, and examples.
- Several folders include helper scripts (mostly shell scripts) for validation/testing workflows.
- `NewAsus/.obsidian/` is currently versioned, indicating this is likely managed as a vault-first project.
- Some duplicate-named files exist such as `SKILL.md.md` in a few folders, which may be intentional backups or artifacts.

## How to use this repo

1. Browse `NewAsus/SKILLS/<topic>/SKILL.md` for core instructions.
2. Use each topic's `references/` for deeper guidance.
3. Use `examples/` and `scripts/` where provided to speed up implementation.
4. Treat handbook folders (`handbook-*`) as installable/packaged guidance sets.

## Suggested next cleanup (optional)

- Confirm whether `SKILL.md.md` files should be retained.
- Add per-skill README files where missing for faster discoverability.
- Decide whether `.obsidian/workspace.json` should remain tracked (it is often user-specific).
