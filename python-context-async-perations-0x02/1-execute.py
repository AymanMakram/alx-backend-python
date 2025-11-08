#!/usr/bin/env python3
"""
A reusable class-based context manager that handles both
database connection and query execution automatically.
"""

import sqlite3


class ExecuteQuery:
    """Custom context manager to execute a given SQL query safely."""

    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Open a database connection, execute the query, and return results."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection gracefully."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db", query, params) as results:
        print(results)