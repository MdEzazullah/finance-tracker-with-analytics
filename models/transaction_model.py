from db import get_connection


def add_transaction(user_id, category_id, amount, type_, date, description=""):
    """
    Adds a new income or expense transaction.
    type_ must be 'income' or 'expense'.
    Returns the new transaction's id, or None on failure.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transactions (user_id, category_id, amount, type, date, description)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, category_id, amount, type_, date, description)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"Error adding transaction: {e}")
        conn.close()
        return None


def get_transactions(user_id, category_id=None, type_=None, start_date=None, end_date=None):
    """
    Fetches transactions for a user, with optional filters.
    Returns a list of dicts, newest first.
    """
    conn = get_connection()
    if not conn:
        return []

    query = """
        SELECT t.id, t.amount, t.type, t.date, t.description, c.name AS category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s
    """
    params = [user_id]

    if category_id:
        query += " AND t.category_id = %s"
        params.append(category_id)
    if type_:
        query += " AND t.type = %s"
        params.append(type_)
    if start_date:
        query += " AND t.date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND t.date <= %s"
        params.append(end_date)

    query += " ORDER BY t.date DESC"

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def update_transaction(transaction_id, amount=None, category_id=None, date=None, description=None):
    """
    Updates one or more fields of an existing transaction.
    Only the fields provided (not None) are changed.
    Returns True if a row was updated, False otherwise.
    """
    conn = get_connection()
    if not conn:
        return False

    fields = []
    params = []

    if amount is not None:
        fields.append("amount = %s")
        params.append(amount)
    if category_id is not None:
        fields.append("category_id = %s")
        params.append(category_id)
    if date is not None:
        fields.append("date = %s")
        params.append(date)
    if description is not None:
        fields.append("description = %s")
        params.append(description)

    if not fields:
        conn.close()
        return False

    params.append(transaction_id)
    query = f"UPDATE transactions SET {', '.join(fields)} WHERE id = %s"

    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    conn.commit()
    updated = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return updated


def delete_transaction(transaction_id):
    """
    Deletes a transaction by id. Returns True if deleted, False otherwise.
    """
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted


if __name__ == "__main__":
    # Quick manual test: run "python -m models.transaction_model" from the project root
    # Uses user_id=1, which should already exist from testing user_model.py

    new_id = add_transaction(1, 3, 250.00, "expense", "2026-09-01", "Groceries")
    print("Added transaction with id:", new_id)

    all_tx = get_transactions(1)
    print("All transactions for user 1:", all_tx)

    if new_id:
        updated = update_transaction(new_id, amount=300.00, description="Groceries + snacks")
        print("Update successful:", updated)

        deleted = delete_transaction(new_id)
        print("Delete successful:", deleted)