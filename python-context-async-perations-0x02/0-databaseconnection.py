#!/usr/bin/env python3
"""
A class-based context manager that handles opening and closing
SQLite database connections automatically.
"""

import sqlite3


class DatabaseConnection:
    """Custom context manager for SQLite database connections."""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Establish a database connection when entering the context."""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the database connection is closed properly."""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)