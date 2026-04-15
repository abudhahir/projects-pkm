# CI/CD Management Reference

This file covers everything pipeline-related: triggering and monitoring pipelines, tracing job logs, managing CI/CD variables, scheduling, linting `.gitlab-ci.yml`, downloading artifacts, and administering runners. Read it whenever the user is debugging CI failures, setting up automation, rotating secrets, or scheduling pipelines.

---

## Pipelines — View and Monitor

`glab ci` is the primary subcommand. Think of pipelines as the outer container and jobs as the individual work units inside.

```bash
glab ci status                         # latest pipeline status for current branch
glab ci view                           # interactive pipeline viewer (select job, see logs)
glab ci list                           # list recent pipelines
glab ci list --branch main             # pipelines for a specific branch

# API-level detail (includes duration, coverage, commit)
glab api "projects/:id/pipelines" --paginate \
  | jq '[.[] | {id:.id, status:.status, ref:.ref, duration:.duration, created:.created_at}]'
```

---

## Pipelines — Trigger and Control

```bash
# Trigger pipeline on current branch
glab ci run

# Trigger on a specific branch
glab ci run --branch develop

# Trigger with CI variables passed at runtime
glab ci run --branch main --variable "DEPLOY_ENV=staging" --variable "SKIP_TESTS=false"

# Retry the latest failed pipeline
glab ci retry

# Retry a specific pipeline by ID
glab api "projects/:id/pipelines/12345/retry" --method POST

# Cancel a running pipeline
glab api "projects/:id/pipelines/12345/cancel" --method POST

# Delete a pipeline (removes its trace, not the code)
glab api "projects/:id/pipelines/12345" --method DELETE
```

---

## Jobs — Inspect and Control

Jobs are the individual steps within a pipeline stage. Knowing their names and IDs is essential for debugging.

```bash
# List jobs for the latest pipeline
glab ci view                           # interactive — press Enter on a job to tail logs

# Trace (stream) logs for a specific job ID
glab ci trace 456789

# Tail logs of the most recent failed job on current branch (shell one-liner)
PIPELINE_ID=$(glab api "projects/:id/pipelines?ref=$(git branch --show-current)" \
  | jq '.[0].id')
FAILED_JOB=$(glab api "projects/:id/pipelines/$PIPELINE_ID/jobs" \
  | jq '[.[] | select(.status == "failed")] | .[0].id')
glab ci trace "$FAILED_JOB"

# Retry a single job
glab api "projects/:id/jobs/456789/retry" --method POST

# Cancel a running job
glab api "projects/:id/jobs/456789/cancel" --method POST

# Play a manual job (one that has `when: manual` in the YAML)
glab api "projects/:id/jobs/456789/play" --method POST

# Erase job log and artifacts (admin use)
glab api "projects/:id/jobs/456789/erase" --method POST
```

---

## Artifacts

Artifacts are files a job produces — binaries, test reports, coverage data, etc. glab can download them without opening a browser.

```bash
# Download artifacts from the latest successful pipeline on main
glab ci artifact main build-job

# Download to a specific path
glab ci artifact main build-job --path ./dist

# Download artifacts for a specific pipeline ID via API
glab api "projects/:id/jobs/456789/artifacts" > artifacts.zip

# List artifact files (metadata only, no download)
glab api "projects/:id/jobs/456789/artifacts?file_type=archive" | head
```

---

## CI/CD Variables

Variables are the secrets and configuration values injected into pipeline jobs. The distinction between **project**, **group**, and **instance** scope matters:

- Project variables: set per-project, most common
- Group variables: inherited by all projects in a group — great for shared tokens
- Instance variables: GitLab admin only, rarely used outside self-managed setups

