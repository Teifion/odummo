BEGIN;

CREATE TABLE odummo_profiles (
    "user" INTEGER NOT NULL,
    matchmaking BOOLEAN NOT NULL,
    last_move TIMESTAMP WITHOUT TIME ZONE,
    
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    
    PRIMARY KEY ("user"),
    FOREIGN KEY("user") REFERENCES users (id)
);
CREATE INDEX ix_odummo_profiles_user ON odummo_profiles ("user");

CREATE TABLE odummo_games (
    id SERIAL NOT NULL,
    turn INTEGER,
    started TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    player1 INTEGER NOT NULL,
    player2 INTEGER NOT NULL,
    winner INTEGER,
    overall_state VARCHAR NOT NULL,
    current_state VARCHAR NOT NULL,
    active_board INTEGER NOT NULL,
    rematch INTEGER,
    source INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(player1) REFERENCES users (id),
    FOREIGN KEY(player2) REFERENCES users (id),
    FOREIGN KEY(winner) REFERENCES users (id),
    FOREIGN KEY(rematch) REFERENCES odummo_games (id),
    FOREIGN KEY(source) REFERENCES odummo_games (id)
);
CREATE INDEX ix_odummo_games_player2 ON odummo_games (player2);
CREATE INDEX ix_odummo_games_player1 ON odummo_games (player1);

CREATE TABLE odummo_moves (
    id SERIAL NOT NULL,
    game INTEGER NOT NULL,
    player INTEGER NOT NULL,
    move INTEGER NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(game) REFERENCES odummo_games (id),
    FOREIGN KEY(player) REFERENCES users (id)
);
CREATE INDEX ix_odummo_moves_player ON odummo_moves (player);

COMMIT;