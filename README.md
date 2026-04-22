# project-pkm

Personal knowledge base for AI-agent workflows, reusable skills, prompts, research notes, and the `ecc-universal` package workspace.

## Start Here

- [AGENTS.md](AGENTS.md) - repo guidance for coding agents
- [CLAUDE.md](CLAUDE.md) - repo context and working conventions
- [skills-src/index.md](skills-src/index.md) - grouped index for the skill source tree
- [SKILLS/index.md](SKILLS/index.md) - compatibility index pointing at the grouped layout
- [packages/everything-claude-code/README.md](packages/everything-claude-code/README.md) - package workspace overview

## Repository Index

- [skills-src/](skills-src/) - grouped skill source tree in `skills-src/<group>/skills/<skill>` layout
- [SKILLS/](SKILLS/) - legacy index and helper files for the skill library
- [packages/everything-claude-code/](packages/everything-claude-code/) - packaged ECC assets, tests, docs, and configs
- [current/](current/) - current notes and short-lived working material
- [projects/](projects/) - experiments and small project workspaces
- [prompts/](prompts/) - reusable prompt assets
- [llms.txt/](llms.txt/) - LLM-oriented notes and collected references
- [Dicsovery/](Dicsovery/) - exploration material and collected discovery notes
- [HOME.base](HOME.base) - small base/home reference file

## skills-src Index

Core workflow and platform skills:
- [agent-development](skills-src/ai-agent-platform/skills/agent-development/) - agent structure and frontmatter patterns
- [command-development](skills-src/ai-agent-platform/skills/command-development/) - slash-command authoring patterns
- [hook-development](skills-src/ai-agent-platform/skills/hook-development/) - Claude Code hook design and validation
- [mcp-integration](skills-src/ai-agent-platform/skills/mcp-integration/) - MCP server integration patterns
- [skill-development](skills-src/ai-agent-platform/skills/skill-development/) - reusable skill authoring guidance
- [gitlab-ops](skills-src/ai-agent-platform/skills/gitlab-ops/) - GitLab operational workflows

Handbooks:
- [handbook-git-worktree](skills-src/handbooks/skills/handbook-git-worktree/) - multi-branch worktree workflows
- [handbook-glab](skills-src/handbooks/skills/handbook-glab/) - GitLab CLI usage
- [handbook-qa](skills-src/handbooks/skills/handbook-qa/) - QA and browser automation workflows
- [handbook-structured-plan-mode](skills-src/handbooks/skills/handbook-structured-plan-mode/) - structured planning workflow
- [handbook-extras](skills-src/handbooks/skills/handbook-extras/) - extra tools and experimental patterns

Architecture and documentation:
- [architecture-patterns](skills-src/architecture-docs/skills/architecture-patterns/) - system design patterns
- [architecture-documenter](skills-src/architecture-docs/skills/architecture-documenter/) - architecture writeups
- [api-documentation](skills-src/architecture-docs/skills/api-documentation/) - API documentation guidance
- [api-reference-documentation](skills-src/architecture-docs/skills/api-reference-documentation/) - reference-style API docs
- [documentation-generator](skills-src/architecture-docs/skills/documentation-generator/) - documentation generation workflows
- [document-writer](skills-src/architecture-docs/skills/document-writer/) - general writing support
- [markdown-documentation](skills-src/architecture-docs/skills/markdown-documentation/) - Markdown documentation patterns
- [visual-explainer](skills-src/architecture-docs/skills/visual-explainer/) - visual technical explanations

