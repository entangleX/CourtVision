# Agent Instructions

## Project Context

This repository is for CourtVision AI, a Wimbledon 2026 predictive analytics project for the EXL Analytics & AI Hackathon.

## Atlassian Rovo MCP

When connected to `atlassianRovo`:

- Use Atlassian site: `https://rohit6053patel.atlassian.net`
- Use Jira project key: `CV26`
- Use Jira board id: `3`
- Prefer Jira issue keys that start with `CV26-`
- Use `maxResults: 10` or `limit: 10` for Jira searches unless the user explicitly asks for a larger result set.
- Before changing Jira issues, summarize the planned changes and ask for confirmation when the action is high-impact.
- Treat Jira as the source of truth for ticket status.
- Treat GitHub as the source of truth for code changes.
- Treat Confluence as the source of truth for durable project decisions.

## Default Jira Workflow

Use the board's actual workflow transitions when available. If the user uses plain language, interpret it as:

- "start ticket" -> move issue to In Progress
- "block ticket" -> move issue to Blocked and add a blocker comment
- "ready for review" -> move issue to In Review and link evidence
- "done" -> move issue to Done only after evidence is present

## Ticket Management Style

Every Jira update should include:

- What changed
- Why it changed
- Evidence link when available
- Next action or blocker

## Useful JQL Defaults

```jql
project = CV26 ORDER BY updated DESC
```

```jql
project = CV26 AND assignee = currentUser() ORDER BY priority DESC, updated DESC
```

```jql
project = CV26 AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

```jql
project = CV26 AND text ~ "blocked" ORDER BY updated DESC
```

