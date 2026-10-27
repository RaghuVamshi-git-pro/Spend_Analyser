from __future__ import annotations

from datetime import date, time
import os
from typing import Any

import requests
import streamlit as st


DEFAULT_API_URL = "http://127.0.0.1:8000"
API_URL = os.getenv("SPEND_ANALYSER_API_URL", DEFAULT_API_URL).rstrip("/")


def api_request(
    method: str,
    path: str,
    **kwargs: Any,
) -> requests.Response:
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            timeout=10,
            **kwargs,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not connect to the API at {API_URL}."
        ) from error

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"API error ({response.status_code}): {detail}")

    return response


def load_expenses(
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    payment_source: str | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, str] = {}
    if category:
        params["category"] = category
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if payment_source:
        params["payment_source"] = payment_source

    return api_request("GET", "/expenses", params=params).json()


def expense_payload(
    amount: float,
    category: str,
    description: str,
    expense_date: date,
    expense_time: time,
    mode_of_payment: str,
    payment_source: str,
    benefits_used: bool,
) -> dict[str, Any]:
    return {
        "amount": amount,
        "category": category,
        "description": description,
        "expense_date": expense_date.isoformat(),
        "expense_time": expense_time.isoformat(),
        "mode_of_payment": mode_of_payment,
        "payment_source": payment_source,
        "benefits_used": benefits_used,
    }


def render_expense_form(
    existing: dict[str, Any] | None = None,
) -> None:
    editing = existing is not None
    title = "Edit expense" if editing else "Add expense"

    with st.form("expense_form", clear_on_submit=not editing):
        st.subheader(title)
        first_column, second_column = st.columns(2)

        with first_column:
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=float(existing["amount"]) if editing else 0.01,
                step=10.0,
                format="%.2f",
            )
            category = st.text_input(
                "Category",
                value=str(existing["category"]) if editing else "",
            )
            expense_date = st.date_input(
                "Date",
                value=(
                    date.fromisoformat(str(existing["expense_date"]))
                    if editing
                    else date.today()
                ),
            )
            expense_time = st.time_input(
                "Time",
                value=(
                    time.fromisoformat(str(existing["expense_time"]))
                    if editing
                    else time(12, 0)
                ),
            )

        with second_column:
            mode_of_payment = st.text_input(
                "Mode of payment",
                value=(
                    str(existing["mode_of_payment"])
                    if editing
                    else ""
                ),
            )
            payment_source = st.text_input(
                "Payment source",
                value=(
                    str(existing["payment_source"])
                    if editing
                    else ""
                ),
            )
            description = st.text_area(
                "Description",
                value=(
                    str(existing["description"])
                    if editing
                    else ""
                ),
            )
            benefits_used = st.checkbox(
                "Benefits used",
                value=bool(existing["benefits_used"]) if editing else False,
            )

        submitted = st.form_submit_button(
            "Save changes" if editing else "Add expense",
            type="primary",
        )

    if not submitted:
        return

    if not category.strip() or not mode_of_payment.strip():
        st.error("Category and mode of payment are required.")
        return

    payload = expense_payload(
        amount,
        category,
        description,
        expense_date,
        expense_time,
        mode_of_payment,
        payment_source,
        benefits_used,
    )

    try:
        if editing:
            api_request("PUT", f"/expenses/{existing['id']}", json=payload)
            st.success("Expense updated.")
            st.session_state.pop("editing_expense", None)
        else:
            api_request("POST", "/expenses", json=payload)
            st.success("Expense added.")
        st.rerun()
    except RuntimeError as error:
        st.error(str(error))


def render_filters() -> dict[str, Any]:
    st.subheader("Filters")
    first_column, second_column, third_column = st.columns(3)
    with first_column:
        category = st.text_input("Category", key="filter_category")
    with second_column:
        start_date = st.date_input(
            "From date",
            value=None,
            key="filter_start_date",
        )
    with third_column:
        end_date = st.date_input(
            "To date",
            value=None,
            key="filter_end_date",
        )

    payment_source = st.text_input(
        "Payment source",
        key="filter_payment_source",
    )

    return {
        "category": category or None,
        "start_date": start_date,
        "end_date": end_date,
        "payment_source": payment_source or None,
    }


def render_expenses(filters: dict[str, Any]) -> None:
    try:
        expenses = load_expenses(**filters)
    except RuntimeError as error:
        st.error(str(error))
        return

    st.subheader(f"Expenses ({len(expenses)})")
    if not expenses:
        st.info("No expenses match the current filters.")
        return

    for expense in expenses:
        label = (
            f"{expense['expense_date']} · {expense['category']} · "
            f"₹{float(expense['amount']):,.2f}"
        )
        with st.expander(label):
            st.write(
                f"**Description:** {expense['description'] or '—'}  \n"
                f"**Time:** {expense['expense_time']}  \n"
                f"**Payment:** {expense['mode_of_payment']}  \n"
                f"**Source:** {expense['payment_source'] or '—'}  \n"
                f"**Benefits used:** {'Yes' if expense['benefits_used'] else 'No'}"
            )
            edit_column, delete_column = st.columns(2)
            with edit_column:
                if st.button("Edit", key=f"edit_{expense['id']}"):
                    st.session_state["editing_expense"] = expense
                    st.rerun()
            with delete_column:
                if st.button("Delete", key=f"delete_{expense['id']}"):
                    try:
                        api_request("DELETE", f"/expenses/{expense['id']}")
                        st.success("Expense deleted.")
                        st.rerun()
                    except RuntimeError as error:
                        st.error(str(error))


def main() -> None:
    st.set_page_config(
        page_title="Spend Analyser",
        page_icon="💰",
        layout="wide",
    )
    st.title("Spend Analyser")
    st.caption(f"API: {API_URL}")

    editing_expense = st.session_state.get("editing_expense")
    if editing_expense:
        if st.button("Cancel editing"):
            st.session_state.pop("editing_expense", None)
            st.rerun()
        render_expense_form(editing_expense)
    else:
        render_expense_form()

    st.divider()
    filters = render_filters()
    render_expenses(filters)


if __name__ == "__main__":
    main()
