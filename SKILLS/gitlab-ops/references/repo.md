# Repository Management Reference

This file covers creating, cloning, forking, configuring, and administering GitLab repositories and projects using glab. It also covers branch protection, deploy keys, webhooks, protected tags, and group/namespace operations. Read this when the user's task involves project structure, access control, repository settings, or cloning workflows.

---

## Cloning and Forking

```bash
# Clone a repository (HTTPS or SSH, auto-detected from glab auth)
glab repo clone owner/project-name

# Clone into a specific directory
glab repo clone owner/project-name ~/work/project

# Clone all repos in a group (sequential)
glab repo clone --group my-org

# Clone all repos in a group into a subdirectory
glab repo clone --group my-org --preserve-namespace

# Fork a project to your namespace
glab repo fork owner/project-name

# Fork and immediately clone
glab repo fork owner/project-name --clone

# Fork to a specific group
glab repo fork owner/project-name --org my-team
```

---

## Creating and Archiving Projects

```bash
# Create new project in your namespace
glab repo create my-new-service

# Create in a group namespace
glab repo create --group my-org my-new-service

# Create with visibility
glab repo create my-new-service --visibility private    # private | internal | public

# Create from an existing local directory
cd ~/existing-project && glab repo create --name existing-project

# Archive a project (read-only; preserves all data)
PROJECT_ID=$(glab api "projects/owner%2Fproject" | jq -r .id)
glab api "projects/$PROJECT_ID" --method PUT --field archived=true

# Unarchive
glab api "projects/$PROJECT_ID" --method PUT --field archived=false
```

---

## Viewing Project Info

```bash
glab repo view                              # current repo details
glab repo view owner/project               # specific project
glab repo view --web                        # open in browser

# Full project metadata via API
glab api "projects/:id" | jq '{
  name: .name,
  namespace: .namespace.full_path,
  visibility: .visibility,
  default_branch: .default_branch,
  ssh_url: .ssh_url_to_repo,
  http_url: .http_url_to_repo,
  last_activity: .last_activity_at,
  stars: .star_count,
  forks: .forks_count
}'
```

---

## Branches

### Listing and Viewing

```bash
glab api "projects/:id/repository/branches" --paginate \
  | jq '[.[] | {name: .name, protected: .protected, merged: .merged, last_commit: .commit.committed_date}]'

# Find branches not merged into main
glab api "projects/:id/repository/branches?merged=false" --paginate \
  | jq '[.[] | select(.name != "main") | .name]'
```

### Creating and Deleting

```bash
# Create branch from main
glab api "projects/:id/repository/branches" --method POST \
  --field branch="feat/new-feature" --field ref="main"

# Delete a branch
glab api "projects/:id/repository/branches/feat%2Fold-feature" --method DELETE

# Bulk-delete merged branches (be careful!)
glab api "projects/:id/repository/branches?merged=true" --paginate \
  | jq -r '.[].name | @uri' \
  | grep -v '^main$' \
  | xargs -I{} glab api "projects/:id/repository/branches/{}" --method DELETE
```

### Branch Protection Rules

Branch protection is one of the most important repo settings — it prevents force-pushes and requires approvals before merge.

```bash
# List protected branches
glab api "projects/:id/protected_branches" | jq '.[].name'

# Protect main: no force push, require MR
glab api "projects/:id/protected_branches" --method POST \
  --field name="main" \
  --field push_access_level=0 \
  --field merge_access_level=40 \
  --field allow_force_push=false

# Access level meanings:
#  0  = No one
# 30  = Developer
# 40  = Maintainer
# 60  = Admin

# Update protection on an existing branch
glab api "projects/:id/protected_branches/main" --method PATCH \
  --field allow_force_push=false

# Unprotect a branch
glab api "projects/:id/protected_branches/main" --method DELETE
```

---

## Tags and Protected Tags

