#!/usr/bin/env python3
"""
Advanced Python: Using Decorators and Context Managers
-------------------------------------------------------
Task: Create a decorator that logs SQL queries executed by any function.
Includes timestamped logs and safe resource handling using context managers.
"""

import sqlite3
import functools
from datetime import datetime
from contextlib import contextmanager


# Context Manager for handling DB connections
@contextmanager
def db_connection(db_name='users.db'):
    """Context manager to handle database connection safely."""
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


# Decorator to log SQL queries before executing the function
def log_queries(func):
    """Decorator that logs SQL queries executed by a function with timestamps."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Retrieve query argument (positional or keyword)
        query = kwargs.get('query') if 'query' in kwargs else args[0] if args else None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if query:
            print(f"[{timestamp}] [LOG] Executing SQL Query: {query}")
        else:
            print(f"[{timestamp}] [LOG] No SQL query provided.")

        result = func(*args, **kwargs)
        print(f"[{timestamp}] [LOG] Query execution completed.\n")
        return result
    return wrapper


@log_queries
def fetch_all_users(query):
    """Fetch all users from the database and return the results."""
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results


if __name__ == "__main__":
    # Example usage
    try:
        users = fetch_all_users(query="SELECT * FROM users;")
        print("Fetched Users:", users)
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