```bash
# List all project variables (does NOT show the values of masked variables)
glab variable list

# Get a specific variable's value
glab variable get DEPLOY_TOKEN

# Create a variable (plain text)
glab variable set DATABASE_URL "postgres://user:pass@host/db"

# Create a masked variable (value hidden in job logs)
glab variable set SECRET_KEY "s3cr3t" --masked

# Create a protected variable (only available in protected branches/tags)
glab variable set PROD_API_KEY "abc123" --protected --masked

# Create with a specific scope (environment-specific variables)
glab variable set DEPLOY_HOST "prod.example.com" --scope production

# Update an existing variable
glab variable update SECRET_KEY "new-value" --masked

# Delete a variable
glab variable delete DEPLOY_TOKEN

# Group-level variables (requires glab api — no direct subcommand)
glab api "groups/my-org/variables" | jq '[.[] | {key: .key, masked: .masked, protected: .protected}]'

glab api "groups/my-org/variables" --method POST \
  --field key="SHARED_NPM_TOKEN" \
  --field value="npm_token_here" \
  --field masked=true \
  --field protected=true
```

---

## .gitlab-ci.yml Linting

Always lint your CI config locally before pushing — a broken YAML silently prevents pipelines from starting.

```bash
# Lint the .gitlab-ci.yml in the current directory
glab ci lint

# Lint a specific file
glab ci lint path/to/.gitlab-ci.yml

# If glab isn't available, use the API directly (useful in CI itself)
curl -s -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  --data "$(jq -Rsc '{content:.}' < .gitlab-ci.yml)" \
  "https://gitlab.com/api/v4/ci/lint" | jq '{valid: .valid, errors: .errors}'
```

---

## Pipeline Schedules

Schedules let you run pipelines on a cron-like timer — useful for nightly builds, weekly dependency scans, or regular deployments.

```bash
# List all schedules
glab schedule list

# Create a schedule (runs every day at 02:00 UTC on main)
glab schedule create \
  --description "Nightly security scan" \
  --cronExpr "0 2 * * *" \
  --ref main \
  --timezone "UTC"

# Create with CI variables passed at schedule time
glab schedule create \
  --description "Weekly full test" \
  --cronExpr "0 6 * * 1" \
  --ref main \
  --variable "RUN_SLOW_TESTS=true"

# Run a schedule immediately (trigger it now)
SCHEDULE_ID=$(glab schedule list --output json | jq '.[] | select(.description=="Nightly security scan") | .id')
glab schedule run "$SCHEDULE_ID"

# Delete a schedule
glab schedule delete "$SCHEDULE_ID"

# API alternative (gives more control over variables per schedule)
glab api "projects/:id/pipeline_schedules" | jq '[.[] | {id:.id, desc:.description, cron:.cron, ref:.ref, active:.active}]'
```

---

## Runners

Runners are the agents that execute jobs. Knowing which runners are available and healthy is important for debugging stuck pipelines.

```bash
# List runners registered to the current project
glab runner list

# List all runners (requires admin token for instance-level)
glab api "runners?type=project_type" | jq '[.[] | {id:.id, name:.description, status:.status, online:.online}]'

# Pause a runner (stops it taking new jobs)
glab api "runners/RUNNER_ID" --method PUT --field paused=true

# Resume a runner
glab api "runners/RUNNER_ID" --method PUT --field paused=false

# Delete a runner
glab api "runners/RUNNER_ID" --method DELETE
```

---

## Environment and Deployment Tracking

Environments represent deployment targets (staging, production, etc.). They track which pipeline deployed what.

```bash
# List environments
glab api "projects/:id/environments" | jq '[.[] | {id:.id, name:.name, state:.state, last_deployment: .last_deployment.iid}]'

# Stop an environment (prevents new deploys without deleting history)
glab api "projects/:id/environments/$ENV_ID/stop" --method POST

# Delete an environment
glab api "projects/:id/environments/$ENV_ID" --method DELETE
```

---

## Common Debugging Workflow

When a user says "my pipeline broke," work through this sequence:

1. Check the pipeline status: `glab ci status`
2. Find which job failed: `glab ci view` → navigate to the red job
3. Stream the full log: `glab ci trace <job-id>`
4. If it looks like a config issue: `glab ci lint`
5. If variables might be wrong: `glab variable list` (remember masked values won't show)
6. If it's a runner issue: `glab runner list` and check runner tags match the job's `tags:` field
7. Retry the job once you've fixed the issue: `glab api projects/:id/jobs/<id>/retry --method POST`