Diagramming and visual tooling:
- [diagram](skills-src/diagramming-visualization/skills/diagram/) - general diagram workflows
- [diagram-generation](skills-src/diagramming-visualization/skills/diagram-generation/) - generated diagram workflows
- [c4-architecture](skills-src/diagramming-visualization/skills/c4-architecture/) - C4-style architecture diagrams
- [draw-io](skills-src/diagramming-visualization/skills/draw-io/) - draw.io diagram support
- [drawio-logical-diagrams](skills-src/diagramming-visualization/skills/drawio-logical-diagrams/) - logical diagram patterns
- [excalidraw-diagram-generator](skills-src/diagramming-visualization/skills/excalidraw-diagram-generator/) - Excalidraw assets and flows
- [mermaid](skills-src/diagramming-visualization/skills/mermaid/) / [mermaid-diagrams](skills-src/diagramming-visualization/skills/mermaid-diagrams/) / [beautiful-mermaid](skills-src/diagramming-visualization/skills/beautiful-mermaid/) - Mermaid authoring variants
- [mermaid-creator](skills-src/diagramming-visualization/skills/mermaid-creator/) / [mermaid-tools](skills-src/diagramming-visualization/skills/mermaid-tools/) / [mermaid-visualizer](skills-src/diagramming-visualization/skills/mermaid-visualizer/) - Mermaid generation and visualization tools
- [mermaid-diagram](skills-src/diagramming-visualization/skills/mermaid-diagram/) / [mermaid-flow-image](skills-src/diagramming-visualization/skills/mermaid-flow-image/) / [obsidian-mermaid](skills-src/diagramming-visualization/skills/obsidian-mermaid/) - diagram-specific Mermaid workflows
- [azure-architecture-diagram](skills-src/cloud/skills/azure-architecture-diagram/) / [azure-resource-visualizer](skills-src/cloud/skills/azure-resource-visualizer/) - Azure visual modeling

Java, Spring, and backend engineering:
- [java-fundamentals](skills-src/java/skills/java-fundamentals/) / [java-21](skills-src/java/skills/java-21/) / [java-generics](skills-src/java/skills/java-generics/) / [java-streams-api](skills-src/java/skills/java-streams-api/) - core Java topics
- [java-coding-standards](skills-src/java/skills/java-coding-standards/) / [java-testing](skills-src/testing-quality/skills/java-testing/) / [java-concurrency](skills-src/java/skills/java-concurrency/) - quality, tests, and concurrency
- [java-spring-boot](skills-src/spring-boot/skills/java-spring-boot/) / [spring-boot-3](skills-src/spring-boot/skills/spring-boot-3/) / [spring-boot-engineer](skills-src/spring-boot/skills/spring-boot-engineer/) - Spring Boot build patterns
- [spring-boot-crud-patterns](skills-src/spring-boot/skills/spring-boot-crud-patterns/) / [spring-boot-rest-api-standards](skills-src/spring-boot/skills/spring-boot-rest-api-standards/) / [spring-boot-openapi-documentation](skills-src/spring-boot/skills/spring-boot-openapi-documentation/) - REST and API patterns
- [spring-boot-dependency-injection](skills-src/spring-boot/skills/spring-boot-dependency-injection/) / [spring-boot-cache](skills-src/spring-boot/skills/spring-boot-cache/) / [spring-boot-actuator](skills-src/spring-boot/skills/spring-boot-actuator/) - runtime and framework patterns
- [spring-boot-event-driven-patterns](skills-src/spring-boot/skills/spring-boot-event-driven-patterns/) / [spring-boot-saga-pattern](skills-src/spring-boot/skills/spring-boot-saga-pattern/) / [microservices-patterns](skills-src/spring-boot/skills/microservices-patterns/) - eventing and microservices
- [springboot-security](skills-src/spring-boot/skills/springboot-security/) / [spring-boot-security-jwt](skills-src/spring-boot/skills/spring-boot-security-jwt/) / [spring-boot-resilience4j](skills-src/spring-boot/skills/spring-boot-resilience4j/) - security and resilience
- [springboot-tdd](skills-src/testing-quality/skills/springboot-tdd/) / [spring-boot-test-patterns](skills-src/testing-quality/skills/spring-boot-test-patterns/) / [springboot-verification](skills-src/testing-quality/skills/springboot-verification/) / [tdd](skills-src/testing-quality/skills/tdd/) / [dev-tdd](skills-src/testing-quality/skills/dev-tdd/) - TDD and verification workflows
- [jpa-patterns](skills-src/spring-boot/skills/jpa-patterns/) / [unit-test-application-events](skills-src/testing-quality/skills/unit-test-application-events/) - JPA and event testing
- [backend-patterns](skills-src/backend-ai/skills/backend-patterns/) / [kotlin-spring-boot](skills-src/backend-ai/skills/kotlin-spring-boot/) / [langchain4j-spring-boot-integration](skills-src/backend-ai/skills/langchain4j-spring-boot-integration/) / [spring-ai-mcp-server-patterns](skills-src/backend-ai/skills/spring-ai-mcp-server-patterns/) - backend and AI integration patterns
- [aws-rds-spring-boot-integration](skills-src/cloud/skills/aws-rds-spring-boot-integration/) / [azure-identity-java](skills-src/cloud/skills/azure-identity-java/) - cloud integration patterns

