# Copilot-Codex Jira Bridge

This repo uses a file-based bridge because Copilot Agent currently has Atlassian MCP access, while Codex may not.

## Files

- `jira/outflow.md`: Codex writes Jira requests here.
- `jira/inflow.md`: Copilot writes Jira results here after calling Atlassian MCP.

## Workflow

1. Codex writes a request in `jira/outflow.md`.
2. User asks VS Code Copilot Agent:

```text
Read jira/outflow.md, execute all Ready requests using Atlassian MCP, then update jira/inflow.md with the results.
```

3. Copilot executes Jira actions through MCP.
4. Copilot updates `jira/inflow.md`.
5. Codex reads `jira/inflow.md` and continues planning or writing the next request.

## One-Shot Copilot Prompt

Use this prompt in VS Code Agent mode:

```text
Read jira/outflow.md. Execute every request marked Status: Ready using Atlassian MCP for project CV26 on rohit6053patel.atlassian.net. After each action, update jira/inflow.md with the latest ticket state, transitions, comments, and any blockers. Then update jira/outflow.md by marking completed requests Done and blocked requests Blocked with notes.
```

## Rules

- Copilot should never invent Jira status.
- Copilot should always fetch issue state from Jira before writing `jira/inflow.md`.
- Codex should never assume Jira changed until `jira/inflow.md` shows the result.
- High-impact bulk updates should require user confirmation.

