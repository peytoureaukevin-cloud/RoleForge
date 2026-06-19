from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR.parent / "data" / "roleforge_v3.db"
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
        cols = {row[1] for row in conn.execute("PRAGMA table_info(heroes)").fetchall()}
        if "goal" not in cols:
            conn.execute("ALTER TABLE heroes ADD COLUMN goal TEXT DEFAULT ''")
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
                    "INSERT INTO inventory_items(hero_id, name, description, quantity) VALUES(?, ?, '', 1)",
                    (hero_id, item),
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
