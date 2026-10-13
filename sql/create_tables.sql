-- Engineering the Beautiful Game
-- PostgreSQL database schema

-- 1. Matches table
CREATE TABLE IF NOT EXISTS matches (
    match_id BIGINT PRIMARY KEY,
    match_date DATE NOT NULL,
    home_team_id INTEGER NOT NULL,
    home_team VARCHAR(150) NOT NULL,
    away_team_id INTEGER NOT NULL,
    away_team VARCHAR(150) NOT NULL,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    home_result VARCHAR(10) NOT NULL,
    away_result VARCHAR(10) NOT NULL,

    CONSTRAINT valid_scores
        CHECK (home_score >= 0 AND away_score >= 0),

    CONSTRAINT valid_home_result
        CHECK (home_result IN ('Win', 'Loss', 'Draw')),

    CONSTRAINT valid_away_result
        CHECK (away_result IN ('Win', 'Loss', 'Draw'))
);

-- 2. Events table
CREATE TABLE IF NOT EXISTS events (
    match_id BIGINT NOT NULL,
    event_id UUID PRIMARY KEY,
    event_index INTEGER,
    period INTEGER,
    minute INTEGER,
    second INTEGER,
    event_type VARCHAR(100),
    team_id INTEGER,
    team_name VARCHAR(150),
    player_id INTEGER,
    possession INTEGER,
    possession_team_id INTEGER,
    start_x DOUBLE PRECISION,
    start_y DOUBLE PRECISION,
    end_x DOUBLE PRECISION,
    end_y DOUBLE PRECISION,
    pass_outcome VARCHAR(100),
    pass_length DOUBLE PRECISION,
    pass_angle DOUBLE PRECISION,
    shot_outcome VARCHAR(100),
    shot_xg DOUBLE PRECISION,

    CONSTRAINT fk_match
        FOREIGN KEY (match_id)
        REFERENCES matches(match_id),

    CONSTRAINT valid_shot_xg
        CHECK (shot_xg BETWEEN 0 AND 1)
);

-- 3. Team-match statistics table
CREATE TABLE IF NOT EXISTS team_match_stats (
    match_id BIGINT NOT NULL,
    team_id INTEGER NOT NULL,
    result VARCHAR(10) NOT NULL,
    total_passes INTEGER,
    completed_passes INTEGER,
    pass_completion_rate DOUBLE PRECISION,
    progressive_passes INTEGER,
    progressive_carries INTEGER,
    final_third_entries INTEGER,
    total_shots INTEGER,
    total_xg DOUBLE PRECISION,
    shot_producing_possessions INTEGER,

    PRIMARY KEY (match_id, team_id),

    FOREIGN KEY (match_id)
        REFERENCES matches(match_id),

    CONSTRAINT valid_result
        CHECK (result IN ('Win', 'Loss', 'Draw'))
);

-- 4. Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_events_match
    ON events(match_id);

CREATE INDEX IF NOT EXISTS idx_events_team
    ON events(team_id);

CREATE INDEX IF NOT EXISTS idx_events_type
    ON events(event_type);

CREATE INDEX IF NOT EXISTS idx_events_possession
    ON events(match_id, possession);