# Data

Use this folder for local datasets.

Suggested layout:

```text
data/raw/          Original downloaded files
data/processed/    Cleaned and model-ready files
data/external/     Small reference files safe to commit
```

Large datasets should not be committed unless they are small, public, and necessary for reproducibility.

## Required Local Inputs

Place these files directly under `data/` before running the local pipeline:

| File | Purpose |
| --- | --- |
| `atp_tennis.csv` | Historical men's match results |
| `wta.csv` | Historical women's match results |
| `MS_Entries.pdf` | Wimbledon 2026 men's direct-entry list |
| `LS_Entries.pdf` | Wimbledon 2026 women's direct-entry list |

Run:

```bash
python scripts/process_and_upload.py
python scripts/phase1_model.py
```

Generated CSV files are written to `data/processed/` and are intentionally ignored by Git.
