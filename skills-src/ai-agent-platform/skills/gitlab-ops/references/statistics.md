# Statistics and Metrics Collection Reference

This file covers how to collect, aggregate, and report on GitLab project and group metrics: pipeline success rates, issue throughput, MR cycle times, contributor activity, and custom analytics. Since glab doesn't have a dedicated `stats` subcommand, almost everything here uses `glab api` (with `--paginate`) combined with `jq` for aggregation.

Read this file when the user wants dashboards, reports, burn-down charts, velocity metrics, audit logs, or any quantitative analysis of GitLab data.

---

## Helper Setup

Set these once at the top of any stats script so the rest of the file stays readable:

```bash
PROJECT_ID=$(glab api projects/:id | jq -r .id)   # numeric ID for current repo
GROUP="my-org"                                      # group namespace
SINCE="2025-01-01T00:00:00Z"                        # start of reporting window
UNTIL="2025-03-31T23:59:59Z"                        # end of reporting window
```

---

## Issue Statistics

### Open / Closed Counts

```bash
# Count open issues
glab api "projects/:id/issues?state=opened" --paginate | jq 'length'

# Count closed issues in date range
glab api "projects/:id/issues?state=closed&closed_after=$SINCE&closed_before=$UNTIL" \
  --paginate | jq 'length'

# Breakdown by label
glab api "projects/:id/issues?state=opened" --paginate \
  | jq 'group_by(.labels[]) | map({label: .[0].labels[0], count: length})'
```

### Issue Age Distribution

How long are issues sitting open? This gives a percentile feel for backlog health:

```bash
glab api "projects/:id/issues?state=opened" --paginate | jq '
  [.[] | {
    iid: .iid,
    title: .title,
    age_days: (
      (now - (.created_at | fromdateiso8601)) / 86400 | floor
    )
  }] | sort_by(.age_days) | reverse
'
```

### Issue Throughput (Issues Closed Per Week)

```bash
glab api "projects/:id/issues?state=closed&closed_after=$SINCE&closed_before=$UNTIL" \
  --paginate | jq '
  [.[] | (.closed_at | split("T")[0] | split("-") | .[0] + "-W" +
    (. as $d | ($d[1] | tonumber) * 4 + ($d[2] | tonumber) / 7 | floor | tostring))] |
  group_by(.) | map({week: .[0], closed: length}) | sort_by(.week)
'
# Note: for precise ISO week numbers, post-process with Python or awk
```

---

## Merge Request Statistics

### MR Throughput

```bash
# MRs merged in date range
glab api "projects/:id/merge_requests?state=merged&updated_after=$SINCE&updated_before=$UNTIL" \
  --paginate | jq 'length'

# MRs by author
glab api "projects/:id/merge_requests?state=merged&updated_after=$SINCE" \
  --paginate | jq 'group_by(.author.username) | map({author: .[0].author.username, merged: length}) | sort_by(.merged) | reverse'
```

### MR Cycle Time (Time from Creation to Merge)

Cycle time is a key engineering health metric — shorter is usually better:

```bash
glab api "projects/:id/merge_requests?state=merged&updated_after=$SINCE" \
  --paginate | jq '
  [.[] | select(.merged_at != null) | {
    iid: .iid,
    title: .title,
    author: .author.username,
    cycle_time_hours: (
      ((.merged_at | fromdateiso8601) - (.created_at | fromdateiso8601)) / 3600 | round
    )
  }] | sort_by(.cycle_time_hours)
'
```

### Open MR Age (Review Queue Health)

```bash
glab api "projects/:id/merge_requests?state=opened" --paginate | jq '
  [.[] | {
    iid: .iid,
    title: .title,
    author: .author.username,
    reviewers: [.reviewers[].username],
    age_hours: ((now - (.created_at | fromdateiso8601)) / 3600 | floor)
  }] | sort_by(.age_hours) | reverse
'
```

---

## Pipeline / CI Statistics

### Pipeline Pass/Fail Rates

