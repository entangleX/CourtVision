# Atlassian MCP Setup for VS Code

This repo is configured for Jira/Confluence automation through the official Atlassian Rovo MCP Server.

## What This Enables

From VS Code Agent mode, you should be able to ask the AI to:

- Search Jira tickets in project `CV26`
- Create new Jira issues
- Add Jira comments
- Update Jira issue fields
- Move tickets through workflow transitions
- Search Confluence
- Create or update Confluence pages

Your Jira board:

```text
https://rohit6053patel.atlassian.net/jira/software/c/projects/CV26/boards/3
```

## Files Added

- `.vscode/mcp.json`: connects VS Code to Atlassian Rovo MCP
- `AGENTS.md`: tells the agent to default to site `rohit6053patel.atlassian.net`, project `CV26`, and board `3`

## Setup Steps in VS Code

1. Open this project folder in VS Code.
2. Make sure GitHub Copilot Chat / Agent mode is enabled.
3. Open Command Palette.
4. Run:

```text
MCP: List Servers
```

5. Start `atlassianRovo`.
6. VS Code should open a browser login/consent flow for Atlassian.
7. Sign in with the Atlassian account that has access to project `CV26`.
8. Return to VS Code and use Agent mode.

## If VS Code Does Not Auto-Detect It

Open:

```text
MCP: Open Workspace Folder MCP Configuration
```

Confirm this exists:

```json
{
  "servers": {
    "atlassianRovo": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v1/mcp/authv2"
    }
  },
  "inputs": []
}
```

Then run:

```text
MCP: Reset Cached Tools
MCP: List Servers
```

## Test Prompts

Use these inside VS Code Agent mode after MCP is connected.

```text
Using Atlassian MCP, list my 10 most recently updated Jira issues in project CV26.
```

```text
Using Atlassian MCP, show all open CV26 Jira tickets grouped by status.
```

```text
Using Atlassian MCP, create a Jira task in CV26 titled "Set up Wimbledon data ingestion" with acceptance criteria for selecting public ATP/WTA datasets.
```

```text
Using Atlassian MCP, add a progress comment to CV26-1 saying: "Repository structure and operating docs are ready. Next step is data source validation."
```

```text
Using Atlassian MCP, get available transitions for CV26-1.
```

```text
Using Atlassian MCP, move CV26-1 to In Progress if that transition exists.
```

## Good Daily Workflow

Start of day:

```text
Using Atlassian MCP, show my assigned CV26 tickets that are not Done, ordered by priority.
```

During work:

```text
Using Atlassian MCP, add a progress comment to CV26-KEY based on my latest git commit and summarize the next step.
```

End of day:

```text
Using Atlassian MCP, summarize all CV26 tickets updated today and draft a standup update for Rohit, Abhinay, and Harshit.
```

Sprint review:

```text
Using Atlassian MCP, summarize completed CV26 tickets for the current sprint and create a Confluence sprint review note.
```

## Security Rules

- Do not commit API tokens, passwords, or OAuth secrets.
- Use OAuth through VS Code where possible.
- Review any bulk Jira update before approving it.
- Keep destructive actions manual unless you explicitly ask the agent to do them.

## Troubleshooting

If you cannot connect:

- Confirm you are logged into the correct Atlassian account.
- Confirm the account can access project `CV26`.
- Run `MCP: Reset Cached Tools`.
- Restart VS Code.
- Check whether Atlassian admin approval is required for the first MCP connection.

If ticket creation works but transitions fail:

- Ask the agent to get available transitions for the issue first.
- Use the exact transition name returned by Jira.

