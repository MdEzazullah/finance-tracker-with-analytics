import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """
    Creates and returns a new connection to the MySQL database.
    Call this each time you need to run a query, and close it when done.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


if __name__ == "__main__":
    # Quick test: run "python db.py" to check the connection works
    conn = get_connection()
    if conn and conn.is_connected():
        print("Connected to MySQL database successfully!")
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tables in finance_tracker:", tables)
        cursor.close()
        conn.close()
    else:
        print("Failed to connect to MySQL database.")