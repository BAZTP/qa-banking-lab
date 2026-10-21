"""SQLite local y datos exclusivamente ficticios."""
import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 260_000).hex()


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    try:
        yield db
    finally:
        db.close()


def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id),
            label TEXT NOT NULL, balance INTEGER NOT NULL CHECK(balance >= 0));
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
            source TEXT REFERENCES accounts(id), destination TEXT REFERENCES accounts(id),
            amount INTEGER NOT NULL CHECK(amount > 0), note TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
        ''')
        for uid, username in [(1, 'ana'), (2, 'bruno')]:
            salt = secrets.token_hex(16)
            db.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)',
                       (uid, username, salt, password_hash('Demo123!', salt)))
        for row in [('LAB-ANA-01', 1, 'Cuenta de práctica', 100000),
                    ('LAB-ANA-02', 1, 'Ahorro ficticio', 25000),
                    ('LAB-BRU-01', 2, 'Cuenta de práctica', 75000)]:
            db.execute('INSERT OR IGNORE INTO accounts VALUES (?, ?, ?, ?)', row)
        db.commit()
