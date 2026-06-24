# Wimbledon 2026 Phase 1 Baseline

Generated: 2026-06-24T15:16:16-04:00
Data cutoff: 2026-06-23 (matches available through 2026-06-21)

## Target

Select eight likely quarterfinalists for each singles draw before the tournament.
The official 128-player bracket was not included in the supplied local files, so the provisional heuristic ranks the field globally. The experimental classification matrix is reported separately and is not the primary submission model.

## Selected Heuristic Layer

`ranking_forward` was selected by mean Top 8 overlap on historical Wimbledon backtests from 2015 onward.

| Candidate | Mean Top 8 hits | Draws tested |
| --- | ---: | ---: |
| balanced | 3.11 | 18 |
| grass_forward | 3.11 | 18 |
| ranking_forward | 3.22 | 18 |
| form_forward | 3.22 | 18 |

## Classification Matrix Validation

| Tour | Evaluated seasons | Entrant rows | Mean Brier | Mean log loss | Mean Top 8 hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| ATP | 5 | 626 | 0.0793 | 0.3274 | 0.40 |
| WTA | 7 | 880 | 0.0719 | 0.3022 | 0.86 |

## Provisional Heuristic Predictions

### Men

| Model rank | Player | Entry rank | Heuristic score | Main evidence |
| ---: | --- | ---: | ---: | --- |
| 1 | SINNER, Jannik (ITA) | 1 | 0.926 | strong overall Elo; entry rank 1; strong grass Elo |
| 2 | ZVEREV, Alexander (GER) | 2 | 0.826 | strong overall Elo; strong grass Elo; entry rank 2 |
| 3 | DJOKOVIC, Novak (SRB) | 3 | 0.815 | strong grass Elo; strong overall Elo; 30-3 recent Wimbledon record |
| 4 | FRITZ, Taylor (USA) | 7 | 0.738 | strong grass Elo; strong overall Elo; 15-5 recent Wimbledon record |
| 5 | MEDVEDEV, Daniil | 6 | 0.731 | strong overall Elo; strong grass Elo; 46-20 recent record |
| 6 | SHELTON, Ben (USA) | 5 | 0.728 | strong overall Elo; strong grass Elo; 45-20 recent record |
| 7 | AUGER-ALIASSIME, Felix (CAN) | 4 | 0.709 | strong overall Elo; strong grass Elo; entry rank 4 |
| 8 | DE MINAUR, Alex (AUS) | 8 | 0.703 | strong grass Elo; strong overall Elo; 46-23 recent record |

### Women

| Model rank | Player | Entry rank | Heuristic score | Main evidence |
| ---: | --- | ---: | ---: | --- |
| 1 | SABALENKA, Aryna | 1 | 0.901 | strong overall Elo; entry rank 1; strong grass Elo |
| 2 | RYBAKINA, Elena (KAZ) | 2 | 0.825 | strong overall Elo; strong grass Elo; entry rank 2 |
| 3 | SWIATEK, Iga (POL) | 3 | 0.820 | strong grass Elo; strong overall Elo; entry rank 3 |
| 4 | PEGULA, Jessica (USA) | 5 | 0.747 | strong overall Elo; strong grass Elo; 51-17 recent record |
| 5 | ANISIMOVA, Amanda (USA) | 6 | 0.724 | strong grass Elo; strong overall Elo; 35-13 recent record |
| 6 | SVITOLINA, Elina (UKR) | 7 | 0.717 | strong overall Elo; strong grass Elo; 36-14 recent record |
| 7 | GAUFF, Coco (USA) | 4 | 0.716 | strong overall Elo; strong grass Elo; entry rank 4 |
| 8 | BENCIC, Belinda (SUI) | 10 | 0.685 | strong grass Elo; strong overall Elo; 32-16 recent record |

## Rolling Form Features

- 30/90/180/365-day smoothed win-rate windows from the historical logs.
- Last 5 and last 10 match rolling form snapshots.
- Short-term minus long-term deltas for overall and grass-only form.
- A categorical trend label (`surging`, `improving`, `stable`, `slipping`, `cooling`) for judge-facing explainability.

## Produced Artifacts

- `data/processed/phase1_player_features.csv`
- `data/processed/phase1_rolling_form_trends.csv`
- `data/processed/phase1_draw_classification_matrix.csv`
- `reports/phase1_backtest.csv`
- `reports/phase1_classifier_backtest.csv`
- `reports/phase1_draw_probabilities_20260624.csv`
- `reports/phase1_draw_summary_20260624.md`
- `submissions/phase_1_top8_predictions_20260624.csv`

## Known Gaps

- The final bracket sections are still absent, so this predicts draw strength at the player level rather than a full path through a published bracket.
- The entry PDFs contain 112 direct entries per draw, before qualifiers and late replacements.
- Injury, fitness, withdrawal news, and grass-court warmup events after 2026-06-21 are not included.
- Match logs provide winners, rankings, and scores but not serve/return point-level features.

## Name Matching

- ATP unresolved or ambiguous entries: 1.
- WTA unresolved or ambiguous entries: 0.

Entries listed below are retained with ranking-only evidence when no history exists; ambiguous matches are excluded:
- ATP: GILL, Felix (GBR) (no_history)
