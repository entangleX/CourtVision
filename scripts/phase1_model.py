#!/usr/bin/env python3
"""Build and backtest an explainable Wimbledon Phase 1 baseline."""

from __future__ import annotations

import argparse
import csv
import math
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
SUBMISSIONS_DIR = ROOT / "submissions"
REPORTS_DIR = ROOT / "reports"
MATCH_PATH = PROCESSED_DIR / "match_history_combined.csv"
ENTRY_PATHS = {
    "ATP": PROCESSED_DIR / "wimbledon_2026_mens_entries.csv",
    "WTA": PROCESSED_DIR / "wimbledon_2026_womens_entries.csv",
}
TOURNAMENT_CUTOFF = date(2026, 6, 23)
TREND_WINDOWS = (30, 90, 180, 365)
CLASSIFIER_FEATURES = [
    "rank_strength",
    "overall_elo_pct",
    "grass_elo_pct",
    "recent_form",
    "grass_form",
    "wimbledon_form",
    "form_30d",
    "form_90d",
    "form_180d",
    "form_365d",
    "rolling_form_5",
    "rolling_form_10",
    "form_trend_delta",
    "grass_trend_delta",
]

ROUND_POINTS = {
    "1st Round": 0,
    "2nd Round": 1,
    "3rd Round": 2,
    "4th Round": 3,
    "Quarterfinals": 4,
    "Semifinals": 5,
    "The Final": 6,
}

# Each candidate deliberately stays simple enough to explain to judges.
WEIGHT_CANDIDATES = {
    "balanced": {
        "rank_strength": 0.24,
        "overall_elo_pct": 0.18,
        "grass_elo_pct": 0.22,
        "recent_form": 0.12,
        "grass_form": 0.08,
        "wimbledon_form": 0.08,
        "form_90d": 0.04,
        "rolling_form_5": 0.02,
        "form_trend_delta": 0.02,
    },
    "grass_forward": {
        "rank_strength": 0.20,
        "overall_elo_pct": 0.12,
        "grass_elo_pct": 0.30,
        "recent_form": 0.10,
        "grass_form": 0.12,
        "wimbledon_form": 0.08,
        "form_90d": 0.04,
        "rolling_form_5": 0.02,
        "form_trend_delta": 0.02,
    },
    "ranking_forward": {
        "rank_strength": 0.33,
        "overall_elo_pct": 0.18,
        "grass_elo_pct": 0.17,
        "recent_form": 0.10,
        "grass_form": 0.06,
        "wimbledon_form": 0.08,
        "form_90d": 0.04,
        "rolling_form_5": 0.02,
        "form_trend_delta": 0.02,
    },
    "form_forward": {
        "rank_strength": 0.20,
        "overall_elo_pct": 0.16,
        "grass_elo_pct": 0.18,
        "recent_form": 0.12,
        "grass_form": 0.10,
        "wimbledon_form": 0.08,
        "form_90d": 0.08,
        "rolling_form_5": 0.04,
        "form_trend_delta": 0.04,
    },
}

# Source files occasionally use several abbreviations for one player.
PLAYER_ALIASES = {
    "Bautista R.": "Bautista Agut R.",
    "Carreno-Busta P.": "Carreno Busta P.",
    "Djokovic N.": "Djokovic N.",
    "Pliskova Ka.": "Pliskova K.",
    "Pliskova Kar.": "Pliskova K.",
    "Ruse E-G.": "Ruse E.G.",
    "Struff J-L.": "Struff J.L.",
}

ENTRY_ALIASES = {
    "CARRENO BUSTA, Pablo (ESP)": "Carreno Busta P.",
    "MCNALLY, Caty (USA)": "McNally C.",
    "MERIDA, Daniel (ESP)": "Merida Aguilar D.",
    "OSORIO, Camila (COL)": "Osorio M.",
    "PLISKOVA, Karolina (CZE) SR": "Pliskova K.",
    "RADUCANU, Emma (GBR)": "Raducanu E.",
    "VALLEJO, Adolfo Daniel (PAR)": "Vallejo D.",
}


@dataclass(frozen=True)
class Match:
    tour: str
    match_date: date
    player_1: str
    player_2: str
    winner: str
    surface: str
    tournament: str
    round_name: str
    rank_1: int | None
    rank_2: int | None


def parse_rank(value: str) -> int | None:
    try:
        rank = int(float(value))
    except (TypeError, ValueError):
        return None
    return rank if rank > 0 else None


def ascii_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return re.sub(r"[^a-z]", "", normalized.encode("ascii", "ignore").decode().lower())


def abbreviated_player_key(value: str) -> tuple[str, str]:
    cleaned = value.strip()
    parts = cleaned.split()
    if len(parts) < 2:
        return ascii_key(cleaned), ""
    surname = ascii_key("".join(parts[:-1]))
    initials = ascii_key(parts[-1])
    return surname, initials


