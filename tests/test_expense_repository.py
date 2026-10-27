from datetime import date, time
from pathlib import Path

from spend_analyser_project.database import get_connection
from spend_analyser_project.expense_repository import create_expense


def test_create_expense_stores_all_fields(tmp_path: Path) -> None:
    database_path = tmp_path / "expenses.db"

    expense_id = create_expense(
        amount=450.50,
        category="Food",
        description="Lunch",
        expense_date=date(2026, 10, 26),
        expense_time=time(13, 30),
        mode_of_payment="Credit Card",
        payment_source="Amazon ICICI Card",
        benefits_used=True,
        database_path=database_path,
    )

    assert expense_id == 1

    with get_connection(database_path) as connection:
        expense = connection.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()

    assert expense is not None
    assert expense["amount"] == 450.50
    assert expense["category"] == "Food"
    assert expense["description"] == "Lunch"
    assert expense["expense_date"] == "2026-10-26"
    assert expense["expense_time"] == "13:30:00"
    assert expense["mode_of_payment"] == "Credit Card"
    assert expense["payment_source"] == "Amazon ICICI Card"
    assert expense["benefits_used"] == 1

from spend_analyser_project.expense_repository import list_expenses

def test_list_expenses_filters_by_category(tmp_path: Path) -> None:
    database_path = tmp_path / "expenses.db"

    create_expense(
        amount=450.50,
        category="Food",
        description="Lunch",
        expense_date=date(2026, 10, 26),
        expense_time=time(13, 30),
        mode_of_payment="Credit Card",
        payment_source="Amazon ICICI Card",
        benefits_used=True,
        database_path=database_path,
    )

    create_expense(
        amount=1000.00,
        category="Travel",
        description="Taxi",
        expense_date=date(2026, 10, 26),
        expense_time=time(14, 00),
        mode_of_payment="UPI",
        payment_source="Google Pay",
        benefits_used=False,
        database_path=database_path,
    )

    food_expenses = list_expenses(
        category="Food",
        database_path=database_path,
    )

    assert len(food_expenses) == 1
    assert food_expenses[0]["category"] == "Food"
    assert food_expenses[0]["description"] == "Lunch"


from spend_analyser_project.expense_repository import update_expense


def test_update_expense_changes_saved_values(tmp_path: Path) -> None:
    database_path = tmp_path / "expenses.db"

    expense_id = create_expense(
        amount=450.50,
        category="Food",
        description="Lunch",
        expense_date=date(2026, 10, 26),
        expense_time=time(13, 30),
        mode_of_payment="Credit Card",
        payment_source="Amazon ICICI Card",
        benefits_used=True,
        database_path=database_path,
    )

    updated = update_expense(
        expense_id,
        amount=500.00,
        category="Food",
        description="Dinner",
        expense_date=date(2026, 10, 26),
        expense_time=time(19, 30),
        mode_of_payment="UPI",
        payment_source="Google Pay",
        benefits_used=False,
        database_path=database_path,
    )

    assert updated is True

    expenses = list_expenses(database_path=database_path)

    assert len(expenses) == 1
    assert expenses[0]["amount"] == 500.00
    assert expenses[0]["description"] == "Dinner"
    assert expenses[0]["expense_time"] == "19:30:00"
    assert expenses[0]["mode_of_payment"] == "UPI"
    assert expenses[0]["benefits_used"] == 0


from spend_analyser_project.expense_repository import delete_expense


def test_delete_expense_removes_saved_expense(tmp_path: Path) -> None:
    database_path = tmp_path / "expenses.db"

    expense_id = create_expense(
        amount=450.50,
        category="Food",
        description="Lunch",
        expense_date=date(2026, 10, 26),
        expense_time=time(13, 30),
        mode_of_payment="Credit Card",
        payment_source="Amazon ICICI Card",
        benefits_used=True,
        database_path=database_path,
    )

    deleted = delete_expense(
        expense_id,
        database_path=database_path,
    )

    assert deleted is True
    assert list_expenses(database_path=database_path) == []

    deleting_again = delete_expense(
        expense_id,
        database_path=database_path,
    )

    assert deleting_again is False