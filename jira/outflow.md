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

- Status: Blocked
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
  - Latest `jira/inflow.md` sync shows active Sprint 1 tickets are `CV26-3` through `CV26-9`.
  - `CV26-1` is not present in the active sprint snapshot, so this request is no longer the best next action.

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

## New Requests

### Request 003

- Status: Ready
- Created by: Codex
- Requested action: Update GitHub setup ticket with blocker
- Jira issue: `CV26-3`
- Priority: High
- Context from repo:
  - Local Git repository is initialized.
  - Initial project setup commits exist.
  - Git remote was set to `git@github.com:entangleX/CourtVision.git`.
  - Push failed because GitHub returned: `Permission to entangleX/CourtVision.git denied to deploy key`.
- Instructions:
  - Get Jira issue `CV26-3`.
  - Add this Jira comment:

```text
Progress update from Codex/Copilot bridge:

Local repository setup is complete and commits exist on main. Remote origin is configured as git@github.com:entangleX/CourtVision.git.

Current blocker: push to GitHub failed because GitHub returned "Permission to entangleX/CourtVision.git denied to deploy key." Rohit needs to either add this machine's SSH key with write access or switch the remote to HTTPS and push with GitHub authentication.

Next action: fix GitHub authentication, push main, then invite Abhinay and Harshit as collaborators.
```

  - If a `Blocked` transition exists for `CV26-3`, move it to `Blocked`.
  - If no `Blocked` transition exists, leave status unchanged and record available transitions in `jira/inflow.md`.
  - Refresh `jira/inflow.md` for `CV26-3` after the update.
- Expected output:
  - `CV26-3` has a Jira progress/blocker comment.
  - `CV26-3` is `Blocked` if the workflow supports it.
  - `jira/inflow.md` shows the latest status for `CV26-3`.
- Execution notes:

### Request 004

- Status: Ready
- Created by: Codex
- Requested action: Move Jira board setup ticket toward approval
- Jira issue: `CV26-4`
- Priority: High
- Context from inflow:
  - Sprint 1 exists and is active.
  - Board id is `3`.
  - Project key is `CV26`.
  - Atlassian MCP connection is working because Copilot produced the active sprint snapshot.
- Instructions:
  - Get Jira issue `CV26-4`.
  - Add this Jira comment:

```text
Progress update from Codex/Copilot bridge:

Jira Scrum board setup is functionally complete for project CV26. Sprint 1 is active on board 3, and the Atlassian MCP bridge successfully produced a current sprint snapshot in jira/inflow.md.

Recommended next state: Pending for Approval, if that transition is available.
```

  - Get available transitions for `CV26-4`.
  - If a transition to `Pending for Approval` exists, move `CV26-4` to `Pending for Approval`.
  - If not, leave status unchanged and record available transitions in `jira/inflow.md`.
  - Refresh `jira/inflow.md` for `CV26-4` after the update.
- Expected output:
  - `CV26-4` has a progress comment.
  - `CV26-4` is moved to `Pending for Approval` if Jira allows it.
  - `jira/inflow.md` shows the latest status for `CV26-4`.
- Execution notes:

### Request 005

- Status: Ready
- Created by: Codex
- Requested action: Refresh active sprint snapshot
- Jira issue: Sprint 1 / Board 3
- Priority: Medium
- Instructions:
  - Refresh the active sprint issue list for board `3`, project `CV26`.
  - Rewrite `jira/inflow.md` into a clean snapshot without duplicated template content.
  - Include:
    - Last sync timestamp
    - Sprint name, state, goal, start date, end date
    - Ticket table for all active sprint issues
    - Blockers
    - Recently updated tickets
    - Available transitions for any issue touched by Requests 003 and 004
- Expected output:
  - `jira/inflow.md` is clean, current, and easy for Codex to read.
- Execution notes:

### Request 006

- Status: Ready
- Created by: Codex
- Requested action: Enrich Sprint 1 tickets with proper descriptions, acceptance criteria, story points, and kickoff comments
- Jira issue: `CV26-3`, `CV26-4`, `CV26-5`, `CV26-6`, `CV26-7`, `CV26-8`, `CV26-9`
- Priority: Highest
- Important:
  - Use Atlassian MCP only.
  - Before updating fields, fetch each issue's editable fields and use the correct Jira field for story points/story point estimate.
  - If a field is not editable, skip that field and mention it in execution notes.
  - Do not overwrite useful existing descriptions; improve them.
  - Add one professional kickoff/progress comment to each ticket.
- Instructions:
  - For each ticket below, update the description with the provided structured description.
  - Add acceptance criteria to the description.
  - Set story points where missing or incorrect.
  - Add labels if Jira supports labels: `courtvision-ai`, plus the ticket-specific labels below.
  - Add a concise comment explaining what was clarified and what the assignee should do next.
  - Refresh `jira/inflow.md` after all updates.

#### CV26-3 — Create GitHub repository and invite team

- Story points: `2`
- Labels: `setup`, `github`, `blocked`
- Description:

```text
Set up the GitHub repository for CourtVision AI and make it ready for collaborative development.

Scope:
- Use repository: entangleX/CourtVision
- Push the local main branch from this workspace
- Invite Rohit, Abhinay, and Harshit as collaborators
- Confirm all team members can clone, branch, commit, and open pull requests
- Keep the repository private unless hackathon rules allow public sharing

Current blocker:
- Push failed because GitHub returned: "Permission to entangleX/CourtVision.git denied to deploy key."

Acceptance criteria:
- main branch exists on GitHub
- README, docs, Jira bridge, and project structure are visible on GitHub
- Abhinay and Harshit have access
- Branch and PR workflow is documented
- Jira ticket contains the final GitHub repo link
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Main blocker is GitHub authentication/write access. Next step: Rohit should fix SSH or switch to HTTPS auth, push main, then invite Abhinay and Harshit.
```

