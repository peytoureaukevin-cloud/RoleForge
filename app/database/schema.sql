CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    setting TEXT NOT NULL,
    summary TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    origin TEXT DEFAULT '',
    class_name TEXT DEFAULT '',
    portrait_description TEXT DEFAULT '',
    strength INTEGER NOT NULL,
    dexterity INTEGER NOT NULL,
    intelligence INTEGER NOT NULL,
    charisma INTEGER NOT NULL,
    constitution INTEGER NOT NULL,
    hp_current INTEGER NOT NULL,
    hp_max INTEGER NOT NULL,
    traits TEXT DEFAULT '',
    flaws TEXT DEFAULT '',
    goal TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hero_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER NOT NULL,
    skill_key TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    value INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (hero_id) REFERENCES heroes(id) ON DELETE CASCADE,
    UNIQUE(hero_id, skill_key)
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    quantity INTEGER DEFAULT 1,
    rarity TEXT DEFAULT 'commun',
    source TEXT DEFAULT 'creation',
    created_at TEXT DEFAULT '',
    updated_at TEXT DEFAULT '',
    FOREIGN KEY (hero_id) REFERENCES heroes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);


CREATE TABLE IF NOT EXISTS codex_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    discovered_at TEXT NOT NULL,
    source TEXT DEFAULT 'conteur',
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, kind, name)
);
