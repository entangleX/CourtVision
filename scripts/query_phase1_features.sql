WITH player_matches AS (
  SELECT
    tour,
    match_date,
    Tournament,
    Surface,
    Round,
    Player_1 AS player_name,
    Player_2 AS opponent_name,
    Winner,
    IF(Winner = Player_1, 1, 0) AS won_match
  FROM `agi-lab-499017.courtvision_raw.match_history_combined`
  UNION ALL
  SELECT
    tour,
    match_date,
    Tournament,
    Surface,
    Round,
    Player_2 AS player_name,
    Player_1 AS opponent_name,
    Winner,
    IF(Winner = Player_2, 1, 0) AS won_match
  FROM `agi-lab-499017.courtvision_raw.match_history_combined`
),
player_rollup AS (
  SELECT
    tour,
    player_name,
    COUNT(*) AS career_matches,
    SUM(won_match) AS career_wins,
    COUNTIF(Surface = 'Grass') AS grass_matches,
    SUM(IF(Surface = 'Grass', won_match, 0)) AS grass_wins,
    COUNTIF(Tournament = 'Wimbledon') AS wimbledon_matches,
    SUM(IF(Tournament = 'Wimbledon', won_match, 0)) AS wimbledon_wins,
    COUNTIF(match_date >= DATE_SUB(DATE '2026-06-28', INTERVAL 90 DAY)) AS recent_matches_90d,
    SUM(IF(match_date >= DATE_SUB(DATE '2026-06-28', INTERVAL 90 DAY), won_match, 0)) AS recent_wins_90d
  FROM player_matches
  WHERE match_date < DATE '2026-06-28'
  GROUP BY tour, player_name
)
SELECT
  e.tour,
  e.player_raw,
  SAFE_CAST(e.rank AS INT64) AS entry_rank,
  SAFE_CAST(e.draw_order AS INT64) AS draw_order,
  r.career_matches,
  r.career_wins,
  SAFE_DIVIDE(r.career_wins, NULLIF(r.career_matches, 0)) AS career_win_rate,
  r.grass_matches,
  r.grass_wins,
  SAFE_DIVIDE(r.grass_wins, NULLIF(r.grass_matches, 0)) AS grass_win_rate,
  r.wimbledon_matches,
  r.wimbledon_wins,
  SAFE_DIVIDE(r.wimbledon_wins, NULLIF(r.wimbledon_matches, 0)) AS wimbledon_win_rate,
  r.recent_matches_90d,
  r.recent_wins_90d,
  SAFE_DIVIDE(r.recent_wins_90d, NULLIF(r.recent_matches_90d, 0)) AS recent_win_rate_90d
FROM `agi-lab-499017.courtvision_raw.wimbledon_2026_mens_entries` e
LEFT JOIN player_rollup r
  ON e.tour = r.tour
 AND e.player_raw = r.player_name

