from typing import Optional

import aiosqlite

import config

_conn: Optional[aiosqlite.Connection] = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trusted_users (
    user_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS banned_users (
    user_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS edit_ignored_chats (
    chat_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS trusted_chats (
    chat_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS food_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    size REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS treats (
    name TEXT PRIMARY KEY,
    nutrition REAL NOT NULL,
    times_eaten INTEGER NOT NULL
);
"""


async def init() -> None:
    global _conn
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = await aiosqlite.connect(config.DB_PATH)
    await _conn.executescript(_SCHEMA)
    await _conn.execute("INSERT OR IGNORE INTO food_state (id, size) VALUES (1, 0.1)")
    await _conn.commit()


async def close() -> None:
    if _conn is not None:
        await _conn.close()


# --- друзья / враги ------------------------------------------------------

async def is_trusted(user_id: int) -> bool:
    cur = await _conn.execute("SELECT 1 FROM trusted_users WHERE user_id = ?", (user_id,))
    return (await cur.fetchone()) is not None


async def is_banned(user_id: int) -> bool:
    cur = await _conn.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (user_id,))
    return (await cur.fetchone()) is not None


async def add_trusted(user_id: int) -> None:
    await _conn.execute("INSERT OR IGNORE INTO trusted_users (user_id) VALUES (?)", (user_id,))
    await _conn.commit()


async def remove_trusted(user_id: int) -> None:
    await _conn.execute("DELETE FROM trusted_users WHERE user_id = ?", (user_id,))
    await _conn.commit()


async def add_banned(user_id: int) -> None:
    await _conn.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (user_id,))
    await _conn.commit()


async def remove_banned(user_id: int) -> None:
    await _conn.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
    await _conn.commit()


# --- реакция на правки сообщений ----------------------------------------

async def is_edit_ignored(chat_id: int) -> bool:
    cur = await _conn.execute("SELECT 1 FROM edit_ignored_chats WHERE chat_id = ?", (chat_id,))
    return (await cur.fetchone()) is not None


async def set_edit_ignored(chat_id: int, ignored: bool) -> None:
    if ignored:
        await _conn.execute(
            "INSERT OR IGNORE INTO edit_ignored_chats (chat_id) VALUES (?)", (
                chat_id,)
        )
    else:
        await _conn.execute("DELETE FROM edit_ignored_chats WHERE chat_id = ?", (chat_id,))
    await _conn.commit()


# --- доверенные чаты ---------------------------------------------------

async def is_trusted_chat(chat_id: int) -> bool:
    cur = await _conn.execute("SELECT 1 FROM trusted_chats WHERE chat_id = ?", (chat_id,))
    return (await cur.fetchone()) is not None


async def add_trusted_chat(chat_id: int) -> None:
    await _conn.execute("INSERT OR IGNORE INTO trusted_chats (chat_id) VALUES (?)", (chat_id,))
    await _conn.commit()


async def remove_trusted_chat(chat_id: int) -> None:
    await _conn.execute("DELETE FROM trusted_chats WHERE chat_id = ?", (chat_id,))
    await _conn.commit()


# --- кормление ---------------------------------------------------------

async def get_size() -> float:
    cur = await _conn.execute("SELECT size FROM food_state WHERE id = 1")
    row = await cur.fetchone()
    return row[0]


async def set_size(value: float) -> None:
    await _conn.execute("UPDATE food_state SET size = ? WHERE id = 1", (value,))
    await _conn.commit()


async def get_treat(name: str) -> Optional[tuple]:
    cur = await _conn.execute(
        "SELECT nutrition, times_eaten FROM treats WHERE name = ?", (name,)
    )
    return await cur.fetchone()


async def feed_treat(name: str, nutrition: float) -> None:
    existing = await get_treat(name)
    if existing:
        await _conn.execute(
            "UPDATE treats SET times_eaten = times_eaten + 1 WHERE name = ?", (
                name,)
        )
    else:
        await _conn.execute(
            "INSERT INTO treats (name, nutrition, times_eaten) VALUES (?, ?, 1)",
            (name, nutrition),
        )
    await _conn.commit()


async def delete_treat(name: str) -> None:
    await _conn.execute("DELETE FROM treats WHERE name = ?", (name,))
    await _conn.commit()


async def top_treats_by_nutrition(limit: int) -> list:
    cur = await _conn.execute(
        "SELECT name, nutrition FROM treats ORDER BY nutrition DESC LIMIT ?", (
            limit,)
    )
    return await cur.fetchall()


async def top_treats_by_times_eaten(limit: int) -> list:
    cur = await _conn.execute(
        "SELECT name, times_eaten FROM treats ORDER BY times_eaten DESC LIMIT ?", (
            limit,)
    )
    return await cur.fetchall()
