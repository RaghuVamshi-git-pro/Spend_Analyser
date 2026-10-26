from datetime import date, time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .expense_repository import (
    create_expense,
    delete_expense,
    list_expenses,
    update_expense,
)


app = FastAPI(title="Spend Analyser API")


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    description: str = ""
    expense_date: date
    expense_time: time
    mode_of_payment: str = Field(min_length=1)
    payment_source: str = ""
    benefits_used: bool = False


class ExpenseCreated(BaseModel):
    id: int


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/expenses", response_model=ExpenseCreated, status_code=201)
def add_expense(expense: ExpenseCreate) -> ExpenseCreated:
    try:
        expense_id = create_expense(
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            expense_date=expense.expense_date,
            expense_time=expense.expense_time,
            mode_of_payment=expense.mode_of_payment,
            payment_source=expense.payment_source,
            benefits_used=expense.benefits_used,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return ExpenseCreated(id=expense_id)


@app.get("/expenses")
def get_expenses(
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    payment_source: str | None = None,
) -> list[dict[str, object]]:
    expenses = list_expenses(
        category=category,
        start_date=start_date,
        end_date=end_date,
        payment_source=payment_source,
    )

    return [dict(expense) for expense in expenses]


@app.put("/expenses/{expense_id}", response_model=ExpenseCreated)
def edit_expense(
    expense_id: int,
    expense: ExpenseCreate,
) -> ExpenseCreated:
    try:
        updated = update_expense(
            expense_id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            expense_date=expense.expense_date,
            expense_time=expense.expense_time,
            mode_of_payment=expense.mode_of_payment,
            payment_source=expense.payment_source,
            benefits_used=expense.benefits_used,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Expense {expense_id} was not found.",
        )

    return ExpenseCreated(id=expense_id)


@app.delete("/expenses/{expense_id}")
def remove_expense(expense_id: int) -> dict[str, object]:
    deleted = delete_expense(expense_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Expense {expense_id} was not found.",
        )

    return {
        "id": expense_id,
        "deleted": True,
    }