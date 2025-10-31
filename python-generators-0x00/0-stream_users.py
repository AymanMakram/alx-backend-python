#!/usr/bin/python3
"""
Module: 0-stream_users
Creates a generator function that streams rows from MySQL one by one.

This function connects to the 'ALX_prodev' database and streams
records from the 'user_data' table using a Python generator (yield).
"""

import mysql.connector


def stream_users():
    """
    Generator that streams user data rows from the 'user_data' table.

    Yields:
        dict: Each row from the table as a dictionary
              (e.g. {'user_id': ..., 'name': ..., 'email': ..., 'age': ...})
    """

    try:
        # Connect to the existing ALX_prodev database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # change if you use another MySQL user
            password="*!eR5$fr8RN3Fb",      # update password if needed
            database="ALX_prodev"
        )

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        # Yield each row as it is fetched
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        # Ensure resources are released
        if cursor:
            cursor.close()
        if connection:
            connection.close()

from itertools import islice
# Print the first 6 users
for user in islice(stream_users(), 6):
    print(user)