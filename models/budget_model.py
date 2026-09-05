from db import get_connection


def set_budget(user_id, category_id, monthly_limit):
    """
    Sets a monthly budget limit for a user + category.
    If a budget already exists for this user/category, it updates it instead of duplicating.
    Returns True on success.
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM budgets WHERE user_id = %s AND category_id = %s",
        (user_id, category_id)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE budgets SET monthly_limit = %s WHERE id = %s",
            (monthly_limit, existing[0])
        )
    else:
        cursor.execute(
            "INSERT INTO budgets (user_id, category_id, monthly_limit) VALUES (%s, %s, %s)",
            (user_id, category_id, monthly_limit)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return True


def get_budgets(user_id):
    """
    Fetches all budgets for a user, along with the category name.
    Returns a list of dicts.
    """
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT b.id, b.monthly_limit, c.id AS category_id, c.name AS category_name
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           WHERE b.user_id = %s""",
        (user_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def check_budget_status(user_id, category_id, year, month):
    """
    Compares actual spending in a category for a given month against the budget limit.
    Returns a dict with limit, spent, and remaining -- or None if no budget is set.
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT monthly_limit FROM budgets WHERE user_id = %s AND category_id = %s",
        (user_id, category_id)
    )
    budget = cursor.fetchone()

    if not budget:
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0) AS total_spent
           FROM transactions
           WHERE user_id = %s AND category_id = %s AND type = 'expense'
           AND YEAR(date) = %s AND MONTH(date) = %s""",
        (user_id, category_id, year, month)
    )
    spent_row = cursor.fetchone()
    cursor.close()
    conn.close()

    spent = spent_row["total_spent"]
    limit = budget["monthly_limit"]

    return {
        "limit": limit,
        "spent": spent,
        "remaining": limit - spent,
        "over_budget": spent > limit
    }


def delete_budget(budget_id):
    """
    Deletes a budget by id. Returns True if deleted, False otherwise.
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE id = %s", (budget_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted


if __name__ == "__main__":
    # Quick manual test: run "python -m models.budget_model" from the project root
    # Uses user_id=1 and category_id=3 (Food), which should exist from earlier tests

    success = set_budget(1, 3, 5000.00)
    print("Budget set:", success)

    budgets = get_budgets(1)
    print("Budgets for user 1:", budgets)

    status = check_budget_status(1, 3, 2026, 9)
    print("Budget status for Food, Sept 2026:", status)