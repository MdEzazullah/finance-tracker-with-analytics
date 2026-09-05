import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, required for running inside Flask
import matplotlib.pyplot as plt

from models.transaction_model import get_transactions
from models.budget_model import get_budgets, check_budget_status
from datetime import date


def _fig_to_base64(fig):
    """Converts a matplotlib figure to a base64 PNG string, embeddable in <img src="data:...">."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110, transparent=True)
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def get_category_breakdown_chart(user_id):
    """
    Pie chart of expense totals by category, all-time.
    Returns a base64 image string, or None if there's no expense data yet.
    """
    transactions = get_transactions(user_id, type_="expense")
    if not transactions:
        return None

    df = pd.DataFrame(transactions)
    df["amount"] = df["amount"].astype(float)

    grouped = df.groupby("category_name")["amount"].sum().sort_values(ascending=False)

    if grouped.empty:
        return None

    colors = ["#4338ca", "#0d9488", "#d97706", "#be123c", "#7c3aed", "#0284c7", "#059669"]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        grouped.values,
        labels=grouped.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors[: len(grouped)],
        textprops={"fontsize": 10, "color": "#16211f"},
        wedgeprops={"edgecolor": "white", "linewidth": 2}
    )
    ax.set_title("Spending by Category", fontsize=13, fontweight="bold", color="#16211f")
    ax.axis("equal")

    return _fig_to_base64(fig)


def get_monthly_trend_chart(user_id):
    """
    Grouped bar chart comparing income vs expense for the last 6 months.
    Returns a base64 image string, or None if there's no transaction data yet.
    """
    transactions = get_transactions(user_id)
    if not transactions:
        return None

    df = pd.DataFrame(transactions)
    df["amount"] = df["amount"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    pivot = df.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0)
    pivot = pivot.sort_index().tail(6)  # last 6 months with data

    if pivot.empty:
        return None

    for col in ["income", "expense"]:
        if col not in pivot.columns:
            pivot[col] = 0

    fig, ax = plt.subplots(figsize=(7, 4.2))
    x = range(len(pivot.index))
    width = 0.35

    ax.bar([i - width / 2 for i in x], pivot["income"], width, label="Income", color="#10b981")
    ax.bar([i + width / 2 for i in x], pivot["expense"], width, label="Expense", color="#e11d48")

    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index, rotation=0, fontsize=9)
    ax.set_ylabel("Amount", fontsize=10)
    ax.set_title("Income vs Expense (Last 6 Months)", fontsize=13, fontweight="bold", color="#16211f")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _fig_to_base64(fig)


def get_summary_stats(user_id):
    """
    Quick text-based insights: highest spending category, and month-over-month change.
    Returns a dict, or a dict with defaults if there's not enough data.
    """
    transactions = get_transactions(user_id, type_="expense")
    if not transactions:
        return {"top_category": None, "top_amount": 0, "mom_change_pct": None}

    df = pd.DataFrame(transactions)
    df["amount"] = df["amount"].astype(float)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")

    by_category = df.groupby("category_name")["amount"].sum().sort_values(ascending=False)
    top_category = by_category.index[0]
    top_amount = round(by_category.iloc[0], 2)

    by_month = df.groupby("month")["amount"].sum().sort_index()
    mom_change_pct = None
    if len(by_month) >= 2:
        prev, curr = by_month.iloc[-2], by_month.iloc[-1]
        if prev > 0:
            mom_change_pct = round(((curr - prev) / prev) * 100, 1)

    return {
        "top_category": top_category,
        "top_amount": top_amount,
        "mom_change_pct": mom_change_pct
    }


def get_budget_vs_actual_chart(user_id):
    """
    Grouped bar chart comparing each category's monthly budget limit
    against what's actually been spent this month.
    Returns a base64 image string, or None if no budgets are set yet.
    """
    user_budgets = get_budgets(user_id)
    if not user_budgets:
        return None

    today = date.today()
    categories = []
    limits = []
    spent_amounts = []

    for b in user_budgets:
        status = check_budget_status(user_id, b["category_id"], today.year, today.month)
        if status:
            categories.append(b["category_name"])
            limits.append(float(status["limit"]))
            spent_amounts.append(float(status["spent"]))

    if not categories:
        return None

    fig, ax = plt.subplots(figsize=(7, 4.2))
    x = range(len(categories))
    width = 0.35

    bar_colors_spent = ["#e11d48" if s > l else "#0d9488" for s, l in zip(spent_amounts, limits)]

    ax.bar([i - width / 2 for i in x], limits, width, label="Budget Limit", color="#c4b5fd")
    ax.bar([i + width / 2 for i in x], spent_amounts, width, label="Spent", color=bar_colors_spent)

    ax.set_xticks(list(x))
    ax.set_xticklabels(categories, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Amount", fontsize=10)
    ax.set_title("Budget vs Actual Spending (This Month)", fontsize=13, fontweight="bold", color="#16211f")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _fig_to_base64(fig)