def canonical_match_name(value: str) -> str:
    cleaned = value.strip()
    parts = cleaned.split()
    if len(parts) < 2:
        return cleaned
    surname = " ".join(parts[:-1])
    initials = ".".join(ascii_key(parts[-1]).upper()) + "."
    canonical = f"{surname} {initials}"
    return PLAYER_ALIASES.get(canonical, canonical)


def entry_player_key(value: str) -> tuple[str, str]:
    cleaned = re.sub(r"\s+\([A-Z]{3}\)(?:\s+SR)?\s*$", "", value.strip())
    if "," not in cleaned:
        return abbreviated_player_key(cleaned)
    surname, given = [part.strip() for part in cleaned.split(",", 1)]
    initials = "".join(part[0] for part in re.findall(r"[A-Za-zÀ-ÿ]+", given) if part)
    return ascii_key(surname), ascii_key(initials)


def load_matches() -> dict[str, list[Match]]:
    by_tour: dict[str, list[Match]] = defaultdict(list)
    with MATCH_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row["match_date"]:
                continue
            match = Match(
                tour=row["tour"],
                match_date=datetime.strptime(row["match_date"], "%Y-%m-%d").date(),
                player_1=canonical_match_name(row["Player_1"]),
                player_2=canonical_match_name(row["Player_2"]),
                winner=canonical_match_name(row["Winner"]),
                surface=row["Surface"],
                tournament=row["Tournament"],
                round_name=row["Round"],
                rank_1=parse_rank(row["Rank_1"]),
                rank_2=parse_rank(row["Rank_2"]),
            )
            by_tour[match.tour].append(match)
    for matches in by_tour.values():
        matches.sort(key=lambda item: item.match_date)
    return by_tour


def build_name_index(matches: list[Match]) -> dict[tuple[str, str], list[str]]:
    index: dict[tuple[str, str], set[str]] = defaultdict(set)
    for match in matches:
        index[abbreviated_player_key(match.player_1)].add(match.player_1)
        index[abbreviated_player_key(match.player_2)].add(match.player_2)
    return {key: sorted(names) for key, names in index.items()}


def resolve_entry_name(raw_name: str, index: dict[tuple[str, str], list[str]]) -> tuple[str, str]:
    if raw_name in ENTRY_ALIASES:
        return ENTRY_ALIASES[raw_name], "manual_alias"
    surname, initials = entry_player_key(raw_name)
    exact = index.get((surname, initials), [])
    if len(exact) == 1:
        return exact[0], "exact"

    first_initial = initials[:1]
    candidates = sorted(
        {
            player
            for (candidate_surname, candidate_initials), players in index.items()
            if candidate_surname == surname and candidate_initials.startswith(first_initial)
            for player in players
        }
    )
    if len(candidates) == 1:
        return candidates[0], "surname_initial"
    if not candidates:
        return f"ENTRY::{raw_name}", "no_history"
    return "", "ambiguous"


def load_entries(tour: str, matches: list[Match]) -> tuple[list[dict[str, object]], list[str]]:
    index = build_name_index(matches)
    entries: list[dict[str, object]] = []
    issues: list[str] = []
    with ENTRY_PATHS[tour].open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            resolved, match_type = resolve_entry_name(row["player_raw"], index)
            if match_type in {"ambiguous", "no_history"}:
                issues.append(f"{row['player_raw']} ({match_type})")
            entries.append(
                {
                    "tour": tour,
                    "player": resolved,
                    "display_name": row["player_raw"],
                    "rank": int(row["rank"]),
                    "name_match": match_type,
                }
            )
    return entries, issues


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elos(matches: list[Match], cutoff: date) -> tuple[dict[str, float], dict[str, float]]:
    overall: dict[str, float] = defaultdict(lambda: 1500.0)
    grass: dict[str, float] = defaultdict(lambda: 1500.0)
    for match in matches:
        if match.match_date >= cutoff:
            break
        winner = match.winner
        loser = match.player_2 if winner == match.player_1 else match.player_1
        expected = expected_score(overall[winner], overall[loser])
        change = 24.0 * (1.0 - expected)
        overall[winner] += change
        overall[loser] -= change
        if match.surface == "Grass":
            grass_expected = expected_score(grass[winner], grass[loser])
            grass_change = 32.0 * (1.0 - grass_expected)
            grass[winner] += grass_change
            grass[loser] -= grass_change
    return dict(overall), dict(grass)


def win_loss(
    matches: list[Match],
    player: str,
    cutoff: date,
    start: date,
    surface: str | None = None,
    tournament: str | None = None,
) -> tuple[int, int]:
    wins = losses = 0
    for match in matches:
        if match.match_date < start:
            continue
        if match.match_date >= cutoff:
            break
        if surface and match.surface != surface:
            continue
        if tournament and match.tournament != tournament:
            continue
        if player not in (match.player_1, match.player_2):
            continue
        if match.winner == player:
            wins += 1
        else:
            losses += 1
    return wins, losses


def player_history(matches: list[Match], player: str, cutoff: date, surface: str | None = None) -> list[Match]:
    history: list[Match] = []
    for match in matches:
        if match.match_date >= cutoff:
            break
        if surface and match.surface != surface:
            continue
        if player in (match.player_1, match.player_2):
            history.append(match)
    return history


