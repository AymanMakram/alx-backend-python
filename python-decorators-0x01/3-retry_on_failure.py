#!/usr/bin/env python3
"""
Advanced Python: Retry Database Operations Decorator
----------------------------------------------------
Task: Implement a decorator that retries database operations on transient failure.
"""

import time
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
            result = func(conn, *args, **kwargs)
            print(f"[{timestamp}] [LOG] Closing database connection successfully.")
            return result
        except sqlite3.Error as e:
            print(f"[{timestamp}] [ERROR] Database error: {e}")
        finally:
            conn.close()
            print(f"[{timestamp}] [LOG] Database connection closed.")
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that retries a function if it raises a transient database error.
    :param retries: Number of retry attempts (default 3)
    :param delay: Delay in seconds between retries (default 2)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    print(f"[{timestamp}] [LOG] Attempt {attempts + 1} of {retries}...")
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    attempts += 1
                    print(f"[{timestamp}] [WARNING] Transient error: {e}")
                    if attempts < retries:
                        print(f"[{timestamp}] [LOG] Retrying in {delay} seconds...\n")
                        time.sleep(delay)
                    else:
                        print(f"[{timestamp}] [ERROR] All {retries} attempts failed.")
                        raise
                except Exception as e:
                    print(f"[{timestamp}] [ERROR] Non-transient error encountered: {e}")
                    raise
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch all users, retrying automatically on transient database errors."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # Attempt to fetch users with automatic retry on failure
    try:
        users = fetch_users_with_retry()
        print("Fetched Users:", users)
    except sqlite3.Error:
        print("Database operation failed after retries.")