from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR.parent / "data" / "roleforge_v4.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Lightweight migration for databases created by earlier prototypes.
        hero_cols = {row[1] for row in conn.execute("PRAGMA table_info(heroes)").fetchall()}
        if "goal" not in hero_cols:
            conn.execute("ALTER TABLE heroes ADD COLUMN goal TEXT DEFAULT ''")
        item_cols = {row[1] for row in conn.execute("PRAGMA table_info(inventory_items)").fetchall()}
        migrations = {
            "rarity": "ALTER TABLE inventory_items ADD COLUMN rarity TEXT DEFAULT 'commun'",
            "source": "ALTER TABLE inventory_items ADD COLUMN source TEXT DEFAULT 'creation'",
            "created_at": "ALTER TABLE inventory_items ADD COLUMN created_at TEXT DEFAULT ''",
            "updated_at": "ALTER TABLE inventory_items ADD COLUMN updated_at TEXT DEFAULT ''",
        }
        for column, ddl in migrations.items():
            if column not in item_cols:
                conn.execute(ddl)
        conn.commit()


def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO settings(key, value) VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
        conn.commit()


def list_campaigns() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM campaigns ORDER BY updated_at DESC, created_at DESC").fetchall()


def create_campaign(name: str, setting: str = "Fantasy") -> int:
    ts = now_iso()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO campaigns(name, setting, summary, created_at, updated_at) VALUES(?, ?, '', ?, ?)",
            (name, setting, ts, ts),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_campaign(campaign_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()


def get_hero(campaign_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM heroes WHERE campaign_id = ? LIMIT 1", (campaign_id,)).fetchone()


def create_hero(campaign_id: int, hero: dict[str, Any], inventory: list[str], skills: list[tuple[str, str, int]] | None = None) -> int:
    ts = now_iso()
    hp_max = 8 + int(hero["constitution"])
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO heroes(
                campaign_id, name, origin, class_name, portrait_description,
                strength, dexterity, intelligence, charisma, constitution,
                hp_current, hp_max, traits, flaws, goal, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                hero["name"], hero["origin"], hero["class_name"], hero["portrait_description"],
                hero["strength"], hero["dexterity"], hero["intelligence"], hero["charisma"], hero["constitution"],
                hp_max, hp_max, hero["traits"], hero["flaws"], hero.get("goal", ""), ts, ts,
            ),
        )
        hero_id = int(cur.lastrowid)
        for skill_key, skill_name, value in (skills or []):
            conn.execute(
                "INSERT INTO hero_skills(hero_id, skill_key, skill_name, value) VALUES(?, ?, ?, ?)",
                (hero_id, skill_key, skill_name, int(value)),
            )
        for item in inventory:
            item = item.strip()
            if item:
                conn.execute(
                    "INSERT INTO inventory_items(hero_id, name, description, quantity, rarity, source, created_at, updated_at) VALUES(?, ?, '', 1, 'commun', 'creation', ?, ?)",
                    (hero_id, item, ts, ts),
                )
        conn.execute("UPDATE campaigns SET updated_at = ? WHERE id = ?", (ts, campaign_id))
        conn.commit()
        return hero_id


def get_skills(hero_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM hero_skills WHERE hero_id = ? ORDER BY id", (hero_id,)).fetchall()


def get_inventory(hero_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM inventory_items WHERE hero_id = ? ORDER BY id", (hero_id,)).fetchall()


def add_journal_entry(campaign_id: int, role: str, content: str) -> None:
    ts = now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO journal_entries(campaign_id, role, content, created_at) VALUES(?, ?, ?, ?)",
            (campaign_id, role, content, ts),
        )
        conn.execute("UPDATE campaigns SET updated_at = ? WHERE id = ?", (ts, campaign_id))
        conn.commit()


def recent_journal(campaign_id: int, limit: int = 12) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM journal_entries
            WHERE campaign_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (campaign_id, limit),
        ).fetchall()[::-1]


def all_journal(campaign_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM journal_entries WHERE campaign_id = ? ORDER BY id ASC",
            (campaign_id,),
        ).fetchall()



def add_inventory_item(hero_id: int, name: str, description: str = "", quantity: int = 1, rarity: str = "commun", source: str = "conteur") -> None:
    name = name.strip()
    if not name:
        return
    ts = now_iso()
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM inventory_items WHERE hero_id = ? AND lower(name) = lower(?)",
            (hero_id, name),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE inventory_items SET quantity = quantity + ?, description = COALESCE(NULLIF(?, ''), description), rarity = COALESCE(NULLIF(?, ''), rarity), updated_at = ? WHERE id = ?",
                (int(quantity), description, rarity, ts, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO inventory_items(hero_id, name, description, quantity, rarity, source, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (hero_id, name, description, int(quantity), rarity or "commun", source, ts, ts),
            )
        conn.commit()


def remove_inventory_item(hero_id: int, name: str, quantity: int = 1) -> None:
    name = name.strip()
    if not name:
        return
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM inventory_items WHERE hero_id = ? AND lower(name) = lower(?)",
            (hero_id, name),
        ).fetchone()
        if not existing:
            return
        remaining = int(existing["quantity"]) - int(quantity)
        if remaining > 0:
            conn.execute(
                "UPDATE inventory_items SET quantity = ?, updated_at = ? WHERE id = ?",
                (remaining, now_iso(), existing["id"]),
            )
        else:
            conn.execute("DELETE FROM inventory_items WHERE id = ?", (existing["id"],))
        conn.commit()


def add_codex_entry(campaign_id: int, kind: str, name: str, description: str = "", source: str = "conteur") -> None:
    kind = (kind or "entrée").strip().lower()
    name = name.strip()
    if not name:
        return
    ts = now_iso()
    sql = """
        INSERT INTO codex_entries(campaign_id, kind, name, description, discovered_at, source)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(campaign_id, kind, name) DO UPDATE SET
            description = CASE WHEN excluded.description != '' THEN excluded.description ELSE codex_entries.description END,
            source = excluded.source
    """
    with get_connection() as conn:
        conn.execute(sql, (campaign_id, kind, name, description, ts, source))
        conn.commit()


def list_codex_entries(campaign_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM codex_entries WHERE campaign_id = ? ORDER BY kind, name",
            (campaign_id,),
        ).fetchall()