def shrunken_win_rate(wins: int, losses: int, prior_matches: int = 6) -> float:
    return (wins + prior_matches * 0.5) / (wins + losses + prior_matches)


def match_result(match: Match, player: str) -> int:
    return 1 if match.winner == player else 0


def rolling_match_form(matches: list[Match], player: str, cutoff: date, limit: int, surface: str | None = None) -> float:
    history = player_history(matches, player, cutoff, surface=surface)
    selected = history[-limit:]
    if not selected:
        return 0.5
    wins = sum(match_result(match, player) for match in selected)
    losses = len(selected) - wins
    return shrunken_win_rate(wins, losses, prior_matches=max(2, limit // 2))


def rolling_window_form(
    matches: list[Match],
    player: str,
    cutoff: date,
    days: int,
    surface: str | None = None,
) -> float:
    wins, losses = win_loss(matches, player, cutoff, cutoff - timedelta(days=days), surface=surface)
    return shrunken_win_rate(wins, losses)


def trend_bucket(delta: float) -> str:
    if delta >= 0.08:
        return "surging"
    if delta >= 0.02:
        return "improving"
    if delta <= -0.08:
        return "cooling"
    if delta <= -0.02:
        return "slipping"
    return "stable"


def percentile_map(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values, key=lambda player: (values[player], player))
    if len(ordered) <= 1:
        return {player: 0.5 for player in ordered}
    return {player: index / (len(ordered) - 1) for index, player in enumerate(ordered)}


def build_features(
    matches: list[Match],
    entrants: list[dict[str, object]],
    cutoff: date,
) -> list[dict[str, object]]:
    overall_elo, grass_elo = calculate_elos(matches, cutoff)
    eligible = [entry for entry in entrants if entry["player"]]
    overall_values = {str(entry["player"]): overall_elo.get(str(entry["player"]), 1500.0) for entry in eligible}
    grass_values = {str(entry["player"]): grass_elo.get(str(entry["player"]), 1500.0) for entry in eligible}
    overall_pct = percentile_map(overall_values)
    grass_pct = percentile_map(grass_values)

    features: list[dict[str, object]] = []
    for entry in eligible:
        player = str(entry["player"])
        rank = int(entry["rank"])
        recent_wins, recent_losses = win_loss(matches, player, cutoff, cutoff - timedelta(days=365))
        grass_wins, grass_losses = win_loss(
            matches, player, cutoff, cutoff - timedelta(days=3 * 365), surface="Grass"
        )
        wimbledon_wins, wimbledon_losses = win_loss(
            matches, player, cutoff, cutoff - timedelta(days=6 * 365), tournament="Wimbledon"
        )

        form_30d = rolling_window_form(matches, player, cutoff, 30)
        form_90d = rolling_window_form(matches, player, cutoff, 90)
        form_180d = rolling_window_form(matches, player, cutoff, 180)
        form_365d = rolling_window_form(matches, player, cutoff, 365)
        rolling_form_5 = rolling_match_form(matches, player, cutoff, 5)
        rolling_form_10 = rolling_match_form(matches, player, cutoff, 10)
        grass_form_90d = rolling_window_form(matches, player, cutoff, 90, surface="Grass")
        grass_form_365d = rolling_window_form(matches, player, cutoff, 365, surface="Grass")
        form_trend_delta = form_90d - form_365d
        grass_trend_delta = grass_form_90d - grass_form_365d

        features.append(
            {
                **entry,
                "rank_strength": max(0.0, 1.0 - math.log(max(rank, 1)) / math.log(128)),
                "overall_elo": overall_values[player],
                "overall_elo_pct": overall_pct[player],
                "grass_elo": grass_values[player],
                "grass_elo_pct": grass_pct[player],
                "recent_wins": recent_wins,
                "recent_losses": recent_losses,
                "recent_form": shrunken_win_rate(recent_wins, recent_losses),
                "grass_wins_3y": grass_wins,
                "grass_losses_3y": grass_losses,
                "grass_form": shrunken_win_rate(grass_wins, grass_losses),
                "wimbledon_wins_6y": wimbledon_wins,
                "wimbledon_losses_6y": wimbledon_losses,
                "wimbledon_form": shrunken_win_rate(wimbledon_wins, wimbledon_losses),
                "form_30d": form_30d,
                "form_90d": form_90d,
                "form_180d": form_180d,
                "form_365d": form_365d,
                "rolling_form_5": rolling_form_5,
                "rolling_form_10": rolling_form_10,
                "grass_form_90d": grass_form_90d,
                "grass_form_365d": grass_form_365d,
                "form_trend_delta": form_trend_delta,
                "grass_trend_delta": grass_trend_delta,
                "trend_bucket": trend_bucket(form_trend_delta),
            }
        )
    return features


def score_features(features: list[dict[str, object]], weights: dict[str, float]) -> list[dict[str, object]]:
    scored = []
    for row in features:
        score = sum(float(row[name]) * weight for name, weight in weights.items())
        scored.append({**row, "model_score": score})
    return sorted(scored, key=lambda row: (-float(row["model_score"]), int(row["rank"])))


def historical_wimbledon_entrants(matches: list[Match], year: int) -> list[dict[str, object]]:
    first_round = [
        match
        for match in matches
        if match.tournament == "Wimbledon" and match.match_date.year == year and match.round_name == "1st Round"
    ]
    ranks: dict[str, int] = {}
    for match in first_round:
        if match.rank_1:
            ranks[match.player_1] = match.rank_1
        if match.rank_2:
            ranks[match.player_2] = match.rank_2
    return [
        {"tour": matches[0].tour, "player": player, "display_name": player, "rank": rank, "name_match": "historical"}
        for player, rank in ranks.items()
    ]


def actual_quarterfinalists(matches: list[Match], year: int) -> set[str]:
    quarterfinal_matches = [
        match
        for match in matches
        if match.tournament == "Wimbledon"
        and match.match_date.year == year
        and match.round_name == "Quarterfinals"
    ]
    return {player for match in quarterfinal_matches for player in (match.player_1, match.player_2)}


def backtest(matches_by_tour: dict[str, list[Match]]) -> tuple[str, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    totals: dict[str, list[int]] = defaultdict(list)
    for tour, matches in matches_by_tour.items():
        years = sorted(
            {
                match.match_date.year
                for match in matches
                if match.tournament == "Wimbledon" and match.match_date.year >= 2015
            }
        )
        for year in years:
            entrants = historical_wimbledon_entrants(matches, year)
            actual = actual_quarterfinalists(matches, year)
            if len(entrants) < 100 or len(actual) != 8:
                continue
            cutoff = min(
                match.match_date
                for match in matches
                if match.tournament == "Wimbledon" and match.match_date.year == year
            )
            features = build_features(matches, entrants, cutoff)
            for model_name, weights in WEIGHT_CANDIDATES.items():
                predicted = {str(row["player"]) for row in score_features(features, weights)[:8]}
                hits = len(predicted & actual)
                totals[model_name].append(hits)
                rows.append({"tour": tour, "year": year, "model": model_name, "top8_hits": hits})

    selected = max(
        WEIGHT_CANDIDATES,
        key=lambda name: (sum(totals[name]) / max(len(totals[name]), 1), name == "balanced"),
    )
    return selected, rows


def logistic(value: float) -> float:
    if value >= 0:
        exp_term = math.exp(-value)
        return 1.0 / (1.0 + exp_term)
    exp_term = math.exp(value)
    return exp_term / (1.0 + exp_term)


def standardize_rows(
    rows: list[dict[str, object]],
    feature_names: list[str],
    means: dict[str, float] | None = None,
    stds: dict[str, float] | None = None,
) -> tuple[list[list[float]], dict[str, float], dict[str, float]]:
    if means is None or stds is None:
        means = {}
        stds = {}
        for name in feature_names:
            values = [float(row[name]) for row in rows]
            mean_value = sum(values) / len(values)
            variance = sum((value - mean_value) ** 2 for value in values) / len(values)
            means[name] = mean_value
            stds[name] = math.sqrt(variance) or 1.0

    matrix = []
    for row in rows:
        matrix.append([(float(row[name]) - means[name]) / stds[name] for name in feature_names])
    return matrix, means, stds


def fit_logistic_classifier(
    rows: list[dict[str, object]],
    feature_names: list[str],
    target_field: str,
    epochs: int = 1200,
    learning_rate: float = 0.05,
    l2: float = 0.002,
) -> tuple[list[float], float, dict[str, float], dict[str, float]]:
    matrix, means, stds = standardize_rows(rows, feature_names)
    targets = [float(row[target_field]) for row in rows]
    weights = [0.0 for _ in feature_names]
    bias = math.log((sum(targets) + 1.0) / (len(targets) - sum(targets) + 1.0))
    sample_count = len(rows)

    for _ in range(epochs):
        gradients = [0.0 for _ in feature_names]
        bias_gradient = 0.0
        for vector, target in zip(matrix, targets):
            score = sum(weight * value for weight, value in zip(weights, vector)) + bias
            prediction = logistic(score)
            error = prediction - target
            bias_gradient += error
            for index, value in enumerate(vector):
                gradients[index] += error * value
        for index in range(len(weights)):
            gradients[index] = gradients[index] / sample_count + l2 * weights[index]
            weights[index] -= learning_rate * gradients[index]
        bias -= learning_rate * (bias_gradient / sample_count)

    return weights, bias, means, stds


def predict_probabilities(
    rows: list[dict[str, object]],
    feature_names: list[str],
    weights: list[float],
    bias: float,
    means: dict[str, float],
    stds: dict[str, float],
) -> list[float]:
    matrix, _, _ = standardize_rows(rows, feature_names, means=means, stds=stds)
    probabilities = []
    for vector in matrix:
        score = sum(weight * value for weight, value in zip(weights, vector)) + bias
        probabilities.append(logistic(score))
    return probabilities


def add_classifier_probabilities(
    train_rows: list[dict[str, object]],
    prediction_rows: list[dict[str, object]],
) -> tuple[list[float], list[float], dict[str, float]]:
    weights, bias, means, stds = fit_logistic_classifier(train_rows, CLASSIFIER_FEATURES, "target_reached_qf")
    train_probs = predict_probabilities(train_rows, CLASSIFIER_FEATURES, weights, bias, means, stds)
    pred_probs = predict_probabilities(prediction_rows, CLASSIFIER_FEATURES, weights, bias, means, stds)
    weight_map = {name: weight for name, weight in zip(CLASSIFIER_FEATURES, weights)}
    weight_map["bias"] = bias
    return train_probs, pred_probs, weight_map


def build_classification_rows(
    matches: list[Match],
    historical_start_year: int = 2015,
) -> list[dict[str, object]]:
    years = sorted(
        {
            match.match_date.year
            for match in matches
            if match.tournament == "Wimbledon" and match.match_date.year >= historical_start_year
        }
    )
    rows: list[dict[str, object]] = []
    for year in years:
        entrants = historical_wimbledon_entrants(matches, year)
        actual = actual_quarterfinalists(matches, year)
        if len(entrants) < 100 or len(actual) != 8:
            continue
        cutoff = min(
            match.match_date
            for match in matches
            if match.tournament == "Wimbledon" and match.match_date.year == year
        )
        for feature_row in build_features(matches, entrants, cutoff):
            rows.append(
                {
                    **feature_row,
                    "season": year,
                    "cutoff_date": cutoff.isoformat(),
                    "target_reached_qf": 1 if str(feature_row["player"]) in actual else 0,
                    "row_type": "historical",
                }
            )
    return rows


def temporal_classifier_backtest(
    matches_by_tour: dict[str, list[Match]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, float]]]:
    rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, float]] = {}
    for tour, matches in matches_by_tour.items():
        matrix_rows = build_classification_rows(matches)
        years = sorted({int(row["season"]) for row in matrix_rows})
        evaluated_years = 0
        total_brier = 0.0
        total_logloss = 0.0
        total_top8_hits = 0
        for year in years:
            train_rows = [row for row in matrix_rows if int(row["season"]) < year]
            test_rows = [row for row in matrix_rows if int(row["season"]) == year]
            if len(train_rows) < 300 or not test_rows:
                continue
            probabilities, _, _ = add_classifier_probabilities(train_rows, test_rows)
            for row, probability in zip(test_rows, probabilities):
                target = float(row["target_reached_qf"])
                clipped = min(max(probability, 1e-6), 1 - 1e-6)
                total_brier += (clipped - target) ** 2
                total_logloss += -(target * math.log(clipped) + (1.0 - target) * math.log(1.0 - clipped))
                rows.append(
                    {
                        "tour": tour,
                        "year": year,
                        "player": row["display_name"],
                        "entry_rank": row["rank"],
                        "target_reached_qf": int(target),
                        "quarterfinal_probability": f"{probability:.6f}",
                    }
                )
            evaluated_years += 1
            ranked = sorted(
                zip(test_rows, probabilities),
                key=lambda item: (-item[1], int(item[0]["rank"])),
            )[:8]
            total_top8_hits += sum(int(item[0]["target_reached_qf"]) for item in ranked)

        sample_count = len(rows) if not summaries else None
        tour_rows = [row for row in rows if row["tour"] == tour]
        sample_count = len(tour_rows)
        summaries[tour] = {
            "evaluated_years": evaluated_years,
            "sample_count": sample_count,
            "mean_brier": total_brier / sample_count if sample_count else 0.0,
            "mean_logloss": total_logloss / sample_count if sample_count else 0.0,
            "mean_top8_hits": total_top8_hits / evaluated_years if evaluated_years else 0.0,
        }
    return rows, summaries


