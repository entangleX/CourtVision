# Jira Outflow

This file is the shared write/request channel from Codex to Copilot Agent.

Codex writes desired Jira actions here. Copilot Agent should read this file, execute the requests through Atlassian MCP, and then update `jira/inflow.md` with the result.

## Execution Rules for Copilot Agent

- Use Atlassian MCP only.
- Target Atlassian site: `https://rohit6053patel.atlassian.net`
- Target Jira project: `CV26`
- Target board id: `3`
- Execute only requests marked `Status: Ready`.
- After execution, change the request status to `Done` or `Blocked`.
- Add execution notes and evidence.
- Update `jira/inflow.md` after every successful Jira read or write.
- If a transition name is ambiguous, fetch available transitions first and record them in `jira/inflow.md`.

## Request Queue

### Request 001

- Status: Ready
- Created by: Codex
- Requested action: Read issue status and transitions
- Jira issue: `CV26-1`
- Priority: High
- Instructions:
  - Get Jira issue `CV26-1`.
  - Record current status, assignee, priority, summary, and updated timestamp in `jira/inflow.md`.
  - Get available transitions for `CV26-1`.
  - Record transition names, IDs, and target statuses in `jira/inflow.md`.
- Expected output:
  - `jira/inflow.md` contains current status for `CV26-1`.
  - `jira/inflow.md` contains available transitions for `CV26-1`.
- Execution notes:

### Request 002

- Status: Waiting
- Created by: Codex
- Requested action: Move issue to In Progress
- Jira issue: `CV26-1`
- Priority: High
- Prerequisite:
  - Request 001 is Done.
  - `jira/inflow.md` shows an available transition to `In Progress`.
- Instructions:
  - Move `CV26-1` to `In Progress` using the correct transition from Jira.
  - Add this Jira comment:

```text
Work started from VS Code Agent mode via Atlassian MCP.
```

  - Update `jira/inflow.md` with the new status and comment confirmation.
- Expected output:
  - `CV26-1` status is `In Progress`.
  - Jira comment is added.
  - `jira/inflow.md` is refreshed.
- Execution notes:

## Completed Requests

Move completed request summaries here after execution.

