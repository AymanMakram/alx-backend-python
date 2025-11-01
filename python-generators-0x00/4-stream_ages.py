#!/usr/bin/python3
"""
Compute the average age of users using a generator
to ensure memory-efficient data processing.
"""

import seed


def stream_user_ages():
    """
    Generator that streams user ages one by one
    from the user_data table in ALX_prodev database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:
        yield row["age"]

    connection.close()


def compute_average_age():
    """
    Uses the stream_user_ages generator to compute
    the average age without loading all rows into memory.
    """
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count == 0:
        print("No users found.")
    else:
        average = total / count
        print(f"Average age of users: {average:.2f}")


if __name__ == "__main__":
    compute_average_age()
