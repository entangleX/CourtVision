# GCP Data Workflow

Use this workflow when you want to process data from VS Code and save outputs directly to Google Cloud.

## Goal

Work locally in VS Code, but keep the shared project data in GCP:

- Raw and processed files in Cloud Storage bucket `tennisdatabase`
- Analysis-ready tables in BigQuery
- Python processing scripts inside this repository

## Recommended Setup

### 1. Install local tools

- Google Cloud CLI
- Python 3.11+
- VS Code extensions:
  - Cloud Code
  - Python
  - Jupyter

### 2. Authenticate from the VS Code terminal

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project agi-lab-499017
gcloud config list
```

Why both commands:

- `gcloud auth login` authenticates the CLI
- `gcloud auth application-default login` lets Python client libraries talk to GCP from VS Code

### 3. Create a local Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create local environment variables

```bash
cp .env.example .env
```

Default values:

```env
GOOGLE_CLOUD_PROJECT=agi-lab-499017
GCP_BUCKET=tennisdatabase
BIGQUERY_DATASET=courtvision_raw
```

## Data Flow

### Cloud Storage layout

Recommended bucket structure:

```text
gs://tennisdatabase/
  raw/
  processed/
  features/
  predictions/
```

Suggested usage:

- `raw/`: original CSVs and PDFs
- `processed/`: cleaned structured tables
- `features/`: model-ready feature tables
- `predictions/`: Top 8 and knockout outputs

### BigQuery layout

Recommended datasets:

- `courtvision_raw`
- `courtvision_features`
- `courtvision_predictions`

## One-command local processing

This repository now includes:

- [scripts/process_and_upload.py](/Users/osho/Desktop/Wimbledon_Hackathon_EXL26/scripts/process_and_upload.py)

It does the following:

1. Reads `data/atp_tennis.csv` and `data/wta.csv`
2. Normalizes ATP/WTA schemas into one combined match-history table
3. Parses `MS_Entries.pdf` and `LS_Entries.pdf` into structured entry tables
4. Writes outputs into `data/processed/`
5. Optionally uploads files to Cloud Storage
6. Optionally loads tables into BigQuery

### Run local processing only

```bash
python scripts/process_and_upload.py
```

### Process and upload to Cloud Storage

```bash
python scripts/process_and_upload.py --upload-gcs
```

### Process and load to BigQuery

```bash
python scripts/process_and_upload.py --load-bigquery
```

### Do both

```bash
python scripts/process_and_upload.py --upload-gcs --load-bigquery
```

## BigQuery preparation

Create the dataset once:

```bash
bq --location=US mk --dataset agi-lab-499017:courtvision_raw
```

You can repeat the same pattern later for:

```bash
bq --location=US mk --dataset agi-lab-499017:courtvision_features
bq --location=US mk --dataset agi-lab-499017:courtvision_predictions
```

## Starter SQL for Phase 1

This repository also includes a baseline BigQuery feature query:

- [scripts/query_phase1_features.sql](/Users/osho/Desktop/Wimbledon_Hackathon_EXL26/scripts/query_phase1_features.sql)

It builds simple Phase 1 features such as:

- career win rate
- grass-court win rate
- Wimbledon win rate
- recent 90-day form

You can run it in BigQuery after loading the raw tables and then save the result into a `courtvision_features` table.

## Suggested team workflow

### Data engineering

- Keep source files under `gs://tennisdatabase/raw/`
- Run processing from VS Code
- Save structured outputs into `gs://tennisdatabase/processed/`
- Load shared tables into BigQuery

### Modeling

- Pull training data from BigQuery into notebooks or scripts
- Save feature tables back to BigQuery or `gs://tennisdatabase/features/`
- Export predictions to `gs://tennisdatabase/predictions/`

## Notes

- Do not commit `.env`, service-account JSON files, or tokens
- Use Application Default Credentials for local Python unless you specifically need a service account
- Start simple: Cloud Storage + BigQuery is enough for the hackathon baseline
