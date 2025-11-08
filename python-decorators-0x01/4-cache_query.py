#!/usr/bin/env python3
"""
Advanced Python: Cache Database Query Results
---------------------------------------------
Task: Implement a decorator that caches the results of database queries to avoid redundant calls.
"""

import time
import sqlite3
import functools
from datetime import datetime


# Global dictionary to store cached query results
query_cache = {}


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


def cache_query(func):
    """Decorator that caches database query results based on the SQL query string."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get('query') if 'query' in kwargs else args[0] if args else None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not query:
            print(f"[{timestamp}] [LOG] No SQL query provided.")
            return func(conn, *args, **kwargs)

        # Check cache
        if query in query_cache:
            print(f"[{timestamp}] [CACHE HIT] Returning cached result for query: {query}")
            return query_cache[query]

        print(f"[{timestamp}] [CACHE MISS] Executing and caching result for query: {query}")
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users from the database and cache the result."""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("Fetched Users:", users)

    # Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Fetched Users Again:", users_again)