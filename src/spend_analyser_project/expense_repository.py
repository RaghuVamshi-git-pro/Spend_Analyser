from datetime import date, time
from pathlib import Path
import sqlite3

from .database import (
    DEFAULT_DATABASE_PATH,
    get_connection,
    initialize_database,
)


def create_expense(
    *,
    amount: float,
    category: str,
    description: str,
    expense_date: date,
    expense_time: time,
    mode_of_payment: str,
    payment_source: str,
    benefits_used: bool,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> int:
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if not category.strip():
        raise ValueError("Category is required.")

    if not mode_of_payment.strip():
        raise ValueError("Mode of payment is required.")

    initialize_database(database_path)

    connection = get_connection(database_path)

    try:
        cursor = connection.execute(
            """
            INSERT INTO expenses (
                amount,
                category,
                description,
                expense_date,
                expense_time,
                mode_of_payment,
                payment_source,
                benefits_used
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                amount,
                category.strip(),
                description.strip(),
                expense_date.isoformat(),
                expense_time.isoformat(),
                mode_of_payment.strip(),
                payment_source.strip(),
                int(benefits_used),
            ),
        )
        connection.commit()

        return int(cursor.lastrowid)
    finally:
        connection.close()


def list_expenses(
    *,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    payment_source: str | None = None,
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[sqlite3.Row]:
    initialize_database(database_path)

    conditions: list[str] = []
    parameters: list[str] = []

    if category is not None:
        conditions.append("category = ?")
        parameters.append(category.strip())

    if start_date is not None:
        conditions.append("expense_date >= ?")
        parameters.append(start_date.isoformat())

    if end_date is not None:
        conditions.append("expense_date <= ?")
        parameters.append(end_date.isoformat())

    if payment_source is not None:
        conditions.append("payment_source = ?")
        parameters.append(payment_source.strip())

    query = """
        SELECT *
        FROM expenses
    """

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY expense_date DESC, expense_time DESC, id DESC
    """

    connection = get_connection(database_path)

    try:
        return connection.execute(query, parameters).fetchall()
    finally:
        connection.close()
