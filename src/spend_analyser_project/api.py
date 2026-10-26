from datetime import date, time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .expense_repository import create_expense


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