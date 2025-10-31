#!/usr/bin/python3
"""
Module: 1-batch_processing
Creates generator functions to fetch and process users in batches
from the `user_data` table in the ALX_prodev MySQL database.
"""

import mysql.connector


def stream_users_in_batches(batch_size):
    """
    Generator that fetches user records from the database in batches.

    Args:
        batch_size (int): Number of rows to fetch per batch.

    Yields:
        list[dict]: A batch (list) of user records as dictionaries.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="*!eR5$fr8RN3Fb",
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield rows

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users fetched from the database.

    Filters users over the age of 25 and prints them one by one.

    Args:
        batch_size (int): Number of rows per batch to fetch.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user.get("age", 0) > 25:
                print(user)
# Example: Call the generator directly
for batch in stream_users_in_batches(10):
    print(batch)  # prints each batch of 10 users

# Example: Process and filter users
batch_processing(50)  # prints only users with age > 25