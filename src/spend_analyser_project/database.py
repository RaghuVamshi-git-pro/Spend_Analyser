from pathlib import Path
import sqlite3
from typing import Final


DEFAULT_DATABASE_PATH: Final[Path] = Path("data") / "expenses.db"


CREATE_EXPENSES_TABLE: Final[str] = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    expense_date TEXT NOT NULL,
    expense_time TEXT NOT NULL,
    mode_of_payment TEXT NOT NULL,
    payment_source TEXT NOT NULL DEFAULT '',
    benefits_used INTEGER NOT NULL CHECK (benefits_used IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def get_connection(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> None:
    connection = get_connection(database_path)

    try:
        connection.execute(CREATE_EXPENSES_TABLE)
        connection.commit()
    finally:
        connection.close()