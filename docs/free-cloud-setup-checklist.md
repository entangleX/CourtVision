# Free Cloud Setup Checklist

This setup keeps the team on free plans for a 3-person hackathon team.

## 1. Atlassian

Use Atlassian Free for Jira and Confluence. Atlassian currently positions the free cloud plan around small teams of up to 10 users, which is enough for this team.

### Jira

1. Go to Atlassian and create a free Jira Software site.
2. Create project:
   - Template: Scrum
   - Project name: CourtVision AI
   - Project key: CVA
3. Invite:
   - Rohit Kumar: rohit6053patel@gmail.com
   - Abhinay Singh: abhi1863@gmail.com
   - Harshit Singh: harshitsingh398@gmail.com
4. Import `jira/courtvision_ai_jira_backlog.csv`.
5. Create the board columns listed in `jira/board-setup.md`.
6. Start Sprint 0.

### Confluence

1. Create a free Confluence space named `CourtVision AI`.
2. Copy pages from `docs/confluence/`:
   - `home.md`
   - `modeling-strategy.md`
   - `dataset-research.md`
   - `decision-log.md`
   - `submission-checklist.md`
3. Add Jira board and GitHub links to the home page.

## 2. GitHub

1. Create a new repository:
   - Name: `courtvision-ai`
   - Visibility: private until submission, public only if allowed by hackathon rules
2. Add collaborators:
   - rohit6053patel@gmail.com
   - abhi1863@gmail.com
   - harshitsingh398@gmail.com
3. Push this local repo.
4. Create labels:
   - `data`
   - `model`
   - `evaluation`
   - `documentation`
   - `submission`
   - `blocked`
   - `urgent`
5. Use pull requests for all changes.

## 3. Communication

Use WhatsApp for speed or Slack Free if you want more organization.

Recommended channels if using Slack:

- `#announcements`
- `#daily-standup`
- `#data`
- `#modeling`
- `#submission`
- `#random`

## 4. Meetings

Use Google Meet because it is free and easy across USA/India.

Create recurring calendar events:

- Sprint Planning: Saturday 9:30 PM IST / 12:00 PM ET
- Midweek Sync: Wednesday 9:30 PM IST / 12:00 PM ET
- Sprint Review + Retro: Friday 9:30 PM IST / 12:00 PM ET

## 5. Cloud Folder

Use Google Drive Free for non-code files if needed:

```text
CourtVision AI/
  01 Admin/
  02 Data Notes/
  03 Submissions/
  04 Presentation/
  05 Meeting Recordings/
```

Do not store private credentials in Drive or GitHub.

## 6. Google Cloud Platform

Use the team's GCP free trial project for cloud storage, processing, and model-related services.

Project details:

- Project name: `AGI-Lab`
- Project ID: `agi-lab-499017`
- Project number: `8095576102`
- Account status: Free Trial with $300.00 credit remaining
- Trial expiration: September 9, 2026

Recommended VS Code setup:

1. Install the Cloud Code extension from the VS Code Marketplace.
2. Authenticate locally with the Google Cloud CLI:

```bash
gcloud auth login
gcloud config set project agi-lab-499017
```

3. Use Google Cloud Console to create service credentials or Gemini API keys only when needed.
4. Store credentials in local environment variables or ignored `.env` files; never commit API keys, service account JSON files, or access tokens to GitHub.

Contributor access:

- Harshit Singh and Abhinay Singh have been added to the `AGI-Lab` GCP project.
- Both contributors have been granted Editor permission on the project.
- They do not need to create separate Google Cloud free trials or add credit cards for this project.
- They should accept the Google Cloud invitation from the invited email account, or sign in to Google Cloud Console with that account and select `AGI-Lab` from the project dropdown.
- After accepting access, each contributor should install the Google Cloud CLI and run:

```bash
gcloud auth login
gcloud config set project agi-lab-499017
```

- The Cloud Code VS Code extension is recommended for visual project access. Contributors should sign in with the invited Google account and select `agi-lab-499017`.
