# Issue Management Reference

This file covers the full lifecycle of GitLab issues, labels, milestones, and merge requests using glab. Read this when the user needs to create, triage, update, close, or bulk-manage issues and MRs.

---

## Issue Lifecycle

### Create

```bash
# Minimal
glab issue create -t "Login page crashes on Safari"

# Full metadata in one command
glab issue create \
  -t "Login page crashes on Safari" \
  -d "Reproduced on Safari 17.3. Steps: 1. Open /login 2. Click submit" \
  --label "bug,high-priority" \
  --assignee jdoe \
  --milestone "v2.4.0" \
  --due-date 2025-06-01

# Create and immediately open in browser
glab issue create -t "..." --web
```

### View and List

```bash
glab issue list                              # open issues, current repo
glab issue list --state=closed              # closed issues
glab issue list --label="bug"               # filter by label
glab issue list --assignee=@me              # my issues
glab issue list --milestone="v2.4.0"        # by milestone
glab issue list --search "login"            # full-text search
glab issue list --author=alice              # by author
glab issue list --page 2 --per-page 50      # pagination

# View single issue
glab issue view 42                          # by issue IID
glab issue view 42 --web                    # open in browser
glab issue view 42 --comments              # include all comments
```

### Update

```bash
# Change title
glab issue update 42 -t "New title"

# Add/remove labels (both flags can be repeated)
glab issue update 42 --label "regression" --unlabel "needs-triage"

# Reassign
glab issue update 42 --assignee carol

# Change milestone
glab issue update 42 --milestone "v2.5.0"

# Set due date
glab issue update 42 --due-date 2025-07-15

# Remove due date
glab issue update 42 --due-date ""
```

### Close / Reopen

```bash
glab issue close 42
glab issue reopen 42

# Bulk-close all issues matching a label (shell loop)
glab issue list --label="stale" --output json \
  | jq '.[].iid' \
  | xargs -I{} glab issue close {}
```

### Notes / Comments

```bash
glab issue note 42 -m "Confirmed in staging. Assigning to @bob."

# Markdown multi-line note
glab issue note 42 -m $'## Root cause\nNull pointer in auth middleware.\n\nFix tracked in !99.'
```

---

## Labels

```bash
glab label list                             # list all project labels
glab label create --name "needs-repro" --color "#e11d48" --description "Needs reproduction steps"
glab label delete "needs-repro"
```

For group-level labels you need the API:
```bash
glab api "groups/:id/labels" --paginate | jq '.[].name'
glab api "groups/:id/labels" --method POST \
  --field name="security" --field color="#dc2626"
```

---

## Milestones

```bash
glab milestone list
glab milestone view "v2.4.0"

# Create
glab api "projects/:id/milestones" --method POST \
  --field title="v2.5.0" \
  --field due_date="2025-08-01" \
  --field description="Summer release"

# Close a milestone
MILESTONE_ID=$(glab api "projects/:id/milestones" | jq '.[] | select(.title=="v2.4.0") | .id')
glab api "projects/:id/milestones/$MILESTONE_ID" --method PUT --field state_event="close"
```

---

## Merge Requests

MRs are tightly coupled to issues in GitLab (closing patterns, linked MRs). The key subcommand is `glab mr`.

### Create

```bash
# From current branch — glab fills title/description from commit
glab mr create --fill

# Draft MR
glab mr create --fill --draft

# Target a non-default branch
glab mr create --fill --target-branch release/v2

# Link to an issue (uses closing pattern in description)
glab mr create --fill -d "Closes #42"

# Full options
glab mr create \
  -t "feat: add OAuth login" \
  -d "Closes #42\n\n## Changes\n- Added OAuth provider\n- Updated tests" \
  --label "feature,needs-review" \
  --assignee @me \
  --reviewer alice,bob \
  --milestone "v2.5.0"
```

### Review Workflow

```bash
glab mr list                                # open MRs in repo
glab mr list --reviewer=@me                 # review queue
glab mr list --assignee=@me                 # my MRs
glab mr view 99                             # show MR detail
glab mr diff 99                             # show diff
glab mr checkout 99                         # check out branch locally

glab mr approve 99
glab mr revoke 99                           # revoke approval

glab mr note 99 -m "Nit: rename variable"

# Mark ready (remove Draft)
glab mr update 99 --ready
```

### Merge

```bash
glab mr merge 99                            # merge now
glab mr merge 99 --when-pipeline-succeeds   # auto-merge after CI
glab mr merge 99 --squash                   # squash commits
glab mr merge 99 --remove-source-branch     # delete branch after merge
```

### Update / Close

```bash
glab mr update 99 -t "New title"
glab mr update 99 --label "reviewed"
glab mr close 99
glab mr reopen 99
```

---

## Bulk Operations and Scripting Patterns

A common pattern is to list issues/MRs as JSON, transform with `jq`, and feed results back to glab. Here are templates:

```bash
# Close all issues older than 90 days that are unassigned
CUTOFF=$(date -d "90 days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
         date -v-90d +%Y-%m-%dT%H:%M:%SZ)  # macOS fallback

glab api "projects/:id/issues?state=opened&assignee_id=None&created_before=$CUTOFF" \
  --paginate | jq '.[].iid' | xargs -I{} glab issue close {}

# Add "stale" label to issues not updated in 60 days
CUTOFF=$(date -d "60 days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
         date -v-60d +%Y-%m-%dT%H:%M:%SZ)
glab api "projects/:id/issues?state=opened&updated_before=$CUTOFF" \
  --paginate | jq '.[].iid' | xargs -I{} glab issue update {} --label "stale"
```

---

## Cross-Project / Group Issue Operations

glab's issue commands are project-scoped. For group-level views, use the API:

```bash
# All open issues across a group
glab api "groups/my-group/issues?state=opened" --paginate \
  | jq '[.[] | {project: .references.full, iid: .iid, title: .title}]'

# Issues assigned to me across all projects in a group
glab api "groups/my-group/issues?state=opened&assignee_username=myusername" --paginate \
  | jq '.[].title'
```