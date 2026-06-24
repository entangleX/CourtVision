# Phase 1 Work Plan

## Objective

Submit eight predicted Wimbledon 2026 quarterfinalists for men's singles and eight for women's singles by 28 June 2026 at 11:59 PM IST.

## Task Board

| Priority | Task | Output | Status |
| --- | --- | --- | --- |
| P0 | Normalize match history and 2026 entry lists | `data/processed/*.csv` | Done |
| P0 | Resolve entry-list names to match-history player IDs | Name-match diagnostics | Done; one ATP entrant has no history |
| P0 | Build ranking, Elo, grass, recent-form, and Wimbledon features | `phase1_player_features.csv` | Done |
| P0 | Backtest candidate baselines on historical Wimbledon draws | `reports/phase1_backtest.csv` | Done |
| P0 | Generate initial men's and women's Top 8 | Phase 1 prediction CSV | Done; baseline only |
| P0 | Add the official 2026 draw and select one favorite per section | Draw-aware prediction revision | Blocked until draw is available |
| P1 | Review withdrawals, injuries, and current grass-season news | Risk-adjustment notes | Initial review done; monitor daily |
| P1 | Team review and freeze final submission | Final CSV and methodology | Not started |
| P2 | Add serve/return statistics if a reliable source is available | Model enhancement | Not started |

## Decision Gates

1. Use historical Top 8 overlap to select the baseline weighting.
2. Do not finalize Phase 1 until direct-entry name matching is reviewed.
3. Re-run after the official draw is published because quarterfinalists must come from eight separate draw sections.
4. Apply manual injury or withdrawal adjustments only when a source and rationale are documented.

## Local Commands

```bash
python3 scripts/process_and_upload.py
python3 scripts/phase1_model.py
```

## Definition of Done

- Sixteen predictions are present: eight men and eight women.
- Every prediction has a model score and human-readable evidence.
- Historical backtest results are saved.
- Data cutoff, known gaps, and any manual adjustments are documented.
- The final file has been reviewed before the submission deadline.
