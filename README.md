# CourtVision AI

Predictive analytics and explainable AI project for the EXL Analytics & AI Hackathon 2026, focused on Wimbledon 2026 predictions.

## Mission

Build a credible, explainable, and presentation-ready tennis prediction system that can forecast:

- Men's and women's top 8 quarterfinalists
- Knockout match winners across quarterfinals, semifinals, and finals
- Set-difference signal for knockout-stage scoring

## Team

| Name | Email | Location |
| --- | --- | --- |
| Rohit Kumar | rohit6053patel@gmail.com | USA |
| Abhinay Singh | abhi1863@gmail.com | India |
| Harshit Singh | harshitsingh398@gmail.com | India |

**Everyone is a co-owner of this product.** We work as one team with shared ownership. Task distribution will be finalized after our first successful meeting and team discussion. Areas of focus include data engineering, model development, explainability, and presentation delivery.

## Operating Model

We will run like a small product team:

- **Project management:** [Jira Scrum board](https://rohit6053patel.atlassian.net/jira/software/c/projects/CV26/boards/3)
- **Knowledge base:** Confluence
- **Code/versioning:** GitHub
- **Async communication:** WhatsApp or Slack free workspace
- **Meetings:** Google Meet
- **AI automation:** Jira/Confluence/GitHub MCP where available, with manual fallback templates

## Current Status (as of 8 June 2026)

- ✅ Repository created
- ✅ Team invited to GitHub
- ✅ Registration deadline passed
- ⏳ Jira board setup: **[CV26 in progress](https://rohit6053patel.atlassian.net/jira/software/c/projects/CV26/boards/3)**
- ⏳ Confluence pages: pending
- 📅 **Phase 1 submission in 20 days** (28 June 2026, 11:59 PM IST) — *CRITICAL PRIORITY*

## Important Dates

| Milestone | Date | Status |
| --- | --- | --- |
| Registration deadline | 8 June 2026 | ✅ Closed |
| Doubt session 1 | 12 June 2026 | 📅 Upcoming |
| Doubt session 2 | 19 June 2026 | 📅 Upcoming |
| **Phase 1 submission** | **28 June 2026, 11:59 PM IST** | **🔴 PRIORITY** |
| Phase 2 submission | 3-4 July 2026 | 📅 Upcoming |
| Phase 3 submission | 7-12 July 2026 | 📅 Upcoming |
| Leaderboard published | 14 July 2026 | 📅 Upcoming |
| Final presentations | 20-24 July 2026 | 📅 Upcoming |

## Repository Structure

```text
data/                 Raw and processed datasets; keep large data out of git when possible
docs/                 Team docs, sprint plans, meeting agendas, Confluence-ready pages
jira/                 Jira import CSVs and board setup notes
notebooks/            Exploration and modeling notebooks
reports/              Evaluation summaries and presentation-ready outputs
scripts/              Automation and utility scripts
src/                  Reusable project code
submissions/          Final prediction files and submission packages
```

## Definition of Done

A task is done only when:

- Code or document changes are committed to a branch
- Results are reproducible or clearly documented
- Evaluation impact is recorded when the task affects modeling
- Jira ticket is updated with status, owner, and evidence
- Pull request is reviewed before merging to `main`

## Getting Started (for team members)

### Clone the Repository

```bash
git clone https://github.com/entangleX/CourtVision.git
cd CourtVision
```

### Explore the Project

- **Sprint plans & decisions:** See `docs/` folder
- **Modeling exploration:** See `notebooks/` (recommended order: 01 → 02 → 03 → 04)
- **Jira board:** [CV26 Scrum Board](https://rohit6053patel.atlassian.net/jira/software/c/projects/CV26/boards/3)
- **Code standards:** Check branch protection rules before opening PRs

### First Steps

1. Review this README and the sprint plan in `docs/`
2. Join the team Jira board and claim a task from Sprint 0
3. Create a feature branch: `git checkout -b feature/task-description`
4. Commit early and often; push to your branch
5. Open a PR for team review before merging to `main`

## Quick Setup (Initial Onboarding)

If setting up the project for the first time:

1. ✅ Repository already created
2. Import `jira/courtvision_ai_jira_backlog.csv` into Jira (if not done)
3. Copy `docs/confluence/*.md` into Confluence pages
4. Ensure all three team members have access to Jira, Confluence, GitHub, and team chat
5. Start Sprint 0 immediately and keep all decisions in docs
