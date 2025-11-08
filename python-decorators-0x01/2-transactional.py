#!/usr/bin/env python3
"""
Advanced Python: Transaction Management Decorator
-------------------------------------------------
Task: Create a decorator that automatically commits or rolls back database transactions.
Includes integration with the with_db_connection decorator.
"""

import sqlite3
import functools
from datetime import datetime


def with_db_connection(func):
    """Decorator that opens and closes the database connection automatically."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [LOG] Opening database connection...")

        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
            print(f"[{timestamp}] [LOG] Closing database connection successfully.")
            return result
        except sqlite3.Error as e:
            print(f"[{timestamp}] [ERROR] Database error: {e}")
        finally:
            conn.close()
            print(f"[{timestamp}] [LOG] Database connection closed.")
    return wrapper


def transactional(func):
    """Decorator that manages database transactions (commit or rollback)."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [LOG] Starting transaction...")

        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"[{timestamp}] [LOG] Transaction committed successfully.")
            return result
        except sqlite3.Error as e:
            conn.rollback()
            print(f"[{timestamp}] [ERROR] Transaction failed. Rolled back due to: {e}")
        except Exception as e:
            conn.rollback()
            print(f"[{timestamp}] [ERROR] Unexpected error. Rolled back due to: {e}")
        finally:
            print(f"[{timestamp}] [LOG] Transaction finished.\n")
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update user's email in the users table."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    print(f"[LOG] Email updated for user ID {user_id}.")


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')