```bash
# Totals for main branch
glab api "projects/:id/pipelines?ref=main&updated_after=$SINCE" \
  --paginate | jq '
  {
    total: length,
    success: [.[] | select(.status == "success")] | length,
    failed: [.[] | select(.status == "failed")] | length,
    canceled: [.[] | select(.status == "canceled")] | length
  } | . + {success_rate: ((.success / .total * 100) | round | tostring + "%")}
'
```

### Average Pipeline Duration

```bash
glab api "projects/:id/pipelines?status=success&ref=main&updated_after=$SINCE" \
  --paginate | jq '
  [.[] | select(.duration != null) | .duration] |
  if length > 0 then
    {count: length, avg_seconds: (add / length | round),
     avg_minutes: (add / length / 60 | round)}
  else "no data" end
'
```

### Most Frequently Failing Jobs

Knowing which jobs fail most often helps prioritize stability work:

```bash
# Get recent failed pipelines, then query their jobs
glab api "projects/:id/pipelines?status=failed&ref=main&updated_after=$SINCE" \
  --paginate | jq '.[].id' | head -20 | while read PID; do
    glab api "projects/:id/pipelines/$PID/jobs" | \
      jq --arg pid "$PID" '[.[] | select(.status == "failed") | {pipeline: $pid, job: .name}]'
done | jq -s 'flatten | group_by(.job) | map({job: .[0].job, failures: length}) | sort_by(.failures) | reverse'
```

---

## Contributor Statistics

### Commit Activity

```bash
# Commits per author since a date
glab api "projects/:id/repository/commits?since=$SINCE&all=true" \
  --paginate | jq '
  group_by(.author_name) |
  map({author: .[0].author_name, commits: length}) |
  sort_by(.commits) | reverse
'

# Commits per day (useful for activity heatmaps)
glab api "projects/:id/repository/commits?since=$SINCE" \
  --paginate | jq '
  [.[] | .committed_date | split("T")[0]] |
  group_by(.) | map({date: .[0], commits: length}) | sort_by(.date)
'
```

### Member Contribution Summary (Group Level)

```bash
# All members of a group
glab api "groups/$GROUP/members" --paginate | jq '[.[] | {name: .name, username: .username, access_level: .access_level}]'
```

---

## Release and Deployment Stats

```bash
# List releases with dates
glab api "projects/:id/releases" --paginate | jq '[.[] | {tag: .tag_name, released: .released_at, name: .name}]'

# Time between releases
glab api "projects/:id/releases" --paginate | jq '
  [.[] | .released_at | fromdateiso8601] | sort |
  to_entries |
  [.[] | select(.key > 0) | {
    gap_days: ((. as $curr | input | .value - $curr.value) / 86400 | floor)
  }]
' 2>/dev/null || echo "use Python for gap math — jq cant self-reference"
```

---

## Putting It Together — Simple Report Script

This pattern produces a Markdown summary you can paste into a wiki or send to stakeholders:

```bash
#!/usr/bin/env bash
# gitlab-report.sh — weekly stats snapshot

SINCE=$(date -d "7 days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v-7d +%Y-%m-%dT%H:%M:%SZ)

ISSUES_CLOSED=$(glab api "projects/:id/issues?state=closed&closed_after=$SINCE" --paginate | jq 'length')
MRS_MERGED=$(glab api "projects/:id/merge_requests?state=merged&updated_after=$SINCE" --paginate | jq 'length')
PIPELINES=$(glab api "projects/:id/pipelines?ref=main&updated_after=$SINCE" --paginate)
PIPE_TOTAL=$(echo "$PIPELINES" | jq 'length')
PIPE_OK=$(echo "$PIPELINES" | jq '[.[] | select(.status=="success")] | length')

cat <<EOF
# Weekly GitLab Report — $(date +%Y-%m-%d)

**Issues closed:** $ISSUES_CLOSED
**MRs merged:** $MRS_MERGED
**Pipeline pass rate (main):** $PIPE_OK / $PIPE_TOTAL
EOF
```

---

## Exporting to CSV

For spreadsheet import, convert jq output to CSV:

```bash
glab api "projects/:id/issues?state=closed&closed_after=$SINCE" --paginate | jq -r '
  ["iid","title","author","labels","closed_at"],
  (.[] | [.iid, .title, .author.username, (.labels | join("|")), .closed_at])
  | @csv
' > issues_report.csv
```