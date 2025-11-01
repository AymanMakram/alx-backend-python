#!/usr/bin/python3
"""
Implements lazy pagination using a Python generator.

This module connects to the ALX_prodev MySQL database and retrieves user data
from the `user_data` table in pages (batches). It fetches only one page at a time,
making it memory efficient for large datasets.

Functions:
    paginate_users(page_size, offset): Fetches one page of users starting from a given offset.
    lazy_pagination(page_size): Generator that yields user pages lazily using pagination.
"""

import seed


def paginate_users(page_size, offset):
    """Fetch one page of users from the user_data table."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """Generator that lazily fetches pages of users from the database."""
    offset = 0
    while True:  # only one loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
    return  # marks end of generator

if __name__ == "__main__":
    print("🚀 Streaming user data in pages using lazy pagination...\n")

    try:
        for page in lazy_pagination(100):  # fetch 100 users per page
            for user in page:
                print(user)
    except KeyboardInterrupt:
        print("\n⛔ Pagination stopped by user.")