#### CV26-4 — Create Jira Scrum board

- Story points: `2`
- Labels: `setup`, `jira`, `scrum`
- Description:

```text
Create and configure the Jira Scrum board used to manage the CourtVision AI hackathon work.

Scope:
- Jira site: rohit6053patel.atlassian.net
- Project key: CV26
- Board id: 3
- Sprint 1 active with setup, data, and modeling foundation tickets
- Workflow should support To Do, In Progress, BLOCKED, IN REVIEW, Pending for Approval, and Done
- Jira should be usable from VS Code through Atlassian MCP

Acceptance criteria:
- Sprint 1 is active
- Core tickets are present in Sprint 1
- Workflow transitions are available
- Atlassian MCP can read board/ticket state
- Ticket is moved to Pending for Approval when setup is verified
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Jira board and Sprint 1 are active, and Atlassian MCP can read/update ticket state. Recommended next step: Rohit reviews and approves.
```

#### CV26-5 — Create Confluence project space

- Story points: `3`
- Labels: `setup`, `confluence`, `docs`
- Description:

```text
Create the Confluence knowledge base for CourtVision AI so team decisions, research, and submission notes have a durable home.

Scope:
- Create a Confluence space or page tree for CourtVision AI
- Add project home page
- Add team charter
- Add sprint plan
- Add dataset research page
- Add modeling strategy page
- Add decision log
- Add submission checklist
- Link Jira board and GitHub repository from the home page

Acceptance criteria:
- Confluence home page exists
- Required pages are created or copied from docs/confluence
- Jira board link is included
- GitHub repo link is included once available
- Team members know where to write research notes and decisions
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Repo already contains Confluence-ready markdown pages under docs/confluence. Next step: publish them into Confluence and add Jira/GitHub links.
```

#### CV26-6 — Register team for hackathon

- Story points: `1`
- Labels: `admin`, `registration`, `urgent`
- Description:

```text
Register the CourtVision AI team for the EXL Analytics & AI Hackathon 2026 before the deadline.

Team:
- Rohit Kumar — Team Lead — rohit6053patel@gmail.com
- Abhinay Singh — Data Engineering — abhi1863@gmail.com
- Harshit Singh — Modeling and Evaluation — harshitsingh398@gmail.com

Scope:
- Confirm team name: CourtVision AI
- Submit registration form before 8 June 2026
- Save registration confirmation
- Share confirmation with the team

Acceptance criteria:
- Team registration is submitted
- Confirmation screenshot/email is saved
- Jira comment includes confirmation status
- Ticket is moved to Done only after confirmation exists
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. This is urgent because the registration deadline is 8 June 2026. Next step: Harshit/Rohit confirm registration and attach or comment evidence.
```

#### CV26-7 — Shortlist public tennis datasets

- Story points: `3`
- Labels: `data`, `research`, `phase-1`
- Description:

```text
Shortlist public tennis datasets that can support Wimbledon 2026 prediction modeling for both men's and women's categories.

Scope:
- Identify public ATP match history datasets
- Identify public WTA match history datasets
- Identify ranking history sources
- Identify Wimbledon historical results/draw data
- Check licensing/usage suitability for hackathon work
- Record source links, coverage years, fields, refresh method, and known risks

Acceptance criteria:
- At least 3 candidate data sources are documented
- Men's and women's coverage is addressed
- Data source risks are recorded
- Recommended dataset stack is proposed
- Findings are added to Confluence or docs/confluence/dataset-research.md
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Next step: Harshit should shortlist sources and record coverage, fields, risks, and recommendation for Phase 1 modeling.
```

#### CV26-8 — Define data schema

- Story points: `3`
- Labels: `data`, `schema`, `phase-1`
- Description:

```text
Define the project data schema needed for repeatable Wimbledon prediction modeling.

Scope:
- Define raw and processed data tables
- Define player identity keys
- Define match-level table fields
- Define ranking/history fields
- Define feature table fields
- Define prediction output schema
- Define data quality checks

Acceptance criteria:
- Schema covers ATP and WTA data
- Player identity normalization approach is documented
- Match outcome labels are defined
- Feature table supports ranking, form, surface, and Wimbledon history signals
- Prediction output schema supports Phase 1 top 8 predictions
- Schema is documented in repo or Confluence
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Next step: Abhinay should define the raw, processed, feature, and prediction output schemas so ingestion and modeling can start cleanly.
```

#### CV26-9 — Build initial data ingestion scripts

- Story points: `5`
- Labels: `data`, `engineering`, `phase-1`
- Description:

```text
Build initial repeatable scripts to ingest selected public tennis datasets into the CourtVision AI project structure.

Scope:
- Create scripts for selected match history data
- Create scripts for rankings/player metadata if available
- Save raw files under data/raw locally
- Save cleaned outputs under data/processed locally
- Keep large data files out of git
- Document how to run ingestion
- Add basic validation checks

Acceptance criteria:
- Scripts can be run from a clean checkout
- Ingestion process is documented
- Processed output is ready for baseline modeling
- Basic row counts and missing-value checks are produced
- No secrets or large raw datasets are committed
```

- Comment:

```text
Ticket clarified by Codex/Copilot bridge. Next step: Abhinay should wait for the selected dataset stack from CV26-7, then implement repeatable ingestion with simple validation outputs.
```

- Expected output:
  - Sprint 1 tickets have professional descriptions.
  - Missing story points are filled.
  - Each ticket has a clear next-action comment.
  - `jira/inflow.md` is refreshed with latest statuses, story points, and recently updated timestamps.
- Execution notes:
