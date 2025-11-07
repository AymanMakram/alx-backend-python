#!/usr/bin/env python3
"""
Advanced Python: Decorator for Automatic Database Connection Handling
----------------------------------------------------------------------
Task: Create a decorator that opens and closes the database connection automatically.
"""

import sqlite3
import functools
from datetime import datetime


def with_db_connection(func):
    """Decorator that handles opening and closing the database connection automatically."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [LOG] Opening database connection...")

        conn = sqlite3.connect("users.db")
        try:
            # Pass the connection object to the wrapped function
            result = func(conn, *args, **kwargs)
            print(f"[{timestamp}] [LOG] Closing database connection successfully.")
            return result
        except sqlite3.Error as e:
            print(f"[{timestamp}] [ERROR] Database error: {e}")
        finally:
            conn.close()
            print(f"[{timestamp}] [LOG] Database connection closed.")
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """Fetch a user by ID from the users table."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print("Fetched User:", user)
