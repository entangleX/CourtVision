# CourtVision AI Delivery Plan

Last updated: 24 June 2026

## Immediate Goal

Submit eight predicted Wimbledon 2026 quarterfinalists for men's singles and eight for women's singles by 28 June 2026 at 11:59 PM IST.

## Current Recommendation

Use the validated heuristic baseline as the provisional shortlist until the official draw is available.

| Men's Singles | Women's Singles |
| --- | --- |
| Jannik Sinner | Aryna Sabalenka |
| Novak Djokovic | Elena Rybakina |
| Alexander Zverev | Iga Swiatek |
| Taylor Fritz | Jessica Pegula |
| Daniil Medvedev | Amanda Anisimova |
| Ben Shelton | Coco Gauff |
| Felix Auger-Aliassime | Elina Svitolina |
| Alex de Minaur | Belinda Bencic |

The experimental classifier outputs are research artifacts only. Their temporal Top 8 validation is too weak to replace the heuristic shortlist.

## Phase Status

### Phase 1: Pre-Tournament Quarterfinalists

Status: In progress

Completed:

- Normalized 112,872 historical ATP and WTA matches.
- Parsed the supplied 2026 direct-entry lists.
- Implemented player identity normalization.
- Built ranking, Elo, grass, Wimbledon-history, and recent-form features.
- Added rolling 30/90/180/365-day and last-5/last-10 form trends.
- Backtested transparent heuristic models on historical Wimbledon tournaments.
- Generated provisional men's and women's Top 8 predictions.
- Documented risks, methodology, and model limitations.

Next:

- Import the official 2026 singles draws after publication.
- Split each draw into eight quarterfinal sections.
- Select one projected winner per section so shortlisted players cannot eliminate each other before the quarterfinals.
- Review injuries, withdrawals, qualifiers, and late replacements.
- Re-run reproducibility checks and freeze the final submission.

### Phase 2: Round-of-16 Revision

Status: Not started

Planned:

- Ingest completed tournament results through the Round of 16.
- Recalculate player and path probabilities.
- Compare the expected gain from revisions against the hackathon penalty.
- Submit revisions only when the evidence clears the decision threshold.

### Phase 3: Knockout Predictions

Status: Not started

Planned:

- Predict quarterfinal, semifinal, and final winners.
- Add match-level win probabilities and set-difference estimates.
- Produce concise explanations and confidence tiers.

## Team Assignments

### Rohit Kumar

Owner: submission and coordination

- Obtain and verify the official men's and women's draws.
- Map the final model output into eight draw sections.
- Review injury and withdrawal evidence.
- Freeze and submit the final Phase 1 package.
- Keep Jira, GitHub, and the leadership narrative synchronized.

### Harshit Singh

Owner: modeling and evaluation

- Audit the heuristic and experimental classifier backtests.
- Diagnose the classifier's weak Top 8 retrieval.
- Compare ranking-only, Elo, grass, form, and hybrid approaches.
- Recommend the final scoring method with evidence.
- Document uncertainty around borderline picks and alternates.

### Abhinay Singh

Owner: data engineering and reproducibility

- Validate source row counts, dates, schemas, and player-name mappings.
- Build or document the official-draw ingestion format.
- Run the project from a clean checkout using the documented commands.
- Confirm all generated artifacts and checksums or row counts.
- Record any missing data or manual preparation required.

## Shared Decision Gates

1. Do not submit the experimental classifier as the primary model unless its Top 8 validation improves materially.
2. Do not freeze predictions before the official draw is mapped into eight sections.
3. Do not apply manual injury adjustments without a dated source and written rationale.
4. Do not mark Phase 1 complete until a clean rerun produces the final sixteen names.

## Reproducible Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/process_and_upload.py
python scripts/phase1_model.py
```

Required local inputs are documented in `data/README.md`. Large raw and processed datasets are intentionally excluded from GitHub.

## Key Artifacts

- `scripts/process_and_upload.py`
- `scripts/phase1_model.py`
- `reports/phase1_backtest.csv`
- `reports/phase1_classifier_backtest.csv`
- `reports/phase1_draw_summary_20260624.md`
- `submissions/phase_1_methodology_20260624.md`
- `submissions/phase_1_top8_predictions_20260624.csv`