def explanation(row: dict[str, object]) -> str:
    factors: list[tuple[float, str]] = [
        (float(row["quarterfinal_probability"]), "high classifier probability"),
        (float(row["grass_elo_pct"]), "strong grass Elo"),
        (float(row["overall_elo_pct"]), "strong overall Elo"),
        (float(row["rolling_form_5"]), "strong last-5-match form"),
        (float(row["form_trend_delta"]), f"{row['trend_bucket']} recent trend"),
        (float(row["wimbledon_form"]), f"{row['wimbledon_wins_6y']}-{row['wimbledon_losses_6y']} recent Wimbledon record"),
    ]
    return "; ".join(label for _, label in sorted(factors, reverse=True)[:3])


def heuristic_explanation(row: dict[str, object]) -> str:
    factors: list[tuple[float, str]] = [
        (float(row["rank_strength"]), f"entry rank {row['rank']}"),
        (float(row["overall_elo_pct"]), "strong overall Elo"),
        (float(row["grass_elo_pct"]), "strong grass Elo"),
        (float(row["recent_form"]), f"{row['recent_wins']}-{row['recent_losses']} recent record"),
        (
            float(row["wimbledon_form"]),
            f"{row['wimbledon_wins_6y']}-{row['wimbledon_losses_6y']} recent Wimbledon record",
        ),
    ]
    return "; ".join(label for _, label in sorted(factors, reverse=True)[:3])


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_methodology(
    path: Path,
    selected_model: str,
    backtest_rows: list[dict[str, object]],
    predictions: dict[str, list[dict[str, object]]],
    name_issues: dict[str, list[str]],
    classifier_summary: dict[str, dict[str, float]],
) -> None:
    model_totals: dict[str, list[int]] = defaultdict(list)
    for row in backtest_rows:
        model_totals[str(row["model"])].append(int(row["top8_hits"]))

    lines = [
        "# Wimbledon 2026 Phase 1 Baseline",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Data cutoff: {TOURNAMENT_CUTOFF.isoformat()} (matches available through 2026-06-21)",
        "",
        "## Target",
        "",
        "Select eight likely quarterfinalists for each singles draw before the tournament.",
        "The official 128-player bracket was not included in the supplied local files, so the provisional heuristic ranks the field globally. The experimental classification matrix is reported separately and is not the primary submission model.",
        "",
        "## Selected Heuristic Layer",
        "",
        f"`{selected_model}` was selected by mean Top 8 overlap on historical Wimbledon backtests from 2015 onward.",
        "",
        "| Candidate | Mean Top 8 hits | Draws tested |",
        "| --- | ---: | ---: |",
    ]
    for model_name in WEIGHT_CANDIDATES:
        hits = model_totals[model_name]
        lines.append(f"| {model_name} | {sum(hits) / len(hits):.2f} | {len(hits)} |")

    lines.extend(
        [
            "",
            "## Classification Matrix Validation",
            "",
            "| Tour | Evaluated seasons | Entrant rows | Mean Brier | Mean log loss | Mean Top 8 hits |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for tour in ("ATP", "WTA"):
        summary = classifier_summary[tour]
        lines.append(
            f"| {tour} | {int(summary['evaluated_years'])} | {int(summary['sample_count'])} | "
            f"{summary['mean_brier']:.4f} | {summary['mean_logloss']:.4f} | {summary['mean_top8_hits']:.2f} |"
        )

    lines.extend(["", "## Provisional Heuristic Predictions", ""])
    for tour, label in (("ATP", "Men"), ("WTA", "Women")):
        lines.extend(
            [
                f"### {label}",
                "",
                "| Model rank | Player | Entry rank | Heuristic score | Main evidence |",
                "| ---: | --- | ---: | ---: | --- |",
            ]
        )
        for index, row in enumerate(predictions[tour][:8], start=1):
            lines.append(
                f"| {index} | {row['display_name']} | {row['rank']} | "
                f"{float(row['model_score']):.3f} | {heuristic_explanation(row)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Rolling Form Features",
            "",
            "- 30/90/180/365-day smoothed win-rate windows from the historical logs.",
            "- Last 5 and last 10 match rolling form snapshots.",
            "- Short-term minus long-term deltas for overall and grass-only form.",
            "- A categorical trend label (`surging`, `improving`, `stable`, `slipping`, `cooling`) for judge-facing explainability.",
            "",
            "## Produced Artifacts",
            "",
            "- `data/processed/phase1_player_features.csv`",
            "- `data/processed/phase1_rolling_form_trends.csv`",
            "- `data/processed/phase1_draw_classification_matrix.csv`",
            "- `reports/phase1_backtest.csv`",
            "- `reports/phase1_classifier_backtest.csv`",
            "- `reports/phase1_draw_probabilities_20260624.csv`",
            "- `reports/phase1_draw_summary_20260624.md`",
            "- `submissions/phase_1_top8_predictions_20260624.csv`",
            "",
            "## Known Gaps",
            "",
            "- The final bracket sections are still absent, so this predicts draw strength at the player level rather than a full path through a published bracket.",
            "- The entry PDFs contain 112 direct entries per draw, before qualifiers and late replacements.",
            "- Injury, fitness, withdrawal news, and grass-court warmup events after 2026-06-21 are not included.",
            "- Match logs provide winners, rankings, and scores but not serve/return point-level features.",
            "",
            "## Name Matching",
            "",
            f"- ATP unresolved or ambiguous entries: {len(name_issues['ATP'])}.",
            f"- WTA unresolved or ambiguous entries: {len(name_issues['WTA'])}.",
        ]
    )
    if name_issues["ATP"] or name_issues["WTA"]:
        lines.extend(
            [
                "",
                "Entries listed below are retained with ranking-only evidence when no history exists; ambiguous matches are excluded:",
            ]
        )
        for tour in ("ATP", "WTA"):
            for issue in name_issues[tour]:
                lines.append(f"- {tour}: {issue}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_draw_summary(
    path: Path,
    predictions: dict[str, list[dict[str, object]]],
    classifier_summary: dict[str, dict[str, float]],
    classifier_weights: dict[str, dict[str, float]],
) -> None:
    lines = [
        "# Phase 1 Draw Classification Summary",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "## Validation",
        "",
        "| Tour | Mean Brier | Mean log loss | Mean Top 8 hits |",
        "| --- | ---: | ---: | ---: |",
    ]
    for tour in ("ATP", "WTA"):
        summary = classifier_summary[tour]
        lines.append(
            f"| {tour} | {summary['mean_brier']:.4f} | {summary['mean_logloss']:.4f} | {summary['mean_top8_hits']:.2f} |"
        )

    lines.extend(["", "## Top Probability Drivers", ""])
    for tour in ("ATP", "WTA"):
        lines.append(f"### {tour}")
        lines.append("")
        sorted_weights = sorted(
            ((name, weight) for name, weight in classifier_weights[tour].items() if name != "bias"),
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:5]
        lines.append("| Feature | Weight |")
        lines.append("| --- | ---: |")
        for feature_name, weight in sorted_weights:
            lines.append(f"| {feature_name} | {weight:.4f} |")
        lines.append("")

    lines.extend(["## Leading 2026 Candidates", ""])
    for tour in ("ATP", "WTA"):
        lines.append(f"### {tour}")
        lines.append("")
        lines.append("| Rank | Player | Quarterfinal probability | Trend |")
        lines.append("| ---: | --- | ---: | --- |")
        for index, row in enumerate(predictions[tour][:12], start=1):
            lines.append(
                f"| {index} | {row['display_name']} | {float(row['quarterfinal_probability']):.3f} | {row['trend_bucket']} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Wimbledon Phase 1 baseline.")
    parser.add_argument("--cutoff", default=TOURNAMENT_CUTOFF.isoformat(), help="Prediction cutoff date (YYYY-MM-DD).")
    args = parser.parse_args()
    cutoff = datetime.strptime(args.cutoff, "%Y-%m-%d").date()

    matches_by_tour = load_matches()
    selected_model, backtest_rows = backtest(matches_by_tour)
    weights = WEIGHT_CANDIDATES[selected_model]

    classifier_backtest_rows, classifier_summary = temporal_classifier_backtest(matches_by_tour)

    predictions: dict[str, list[dict[str, object]]] = {}
    heuristic_predictions: dict[str, list[dict[str, object]]] = {}
    name_issues: dict[str, list[str]] = {}
    all_features: list[dict[str, object]] = []
    rolling_trend_rows: list[dict[str, object]] = []
    classification_matrix_rows: list[dict[str, object]] = []
    submission_rows: list[dict[str, object]] = []
    draw_probability_rows: list[dict[str, object]] = []
    classifier_weights: dict[str, dict[str, float]] = {}

    for tour in ("ATP", "WTA"):
        entries, issues = load_entries(tour, matches_by_tour[tour])
        current_features = build_features(matches_by_tour[tour], entries, cutoff)
        scored_features = score_features(current_features, weights)
        historical_rows = build_classification_rows(matches_by_tour[tour])
        train_probs, pred_probs, tour_weights = add_classifier_probabilities(historical_rows, scored_features)
        classifier_weights[tour] = tour_weights

        for row, probability in zip(historical_rows, train_probs):
            classification_matrix_rows.append({**row, "quarterfinal_probability": probability})
        for row, probability in zip(scored_features, pred_probs):
            row["quarterfinal_probability"] = probability
            row["hybrid_score"] = 0.65 * probability + 0.35 * float(row["model_score"])
            classification_matrix_rows.append(
                {
                    **row,
                    "season": 2026,
                    "cutoff_date": cutoff.isoformat(),
                    "target_reached_qf": "",
                    "row_type": "prediction",
                }
            )

        heuristic_predictions[tour] = list(scored_features)
        predictions[tour] = sorted(
            scored_features,
            key=lambda row: (-float(row["quarterfinal_probability"]), -float(row["hybrid_score"]), int(row["rank"])),
        )
        name_issues[tour] = issues
        all_features.extend(predictions[tour])

        for row in predictions[tour]:
            rolling_trend_rows.append(
                {
                    "tour": tour,
                    "player": row["display_name"],
                    "entry_rank": row["rank"],
                    "quarterfinal_probability": f"{float(row['quarterfinal_probability']):.4f}",
                    "form_30d": f"{float(row['form_30d']):.4f}",
                    "form_90d": f"{float(row['form_90d']):.4f}",
                    "form_180d": f"{float(row['form_180d']):.4f}",
                    "form_365d": f"{float(row['form_365d']):.4f}",
                    "rolling_form_5": f"{float(row['rolling_form_5']):.4f}",
                    "rolling_form_10": f"{float(row['rolling_form_10']):.4f}",
                    "grass_form_90d": f"{float(row['grass_form_90d']):.4f}",
                    "grass_form_365d": f"{float(row['grass_form_365d']):.4f}",
                    "form_trend_delta": f"{float(row['form_trend_delta']):.4f}",
                    "grass_trend_delta": f"{float(row['grass_trend_delta']):.4f}",
                    "trend_bucket": row["trend_bucket"],
                }
            )

        for model_rank, row in enumerate(heuristic_predictions[tour][:8], start=1):
            submission_rows.append(
                {
                    "category": "Men's Singles" if tour == "ATP" else "Women's Singles",
                    "model_rank": model_rank,
                    "player": row["display_name"],
                    "entry_rank": row["rank"],
                    "model_score": f"{float(row['model_score']):.4f}",
                    "main_evidence": heuristic_explanation(row),
                }
            )
        for model_rank, row in enumerate(predictions[tour], start=1):
            draw_probability_rows.append(
                {
                    "tour": tour,
                    "model_rank": model_rank,
                    "player": row["display_name"],
                    "entry_rank": row["rank"],
                    "quarterfinal_probability": f"{float(row['quarterfinal_probability']):.4f}",
                    "hybrid_score": f"{float(row['hybrid_score']):.4f}",
                    "trend_bucket": row["trend_bucket"],
                    "main_evidence": explanation(row),
                }
            )

    feature_fields = [
        "tour",
        "player",
        "display_name",
        "rank",
        "name_match",
        "rank_strength",
        "overall_elo",
        "overall_elo_pct",
        "grass_elo",
        "grass_elo_pct",
        "recent_wins",
        "recent_losses",
        "recent_form",
        "grass_wins_3y",
        "grass_losses_3y",
        "grass_form",
        "wimbledon_wins_6y",
        "wimbledon_losses_6y",
        "wimbledon_form",
        "form_30d",
        "form_90d",
        "form_180d",
        "form_365d",
        "rolling_form_5",
        "rolling_form_10",
        "grass_form_90d",
        "grass_form_365d",
        "form_trend_delta",
        "grass_trend_delta",
        "trend_bucket",
        "model_score",
        "quarterfinal_probability",
        "hybrid_score",
    ]
    write_csv(PROCESSED_DIR / "phase1_player_features.csv", all_features, feature_fields)
    write_csv(
        PROCESSED_DIR / "phase1_rolling_form_trends.csv",
        rolling_trend_rows,
        [
            "tour",
            "player",
            "entry_rank",
            "quarterfinal_probability",
            "form_30d",
            "form_90d",
            "form_180d",
            "form_365d",
            "rolling_form_5",
            "rolling_form_10",
            "grass_form_90d",
            "grass_form_365d",
            "form_trend_delta",
            "grass_trend_delta",
            "trend_bucket",
        ],
    )
    write_csv(
        PROCESSED_DIR / "phase1_draw_classification_matrix.csv",
        classification_matrix_rows,
        [
            "tour",
            "season",
            "cutoff_date",
            "row_type",
            "player",
            "display_name",
            "rank",
            "name_match",
            "rank_strength",
            "overall_elo",
            "overall_elo_pct",
            "grass_elo",
            "grass_elo_pct",
            "recent_form",
            "grass_form",
            "wimbledon_form",
            "form_30d",
            "form_90d",
            "form_180d",
            "form_365d",
            "rolling_form_5",
            "rolling_form_10",
            "grass_form_90d",
            "grass_form_365d",
            "form_trend_delta",
            "grass_trend_delta",
            "quarterfinal_probability",
            "target_reached_qf",
        ],
    )
    write_csv(
        REPORTS_DIR / "phase1_backtest.csv",
        backtest_rows,
        ["tour", "year", "model", "top8_hits"],
    )
    write_csv(
        REPORTS_DIR / "phase1_classifier_backtest.csv",
        classifier_backtest_rows,
        ["tour", "year", "player", "entry_rank", "target_reached_qf", "quarterfinal_probability"],
    )
    write_csv(
        REPORTS_DIR / "phase1_draw_probabilities_20260624.csv",
        draw_probability_rows,
        ["tour", "model_rank", "player", "entry_rank", "quarterfinal_probability", "hybrid_score", "trend_bucket", "main_evidence"],
    )
    write_csv(
        SUBMISSIONS_DIR / "phase_1_top8_predictions_20260624.csv",
        submission_rows,
        ["category", "model_rank", "player", "entry_rank", "model_score", "main_evidence"],
    )
    write_methodology(
        SUBMISSIONS_DIR / "phase_1_methodology_20260624.md",
        selected_model,
        backtest_rows,
        heuristic_predictions,
        name_issues,
        classifier_summary,
    )
    write_draw_summary(
        REPORTS_DIR / "phase1_draw_summary_20260624.md",
        predictions,
        classifier_summary,
        classifier_weights,
    )

    print(f"Selected heuristic model: {selected_model}")
    for tour in ("ATP", "WTA"):
        summary = classifier_summary[tour]
        print(
            f"{tour} classifier validation: "
            f"Brier={summary['mean_brier']:.4f}, logloss={summary['mean_logloss']:.4f}, "
            f"mean_top8_hits={summary['mean_top8_hits']:.2f}"
        )
        print(f"{tour} heuristic Top 8:")
        for index, row in enumerate(heuristic_predictions[tour][:8], start=1):
            print(
                f"  {index}. {row['display_name']} "
                f"(score={float(row['model_score']):.3f})"
            )
        print(f"  Name matching issues: {len(name_issues[tour])}")


if __name__ == "__main__":
    main()
