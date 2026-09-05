from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from config import Config
from models.user_model import create_user, verify_user
from models.transaction_model import add_transaction, get_transactions, delete_transaction
from models.category_model import get_all_categories
from models.budget_model import set_budget, get_budgets, check_budget_status
from analytics import get_category_breakdown_chart, get_monthly_trend_chart, get_summary_stats, get_budget_vs_actual_chart
from datetime import date

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


@app.context_processor
def inject_user_avatar():
    email = session.get("user_email")
    avatar_url = None
    if email:
        email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
        avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
    return dict(avatar_url=avatar_url, current_user_email=email, current_user_name=session.get("user_name"))


def login_required(view_func):
    """Simple decorator to block access to pages unless the user is logged in."""
    from functools import wraps

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        new_id = create_user(name, email, password)
        if new_id:
            flash("Account created! Please log in.")
            return redirect(url_for("login"))
        else:
            flash("That email is already registered.")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = verify_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    transactions = get_transactions(user_id)

    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expense

    return render_template(
        "dashboard.html",
        transactions=transactions[:5],  # show only the 5 most recent on the dashboard
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )


@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    user_id = session["user_id"]

    if request.method == "POST":
        category_id = request.form["category_id"]
        amount = request.form["amount"]
        type_ = request.form["type"]
        date = request.form["date"]
        description = request.form.get("description", "")

        add_transaction(user_id, category_id, amount, type_, date, description)
        flash("Transaction added.")
        return redirect(url_for("transactions"))

    all_transactions = get_transactions(user_id)
    categories = get_all_categories()
    return render_template("transactions.html", transactions=all_transactions, categories=categories)


@app.route("/transactions/delete/<int:transaction_id>")
@login_required
def delete_transaction_route(transaction_id):
    delete_transaction(transaction_id)
    flash("Transaction deleted.")
    return redirect(url_for("transactions"))


@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    user_id = session["user_id"]

    if request.method == "POST":
        category_id = request.form["category_id"]
        monthly_limit = request.form["monthly_limit"]
        set_budget(user_id, category_id, monthly_limit)
        flash("Budget saved.")
        return redirect(url_for("budgets"))

    categories = get_all_categories(type_="expense")
    user_budgets = get_budgets(user_id)

    today = date.today()
    budget_status = []
    for b in user_budgets:
        status = check_budget_status(user_id, b["category_id"], today.year, today.month)
        if status:
            limit = float(status["limit"])
            spent = float(status["spent"])
            pct = round((spent / limit * 100), 1) if limit > 0 else 0
            pct = min(pct, 100)  # cap the bar at 100% even if over budget

            budget_status.append({
                "category_name": b["category_name"],
                "limit": status["limit"],
                "spent": status["spent"],
                "remaining": status["remaining"],
                "over_budget": status["over_budget"],
                "pct": pct
            })

    return render_template("budgets.html", categories=categories, budget_status=budget_status)


@app.route("/analytics")
@login_required
def analytics():
    user_id = session["user_id"]
    view = request.args.get("view", "category")  # 'category' or 'trend' — defaults to category

    category_chart = get_category_breakdown_chart(user_id) if view == "category" else None
    trend_chart = get_monthly_trend_chart(user_id) if view == "trend" else None
    budget_chart = get_budget_vs_actual_chart(user_id) if view == "budget" else None
    stats = get_summary_stats(user_id)

    return render_template(
        "analytics.html",
        category_chart=category_chart,
        trend_chart=trend_chart,
        budget_chart=budget_chart,
        stats=stats,
        view=view
    )


if __name__ == "__main__":
    app.run(debug=True)