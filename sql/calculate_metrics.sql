-- Engineering the Beautiful Game
-- Team-match performance metrics

BEGIN;

-- Rebuild the statistics table from source events
DELETE FROM team_match_stats;

WITH team_matches AS (
    SELECT
        match_id,
        home_team_id AS team_id,
        home_result AS result
    FROM matches

    UNION ALL

    SELECT
        match_id,
        away_team_id AS team_id,
        away_result AS result
    FROM matches
),

event_metrics AS (
    SELECT
        match_id,
        team_id,

        COUNT(*) FILTER (
            WHERE event_type = 'Pass'
        ) AS total_passes,

        COUNT(*) FILTER (
            WHERE event_type = 'Pass'
              AND pass_outcome IS NULL
        ) AS completed_passes,

        COUNT(*) FILTER (
            WHERE event_type = 'Pass'
              AND pass_outcome IS NULL
              AND start_x IS NOT NULL
              AND end_x IS NOT NULL
              AND end_x - start_x >= 10
        ) AS progressive_passes,

        COUNT(*) FILTER (
            WHERE event_type = 'Carry'
              AND start_x IS NOT NULL
              AND end_x IS NOT NULL
              AND end_x - start_x >= 10
        ) AS progressive_carries,

        -- Successful passes and carries entering the final third
        COUNT(*) FILTER (
            WHERE (
            (event_type = 'Pass' AND pass_outcome IS NULL)
            OR event_type = 'Carry'
            )
            AND start_x < 80
            AND end_x >= 80
        ) AS final_third_entries,

        -- Distinct possessions containing at least one shot
        COUNT(DISTINCT possession) FILTER (
            WHERE event_type = 'Shot'
        ) AS shot_producing_possessions,

        COUNT(*) FILTER (
            WHERE event_type = 'Shot'
        ) AS total_shots,

        COALESCE(
            SUM(shot_xg) FILTER (
                WHERE event_type = 'Shot'
            ), 0
        ) AS total_xg

    FROM events
    GROUP BY match_id, team_id
)

INSERT INTO team_match_stats (
    match_id,
    team_id,
    result,
    total_passes,
    completed_passes,
    pass_completion_rate,
    progressive_passes,
    progressive_carries,
    final_third_entries,
    shot_producing_possessions,
    total_shots,
    total_xg
)

SELECT
    tm.match_id,
    tm.team_id,
    tm.result,
    COALESCE(em.total_passes, 0),
    COALESCE(em.completed_passes, 0),

    ROUND(
        100.0 * COALESCE(em.completed_passes, 0)
        / NULLIF(em.total_passes, 0),
        2
    ),

    COALESCE(em.progressive_passes, 0),
    COALESCE(em.progressive_carries, 0),
    COALESCE(em.final_third_entries, 0),
    COALESCE(em.shot_producing_possessions, 0),
    COALESCE(em.total_shots, 0),
    COALESCE(em.total_xg, 0)

FROM team_matches tm
LEFT JOIN event_metrics em
    ON tm.match_id = em.match_id
   AND tm.team_id = em.team_id;

COMMIT;