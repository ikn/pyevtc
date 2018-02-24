DROP TABLE IF EXISTS "metadata";
CREATE TABLE "metadata" (
    "name" TEXT NOT NULL UNIQUE,
    "value" TEXT NOT NULL
);

DROP TABLE IF EXISTS "entities";
CREATE TABLE "entities" (
    "type" INT NOT NULL,
    "subtype" INT NOT NULL,
    "player_elite_spec" INT,
    "id" INT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "account" TEXT,
    "subgroup" TEXT,
    "toughness" INT NOT NULL,
    "concentration" INT NOT NULL,
    "healing" INT NOT NULL,
    "condition_damage" INT NOT NULL
);

CREATE INDEX "idx_entities_type" ON "entities" ("type");

DROP TABLE IF EXISTS "skills";
CREATE TABLE "skills" (
    "id" INT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL
);

DROP TABLE IF EXISTS "events";
CREATE TABLE "events" (
    "type" INT NOT NULL,
    "subtype" INT,
    "time" INT NOT NULL,
    "source_entity_id" INT NOT NULL REFERENCES "entities" ("id"),
    "dest_entity_id" INT NOT NULL REFERENCES "entities" ("id"),
    "skill_id" INT NOT NULL REFERENCES "skills" ("id"),
    "value" INT NOT NULL,
    "buff_damage" INT NOT NULL,
    "team" INT NOT NULL,
    "hit_result" INT NOT NULL,
    "hit_barrier" INT NOT NULL
);

CREATE INDEX "idx_events_type" ON "events" ("type");
CREATE INDEX "idx_events_time" ON "events" ("time");
