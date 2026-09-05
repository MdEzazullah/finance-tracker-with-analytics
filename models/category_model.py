from db import get_connection


def get_all_categories(type_=None):
    """
    Fetches all categories, optionally filtered by 'income' or 'expense'.
    Returns a list of dicts.
    """
    conn = get_connection()
    if not conn:
        return []

    query = "SELECT id, name, type FROM categories"
    params = []

    if type_:
        query += " WHERE type = %s"
        params.append(type_)

    query += " ORDER BY name"

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def add_category(name, type_):
    """
    Adds a new category. type_ must be 'income' or 'expense'.
    Returns the new category's id, or None on failure.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, type) VALUES (%s, %s)",
            (name, type_)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"Error adding category: {e}")
        conn.close()
        return None


def delete_category(category_id):
    """
    Deletes a category by id. Returns True if deleted, False otherwise.
    Note: this will fail if transactions/budgets still reference it,
    unless you want cascading deletes (already set up in schema.sql).
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted


if __name__ == "__main__":
    # Quick manual test: run "python -m models.category_model" from the project root

    all_categories = get_all_categories()
    print("All categories:", all_categories)

    expense_only = get_all_categories(type_="expense")
    print("Expense categories:", expense_only)

    new_id = add_category("Health", "expense")
    print("Added new category with id:", new_id)