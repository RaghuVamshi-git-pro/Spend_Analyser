from pathlib import Path

from spend_analyser_project.database import get_connection, initialize_database


def test_initialize_database_creates_expenses_table(tmp_path: Path) -> None:
    database_path = tmp_path / "expenses.db"

    initialize_database(database_path)

    assert database_path.exists()

    with get_connection(database_path) as connection:
        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'expenses'
            """
        ).fetchone()

    assert table is not None