Other skill areas:
- [front-end](skills-src/frontend/skills/front-end/) - frontend-related material
- [pattern-detector](skills-src/architecture-docs/skills/pattern-detector/) - recurring-pattern identification
- [senior-architect](skills-src/architecture-docs/skills/senior-architect/) / [java-architect](skills-src/architecture-docs/skills/java-architect/) - architecture review perspectives
- [Art](skills-src/diagramming-visualization/skills/Art/) - miscellaneous creative material

## Package Workspace Index

Inside [packages/everything-claude-code/](packages/everything-claude-code/):
- [agents/](packages/everything-claude-code/agents/) - packaged agent definitions
- [skills/](packages/everything-claude-code/skills/) - packaged skills
- [commands/](packages/everything-claude-code/commands/) - slash commands
- [hooks/](packages/everything-claude-code/hooks/) - automation hooks
- [rules/](packages/everything-claude-code/rules/) - always-on rule sets
- [mcp-configs/](packages/everything-claude-code/mcp-configs/) - MCP connection configs
- [scripts/](packages/everything-claude-code/scripts/) - install and validation scripts
- [tests/](packages/everything-claude-code/tests/) - package verification
- [docs/](packages/everything-claude-code/docs/) - package docs and translations
- [examples/](packages/everything-claude-code/examples/) - usage examples
- [manifests/](packages/everything-claude-code/manifests/) / [schemas/](packages/everything-claude-code/schemas/) / [assets/](packages/everything-claude-code/assets/) - packaged metadata and assets
- [contexts/](packages/everything-claude-code/contexts/) / [plugins/](packages/everything-claude-code/plugins/) - harness-specific support files
- [AGENTS.md](packages/everything-claude-code/AGENTS.md) / [CLAUDE.md](packages/everything-claude-code/CLAUDE.md) / [.codex/AGENTS.md](packages/everything-claude-code/.codex/AGENTS.md) - package-local guidance

## Other Directories

- [current/github-copilot-sdk/](current/github-copilot-sdk/) - Copilot SDK notes and references
- [current/tasks.md](current/tasks.md) - lightweight working task list
- [projects/diagram-generator/](projects/diagram-generator/) - diagram-generator experiment
- [prompts/vis-expl/](prompts/vis-expl/) - visual explanation prompts for diff review, fact checking, slide generation, plan review, web diagrams, and project recap
- [llms.txt/MCP/](llms.txt/MCP/) - MCP-oriented LLM notes
- [llms.txt/research/](llms.txt/research/) - research notes
- [llms.txt/generatorss/](llms.txt/generatorss/) - collected generator-related links
- [Dicsovery/diagram-as-a-code/](Dicsovery/diagram-as-a-code/) - diagram-as-code exploration notes
- [Dicsovery/links/](Dicsovery/links/) - collected raw reference links and exports

## Validation

- Docs-only changes: check links, paths, and consistency
- Package changes: use the relevant checks in `packages/everything-claude-code/`

```bash
node tests/run-all.js
npm run lint
npm test
npm run coverage
```

## External Reference

- [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills)
