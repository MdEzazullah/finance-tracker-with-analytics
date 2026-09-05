import bcrypt
from db import get_connection


def create_user(name, email, password):
    """
    Registers a new user. Hashes the password before storing it.
    Returns the new user's id on success, or None if the email already exists.
    """
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash.decode("utf-8"))
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.close()
        return None


def verify_user(email, password):
    """
    Checks email + password against the database.
    Returns the user's dict (id, name, email) if valid, or None if invalid.
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return None

    stored_hash = user["password_hash"].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return {"id": user["id"], "name": user["name"], "email": user["email"]}
    else:
        return None


def get_user_by_id(user_id):
    """
    Fetches a single user's public info by id (no password hash).
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


if __name__ == "__main__":
    # Quick manual test: run "python models/user_model.py" from the project root
    # (or "python -m models.user_model" if you get import errors)
    test_id = create_user("Test User", "test@example.com", "mypassword123")
    print("Created user with id:", test_id)

    result = verify_user("test@example.com", "mypassword123")
    print("Login check (correct password):", result)

    result_fail = verify_user("test@example.com", "wrongpassword")
    print("Login check (wrong password):", result_fail)

