CREATE TYPE state_enum AS ENUM ('NEW', 'INSTALLING', 'RUNNING');
CREATE TABLE IF NOT EXISTS apps (
    uuid UUID PRIMARY KEY,
    kind VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    version VARCHAR(255) NOT NULL,
    description VARCHAR(4096) NOT NULL,
    state state_enum,
    json JSONB NOT NULL
);