```bash
# List tags
glab api "projects/:id/repository/tags" --paginate | jq '[.[] | {name: .name, date: .commit.committed_date}]'

# Create a tag
glab api "projects/:id/repository/tags" --method POST \
  --field tag_name="v2.5.0" --field ref="main" \
  --field message="Release v2.5.0"

# Protect a tag pattern (only maintainers can push)
glab api "projects/:id/protected_tags" --method POST \
  --field name="v*" \
  --field create_access_levels='[{"access_level":40}]'
```

---

## Deploy Keys

Deploy keys allow read-only (or read-write) SSH access to a repository without user credentials — common for CI servers and automated tools.

```bash
# List deploy keys
glab api "projects/:id/deploy_keys" | jq '[.[] | {id: .id, title: .title, can_push: .can_push, created: .created_at}]'

# Add a deploy key (read-only by default)
glab api "projects/:id/deploy_keys" --method POST \
  --field title="prod-deploy-server" \
  --field key="ssh-rsa AAAA...your-public-key..." \
  --field can_push=false

# Enable an existing deploy key from another project
glab api "projects/:id/deploy_keys/$DEPLOY_KEY_ID/enable" --method POST

# Remove a deploy key
glab api "projects/:id/deploy_keys/$DEPLOY_KEY_ID" --method DELETE
```

---

## Webhooks

Webhooks let GitLab push events to external systems. Think of them as "publish-subscribe" for repository events.

```bash
# List webhooks
glab api "projects/:id/hooks" | jq '[.[] | {id: .id, url: .url, events: {push: .push_events, mr: .merge_requests_events, issues: .issues_events, pipeline: .pipeline_events}}]'

# Create a webhook for push + pipeline events
glab api "projects/:id/hooks" --method POST \
  --field url="https://ci.example.com/hooks/gitlab" \
  --field push_events=true \
  --field pipeline_events=true \
  --field merge_requests_events=false \
  --field token="secret-token-here" \
  --field enable_ssl_verification=true

# Test a webhook (trigger a test ping)
glab api "projects/:id/hooks/$HOOK_ID/test/push_events" --method POST

# Delete a webhook
glab api "projects/:id/hooks/$HOOK_ID" --method DELETE
```

---

## Project Members and Access

```bash
# List members
glab api "projects/:id/members" --paginate \
  | jq '[.[] | {name: .name, username: .username, access_level: .access_level}]'

# Add a member (access_level: 20=Reporter, 30=Developer, 40=Maintainer, 50=Owner)
glab api "projects/:id/members" --method POST \
  --field user_id=12345 \
  --field access_level=30

# Change access level
glab api "projects/:id/members/12345" --method PUT --field access_level=40

# Remove a member
glab api "projects/:id/members/12345" --method DELETE
```

---

## Group-Level Repository Operations

Some operations must be run at the group level when you manage many repos:

```bash
# List all projects in a group (recursive = includes subgroups)
glab api "groups/my-org/projects?include_subgroups=true" --paginate \
  | jq '[.[] | {name: .name, path: .path_with_namespace, visibility: .visibility}]'

# Transfer a project to a different group
glab api "projects/:id/transfer" --method PUT --field namespace="new-group"

# Search for projects by name across all accessible namespaces
glab api "projects?search=my-service" --paginate | jq '[.[] | .path_with_namespace]'
```

---

## Repository File Operations (non-git)

Sometimes you need to read or write a single file via API without a full clone — handy in scripts:

```bash
# Read a file (base64 encoded — pipe through base64 -d)
glab api "projects/:id/repository/files/README%2Emd/raw?ref=main"

# Create or update a file
glab api "projects/:id/repository/files/config%2Fsettings.json" --method POST \
  --field branch="main" \
  --field content="$(cat settings.json | base64)" \
  --field encoding="base64" \
  --field commit_message="chore: update settings"

# Use PUT instead of POST to update an existing file
glab api "projects/:id/repository/files/config%2Fsettings.json" --method PUT \
  --field branch="main" \
  --field content="$(cat settings.json | base64)" \
  --field encoding="base64" \
  --field commit_message="chore: update settings"
```