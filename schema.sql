CREATE TABLE game_states (
    slug        VARCHAR(64)     PRIMARY KEY,
    game_state  JSONB           NOT NULL
);

CREATE TABLE admin (
    password        VARCHAR(64)     PRIMARY KEY
);