from datetime import date, time
from pathlib import Path

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