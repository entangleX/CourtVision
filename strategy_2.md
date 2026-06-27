# Strategy 2: Feature-Rich Gradient Boosting Model

## Best Owner

Harshit

## Core Idea

Build a supervised machine learning model that predicts whether each player reaches the Wimbledon quarterfinals using player-level and draw-level features. This approach focuses on discovering nonlinear relationships across ranking, surface form, recent momentum, historical performance, and draw difficulty.

This should be our strongest machine-learning track and a useful challenger to the Elo simulation.

## Decision This Model Supports

Which players have the highest probability of becoming Wimbledon quarterfinalists after accounting for form, surface fit, history, and draw context?

## Data Inputs

- Historical ATP and WTA match logs.
- Player rankings and entry ranks.
- Historical Wimbledon outcomes.
- Grass-court match results.
- Recent match results before Wimbledon.
- Official 2026 draw sections.
- Seed and opponent-path features.

## Prediction Target

For each player in each historical Wimbledon draw:

```text
target = 1 if player reached the quarterfinals
target = 0 otherwise
```

## Feature Set

Player strength:

- Entry rank.
- Seed.
- Overall win rate.
- Grass-court win rate.
- Wimbledon career win rate.
- Grand Slam win rate.

Recent form:

- Last 5 match win rate.
- Last 10 match win rate.
- Last 20 match win rate.
- Recent grass win rate.
- Recent opponent quality.

Draw context:

- Draw section.
- Average rank of possible opponents before QF.
- Strongest possible seeded opponent before QF.
- Number of dangerous unseeded players in section.
- Whether a top 4 seed is in the same section.

Risk features:

- Injury or retirement flag.
- Recent long-match fatigue.
- First-round upset risk.
- Low grass sample-size flag.

## Modeling Method

Recommended model:

```text
CatBoost or LightGBM classifier
```

Fallback if dependencies are difficult:

```text
sklearn HistGradientBoostingClassifier or RandomForestClassifier
```

Training setup:

1. Create one row per player per Wimbledon year.
2. Use only pre-tournament features.
3. Train on earlier years.
4. Validate on later years using walk-forward validation.
5. Predict 2026 quarterfinal probability for every draw player.
6. Select one highest-probability player per draw section.

## Validation

Primary metric:

- Mean Top 8 hits across historical Wimbledon years.

Secondary metrics:

- Section-level winner accuracy.
- Brier score.
- Precision among top 8 predicted players.
- Calibration curve: predicted probability vs observed QF rate.

Guardrails:

- Avoid random train-test split because that leaks future information.
- Use year-based validation.
- Keep ATP and WTA models separate unless sample size becomes too small.
- Compare against ranking-only, seed-only, and Elo-only baselines.

## Strengths

- Captures nonlinear patterns that simple Elo can miss.
- Can learn interaction effects, such as "strong grass form matters more for lower-ranked players."
- Gives feature importance for presentation.
- Good challenger model for the final ensemble.

## Weaknesses

- Historical Wimbledon sample size is limited.
- Can overfit if too many features are added.
- Needs careful leakage control.
- Less intuitive than Elo unless explained well.

## Deliverables

- `data/processed/strategy_2_player_training_matrix.csv`
- `reports/strategy_2_backtest_results.csv`
- `reports/strategy_2_feature_importance.md`
- `reports/strategy_2_2026_qf_probabilities.csv`
- `submissions/strategy_2_phase1_top8.csv`

## Final Output Format

For each player:

```text
Tour, Section, Player, QF Probability, Rank, Seed, Top Features
```

## Recommendation

Use this as the main ML challenger. If it agrees with Strategy 1, those picks become high-confidence. If it disagrees, investigate whether the difference comes from draw path, surface form, or model overfitting.
