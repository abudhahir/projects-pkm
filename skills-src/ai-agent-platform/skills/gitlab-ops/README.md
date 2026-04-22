# gitlab-ops

A Claude skill for managing GitLab entirely from the command line. It covers four domains — issue management, statistics & reporting, repository administration, and CI/CD operations — using `glab` (the official GitLab CLI) as the primary tool, with the GitLab REST API via `glab api` or `curl` as a fallback when `glab` doesn't expose a direct subcommand.

---

## Why this skill exists

Switching to a browser tab just to create an issue, check a pipeline, or rotate a CI variable interrupts your flow. This skill makes Claude your GitLab co-pilot at the terminal: it knows the right `glab` command for the task at hand, knows when to reach for the raw API instead, and can string together `jq` pipelines to generate real reports from GitLab data — all without you having to look anything up.

---

## Requirements

- **[glab](https://gitlab.com/gitlab-org/cli)** v1.40.0 or later — the official GitLab CLI
- **jq** — for JSON processing in statistics and bulk-operation patterns
- A GitLab personal access token with `api` and `write_repository` scopes (or OAuth login via `glab auth login`)
- GitLab 16.0 or later (glab's officially supported minimum)

### Quick install

```bash
# macOS / Linux (Homebrew)
brew install glab

# Debian / Ubuntu
sudo apt install glab

# Arch Linux
sudo pacman -S glab

# Authenticate (interactive — works for both gitlab.com and self-managed)
glab auth login

# Verify
glab auth status
```

---

## What it covers

### Issue Management

The full issue lifecycle from the terminal: creating issues with labels, milestones, assignees, and due dates in a single command; listing and filtering by state, label, author, or milestone; updating, closing, and bulk-operating on issues using shell loops; adding comments; managing labels and milestones; and the complete merge request workflow from `glab mr create --fill` through approval, merge, and branch cleanup. Cross-project group-level issue queries are handled via `glab api`.

### Statistics & Reporting

Patterns for turning raw GitLab API responses into actionable metrics: issue throughput and age distribution, MR cycle times (time from open to merge), pipeline pass/fail rates and average duration, the most frequently failing jobs, commit activity by author, contributor summaries, and release cadence. Includes a ready-to-run shell script that generates a Markdown weekly report, and a CSV export template for importing into spreadsheets.

### Repository Management

Project creation, cloning (including bulk group clones with `--group`), forking, archiving, and transferring between namespaces. Branch protection rules with access level reference, protected tag patterns, deploy key management, webhook creation and testing, project member access control, and file read/write operations via the API — useful for patching config files in a repo without a full clone.

### CI/CD Management

Triggering, monitoring, and cancelling pipelines; streaming job logs with `glab ci trace`; downloading build artifacts; creating, updating, and rotating CI/CD variables (masked, protected, environment-scoped, and group-level); linting `.gitlab-ci.yml` before pushing; managing pipeline schedules with cron expressions; runner health and administration; and a step-by-step debugging workflow for when a pipeline breaks.

---

## File structure

```
gitlab-ops/
├── SKILL.md                  # Core skill — loaded whenever the skill triggers (~130 lines)
└── references/
    ├── issues.md             # Issue & MR lifecycle, labels, milestones, bulk ops
    ├── statistics.md         # Metrics, reporting, jq aggregations, CSV export
    ├── repo.md               # Clone, fork, branch protection, webhooks, deploy keys
    └── cicd.md               # Pipelines, jobs, artifacts, variables, schedules, runners
```

`SKILL.md` is always loaded when the skill activates — it handles setup, authentication, the tool-selection decision tree (`glab` → `glab api` → `curl`), and routes to the right reference file for each domain. The reference files are loaded on demand, keeping the context lean for single-domain tasks.

---

## Installing the skill

```bash
# Project-scoped — active only inside this repository
mkdir -p .claude/skills
cp gitlab-ops.skill .claude/skills/

# User-scoped — active in every project
mkdir -p ~/.claude/skills
cp gitlab-ops.skill ~/.claude/skills/
```

Once installed, the skill auto-triggers when you ask Claude Code to do anything involving GitLab — you don't need an explicit `@skill` invocation. It will activate on mentions of `glab`, `gitlab-ci`, pipelines, issues, CI variables, branch protection, and similar terms.

---

## Usage examples

After installing, just ask Claude Code naturally:

```
Create an issue for the login bug, label it "bug" and "high-priority", assign it to @alice, and link it to the v2.5 milestone.
```

```
Show me the pipeline pass rate for main over the last 30 days and which jobs fail most often.
```

```
Clone all repos in the my-org group and protect the main branch in each one.
```

```
The nightly pipeline failed — trace the logs for the failing job, then retry it.
```

```
Rotate the DEPLOY_TOKEN variable in all projects under the infra group.
```

---

## The glab-first philosophy

The skill is built around a simple decision tree: prefer the `glab` subcommand because it reads cleanly, authenticates automatically, and understands your current repo's remote. Fall back to `glab api` (which wraps the REST API with auth and auto-expands `:id` to the current project's numeric ID) when glab doesn't have a direct command. Reserve raw `curl` for truly edge-case admin endpoints. The `--paginate` flag on `glab api` is the single most useful piece of knowledge in the whole skill — it automatically walks every page and streams results as one JSON array, making bulk operations and metrics collection dramatically simpler.

---

## Self-managed and GitLab Dedicated instances

Everything in this skill works against self-managed and GitLab Dedicated instances. Authenticate with your instance's hostname:

```bash
glab auth login --hostname gitlab.yourcompany.com
# or non-interactively:
glab auth login --hostname gitlab.yourcompany.com --stdin < my-token.txt
```

The `GITLAB_HOST` environment variable can override the host for a single command or script without changing your global auth config.

---

## Contributing

Issues and improvements are welcome. The four reference files are designed to be independently editable — if you add new `glab` subcommands or API patterns, drop them into the relevant file. Keep `SKILL.md` itself under 500 lines; if a domain grows significantly, consider splitting it into sub-files and adding a pointer in the routing table.

---

## Compatibility

| Component | Version |
|-----------|---------|
| glab | v1.40.0+ |
| GitLab | 16.0+ |
| jq | 1.6+ |
| Skill format | Claude skills v1 |

Last updated: April 2026